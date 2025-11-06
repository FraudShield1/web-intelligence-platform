"""Database models"""

from app.database import Base
from app.models.site import Site
from app.models.job import Job
from app.models.blueprint import Blueprint
from app.models.selector import Selector
from app.models.user import User
from app.models.analytics import AnalyticsMetric

# Import PlatformTemplate from the legacy models.py file
# This is a workaround since PlatformTemplate is still in app/models.py
# instead of app/models/template.py
import sys
import os
import importlib.util

# Get the path to models.py
models_py_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models.py")
if os.path.exists(models_py_path):
    spec = importlib.util.spec_from_file_location("app.models_legacy", models_py_path)
    if spec and spec.loader:
        models_legacy = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(models_legacy)
        PlatformTemplate = models_legacy.PlatformTemplate
    else:
        # Fallback: define PlatformTemplate here if import fails
        from sqlalchemy import Column, String, Float, DateTime, JSON, UUID, Boolean
        import uuid
        from datetime import datetime
        
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
else:
    # Fallback definition
    from sqlalchemy import Column, String, Float, DateTime, JSON, UUID, Boolean
    import uuid
    from datetime import datetime
    
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

__all__ = ["Base", "Site", "Job", "Blueprint", "Selector", "User", "AnalyticsMetric", "PlatformTemplate"]

