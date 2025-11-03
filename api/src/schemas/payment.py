"""
Payment schemas
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict
from datetime import datetime
from uuid import UUID


class PaymentBase(BaseModel):
    type: str  # deposit, full_payment, tip, package, gift_card, no_show_fee, refund
    method: str  # card, cash, check, other
    amount: int  # In cents
    tip_amount: int = 0
    description: Optional[str] = None


class PaymentCreate(PaymentBase):
    owner_id: UUID
    appointment_id: Optional[UUID] = None
    package_id: Optional[UUID] = None
    stripe_payment_method_id: Optional[str] = None
    receipt_email: Optional[EmailStr] = None


class PaymentUpdate(BaseModel):
    status: Optional[str] = None
    refund_amount: Optional[int] = None
    stripe_refund_id: Optional[str] = None


class PaymentResponse(PaymentBase):
    id: UUID
    tenant_id: UUID
    owner_id: UUID
    appointment_id: Optional[UUID] = None
    package_id: Optional[UUID] = None
    status: str
    refund_amount: int
    net_amount: int
    stripe_payment_intent_id: Optional[str] = None
    stripe_charge_id: Optional[str] = None
    stripe_customer_id: Optional[str] = None
    card_last4: Optional[str] = None
    card_brand: Optional[str] = None
    card_exp_month: Optional[int] = None
    card_exp_year: Optional[int] = None
    failure_code: Optional[str] = None
    failure_message: Optional[str] = None
    processed_at: Optional[datetime] = None
    succeeded_at: Optional[datetime] = None
    receipt_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
