# ===============================
# LOAD ENV
# ===============================
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()


# ===============================
# IMPORTS
# ===============================
from langchain_groq import ChatGroq
from langchain_chroma import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings

from langchain_classic.chains import ConversationalRetrievalChain
from langchain_classic.memory import ConversationBufferWindowMemory

from langchain_core.prompts import PromptTemplate


# ===============================
# PATH SETUP
# ===============================
BASE_DIR = Path(__file__).resolve().parent.parent
VECTORDB_DIR = BASE_DIR / "data" / "vectordb"


# ===============================
# EMBEDDING (load once → faster)
# ===============================
embedding = SentenceTransformerEmbeddings(
    model_name="all-MiniLM-L6-v2"
)


# ===============================
# LLM (load once)
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
-Answer in the same language as the user's question.
If user speaks Hindi, reply in Hindi.
If English, reply in English.

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
# HELPER → Load DB for meeting
# ===============================
def load_chain(meeting_id: str):
    """
    Creates retriever + memory + chain
    specific to ONE meeting.
    """

    db_path = VECTORDB_DIR / meeting_id


    if not db_path.exists():
        raise ValueError(f"Meeting not found: {meeting_id}")

    db = Chroma(
        persist_directory=str(db_path),
        embedding_function=embedding,
        collection_name="meeting_chunks"
    )

    retriever = db.as_retriever(search_kwargs={"k": 5})

    # 🔥 NEW memory created per meeting (important)
    memory = ConversationBufferWindowMemory(
        k=4,
        memory_key="chat_history",
        return_messages=True
    )

    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        combine_docs_chain_kwargs={"prompt": prompt}
    )

    return chain


# ===============================
# MAIN FUNCTION (API safe)
# ===============================
def ask_question(query: str, meeting_id: str) -> str:
    """
    Called by FastAPI.

    Each meeting:
      → separate vectordb
      → separate memory
    """

    if not query.strip():
        return "Please ask a valid question."

    qa_chain = load_chain(meeting_id)

    result = qa_chain.invoke({
        "question": query
    })

    return result["answer"]
