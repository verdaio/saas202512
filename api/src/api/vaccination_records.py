"""
Vaccination record API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import uuid

from ..db.base import get_db
from ..core.dependencies import get_current_user, get_current_tenant, require_staff_or_admin
from ..models.user import User
from ..models.tenant import Tenant
from ..models.vaccination_record import VaccinationRecord
from ..models.pet import Pet
from ..schemas.vaccination_record import VaccinationRecordCreate, VaccinationRecordUpdate, VaccinationRecordResponse

router = APIRouter()


@router.post("/", response_model=VaccinationRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_vaccination_record(
    vaccination_data: VaccinationRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_admin),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Create new vaccination record (staff/admin/owner)
    """
    # Verify pet exists and belongs to tenant
    pet = db.query(Pet).filter(
        Pet.id == vaccination_data.pet_id,
        Pet.tenant_id == current_tenant.id
    ).first()

    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pet not found"
        )

    vaccination = VaccinationRecord(
        id=uuid.uuid4(),
        tenant_id=current_tenant.id,
        **vaccination_data.model_dump()
    )

    # Auto-update status based on expiry date
    vaccination.update_status()

    db.add(vaccination)
    db.commit()
    db.refresh(vaccination)

    # Update pet's vaccination status
    pet.vaccination_status = vaccination.status
    pet.vaccination_expires_at = vaccination.expiry_date
    db.commit()

    return vaccination


@router.get("/", response_model=List[VaccinationRecordResponse])
async def list_vaccination_records(
    skip: int = 0,
    limit: int = 100,
    pet_id: UUID = None,
    type: str = None,
    status: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    List vaccination records for current tenant
    """
    query = db.query(VaccinationRecord).filter(VaccinationRecord.tenant_id == current_tenant.id)

    if pet_id:
        query = query.filter(VaccinationRecord.pet_id == pet_id)

    if type:
        query = query.filter(VaccinationRecord.type == type)

    if status:
        query = query.filter(VaccinationRecord.status == status)

    records = query.order_by(VaccinationRecord.expiry_date.desc()).offset(skip).limit(limit).all()
    return records


@router.get("/{record_id}", response_model=VaccinationRecordResponse)
async def get_vaccination_record(
    record_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Get vaccination record by ID
    """
    record = db.query(VaccinationRecord).filter(
        VaccinationRecord.id == record_id,
        VaccinationRecord.tenant_id == current_tenant.id
    ).first()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vaccination record not found"
        )

    return record


@router.put("/{record_id}", response_model=VaccinationRecordResponse)
async def update_vaccination_record(
    record_id: UUID,
    vaccination_data: VaccinationRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_admin),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Update vaccination record (staff/admin/owner)
    """
    record = db.query(VaccinationRecord).filter(
        VaccinationRecord.id == record_id,
        VaccinationRecord.tenant_id == current_tenant.id
    ).first()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vaccination record not found"
        )

    # Update fields
    for field, value in vaccination_data.model_dump(exclude_unset=True).items():
        setattr(record, field, value)

    # Update status if expiry date changed
    if vaccination_data.expiry_date:
        record.update_status()

    db.commit()
    db.refresh(record)

    # Update pet's vaccination status if this is the most recent record
    pet = db.query(Pet).filter(Pet.id == record.pet_id).first()
    if pet:
        latest_record = db.query(VaccinationRecord).filter(
            VaccinationRecord.pet_id == pet.id
        ).order_by(VaccinationRecord.expiry_date.desc()).first()

        if latest_record:
            pet.vaccination_status = latest_record.status
            pet.vaccination_expires_at = latest_record.expiry_date
            db.commit()

    return record


@router.post("/{record_id}/verify", response_model=VaccinationRecordResponse)
async def verify_vaccination_record(
    record_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_admin),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Verify vaccination record (staff/admin/owner)
    """
    record = db.query(VaccinationRecord).filter(
        VaccinationRecord.id == record_id,
        VaccinationRecord.tenant_id == current_tenant.id
    ).first()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vaccination record not found"
        )

    from datetime import datetime
    record.verified_by_staff = True
    record.verified_at = datetime.utcnow()
    record.verified_by_user_id = current_user.id

    db.commit()
    db.refresh(record)

    return record


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vaccination_record(
    record_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_admin),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Delete vaccination record (staff/admin/owner)
    """
    record = db.query(VaccinationRecord).filter(
        VaccinationRecord.id == record_id,
        VaccinationRecord.tenant_id == current_tenant.id
    ).first()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vaccination record not found"
        )

    from datetime import datetime
    record.deleted_at = datetime.utcnow()
    db.commit()

    return None
