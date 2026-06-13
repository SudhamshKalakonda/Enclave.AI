from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import Document
from core.vector_store import get_vector_store, get_retriever
from dotenv import load_dotenv
import os
import tempfile

load_dotenv()

CHUNK_SIZE = 512
CHUNK_OVERLAP = 50

def get_text_splitter():
    return RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""],
    )

def load_and_split_pdf(file_path: str) -> list[Document]:
    loader = PyPDFLoader(file_path)
    pages = loader.load()
    splitter = get_text_splitter()
    chunks = splitter.split_documents(pages)
    print(f"Loaded {len(pages)} pages → {len(chunks)} chunks")
    return chunks

def ingest_document(file_path: str, metadata: dict = {}) -> int:
    chunks = load_and_split_pdf(file_path)
    for chunk in chunks:
        chunk.metadata.update(metadata)
    vector_store = get_vector_store()
    vector_store.add_documents(chunks)
    print(f"Ingested {len(chunks)} chunks into Qdrant")
    return len(chunks)

def ingest_bytes(file_bytes: bytes, filename: str, metadata: dict = {}) -> int:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name
    try:
        return ingest_document(tmp_path, metadata)
    finally:
        os.unlink(tmp_path)

def query_documents(question: str, k: int = 4) -> list[Document]:
    retriever = get_retriever(k=k)
    docs = retriever.invoke(question)
    return docs

def format_context(docs: list[Document]) -> str:
    context_parts = []
    for i, doc in enumerate(docs):
        source = doc.metadata.get("source", "Unknown")
        page = doc.metadata.get("page", "?")
        context_parts.append(
            f"[Source {i+1}: {os.path.basename(source)}, Page {page}]\n{doc.page_content}"
        )
    return "\n\n---\n\n".join(context_parts)