"""
Meeting Intelligence System — FastAPI backend
Clean + beginner friendly + debug safe
"""

from pathlib import Path
from uuid import uuid4
import traceback
import importlib

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool

from src.recorder import start_recording, stop_recording   # ✅ NEW


# ===============================
# Load services ONLY ONCE (better)
# ===============================
def load_services():
    for module_name in ("services", "src.services"):
        try:
            return importlib.import_module(module_name)
        except ModuleNotFoundError:
            continue
    raise RuntimeError(
        "services.py not found. Create src/services.py with "
        "process_meeting, generate_notes, ask_question"
    )


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

app.state.meeting_processed = False

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".mp4", ".mp3", ".wav"}


# ===============================
# 🔥 NEW: recording stream holder
# ===============================
stream = None


# ===============================
# Models
# ===============================
class ChatRequest(BaseModel):
    question: str


# ===============================
# Routes
# ===============================
@app.get("/")
async def root():
    return {"message": "API running"}


# ------------------------------------------------
# 🔥 NEW: Start recording
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
# 🔥 NEW: Stop recording + process automatically
# ------------------------------------------------
@app.post("/stop-recording")
async def stop_rec():
    global stream

    if stream is None:
        raise HTTPException(400, "Recording not started")

    try:
        audio_path = stop_recording(stream, "uploads/meeting.wav")

        # run SAME pipeline you already use
        await run_in_threadpool(process_meeting, str(audio_path))

        app.state.meeting_processed = True
        stream = None

        return {"message": "Recording stopped & meeting processed"}
    except Exception:
        traceback.print_exc()
        raise HTTPException(500, "Recording processing failed")


# -------------------------------
# Upload + process (OLD METHOD still works)
# -------------------------------
@app.post("/upload")
async def upload(file: UploadFile = File(...)):

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, "Only mp4/mp3/wav allowed")

    file_path = UPLOAD_DIR / f"{uuid4().hex}{ext}"

    try:
        with open(file_path, "wb") as f:
            while chunk := await file.read(1024 * 1024):
                f.write(chunk)
    except Exception:
        traceback.print_exc()
        raise HTTPException(500, "Failed to save file")

    try:
        await run_in_threadpool(process_meeting, str(file_path))
    except Exception:
        traceback.print_exc()
        raise HTTPException(500, "Pipeline crashed. Check terminal.")

    app.state.meeting_processed = True

    return {"message": "meeting processed successfully"}


# -------------------------------
# Notes
# -------------------------------
@app.post("/notes")
async def notes():

    if not app.state.meeting_processed:
        raise HTTPException(400, "Upload/Record meeting first")

    try:
        result = await run_in_threadpool(generate_notes)
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
        answer = await run_in_threadpool(ask_question, payload.question)
        return {"answer": answer}
    except Exception:
        traceback.print_exc()
        raise HTTPException(500, "Chat failed")
