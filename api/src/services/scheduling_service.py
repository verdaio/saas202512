"""
Scheduling service with availability logic and double-booking prevention
Sprint 2 implementation
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional, Tuple
from datetime import datetime, timedelta, time, date
from uuid import UUID

from ..models.appointment import Appointment, AppointmentStatus
from ..models.staff import Staff
from ..models.service import Service
from ..models.resource import Resource
from ..models.pet import Pet
from ..models.vaccination_record import VaccinationRecord
from ..models.tenant import Tenant


class SchedulingService:
    """Business logic for scheduling and availability checking"""

    @staticmethod
    def check_staff_availability(
        db: Session,
        tenant: Tenant,
        staff_id: UUID,
        start_time: datetime,
        end_time: datetime,
        exclude_appointment_id: UUID = None
    ) -> bool:
        """
        Check if staff member is available for the given time slot
        """
        # Get staff member
        staff = db.query(Staff).filter(
            Staff.id == staff_id,
            Staff.tenant_id == tenant.id
        ).first()

        if not staff or not staff.is_available:
            return False

        # Check for overlapping appointments with row-level locking (double-booking prevention)
        query = db.query(Appointment).filter(
            Appointment.tenant_id == tenant.id,
            Appointment.staff_id == staff_id,
            Appointment.status.in_([
                AppointmentStatus.PENDING,
                AppointmentStatus.CONFIRMED,
                AppointmentStatus.IN_PROGRESS
            ]),
            or_(
                # New appointment starts during existing appointment
                and_(
                    Appointment.scheduled_start <= start_time,
                    Appointment.scheduled_end > start_time
                ),
                # New appointment ends during existing appointment
                and_(
                    Appointment.scheduled_start < end_time,
                    Appointment.scheduled_end >= end_time
                ),
                # New appointment completely contains existing appointment
                and_(
                    Appointment.scheduled_start >= start_time,
                    Appointment.scheduled_end <= end_time
                )
            )
        ).with_for_update()  # Row-level lock for double-booking prevention

        if exclude_appointment_id:
            query = query.filter(Appointment.id != exclude_appointment_id)

        overlapping = query.first()

        if overlapping:
            return False

        # TODO: Check staff schedule (working hours, breaks)
        # For now, assume staff is available during business hours (9am-5pm)

        return True

    @staticmethod
    def check_resource_availability(
        db: Session,
        tenant: Tenant,
        resource_id: UUID,
        start_time: datetime,
        end_time: datetime,
        exclude_appointment_id: UUID = None
    ) -> bool:
        """
        Check if resource (table, van, room) is available for the given time slot
        """
        # Get resource
        resource = db.query(Resource).filter(
            Resource.id == resource_id,
            Resource.tenant_id == tenant.id
        ).first()

        if not resource or not resource.is_bookable:
            return False

        # Check capacity
        # Count overlapping appointments using this resource
        query = db.query(func.count(Appointment.id)).filter(
            Appointment.tenant_id == tenant.id,
            Appointment.resource_id == resource_id,
            Appointment.status.in_([
                AppointmentStatus.PENDING,
                AppointmentStatus.CONFIRMED,
                AppointmentStatus.IN_PROGRESS
            ]),
            or_(
                and_(
                    Appointment.scheduled_start <= start_time,
                    Appointment.scheduled_end > start_time
                ),
                and_(
                    Appointment.scheduled_start < end_time,
                    Appointment.scheduled_end >= end_time
                ),
                and_(
                    Appointment.scheduled_start >= start_time,
                    Appointment.scheduled_end <= end_time
                )
            )
        )

        if exclude_appointment_id:
            query = query.filter(Appointment.id != exclude_appointment_id)

        overlapping_count = query.scalar()

        # Check if resource has capacity
        if overlapping_count >= resource.capacity:
            return False

        return True

    @staticmethod
    def validate_vaccination_requirements(
        db: Session,
        tenant: Tenant,
        pet_ids: List[UUID],
        service_id: UUID
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate that all pets meet vaccination requirements for the service
        Returns (is_valid, error_message)
        """
        # Get service
        service = db.query(Service).filter(
            Service.id == service_id,
            Service.tenant_id == tenant.id
        ).first()

        if not service:
            return False, "Service not found"

        if not service.requires_vaccination:
            return True, None

        # Check each pet
        for pet_id in pet_ids:
            pet = db.query(Pet).filter(
                Pet.id == pet_id,
                Pet.tenant_id == tenant.id
            ).first()

            if not pet:
                return False, f"Pet {pet_id} not found"

            # Get most recent vaccination records
            if service.vaccination_types_required:
                for vacc_type in service.vaccination_types_required:
                    latest_vacc = db.query(VaccinationRecord).filter(
                        VaccinationRecord.pet_id == pet_id,
                        VaccinationRecord.tenant_id == tenant.id,
                        VaccinationRecord.type == vacc_type
                    ).order_by(VaccinationRecord.expiry_date.desc()).first()

                    if not latest_vacc or not latest_vacc.is_current:
                        return False, f"Pet {pet.name} requires current {vacc_type} vaccination"
            else:
                # Check general vaccination status
                if pet.vaccination_status not in ["current", "verified"]:
                    return False, f"Pet {pet.name} vaccination status is {pet.vaccination_status}"

        return True, None

    @staticmethod
    def get_available_time_slots(
        db: Session,
        tenant: Tenant,
        date: date,
        service_id: UUID,
        staff_id: UUID = None
    ) -> List[dict]:
        """
        Get all available time slots for a given date and service
        Returns list of {start_time, end_time, staff_id}
        """
        # Get service
        service = db.query(Service).filter(
            Service.id == service_id,
            Service.tenant_id == tenant.id
        ).first()

        if not service:
            return []

        # Calculate total duration including buffers
        total_duration = service.duration_minutes + service.setup_buffer_minutes + service.cleanup_buffer_minutes

        # Business hours (TODO: Get from tenant settings)
        business_start = time(9, 0)
        business_end = time(17, 0)

        # Generate time slots (every 30 minutes)
        slots = []
        current_time = datetime.combine(date, business_start)
        end_datetime = datetime.combine(date, business_end)

        while current_time + timedelta(minutes=total_duration) <= end_datetime:
            slot_end = current_time + timedelta(minutes=total_duration)

            # Get available staff for this slot
            available_staff = []

            if staff_id:
                # Check specific staff member
                if SchedulingService.check_staff_availability(
                    db, tenant, staff_id, current_time, slot_end
                ):
                    available_staff.append(staff_id)
            else:
                # Find any available staff
                all_staff = db.query(Staff).filter(
                    Staff.tenant_id == tenant.id,
                    Staff.is_active == True,
                    Staff.is_available == True
                ).all()

                for staff_member in all_staff:
                    if SchedulingService.check_staff_availability(
                        db, tenant, staff_member.id, current_time, slot_end
                    ):
                        available_staff.append(staff_member.id)

            # If staff available, add slot
            if available_staff:
                slots.append({
                    "start_time": current_time.isoformat(),
                    "end_time": slot_end.isoformat(),
                    "staff_ids": [str(sid) for sid in available_staff],
                    "duration_minutes": total_duration
                })

            # Move to next slot (30 minute intervals)
            current_time += timedelta(minutes=30)

        return slots

    @staticmethod
    def validate_booking(
        db: Session,
        tenant: Tenant,
        start_time: datetime,
        end_time: datetime,
        service_id: UUID,
        pet_ids: List[UUID],
        staff_id: UUID = None,
        resource_id: UUID = None,
        exclude_appointment_id: UUID = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Comprehensive booking validation
        Returns (is_valid, error_message)
        """
        # 1. Validate service exists
        service = db.query(Service).filter(
            Service.id == service_id,
            Service.tenant_id == tenant.id
        ).first()

        if not service:
            return False, "Service not found"

        if not service.is_active or not service.is_bookable_online:
            return False, "Service is not available for booking"

        # 2. Validate time slot is in the future
        if start_time <= datetime.utcnow():
            return False, "Cannot book appointments in the past"

        # 3. Validate duration matches service
        expected_duration = service.duration_minutes + service.setup_buffer_minutes + service.cleanup_buffer_minutes
        actual_duration = (end_time - start_time).total_seconds() / 60

        if abs(actual_duration - expected_duration) > 1:  # Allow 1 minute tolerance
            return False, f"Invalid appointment duration. Expected {expected_duration} minutes, got {actual_duration}"

        # 4. Validate max pets per session
        if len(pet_ids) > service.max_pets_per_session:
            return False, f"Service allows maximum {service.max_pets_per_session} pets per session"

        # 5. Validate vaccination requirements
        is_valid, error = SchedulingService.validate_vaccination_requirements(
            db, tenant, pet_ids, service_id
        )
        if not is_valid:
            return False, error

        # 6. Check staff availability (with row lock for double-booking prevention)
        if staff_id:
            if not SchedulingService.check_staff_availability(
                db, tenant, staff_id, start_time, end_time, exclude_appointment_id
            ):
                return False, "Staff member is not available at this time"

        # 7. Check resource availability
        if resource_id:
            if not SchedulingService.check_resource_availability(
                db, tenant, resource_id, start_time, end_time, exclude_appointment_id
            ):
                return False, "Resource is not available at this time"

        # 8. Validate resource requirements
        if service.requires_table or service.requires_van or service.requires_room:
            if not resource_id:
                return False, "This service requires a resource (table/van/room)"

        return True, None

    @staticmethod
    def find_next_available_slot(
        db: Session,
        tenant: Tenant,
        service_id: UUID,
        start_date: date,
        staff_id: UUID = None
    ) -> Optional[dict]:
        """
        Find the next available time slot starting from the given date
        Returns first available slot or None
        """
        # Search up to 14 days ahead
        for days_ahead in range(14):
            check_date = start_date + timedelta(days=days_ahead)

            # Skip weekends (TODO: Check tenant business days)
            if check_date.weekday() >= 5:  # 5=Saturday, 6=Sunday
                continue

            slots = SchedulingService.get_available_time_slots(
                db, tenant, check_date, service_id, staff_id
            )

            if slots:
                return slots[0]

        return None

    @staticmethod
    def calculate_appointment_end_time(
        service: Service,
        start_time: datetime
    ) -> datetime:
        """
        Calculate appointment end time including buffers
        """
        total_duration = service.duration_minutes + service.setup_buffer_minutes + service.cleanup_buffer_minutes
        return start_time + timedelta(minutes=total_duration)
