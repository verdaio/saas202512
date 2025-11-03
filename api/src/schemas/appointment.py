"""
Appointment schemas
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class AppointmentBase(BaseModel):
    owner_id: UUID
    pet_ids: List[UUID]
    service_id: UUID
    staff_id: Optional[UUID] = None
    resource_id: Optional[UUID] = None
    scheduled_start: datetime
    scheduled_end: datetime
    customer_notes: Optional[str] = None


class AppointmentCreate(AppointmentBase):
    pass


class AppointmentUpdate(BaseModel):
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    staff_id: Optional[UUID] = None
    status: Optional[str] = None


class AppointmentResponse(AppointmentBase):
    id: UUID
    tenant_id: UUID
    status: str
    source: str
    deposit_required: Optional[int] = None
    deposit_paid: int
    total_amount: int
    amount_paid: int
    vaccination_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True
