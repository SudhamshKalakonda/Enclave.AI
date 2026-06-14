from fastapi.responses import StreamingResponse
from agents.reasoning_agent import reasoning_agent_stream
from core.rag import query_documents, format_context
from utils.audit_logger import log_query
import json
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
@router.post("/stream")
async def stream_query(request: QuestionRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    async def generate():
        question = request.question
        
        # Step 1 — send status
        yield f"data: {json.dumps({'type': 'status', 'content': 'Searching documents...'})}\n\n"
        
        # Step 2 — retrieve documents
        docs = query_documents(question, k=4)
        context = format_context(docs)
        
        yield f"data: {json.dumps({'type': 'status', 'content': 'Analyzing your question...'})}\n\n"
        
        # Step 3 — stream reasoning agent tokens
        full_answer = ""
        async for token in reasoning_agent_stream(question, context):
            full_answer += token
            yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"
        
        # Step 4 — run compliance check on full answer
        yield f"data: {json.dumps({'type': 'status', 'content': 'Checking compliance...'})}\n\n"
        
        from agents.compliance_agent import compliance_agent
        compliance_state = compliance_agent({
            "question": question,
            "answer": full_answer,
            "retrieved_docs": docs,
            "context": context,
            "retrieval_assessment": "SUFFICIENT",
            "compliance_result": "",
            "needs_human_approval": False,
            "final_response": ""
        })
        
        log_query(question, full_answer, [d.metadata.get("source", "") for d in docs])
        
        # Step 5 — send final compliance result
        yield f"data: {json.dumps({'type': 'compliance', 'content': compliance_state['compliance_result'], 'needs_approval': compliance_state['needs_human_approval']})}\n\n"
        
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )