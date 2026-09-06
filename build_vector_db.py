import chromadb
from chromadb.utils import embedding_functions

# Initialize persistent ChromaDB client in the project folder
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Use sentence-transformers embedding function
embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

# Get or create collection
collection = chroma_client.get_or_create_collection(
    name="enterprise_knowledge",
    embedding_function=embedding_func
)

# Enterprise knowledge documents
documents = [
    "High-risk customers are defined as users with a credit score below 600 and account balances over $50,000.",
    "For churn retention, issue a 15% promotional discount or offer a dedicated account manager.",
    "Accounts inactive for more than 90 days trigger an automated re-engagement email sequence.",
    "Premium tier support guarantees a 1-hour response time for critical technical issues."
]

ids = ["doc1", "doc2", "doc3", "doc4"]

# Upsert documents (inserts or updates existing entries safely)
collection.upsert(
    documents=documents,
    ids=ids
)

print("✅ Vector database populated and saved to './chroma_db'!")