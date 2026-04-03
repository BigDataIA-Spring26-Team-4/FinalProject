"""Agentic chat endpoint — routes to LangGraph supervisor."""
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    response: str
    risk_score: float | None = None
    citations: list[dict] = []
    requires_hitl: bool = False


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a natural language query to the LangGraph supervisor agent."""
    # TODO: Invoke LangGraph supervisor with user message
    raise NotImplementedError
