from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.rag.retriever import retrieve
from backend.rag.generator import generate_response
import time

router = APIRouter()

class ChatRequest(BaseModel):
    query: str
    top_k: int = 3

class ChatResponse(BaseModel):
    query: str
    response: str
    sources: list[str]
    latency_ms: float

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    start = time.time()

    chunks = retrieve(request.query, top_k=request.top_k)
    if not chunks:
        raise HTTPException(status_code=404, detail="No relevant documents found")

    response = generate_response(request.query, chunks)

    latency_ms = (time.time() - start) * 1000

    return ChatResponse(
        query=request.query,
        response=response,
        sources=list(set(c["source"] for c in chunks)),
        latency_ms=round(latency_ms, 2)
    )

@router.get("/health")
async def health():
    return {"status": "ok", "service": "dawrek-ai"}
