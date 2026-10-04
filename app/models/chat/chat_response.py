from pydantic import BaseModel

class Usage(BaseModel):
    input_tokens: int
    output_tokens: int

class ChatResponse(BaseModel):
    latency: float
    answer: str
    model: str
    usage: Usage
