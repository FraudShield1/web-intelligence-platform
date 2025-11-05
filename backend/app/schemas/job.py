"""Job request/response schemas"""

from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime
from uuid import UUID


class JobCreate(BaseModel):
    """Request body for creating a new job"""
    site_id: UUID = Field(..., description="Site ID to process")
    job_type: str = Field(..., description="Job type: fingerprint, discovery, extraction")
    method: Optional[str] = Field(None, description="Method: static, browser, api, auto")
    progress: Optional[int] = Field(0, description="Progress percentage")


class JobProgress(BaseModel):
    """Job progress information"""
    current_step: str
    percentage: int = Field(..., ge=0, le=100)
    message: str


class JobResponse(BaseModel):
    """Job entity response"""
    job_id: UUID
    site_id: Optional[UUID]
    job_type: str
    method: Optional[str]
    status: str
    progress: int
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]
    result: Optional[dict]

    class Config:
        from_attributes = True


class JobDetailResponse(JobResponse):
    """Detailed job information - same as JobResponse for now"""
    pass


class JobListResponse(BaseModel):
    """Paginated list of jobs"""
    total: int
    limit: int
    offset: int
    jobs: List[JobResponse]

