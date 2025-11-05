"""API v1 routes"""

from fastapi import APIRouter

from app.api.v1 import sites, jobs

router = APIRouter()

# Include route modules
router.include_router(sites.router, tags=["Sites"])
router.include_router(jobs.router, tags=["Jobs"])

__all__ = ["router"]

