"""
Meeting Intelligence System — FastAPI backend
"""

from pathlib import Path
from uuid import uuid4
import traceback
import importlib
import os
import json
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool

from src.recorder import start_recording, stop_recording
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from docx import Document


# ===============================
# Load services ONLY ONCE
# ===============================
def load_services():
    for module_name in ("services", "src.services"):
        try:
            return importlib.import_module(module_name)
        except ModuleNotFoundError:
            continue
    raise RuntimeError("services.py not found")


services = load_services()
process_meeting = getattr(services, "process_meeting")
generate_notes = getattr(services, "generate_notes")
ask_question = getattr(services, "ask_question")


# ===============================
# App setup
# ===============================
app = FastAPI(title="Meeting Intelligence System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".mp4", ".mp3", ".wav"}


# ===============================
# Runtime state
# ===============================
stream = None


# ===============================
# Models
# ===============================
class ChatRequest(BaseModel):
    question: str
    meeting_id: str


class NotesRequest(BaseModel):
    meeting_id: str


class MeetingName(BaseModel):
    meeting_id: str
    name: str


# ===============================
# Root
# ===============================
@app.get("/")
async def root():
    return {"message": "API running"}


# ===============================
# Start recording
# ===============================
@app.post("/start-recording")
async def start_rec():
    global stream
    try:
        stream = start_recording()
        return {"message": "Recording started"}
    except Exception:
        traceback.print_exc()
        raise HTTPException(500, "Recording failed to start")


# ===============================
# Stop recording + process
# ===============================
@app.post("/stop-recording")
async def stop_rec():
    global stream

    if stream is None:
        raise HTTPException(400, "Recording not started")

    try:
        meeting_id = uuid4().hex

        audio_path = stop_recording(stream, "uploads/meeting.wav")
        await run_in_threadpool(process_meeting, str(audio_path), meeting_id)

        stream = None

        return {
            "message": "Recording stopped & processed",
            "meeting_id": meeting_id
        }

    except Exception:
        traceback.print_exc()
        raise HTTPException(500, "Recording processing failed")


# ===============================
# Upload + process
# ===============================
@app.post("/upload")
async def upload(file: UploadFile = File(...)):

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, "Only mp4/mp3/wav allowed")

    meeting_id = uuid4().hex
    file_path = UPLOAD_DIR / f"{meeting_id}{ext}"

    try:
        with open(file_path, "wb") as f:
            while chunk := await file.read(1024 * 1024):
                f.write(chunk)

        await run_in_threadpool(process_meeting, str(file_path), meeting_id)

    except Exception:
        traceback.print_exc()
        raise HTTPException(500, "Pipeline crashed")

    return {
        "message": "meeting processed successfully",
        "meeting_id": meeting_id
    }


# ===============================
# Generate highlights (SELECTED MEETING)
# ===============================
@app.post("/notes")
async def notes(payload: NotesRequest):

    try:
        result = await run_in_threadpool(
            generate_notes,
            payload.meeting_id
        )
        return {"notes": result}

    except Exception:
        traceback.print_exc()
        raise HTTPException(500, "Notes generation failed")


# ===============================
# Chat (SELECTED MEETING)
# ===============================
@app.post("/chat")
async def chat(payload: ChatRequest):

    try:
        answer = await run_in_threadpool(
            ask_question,
            payload.question,
            payload.meeting_id
        )
        return {"answer": answer}

    except Exception:
        traceback.print_exc()
        raise HTTPException(500, "Chat failed")


# ==========================================================
# Download Highlights
# ==========================================================
@app.get("/download-notes")
def download_notes(meeting_id: str, format: str = "pdf"):

    # ---------- load meeting name ----------
    meeting_name = meeting_id
    mapping_file = "data/meetings.json"

    if os.path.exists(mapping_file):
        with open(mapping_file) as f:
            db = json.load(f)
            meeting_name = db.get(meeting_id, meeting_id)

    meeting_name = "".join(
        c for c in meeting_name if c.isalnum() or c in (" ", "-", "_")
    ).strip()

    download_time = datetime.now().strftime("%d %b %Y, %I:%M %p")

    txt_path = f"Notes/highlights_{meeting_id}.txt"

    if not os.path.exists(txt_path):
        return {"error": "Highlights not generated yet."}

    with open(txt_path, "r", encoding="utf-8") as f:
        text = f.read()


    # ================= PDF =================
    if format == "pdf":

        pdf_path = f"Notes/{meeting_name}_{meeting_id}.pdf"

        doc = SimpleDocTemplate(pdf_path)
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph("Meeting Highlights", styles["Heading1"]))
        elements.append(Spacer(1, 20))
        elements.append(Paragraph(f"Meeting: {meeting_name}", styles["Normal"]))
        elements.append(Paragraph(f"Downloaded: {download_time}", styles["Normal"]))
        elements.append(Spacer(1, 20))

        for line in text.split("\n"):
            elements.append(Paragraph(line, styles["BodyText"]))
            elements.append(Spacer(1, 8))

        doc.build(elements)

        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=f"{meeting_name}.pdf"
        )


    # ================= TXT =================
    elif format == "txt":

        header = f"Meeting: {meeting_name}\nDownloaded: {download_time}\n\n"
        temp_path = f"Notes/{meeting_name}_{meeting_id}.txt"

        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(header + text)

        return FileResponse(
            temp_path,
            media_type="text/plain",
            filename=f"{meeting_name}.txt"
        )


    # ================= DOCX =================
    elif format == "docx":

        docx_path = f"Notes/{meeting_name}_{meeting_id}.docx"

        document = Document()
        document.add_heading("Meeting Highlights", 0)
        document.add_paragraph(f"Meeting: {meeting_name}")
        document.add_paragraph(f"Downloaded: {download_time}")
        document.add_paragraph("")

        for line in text.split("\n"):
            document.add_paragraph(line)

        document.save(docx_path)

        return FileResponse(
            docx_path,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=f"{meeting_name}.docx"
        )

    else:
        return {"error": "Invalid format"}


# ==========================================================
# Save meeting name
# ==========================================================
@app.post("/set-meeting-name")
def set_meeting_name(data: MeetingName):

    os.makedirs("data", exist_ok=True)
    file = "data/meetings.json"

    if os.path.exists(file):
        with open(file) as f:
            db = json.load(f)
    else:
        db = {}

    db[data.meeting_id] = data.name

    with open(file, "w") as f:
        json.dump(db, f, indent=2)

    return {"status": "saved"}


# ==========================================================
# Meeting history list
# ==========================================================
@app.get("/meetings")
def list_meetings():

    file = "data/meetings.json"

    if not os.path.exists(file):
        return []

    with open(file) as f:
        db = json.load(f)

    meetings = [{"id": k, "name": v} for k, v in db.items()]
    meetings.reverse()

    return meetings
