"""
Yatra AI - Core Configuration
Loads all settings from environment variables.
"""
import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # === App Settings ===
    APP_NAME: str = "Yatra AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:5500", "http://localhost:5500"]

    # === Gemma 4 / Gemini API ===
    GEMMA_API_KEY: str = ""
    # Primary model: Gemma 4 Dense (31B). Fallback to MoE variant.
    GEMMA_MODEL: str = "gemma-4-31b-it"
    GEMMA_MODEL_FALLBACK: str = "gemma-4-26b-a4b-it"
    GEMMA_MAX_TOKENS: int = 8192
    GEMMA_TEMPERATURE: float = 0.7

    # === Database (optional - SQLite by default for easy setup) ===
    DATABASE_URL: str = "sqlite:///./yatra_ai.db"

    # === Rate limiting ===
    MAX_TRIPS_PER_DAY: int = 20

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
