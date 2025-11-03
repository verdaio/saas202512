"""
Staff service with business logic
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
import uuid

from ..models.staff import Staff
from ..models.tenant import Tenant
from ..schemas.staff import StaffCreate, StaffUpdate


class StaffService:
    """Business logic for staff management"""

    @staticmethod
    def create_staff(
        db: Session,
        tenant: Tenant,
        staff_data: StaffCreate
    ) -> Staff:
        """
        Create new staff member with validation
        """
        # Validate email uniqueness if provided
        if staff_data.email:
            existing = db.query(Staff).filter(
                Staff.tenant_id == tenant.id,
                Staff.email == staff_data.email
            ).first()

            if existing:
                raise ValueError("Staff member with this email already exists")

        staff = Staff(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            **staff_data.model_dump()
        )

        db.add(staff)
        db.commit()
        db.refresh(staff)

        return staff

    @staticmethod
    def get_staff(
        db: Session,
        tenant: Tenant,
        staff_id: UUID
    ) -> Optional[Staff]:
        """Get staff member by ID"""
        return db.query(Staff).filter(
            Staff.id == staff_id,
            Staff.tenant_id == tenant.id
        ).first()

    @staticmethod
    def list_staff(
        db: Session,
        tenant: Tenant,
        skip: int = 0,
        limit: int = 100,
        is_active: bool = None,
        can_groom: bool = None
    ) -> List[Staff]:
        """List staff members with filters"""
        query = db.query(Staff).filter(Staff.tenant_id == tenant.id)

        if is_active is not None:
            query = query.filter(Staff.is_active == is_active)

        if can_groom is not None:
            query = query.filter(Staff.can_groom == can_groom)

        return query.offset(skip).limit(limit).all()

    @staticmethod
    def update_staff(
        db: Session,
        tenant: Tenant,
        staff_id: UUID,
        staff_data: StaffUpdate
    ) -> Optional[Staff]:
        """Update staff member"""
        staff = StaffService.get_staff(db, tenant, staff_id)

        if not staff:
            return None

        # Update fields
        for field, value in staff_data.model_dump(exclude_unset=True).items():
            setattr(staff, field, value)

        db.commit()
        db.refresh(staff)

        return staff

    @staticmethod
    def deactivate_staff(
        db: Session,
        tenant: Tenant,
        staff_id: UUID
    ) -> bool:
        """Deactivate staff member"""
        staff = StaffService.get_staff(db, tenant, staff_id)

        if not staff:
            return False

        staff.is_active = False
        db.commit()

        return True

    @staticmethod
    def get_available_staff(
        db: Session,
        tenant: Tenant,
        service_type: str = None
    ) -> List[Staff]:
        """
        Get available staff members, optionally filtered by service capability
        """
        query = db.query(Staff).filter(
            Staff.tenant_id == tenant.id,
            Staff.is_active == True,
            Staff.is_available == True
        )

        if service_type == "grooming":
            query = query.filter(Staff.can_groom == True)
        elif service_type == "training":
            query = query.filter(Staff.can_train == True)
        elif service_type == "bathing":
            query = query.filter(Staff.can_bathe == True)

        return query.all()
