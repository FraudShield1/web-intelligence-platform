"""Vercel serverless entry point - Simple working version"""
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os

# Create a simple FastAPI app
app = FastAPI(title="Web Intelligence Platform API")

# CORS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", '["*"]')
if isinstance(CORS_ORIGINS, str):
    import json
    try:
        CORS_ORIGINS = json.loads(CORS_ORIGINS)
    except:
        CORS_ORIGINS = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "name": "Web Intelligence Platform API",
        "version": "1.0.0",
        "status": "online",
        "message": "API is running on Vercel serverless"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "web-intelligence-platform",
        "platform": "vercel-serverless"
    }

@app.get("/api/health")
async def api_health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "web-intelligence-platform", 
        "platform": "vercel-serverless"
    }

@app.get("/api")
async def api_root():
    return {
        "message": "Web Intelligence Platform API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health",
            "metrics": "/api/v1/analytics/dashboard",
            "sites": "/api/v1/sites",
            "jobs": "/api/v1/jobs",
            "blueprints": "/api/v1/blueprints"
        },
        "note": "Full API features available via local backend or dedicated server deployment"
    }

# Mock endpoints for dashboard metrics
@app.get("/api/v1/analytics/dashboard")
async def dashboard_metrics():
    """Mock dashboard metrics for frontend"""
    return {
        "total_sites": 0,
        "active_jobs": 0,
        "completed_jobs": 0,
        "success_rate": 0,
        "avg_processing_time": 0,
        "total_blueprints": 0,
        "note": "Connect to local backend or dedicated server for real-time data"
    }

@app.get("/api/v1/sites")
async def list_sites():
    """Mock sites endpoint"""
    return {
        "sites": [],
        "total": 0,
        "page": 1,
        "note": "Run local backend for full site management"
    }

@app.get("/api/v1/jobs")
async def list_jobs():
    """Mock jobs endpoint"""
    return {
        "jobs": [],
        "total": 0,
        "page": 1,
        "note": "Run local backend for job monitoring"
    }

@app.get("/api/v1/blueprints")
async def list_blueprints():
    """Mock blueprints endpoint"""
    return {
        "blueprints": [],
        "total": 0,
        "page": 1,
        "note": "Run local backend for blueprint access"
    }
