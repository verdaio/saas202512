"""
Resource schemas
"""
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime
from uuid import UUID


class ResourceBase(BaseModel):
    name: str
    type: str  # table, van, room, cage, other
    description: Optional[str] = None
    capacity: int = 1
    is_bookable: bool = True
    travel_time_minutes: int = 0


class ResourceCreate(ResourceBase):
    schedule: Optional[Dict] = None
    location: Optional[str] = None
    color: Optional[str] = None
    display_order: int = 0


class ResourceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    capacity: Optional[int] = None
    is_active: Optional[bool] = None
    is_bookable: Optional[bool] = None
    schedule: Optional[Dict] = None


class ResourceResponse(ResourceBase):
    id: UUID
    tenant_id: UUID
    is_active: bool
    schedule: Optional[Dict] = None
    location: Optional[str] = None
    color: Optional[str] = None
    display_order: int
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
