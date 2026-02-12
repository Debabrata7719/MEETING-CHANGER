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
# PROMPT (UPGRADED INTELLIGENCE)
# ===============================
template = """
You are an expert meeting assistant.

STRICT RULES:
- Answer ONLY from context
- Do NOT guess or hallucinate
- If answer not present → say: "Not found in the meeting transcript"
- Keep answer concise but complete
- Prefer bullet points if multiple items
- Preserve numbers, dates, and names exactly

Language Rule:
Respond in the SAME language as the question.

Context:
{context}

Question:
{question}

Answer:
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

    # ===== Improved Retriever =====
    retriever = db.as_retriever(
        search_kwargs={
            "k": 7   # slightly more context improves accuracy
        }
    )

    # ===== Meeting-specific memory =====
    memory = ConversationBufferWindowMemory(
        k=5,  # slightly longer memory window
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
        "question": query.strip()
    })

    answer = result["answer"].strip()

    # ===== Extra Safety Filter =====
    if not answer:
        return "Not found in the meeting transcript"

    return answer
