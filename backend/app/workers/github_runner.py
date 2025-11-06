"""GitHub Actions worker runner - processes jobs from queue"""
import asyncio
import sys
import os
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from uuid import UUID

from app.config import settings
from app.models import Job
from app.workers.fingerprinter import _fingerprint_site_async
from app.workers.discoverer import _discover_site_async
from app.workers.selector_generator import _generate_selectors_async


async def process_queued_jobs(job_type: str, max_jobs: int = 5):
    """Process queued jobs of a specific type"""
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    processed = 0
    failed = 0
    
    async with async_session() as db:
        # Get queued jobs
        stmt = select(Job).where(
            Job.job_type == job_type,
            Job.status == "queued"
        ).limit(max_jobs)
        
        result = await db.execute(stmt)
        jobs = result.scalars().all()
        
        print(f"Found {len(jobs)} queued {job_type} jobs")
        
        for job in jobs:
            try:
                print(f"Processing job {job.job_id}...")
                
                if job_type == "fingerprint":
                    result = await _fingerprint_site_async(
                        str(job.site_id),
                        str(job.job_id)
                    )
                elif job_type == "discover":
                    # Feature G discovery
                    from app.workers.discoverer import _discover_site_async
                    result = await _discover_site_async(
                        str(job.site_id),
                        str(job.job_id)
                    )
                elif job_type == "selector_generation":
                    # Get blueprint_id from job payload
                    blueprint_id = job.payload.get("blueprint_id") if job.payload else None
                    fields = job.payload.get("fields", ["title", "price"]) if job.payload else ["title", "price"]
                    
                    result = await _generate_selectors_async(
                        blueprint_id,
                        str(job.job_id),
                        fields
                    )
                
                if result.get("success"):
                    processed += 1
                    print(f"✅ Job {job.job_id} completed successfully")
                else:
                    failed += 1
                    print(f"❌ Job {job.job_id} failed: {result.get('error')}")
                    
            except Exception as e:
                failed += 1
                print(f"❌ Job {job.job_id} error: {str(e)}")
    
    await engine.dispose()
    
    print(f"\n📊 Summary:")
    print(f"  Processed: {processed}")
    print(f"  Failed: {failed}")
    print(f"  Total: {len(jobs)}")
    
    return {"processed": processed, "failed": failed, "total": len(jobs)}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m app.workers.github_runner <job_type> [--max-jobs=N]")
        print("Job types: fingerprint, discovery, selector_generation")
        sys.exit(1)
    
    job_type = sys.argv[1]
    max_jobs = 5
    
    # Parse max-jobs argument
    for arg in sys.argv[2:]:
        if arg.startswith("--max-jobs="):
            max_jobs = int(arg.split("=")[1])
    
    print(f"🚀 Starting GitHub Actions worker for: {job_type}")
    print(f"   Max jobs per run: {max_jobs}")
    print()
    
    result = asyncio.run(process_queued_jobs(job_type, max_jobs))
    
    # Exit with error code if all jobs failed
    if result["total"] > 0 and result["failed"] == result["total"]:
        sys.exit(1)

