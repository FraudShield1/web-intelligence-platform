"""Blueprint request/response schemas"""

from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime
from uuid import UUID


class Category(BaseModel):
    """Category information"""
    id: str
    name: str
    slug: str
    url: str
    parent_id: Optional[str] = None
    depth: int
    confidence: float = Field(..., ge=0, le=1)


class Endpoint(BaseModel):
    """API endpoint information"""
    url: str
    method: str
    params: Optional[dict] = None
    response_schema: Optional[dict] = None
    confidence: float = Field(..., ge=0, le=1)


class Selector(BaseModel):
    """Selector information"""
    selector_id: Optional[str] = None
    field_name: str
    css_selector: Optional[str] = None
    xpath: Optional[str] = None
    confidence: float = Field(..., ge=0, le=1)
    generation_method: Optional[str] = None


class RenderHints(BaseModel):
    """Rendering hints"""
    requires_js: bool = False
    browser_type: Optional[str] = None
    wait_for_selector: Optional[str] = None
    timeout_seconds: int = 30


class BlueprintResponse(BaseModel):
    """Blueprint (Site Intelligence Object) response"""
    blueprint_id: UUID
    site_id: UUID
    version: int
    confidence_score: Optional[float]
    categories_data: List[Category]
    endpoints_data: List[Endpoint]
    render_hints_data: RenderHints
    selectors_data: List[Selector]
    created_at: datetime
    created_by: Optional[str]
    notes: Optional[str]

    class Config:
        from_attributes = True


class BlueprintListResponse(BaseModel):
    """List of blueprint versions"""
    site_id: UUID
    total_versions: int
    versions: List[dict]

