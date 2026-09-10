import os
import chromadb
from chromadb.utils import embedding_functions
from groq import Groq
import joblib
import pandas as pd

# 1. Load Scikit-Learn Model
model = joblib.load("churn_model.joblib")

# 2. Initialize ChromaDB
chroma_client = chromadb.PersistentClient(path="./chroma_db")
embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)
collection = chroma_client.get_or_create_collection(
    name="enterprise_knowledge", embedding_function=embedding_func
)

# 3. Initialize Groq LLM Client
# PASTE YOUR ACTUAL GROQ KEY HERE IF NOT SET IN ENVIRONMENT:
# Before (INSECURE):
# groq_client = Groq(api_key="gsk_xxxxxxxxxxxx...")

# After (SECURE):
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY)
groq_client = None
if GROQ_API_KEY and not GROQ_API_KEY.startswith("YOUR_GROQ"):
    try:
        groq_client = Groq(api_key=GROQ_API_KEY)
    except Exception as e:
        print(f"Error initializing Groq client: {e}")


def predict_customer_churn(credit_score, age, tenure, balance, num_products):
    input_data = pd.DataFrame(
        [[credit_score, age, tenure, balance, num_products]],
        columns=["credit_score", "age", "tenure", "balance", "num_products"],
    )
    prediction = model.predict(input_data)[0]
    probabilities = model.predict_proba(input_data)[0]
    churn_prob = float(probabilities[1])

    risk_label = "High Risk" if prediction == 1 else "Low Risk"
    return risk_label, round(churn_prob * 100, 2)


def search_knowledge_base(query: str, n_results: int = 2):
    # Step A: Vector Retrieval from ChromaDB
    try:
        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        
        if not documents:
            return {
                "answer": "No relevant context found in vector database.",
                "sources": []
            }
            
        retrieved_context = "\n\n".join(documents)
        sources = [
            {
                "document": meta.get("source", "Default Base Document") if meta else "Default Base Document",
                "chunk_index": meta.get("chunk_index", 0) if meta else 0,
                "snippet": doc[:180] + "..." if len(doc) > 180 else doc
            }
            for doc, meta in zip(documents, metadatas)
        ]
    except Exception as e:
        return {
            "answer": f"ChromaDB retrieval error: {str(e)}",
            "sources": []
        }

    # Step B: LLM Generation via Groq
    if not groq_client:
        return {
            "answer": f"[Retrieved Context]: {retrieved_context}\n\n(Note: Groq client not active.)",
            "sources": sources
        }

    try:
        prompt = f"""
        You are an enterprise AI assistant. Answer the user question based ONLY on the following context.

        Context:
        {retrieved_context}

        User Question: {query}

        Answer:
        """

        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="openai/gpt-oss-20b"
        )
        return {
            "answer": chat_completion.choices[0].message.content,
            "sources": sources
        }
    except Exception as e:
        return {
            "answer": f"Groq API Error: {str(e)}",
            "sources": sources
        }
        
import uuid

def ingest_document_text(text: str, filename: str, chunk_size: int = 1000, overlap: int = 100):
    """Increases chunk size to 1000 characters to reduce embedding inference overhead."""
    if not text.strip():
        return 0

    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap

    ids = [f"{filename}_{uuid.uuid4().hex[:8]}" for _ in chunks]
    metadatas = [{"source": filename, "chunk_index": i} for i in range(len(chunks))]

    collection.add(
        documents=chunks,
        ids=ids,
        metadatas=metadatas
    )
    return len(chunks)

def get_knowledge_base_stats():
    """Returns chunk count and unique document sources in ChromaDB."""
    try:
        data = collection.get()
        count = len(data.get("ids", []))
        metadatas = data.get("metadatas", []) or []
        unique_sources = sorted(list({meta.get("source") for meta in metadatas if meta and "source" in meta}))
        return {"total_chunks": count, "documents": unique_sources}
    except Exception as e:
        return {"total_chunks": 0, "documents": [], "error": str(e)}

def purge_knowledge_base():
    """Deletes all embeddings and resets the collection."""
    global collection
    try:
        chroma_client.delete_collection(name="enterprise_knowledge_base")
        collection = chroma_client.get_or_create_collection(name="enterprise_knowledge_base")
        return True
    except Exception as e:
        print(f"Error purging collection: {e}")
        return False