"""Tests for Jobs endpoints"""
import pytest
from httpx import AsyncClient
from app.main import app
import uuid

@pytest.fixture
async def client():
    """Async client for testing"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_list_jobs(client):
    """Test listing jobs"""
    response = await client.get("/api/v1/jobs")
    assert response.status_code == 200
    data = response.json()
    assert "jobs" in data
    assert "total" in data

@pytest.mark.asyncio
async def test_list_jobs_filtered(client):
    """Test listing jobs with filters"""
    response = await client.get("/api/v1/jobs?status=running&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 0

@pytest.mark.asyncio
async def test_get_nonexistent_job(client):
    """Test getting non-existent job"""
    fake_id = str(uuid.uuid4())
    response = await client.get(f"/api/v1/jobs/{fake_id}")
    assert response.status_code == 404

