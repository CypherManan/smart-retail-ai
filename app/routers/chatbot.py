from fastapi import APIRouter
from app.services import pipeline
from app.schemas import ChatbotRequest, ChatbotResponse

router = APIRouter(tags=["chatbot"])


@router.post("/chatbot", response_model=ChatbotResponse)
async def chatbot(request: ChatbotRequest):
    return pipeline.chatbot_reply(request.message)
