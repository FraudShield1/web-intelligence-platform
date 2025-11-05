"""Main FastAPI application"""
import logging
import time
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db, close_db
from app.routes_sites import router as sites_router
from app.routes_jobs import router as jobs_router
from app.routes_blueprints import router as blueprints_router
from app.routes_analytics import router as analytics_router
from app.routes_auth import router as auth_router
from app.routes_public import router as public_router
from app.middleware_rate_limit import RateLimiter

# Prometheus
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "path", "status"]
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds", "Request latency", ["method", "path"]
)

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
logger = logging.getLogger(__name__)

rate_limiter = RateLimiter()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown"""
    # Startup
    logger.info("Initializing application")
    try:
        await rate_limiter.init()
    except Exception as e:
        logger.warning(f"Rate limiter init failed (OK for serverless): {e}")
    yield
    # Shutdown
    logger.info("Application shutdown")
    try:
        await close_db()
    except Exception as e:
        logger.warning(f"DB close failed (OK for serverless): {e}")

# Conditionally hide docs in production
_docs_url = "/docs" if (settings.DEBUG or settings.ENABLE_DOCS) else None
_redoc_url = "/redoc" if (settings.DEBUG or settings.ENABLE_DOCS) else None
_openapi_url = "/openapi.json" if (settings.DEBUG or settings.ENABLE_DOCS) else None

app = FastAPI(
    title="Web Intelligence Platform API",
    description="Automated discovery and scoring of website extraction surfaces",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=_docs_url,
    redoc_url=_redoc_url,
    openapi_url=_openapi_url,
)

# CORS middleware (hardened)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)

@app.middleware("http")
async def apply_rate_limit(request: Request, call_next):
    return await rate_limiter(request, call_next)

@app.middleware("http")
async def add_request_id_and_metrics(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    start = time.perf_counter()
    try:
        response: Response = await call_next(request)
        status_code = response.status_code
    except Exception as e:
        status_code = 500
        raise
    finally:
        path = request.url.path
        method = request.method
        REQUEST_COUNT.labels(method=method, path=path, status=str(status_code)).inc()
        REQUEST_LATENCY.labels(method=method, path=path).observe(time.perf_counter() - start)
    response.headers["X-Request-ID"] = request_id
    return response

# Health check endpoint
@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "web-intelligence-platform"
    }

# Prometheus metrics
@app.get("/metrics")
async def metrics():
    if not settings.PROMETHEUS_ENABLED:
        return Response(status_code=404)
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Root endpoint
@app.get("/")
async def root():
    """API root"""
    return {
        "name": "Web Intelligence Platform API",
        "version": "1.0.0",
        "docs": "/docs" if _docs_url else None,
        "openapi": "/openapi.json" if _openapi_url else None
    }

# Include routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(sites_router, prefix="/api/v1")
app.include_router(jobs_router, prefix="/api/v1")
app.include_router(blueprints_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")
app.include_router(public_router, prefix="/api/v1")  # Public endpoints - no auth required

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.RELOAD
    )

# Vercel serverless - export app directly
# Vercel's Python runtime will automatically detect and use the 'app' variable
