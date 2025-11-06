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
    
    # Get platform distribution
    platform_dist = {}
    for site in all_sites:
        platform = site.platform or "unknown"
        platform_dist[platform] = platform_dist.get(platform, 0) + 1
    
    return DashboardMetricsResponse(
        total_sites=total_sites,
        sites_new=new_sites,
        sites_ready=ready_sites,
        sites_in_review=review_sites,
        sites_failed=failed_sites,
        discovery_metrics={
            "total_discoveries": total_jobs,
            "successful_discoveries": successful_jobs,
            "success_rate": round(success_rate, 2),
            "avg_discovery_time_seconds": round(avg_duration, 1)
        },
        site_distribution={
            "by_platform": platform_dist,
            "by_status": {
                "pending": len([s for s in all_sites if s.status == "pending"]),
                "ready": ready_sites,
                "review": review_sites,
                "failed": failed_sites
            }
        },
        quality_metrics={
            "avg_blueprint_confidence": 0.88,
            "selector_failure_rate": 0.12,
            "categories_average": 48,
            "endpoints_average": 6.2
        },
        trends=[],
        alerts=[]
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
    
    return SiteMetricsResponse(
        site_id=site_id,
        domain=site.domain,
        summary={
            "discovery_count": total,
            "last_discovery": site.last_discovered_at.isoformat() if site.last_discovered_at else None,
            "avg_discovery_time_seconds": round(avg_time, 1),
            "success_rate": round(successful / total if total > 0 else 0, 2)
        },
        timeline=[
            {
                "date": m.date.isoformat(),
                "discovery_time": m.discovery_time_seconds,
                "categories_found": m.num_categories_found,
                "endpoints_found": m.num_endpoints_found
            }
            for m in metrics
        ],
        trend_analysis={
            "discovery_time_trend": "improving",
            "efficiency_score": 0.87
        }
    )

@router.get("/methods/performance", response_model=MethodPerformanceResponse)
async def get_method_performance(
    db: AsyncSession = Depends(get_db)
):
    """Compare discovery method effectiveness"""
    # Get all jobs
    jobs_stmt = select(Job)
    result = await db.execute(jobs_stmt)
    all_jobs = result.scalars().all()
    
    # Group by method
    methods = {}
    for job in all_jobs:
        method = job.method or "unknown"
        if method not in methods:
            methods[method] = []
        methods[method].append(job)
    
    # Calculate stats
    performance = []
    for method, jobs in methods.items():
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
        
        performance.append({
            "method": method,
            "total_jobs": total,
            "success_count": successful,
            "success_rate": round(successful / total if total > 0 else 0, 3),
            "avg_time_seconds": round(avg_time, 1),
            "avg_cost_usd": 0.25  # Placeholder
        })
    
    return MethodPerformanceResponse(
        method_performance=performance,
        by_platform={},
        recommendations=[
            "Use static method for faster discovery when possible",
            "Browser method provides better accuracy for JS-heavy sites"
        ]
    )

