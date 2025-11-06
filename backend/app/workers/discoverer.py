"""Discoverer worker - Feature G: Advanced site discovery with compliance"""
import asyncio
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.celery_app import celery_app
from app.config import settings
from app.models import Site, Job, Blueprint
from app.services.discovery_service import discovery_service
from app.services.template_matcher import template_matcher


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
            # Run Feature G discovery (all 6 phases with compliance)
            url = f"https://{site.domain}"
            print(f"🚀 Starting Feature G discovery for {url}")
            
            discovery_result = await discovery_service.discover_site(url)
            
            if not discovery_result.get("success"):
                error_msg = discovery_result.get("error", "Discovery failed")
                raise Exception(f"Discovery failed: {error_msg}")
            
            print(f"✅ Discovery complete! Confidence: {discovery_result['confidence_score']}")
            
            # Try to find and apply platform template (Feature F)
            template = None
            if site.platform:
                print(f"🔍 Looking for template for platform: {site.platform}")
                template = await template_matcher.find_template(
                    platform_name=site.platform,
                    fingerprint_data=site.fingerprint_data,
                    variant=None,  # Could extract from fingerprint_data if needed
                    db=db
                )
                
                if template:
                    print(f"✅ Found template: {template.platform_name} (confidence: {template.confidence})")
                    # Merge template data with discovery results
                    discovery_result = template_matcher.apply_template_to_blueprint(
                        template,
                        discovery_result
                    )
                    print("✅ Template applied to blueprint")
                else:
                    print("ℹ️ No template found, using discovery data only")
            
            # Get existing blueprints to determine next version
            blueprint_stmt = select(Blueprint).where(
                Blueprint.site_id == UUID(site_id)
            ).order_by(Blueprint.version.desc()).limit(1)
            result = await db.execute(blueprint_stmt)
            existing_blueprint = result.scalar_one_or_none()
            
            version = (existing_blueprint.version + 1) if existing_blueprint else 1
            
            # Create blueprint from discovery results
            blueprint = Blueprint(
                blueprint_id=uuid4(),
                site_id=UUID(site_id),
                version=version,
                confidence_score=discovery_result["confidence_score"],
                # Store categories data
                categories_data=discovery_result["categories"].get("categories", {}),
                # Store endpoints data
                endpoints_data=discovery_result["endpoints"].get("endpoints", []),
                # Store render hints
                render_hints_data=discovery_result.get("render_hints", {}),
                # Store selectors data
                selectors_data=discovery_result["selectors"].get("selectors", {}),
                created_by="system_featureG",
                notes=f"Feature G discovery (job {job_id}). Found {discovery_result['categories'].get('total_categories', 0)} categories, {discovery_result['products'].get('total_products_found', 0)} products, {len(discovery_result['selectors'].get('selectors', {}))} selectors."
            )
            
            db.add(blueprint)
            
            # Update site with discovery status
            site.status = "discovered"
            site.blueprint_version = version
            site.last_discovered_at = datetime.utcnow()
            
            # Update job with complete results
            job.status = "success"
            job.completed_at = datetime.utcnow()
            job.result = {
                "blueprint_id": str(blueprint.blueprint_id),
                "version": version,
                "confidence_score": discovery_result["confidence_score"],
                "categories_found": discovery_result["categories"].get("total_categories", 0),
                "products_found": discovery_result["products"].get("total_products_found", 0),
                "selectors_found": len(discovery_result["selectors"].get("selectors", {})),
                "endpoints_found": discovery_result["endpoints"].get("total_endpoints", 0),
                "duration_seconds": discovery_result.get("duration_seconds", 0)
            }
            
            await db.commit()
            
            print(f"💾 Blueprint v{version} saved successfully!")
            
            return {
                "success": True,
                "site_id": site_id,
                "blueprint_id": str(blueprint.blueprint_id),
                "version": version,
                "discovery_summary": job.result
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
