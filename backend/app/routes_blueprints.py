"""Blueprints API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import uuid as uuid_lib

from app.database import get_db
from app.models import Blueprint, Site
from app.schemas import BlueprintResponse, BlueprintListResponse
# Temporarily disabled for easier testing
# from app.security import get_current_user, require_roles

router = APIRouter(prefix="/blueprints", tags=["blueprints"])

@router.get("/sites/{site_id}/latest", response_model=BlueprintResponse)
async def get_latest_blueprint(
    site_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get the most recent blueprint for a site"""
    # Verify site exists
    site_stmt = select(Site).where(Site.site_id == site_id)
    result = await db.execute(site_stmt)
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Site not found")
    
    # Get latest blueprint
    stmt = select(Blueprint).where(
        Blueprint.site_id == site_id
    ).order_by(Blueprint.version.desc()).limit(1)
    
    result = await db.execute(stmt)
    blueprint = result.scalar_one_or_none()
    
    if not blueprint:
        raise HTTPException(status_code=404, detail="Blueprint not found")
    
    return blueprint

@router.get("/{blueprint_id}", response_model=BlueprintResponse)
async def get_blueprint(
    blueprint_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific blueprint"""
    stmt = select(Blueprint).where(Blueprint.blueprint_id == blueprint_id)
    result = await db.execute(stmt)
    blueprint = result.scalar_one_or_none()
    
    if not blueprint:
        raise HTTPException(status_code=404, detail="Blueprint not found")
    
    return blueprint

@router.get("/sites/{site_id}/versions", response_model=BlueprintListResponse)
async def list_blueprint_versions(
    site_id: UUID,
    limit: int = Query(10, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List all versions of a site's blueprints"""
    # Verify site exists
    site_stmt = select(Site).where(Site.site_id == site_id)
    result = await db.execute(site_stmt)
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Site not found")
    
    # Get blueprints
    stmt = select(Blueprint).where(
        Blueprint.site_id == site_id
    ).order_by(Blueprint.version.desc()).limit(limit)
    
    result = await db.execute(stmt)
    blueprints = result.scalars().all()
    
    versions = [
        {
            "blueprint_id": str(b.blueprint_id),
            "version": b.version,
            "confidence_score": b.confidence_score,
            "created_at": b.created_at.isoformat()
        }
        for b in blueprints
    ]
    
    return BlueprintListResponse(
        site_id=site_id,
        total_versions=len(blueprints),
        versions=versions
    )

@router.post("/{blueprint_id}/rollback", response_model=BlueprintResponse, status_code=201)
async def rollback_blueprint(
    blueprint_id: UUID,
    to_version: int,
    reason: str = None,
    db: AsyncSession = Depends(get_db)
):
    """Rollback to a previous blueprint version"""
    # Get current blueprint
    stmt = select(Blueprint).where(Blueprint.blueprint_id == blueprint_id)
    result = await db.execute(stmt)
    current = result.scalar_one_or_none()
    
    if not current:
        raise HTTPException(status_code=404, detail="Blueprint not found")
    
    # Get target version
    target_stmt = select(Blueprint).where(
        (Blueprint.site_id == current.site_id) &
        (Blueprint.version == to_version)
    )
    result = await db.execute(target_stmt)
    target = result.scalar_one_or_none()
    
    if not target:
        raise HTTPException(status_code=404, detail="Target version not found")
    
    # Create new version by copying target
    new_blueprint = Blueprint(
        blueprint_id=uuid_lib.uuid4(),
        site_id=current.site_id,
        version=current.version + 1,
        confidence_score=target.confidence_score,
        categories_data=target.categories_data,
        endpoints_data=target.endpoints_data,
        render_hints_data=target.render_hints_data,
        selectors_data=target.selectors_data,
        notes=f"Rollback from {current.version} to {to_version}. Reason: {reason or 'Not specified'}"
    )
    db.add(new_blueprint)
    await db.commit()
    await db.refresh(new_blueprint)
    
    return new_blueprint

@router.get("/{blueprint_id}/export", dependencies=[Depends(get_current_user)])
async def export_blueprint(
    blueprint_id: UUID,
    format: str = Query("json", regex="^(json|yaml)$"),
    db: AsyncSession = Depends(get_db)
):
    """Export blueprint as JSON or YAML"""
    from fastapi.responses import Response
    import json
    import yaml
    
    stmt = select(Blueprint).where(Blueprint.blueprint_id == blueprint_id)
    result = await db.execute(stmt)
    blueprint = result.scalar_one_or_none()
    
    if not blueprint:
        raise HTTPException(status_code=404, detail="Blueprint not found")
    
    export_data = {
        "blueprint_id": str(blueprint.blueprint_id),
        "site_id": str(blueprint.site_id),
        "version": blueprint.version,
        "confidence_score": blueprint.confidence_score,
        "exported_at": blueprint.created_at.isoformat() if blueprint.created_at else None,
        "categories": blueprint.categories_data or {},
        "endpoints": blueprint.endpoints_data or {},
        "selectors": blueprint.selectors_data or {},
        "render_hints": blueprint.render_hints_data or {}
    }
    
    if format == "yaml":
        yaml_content = yaml.dump(export_data, default_flow_style=False, allow_unicode=True)
        return Response(
            content=yaml_content,
            media_type="application/x-yaml",
            headers={"Content-Disposition": f"attachment; filename=blueprint_{blueprint_id}.yaml"}
        )
    else:
        json_content = json.dumps(export_data, indent=2)
        return Response(
            content=json_content,
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=blueprint_{blueprint_id}.json"}
        )

