from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.api.routes import chat, health
from app.providers.base import (
    ProviderError,
    ProviderTimeoutError,
    ProviderUnavailableError,
    ProviderRateLimitError,
)

app = FastAPI()

ERROR_STATUS_MAPPING = {
    ProviderTimeoutError: status.HTTP_504_GATEWAY_TIMEOUT,
    ProviderUnavailableError: status.HTTP_503_SERVICE_UNAVAILABLE,
    ProviderRateLimitError: status.HTTP_429_TOO_MANY_REQUESTS,
}

@app.exception_handler(ProviderError)
async def provider_error_handler(request: Request, exc: ProviderError):
    code = ERROR_STATUS_MAPPING.get(type(exc), status.HTTP_502_BAD_GATEWAY)
    headers = {"Retry-After": "30"} if code == 429 else None
    return JSONResponse(status_code=code, content={"detail": str(exc)}, headers=headers)


app.include_router(health.router)
app.include_router(chat.router)
