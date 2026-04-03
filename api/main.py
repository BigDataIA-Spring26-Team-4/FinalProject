"""FastAPI application — Maritime AI Sentinel."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import alerts, chat, risk, vessels

app = FastAPI(
    title="Maritime AI Sentinel",
    description="Maritime supply chain risk intelligence API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(risk.router, prefix="/api/v1/risk", tags=["Risk"])
app.include_router(vessels.router, prefix="/api/v1/vessels", tags=["Vessels"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["Alerts"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])


@app.get("/health")
async def health():
    return {"status": "ok"}
