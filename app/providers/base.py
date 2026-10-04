from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ProviderReply:
    text: str
    model: str
    input_tokens: int
    output_tokens: int

class ProviderError(Exception):
    """Base for all AI provider failures."""

class ProviderRateLimitError(ProviderError):
    pass

class ProviderUnavailableError(ProviderError):
    pass

class ProviderTimeoutError(ProviderError):
    pass

class AIProvider(ABC):
    @abstractmethod
    async def chat(self, message: str) -> ProviderReply:
        pass
