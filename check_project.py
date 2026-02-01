import chromadb
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(BASE_DIR, "data", "vectordb")

client = chromadb.Client(
    settings=chromadb.Settings(
        persist_directory=db_path,
        is_persistent=True
    )
)

collection = client.get_collection("meeting_chunks")


results = collection.query(
    query_texts=["motivation"],
    n_results=2
)

print(results["documents"])
