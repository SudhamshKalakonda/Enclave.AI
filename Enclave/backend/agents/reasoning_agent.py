from core.llm import get_llm
from utils.audit_logger import log_agent_action
from langchain.prompts import ChatPromptTemplate

REASONING_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert AI analyst for an Indian BFSI company.
You analyze documents and answer questions accurately based only on the provided context.

Rules:
- Answer only from the provided context
- If context is insufficient, say so clearly  
- Be precise and professional
- Cite which source you used
- For financial decisions, always recommend human review"""),
    ("human", """Question: {question}

Context from documents:
{context}

Provide a clear, structured answer.""")
])

def reasoning_agent(state: dict) -> dict:
    question = state["question"]
    context = state.get("context", "")
    print(f"[Reasoning Agent] Analyzing question: {question}")
    llm = get_llm()
    chain = REASONING_PROMPT | llm
    response = chain.invoke({
        "question": question,
        "context": context
    })
    log_agent_action(
        agent_name="reasoning_agent",
        action="analyze_and_answer",
        input_data=question,
        output_data=response.content
    )
    return {
        **state,
        "answer": response.content
    }