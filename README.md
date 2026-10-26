# FastAPI AI Chat Service

An async **FastAPI** backend that wraps Google **Gemini** behind a clean, provider-agnostic API, with a growing **retrieval (RAG)** toolkit for chunking, embedding and semantic search.

It is built to be production-minded from the start: typed request/response models, retries with exponential backoff, timeouts, upstream errors mapped to proper HTTP status codes, and a mock provider so you can develop and test without spending API quota.

---

## Features

- **`POST /chat`**: send a message, get back the model's answer plus latency and token usage.
- **Pluggable AI providers**: a single `AIProvider` interface with two implementations:
  - `GeminiProvider`: real calls through the `google-genai` SDK
  - `MockProvider`: deterministic canned replies from JSON, so it's free, offline and repeatable
- **Resilience built in**:
  - Configurable request timeout
  - Automatic retries on `429` / `500` / `503` with exponential backoff and jitter
  - Global exception handler that turns provider failures into meaningful HTTP responses
- **Retrieval toolkit (in progress)**: text chunking with overlap, Gemini embeddings (`gemini-embedding-001`) and cosine-similarity search
- **Typed configuration** through `pydantic-settings` and a `.env` file
- **Async test suite** with `pytest`, `pytest-asyncio` and `httpx`

---

## Architecture

```
          ┌──────────────┐
 HTTP ──▶ │  API routes  │  app/api/routes/       (chat, health)
          └──────┬───────┘
                 ▼
          ┌──────────────┐
          │  AIService   │  app/services/         (timing, response shaping)
          └──────┬───────┘
                 ▼
          ┌──────────────┐
          │  AIProvider  │  app/providers/base.py (interface + error types)
          └──┬────────┬──┘
             ▼        ▼
     GeminiProvider  MockProvider
```

Routes depend on the `AIService`, and the service depends only on the abstract `AIProvider`. To swap Gemini for another model (or the mock), you change a single dependency function in `app/api/routes/chat.py`.

---

## Project Structure

```
.
├── app/
│   ├── main.py                  # FastAPI app, routers, global error handler
│   ├── config.py                # Settings loaded from environment / .env
│   ├── api/routes/
│   │   ├── chat.py              # POST /chat
│   │   └── health.py            # GET /health
│   ├── models/
│   │   ├── chat/                # ChatRequest / ChatResponse schemas
│   │   └── mock-model.json      # Canned replies for MockProvider
│   ├── providers/
│   │   ├── base.py              # AIProvider interface, ProviderReply, error classes
│   │   ├── gemini_provider.py   # Gemini implementation with retries + timeout
│   │   └── mock_provider.py     # Deterministic offline provider
│   ├── services/
│   │   └── ai_service.py        # Orchestrates provider calls, measures latency
│   └── retrievals/
│       ├── chunking.py          # Overlapping text chunker
│       ├── embeddings.py        # Document / query embeddings via Gemini
│       └── search.py            # Cosine similarity + top-k search
├── tests/                       # pytest suite
├── .env.example
├── pyproject.toml               # pytest config (asyncio_mode = auto)
└── requirements.txt
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- A [Google Gemini API key](https://aistudio.google.com/app/apikey)

### 1. Clone and create a virtual environment

```bash
git clone <your-repo-url>
cd py-fast-api-day-3

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

Copy the example file and add your key:

```bash
cp .env.example .env
```

| Variable         | Description                                 | Default            |
| ---------------- | ------------------------------------------- | ------------------ |
| `GEMINI_API_KEY` | Your Google Gemini API key (**required**)   | —                  |
| `GEMINI_MODEL`   | Gemini model used for chat                  | `gemini-3.8-flash` |
| `AI_TIMEOUT`     | Seconds to wait for the provider            | `60`               |
| `MAX_RETRIES`    | Retry attempts for transient provider errors | `3`               |

### 4. Run the server

```bash
uvicorn app.main:app --reload
```

The API is now available at `http://127.0.0.1:8000`.
Interactive docs: **http://127.0.0.1:8000/docs** (Swagger UI) or **/redoc**.

---

## API Reference

### `GET /health`

Liveness check.

```json
{ "status": "ok" }
```

### `POST /chat`

**Request**

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Explain RAG in one sentence."}'
```

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

`latency` is in milliseconds.

### Error responses

Provider failures are caught globally and returned as `{"detail": "<message>"}` with an appropriate status:

| Situation                                  | Status                    |
| ------------------------------------------ | ------------------------- |
| Provider timed out                         | `504 Gateway Timeout`     |
| Provider unavailable after retries         | `503 Service Unavailable` |
| Rate limited after retries                 | `429 Too Many Requests` (includes `Retry-After: 30`) |
| Any other provider error                   | `502 Bad Gateway`         |
| Invalid request body                       | `422 Unprocessable Entity` |

---

## Using the Mock Provider

To develop without calling Gemini, switch the dependency in `app/api/routes/chat.py`:

```python
def get_ai_service() -> AIService:
    return AIService(MockProvider())
```

The mock hashes the incoming message to pick a reply from `app/models/mock-model.json`, so the same input always returns the same output. That makes it a good fit for demos and tests.

---

## Retrieval / RAG Toolkit

The `app/retrievals` package holds the building blocks for retrieval-augmented generation:

1. **Chunking**: `chunk_text(text, chunk_size=500, overlap=50)` splits text into overlapping windows so context isn't lost at boundaries.
2. **Embeddings**: `embed_documents()` and `embed_query()` call `gemini-embedding-001` with the correct `RETRIEVAL_DOCUMENT` / `RETRIEVAL_QUERY` task types.
3. **Search**: `search(query, documents, k)` embeds both sides, scores them with cosine similarity and returns the top-k matches.

Run these modules **from the project root with `-m`** so the `app` package resolves:

```bash
python -m app.retrievals.chunking
python -m app.retrievals.search
```

> Running a file directly (`python app/retrievals/search.py`) fails with `ModuleNotFoundError: No module named 'app'`.

---

## Running Tests

```bash
pytest
```

The tests set a dummy `GEMINI_API_KEY` (see `tests/conftest.py`), so no real key or network access is required. Async tests run automatically thanks to `asyncio_mode = "auto"` in `pyproject.toml`.

---

## Roadmap

- [ ] Wire retrieval into `/chat` for grounded answers
- [ ] Persist embeddings in a vector store
- [ ] Select provider through configuration instead of code
- [ ] Streaming responses
- [ ] Docker setup

---

## Tech Stack

**FastAPI** · **Uvicorn** · **Pydantic v2** · **pydantic-settings** · **Google GenAI SDK** · **pytest**
