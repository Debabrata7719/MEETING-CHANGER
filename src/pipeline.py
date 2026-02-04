# src/pipeline.py

from langchain_classic.chains import TransformChain, SimpleSequentialChain

from src.video_to_audio import video_to_audio
from src.audio_to_text import audio_to_text
from src.chunk_text import chunk_text
from src.embed_store import embed_store


# =================================
# ONLY PREPROCESSING (NO LLM HERE)
# =================================


# 1️⃣ Video → Audio
video_chain = TransformChain(
    input_variables=["video"],
    output_variables=["audio"],
    transform=lambda x: {"audio": video_to_audio(x["video"])}
)


# 2️⃣ Audio → Text
audio_chain = TransformChain(
    input_variables=["audio"],
    output_variables=["text"],
    transform=lambda x: {"text": audio_to_text(x["audio"])}
)


# 3️⃣ Text → Chunks
chunk_chain = TransformChain(
    input_variables=["text"],
    output_variables=["chunks"],
    transform=lambda x: {"chunks": chunk_text(x["text"])}
)


# 4️⃣ Chunks → Embeddings → VectorDB
embed_chain = TransformChain(
    input_variables=["chunks"],
    output_variables=["db"],
    transform=lambda x: {"db": embed_store(x["chunks"])}
)


# =================================
# PIPELINE (NO HIGHLIGHTS HERE)
# =================================

pipeline = SimpleSequentialChain(
    chains=[
        video_chain,
        audio_chain,
        chunk_chain,
        embed_chain
    ],
    verbose=True
)


# =================================
# API wrapper
# =================================

def run_pipeline(video_path: str):
    return pipeline.run(video_path)
