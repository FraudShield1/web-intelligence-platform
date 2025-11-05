"""Selector model for tracking CSS/XPath selectors"""

from sqlalchemy import Column, String, DateTime, Float, Integer, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.database import Base


class Selector(Base):
    """Selector entity - individual CSS/XPath selector for data extraction"""

    __tablename__ = "selectors"

    # Primary Key
    selector_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)

    # Foreign Keys
    blueprint_id = Column(UUID(as_uuid=True), ForeignKey("blueprints.blueprint_id"), nullable=False, index=True)

    # Field Information
    field_name = Column(String(100), nullable=False, index=True)  # price, title, image_url, etc.

    # Selectors
    css_selector = Column(String(500), nullable=True)
    xpath = Column(String(500), nullable=True)

    # Quality
    confidence = Column(Float, nullable=True)  # 0-1
    generation_method = Column(String(50), nullable=True)  # llm, heuristic, manual, template
    test_pass_rate = Column(Float, nullable=True)  # % of test pages where selector worked

    # Testing Data
    test_count = Column(Integer, default=0)
    test_failures = Column(Integer, default=0)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    last_tested_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)

    def __repr__(self):
        return f"<Selector(selector_id={self.selector_id}, field_name={self.field_name})>"

    def __str__(self):
        return f"{self.field_name} (confidence: {self.confidence})"

    @property
    def is_healthy(self):
        """Check if selector is healthy based on pass rate"""
        if self.test_pass_rate is None:
            return None
        return self.test_pass_rate >= 0.9

    @property
    def is_at_risk(self):
        """Check if selector is at risk"""
        if self.test_pass_rate is None:
            return None
        return 0.7 <= self.test_pass_rate < 0.9

    @property
    def is_broken(self):
        """Check if selector is broken"""
        if self.test_pass_rate is None:
            return None
        return self.test_pass_rate < 0.7

