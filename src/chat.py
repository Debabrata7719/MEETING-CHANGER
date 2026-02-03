# ===============================
# LOAD ENV
# ===============================
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()


# ===============================
# IMPORTS
# ===============================
from langchain_groq import ChatGroq
from langchain_chroma import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate


# ===============================
# PATH SETUP (robust)
# ===============================
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "vectordb"


# ===============================
# EMBEDDING (load once → faster)
# ===============================
embedding = SentenceTransformerEmbeddings(
    model_name="all-MiniLM-L6-v2"
)


# ===============================
# VECTOR DB
# ===============================
db = Chroma(
    persist_directory=str(DB_PATH),
    embedding_function=embedding,
    collection_name="meeting_chunks"
)

retriever = db.as_retriever(search_kwargs={"k": 5})


# ===============================
# LLM
# ===============================
llm = ChatGroq(
    model_name="openai/gpt-oss-120b",
    temperature=0
)


# ===============================
# PROMPT
# ===============================
template = """
Answer ONLY using context.

Rules:
- Do not guess
- If not found say: "Not found in the meeting transcript"

Context:
{context}

Question:
{question}
"""

prompt = PromptTemplate(
    template=template,
    input_variables=["context", "question"]
)


# ===============================
# QA CHAIN
# ===============================
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    chain_type="stuff",
    chain_type_kwargs={"prompt": prompt}
)


# ===============================
# MAIN FUNCTION (API safe)
# ===============================
def ask_question(query: str) -> str:
    """
    Called by FastAPI.
    Returns answer string.
    """

    if not query.strip():
        return "Please ask a valid question."

    result = qa_chain.invoke({"query": query})

    return result["result"]
