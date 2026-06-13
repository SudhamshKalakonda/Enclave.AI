from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from agents.supervisor import run_enclave
from utils.document_processor import process_uploaded_file
from utils.audit_logger import get_audit_trail, log_human_approval

router = APIRouter()

class QuestionRequest(BaseModel):
    question: str

class ApprovalRequest(BaseModel):
    decision_id: str
    decision: str
    approved_by: str

@router.post("/query")
async def query(request: QuestionRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    try:
        result = run_enclave(request.question)
        return {
            "success": True,
            "answer": result["final_response"],
            "needs_human_approval": result["needs_human_approval"],
            "compliance_result": result["compliance_result"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files supported")
    try:
        file_bytes = await file.read()
        result = process_uploaded_file(file_bytes, file.filename)
        if not result["success"]:
            raise HTTPException(status_code=422, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/approve")
async def approve_decision(request: ApprovalRequest):
    entry = log_human_approval(
        decision_id=request.decision_id,
        decision=request.decision,
        approved_by=request.approved_by
    )
    return {"success": True, "logged": entry}

@router.get("/audit")
async def get_audit(date: str = None):
    trail = get_audit_trail(date)
    return {"success": True, "count": len(trail), "entries": trail}

@router.get("/status")
async def status():
    return {
        "success": True,
        "services": {
            "llm": "ollama/llama3.1:8b",
            "vector_db": "qdrant/localhost:6333",
            "embeddings": "BAAI/bge-base-en-v1.5",
            "agents": ["retrieval", "reasoning", "compliance"]
        }
    }
