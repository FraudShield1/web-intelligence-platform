"""Tests for Sites endpoints"""
import pytest
from httpx import AsyncClient
from app.main import app
from app.database import get_db
from app.models import Site
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

@pytest.fixture
async def client():
    """Async client for testing"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_create_site(client):
    """Test creating a site"""
    response = await client.post(
        "/api/v1/sites",
        json={"domain": "test-example.com", "business_value_score": 0.85}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["domain"] == "test-example.com"
    assert data["status"] == "pending"

@pytest.mark.asyncio
async def test_list_sites(client):
    """Test listing sites"""
    response = await client.get("/api/v1/sites")
    assert response.status_code == 200
    data = response.json()
    assert "sites" in data
    assert "total" in data
    assert "limit" in data

@pytest.mark.asyncio
async def test_list_sites_with_filters(client):
    """Test listing sites with filters"""
    response = await client.get("/api/v1/sites?status=ready&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert data["limit"] == 10

@pytest.mark.asyncio
async def test_get_nonexistent_site(client):
    """Test getting non-existent site"""
    fake_id = str(uuid.uuid4())
    response = await client.get(f"/api/v1/sites/{fake_id}")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_health_check(client):
    """Test health endpoint"""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

@pytest.mark.asyncio
async def test_api_root(client):
    """Test API root endpoint"""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data

