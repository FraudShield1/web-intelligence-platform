"""Vercel serverless entry point for FastAPI"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.main import app

# Vercel expects a variable named 'app' or handler
handler = app

