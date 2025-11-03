"""
Service API endpoints
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
from ..models.service import Service
from ..schemas.service import ServiceCreate, ServiceUpdate, ServiceResponse

router = APIRouter()


@router.post("/", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
async def create_service(
    service_data: ServiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_owner),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Create new service (owner only)
    """
    service = Service(
        id=uuid.uuid4(),
        tenant_id=current_tenant.id,
        **service_data.model_dump()
    )

    db.add(service)
    db.commit()
    db.refresh(service)

    return service


@router.get("/", response_model=List[ServiceResponse])
async def list_services(
    skip: int = 0,
    limit: int = 100,
    category: str = None,
    is_active: bool = None,
    is_bookable_online: bool = None,
    db: Session = Depends(get_db),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    List services for current tenant (public endpoint for booking widget)
    """
    query = db.query(Service).filter(Service.tenant_id == current_tenant.id)

    if category:
        query = query.filter(Service.category == category)

    if is_active is not None:
        query = query.filter(Service.is_active == is_active)

    if is_bookable_online is not None:
        query = query.filter(Service.is_bookable_online == is_bookable_online)

    services = query.order_by(Service.display_order, Service.name).offset(skip).limit(limit).all()
    return services


@router.get("/{service_id}", response_model=ServiceResponse)
async def get_service(
    service_id: UUID,
    db: Session = Depends(get_db),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Get service by ID (public endpoint for booking widget)
    """
    service = db.query(Service).filter(
        Service.id == service_id,
        Service.tenant_id == current_tenant.id
    ).first()

    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )

    return service


@router.put("/{service_id}", response_model=ServiceResponse)
async def update_service(
    service_id: UUID,
    service_data: ServiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_owner),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Update service (owner only)
    """
    service = db.query(Service).filter(
        Service.id == service_id,
        Service.tenant_id == current_tenant.id
    ).first()

    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )

    # Update fields
    for field, value in service_data.model_dump(exclude_unset=True).items():
        setattr(service, field, value)

    db.commit()
    db.refresh(service)

    return service


@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service(
    service_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_owner),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Delete (deactivate) service (owner only)
    """
    service = db.query(Service).filter(
        Service.id == service_id,
        Service.tenant_id == current_tenant.id
    ).first()

    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )

    service.is_active = False
    db.commit()

    return None
