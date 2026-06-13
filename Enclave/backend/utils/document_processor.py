import os
from pathlib import Path
from core.rag import ingest_bytes, ingest_document
from utils.audit_logger import log_document_ingestion

SUPPORTED_EXTENSIONS = [".pdf"]

def process_uploaded_file(file_bytes: bytes, filename: str) -> dict:
    ext = Path(filename).suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        return {
            "success": False,
            "error": f"Unsupported file type: {ext}. Only PDF supported."
        }
    try:
        metadata = {
            "filename": filename,
            "source": filename,
        }
        chunks = ingest_bytes(file_bytes, filename, metadata)
        log_document_ingestion(filename, chunks)
        return {
            "success": True,
            "filename": filename,
            "chunks_ingested": chunks,
            "message": f"Successfully processed {filename} into {chunks} chunks"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def process_file_from_path(file_path: str) -> dict:
    filename = os.path.basename(file_path)
    ext = Path(filename).suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        return {
            "success": False,
            "error": f"Unsupported file type: {ext}"
        }
    try:
        chunks = ingest_document(file_path, {"source": filename, "filename": filename})
        log_document_ingestion(filename, chunks)
        return {
            "success": True,
            "filename": filename,
            "chunks_ingested": chunks,
            "message": f"Successfully processed {filename} into {chunks} chunks"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }