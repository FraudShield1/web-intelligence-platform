"""Configuration management for Web Intelligence Platform"""
import os
import json
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    """Application settings from environment"""
    
    # App
    APP_NAME: str = "Web Intelligence Platform"
    DEBUG: bool = False
    RELOAD: bool = False
    ENABLE_DOCS: bool = True  # Enable for Railway deployment
    
    # Server
    API_HOST: str = "0.0.0.0"
    API_PORT: int = int(os.getenv("PORT", "8000"))
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://wip:password@localhost:5432/web_intelligence"
    )
    
    # Redis (for caching/rate limiting/Celery)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    UPSTASH_REDIS_REST_URL: str = os.getenv("UPSTASH_REDIS_REST_URL", "")
    UPSTASH_REDIS_REST_TOKEN: str = os.getenv("UPSTASH_REDIS_REST_TOKEN", "")
    
    # Celery
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", os.getenv("REDIS_URL", "redis://localhost:6379/0"))
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", os.getenv("REDIS_URL", "redis://localhost:6379/0"))
    
    # LLM
    LLM_PROVIDER: str = "openrouter"
    LLM_MODEL: str = "anthropic/claude-3-sonnet-20240229"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 4096
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "your-jwt-secret-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REQUIRE_AUTH: bool = os.getenv("REQUIRE_AUTH", "false").lower() == "true"  # Default to no auth for testing
    
    # CORS
    CORS_ORIGINS: List[str] = []
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Parse CORS_ORIGINS from JSON string if provided
        cors_str = os.getenv("CORS_ORIGINS", '["http://localhost:3000","http://localhost:8000"]')
        try:
            self.CORS_ORIGINS = json.loads(cors_str) if isinstance(cors_str, str) else cors_str
        except:
            self.CORS_ORIGINS = ["http://localhost:3000", "http://localhost:8000"]
    
    # Rate limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    RATE_LIMIT_MAX_REQUESTS: int = 300
    
    # Metrics/Observability
    PROMETHEUS_ENABLED: bool = True
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Email (optional)
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    FROM_EMAIL: str = os.getenv("FROM_EMAIL", "noreply@webintel.com")
    
    # Features
    ENABLE_WORKERS: bool = True
    ENABLE_NOTIFICATIONS: bool = bool(os.getenv("SMTP_USER"))
    
    # Sentry (optional)
    SENTRY_DSN: str = os.getenv("SENTRY_DSN", "")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
