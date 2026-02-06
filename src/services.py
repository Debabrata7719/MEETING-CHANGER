from src.pipeline import run_pipeline
from src.embed_store import embed_store
from src.highlights import extract_highlights
from src.chat import ask_question as chat_ask


def process_meeting(file_path: str, meeting_id: str):
    chunks_file = run_pipeline(file_path)
    embed_store(chunks_file, meeting_id)


def generate_notes(meeting_id: str):   # 🔥 FIXED
    return extract_highlights(meeting_id)


def ask_question(query: str, meeting_id: str):
    return chat_ask(query, meeting_id)
