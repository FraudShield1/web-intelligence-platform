"""Site model"""

from sqlalchemy import Column, String, Float, DateTime, Integer, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.database import Base


class Site(Base):
    """Site entity - represents a website to be discovered and analyzed"""

    __tablename__ = "sites"

    # Primary Key
    site_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)

    # Basic Info
    domain = Column(String(255), nullable=False, unique=True, index=True)
    platform = Column(String(100), nullable=True, index=True)  # shopify, magento, custom, etc.
    status = Column(String(50), default="pending", nullable=False, index=True)  # pending, ready, review, failed

    # Scores
    complexity_score = Column(Float, nullable=True)  # 0-1
    business_value_score = Column(Float, nullable=True)  # 0-1

    # Fingerprint Data
    fingerprint_data = Column(JSON, nullable=True)  # Detected tech stack, CMS, frameworks

    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_discovered_at = Column(DateTime, nullable=True)

    # Blueprint Versioning
    blueprint_version = Column(Integer, default=0)

    # Metadata
    notes = Column(Text, nullable=True)
    organization_id = Column(UUID(as_uuid=True), nullable=True)
    created_by = Column(String(100), nullable=True)

    def __repr__(self):
        return f"<Site(site_id={self.site_id}, domain={self.domain}, status={self.status})>"

    def __str__(self):
        return f"{self.domain} ({self.status})"

