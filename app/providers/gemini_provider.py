import random

from google import genai
from google.genai import errors

import asyncio

from app.providers.base import (
    AIProvider,
    ProviderReply,
    ProviderTimeoutError,
    ProviderUnavailableError,
    ProviderRateLimitError,
    ProviderError,
)

RETRYABLE_CODES = {429, 500, 503}


class GeminiProvider(AIProvider):
    def __init__(
        self, api_key: str, model: str, timeout: int = 60, max_retries: int = 3
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
                    timeout=self.timeout,
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
                raise ProviderTimeoutError(f"The AI provider did not respond within {self.timeout} seconds.")                         
            except errors.APIError as e:
                if e.code not in RETRYABLE_CODES:
                    raise ProviderError(f"Gemini error {e.code}: {e.message}") from e
                if attempt == self.max_retries:
                    if e.code == 429:
                        raise ProviderRateLimitError("Gemini rate limit exceeded") from e
                    raise ProviderUnavailableError("Gemini is temporarily unavailable") from e
                await asyncio.sleep(2 ** attempt + random.uniform(0, 0.5))                 
            except Exception as e:
                            raise ProviderError(f"An unexpected error occurred: {str(e)}") 