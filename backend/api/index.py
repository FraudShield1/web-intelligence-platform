"""Main API entry point for Vercel serverless deployment"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os

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
        "message": "Web Intelligence Platform API",
        "status": "online",
        "version": "1.0.0"
    }

@app.get("/api/health")
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Web Intelligence Platform"
    }

@app.get("/api")
async def api_root():
    return {
        "message": "Web Intelligence Platform API",
        "endpoints": {
            "health": "/api/health",
            "auth": "/api/auth/*",
            "sites": "/api/sites",
            "jobs": "/api/jobs",
            "blueprints": "/api/blueprints",
            "analytics": "/api/analytics"
        },
        "docs": "/docs"
    }
