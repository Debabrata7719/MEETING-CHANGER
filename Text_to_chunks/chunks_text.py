import os
from langchain_text_splitters import RecursiveCharacterTextSplitter



input_file = "audio_to_text/Converted Audio To Text.txt"
output_folder = "Text_to_chunks"
output_file = "chunks.txt"


os.makedirs(output_folder, exist_ok=True)


# read transcript
with open(input_file, "r", encoding="utf-8") as f:
    text = f.read()


# chunking
splitter = RecursiveCharacterTextSplitter(
    chunk_size=150,
    chunk_overlap=30
)


chunks = splitter.split_text(text)


# save chunks
output_path = os.path.join(output_folder, output_file)

with open(output_path, "w", encoding="utf-8") as f:
    for i, chunk in enumerate(chunks, 1):
        f.write(f"\n----- CHUNK {i} -----\n")
        f.write(chunk + "\n")


print(f"Chunks saved at: {output_path}")
print(f"Total chunks created: {len(chunks)}")
