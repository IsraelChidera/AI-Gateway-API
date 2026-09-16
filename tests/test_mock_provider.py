import json
from pathlib import Path

import pytest

from app.providers.mock_provider import MockProvider

MOCK_DATA_PATH = Path(__file__).resolve().parent.parent / "app" / "models" / "mock-model.json"


@pytest.mark.asyncio
async def test_mock_provider_answer_comes_from_source_file():
    provider = MockProvider()
    entries = json.loads(MOCK_DATA_PATH.read_text(encoding="utf-8"))

    reply = await provider.chat("hello")

    matches = [e for e in entries if e["answer"] == reply.text]
    assert matches, "mock answer should be one of the entries in mock-model.json"
    assert reply.model == "mock-model"
    assert reply.input_tokens == matches[0]["input_tokens"]
    assert reply.output_tokens == matches[0]["output_tokens"]


@pytest.mark.asyncio
async def test_mock_provider_is_deterministic_per_message():
    provider = MockProvider()
    first = await provider.chat("what is RAG?")
    second = await provider.chat("what is RAG?")
    assert first == second
