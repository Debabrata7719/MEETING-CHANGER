import os
import chromadb
from sentence_transformers import SentenceTransformer

chunks_file = "Text_to_chunks/chunks.txt"
db_folder = "vectordb"
collection_name = "meeting_chunks"


# -------- Step 1: Load chunks --------
chunks = []

with open(chunks_file, "r", encoding="utf-8") as f:
    text = f.read()

# split by marker
raw_chunks = text.split("----- CHUNK")

for c in raw_chunks:
    c = c.strip()
    if len(c) > 20:
        chunks.append(c)

print(f"✅ Loaded {len(chunks)} chunks")


# -------- Step 2: Load embedding model --------
model = SentenceTransformer("all-MiniLM-L6-v2")


# -------- Step 3: Generate embeddings --------
embeddings = model.encode(chunks).tolist()

print("✅ Embeddings created")


# -------- Step 4: Create Chroma DB --------
os.makedirs(db_folder, exist_ok=True)

client = chromadb.Client(
    settings=chromadb.Settings(
        persist_directory=db_folder,
        is_persistent=True
    )
)

collection = client.get_or_create_collection(collection_name)


# -------- Step 5: Store in DB --------
collection.add(
    documents=chunks,
    embeddings=embeddings,
    ids=[str(i) for i in range(len(chunks))]
)

print("✅ Stored embeddings in ChromaDB")
print(f"📁 Saved inside folder: {db_folder}")
