from fastapi import APIRouter, Depends

from app.models.chat.chat_request import ChatRequest
from app.models.chat.chat_response import ChatResponse
from app.providers.mock_provider import MockProvider
from app.providers.gemini_provider import GeminiProvider
from app.services.ai_service import AIService
from app.config import get_settings

router = APIRouter(tags=["chat"])

settings = get_settings()

# def get_ai_service() -> AIService:
#     return AIService(MockProvider())


def get_ai_service() -> AIService:
    return AIService(
        GeminiProvider(
            api_key=settings.gemini_api_key,
            model=settings.gemini_model,
            timeout=settings.ai_timeout,
            max_retries=settings.max_retries,
        )
    )


@router.post("/chat", response_model=ChatResponse)
async def chat(chat_request: ChatRequest, service: AIService = Depends(get_ai_service)):
    return await service.chat(chat_request)
