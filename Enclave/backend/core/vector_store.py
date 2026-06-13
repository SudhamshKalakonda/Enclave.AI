from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from langchain_qdrant import QdrantVectorStore
from langchain_community.embeddings import HuggingFaceEmbeddings
from dotenv import load_dotenv
import os

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "enclave-docs")
EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"
VECTOR_SIZE = 768

def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"}
    )

def get_qdrant_client():
    return QdrantClient(url=QDRANT_URL)

def ensure_collection_exists():
    client = get_qdrant_client()
    collections = [c.name for c in client.get_collections().collections]
    if QDRANT_COLLECTION not in collections:
        client.create_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE
            )
        )
        print(f"Created collection: {QDRANT_COLLECTION}")
    else:
        print(f"Collection already exists: {QDRANT_COLLECTION}")

def get_vector_store():
    ensure_collection_exists()
    return QdrantVectorStore(
        client=get_qdrant_client(),
        collection_name=QDRANT_COLLECTION,
        embedding=get_embeddings()
    )

def get_retriever(k: int = 4):
    vector_store = get_vector_store()
    return vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k}
    )