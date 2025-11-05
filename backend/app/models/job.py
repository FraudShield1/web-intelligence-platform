"""Job model for tracking discovery and processing tasks"""

from sqlalchemy import Column, String, DateTime, Integer, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.database import Base


class Job(Base):
    """Job entity - represents a discovery or processing job"""

    __tablename__ = "jobs"

    # Primary Key
    job_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)

    # Foreign Keys
    site_id = Column(UUID(as_uuid=True), ForeignKey("sites.site_id", ondelete="CASCADE"), nullable=True, index=True)

    # Job Configuration
    job_type = Column(String(100), nullable=False)  # fingerprint, discovery, extraction, blueprint_update
    method = Column(String(50), nullable=True)  # static, browser, api, auto
    status = Column(String(50), default="pending", nullable=False, index=True)  # pending, running, success, failed

    # Progress
    progress = Column(Integer, default=0)

    # Data
    result = Column(JSON, nullable=True)  # Output results
    error_message = Column(Text, nullable=True)

    # Timing
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Job(job_id={self.job_id}, type={self.job_type}, status={self.status})>"

    def __str__(self):
        return f"Job {self.job_id}: {self.job_type} ({self.status})"

    @property
    def is_running(self):
        return self.status == "running"

    @property
    def is_completed(self):
        return self.status in ["success", "failed"]

    @property
    def is_failed(self):
        return self.status == "failed"
    
    @property
    def duration_seconds(self):
        """Calculate duration in seconds if job is completed"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

