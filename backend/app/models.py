"""Database models for Web Intelligence Platform"""
from sqlalchemy import Column, String, Float, DateTime, JSON, UUID, Integer, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

Base = declarative_base()

class Site(Base):
    """Master record for each discovered website"""
    __tablename__ = "sites"
    
    site_id = Column(UUID, primary_key=True, default=uuid.uuid4)
    domain = Column(String(255), unique=True, nullable=False, index=True)
    platform = Column(String(100), nullable=True)
    status = Column(String(50), default='pending', index=True)
    fingerprint_data = Column(JSON, nullable=True)
    complexity_score = Column(Float, nullable=True)
    business_value_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_discovered_at = Column(DateTime, nullable=True)
    blueprint_version = Column(Integer, default=0)
    notes = Column(Text, nullable=True)
    
    # Relationships
    jobs = relationship("Job", back_populates="site", cascade="all, delete-orphan")
    blueprints = relationship("Blueprint", back_populates="site", cascade="all, delete-orphan")
    metrics = relationship("AnalyticsMetric", back_populates="site", cascade="all, delete-orphan")

class Job(Base):
    """Job queue for discovery tasks"""
    __tablename__ = "jobs"
    
    job_id = Column(UUID, primary_key=True, default=uuid.uuid4)
    site_id = Column(UUID, ForeignKey("sites.site_id"), nullable=False, index=True)
    job_type = Column(String(50), nullable=False)  # fingerprint, discovery, extraction
    method = Column(String(50), nullable=True)  # static, browser, api, auto
    status = Column(String(50), default='queued', index=True)  # queued, running, success, failed
    priority = Column(Integer, default=0, index=True)
    attempt_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    error_code = Column(String(50), nullable=True)
    error_message = Column(Text, nullable=True)
    worker_id = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    payload = Column(JSON, nullable=True)
    result = Column(JSON, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    heartbeat_at = Column(DateTime, nullable=True)
    
    # Relationships
    site = relationship("Site", back_populates="jobs")

class Blueprint(Base):
    """Site intelligence object with versioning"""
    __tablename__ = "blueprints"
    
    blueprint_id = Column(UUID, primary_key=True, default=uuid.uuid4)
    site_id = Column(UUID, ForeignKey("sites.site_id"), nullable=False, index=True)
    version = Column(Integer, nullable=False)
    confidence_score = Column(Float, nullable=True)
    categories_data = Column(JSON, default={})
    endpoints_data = Column(JSON, default={})
    render_hints_data = Column(JSON, default={})
    selectors_data = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    site = relationship("Site", back_populates="blueprints")
    selectors = relationship("Selector", back_populates="blueprint", cascade="all, delete-orphan")

class Selector(Base):
    """Individual CSS/XPath selectors"""
    __tablename__ = "selectors"
    
    selector_id = Column(UUID, primary_key=True, default=uuid.uuid4)
    blueprint_id = Column(UUID, ForeignKey("blueprints.blueprint_id"), nullable=False)
    field_name = Column(String(100), nullable=False)
    css_selector = Column(String(500), nullable=True)
    xpath = Column(String(500), nullable=True)
    confidence = Column(Float, nullable=True)
    generation_method = Column(String(50), nullable=True)  # llm, heuristic, manual
    test_pass_rate = Column(Float, nullable=True)
    test_count = Column(Integer, default=0)
    test_failures = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_tested_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    blueprint = relationship("Blueprint", back_populates="selectors")

class AnalyticsMetric(Base):
    """Time-series metrics for reporting"""
    __tablename__ = "analytics_metrics"
    
    metric_id = Column(UUID, primary_key=True, default=uuid.uuid4)
    site_id = Column(UUID, ForeignKey("sites.site_id"), nullable=True)
    date = Column(DateTime, default=datetime.utcnow, index=True)
    discovery_time_seconds = Column(Integer, nullable=True)
    num_categories_found = Column(Integer, nullable=True)
    num_endpoints_found = Column(Integer, nullable=True)
    selector_failure_rate = Column(Float, nullable=True)
    fetch_cost_usd = Column(Float, nullable=True)
    items_extracted = Column(Integer, nullable=True)
    method = Column(String(50), nullable=True)
    job_id = Column(UUID, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    site = relationship("Site", back_populates="metrics")

class PlatformTemplate(Base):
    """Reusable platform patterns"""
    __tablename__ = "platform_templates"
    
    template_id = Column(UUID, primary_key=True, default=uuid.uuid4)
    platform_name = Column(String(100), nullable=False, index=True)
    platform_variant = Column(String(100), nullable=True)
    category_selectors = Column(JSON, nullable=True)
    product_list_selectors = Column(JSON, nullable=True)
    api_patterns = Column(JSON, nullable=True)
    render_hints = Column(JSON, nullable=True)
    confidence = Column(Float, nullable=True)
    active = Column(Boolean, default=True)
    match_patterns = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class User(Base):
    """User accounts"""
    __tablename__ = "users"
    
    user_id = Column(UUID, primary_key=True, default=uuid.uuid4)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=True)
    role = Column(String(50), default='viewer')  # admin, product_lead, scraper_engineer, viewer
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

