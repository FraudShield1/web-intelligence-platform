"""Public API endpoints (no auth required)"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import uuid as uuid_lib

from app.database import get_db
from app.models import Site, Job, Blueprint
from app.schemas import (
    SiteCreate, SiteResponse, SiteListResponse,
    JobResponse, JobListResponse,
    BlueprintResponse, BlueprintListResponse,
    DashboardMetricsResponse
)
from app.workers.fingerprinter import fingerprint_site

router = APIRouter(prefix="/public", tags=["public"])

# ============================================================================
# SITES
# ============================================================================

@router.post("/sites", response_model=SiteResponse, status_code=201)
async def create_site_public(
    site_data: SiteCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new site (public endpoint)"""
    # Check if domain already exists
    stmt = select(Site).where(Site.domain == site_data.domain)
    existing = await db.execute(stmt)
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Site already exists")
    
    site_uuid = uuid_lib.uuid4()
    db_site = Site(
        site_id=site_uuid,
        domain=site_data.domain,
        status="pending",
        business_value_score=site_data.business_value_score or 0.5,
        notes=site_data.notes
    )
    db.add(db_site)
    await db.commit()
    await db.refresh(db_site)
    
    # Create fingerprinting job
    fingerprint_job = Job(
        job_id=uuid_lib.uuid4(),
        site_id=site_uuid,
        job_type="fingerprint",
        method="auto",
        status="queued"
    )
    db.add(fingerprint_job)
    await db.commit()
    
    # Trigger async fingerprinting worker
    try:
        fingerprint_site.delay(str(site_uuid), str(fingerprint_job.job_id))
    except Exception:
        pass
    
    return db_site

@router.get("/sites", response_model=SiteListResponse)
async def list_sites_public(
    status: str = Query(None),
    platform: str = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """List sites (public endpoint)"""
    query = select(Site)
    
    if status:
        query = query.where(Site.status == status)
    if platform:
        query = query.where(Site.platform == platform)
    
    # Get total count
    count_query = select(func.count()).select_from(Site)
    if status:
        count_query = count_query.where(Site.status == status)
    if platform:
        count_query = count_query.where(Site.platform == platform)
    
    result = await db.execute(count_query)
    total = result.scalar() or 0
    
    # Get paginated results
    query = query.order_by(Site.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    sites = result.scalars().all()
    
    return SiteListResponse(
        total=total,
        limit=limit,
        offset=offset,
        sites=sites
    )

@router.get("/sites/{site_id}", response_model=SiteResponse)
async def get_site_public(
    site_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get site details (public endpoint)"""
    stmt = select(Site).where(Site.site_id == site_id)
    result = await db.execute(stmt)
    site = result.scalar_one_or_none()
    
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    
    return site

# ============================================================================
# JOBS
# ============================================================================

@router.get("/jobs", response_model=JobListResponse)
async def list_jobs_public(
    status: str = Query(None),
    job_type: str = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """List jobs (public endpoint)"""
    query = select(Job)
    
    if status:
        query = query.where(Job.status == status)
    if job_type:
        query = query.where(Job.job_type == job_type)
    
    # Get total count
    count_query = select(func.count()).select_from(Job)
    if status:
        count_query = count_query.where(Job.status == status)
    if job_type:
        count_query = count_query.where(Job.job_type == job_type)
    
    result = await db.execute(count_query)
    total = result.scalar() or 0
    
    # Get paginated results
    query = query.order_by(Job.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    jobs = result.scalars().all()
    
    return JobListResponse(
        total=total,
        limit=limit,
        offset=offset,
        jobs=jobs
    )

@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job_public(
    job_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get job details (public endpoint)"""
    stmt = select(Job).where(Job.job_id == job_id)
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job

# ============================================================================
# BLUEPRINTS
# ============================================================================

@router.get("/blueprints", response_model=BlueprintListResponse)
async def list_blueprints_public(
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """List blueprints (public endpoint)"""
    count_query = select(func.count()).select_from(Blueprint)
    result = await db.execute(count_query)
    total = result.scalar() or 0
    
    query = select(Blueprint).order_by(Blueprint.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    blueprints = result.scalars().all()
    
    return BlueprintListResponse(
        total=total,
        limit=limit,
        offset=offset,
        blueprints=blueprints
    )

# ============================================================================
# ANALYTICS
# ============================================================================

@router.get("/analytics/dashboard", response_model=DashboardMetricsResponse)
async def dashboard_metrics_public(db: AsyncSession = Depends(get_db)):
    """Get dashboard metrics (public endpoint)"""
    # Total sites
    total_sites_query = select(func.count()).select_from(Site)
    result = await db.execute(total_sites_query)
    total_sites = result.scalar() or 0
    
    # Total jobs
    total_jobs_query = select(func.count()).select_from(Job)
    result = await db.execute(total_jobs_query)
    total_jobs = result.scalar() or 0
    
    # Completed jobs
    completed_jobs_query = select(func.count()).select_from(Job).where(Job.status == "completed")
    result = await db.execute(completed_jobs_query)
    completed_jobs = result.scalar() or 0
    
    # Success rate
    success_rate = (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0
    
    return DashboardMetricsResponse(
        total_sites=total_sites,
        total_jobs=total_jobs,
        completed_jobs=completed_jobs,
        failed_jobs=0,  # Simplified
        success_rate=success_rate,
        avg_completion_time=0,  # Simplified
        total_cost=0  # Simplified
    )

