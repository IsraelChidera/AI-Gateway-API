# AI Gateway API

A lightweight, async **AI gateway** built with **FastAPI**. It sits between your applications and large language model providers, exposing **one stable, unified API** no matter which model is behind it.

Clients send a simple request. The gateway routes it to the configured provider (currently Google **Gemini**), handles timeouts, retries and rate limits, and returns a **normalized response** with the answer, latency and token usage.

```
   Your apps                AI Gateway                     LLM providers
 ┌───────────┐       ┌──────────────────────┐        ┌──────────────────┐
 │ Web / API │       │  • Unified /chat API │        │  Google Gemini   │
 │ Mobile    │ ────▶ │  • Retries + backoff │ ────▶  │  Mock (offline)  │
 │ Services  │       │  • Timeouts          │        │  …more to come   │
 └───────────┘       │  • Error mapping     │        └──────────────────┘
                     │  • Usage + latency   │
                     └──────────────────────┘
```

---

## Why a gateway?

Calling an LLM SDK directly from every service spreads the same concerns everywhere: API keys, retry logic, error handling, cost tracking. This gateway centralizes them:

| Concern              | Without a gateway                       | With this gateway                                      |
| -------------------- | --------------------------------------- | ------------------------------------------------------ |
| **Provider lock-in** | SDK calls hard-coded in every service   | Swap providers behind one `AIProvider` interface       |
| **Reliability**      | Each client writes its own retries      | Built-in exponential backoff with jitter               |
| **Errors**           | Raw, provider-specific SDK exceptions   | Consistent HTTP status codes (`429`, `503`, `504`, …)  |
| **Observability**    | Usage scattered or untracked            | Every response reports latency and token usage         |
| **Secrets**          | API keys copied into many apps          | Keys live in one place, the gateway                    |

---

## Features

- **Unified chat endpoint**: `POST /chat` with the same request/response shape for every provider
- **Provider abstraction**: any model plugs in by implementing a single `chat()` method
  - `GeminiProvider`: Google Gemini through the official `google-genai` SDK
  - `MockProvider`: deterministic offline replies for development and testing
- **Resilience**
  - Configurable per-request timeout
  - Automatic retries on transient errors (`429`, `500`, `503`) with exponential backoff and jitter
- **Error normalization**: provider failures are translated into standard HTTP responses, including `Retry-After` on rate limits
- **Usage metering**: input/output token counts and end-to-end latency returned with every reply
- **Health check**: `GET /health` for load balancers and uptime monitors
- **Retrieval toolkit (in progress)**: chunking, Gemini embeddings and cosine-similarity search as the base for RAG
- **Typed config and tests**: `pydantic-settings` for configuration, async `pytest` suite

---

## Architecture

```
 Request ──▶ API routes ──▶ AIService ──▶ AIProvider (interface)
            (validation)   (latency,         │
                            normalization)   ├── GeminiProvider
                                             └── MockProvider
                  ▲
                  └── Global exception handler: ProviderError ─▶ HTTP status
```

| Layer        | Location                    | Responsibility                                              |
| ------------ | --------------------------- | ----------------------------------------------------------- |
| **Routes**   | `app/api/routes/`           | HTTP interface, request validation, dependency injection    |
| **Service**  | `app/services/ai_service.py`| Times the call, shapes the unified `ChatResponse`           |
| **Providers**| `app/providers/`            | Talk to a specific LLM, apply retries/timeouts, raise typed errors |
| **Errors**   | `app/main.py`               | Map `ProviderError` subclasses to HTTP status codes         |

---

## Quick Start

### Prerequisites

- Python 3.11+
- A [Google Gemini API key](https://aistudio.google.com/app/apikey)

### 1. Clone and set up

```bash
git clone https://github.com/IsraelChidera/py-fast-api-day-3.git
cd py-fast-api-day-3

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
```

| Variable         | Description                                   | Default            |
| ---------------- | --------------------------------------------- | ------------------ |
| `GEMINI_API_KEY` | Google Gemini API key (**required**)          | —                  |
| `GEMINI_MODEL`   | Model the gateway routes chat requests to     | `gemini-3.8-flash` |
| `AI_TIMEOUT`     | Seconds before an upstream call times out     | `60`               |
| `MAX_RETRIES`    | Retry attempts for transient upstream errors  | `3`                |

### 3. Run the gateway

```bash
uvicorn app.main:app --reload
```

- API: `http://127.0.0.1:8000`
- Swagger UI: **http://127.0.0.1:8000/docs**
- ReDoc: **http://127.0.0.1:8000/redoc**

---

## API Reference

### `GET /health`

Returns `200 OK` while the gateway is up.

```json
{ "status": "ok" }
```

### `POST /chat`

Send a prompt through the gateway.

**Request**

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Explain RAG in one sentence."}'
```

| Field     | Type   | Required | Description             |
| --------- | ------ | -------- | ----------------------- |
| `message` | string | yes      | The prompt for the model |

**Response** `200 OK`

```json
{
  "latency": 842.17,
  "answer": "RAG combines document retrieval with text generation so answers are grounded in your data.",
  "model": "gemini-3.8-flash",
  "usage": {
    "input_tokens": 8,
    "output_tokens": 19
  }
}
```

| Field                 | Description                                       |
| --------------------- | ------------------------------------------------- |
| `latency`             | End-to-end provider latency in **milliseconds**   |
| `answer`              | The model's reply                                 |
| `model`               | Which model actually served the request           |
| `usage.input_tokens`  | Prompt tokens consumed                            |
| `usage.output_tokens` | Completion tokens generated                       |

### Error responses

Every upstream failure comes back in one shape, `{"detail": "<message>"}`, with a meaningful status code:

| Upstream situation                     | Gateway status              |
| -------------------------------------- | --------------------------- |
| Provider did not respond in time       | `504 Gateway Timeout`       |
| Provider still failing after retries   | `503 Service Unavailable`   |
| Rate limited after retries             | `429 Too Many Requests` + `Retry-After: 30` |
| Any other provider error               | `502 Bad Gateway`           |
| Malformed request body                 | `422 Unprocessable Entity`  |

---

## Adding a Provider

Each provider implements one async method and returns a `ProviderReply`:

```python
from app.providers.base import AIProvider, ProviderReply

class MyProvider(AIProvider):
    async def chat(self, message: str) -> ProviderReply:
        ...  # call your model here
        return ProviderReply(text=..., model=..., input_tokens=..., output_tokens=...)
```

Raise `ProviderTimeoutError`, `ProviderRateLimitError`, `ProviderUnavailableError` or `ProviderError` on failure, and the gateway maps them to HTTP responses for you. Then return your provider from `get_ai_service()` in `app/api/routes/chat.py`.

### Offline mode with the mock provider

```python
def get_ai_service() -> AIService:
    return AIService(MockProvider())
```

`MockProvider` hashes each message to pick a canned reply from `app/models/mock-model.json`, so responses are deterministic and cost nothing.

---

## Retrieval Toolkit (RAG foundations)

`app/retrievals/` contains the building blocks for grounding gateway answers in your own data:

| Module          | What it does                                                                 |
| --------------- | ---------------------------------------------------------------------------- |
| `chunking.py`   | `chunk_text()` splits text into overlapping windows so context isn't cut off |
| `embeddings.py` | `embed_documents()` / `embed_query()` via `gemini-embedding-001`             |
| `search.py`     | Cosine-similarity ranking that returns the top-k most relevant chunks        |

Run them from the project root as modules:

```bash
python -m app.retrievals.chunking
python -m app.retrievals.search
```

> Running a file directly (e.g. `python app/retrievals/search.py`) fails with `ModuleNotFoundError: No module named 'app'`.

---

## Project Structure

```
app/
├── main.py                 # App entry point, routers, global error handler
├── config.py               # Environment-based settings
├── api/routes/             # /chat and /health endpoints
├── models/chat/            # Unified request / response schemas
├── providers/              # AIProvider interface + Gemini and Mock implementations
├── services/               # AIService: orchestration, latency, normalization
└── retrievals/             # Chunking, embeddings, semantic search
tests/                      # Async pytest suite
```

---

## Testing

```bash
pytest
```

No real API key or network access is needed: `tests/conftest.py` sets a dummy key, and async tests run automatically (`asyncio_mode = "auto"`).

---

## Roadmap

- [ ] Additional providers (OpenAI, Anthropic Claude, local models)
- [ ] Provider selection and fallback through configuration
- [ ] Gateway API keys / client authentication
- [ ] Per-client rate limiting and usage quotas
- [ ] Response caching
- [ ] Streaming responses
- [ ] Retrieval-augmented `/chat` with a vector store
- [ ] Docker image and deployment guide

---

## Tech Stack

**FastAPI** · **Uvicorn** · **Pydantic v2** · **pydantic-settings** · **Google GenAI SDK** · **pytest** · **httpx**
