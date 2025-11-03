"""
Vaccination record schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from uuid import UUID


class VaccinationRecordBase(BaseModel):
    type: str  # rabies, distemper, parvo, bordetella, leukemia, lyme, dhpp, fvrcp, other
    name: Optional[str] = None
    administered_date: date
    expiry_date: date
    veterinarian_name: Optional[str] = None
    veterinarian_clinic: Optional[str] = None
    veterinarian_phone: Optional[str] = None
    license_number: Optional[str] = None


class VaccinationRecordCreate(VaccinationRecordBase):
    pet_id: UUID
    certificate_url: Optional[str] = None
    lot_number: Optional[str] = None
    manufacturer: Optional[str] = None
    notes: Optional[str] = None


class VaccinationRecordUpdate(BaseModel):
    expiry_date: Optional[date] = None
    status: Optional[str] = None
    verified_by_staff: Optional[bool] = None
    certificate_url: Optional[str] = None


class VaccinationRecordResponse(VaccinationRecordBase):
    id: UUID
    tenant_id: UUID
    pet_id: UUID
    status: str
    certificate_url: Optional[str] = None
    lot_number: Optional[str] = None
    manufacturer: Optional[str] = None
    verified_by_staff: bool
    verified_at: Optional[datetime] = None
    verified_by_user_id: Optional[UUID] = None
    reminder_sent_30d: bool
    reminder_sent_14d: bool
    reminder_sent_7d: bool
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
