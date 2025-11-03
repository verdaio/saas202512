"""
Tenant schemas
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class TenantBase(BaseModel):
    business_name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    phone: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = Field(None, max_length=2)
    zip_code: Optional[str] = None
    timezone: str = "America/New_York"
    currency: str = "USD"


class TenantCreate(TenantBase):
    subdomain: str = Field(..., min_length=3, max_length=63, pattern="^[a-z0-9-]+$")


class TenantUpdate(BaseModel):
    business_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    timezone: Optional[str] = None


class TenantResponse(TenantBase):
    id: UUID
    subdomain: str
    status: str
    is_active: bool
    plan_type: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
