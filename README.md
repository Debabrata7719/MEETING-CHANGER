# Meeting Intelligence System

Turn meetings into searchable knowledge with AI-powered transcription, highlights, and chat.

---

## Overview

The **Meeting Intelligence System** is an end-to-end AI application that converts meeting recordings into structured insights. It allows users to upload or record meetings, automatically transcribe them, generate highlights, and ask questions about the meeting content using an intelligent chat assistant.

This project demonstrates a production-style architecture using modern LLM pipelines, vector databases, and retrieval-augmented generation.

<p align="center">
  <img src="assets/ui.png" width="900">
</p>


## Features

### Core Features

* Upload or record meeting audio/video
* Automatic speech-to-text transcription
* Semantic chunking of transcript
* Vector embeddings storage
* Meeting highlights generation
* Conversational Q&A over meetings
* Multi-meeting support with session switching

### Advanced Features

* Meeting-specific vector databases
* Conversational memory for chat
* Highlight extraction agent
* Structured retrieval queries
* Download highlights (PDF / TXT / DOCX)
* Meeting history panel
* Active meeting indicator
* Recording timer
* Modal UI inputs
* Multi-language chat responses

---

## Tech Stack

**Backend**

* Python
* FastAPI
* LangChain
* Groq LLM
* Whisper
* SentenceTransformers
* Chroma Vector DB

**Frontend**

* HTML
* CSS
* JavaScript (Vanilla)

**Processing Pipeline**

```
Video → Audio → Transcript → Chunks → Embeddings → Vector DB → Retrieval → LLM
```

---

## Project Structure

```
Project Structure
-----------------

MEETING CHANGER/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── data/
│   ├── intermediate/
│   └── vectordb/
│
├── Frontend/
│   ├── index.html
│   ├── script.js
│   └── style.css
│
├── Notes/
│     Note:
         - vectordb stores embeddings per meeting
         - uploads stores user recordings
         - intermediate stores temporary processing files

├── src/
│   ├── audio_to_text.py
│   ├── chat.py
│   ├── chunk_text.py
│   ├── embed_store.py
│   ├── highlights.py
│   ├── pipeline.py
│   ├── recorder.py
│   ├── services.py
│   └── video_to_audio.py
│
├── uploads/
├── venv/
├── .env
├── .gitignore
├── main.py
├── README.md
└── requirements.txt


## Installation

### 1. Clone Repository

```
git clone <repo_url>
cd project
```

### 2. Create Virtual Environment

```
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```
pip install -r requirements.txt
```

### 4. Add Environment Variables

Create `.env`

```
GROQ_API_KEY=your_key_here
```

---

## Running the Application

Start backend server:

```
uvicorn main:app --reload
```

Open frontend:

```
Frontend/index.html
```

---

## How It Works

### Upload Flow

1. User uploads meeting
2. Backend extracts audio
3. Whisper generates transcript
4. Text is chunked
5. Embeddings created
6. Stored in Chroma DB

---

### Highlights Flow

1. Retriever fetches important chunks
2. LLM analyzes context
3. Extracts key insights
4. Saves notes file

---

### Chat Flow

1. User asks question
2. Retriever finds relevant chunks
3. LLM answers using context only
4. Memory stores recent conversation

---

## API Endpoints

### Upload Meeting

```
POST /upload
```

### Generate Highlights

```
GET /notes?meeting_id=xxx
```

### Ask Question

```
POST /chat
```

---

## Highlight Extraction Logic

Highlights agent:

* runs multi-query retrieval
* selects best chunks
* removes duplicates
* sends optimized context to LLM
* formats concise highlights

---

## Chat Intelligence Logic

Chat agent:

* uses Conversational Retrieval Chain
* maintains short-term memory
* prevents hallucination
* answers only from transcript

---

## UI Design Principles

* Clean dashboard layout
* Real-time feedback indicators
* Clear hierarchy
* Sticky chat input
* Interactive hover effects
* Structured highlight display

---

## Performance Optimizations

* embeddings loaded once
* LLM initialized once
* meeting-specific vector DB
* limited retrieval context
* deduplicated chunks

---

## Security Considerations

* Meeting isolation via meeting_id
* No cross-meeting data access
* Context-restricted answering
* Environment-based API keys

---

## Future Improvements

* Speaker diarization
* Live transcription streaming
* Role-based highlights
* Meeting analytics dashboard
* Sentiment analysis
* Action item auto-assignment

---

## Resume Description

> Built an AI-powered Meeting Intelligence System that converts recordings into searchable knowledge using Whisper, LangChain, ChromaDB, and Groq LLM, featuring semantic retrieval chat, automated highlights, and production-style architecture.

