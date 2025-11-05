"""Main FastAPI application"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db, close_db
from app.routes_sites import router as sites_router
from app.routes_jobs import router as jobs_router
from app.routes_blueprints import router as blueprints_router
from app.routes_analytics import router as analytics_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown"""
    # Startup
    logger.info("Initializing database...")
    await init_db()
    logger.info("Application startup complete")
    yield
    # Shutdown
    logger.info("Application shutdown")
    await close_db()

app = FastAPI(
    title="Web Intelligence Platform API",
    description="Automated discovery and scoring of website extraction surfaces",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "web-intelligence-platform"
    }

# Root endpoint
@app.get("/")
async def root():
    """API root"""
    return {
        "name": "Web Intelligence Platform API",
        "version": "1.0.0",
        "docs": "/docs",
        "openapi": "/openapi.json"
    }

# Include routers
app.include_router(sites_router, prefix="/api/v1")
app.include_router(jobs_router, prefix="/api/v1")
app.include_router(blueprints_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.RELOAD
    )
