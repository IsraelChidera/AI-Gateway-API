from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.providers.gemini_provider import GeminiProvider


@pytest.mark.asyncio
async def test_gemini_provider_maps_response_to_provider_reply(monkeypatch):
    provider = GeminiProvider(api_key="test-key", model="gemini-2.5-flash")

    fake_response = SimpleNamespace(
        text="hello there",
        usage_metadata=SimpleNamespace(prompt_token_count=5, candidates_token_count=7),
    )
    provider.client.aio.models.generate_content = AsyncMock(return_value=fake_response)

    reply = await provider.chat("hi")

    assert reply.text == "hello there"
    assert reply.model == "gemini-2.5-flash"
    assert reply.input_tokens == 5
    assert reply.output_tokens == 7
