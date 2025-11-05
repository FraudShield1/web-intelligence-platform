"""Blueprint model for storing site intelligence objects"""

from sqlalchemy import Column, String, DateTime, Integer, JSON, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.database import Base


class Blueprint(Base):
    """Blueprint entity - versioned Site Intelligence Object"""

    __tablename__ = "blueprints"

    # Primary Key
    blueprint_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)

    # Foreign Keys
    site_id = Column(UUID(as_uuid=True), ForeignKey("sites.site_id"), nullable=False, index=True)

    # Version Management
    version = Column(Integer, nullable=False)

    # Quality Metrics
    confidence_score = Column(Float, nullable=True)  # 0-1

    # Extracted Data (JSON)
    categories_data = Column(JSON, nullable=False, default=[])  # Array of categories
    endpoints_data = Column(JSON, nullable=False, default=[])  # Array of API endpoints
    render_hints_data = Column(JSON, nullable=False, default={})  # Rendering requirements
    selectors_data = Column(JSON, nullable=False, default=[])  # Array of selectors

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    created_by = Column(String(100), nullable=True)
    notes = Column(String(1000), nullable=True)

    __table_args__ = (
        # Unique constraint for site_id and version combination
        __import__("sqlalchemy").UniqueConstraint("site_id", "version", name="uq_site_version"),
    )

    def __repr__(self):
        return f"<Blueprint(blueprint_id={self.blueprint_id}, site_id={self.site_id}, version={self.version})>"

    def __str__(self):
        return f"Blueprint v{self.version} (confidence: {self.confidence_score})"

    @property
    def categories_count(self):
        return len(self.categories_data) if self.categories_data else 0

    @property
    def endpoints_count(self):
        return len(self.endpoints_data) if self.endpoints_data else 0

    @property
    def selectors_count(self):
        return len(self.selectors_data) if self.selectors_data else 0

