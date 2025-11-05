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
    site_id = Column(UUID(as_uuid=True), ForeignKey("sites.site_id"), nullable=False, index=True)

    # Job Configuration
    job_type = Column(String(50), nullable=False, index=True)  # fingerprint, discovery, extraction, blueprint_update
    method = Column(String(50), nullable=True)  # static, browser, api, auto
    status = Column(String(50), default="queued", nullable=False, index=True)  # queued, running, success, failed, timeout, cancelled

    # Priority & Retry
    priority = Column(Integer, default=0, index=True)
    attempt_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)

    # Timing
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    heartbeat_at = Column(DateTime, nullable=True)

    # Execution
    worker_id = Column(String(100), nullable=True, index=True)
    duration_seconds = Column(Integer, nullable=True)

    # Error Handling
    error_code = Column(String(50), nullable=True)
    error_message = Column(Text, nullable=True)

    # Data
    payload = Column(JSON, nullable=True)  # Input parameters
    result = Column(JSON, nullable=True)  # Output results

    def __repr__(self):
        return f"<Job(job_id={self.job_id}, type={self.job_type}, status={self.status})>"

    def __str__(self):
        return f"Job {self.job_id}: {self.job_type} ({self.status})"

    @property
    def is_running(self):
        return self.status == "running"

    @property
    def is_completed(self):
        return self.status in ["success", "failed", "timeout", "cancelled"]

    @property
    def is_failed(self):
        return self.status == "failed"

    @property
    def can_retry(self):
        return self.attempt_count < self.max_retries

