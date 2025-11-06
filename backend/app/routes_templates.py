"""Template management API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import datetime

from app.database import get_db
from app.models import PlatformTemplate  # Exported from app.models/__init__.py
from app.schemas.template import TemplateCreate, TemplateUpdate, TemplateResponse, TemplateListResponse

router = APIRouter(prefix="/templates", tags=["templates"])


@router.post("", response_model=TemplateResponse, status_code=201)
async def create_template(
    template_data: TemplateCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new platform template"""
    template = PlatformTemplate(
        platform_name=template_data.platform_name,
        platform_variant=template_data.platform_variant,
        category_selectors=template_data.category_selectors,
        product_list_selectors=template_data.product_list_selectors,
        api_patterns=template_data.api_patterns,
        render_hints=template_data.render_hints,
        confidence=template_data.confidence,
        active=template_data.active,
        match_patterns=template_data.match_patterns
    )
    
    db.add(template)
    await db.commit()
    await db.refresh(template)
    
    return template


@router.get("", response_model=TemplateListResponse)
async def list_templates(
    platform_name: Optional[str] = Query(None, description="Filter by platform name"),
    active: Optional[bool] = Query(None, description="Filter by active status"),
    limit: int = Query(50, le=100, ge=1),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """List all templates with optional filtering"""
    stmt = select(PlatformTemplate)
    
    if platform_name:
        stmt = stmt.where(PlatformTemplate.platform_name == platform_name)
    
    if active is not None:
        stmt = stmt.where(PlatformTemplate.active == active)
    
    # Get total count
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0
    
    # Get paginated results
    stmt = stmt.order_by(PlatformTemplate.platform_name, PlatformTemplate.created_at.desc())
    stmt = stmt.limit(limit).offset(offset)
    
    result = await db.execute(stmt)
    templates = result.scalars().all()
    
    return TemplateListResponse(
        templates=[TemplateResponse.model_validate(t) for t in templates],
        total=total
    )


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific template"""
    stmt = select(PlatformTemplate).where(PlatformTemplate.template_id == template_id)
    result = await db.execute(stmt)
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return template


@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: UUID,
    template_data: TemplateUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a template"""
    stmt = select(PlatformTemplate).where(PlatformTemplate.template_id == template_id)
    result = await db.execute(stmt)
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Update fields
    update_data = template_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(template, field, value)
    
    template.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(template)
    
    return template


@router.delete("/{template_id}", status_code=204)
async def delete_template(
    template_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete a template"""
    stmt = select(PlatformTemplate).where(PlatformTemplate.template_id == template_id)
    result = await db.execute(stmt)
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    await db.delete(template)
    await db.commit()
    
    return None


@router.get("/platform/{platform_name}/best", response_model=TemplateResponse)
async def get_best_template_for_platform(
    platform_name: str,
    variant: Optional[str] = Query(None, description="Platform variant"),
    db: AsyncSession = Depends(get_db)
):
    """Get the best matching template for a platform"""
    stmt = select(PlatformTemplate).where(
        PlatformTemplate.platform_name == platform_name,
        PlatformTemplate.active == True
    )
    
    if variant:
        stmt = stmt.where(PlatformTemplate.platform_variant == variant)
    
    # Order by confidence (highest first), then by variant match
    stmt = stmt.order_by(
        PlatformTemplate.confidence.desc().nulls_last(),
        PlatformTemplate.created_at.desc()
    ).limit(1)
    
    result = await db.execute(stmt)
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(
            status_code=404,
            detail=f"No active template found for platform '{platform_name}'"
        )
    
    return template

