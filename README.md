# 🎙️ Meeting Changer – Video to AI Q&A Bot

Convert a meeting video into text and chat with it using AI.

## 🚀 Pipeline

Video (.mp4)
→ Audio (FFmpeg)
→ Transcript (Whisper)
→ Text Chunks (LangChain)
→ Embeddings
→ Vector DB (ChromaDB)
→ Ask Questions (RAG Chatbot)

## 🛠️ Tech Stack
Python • FFmpeg • Whisper • LangChain • SentenceTransformers • ChromaDB

## 📂 Structure

src/
- video_to_audio.py
- audio_to_text.py
- chunk_text.py
- embed_store.py
- chat.py
- pipeline.py

data/
- input/
- intermediate/
- vectordb/

## ▶️ Run

Install:
```bash
pip install -r requirements.txt

Process video:
python src/pipeline.py

Chat with meeting:
python src/chat.py
