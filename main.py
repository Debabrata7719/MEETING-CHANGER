"""
Meeting Intelligence System — FastAPI backend
"""

from pathlib import Path
from uuid import uuid4
import traceback
import importlib

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool

from src.recorder import start_recording, stop_recording


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
app.state.current_meeting_id = None
app.state.meeting_processed = False
stream = None


# ===============================
# Models
# ===============================
class ChatRequest(BaseModel):
    question: str
    meeting_id: str   # 🔥 NEW


# ===============================
# Routes
# ===============================
@app.get("/")
async def root():
    return {"message": "API running"}


# ------------------------------------------------
# Start recording
# ------------------------------------------------
@app.post("/start-recording")
async def start_rec():
    global stream

    try:
        stream = start_recording()
        return {"message": "Recording started"}
    except Exception:
        traceback.print_exc()
        raise HTTPException(500, "Recording failed to start")


# ------------------------------------------------
# Stop recording + process
# ------------------------------------------------
@app.post("/stop-recording")
async def stop_rec():
    global stream

    if stream is None:
        raise HTTPException(400, "Recording not started")

    try:
        meeting_id = uuid4().hex  # 🔥 NEW

        audio_path = stop_recording(stream, "uploads/meeting.wav")

        await run_in_threadpool(process_meeting, str(audio_path), meeting_id)

        app.state.current_meeting_id = meeting_id
        app.state.meeting_processed = True
        stream = None

        return {
            "message": "Recording stopped & meeting processed",
            "meeting_id": meeting_id   # 🔥 send to frontend
        }

    except Exception:
        traceback.print_exc()
        raise HTTPException(500, "Recording processing failed")


# -------------------------------
# Upload + process
# -------------------------------
@app.post("/upload")
async def upload(file: UploadFile = File(...)):

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, "Only mp4/mp3/wav allowed")

    meeting_id = uuid4().hex  # 🔥 NEW

    file_path = UPLOAD_DIR / f"{meeting_id}{ext}"

    try:
        with open(file_path, "wb") as f:
            while chunk := await file.read(1024 * 1024):
                f.write(chunk)

        await run_in_threadpool(process_meeting, str(file_path), meeting_id)

    except Exception:
        traceback.print_exc()
        raise HTTPException(500, "Pipeline crashed. Check terminal.")

    app.state.current_meeting_id = meeting_id
    app.state.meeting_processed = True

    return {
        "message": "meeting processed successfully",
        "meeting_id": meeting_id   # 🔥 send to frontend
    }


# -------------------------------
# Notes
# -------------------------------
@app.post("/notes")
async def notes():

    if not app.state.meeting_processed:
        raise HTTPException(400, "Upload/Record meeting first")

    try:
        # 🔥 pass meeting_id to highlights
        result = await run_in_threadpool(
            generate_notes,
            app.state.current_meeting_id
        )

        return {"notes": result}

    except Exception:
        traceback.print_exc()
        raise HTTPException(500, "Notes generation failed")


# -------------------------------
# Chat
# -------------------------------
@app.post("/chat")
async def chat(payload: ChatRequest):

    if not app.state.meeting_processed:
        raise HTTPException(400, "Upload/Record meeting first")

    try:
        answer = await run_in_threadpool(
            ask_question,
            payload.question,
            payload.meeting_id   # 🔥 NEW
        )

        return {"answer": answer}

    except Exception:
        traceback.print_exc()
        raise HTTPException(500, "Chat failed")
