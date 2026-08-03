from fastapi import APIRouter
from app.services import pipeline
from app.schemas import SentimentRequest, SentimentResponse

router = APIRouter(tags=["nlp"])


@router.post("/analyze-sentiment", response_model=SentimentResponse)
async def analyze_sentiment(request: SentimentRequest):
    return pipeline.analyze_sentiment(request.text)
