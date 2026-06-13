import json
import os
from datetime import datetime
from pathlib import Path

LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

def log_event(event_type: str, data: dict) -> dict:
    entry = {
        "id": f"{event_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event_type": event_type,
        "data": data
    }
    log_file = LOG_DIR / f"{datetime.utcnow().strftime('%Y-%m-%d')}.jsonl"
    with open(log_file, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry

def log_agent_action(agent_name: str, action: str, input_data: str, output_data: str) -> dict:
    return log_event("agent_action", {
        "agent": agent_name,
        "action": action,
        "input": input_data[:500],
        "output": output_data[:500]
    })

def log_document_ingestion(filename: str, chunks: int) -> dict:
    return log_event("document_ingestion", {
        "filename": filename,
        "chunks_created": chunks
    })

def log_query(question: str, answer: str, sources: list) -> dict:
    return log_event("query", {
        "question": question,
        "answer": answer[:500],
        "sources": sources
    })

def log_human_approval(decision_id: str, decision: str, approved_by: str) -> dict:
    return log_event("human_approval", {
        "decision_id": decision_id,
        "decision": decision,
        "approved_by": approved_by,
        "approved_at": datetime.utcnow().isoformat() + "Z"
    })

def get_audit_trail(date: str = None) -> list:
    if not date:
        date = datetime.utcnow().strftime('%Y-%m-%d')
    log_file = LOG_DIR / f"{date}.jsonl"
    if not log_file.exists():
        return []
    with open(log_file, "r") as f:
        return [json.loads(line) for line in f.readlines()]