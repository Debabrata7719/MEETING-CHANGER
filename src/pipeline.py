# src/pipeline.py

from langchain_classic.chains import TransformChain, SimpleSequentialChain

from video_to_audio import video_to_audio
from audio_to_text import audio_to_text
from chunk_text import chunk_text
from embed_store import embed_store


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


# 5️⃣ Combine all chains
pipeline = SimpleSequentialChain(
    chains=[
        video_chain,
        audio_chain,
        chunk_chain,
        embed_chain
    ],
    verbose=True
)


# 6️⃣ Run
if __name__ == "__main__":
    pipeline.run("data/input/meeting.mp4")
