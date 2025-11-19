"""
Configuration management for WhatsApp Bot
"""
from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Twilio WhatsApp
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_WHATSAPP_NUMBER: str = "whatsapp:+14155238886"

    # LLM Configuration
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-3-sonnet-20240229"
    LLM_PROVIDER: Literal["openai", "anthropic"] = "openai"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    USE_REDIS: bool = False

    # Application Settings
    WEBHOOK_URL: str = ""
    MAX_CONVERSATION_HISTORY: int = 10
    MAX_TOKENS: int = 1000
    TEMPERATURE: float = 0.7

    # Knowledge Base
    KNOWLEDGE_BASE_PATH: str = "./knowledge_base"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
