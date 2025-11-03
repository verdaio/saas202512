"""
Owner service with business logic
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
import uuid

from ..models.owner import Owner
from ..models.tenant import Tenant
from ..schemas.owner import OwnerCreate, OwnerUpdate


class OwnerService:
    """Business logic for pet owner management"""

    @staticmethod
    def create_owner(
        db: Session,
        tenant: Tenant,
        owner_data: OwnerCreate
    ) -> Owner:
        """
        Create new pet owner with validation
        """
        # Check for duplicate email
        existing = db.query(Owner).filter(
            Owner.tenant_id == tenant.id,
            Owner.email == owner_data.email
        ).first()

        if existing:
            raise ValueError("Owner with this email already exists")

        # Check for duplicate phone
        existing_phone = db.query(Owner).filter(
            Owner.tenant_id == tenant.id,
            Owner.phone == owner_data.phone
        ).first()

        if existing_phone:
            raise ValueError("Owner with this phone number already exists")

        owner = Owner(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            **owner_data.model_dump()
        )

        db.add(owner)
        db.commit()
        db.refresh(owner)

        return owner

    @staticmethod
    def get_owner(
        db: Session,
        tenant: Tenant,
        owner_id: UUID
    ) -> Optional[Owner]:
        """Get owner by ID"""
        return db.query(Owner).filter(
            Owner.id == owner_id,
            Owner.tenant_id == tenant.id
        ).first()

    @staticmethod
    def get_owner_by_email(
        db: Session,
        tenant: Tenant,
        email: str
    ) -> Optional[Owner]:
        """Get owner by email"""
        return db.query(Owner).filter(
            Owner.tenant_id == tenant.id,
            Owner.email == email
        ).first()

    @staticmethod
    def get_owner_by_phone(
        db: Session,
        tenant: Tenant,
        phone: str
    ) -> Optional[Owner]:
        """Get owner by phone"""
        return db.query(Owner).filter(
            Owner.tenant_id == tenant.id,
            Owner.phone == phone
        ).first()

    @staticmethod
    def list_owners(
        db: Session,
        tenant: Tenant,
        skip: int = 0,
        limit: int = 100,
        search: str = None,
        is_active: bool = None
    ) -> List[Owner]:
        """List owners with filters and search"""
        query = db.query(Owner).filter(Owner.tenant_id == tenant.id)

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

        return query.order_by(Owner.last_name, Owner.first_name).offset(skip).limit(limit).all()

    @staticmethod
    def update_owner(
        db: Session,
        tenant: Tenant,
        owner_id: UUID,
        owner_data: OwnerUpdate
    ) -> Optional[Owner]:
        """Update owner"""
        owner = OwnerService.get_owner(db, tenant, owner_id)

        if not owner:
            return None

        # Update fields
        for field, value in owner_data.model_dump(exclude_unset=True).items():
            setattr(owner, field, value)

        db.commit()
        db.refresh(owner)

        return owner

    @staticmethod
    def deactivate_owner(
        db: Session,
        tenant: Tenant,
        owner_id: UUID
    ) -> bool:
        """Deactivate owner"""
        owner = OwnerService.get_owner(db, tenant, owner_id)

        if not owner:
            return False

        owner.is_active = False
        db.commit()

        return True
