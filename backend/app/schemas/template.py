"""Template schemas"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from uuid import UUID
from datetime import datetime


class TemplateCreate(BaseModel):
    """Schema for creating a template"""
    platform_name: str = Field(..., description="Platform name (e.g., 'shopify', 'magento')")
    platform_variant: Optional[str] = Field(None, description="Variant (e.g., '2.x', '1.x')")
    category_selectors: Optional[Dict[str, Any]] = Field(None, description="Category navigation selectors")
    product_list_selectors: Optional[Dict[str, Any]] = Field(None, description="Product listing page selectors")
    api_patterns: Optional[Dict[str, Any]] = Field(None, description="API endpoint patterns")
    render_hints: Optional[Dict[str, Any]] = Field(None, description="Rendering requirements")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Template confidence score")
    active: bool = Field(True, description="Whether template is active")
    match_patterns: Optional[Dict[str, Any]] = Field(None, description="Patterns to detect this template")


class TemplateUpdate(BaseModel):
    """Schema for updating a template"""
    platform_name: Optional[str] = None
    platform_variant: Optional[str] = None
    category_selectors: Optional[Dict[str, Any]] = None
    product_list_selectors: Optional[Dict[str, Any]] = None
    api_patterns: Optional[Dict[str, Any]] = None
    render_hints: Optional[Dict[str, Any]] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    active: Optional[bool] = None
    match_patterns: Optional[Dict[str, Any]] = None


class TemplateResponse(BaseModel):
    """Schema for template response"""
    template_id: UUID
    platform_name: str
    platform_variant: Optional[str]
    category_selectors: Optional[Dict[str, Any]]
    product_list_selectors: Optional[Dict[str, Any]]
    api_patterns: Optional[Dict[str, Any]]
    render_hints: Optional[Dict[str, Any]]
    confidence: Optional[float]
    active: bool
    match_patterns: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TemplateListResponse(BaseModel):
    """Schema for template list response"""
    templates: List[TemplateResponse]
    total: int

