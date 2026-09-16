import hashlib
import json
from pathlib import Path

from app.providers.base import AIProvider, ProviderReply

_MOCK_DATA_PATH = Path(__file__).resolve().parent.parent / "models" / "mock-model.json"
_MOCK_RESPONSES = json.loads(_MOCK_DATA_PATH.read_text(encoding="utf-8"))


class MockProvider(AIProvider):
    """Canned provider backed by mock-model.json, no external calls."""

    async def chat(self, message: str) -> ProviderReply:
        # Deterministic pick: same message always maps to the same canned entry.
        digest = hashlib.md5(message.encode("utf-8")).hexdigest()
        index = int(digest, 16) % len(_MOCK_RESPONSES)
        entry = _MOCK_RESPONSES[index]

        return ProviderReply(
            text=entry["answer"],
            model="mock-model",
            input_tokens=entry["input_tokens"],
            output_tokens=entry["output_tokens"],
        )
