import chromadb

client = chromadb.Client(
    settings=chromadb.Settings(
        persist_directory="vectordb",
        is_persistent=True
    )
)

collection = client.get_collection("meeting_chunks")


results = collection.query(
    query_texts=["motivation"],
    n_results=2
)

print(results["documents"])
