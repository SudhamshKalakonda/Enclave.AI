from core.llm import get_fast_llm
from utils.audit_logger import log_agent_action
from langchain.prompts import ChatPromptTemplate

COMPLIANCE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an RBI compliance officer AI for an Indian bank.
Your job is to review AI-generated answers and flag any compliance concerns.

Check for:
- Definitive financial decisions without human approval
- Violations of RBI KYC guidelines
- Missing risk disclosures
- Regulatory requirement gaps

Output format:
COMPLIANCE_STATUS: PASS or FLAG
RISK_LEVEL: LOW, MEDIUM, or HIGH  
NOTES: Brief explanation"""),
    ("human", """Original question: {question}

AI Answer to review:
{answer}

Assess compliance.""")
])

def compliance_agent(state: dict) -> dict:
    question = state["question"]
    answer = state.get("answer", "")
    print(f"[Compliance Agent] Reviewing answer for compliance")
    llm = get_fast_llm()
    chain = COMPLIANCE_PROMPT | llm
    compliance_result = chain.invoke({
        "question": question,
        "answer": answer
    })
    needs_approval = "FLAG" in compliance_result.content or "HIGH" in compliance_result.content
    log_agent_action(
        agent_name="compliance_agent",
        action="compliance_check",
        input_data=answer[:300],
        output_data=compliance_result.content
    )
    return {
        **state,
        "compliance_result": compliance_result.content,
        "needs_human_approval": needs_approval
    }