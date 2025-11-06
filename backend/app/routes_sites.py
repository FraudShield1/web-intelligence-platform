"""Sites API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import uuid as uuid_lib

from app.database import get_db
from app.models import Site, Job
from app.schemas import SiteCreate, SiteUpdate, SiteResponse, SiteDetailResponse, SiteListResponse
# Temporarily disabled for easier testing
# from app.security import get_current_user, require_roles
from app.workers.fingerprinter import fingerprint_site
# Lazy import to avoid startup failures
try:
    from app.workers.discoverer import discover_site
    DISCOVERER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Discovery worker not available: {e}")
    discover_site = None
    DISCOVERER_AVAILABLE = False

router = APIRouter(prefix="/sites", tags=["sites"])

@router.post("", response_model=SiteResponse, status_code=201)
async def create_site(
    site_data: SiteCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new site and initiate fingerprinting"""
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
    except Exception as e:
        # If Celery not available, job stays queued
        pass
    
    return db_site

@router.get("", response_model=SiteListResponse)
async def list_sites(
    status: str = Query(None),
    platform: str = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """List sites with filtering and pagination"""
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

@router.get("/{site_id}", response_model=SiteDetailResponse)
async def get_site(
    site_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get site details with fingerprint data"""
    stmt = select(Site).where(Site.site_id == site_id)
    result = await db.execute(stmt)
    site = result.scalar_one_or_none()
    
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    
    return site

@router.put("/{site_id}", response_model=SiteResponse)
async def update_site(
    site_id: UUID,
    site_data: SiteUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update site metadata"""
    stmt = select(Site).where(Site.site_id == site_id)
    result = await db.execute(stmt)
    db_site = result.scalar_one_or_none()
    
    if not db_site:
        raise HTTPException(status_code=404, detail="Site not found")
    
    for key, value in site_data.dict(exclude_unset=True).items():
        setattr(db_site, key, value)
    
    await db.commit()
    await db.refresh(db_site)
    return db_site

@router.delete("/{site_id}", status_code=204)
async def delete_site(
    site_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete a site"""
    stmt = select(Site).where(Site.site_id == site_id)
    result = await db.execute(stmt)
    db_site = result.scalar_one_or_none()
    
    if not db_site:
        raise HTTPException(status_code=404, detail="Site not found")
    
    await db.delete(db_site)
    await db.commit()

