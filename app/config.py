from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = "gemini-3.8-flash"
    ai_timeout: int = 60
    max_retries: int = 3


@lru_cache
def get_settings() -> Settings:
    return Settings()
