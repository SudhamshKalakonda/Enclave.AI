from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Enclave API",
    description="Privacy-first enterprise AI agent for Indian BFSI",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")

@app.get("/")
def root():
    return {
        "name": "Enclave",
        "status": "running",
        "version": "1.0.0",
        "description": "Privacy-first enterprise AI agent"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}