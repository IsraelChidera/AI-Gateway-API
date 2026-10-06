from fastapi import APIRouter, Depends, HTTPException

from app.models.chat.chat_request import ChatRequest
from app.models.chat.chat_response import ChatResponse
from app.providers.base import ProviderTimeoutError
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


@router.post(
    "/chat",
    response_model=ChatResponse,
    status_code=200,
    summary="Send a message to the AI model and receive a response.",
    responses={
        200: {"description": "Successful response from the AI model."},
        400: {"description": "Bad request. The input message is invalid."},
        429: {"description": "Rate limit exceeded. Please try again later."},
        503: {
            "description": "Service unavailable. The AI provider is currently unavailable."
        },
        504: {
            "description": "Gateway timeout. The AI provider did not respond in time."
        },
        500: {"description": "Internal server error. An unexpected error occurred."},
    },
)
async def chat(chat_request: ChatRequest, service: AIService = Depends(get_ai_service)):
    try:
        return await service.chat(chat_request)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )
    except ProviderTimeoutError:
        raise HTTPException(
            status_code=504, detail="The AI provider did not respond in time."
        )
    # except ProviderUnavailableError:
    #     raise HTTPException(
    #         status_code=503, detail="The AI provider is currently unavailable."
    #     )
