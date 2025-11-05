"""Pydantic schemas for request/response"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

# ============================================================================
# Sites
# ============================================================================

class SiteCreate(BaseModel):
    domain: str = Field(..., example="example-store.com")
    business_value_score: Optional[float] = Field(None, ge=0, le=1)
    priority: Optional[str] = None
    notes: Optional[str] = None

class SiteUpdate(BaseModel):
    business_value_score: Optional[float] = None
    priority: Optional[str] = None
    notes: Optional[str] = None

class SiteResponse(BaseModel):
    site_id: UUID
    domain: str
    platform: Optional[str] = None
    status: str
    complexity_score: Optional[float] = None
    business_value_score: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    last_discovered_at: Optional[datetime] = None
    blueprint_version: int = 0
    
    class Config:
        from_attributes = True

class SiteListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    sites: List[SiteResponse]

# ============================================================================
# Jobs
# ============================================================================

class JobCreate(BaseModel):
    site_id: UUID
    job_type: str = Field(..., example="discovery")
    method: Optional[str] = "auto"
    priority: Optional[str] = "normal"

class JobResponse(BaseModel):
    job_id: UUID
    site_id: UUID
    job_type: str
    method: Optional[str]
    status: str
    created_at: datetime
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    attempt_count: int
    
    class Config:
        from_attributes = True

class JobListResponse(BaseModel):
    total: int
    jobs: List[JobResponse]

# ============================================================================
# Blueprints
# ============================================================================

class BlueprintResponse(BaseModel):
    blueprint_id: UUID
    site_id: UUID
    version: int
    confidence_score: Optional[float] = None
    categories_data: Dict[str, Any]
    endpoints_data: Dict[str, Any]
    render_hints_data: Dict[str, Any]
    selectors_data: Dict[str, Any]
    created_at: datetime
    created_by: Optional[str] = None
    
    class Config:
        from_attributes = True

class BlueprintListResponse(BaseModel):
    site_id: UUID
    total_versions: int
    versions: List[Dict[str, Any]]

# ============================================================================
# Analytics
# ============================================================================

class DashboardMetricsResponse(BaseModel):
    total_sites: int
    sites_new: int
    sites_ready: int
    sites_in_review: int
    sites_failed: int
    discovery_metrics: Dict[str, Any]
    site_distribution: Dict[str, Any]
    quality_metrics: Dict[str, Any]
    trends: List[Dict[str, Any]]
    alerts: List[Dict[str, Any]]

class SiteMetricsResponse(BaseModel):
    site_id: UUID
    domain: str
    summary: Dict[str, Any]
    timeline: List[Dict[str, Any]]
    trend_analysis: Dict[str, Any]

class MethodPerformanceResponse(BaseModel):
    method_performance: List[Dict[str, Any]]
    by_platform: Dict[str, Any]
    recommendations: List[str]

# ============================================================================
# Auth
# ============================================================================

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class LoginRequest(BaseModel):
    username: str
    password: str

# ============================================================================
# Error Response
# ============================================================================

class ErrorResponse(BaseModel):
    error: Dict[str, Any] = Field(..., example={
        "code": "ERR_CODE",
        "message": "Human-readable message",
        "request_id": "req-uuid"
    })

