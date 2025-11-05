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
    priority: Optional[int] = Field(0, description="Priority level")
    parameters: Optional[dict] = Field(None, description="Job-specific parameters")


class JobProgress(BaseModel):
    """Job progress information"""
    current_step: str
    percentage: int = Field(..., ge=0, le=100)
    message: str


class JobResponse(BaseModel):
    """Job entity response"""
    job_id: UUID
    site_id: UUID
    job_type: str
    method: Optional[str]
    status: str
    priority: int
    attempt_count: int
    created_at: datetime
    started_at: Optional[datetime]
    ended_at: Optional[datetime]

    class Config:
        from_attributes = True


class JobDetailResponse(JobResponse):
    """Detailed job information"""
    heartbeat_at: Optional[datetime]
    worker_id: Optional[str]
    duration_seconds: Optional[int]
    error_code: Optional[str]
    error_message: Optional[str]
    payload: Optional[dict]
    result: Optional[dict]
    progress: Optional[JobProgress]


class JobListResponse(BaseModel):
    """Paginated list of jobs"""
    total: int
    limit: int
    offset: int
    jobs: List[JobResponse]

