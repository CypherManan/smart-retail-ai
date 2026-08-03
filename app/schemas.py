from pydantic import BaseModel
from typing import Optional, Dict


class SentimentRequest(BaseModel):
    text: str


class SentimentResponse(BaseModel):
    sentiment: str
    confidence: float
    scores: Dict[str, float]


class ChatbotRequest(BaseModel):
    message: str


class ChatbotResponse(BaseModel):
    reply: str
    intent: str
    confidence: float


class FaceRecognitionResponse(BaseModel):
    status: str
    customer_id: Optional[str] = None
    distance: Optional[float] = None
    error: Optional[str] = None


class ProductClassificationResponse(BaseModel):
    category: Optional[str] = None
    confidence: Optional[float] = None
    error: Optional[str] = None


class DashboardStatsResponse(BaseModel):
    total_visits: int
    returning_customers: int
    unique_visitors_seen: int
    sentiment_breakdown: Dict[str, int]
    total_feedback_analyzed: int
