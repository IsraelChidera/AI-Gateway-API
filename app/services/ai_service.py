from app.models.chat.chat_request import ChatRequest
from app.models.chat.chat_response import ChatResponse, Usage
from app.providers.base import AIProvider
import time


class AIService:
    def __init__(self, provider: AIProvider):
        self.provider = provider

    async def chat(self, chat_request: ChatRequest) -> ChatResponse:
        start_time = time.perf_counter()
        reply = await self.provider.chat(chat_request.message)
        end_time = time.perf_counter()

        latency_ms = (end_time - start_time) * 1000

        return ChatResponse(
            latency=latency_ms,
            answer=reply.text,
            model=reply.model,
            usage=Usage(input_tokens=reply.input_tokens, output_tokens=reply.output_tokens),
        )
             