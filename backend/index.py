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
            "root": "/"
        },
        "note": "Full API features available via local backend or dedicated server deployment"
    }
