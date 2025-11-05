"""Analytics schemas"""
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID


class AnalyticsMetricResponse(BaseModel):
    """Analytics metric response"""
    metric_id: UUID
    site_id: Optional[UUID]
    discovery_time_seconds: Optional[int]
    num_categories_found: Optional[int]
    num_endpoints_found: Optional[int]
    selector_failure_rate: Optional[float]
    fetch_cost_usd: Optional[float]
    items_extracted: Optional[int]
    method: Optional[str]
    
    class Config:
        from_attributes = True


class DashboardMetricsResponse(BaseModel):
    """Dashboard overview metrics"""
    total_sites: int
    active_jobs: int
    total_blueprints: int
    avg_discovery_time: Optional[float]
    success_rate: Optional[float]


class SiteMetricsResponse(BaseModel):
    """Site-specific metrics"""
    site_id: UUID
    domain: str
    total_jobs: int
    successful_jobs: int
    failed_jobs: int
    avg_discovery_time: Optional[float]
    total_categories: Optional[int]
    total_endpoints: Optional[int]
    last_run: Optional[str]


class MethodPerformanceResponse(BaseModel):
    """Method performance comparison"""
    method: str
    total_runs: int
    success_rate: float
    avg_discovery_time: float
    avg_categories_found: float
    avg_cost_usd: float

