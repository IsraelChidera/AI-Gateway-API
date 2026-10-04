from google import genai
import asyncio

from app.providers.base import (
    AIProvider,
    ProviderReply,
    ProviderTimeoutError,
    ProviderUnavailableError,
    ProviderRateLimitError,
    ProviderError,
)

RETRYABLE_CODES = {429, 503, 504}


class GeminiProvider(AIProvider):
    def __init__(
        self, api_key: str, model: str, timeout: int = 30, max_retries: int = 3
    ):
        self.client = genai.Client(api_key=api_key)
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries

    async def chat(self, message: str) -> ProviderReply:
        for attempt in range(self.max_retries + 1):
            try:
                response = await asyncio.wait_for(
                    self.client.aio.models.generate_content(
                        model=self.model,
                        contents=message,
                    ),
                    timeout=self.timeout
                )
                # response = await
                usage = response.usage_metadata
                return ProviderReply(
                    text=response.text,
                    model=self.model,
                    input_tokens=usage.prompt_token_count or 0,
                    output_tokens=usage.candidates_token_count or 0,
                )
            except TimeoutError:
                return ProviderReply(
                    text="The request timed out. Please try again later.",
                    model=self.model,
                    input_tokens=0,
                    output_tokens=0,
                )
            except Exception as e:
                return ProviderReply(
                    text=f"An error occurred: {str(e)}",
                    model=self.model,
                    input_tokens=0,
                    output_tokens=0,
                )
            # await asyncio.sleep(2 ** at tempt + random.uniform(0, 1))  # Exponential backoff with jitter
