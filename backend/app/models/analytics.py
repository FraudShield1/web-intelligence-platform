"""Analytics metric model"""
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.database import Base


class AnalyticsMetric(Base):
    __tablename__ = "analytics_metrics"

    metric_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(UUID(as_uuid=True), ForeignKey("sites.site_id"), nullable=True)
    date = Column(DateTime, default=datetime.utcnow)
    discovery_time_seconds = Column(Integer)
    num_categories_found = Column(Integer)
    num_endpoints_found = Column(Integer)
    selector_failure_rate = Column(Float)
    fetch_cost_usd = Column(Float)
    items_extracted = Column(Integer)
    method = Column(String(50))
    job_id = Column(UUID(as_uuid=True))
    created_at = Column(DateTime, default=datetime.utcnow)

