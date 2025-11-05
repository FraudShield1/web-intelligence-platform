#!/usr/bin/env python3
"""
Backend Starter Setup & Structure Guide
Web Intelligence Platform

This file demonstrates the complete structure and key modules.
Ready to be expanded into a full FastAPI application.
"""

# ============================================================================
# 1. PROJECT STRUCTURE
# ============================================================================

"""
web-intelligence-platform/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app entry point
│   │   ├── config.py               # Configuration management
│   │   ├── database.py             # Database connection & ORM setup
│   │   ├── dependencies.py         # Shared dependencies
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── sites.py        # Sites endpoints
│   │   │   │   ├── jobs.py         # Jobs endpoints
│   │   │   │   ├── blueprints.py   # Blueprint endpoints
│   │   │   │   ├── analytics.py    # Analytics endpoints
│   │   │   │   └── auth.py         # Auth endpoints
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── site.py             # Site ORM models
│   │   │   ├── job.py              # Job ORM models
│   │   │   ├── blueprint.py        # Blueprint ORM models
│   │   │   └── user.py             # User ORM models
│   │   │
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── site.py             # Pydantic schemas
│   │   │   ├── job.py
│   │   │   ├── blueprint.py
│   │   │   └── analytics.py
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── site_service.py     # Business logic
│   │   │   ├── job_service.py
│   │   │   ├── blueprint_service.py
│   │   │   ├── analytics_service.py
│   │   │   ├── llm_service.py      # LLM integration
│   │   │   └── discovery_service.py
│   │   │
│   │   ├── workers/
│   │   │   ├── __init__.py
│   │   │   ├── base_worker.py      # Base class
│   │   │   ├── fingerprinter.py    # Fingerprint worker
│   │   │   ├── browser_worker.py   # Browser worker
│   │   │   └── static_crawler.py   # Static crawler
│   │   │
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── logging.py
│   │   │   ├── retry.py
│   │   │   ├── cache.py
│   │   │   └── validators.py
│   │   │
│   │   └── middleware/
│   │       ├── __init__.py
│   │       ├── auth_middleware.py
│   │       ├── error_handler.py
│   │       └── logging_middleware.py
│   │
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── main.py  # Run as: uvicorn main:app --reload

├── workers/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── worker_main.py

├── docs/
│   └── (existing documentation)

└── frontend/
    └── (React dashboard)
"""

# ============================================================================
# 2. REQUIREMENTS.TXT
# ============================================================================

REQUIREMENTS = """
# Core
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0

# Database
sqlalchemy==2.0.23
alembic==1.13.0
psycopg2-binary==2.9.9
asyncpg==0.29.0

# Message Queue
pika==1.3.2
aio-pika==13.1.0

# LLM & External APIs
anthropic==0.7.1
openai==1.3.6

# Web Scraping
httpx==0.25.2
beautifulsoup4==4.12.2
lxml==4.9.3
selenium==4.15.2
playwright==1.40.0

# Browser Automation
playwright==1.40.0

# Async
asyncio==3.4.3
aioredis==2.0.1

# Monitoring & Logging
prometheus-client==0.19.0
python-json-logger==2.0.7

# Auth & Security
pyjwt==2.8.0
python-jose==3.3.0
passlib==1.7.4
bcrypt==4.1.0

# Utilities
python-dotenv==1.0.0
pyyaml==6.0.1
requests==2.31.0
click==8.1.7

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
httpx-mock==0.24.1

# Development
black==23.12.0
flake8==6.1.0
mypy==1.7.1
isort==5.13.2
"""

# ============================================================================
# 3. CORE APPLICATION SETUP (main.py)
# ============================================================================

MAIN_PY = """
# backend/app/main.py
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_db
from app.api.v1 import sites, jobs, blueprints, analytics, auth
from app.middleware.error_handler import error_handling_middleware

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing database...")
    await init_db()
    logger.info("Application startup complete")
    yield
    # Shutdown
    logger.info("Application shutdown")

app = FastAPI(
    title="Web Intelligence Platform",
    description="Automated discovery & scoring of website extraction surfaces",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Error handling middleware
app.add_middleware(error_handling_middleware)

# Health check
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "version": "1.0.0"
    }

# Routes
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(sites.router, prefix="/api/v1", tags=["sites"])
app.include_router(jobs.router, prefix="/api/v1", tags=["jobs"])
app.include_router(blueprints.router, prefix="/api/v1", tags=["blueprints"])
app.include_router(analytics.router, prefix="/api/v1", tags=["analytics"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""

# ============================================================================
# 4. CONFIGURATION MODULE
# ============================================================================

CONFIG_PY = """
# backend/app/config.py
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Web Intelligence Platform"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "postgresql://user:pass@localhost:5432/web_intelligence"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # RabbitMQ
    RABBITMQ_URL: str = "amqp://user:pass@localhost:5672/"
    
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
    
    # Worker
    WORKER_TYPE: str = "api"  # api, fingerprinter, browser, static_crawler
    MAX_WORKERS: int = 4
    
    # Monitoring
    PROMETHEUS_ENABLED: bool = True
    PROMETHEUS_PORT: int = 9090
    
    class Config:
        env_file = ".env"

settings = Settings()
"""

# ============================================================================
# 5. DATABASE SETUP
# ============================================================================

DATABASE_PY = """
# backend/app/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

from app.config import settings

# Use asyncpg driver for PostgreSQL
engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.DEBUG,
    poolclass=NullPool,
    future=True
)

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

async def init_db():
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with async_session() as session:
        yield session
"""

# ============================================================================
# 6. MODELS EXAMPLE
# ============================================================================

MODELS_SITE_PY = """
# backend/app/models/site.py
from sqlalchemy import Column, String, Float, DateTime, JSON, UUID, Enum
from sqlalchemy.ext.declarative import declarative_base
import uuid
from datetime import datetime
import enum

Base = declarative_base()

class SiteStatus(str, enum.Enum):
    PENDING = "pending"
    READY = "ready"
    REVIEW = "review"
    FAILED = "failed"

class Site(Base):
    __tablename__ = "sites"
    
    site_id = Column(UUID, primary_key=True, default=uuid.uuid4)
    domain = Column(String(255), unique=True, nullable=False)
    platform = Column(String(100))
    status = Column(String(50), default=SiteStatus.PENDING)
    fingerprint_data = Column(JSON)
    complexity_score = Column(Float)
    business_value_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_discovered_at = Column(DateTime)
    blueprint_version = Column(Integer, default=0)
    notes = Column(String)
"""

# ============================================================================
# 7. SCHEMAS EXAMPLE
# ============================================================================

SCHEMAS_SITE_PY = """
# backend/app/schemas/site.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class SiteCreate(BaseModel):
    domain: str = Field(..., example="example.com")
    business_value_score: Optional[float] = Field(None, ge=0, le=1)
    priority: Optional[str] = None
    notes: Optional[str] = None

class SiteUpdate(BaseModel):
    business_value_score: Optional[float] = None
    priority: Optional[str] = None
    notes: Optional[str] = None

class SiteResponse(BaseModel):
    site_id: UUID
    domain: str
    platform: Optional[str]
    status: str
    complexity_score: Optional[float]
    business_value_score: Optional[float]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class SiteListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    sites: List[SiteResponse]
"""

# ============================================================================
# 8. SERVICE LAYER EXAMPLE
# ============================================================================

SERVICE_SITE_PY = """
# backend/app/services/site_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from typing import Optional, List

from app.models.site import Site
from app.schemas.site import SiteCreate, SiteUpdate, SiteResponse

class SiteService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_site(self, site_data: SiteCreate) -> SiteResponse:
        db_site = Site(**site_data.dict())
        self.db.add(db_site)
        await self.db.commit()
        await self.db.refresh(db_site)
        return SiteResponse.from_orm(db_site)
    
    async def get_site(self, site_id: UUID) -> Optional[SiteResponse]:
        result = await self.db.execute(
            select(Site).where(Site.site_id == site_id)
        )
        site = result.scalar_one_or_none()
        if site:
            return SiteResponse.from_orm(site)
        return None
    
    async def list_sites(
        self,
        status: Optional[str] = None,
        platform: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> dict:
        query = select(Site)
        
        if status:
            query = query.where(Site.status == status)
        if platform:
            query = query.where(Site.platform == platform)
        
        # Get total count
        result = await self.db.execute(select(Site))
        total = len(result.all())
        
        # Get paginated results
        query = query.limit(limit).offset(offset)
        result = await self.db.execute(query)
        sites = result.scalars().all()
        
        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "sites": [SiteResponse.from_orm(site) for site in sites]
        }
    
    async def update_site(self, site_id: UUID, site_data: SiteUpdate) -> Optional[SiteResponse]:
        result = await self.db.execute(
            select(Site).where(Site.site_id == site_id)
        )
        db_site = result.scalar_one_or_none()
        if not db_site:
            return None
        
        for key, value in site_data.dict(exclude_unset=True).items():
            setattr(db_site, key, value)
        
        await self.db.commit()
        await self.db.refresh(db_site)
        return SiteResponse.from_orm(db_site)
    
    async def delete_site(self, site_id: UUID) -> bool:
        result = await self.db.execute(
            select(Site).where(Site.site_id == site_id)
        )
        db_site = result.scalar_one_or_none()
        if not db_site:
            return False
        
        await self.db.delete(db_site)
        await self.db.commit()
        return True
"""

# ============================================================================
# 9. API ENDPOINTS EXAMPLE
# ============================================================================

API_SITES_PY = """
# backend/app/api/v1/sites.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.database import get_db
from app.schemas.site import SiteCreate, SiteUpdate, SiteResponse, SiteListResponse
from app.services.site_service import SiteService

router = APIRouter(prefix="/sites", tags=["sites"])

@router.post("", response_model=SiteResponse, status_code=201)
async def create_site(
    site_data: SiteCreate,
    db: AsyncSession = Depends(get_db)
):
    service = SiteService(db)
    return await service.create_site(site_data)

@router.get("", response_model=SiteListResponse)
async def list_sites(
    status: str = Query(None),
    platform: str = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    service = SiteService(db)
    return await service.list_sites(status, platform, limit, offset)

@router.get("/{site_id}", response_model=SiteResponse)
async def get_site(
    site_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    service = SiteService(db)
    site = await service.get_site(site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    return site

@router.put("/{site_id}", response_model=SiteResponse)
async def update_site(
    site_id: UUID,
    site_data: SiteUpdate,
    db: AsyncSession = Depends(get_db)
):
    service = SiteService(db)
    site = await service.update_site(site_id, site_data)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    return site

@router.delete("/{site_id}", status_code=204)
async def delete_site(
    site_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    service = SiteService(db)
    deleted = await service.delete_site(site_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Site not found")
    return None
"""

# ============================================================================
# 10. DOCKERFILE
# ============================================================================

DOCKERFILE = """
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    postgresql-client \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Run app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
"""

# ============================================================================
# 11. DOCKER COMPOSE
# ============================================================================

DOCKER_COMPOSE_YML = """
version: '3.8'

services:
  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://wip:password@postgres:5432/web_intelligence
      - REDIS_URL=redis://redis:6379/0
      - RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
      - LLM_PROVIDER=anthropic
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    depends_on:
      - postgres
      - redis
      - rabbitmq
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --reload

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=wip
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=web_intelligence
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  rabbitmq:
    image: rabbitmq:3-management
    environment:
      - RABBITMQ_DEFAULT_USER=guest
      - RABBITMQ_DEFAULT_PASS=guest
    ports:
      - "5672:5672"
      - "15672:15672"

volumes:
  postgres_data:
"""

# ============================================================================
# 12. ENVIRONMENT TEMPLATE
# ============================================================================

ENV_TEMPLATE = """
# .env
DEBUG=False
DATABASE_URL=postgresql://wip:password@localhost:5432/web_intelligence
REDIS_URL=redis://localhost:6379/0
RABBITMQ_URL=amqp://guest:guest@localhost:5672/

# LLM
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your-key-here
OPENAI_API_KEY=your-key-here

# Auth
SECRET_KEY=your-secret-key-change-this
JWT_ALGORITHM=HS256

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]

# Worker
WORKER_TYPE=api
MAX_WORKERS=4
"""

if __name__ == "__main__":
    print("Backend Setup Guide")
    print("=" * 80)
    print("\\n1. Create project structure:")
    print("   mkdir -p backend/app/{api/v1,models,schemas,services,workers,utils,middleware}")
    print("\\n2. Create requirements.txt with content above")
    print("\\n3. Create main.py, config.py, database.py files")
    print("\\n4. Set up database:")
    print("   docker-compose up -d postgres redis rabbitmq")
    print("   psql -U wip -d web_intelligence < DATABASE.sql")
    print("\\n5. Run application:")
    print("   pip install -r requirements.txt")
    print("   uvicorn app.main:app --reload")
    print("\\nAPI available at: http://localhost:8000")
    print("Docs at: http://localhost:8000/docs")

