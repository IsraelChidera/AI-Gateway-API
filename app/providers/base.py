from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ProviderReply:
    text: str
    model: str
    input_tokens: int
    output_tokens: int


class AIProvider(ABC):
    @abstractmethod
    async def chat(self, message: str) -> ProviderReply:
        pass
