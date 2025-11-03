"""
Staff API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import uuid

from ..db.base import get_db
from ..core.dependencies import get_current_user, get_current_tenant, require_owner
from ..models.user import User
from ..models.tenant import Tenant
from ..models.staff import Staff
from ..schemas.staff import StaffCreate, StaffUpdate, StaffResponse

router = APIRouter()


@router.post("/", response_model=StaffResponse, status_code=status.HTTP_201_CREATED)
async def create_staff(
    staff_data: StaffCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_owner),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Create new staff member (owner only)
    """
    staff = Staff(
        id=uuid.uuid4(),
        tenant_id=current_tenant.id,
        **staff_data.model_dump()
    )

    db.add(staff)
    db.commit()
    db.refresh(staff)

    return staff


@router.get("/", response_model=List[StaffResponse])
async def list_staff(
    skip: int = 0,
    limit: int = 100,
    is_active: bool = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    List all staff members for current tenant
    """
    query = db.query(Staff).filter(Staff.tenant_id == current_tenant.id)

    if is_active is not None:
        query = query.filter(Staff.is_active == is_active)

    staff_list = query.offset(skip).limit(limit).all()
    return staff_list


@router.get("/{staff_id}", response_model=StaffResponse)
async def get_staff(
    staff_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Get staff member by ID
    """
    staff = db.query(Staff).filter(
        Staff.id == staff_id,
        Staff.tenant_id == current_tenant.id
    ).first()

    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff member not found"
        )

    return staff


@router.put("/{staff_id}", response_model=StaffResponse)
async def update_staff(
    staff_id: UUID,
    staff_data: StaffUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_owner),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Update staff member (owner only)
    """
    staff = db.query(Staff).filter(
        Staff.id == staff_id,
        Staff.tenant_id == current_tenant.id
    ).first()

    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff member not found"
        )

    # Update fields
    for field, value in staff_data.model_dump(exclude_unset=True).items():
        setattr(staff, field, value)

    db.commit()
    db.refresh(staff)

    return staff


@router.delete("/{staff_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_staff(
    staff_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_owner),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Delete (deactivate) staff member (owner only)
    """
    staff = db.query(Staff).filter(
        Staff.id == staff_id,
        Staff.tenant_id == current_tenant.id
    ).first()

    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff member not found"
        )

    staff.is_active = False
    db.commit()

    return None
