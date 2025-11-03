"""
Package API endpoints (punch cards, class credits, memberships)
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
from ..models.package import Package, PackageStatus
from ..models.owner import Owner
from ..schemas.package import PackageCreate, PackageUpdate, PackageResponse

router = APIRouter()


@router.post("/", response_model=PackageResponse, status_code=status.HTTP_201_CREATED)
async def create_package(
    package_data: PackageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_admin),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Create new package (staff/admin/owner)
    """
    # Verify owner exists
    owner = db.query(Owner).filter(
        Owner.id == package_data.owner_id,
        Owner.tenant_id == current_tenant.id
    ).first()

    if not owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Owner not found"
        )

    package = Package(
        id=uuid.uuid4(),
        tenant_id=current_tenant.id,
        remaining_credits=package_data.total_credits,
        status=PackageStatus.ACTIVE,
        **package_data.model_dump()
    )

    db.add(package)
    db.commit()
    db.refresh(package)

    return package


@router.get("/", response_model=List[PackageResponse])
async def list_packages(
    skip: int = 0,
    limit: int = 100,
    owner_id: UUID = None,
    type: str = None,
    status: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    List packages for current tenant
    """
    query = db.query(Package).filter(Package.tenant_id == current_tenant.id)

    if owner_id:
        query = query.filter(Package.owner_id == owner_id)

    if type:
        query = query.filter(Package.type == type)

    if status:
        query = query.filter(Package.status == status)

    packages = query.order_by(Package.created_at.desc()).offset(skip).limit(limit).all()
    return packages


@router.get("/{package_id}", response_model=PackageResponse)
async def get_package(
    package_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Get package by ID
    """
    package = db.query(Package).filter(
        Package.id == package_id,
        Package.tenant_id == current_tenant.id
    ).first()

    if not package:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Package not found"
        )

    return package


@router.put("/{package_id}", response_model=PackageResponse)
async def update_package(
    package_id: UUID,
    package_data: PackageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_admin),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Update package (staff/admin/owner)
    """
    package = db.query(Package).filter(
        Package.id == package_id,
        Package.tenant_id == current_tenant.id
    ).first()

    if not package:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Package not found"
        )

    # Update fields
    for field, value in package_data.model_dump(exclude_unset=True).items():
        setattr(package, field, value)

    db.commit()
    db.refresh(package)

    return package


@router.post("/{package_id}/use", response_model=PackageResponse)
async def use_package_credit(
    package_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_admin),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Use one credit from package (staff/admin/owner)
    """
    package = db.query(Package).filter(
        Package.id == package_id,
        Package.tenant_id == current_tenant.id
    ).first()

    if not package:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Package not found"
        )

    if not package.is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Package is not valid (expired or exhausted)"
        )

    success = package.use_credit()

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No credits remaining"
        )

    db.commit()
    db.refresh(package)

    return package


@router.post("/{package_id}/cancel", response_model=PackageResponse)
async def cancel_package(
    package_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_admin),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Cancel package (staff/admin/owner)
    """
    package = db.query(Package).filter(
        Package.id == package_id,
        Package.tenant_id == current_tenant.id
    ).first()

    if not package:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Package not found"
        )

    from datetime import datetime
    package.status = PackageStatus.CANCELLED
    package.cancelled_at = datetime.utcnow()

    db.commit()
    db.refresh(package)

    return package
