from google.genai import types
from google import genai

from app.config import get_settings

settings = get_settings()

client = genai.Client(api_key=settings.gemini_api_key)

demo_documents = [
    "You can reset your password from the account settings page.",
    "Two-factor authentication can be enabled from security settings.",
    "Invoices are available from the billing dashboard.",
    "You can update your company address from organization settings.",
    "Our API uses OAuth 2.0 for authentication.",
]

def embed_documents(docs: list[str]) -> list[list[float]]:
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=docs,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")
    )
    return [embedding.values for embedding in result.embeddings]

def embed_query(query: str) -> list[float]:
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=[query],
        config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY")
    )
    return result.embeddings[0].values