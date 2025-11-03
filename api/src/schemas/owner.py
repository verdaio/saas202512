"""
Owner schemas
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID


class OwnerBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    sms_opted_in: bool = True
    email_opted_in: bool = True
    preferred_contact_method: str = "sms"


class OwnerCreate(OwnerBase):
    pass


class OwnerUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    address_line1: Optional[str] = None
    sms_opted_in: Optional[bool] = None
    email_opted_in: Optional[bool] = None


class OwnerResponse(OwnerBase):
    id: UUID
    tenant_id: UUID
    user_id: Optional[UUID] = None
    has_payment_method: bool
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
