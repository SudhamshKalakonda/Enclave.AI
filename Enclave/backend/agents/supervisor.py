from langgraph.graph import StateGraph, END
from typing import TypedDict, List
from langchain.schema import Document
from agents.retrieval_agent import retrieval_agent
from agents.reasoning_agent import reasoning_agent
from agents.compliance_agent import compliance_agent
from utils.audit_logger import log_event

class EnclaveState(TypedDict):
    question: str
    retrieved_docs: List[Document]
    context: str
    retrieval_assessment: str
    answer: str
    compliance_result: str
    needs_human_approval: bool
    final_response: str

def should_proceed_to_reasoning(state: dict) -> str:
    assessment = state.get("retrieval_assessment", "")
    if "INSUFFICIENT" in assessment:
        return "insufficient"
    return "sufficient"

def finalize_response(state: dict) -> dict:
    needs_approval = state.get("needs_human_approval", False)
    answer = state.get("answer", "")
    compliance = state.get("compliance_result", "")
    if needs_approval:
        final = f"""⚠️ HUMAN APPROVAL REQUIRED

{answer}

---
Compliance Review: {compliance}

This response has been flagged for human review before action is taken."""
    else:
        final = f"""{answer}

---
✅ Compliance Check: PASSED
{compliance}"""
    log_event("final_response", {
        "question": state["question"],
        "needs_approval": needs_approval,
        "response_length": len(final)
    })
    return {**state, "final_response": final}

def handle_insufficient(state: dict) -> dict:
    return {
        **state,
        "answer": "I could not find sufficient information in the uploaded documents to answer this question accurately. Please upload relevant documents first.",
        "compliance_result": "COMPLIANCE_STATUS: PASS\nRISK_LEVEL: LOW\nNOTES: Insufficient data response",
        "needs_human_approval": False
    }

def build_enclave_graph():
    graph = StateGraph(EnclaveState)
    graph.add_node("retrieval", retrieval_agent)
    graph.add_node("reasoning", reasoning_agent)
    graph.add_node("compliance", compliance_agent)
    graph.add_node("finalize", finalize_response)
    graph.add_node("insufficient", handle_insufficient)
    graph.set_entry_point("retrieval")
    graph.add_conditional_edges(
        "retrieval",
        should_proceed_to_reasoning,
        {
            "sufficient": "reasoning",
            "insufficient": "insufficient"
        }
    )
    graph.add_edge("reasoning", "compliance")
    graph.add_edge("compliance", "finalize")
    graph.add_edge("insufficient", "finalize")
    graph.add_edge("finalize", END)
    return graph.compile()

enclave_graph = build_enclave_graph()

def run_enclave(question: str) -> dict:
    initial_state = {
        "question": question,
        "retrieved_docs": [],
        "context": "",
        "retrieval_assessment": "",
        "answer": "",
        "compliance_result": "",
        "needs_human_approval": False,
        "final_response": ""
    }
    result = enclave_graph.invoke(initial_state)
    return result