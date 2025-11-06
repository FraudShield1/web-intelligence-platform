"""Discovery API endpoints - Feature G"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID, uuid4
from datetime import datetime

from app.database import get_db
from app.models import Site, Job
from app.schemas.job import JobResponse
from app.workers.discoverer import discover_site

router = APIRouter(prefix="/discovery", tags=["discovery"])


@router.post("/sites/{site_id}/discover", response_model=JobResponse)
async def trigger_discovery(
    site_id: UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger Feature G discovery for a site
    
    This will:
    - Run all 6 phases of discovery
    - Create a versioned blueprint
    - Update site status to 'discovered'
    """
    # Get site
    stmt = select(Site).where(Site.site_id == site_id)
    result = await db.execute(stmt)
    site = result.scalar_one_or_none()
    
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    
    # Check if already discovering
    active_job_stmt = select(Job).where(
        Job.site_id == site_id,
        Job.job_type == "discover",
        Job.status.in_(["queued", "running"])
    )
    result = await db.execute(active_job_stmt)
    active_job = result.scalar_one_or_none()
    
    if active_job:
        raise HTTPException(
            status_code=409,
            detail=f"Discovery already in progress (job {active_job.job_id})"
        )
    
    # Create discovery job
    job = Job(
        job_id=uuid4(),
        site_id=site_id,
        job_type="discover",
        method="manual",
        status="queued",
        created_at=datetime.utcnow()
    )
    
    db.add(job)
    await db.commit()
    await db.refresh(job)
    
    # Trigger discovery worker
    try:
        discover_site.delay(str(site_id), str(job.job_id))
    except Exception as e:
        # If Celery not available, mark job as failed
        job.status = "failed"
        job.error_message = f"Failed to queue job: {str(e)}"
        await db.commit()
    
    return job


@router.get("/sites/{site_id}/status")
async def get_discovery_status(
    site_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get current discovery status for a site"""
    # Get site
    stmt = select(Site).where(Site.site_id == site_id)
    result = await db.execute(stmt)
    site = result.scalar_one_or_none()
    
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    
    # Get latest discovery job
    job_stmt = select(Job).where(
        Job.site_id == site_id,
        Job.job_type == "discover"
    ).order_by(Job.created_at.desc()).limit(1)
    
    result = await db.execute(job_stmt)
    latest_job = result.scalar_one_or_none()
    
    return {
        "site_id": site_id,
        "site_status": site.status,
        "blueprint_version": site.blueprint_version,
        "last_discovered_at": site.last_discovered_at,
        "latest_job": {
            "job_id": latest_job.job_id,
            "status": latest_job.status,
            "started_at": latest_job.started_at,
            "completed_at": latest_job.completed_at,
            "result": latest_job.result
        } if latest_job else None
    }

