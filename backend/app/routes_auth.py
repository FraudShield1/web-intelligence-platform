"""Authentication routes: login to obtain JWT"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import User
from app.security import verify_password, create_access_token, hash_password
from app.schemas import TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.username == form_data.username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user or not user.password_hash or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    token = create_access_token(str(user.user_id), user.role)
    return TokenResponse(access_token=token, token_type="bearer", expires_in=60 * 60)

@router.post("/bootstrap", response_model=TokenResponse)
async def bootstrap_admin(db: AsyncSession = Depends(get_db)):
    """Create a default admin if none exists (one-time)."""
    stmt = select(User).limit(1)
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    admin = User(username="admin", email="admin@example.com", role="admin", password_hash=hash_password("admin"))
    db.add(admin)
    await db.commit()
    token = create_access_token(str(admin.user_id), admin.role)
    return TokenResponse(access_token=token, token_type="bearer", expires_in=60 * 60)
