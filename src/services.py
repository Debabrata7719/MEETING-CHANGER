# src/services.py

from src.pipeline import run_pipeline
from src.highlights import extract_highlights
from src.chat import ask_question as chat_ask


# called after upload
def process_meeting(file_path: str):
    run_pipeline(file_path)


# for notes
def generate_notes():
    return extract_highlights()


# for chat
def ask_question(query: str):
    return chat_ask(query)
