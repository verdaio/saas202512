"""
Pet schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from uuid import UUID


class PetBase(BaseModel):
    name: str
    species: str
    breed: Optional[str] = None
    gender: Optional[str] = None
    color: Optional[str] = None
    weight: Optional[int] = None
    date_of_birth: Optional[date] = None
    age_years: Optional[int] = None
    age_months: Optional[int] = None
    microchip_number: Optional[str] = None
    license_number: Optional[str] = None
    allergies: Optional[str] = None
    medical_conditions: Optional[str] = None
    medications: Optional[str] = None
    veterinarian_name: Optional[str] = None
    veterinarian_phone: Optional[str] = None
    temperament: Optional[str] = None
    special_instructions: Optional[str] = None
    is_aggressive: bool = False
    needs_muzzle: bool = False
    vaccination_status: str = "unknown"
    vaccination_expires_at: Optional[date] = None


class PetCreate(PetBase):
    owner_id: UUID


class PetUpdate(BaseModel):
    name: Optional[str] = None
    breed: Optional[str] = None
    weight: Optional[int] = None
    allergies: Optional[str] = None
    medical_conditions: Optional[str] = None
    temperament: Optional[str] = None
    special_instructions: Optional[str] = None
    vaccination_status: Optional[str] = None
    vaccination_expires_at: Optional[date] = None


class PetResponse(PetBase):
    id: UUID
    tenant_id: UUID
    owner_id: UUID
    is_active: bool
    is_deceased: bool
    photo_url: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
