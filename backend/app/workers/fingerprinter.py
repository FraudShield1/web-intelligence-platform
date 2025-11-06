"""Fingerprinter worker - analyzes site and detects platform/CMS"""
import asyncio
from uuid import UUID
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.celery_app import celery_app
from app.config import settings
from app.models import Site, Job
from app.services.fingerprint_service import fingerprint_service


async def _fingerprint_site_async(site_id: str, job_id: str):
    """Async fingerprinting logic"""
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        # Get site
        site_stmt = select(Site).where(Site.site_id == UUID(site_id))
        result = await db.execute(site_stmt)
        site = result.scalar_one_or_none()
        
        if not site:
            return {"error": "Site not found"}
        
        # Get job
        job_stmt = select(Job).where(Job.job_id == UUID(job_id))
        result = await db.execute(job_stmt)
        job = result.scalar_one_or_none()
        
        if not job:
            return {"error": "Job not found"}
        
        # Update job status
        job.status = "running"
        job.started_at = datetime.utcnow()
        await db.commit()
        
        try:
            # Run fingerprinting
            url = f"https://{site.domain}"
            fingerprint = await fingerprint_service.fingerprint_site(url)
            
            # Update site with fingerprint data
            site.platform = fingerprint.get("platform", "unknown")
            site.fingerprint_data = fingerprint
            site.complexity_score = fingerprint.get("complexity_score", 0.5)
            site.status = "fingerprinted"
            site.last_discovered_at = datetime.utcnow()
            
            # Update job
            job.status = "success"
            job.completed_at = datetime.utcnow()
            job.result = fingerprint
            
            await db.commit()
            
            return {
                "success": True,
                "site_id": site_id,
                "platform": fingerprint.get("platform"),
                "complexity": fingerprint.get("complexity_score")
            }
            
        except Exception as e:
            job.status = "failed"
            job.ended_at = datetime.utcnow()
            job.error_message = str(e)
            site.status = "error"
            await db.commit()
            
            return {"success": False, "error": str(e)}
        
        finally:
            await engine.dispose()


@celery_app.task(name="workers.fingerprint_site", bind=True)
def fingerprint_site(self, site_id: str, job_id: str):
    """Celery task to fingerprint a site"""
    try:
        result = asyncio.run(_fingerprint_site_async(site_id, job_id))
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}
