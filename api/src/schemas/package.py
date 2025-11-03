"""
Package schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class PackageBase(BaseModel):
    name: str
    type: str  # punch_card, class_credits, membership, gift_card
    description: Optional[str] = None
    price_paid: int  # In cents
    value: Optional[int] = None
    total_credits: int
    unlimited: bool = False
    never_expires: bool = False


class PackageCreate(PackageBase):
    owner_id: UUID
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    gift_code: Optional[str] = None
    recipient_name: Optional[str] = None
    recipient_email: Optional[str] = None
    message: Optional[str] = None


class PackageUpdate(BaseModel):
    status: Optional[str] = None
    remaining_credits: Optional[int] = None
    valid_until: Optional[datetime] = None


class PackageResponse(PackageBase):
    id: UUID
    tenant_id: UUID
    owner_id: UUID
    remaining_credits: int
    status: str
    payment_id: Optional[UUID] = None
    stripe_payment_intent_id: Optional[str] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    first_used_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    gift_code: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
