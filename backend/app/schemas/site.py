"""Site request/response schemas"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class SiteCreate(BaseModel):
    """Request body for creating a new site"""
    domain: str = Field(..., min_length=3, example="example.com", description="Website domain")
    business_value_score: Optional[float] = Field(None, ge=0, le=1, description="Business value (0-1)")
    priority: Optional[str] = Field(None, example="high", description="Priority level")
    notes: Optional[str] = Field(None, description="Additional notes")


class SiteUpdate(BaseModel):
    """Request body for updating a site"""
    business_value_score: Optional[float] = Field(None, ge=0, le=1)
    priority: Optional[str] = None
    notes: Optional[str] = None


class SiteResponse(BaseModel):
    """Site entity response"""
    site_id: UUID
    domain: str
    platform: Optional[str]
    status: str
    complexity_score: Optional[float]
    business_value_score: Optional[float]
    blueprint_version: int
    created_at: datetime
    updated_at: datetime
    last_discovered_at: Optional[datetime]

    class Config:
        from_attributes = True


class SiteDetailResponse(SiteResponse):
    """Detailed site information"""
    fingerprint_data: Optional[dict]
    notes: Optional[str]
    created_by: Optional[str]


class SiteListResponse(BaseModel):
    """Paginated list of sites"""
    total: int
    limit: int
    offset: int
    sites: List[SiteResponse]

