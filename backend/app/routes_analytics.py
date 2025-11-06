"""Analytics API endpoints"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import datetime, timedelta

from app.database import get_db
from app.models import Site, Job, AnalyticsMetric
from app.schemas import DashboardMetricsResponse, SiteMetricsResponse, MethodPerformanceResponse

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/dashboard", response_model=DashboardMetricsResponse)
async def get_dashboard_metrics(
    date_range: str = Query("7d"),
    db: AsyncSession = Depends(get_db)
):
    """Get high-level dashboard metrics"""
    # Parse date range
    if date_range == "7d":
        days = 7
    elif date_range == "30d":
        days = 30
    elif date_range == "1d":
        days = 1
    else:
        days = 7
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get site counts
    sites_stmt = select(Site)
    result = await db.execute(sites_stmt)
    all_sites = result.scalars().all()
    total_sites = len(all_sites)
    
    new_sites = len([s for s in all_sites if s.created_at > start_date])
    ready_sites = len([s for s in all_sites if s.status == "ready"])
    review_sites = len([s for s in all_sites if s.status == "review"])
    failed_sites = len([s for s in all_sites if s.status == "failed"])
    
    # Get job stats
    jobs_stmt = select(Job).where(Job.created_at > start_date)
    result = await db.execute(jobs_stmt)
    jobs = result.scalars().all()
    
    successful_jobs = len([j for j in jobs if j.status == "success"])
    total_jobs = len(jobs)
    success_rate = successful_jobs / total_jobs if total_jobs > 0 else 0
    
    # Calculate average duration safely
    avg_duration = 0
    if successful_jobs > 0:
        durations = []
        for j in jobs:
            if j.status == "success" and j.started_at and j.completed_at:
                duration = (j.completed_at - j.started_at).total_seconds()
                durations.append(duration)
        if durations:
            avg_duration = sum(durations) / len(durations)
    
    # Count active jobs (running status)
    active_jobs = len([j for j in jobs if j.status in ["running", "queued"]])
    
    # Count total blueprints (sites with blueprints)
    total_blueprints = len([s for s in all_sites if s.blueprint_version and s.blueprint_version > 0])
    
    return DashboardMetricsResponse(
        total_sites=total_sites,
        active_jobs=active_jobs,
        total_blueprints=total_blueprints,
        avg_discovery_time=avg_duration if avg_duration > 0 else None,
        success_rate=success_rate if total_jobs > 0 else None
    )

@router.get("/sites/{site_id}/metrics", response_model=SiteMetricsResponse)
async def get_site_metrics(
    site_id: UUID,
    start_date: str = Query(None),
    end_date: str = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get metrics for specific site"""
    # Get site
    site_stmt = select(Site).where(Site.site_id == site_id)
    result = await db.execute(site_stmt)
    site = result.scalar_one_or_none()
    
    if not site:
        return {"error": "Site not found"}
    
    # Get metrics
    metrics_stmt = select(AnalyticsMetric).where(
        AnalyticsMetric.site_id == site_id
    ).order_by(AnalyticsMetric.date.desc()).limit(30)
    
    result = await db.execute(metrics_stmt)
    metrics = result.scalars().all()
    
    # Get jobs for this site
    jobs_stmt = select(Job).where(Job.site_id == site_id)
    result = await db.execute(jobs_stmt)
    jobs = result.scalars().all()
    
    successful = len([j for j in jobs if j.status == "success"])
    total = len(jobs)
    
    # Calculate average time safely
    avg_time = 0
    if successful > 0:
        durations = []
        for j in jobs:
            if j.status == "success" and j.started_at and j.completed_at:
                duration = (j.completed_at - j.started_at).total_seconds()
                durations.append(duration)
        if durations:
            avg_time = sum(durations) / len(durations)
    
    failed = len([j for j in jobs if j.status == "failed"])
    
    return SiteMetricsResponse(
        site_id=site_id,
        domain=site.domain,
        total_jobs=total,
        successful_jobs=successful,
        failed_jobs=failed,
        avg_discovery_time=avg_time if avg_time > 0 else None,
        total_categories=None,  # Could calculate from metrics if needed
        total_endpoints=None,   # Could calculate from metrics if needed
        last_run=site.last_discovered_at.isoformat() if site.last_discovered_at else None
    )

@router.get("/methods/performance")
async def get_method_performance(
    db: AsyncSession = Depends(get_db)
):
    """Compare discovery method effectiveness"""
    # Get all jobs
    jobs_stmt = select(Job)
    result = await db.execute(jobs_stmt)
    all_jobs = result.scalars().all()
    
    if not all_jobs:
        # Return empty result if no jobs
        return {
            "method": "none",
            "total_runs": 0,
            "success_rate": 0.0,
            "avg_discovery_time": 0.0,
            "avg_categories_found": 0.0,
            "avg_cost_usd": 0.0
        }
    
    # Use the first method found, or aggregate all methods
    # For now, let's aggregate all methods together
    successful = len([j for j in all_jobs if j.status == "success"])
    total = len(all_jobs)
    
    # Calculate average time safely
    avg_time = 0.0
    if successful > 0:
        durations = []
        for j in all_jobs:
            if j.status == "success" and j.started_at and j.completed_at:
                duration = (j.completed_at - j.started_at).total_seconds()
                durations.append(duration)
        if durations:
            avg_time = sum(durations) / len(durations)
    
    return MethodPerformanceResponse(
        method="all",
        total_runs=total,
        success_rate=round(successful / total if total > 0 else 0, 3),
        avg_discovery_time=round(avg_time, 1),
        avg_categories_found=0.0,  # Placeholder
        avg_cost_usd=0.25  # Placeholder
    )

