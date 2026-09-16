from fastapi import APIRouter, Depends

from app.models.chat.chat_request import ChatRequest
from app.models.chat.chat_response import ChatResponse
from app.providers.mock_provider import MockProvider
from app.services.ai_service import AIService

router = APIRouter(tags=["chat"])

def get_ai_service() -> AIService:
    return AIService(MockProvider())


@router.post("/chat", response_model=ChatResponse)
async def chat(chat_request: ChatRequest, service: AIService = Depends(get_ai_service)):
    return await service.chat(chat_request)
