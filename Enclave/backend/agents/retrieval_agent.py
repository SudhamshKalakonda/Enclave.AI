from langchain.schema import Document
from core.rag import query_documents, format_context
from core.llm import get_fast_llm
from utils.audit_logger import log_agent_action
from langchain.prompts import ChatPromptTemplate

RETRIEVAL_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a document retrieval specialist for an Indian BFSI company.
Your job is to analyze retrieved document chunks and determine if they contain 
enough information to answer the user's question.

Be concise. Output only:
1. SUFFICIENT - if chunks contain enough information
2. INSUFFICIENT - if more context is needed

Then provide a one line reason."""),
    ("human", "Question: {question}\n\nRetrieved chunks:\n{context}")
])

def retrieval_agent(state: dict) -> dict:
    question = state["question"]
    print(f"[Retrieval Agent] Searching for: {question}")
    docs = query_documents(question, k=4)
    context = format_context(docs)
    llm = get_fast_llm()
    chain = RETRIEVAL_PROMPT | llm
    assessment = chain.invoke({
        "question": question,
        "context": context
    })
    log_agent_action(
        agent_name="retrieval_agent",
        action="retrieve_and_assess",
        input_data=question,
        output_data=assessment.content
    )
    return {
        **state,
        "retrieved_docs": docs,
        "context": context,
        "retrieval_assessment": assessment.content
    }