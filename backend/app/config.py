"""Configuration management for Web Intelligence Platform"""
import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    """Application settings from environment"""
    
    # App
    APP_NAME: str = "Web Intelligence Platform"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://wip:password@localhost:5432/web_intelligence"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # RabbitMQ
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"
    
    # LLM
    LLM_PROVIDER: str = "anthropic"
    LLM_MODEL: str = "claude-3-opus-20240229"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 4096
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Server
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    RELOAD: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
