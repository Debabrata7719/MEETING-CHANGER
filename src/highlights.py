from langchain_chroma import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()


def extract_highlights(meeting_id: str):

    print("🔍 Extracting meeting highlights...")

    # ========= Embedding =========
    embedding = SentenceTransformerEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )

    #  LOAD MEETING-SPECIFIC DB
    db_path = os.path.join("data", "vectordb", meeting_id)

    db = Chroma(
        persist_directory=db_path,
        embedding_function=embedding,
        collection_name="meeting_chunks"
    )

    retriever = db.as_retriever(search_kwargs={"k": 5})

    # ========= Queries =========
    queries = [
        "important topics discussed",
        "decisions made in the meeting",
        "action items and tasks assigned",
        "deadlines or plans"
    ]

    chunks = []

    for q in queries:
        docs = retriever.invoke(q)
        chunks.extend([d.page_content for d in docs])

    context = "\n\n".join(chunks)

    # ========= LLM =========
    llm = ChatGroq(
        model_name="openai/gpt-oss-120b",
        temperature=0
    )

    prompt = ChatPromptTemplate.from_template("""
Extract clean meeting highlights from the text.

Return:
• Key Topics
• Decisions
• Action Items

Text:
{text}
""")

    chain = prompt | llm

    result = chain.invoke({"text": context}).content

    # ========= Save =========
    os.makedirs("Notes", exist_ok=True)

    with open(f"Notes/highlights_{meeting_id}.txt", "w", encoding="utf-8") as f:
        f.write(result)

    print("✅ Highlights saved")
    return result
