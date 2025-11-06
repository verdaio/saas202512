"""
Pet API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import uuid

from ..db.base import get_db
from ..core.dependencies import get_current_user, get_current_tenant, get_public_tenant, require_staff_or_admin
from ..models.user import User
from ..models.tenant import Tenant
from ..models.pet import Pet
from ..models.owner import Owner
from ..schemas.pet import PetCreate, PetUpdate, PetResponse

router = APIRouter()


@router.post("/", response_model=PetResponse, status_code=status.HTTP_201_CREATED)
async def create_pet(
    pet_data: PetCreate,
    db: Session = Depends(get_db),
    current_tenant: Tenant = Depends(get_public_tenant)
):
    """
    Create new pet (public endpoint for booking widget)
    """
    # Verify owner exists and belongs to tenant
    owner = db.query(Owner).filter(
        Owner.id == pet_data.owner_id,
        Owner.tenant_id == current_tenant.id
    ).first()

    if not owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Owner not found"
        )

    pet = Pet(
        id=uuid.uuid4(),
        tenant_id=current_tenant.id,
        **pet_data.model_dump()
    )

    db.add(pet)
    db.commit()
    db.refresh(pet)

    return pet


@router.get("/", response_model=List[PetResponse])
async def list_pets(
    skip: int = 0,
    limit: int = 100,
    owner_id: UUID = None,
    species: str = None,
    is_active: bool = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    List pets for current tenant
    """
    query = db.query(Pet).filter(Pet.tenant_id == current_tenant.id)

    if owner_id:
        query = query.filter(Pet.owner_id == owner_id)

    if species:
        query = query.filter(Pet.species == species)

    if is_active is not None:
        query = query.filter(Pet.is_active == is_active)

    pets = query.offset(skip).limit(limit).all()
    return pets


@router.get("/{pet_id}", response_model=PetResponse)
async def get_pet(
    pet_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Get pet by ID
    """
    pet = db.query(Pet).filter(
        Pet.id == pet_id,
        Pet.tenant_id == current_tenant.id
    ).first()

    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pet not found"
        )

    return pet


@router.put("/{pet_id}", response_model=PetResponse)
async def update_pet(
    pet_id: UUID,
    pet_data: PetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_admin),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Update pet (staff/admin/owner)
    """
    pet = db.query(Pet).filter(
        Pet.id == pet_id,
        Pet.tenant_id == current_tenant.id
    ).first()

    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pet not found"
        )

    # Update fields
    for field, value in pet_data.model_dump(exclude_unset=True).items():
        setattr(pet, field, value)

    db.commit()
    db.refresh(pet)

    return pet


@router.delete("/{pet_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pet(
    pet_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_admin),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Delete (deactivate) pet (staff/admin/owner)
    """
    pet = db.query(Pet).filter(
        Pet.id == pet_id,
        Pet.tenant_id == current_tenant.id
    ).first()

    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pet not found"
        )

    pet.is_active = False
    db.commit()

    return None
