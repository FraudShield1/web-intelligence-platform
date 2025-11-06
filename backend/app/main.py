"""Main FastAPI application"""
import logging
import time
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db, close_db
# Lazy import all routers to avoid startup failures
try:
    from app.routes_sites import router as sites_router
    SITES_ROUTER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Sites router not available: {e}")
    sites_router = None
    SITES_ROUTER_AVAILABLE = False

try:
    from app.routes_jobs import router as jobs_router
    JOBS_ROUTER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Jobs router not available: {e}")
    jobs_router = None
    JOBS_ROUTER_AVAILABLE = False

try:
    from app.routes_blueprints import router as blueprints_router
    BLUEPRINTS_ROUTER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Blueprints router not available: {e}")
    blueprints_router = None
    BLUEPRINTS_ROUTER_AVAILABLE = False

try:
    from app.routes_analytics import router as analytics_router
    ANALYTICS_ROUTER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Analytics router not available: {e}")
    analytics_router = None
    ANALYTICS_ROUTER_AVAILABLE = False

try:
    from app.routes_auth import router as auth_router
    AUTH_ROUTER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Auth router not available: {e}")
    auth_router = None
    AUTH_ROUTER_AVAILABLE = False

try:
    from app.routes_public import router as public_router
    PUBLIC_ROUTER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Public router not available: {e}")
    public_router = None
    PUBLIC_ROUTER_AVAILABLE = False

try:
    from app.routes_discovery import router as discovery_router
    DISCOVERY_ROUTER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Discovery router not available: {e}")
    discovery_router = None
    DISCOVERY_ROUTER_AVAILABLE = False

try:
    from app.routes_templates import router as templates_router
    TEMPLATES_ROUTER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Templates router not available: {e}")
    templates_router = None
    TEMPLATES_ROUTER_AVAILABLE = False
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

# Debug endpoint to check database connection
@app.get("/debug/db")
async def debug_db():
    """Debug database connection"""
    try:
        from app.database import get_db
        async for db in get_db():
            # Try a simple query
            from sqlalchemy import text
            result = await db.execute(text("SELECT 1"))
            return {
                "status": "success",
                "message": "Database connection working",
                "test_query": "SELECT 1",
                "database_url_set": bool(settings.DATABASE_URL)
            }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "type": type(e).__name__,
            "database_url_set": bool(settings.DATABASE_URL)
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
app.include_router(discovery_router, prefix="/api/v1")  # Feature G discovery endpoints
app.include_router(templates_router, prefix="/api/v1")  # Feature F: Template library
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
