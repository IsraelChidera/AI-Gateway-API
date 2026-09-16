from app.models.chat.chat_request import ChatRequest
from app.models.chat.chat_response import ChatResponse, Usage
from app.providers.base import AIProvider


class AIService:
    def __init__(self, provider: AIProvider):
        self.provider = provider

    async def chat(self, chat_request: ChatRequest) -> ChatResponse:
        reply = await self.provider.chat(chat_request.message)
        return ChatResponse(
            answer=reply.text,
            model=reply.model,
            usage=Usage(input_tokens=reply.input_tokens, output_tokens=reply.output_tokens),
        )
