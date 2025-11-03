"""
Appointment service with business logic
TODO Sprint 2: Add scheduling validation and double-booking prevention
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from uuid import UUID
import uuid

from ..models.appointment import Appointment, AppointmentStatus
from ..models.owner import Owner
from ..models.service import Service
from ..models.tenant import Tenant
from ..schemas.appointment import AppointmentCreate, AppointmentUpdate


class AppointmentService:
    """Business logic for appointment management"""

    @staticmethod
    def create_appointment(
        db: Session,
        tenant: Tenant,
        appointment_data: AppointmentCreate
    ) -> Appointment:
        """
        Create new appointment with validation
        TODO Sprint 2: Add double-booking prevention
        TODO Sprint 2: Add staff/resource availability checking
        """
        # Verify owner exists
        owner = db.query(Owner).filter(
            Owner.id == appointment_data.owner_id,
            Owner.tenant_id == tenant.id
        ).first()

        if not owner:
            raise ValueError("Owner not found")

        # Verify service exists
        service = db.query(Service).filter(
            Service.id == appointment_data.service_id,
            Service.tenant_id == tenant.id
        ).first()

        if not service:
            raise ValueError("Service not found")

        # Calculate deposit if required
        deposit_required = None
        if service.deposit_amount:
            deposit_required = service.deposit_amount
        elif service.deposit_percentage:
            deposit_required = (service.price * service.deposit_percentage) // 100

        # TODO Sprint 2: Validate time slot availability
        # TODO Sprint 2: Check staff availability
        # TODO Sprint 2: Check resource availability
        # TODO Sprint 2: Validate vaccination requirements

        appointment = Appointment(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            status=AppointmentStatus.PENDING,
            source="online",
            deposit_required=deposit_required,
            total_amount=service.price,
            **appointment_data.model_dump()
        )

        db.add(appointment)
        db.commit()
        db.refresh(appointment)

        return appointment

    @staticmethod
    def get_appointment(
        db: Session,
        tenant: Tenant,
        appointment_id: UUID
    ) -> Optional[Appointment]:
        """Get appointment by ID"""
        return db.query(Appointment).filter(
            Appointment.id == appointment_id,
            Appointment.tenant_id == tenant.id
        ).first()

    @staticmethod
    def list_appointments(
        db: Session,
        tenant: Tenant,
        skip: int = 0,
        limit: int = 100,
        owner_id: UUID = None,
        staff_id: UUID = None,
        status: str = None,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> List[Appointment]:
        """List appointments with filters"""
        query = db.query(Appointment).filter(Appointment.tenant_id == tenant.id)

        if owner_id:
            query = query.filter(Appointment.owner_id == owner_id)

        if staff_id:
            query = query.filter(Appointment.staff_id == staff_id)

        if status:
            query = query.filter(Appointment.status == status)

        if start_date:
            query = query.filter(Appointment.scheduled_start >= start_date)

        if end_date:
            query = query.filter(Appointment.scheduled_end <= end_date)

        return query.order_by(Appointment.scheduled_start).offset(skip).limit(limit).all()

    @staticmethod
    def update_appointment(
        db: Session,
        tenant: Tenant,
        appointment_id: UUID,
        appointment_data: AppointmentUpdate
    ) -> Optional[Appointment]:
        """
        Update appointment
        TODO Sprint 2: Re-validate time slot if time changed
        """
        appointment = AppointmentService.get_appointment(db, tenant, appointment_id)

        if not appointment:
            return None

        # TODO Sprint 2: If time is changing, validate new time slot

        # Update fields
        for field, value in appointment_data.model_dump(exclude_unset=True).items():
            setattr(appointment, field, value)

        db.commit()
        db.refresh(appointment)

        return appointment

    @staticmethod
    def cancel_appointment(
        db: Session,
        tenant: Tenant,
        appointment_id: UUID
    ) -> Optional[Appointment]:
        """Cancel appointment"""
        appointment = AppointmentService.get_appointment(db, tenant, appointment_id)

        if not appointment:
            return None

        if appointment.status in [AppointmentStatus.COMPLETED, AppointmentStatus.CANCELLED]:
            raise ValueError("Cannot cancel completed or already cancelled appointment")

        appointment.status = AppointmentStatus.CANCELLED
        appointment.cancelled_at = datetime.utcnow()

        db.commit()
        db.refresh(appointment)

        return appointment

    @staticmethod
    def confirm_appointment(
        db: Session,
        tenant: Tenant,
        appointment_id: UUID
    ) -> Optional[Appointment]:
        """Confirm appointment"""
        appointment = AppointmentService.get_appointment(db, tenant, appointment_id)

        if not appointment:
            return None

        appointment.status = AppointmentStatus.CONFIRMED
        appointment.confirmed_at = datetime.utcnow()

        db.commit()
        db.refresh(appointment)

        return appointment

    @staticmethod
    def complete_appointment(
        db: Session,
        tenant: Tenant,
        appointment_id: UUID
    ) -> Optional[Appointment]:
        """Mark appointment as completed"""
        appointment = AppointmentService.get_appointment(db, tenant, appointment_id)

        if not appointment:
            return None

        appointment.status = AppointmentStatus.COMPLETED
        appointment.completed_at = datetime.utcnow()

        db.commit()
        db.refresh(appointment)

        return appointment

    # TODO Sprint 2: Add these methods
    # @staticmethod
    # def check_availability(db, tenant, start_time, end_time, staff_id, resource_id): pass
    # @staticmethod
    # def get_available_time_slots(db, tenant, date, service_id): pass
    # @staticmethod
    # def prevent_double_booking(db, tenant, start_time, end_time, staff_id): pass
