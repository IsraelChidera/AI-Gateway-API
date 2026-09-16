from google import genai

from app.providers.base import AIProvider, ProviderReply


class GeminiProvider(AIProvider):
    def __init__(self, api_key: str, model: str):
        self.client = genai.Client(api_key=api_key)
        self.model = model

    async def chat(self, message: str) -> ProviderReply:
        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=message,
        )
        usage = response.usage_metadata
        return ProviderReply(
            text=response.text,
            model=self.model,
            input_tokens=usage.prompt_token_count or 0,
            output_tokens=usage.candidates_token_count or 0,
        )
