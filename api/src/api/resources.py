"""
Resource API endpoints
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
from ..models.resource import Resource
from ..schemas.resource import ResourceCreate, ResourceUpdate, ResourceResponse

router = APIRouter()


@router.post("/", response_model=ResourceResponse, status_code=status.HTTP_201_CREATED)
async def create_resource(
    resource_data: ResourceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_owner),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Create new resource (owner only)
    """
    resource = Resource(
        id=uuid.uuid4(),
        tenant_id=current_tenant.id,
        **resource_data.model_dump()
    )

    db.add(resource)
    db.commit()
    db.refresh(resource)

    return resource


@router.get("/", response_model=List[ResourceResponse])
async def list_resources(
    skip: int = 0,
    limit: int = 100,
    type: str = None,
    is_active: bool = None,
    is_bookable: bool = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    List resources for current tenant
    """
    query = db.query(Resource).filter(Resource.tenant_id == current_tenant.id)

    if type:
        query = query.filter(Resource.type == type)

    if is_active is not None:
        query = query.filter(Resource.is_active == is_active)

    if is_bookable is not None:
        query = query.filter(Resource.is_bookable == is_bookable)

    resources = query.order_by(Resource.display_order, Resource.name).offset(skip).limit(limit).all()
    return resources


@router.get("/{resource_id}", response_model=ResourceResponse)
async def get_resource(
    resource_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Get resource by ID
    """
    resource = db.query(Resource).filter(
        Resource.id == resource_id,
        Resource.tenant_id == current_tenant.id
    ).first()

    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )

    return resource


@router.put("/{resource_id}", response_model=ResourceResponse)
async def update_resource(
    resource_id: UUID,
    resource_data: ResourceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_owner),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Update resource (owner only)
    """
    resource = db.query(Resource).filter(
        Resource.id == resource_id,
        Resource.tenant_id == current_tenant.id
    ).first()

    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )

    # Update fields
    for field, value in resource_data.model_dump(exclude_unset=True).items():
        setattr(resource, field, value)

    db.commit()
    db.refresh(resource)

    return resource


@router.delete("/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resource(
    resource_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_owner),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Delete (deactivate) resource (owner only)
    """
    resource = db.query(Resource).filter(
        Resource.id == resource_id,
        Resource.tenant_id == current_tenant.id
    ).first()

    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )

    resource.is_active = False
    db.commit()

    return None
