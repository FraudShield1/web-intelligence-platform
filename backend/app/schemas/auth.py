"""Auth schemas"""
from pydantic import BaseModel


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str
    expires_in: int

