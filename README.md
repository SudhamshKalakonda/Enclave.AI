# Enclave.AI

> Privacy-first enterprise AI agent for Indian BFSI — 100% on-premise, zero data leaves your infrastructure.

![Python](https://img.shields.io/badge/Python-3.11-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green) ![LangGraph](https://img.shields.io/badge/LangGraph-0.2.50-orange) ![Next.js](https://img.shields.io/badge/Next.js-16-black)

## The Problem

Indian banks, NBFCs, and insurance companies cannot use ChatGPT or cloud AI for sensitive documents — RBI regulations prohibit customer financial data from leaving their servers. But they still need AI to process thousands of loan applications, compliance documents, and KYC files daily.

## The Solution

Enclave runs entirely on your own hardware. No internet. No cloud. No data ever leaves your server.

## Architecture
Document Upload

↓

RAG Pipeline (PyPDF → Chunking → BGE Embeddings → Qdrant)

↓

LangGraph Multi-Agent System

├── Retrieval Agent   — semantic search across documents

├── Reasoning Agent   — Llama 3.1 8B analysis

└── Compliance Agent  — RBI guideline validation

↓

Immutable Audit Logger (RBI compliance trail)

↓

FastAPI + Next.js UI

## Tech Stack

| Layer | Technology |
|---|---|
| Local LLM | Ollama + Llama 3.1 8B |
| Vector Database | Qdrant (Docker, fully local) |
| Embeddings | BAAI/bge-base-en-v1.5 (768-dim) |
| Agent Framework | LangGraph 0.2.50 |
| Backend | FastAPI + Python 3.11 |
| Frontend | Next.js 16 + Tailwind |
| Containerization | Docker |

## Key Features

- **100% On-Premise** — Llama runs via Ollama, vectors stored in local Qdrant
- **Multi-Agent Pipeline** — LangGraph orchestrates retrieval, reasoning, and compliance agents
- **RBI Compliance** — immutable audit logs of every agent decision with timestamps
- **Human Approval Gates** — high-risk decisions flagged for human review before action
- **PDF Intelligence** — upload any financial document and query it in natural language

## Running Locally

**Prerequisites:** Ollama, Docker, Python 3.11, Node.js

```bash
# 1. Pull the LLM
ollama pull llama3.1:8b

# 2. Start Qdrant
docker run -d --name qdrant -p 6333:6333 qdrant/qdrant

# 3. Backend
cd Enclave/backend
conda create -n enclave python=3.11 -y
conda activate enclave
pip install -r requirements.txt
cp .env.example .env
uvicorn api.main:app --reload --port 8000

# 4. Frontend
cd ../../frontend
npm install
npm run dev
```

Open `http://localhost:3000`

## Use Case

Upload a loan application PDF → Ask "Does this applicant meet RBI KYC requirements?" → Enclave retrieves relevant document sections, reasons over them using a local LLM, checks compliance, and returns a structured answer with full audit trail — all without any data leaving your server.

## Author

Sudhamsh Kalakonda — [Portfolio](https://sudhamshkalakonda.com) | [LinkedIn](https://linkedin.com/in/sudhamshkalakonda)
EOF
