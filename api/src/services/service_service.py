"""
Service service with business logic (for grooming/training services)
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
import uuid

from ..models.service import Service
from ..models.tenant import Tenant
from ..schemas.service import ServiceCreate, ServiceUpdate


class ServiceService:
    """Business logic for service management"""

    @staticmethod
    def create_service(
        db: Session,
        tenant: Tenant,
        service_data: ServiceCreate
    ) -> Service:
        """
        Create new service with validation
        """
        # Check for duplicate name
        existing = db.query(Service).filter(
            Service.tenant_id == tenant.id,
            Service.name == service_data.name
        ).first()

        if existing:
            raise ValueError("Service with this name already exists")

        # Validate duration
        if service_data.duration_minutes < 1:
            raise ValueError("Duration must be at least 1 minute")

        # Validate price
        if service_data.price < 0:
            raise ValueError("Price cannot be negative")

        service = Service(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            **service_data.model_dump()
        )

        db.add(service)
        db.commit()
        db.refresh(service)

        return service

    @staticmethod
    def get_service(
        db: Session,
        tenant: Tenant,
        service_id: UUID
    ) -> Optional[Service]:
        """Get service by ID"""
        return db.query(Service).filter(
            Service.id == service_id,
            Service.tenant_id == tenant.id
        ).first()

    @staticmethod
    def list_services(
        db: Session,
        tenant: Tenant,
        skip: int = 0,
        limit: int = 100,
        category: str = None,
        is_active: bool = None,
        is_bookable_online: bool = None
    ) -> List[Service]:
        """List services with filters"""
        query = db.query(Service).filter(Service.tenant_id == tenant.id)

        if category:
            query = query.filter(Service.category == category)

        if is_active is not None:
            query = query.filter(Service.is_active == is_active)

        if is_bookable_online is not None:
            query = query.filter(Service.is_bookable_online == is_bookable_online)

        return query.order_by(Service.display_order, Service.name).offset(skip).limit(limit).all()

    @staticmethod
    def get_bookable_services(
        db: Session,
        tenant: Tenant
    ) -> List[Service]:
        """Get all bookable services for booking widget"""
        return db.query(Service).filter(
            Service.tenant_id == tenant.id,
            Service.is_active == True,
            Service.is_bookable_online == True
        ).order_by(Service.display_order, Service.name).all()

    @staticmethod
    def update_service(
        db: Session,
        tenant: Tenant,
        service_id: UUID,
        service_data: ServiceUpdate
    ) -> Optional[Service]:
        """Update service"""
        service = ServiceService.get_service(db, tenant, service_id)

        if not service:
            return None

        # Update fields
        for field, value in service_data.model_dump(exclude_unset=True).items():
            setattr(service, field, value)

        db.commit()
        db.refresh(service)

        return service

    @staticmethod
    def deactivate_service(
        db: Session,
        tenant: Tenant,
        service_id: UUID
    ) -> bool:
        """Deactivate service"""
        service = ServiceService.get_service(db, tenant, service_id)

        if not service:
            return False

        service.is_active = False
        db.commit()

        return True

    @staticmethod
    def calculate_total_duration(
        service: Service
    ) -> int:
        """Calculate total duration including buffers"""
        return service.duration_minutes + service.setup_buffer_minutes + service.cleanup_buffer_minutes
