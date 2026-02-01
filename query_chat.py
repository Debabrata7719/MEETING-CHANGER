#LOAD ENV
from dotenv import load_dotenv
import os

load_dotenv()  


#IMPORTS
from langchain_groq import ChatGroq
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_classic.chains import RetrievalQA



# STEP 1 — Embedding model

embedding = SentenceTransformerEmbeddings(
    model_name="all-MiniLM-L6-v2"
)


# =========================
# STEP 2 — Load Chroma DB (with correct collection name)
# =========================
db = Chroma(
    persist_directory="vectordb",
    embedding_function=embedding,
    collection_name="meeting_chunks"  # Must match the collection used in embedding_and_store.py
)


# =========================
# STEP 3 — Create Retriever
# =========================
# Get total document count for smart handling
collection = db._collection
total_docs = collection.count()

# For small transcripts (≤10 chunks), retrieve all for full context
if total_docs <= 10 and total_docs > 0:
    retriever = db.as_retriever(search_kwargs={"k": total_docs})
    print(f"📝 Small transcript detected ({total_docs} chunks) - using FULL context mode")
elif total_docs > 10:
    retriever = db.as_retriever(search_kwargs={"k": 5})
    print(f"📚 Large transcript ({total_docs} chunks) - using retrieval mode (top 5)")
else:
    print("❌ ERROR: No chunks found in VectorDB! Run embedding_and_store.py first.")
    exit(1)


# =========================
# STEP 4 — Load Groq LLM
# =========================
llm = ChatGroq(
    model_name="openai/gpt-oss-120b",  # fast + good
    temperature=0
)


# =========================
# STEP 5 — RetrievalQA Chain
# =========================
from langchain_core.prompts import PromptTemplate

template = """
Answer the question based strictly on the context below. 
Keep your answer CONCISE, SHORT, and to the point (max 2-3 sentences).

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

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    chain_type="stuff",
    chain_type_kwargs={"prompt": prompt}
)


# =========================
# STEP 6 — Chat loop
# =========================
print("\n🔥 Chat with your meeting (type 'exit' to stop)\n")

while True:
    query = input("You: ")

    if query.lower() == "exit":
        break

    result = qa_chain.invoke({"query": query})

    print("\nAI:", result["result"], "\n")
