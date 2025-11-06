"""
Owner API endpoints
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
from ..models.owner import Owner
from ..schemas.owner import OwnerCreate, OwnerUpdate, OwnerResponse

router = APIRouter()


@router.post("/", response_model=OwnerResponse, status_code=status.HTTP_201_CREATED)
async def create_owner(
    owner_data: OwnerCreate,
    db: Session = Depends(get_db),
    current_tenant: Tenant = Depends(get_public_tenant)
):
    """
    Create new pet owner (public endpoint for booking widget)
    """
    # Check if email already exists for this tenant
    existing = db.query(Owner).filter(
        Owner.tenant_id == current_tenant.id,
        Owner.email == owner_data.email
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Owner with this email already exists"
        )

    owner = Owner(
        id=uuid.uuid4(),
        tenant_id=current_tenant.id,
        **owner_data.model_dump()
    )

    db.add(owner)
    db.commit()
    db.refresh(owner)

    return owner


@router.get("/", response_model=List[OwnerResponse])
async def list_owners(
    skip: int = 0,
    limit: int = 100,
    search: str = None,
    is_active: bool = None,
    db: Session = Depends(get_db),
    current_tenant: Tenant = Depends(get_public_tenant)
):
    """
    List all pet owners for current tenant (public endpoint for booking widget search)
    """
    query = db.query(Owner).filter(Owner.tenant_id == current_tenant.id)

    if is_active is not None:
        query = query.filter(Owner.is_active == is_active)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Owner.first_name.ilike(search_pattern)) |
            (Owner.last_name.ilike(search_pattern)) |
            (Owner.email.ilike(search_pattern)) |
            (Owner.phone.ilike(search_pattern))
        )

    owners = query.offset(skip).limit(limit).all()
    return owners


@router.get("/{owner_id}", response_model=OwnerResponse)
async def get_owner(
    owner_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Get owner by ID
    """
    owner = db.query(Owner).filter(
        Owner.id == owner_id,
        Owner.tenant_id == current_tenant.id
    ).first()

    if not owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Owner not found"
        )

    return owner


@router.put("/{owner_id}", response_model=OwnerResponse)
async def update_owner(
    owner_id: UUID,
    owner_data: OwnerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_admin),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Update owner (staff/admin/owner)
    """
    owner = db.query(Owner).filter(
        Owner.id == owner_id,
        Owner.tenant_id == current_tenant.id
    ).first()

    if not owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Owner not found"
        )

    # Update fields
    for field, value in owner_data.model_dump(exclude_unset=True).items():
        setattr(owner, field, value)

    db.commit()
    db.refresh(owner)

    return owner


@router.delete("/{owner_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_owner(
    owner_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_admin),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Delete (deactivate) owner (staff/admin/owner)
    """
    owner = db.query(Owner).filter(
        Owner.id == owner_id,
        Owner.tenant_id == current_tenant.id
    ).first()

    if not owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Owner not found"
        )

    owner.is_active = False
    db.commit()

    return None
