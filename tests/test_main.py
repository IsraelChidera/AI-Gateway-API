from fastapi.testclient import TestClient

from app.main import app
from app.api.routes.chat import get_ai_service
from app.models.chat.chat_response import ChatResponse, Usage
from app.providers.base import AIProvider, ProviderReply

client = TestClient(app)


class FakeProvider(AIProvider):
    async def chat(self, message: str) -> ProviderReply:
        return ProviderReply(
            text=f"echo: {message}",
            model="fake-model",
            input_tokens=1,
            output_tokens=2,
        )


def override_get_ai_service():
    from app.services.ai_service import AIService

    return AIService(FakeProvider())


app.dependency_overrides[get_ai_service] = override_get_ai_service


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_chat_returns_provider_answer():
    response = client.post("/chat", json={"message": "hello"})
    assert response.status_code == 200
    expected = ChatResponse(
        answer="echo: hello",
        model="fake-model",
        usage=Usage(input_tokens=1, output_tokens=2),
    )
    assert response.json() == expected.model_dump()


def test_chat_requires_message_field():
    response = client.post("/chat", json={})
    assert response.status_code == 422
