"""
Staff schemas
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict
from datetime import datetime
from uuid import UUID


class StaffBase(BaseModel):
    first_name: str
    last_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    title: Optional[str] = None
    bio: Optional[str] = None
    skills: Optional[List[str]] = None
    is_available: bool = True
    can_groom: bool = False
    can_train: bool = False
    can_bathe: bool = False


class StaffCreate(StaffBase):
    schedule: Optional[Dict] = None
    commission_rate: Optional[int] = None
    hourly_rate: Optional[int] = None


class StaffUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    title: Optional[str] = None
    bio: Optional[str] = None
    is_available: Optional[bool] = None
    schedule: Optional[Dict] = None


class StaffResponse(StaffBase):
    id: UUID
    tenant_id: UUID
    user_id: Optional[UUID] = None
    is_active: bool
    photo_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
