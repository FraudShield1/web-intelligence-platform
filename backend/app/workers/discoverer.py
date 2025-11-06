"""Discoverer worker - finds categories and product structures using LLM"""
import asyncio
from uuid import UUID, uuid4
from datetime import datetime
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.celery_app import celery_app
from app.config import settings
from app.models import Site, Job, Blueprint
from app.services.llm_service import llm_service


async def _discover_site_async(site_id: str, job_id: str):
    """Async discovery logic"""
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
        
        # Update job
        job.status = "running"
        job.started_at = datetime.utcnow()
        await db.commit()
        
        try:
            # Fetch site HTML
            url = f"https://{site.domain}"
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                response = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
                html = response.text
            
            # Analyze with LLM
            analysis = await llm_service.analyze_site_structure(html, url)
            
            if not analysis.get("success"):
                raise Exception(analysis.get("error", "LLM analysis failed"))
            
            # Get or create blueprint
            blueprint_stmt = select(Blueprint).where(
                Blueprint.site_id == UUID(site_id)
            ).order_by(Blueprint.version.desc()).limit(1)
            result = await db.execute(blueprint_stmt)
            existing_blueprint = result.scalar_one_or_none()
            
            version = (existing_blueprint.version + 1) if existing_blueprint else 1
            
            # Create new blueprint
            blueprint = Blueprint(
                blueprint_id=uuid4(),
                site_id=UUID(site_id),
                version=version,
                confidence_score=0.8,  # Base confidence from discovery
                categories_data={"discovered": True, "analysis": analysis},
                endpoints_data={},
                render_hints_data={"requires_js": site.fingerprint_data.get("requires_js", False)},
                selectors_data={},
                created_by="system",
                notes=f"Discovered via LLM analysis (job {job_id})"
            )
            
            db.add(blueprint)
            
            # Update site
            site.status = "discovered"
            site.blueprint_version = version
            site.last_discovered_at = datetime.utcnow()
            
            # Update job
            job.status = "success"
            job.completed_at = datetime.utcnow()
            job.result = {"blueprint_id": str(blueprint.blueprint_id), "version": version}
            
            await db.commit()
            
            return {
                "success": True,
                "site_id": site_id,
                "blueprint_id": str(blueprint.blueprint_id),
                "version": version
            }
            
        except Exception as e:
            job.status = "failed"
            job.ended_at = datetime.utcnow()
            job.error_message = str(e)
            await db.commit()
            
            return {"success": False, "error": str(e)}
        
        finally:
            await engine.dispose()


@celery_app.task(name="workers.discover_site", bind=True)
def discover_site(self, site_id: str, job_id: str):
    """Celery task to discover site structure"""
    try:
        result = asyncio.run(_discover_site_async(site_id, job_id))
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}
