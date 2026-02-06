# src/pipeline.py

from langchain_classic.chains import TransformChain, SimpleSequentialChain

from src.video_to_audio import video_to_audio
from src.audio_to_text import audio_to_text
from src.chunk_text import chunk_text


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


# 3️⃣ Text → Chunks (LAST STEP)
chunk_chain = TransformChain(
    input_variables=["text"],
    output_variables=["chunks"],
    transform=lambda x: {"chunks": chunk_text(x["text"])}
)


# 🔥 NO embed_store here anymore
pipeline = SimpleSequentialChain(
    chains=[
        video_chain,
        audio_chain,
        chunk_chain
    ],
    verbose=True
)


def run_pipeline(video_path: str):
    """
    Returns chunks file path only.
    Embedding handled in services.py
    """
    return pipeline.run(video_path)
