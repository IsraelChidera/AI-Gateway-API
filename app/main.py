from fastapi import FastAPI

from app.api.routes import chat, health

app = FastAPI()

app.include_router(health.router)
app.include_router(chat.router)
