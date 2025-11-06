"""
Appointment service with business logic
Sprint 2: Scheduling validation and double-booking prevention implemented
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
from .scheduling_service import SchedulingService


class AppointmentService:
    """Business logic for appointment management"""

    @staticmethod
    def create_appointment(
        db: Session,
        tenant: Tenant,
        appointment_data: AppointmentCreate
    ) -> Appointment:
        """
        Create new appointment with comprehensive validation
        Includes double-booking prevention and availability checking
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

        # Validate booking with scheduling service (includes double-booking prevention)
        is_valid, error_message = SchedulingService.validate_booking(
            db=db,
            tenant=tenant,
            start_time=appointment_data.scheduled_start,
            end_time=appointment_data.scheduled_end,
            service_id=appointment_data.service_id,
            pet_ids=appointment_data.pet_ids,
            staff_id=appointment_data.staff_id,
            resource_id=appointment_data.resource_id
        )

        if not is_valid:
            raise ValueError(error_message)

        # Calculate deposit if required
        deposit_required = None
        if service.deposit_amount:
            deposit_required = service.deposit_amount
        elif service.deposit_percentage:
            deposit_required = (service.price * service.deposit_percentage) // 100

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
        Update appointment with re-validation if time changed
        """
        appointment = AppointmentService.get_appointment(db, tenant, appointment_id)

        if not appointment:
            return None

        # Check if time is changing
        time_changed = (
            appointment_data.scheduled_start is not None or
            appointment_data.scheduled_end is not None
        )

        if time_changed:
            # Get new times (use existing if not provided)
            new_start = appointment_data.scheduled_start or appointment.scheduled_start
            new_end = appointment_data.scheduled_end or appointment.scheduled_end

            # Re-validate with scheduling service
            is_valid, error_message = SchedulingService.validate_booking(
                db=db,
                tenant=tenant,
                start_time=new_start,
                end_time=new_end,
                service_id=appointment.service_id,
                pet_ids=[pet.id for pet in appointment.pets] if hasattr(appointment, 'pets') else [],
                staff_id=appointment_data.staff_id or appointment.staff_id,
                resource_id=appointment.resource_id,
                exclude_appointment_id=appointment_id  # Exclude this appointment from conflict check
            )

            if not is_valid:
                raise ValueError(error_message)

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
