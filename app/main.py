import os
from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import APIKeyHeader

from app.routers import vision, nlp, chatbot
from app.services import pipeline  # triggers model loading once at startup
from app.schemas import DashboardStatsResponse

API_KEY = os.environ.get("API_KEY", "demo-key-123")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(key: str = Security(api_key_header)):
    if key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return key


app = FastAPI(
    title="Smart Retail & Customer Intelligence Platform",
    description="Face recognition, product classification, sentiment analysis, and a support chatbot behind one API.",
    version="1.0.0",
)

app.include_router(vision.router, dependencies=[Depends(verify_api_key)])
app.include_router(nlp.router, dependencies=[Depends(verify_api_key)])
app.include_router(chatbot.router, dependencies=[Depends(verify_api_key)])


@app.get("/dashboard/stats", response_model=DashboardStatsResponse, dependencies=[Depends(verify_api_key)])
async def dashboard_stats():
    return pipeline.get_dashboard_stats()


@app.get("/")
async def root():
    return {"message": "Smart Retail AI Platform is running. See /docs for API documentation."}
