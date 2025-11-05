"""User model for authentication and authorization"""

from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.database import Base


class User(Base):
    """User entity for authentication"""

    __tablename__ = "users"

    # Primary Key
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)

    # Credentials
    username = Column(String(100), nullable=False, unique=True, index=True)
    email = Column(String(100), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)

    # Role-Based Access Control
    role = Column(String(50), default="viewer")  # admin, product_lead, scraper_engineer, viewer

    # Status
    is_active = Column(Boolean, default=True, index=True)

    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)

    # Organization (for multi-tenant)
    organization_id = Column(UUID(as_uuid=True), nullable=True)

    def __repr__(self):
        return f"<User(user_id={self.user_id}, username={self.username}, role={self.role})>"

    def __str__(self):
        return f"{self.username} ({self.role})"

    @property
    def is_admin(self):
        return self.role == "admin"

    @property
    def is_product_lead(self):
        return self.role == "product_lead"

    @property
    def is_scraper_engineer(self):
        return self.role == "scraper_engineer"

