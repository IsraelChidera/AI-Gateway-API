from fastapi import FastAPI

from app.models.chat_request import ChatRequest

app = FastAPI() 

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/chat")
async def chat(chat_request: ChatRequest):
    return {"message": chat_request.message}
