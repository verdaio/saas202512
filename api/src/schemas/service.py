"""
Service schemas
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class ServiceBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    price: int  # In cents
    deposit_amount: Optional[int] = None
    deposit_percentage: Optional[int] = None
    duration_minutes: int
    setup_buffer_minutes: int = 0
    cleanup_buffer_minutes: int = 0
    max_pets_per_session: int = 1
    requires_vaccination: bool = True
    vaccination_types_required: Optional[List[str]] = None
    requires_table: bool = False
    requires_van: bool = False
    requires_room: bool = False
    is_bookable_online: bool = True
    staff_assignment: str = "any"


class ServiceCreate(ServiceBase):
    color: Optional[str] = None
    icon: Optional[str] = None
    display_order: int = 0


class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    duration_minutes: Optional[int] = None
    is_active: Optional[bool] = None
    is_bookable_online: Optional[bool] = None


class ServiceResponse(ServiceBase):
    id: UUID
    tenant_id: UUID
    is_active: bool
    color: Optional[str] = None
    icon: Optional[str] = None
    display_order: int
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
