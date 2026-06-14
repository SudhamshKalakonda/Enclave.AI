from core.llm import get_llm, get_streaming_llm
from utils.audit_logger import log_agent_action
from langchain.prompts import ChatPromptTemplate
from typing import AsyncGenerator

REASONING_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert AI analyst for an Indian BFSI company.
You analyze documents and answer questions accurately based only on the provided context.
     Answer questions clearly and concisely based only on the provided context.

Rules:
- Answer only from the provided context
- If context is insufficient, say so clearly
- Be precise and professional
- Cite which source you used
- Use clear headings where needed
- Use bullet points for lists
- Be specific and cite page numbers
- Keep answers focused and professional
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

async def reasoning_agent_stream(question: str, context: str) -> AsyncGenerator[str, None]:
    print(f"[Reasoning Agent] Streaming answer for: {question}")
    llm = get_streaming_llm()
    prompt = REASONING_PROMPT.format_messages(
        question=question,
        context=context
    )
    async for chunk in llm.astream(prompt):
        if chunk.content:
            yield chunk.content