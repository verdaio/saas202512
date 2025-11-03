"""
Authentication schemas
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data"""
    sub: str  # User ID
    tenant_id: str
    email: str
    role: str
    exp: Optional[datetime] = None
    iat: Optional[datetime] = None


class LoginRequest(BaseModel):
    """Login request schema"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    subdomain: Optional[str] = None  # Tenant subdomain


class SignupRequest(BaseModel):
    """Tenant signup request"""
    business_name: str = Field(..., min_length=2, max_length=255)
    subdomain: str = Field(..., min_length=3, max_length=63, pattern="^[a-z0-9-]+$")
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = None


class PasswordResetRequest(BaseModel):
    """Password reset request"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation"""
    token: str
    new_password: str = Field(..., min_length=8)


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str
