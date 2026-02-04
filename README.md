# 🎯 Meeting Intelligence System

Convert meeting recordings into **highlights + answers + chat**.

Upload a meeting → get transcript → generate notes → ask questions.

Built with FastAPI + LangChain + Whisper + ChromaDB + Groq.

---

## 🚀 Features

- Upload mp4 / mp3 / wav
- Speech → text (Whisper)
- Vector search (ChromaDB)
- AI highlights (on demand)
- Chat with your meeting
- Clean dashboard UI

---

## 🏗️ Tech Stack

Backend: FastAPI  
AI: Whisper, LangChain, SentenceTransformers, Groq  
DB: Chroma Vector DB  
Frontend: HTML, CSS, JS  

---

## ⚙️ Workflow

Video → Audio → Transcript → Chunks → Embeddings → Vector DB


- `/upload` → process meeting  
- `/notes` → generate highlights  
- `/chat` → ask questions  

Highlights run **only when requested** (not during upload).

---

## 🛠️ Setup

```bash
git clone <repo>
cd meeting-intelligence
python -m venv venv
pip install -r requirements.txt
Create .env

GROQ_API_KEY=your_key
Run backend:

uvicorn main:app --reload
Open frontend:

index.html
or

python -m http.server 5500
Problems faced ----------
Highlights auto-running during upload → separated into /notes

Chroma import errors → switched to langchain-chroma

File upload issues → installed python-multipart

Chat UI layout fixes with CSS

Learned a lot about building real-world RAG + FastAPI apps.