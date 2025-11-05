"""Jobs API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import uuid as uuid_lib

from app.database import get_db
from app.models import Job, Site
from app.schemas import JobCreate, JobResponse, JobListResponse
# Temporarily disabled for easier testing
# from app.security import get_current_user, require_roles

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.post("", response_model=JobResponse, status_code=201)
async def create_job(
    job_data: JobCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new discovery job"""
    # Verify site exists
    site_stmt = select(Site).where(Site.site_id == job_data.site_id)
    result = await db.execute(site_stmt)
    site = result.scalar_one_or_none()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    
    # Check if job already running for this site
    running_stmt = select(Job).where(
        (Job.site_id == job_data.site_id) & 
        (Job.status == "running")
    )
    result = await db.execute(running_stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Job already running for this site")
    
    # Create job
    db_job = Job(
        job_id=uuid_lib.uuid4(),
        site_id=job_data.site_id,
        job_type=job_data.job_type,
        method=job_data.method or "auto",
        status="queued",
        priority=1 if job_data.priority == "high" else 0
    )
    db.add(db_job)
    await db.commit()
    await db.refresh(db_job)
    
    return db_job

@router.get("", response_model=JobListResponse)
async def list_jobs(
    site_id: UUID = Query(None),
    status: str = Query(None),
    job_type: str = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """List jobs with filtering"""
    query = select(Job)
    
    if site_id:
        query = query.where(Job.site_id == site_id)
    if status:
        query = query.where(Job.status == status)
    if job_type:
        query = query.where(Job.job_type == job_type)
    
    # Get total
    count_stmt = select(func.count()).select_from(Job)
    if site_id:
        count_stmt = count_stmt.where(Job.site_id == site_id)
    if status:
        count_stmt = count_stmt.where(Job.status == status)
    if job_type:
        count_stmt = count_stmt.where(Job.job_type == job_type)
    
    result = await db.execute(count_stmt)
    total = result.scalar() or 0
    
    # Get paginated
    query = query.order_by(Job.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    jobs = result.scalars().all()
    
    return JobListResponse(total=total, jobs=jobs)

@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get job status"""
    stmt = select(Job).where(Job.job_id == job_id)
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job

@router.post("/{job_id}/cancel", response_model=JobResponse)
async def cancel_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Cancel a job"""
    stmt = select(Job).where(Job.job_id == job_id)
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status in ["success", "failed"]:
        raise HTTPException(status_code=409, detail="Cannot cancel completed job")
    
    job.status = "cancelled"
    await db.commit()
    await db.refresh(job)
    
    return job

@router.post("/{job_id}/retry", response_model=JobResponse, status_code=201)
async def retry_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Retry a failed job"""
    stmt = select(Job).where(Job.job_id == job_id)
    result = await db.execute(stmt)
    old_job = result.scalar_one_or_none()
    
    if not old_job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if old_job.status != "failed":
        raise HTTPException(status_code=400, detail="Job not in failed state")
    
    if old_job.attempt_count >= old_job.max_retries:
        raise HTTPException(status_code=409, detail="Max retries exceeded")
    
    # Create new job
    new_job = Job(
        job_id=uuid_lib.uuid4(),
        site_id=old_job.site_id,
        job_type=old_job.job_type,
        method=old_job.method,
        status="queued",
        priority=old_job.priority + 1  # Increase priority for retry
    )
    db.add(new_job)
    await db.commit()
    await db.refresh(new_job)
    
    return new_job

