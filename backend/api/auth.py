"""Serverless auth endpoint for Vercel"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os

# Import from parent app
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.models import User
from app.security import verify_password, create_access_token

app = FastAPI()

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@app.post("/api/auth/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login endpoint"""
    async with async_session() as db:
        stmt = select(User).where(User.username == form_data.username)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user or not verify_password(form_data.password, user.password_hash):
            raise HTTPException(status_code=400, detail="Incorrect username or password")
        
        token = create_access_token(str(user.user_id), user.role)
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": 3600
        }

# Export for Vercel
handler = app

