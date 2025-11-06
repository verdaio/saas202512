"""
Schedule and availability API endpoints
Sprint 2 - Scheduling Engine
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
from uuid import UUID

from ..db.session import get_db
from ..core.dependencies import get_current_tenant
from ..services.scheduling_service import SchedulingService
from ..models.tenant import Tenant
from pydantic import BaseModel


router = APIRouter()


# ==================== REQUEST/RESPONSE SCHEMAS ====================

class AvailabilityCheckRequest(BaseModel):
    """Request schema for checking availability"""
    staff_id: Optional[UUID] = None
    resource_id: Optional[UUID] = None
    start_time: datetime
    end_time: datetime
    exclude_appointment_id: Optional[UUID] = None


class AvailabilityCheckResponse(BaseModel):
    """Response schema for availability check"""
    is_available: bool
    reason: Optional[str] = None


class TimeSlotResponse(BaseModel):
    """Response schema for a time slot"""
    start_time: str
    end_time: str
    staff_ids: List[str]
    duration_minutes: int


class NextAvailableSlotResponse(BaseModel):
    """Response schema for next available slot"""
    found: bool
    slot: Optional[TimeSlotResponse] = None
    message: Optional[str] = None


# ==================== ENDPOINTS ====================

@router.get("/available-slots", response_model=List[dict])
def get_available_time_slots(
    service_id: UUID,
    date: date,
    staff_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant)
):
    """
    Get all available time slots for a service on a given date

    **Parameters:**
    - **service_id**: ID of the service
    - **date**: Date to check (YYYY-MM-DD format)
    - **staff_id**: Optional - filter by specific staff member

    **Returns:**
    - List of available time slots with staff assignments

    **Example:**
    ```
    GET /api/v1/schedule/available-slots?service_id=123&date=2025-11-15
    ```

    **Use case:** Booking widget displays available appointment times
    """
    slots = SchedulingService.get_available_time_slots(
        db=db,
        tenant=tenant,
        date=date,
        service_id=service_id,
        staff_id=staff_id
    )

    return slots


@router.post("/check-staff-availability", response_model=AvailabilityCheckResponse)
def check_staff_availability(
    request: AvailabilityCheckRequest,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant)
):
    """
    Check if a staff member is available for a specific time slot

    **Use case:** Validate staff selection before creating appointment

    **Parameters in request body:**
    - **staff_id**: Staff member ID (required)
    - **start_time**: Proposed start time
    - **end_time**: Proposed end time
    - **exclude_appointment_id**: Optional - for rescheduling

    **Returns:**
    - is_available: Boolean
    - reason: String explaining why not available (if applicable)
    """
    if not request.staff_id:
        raise HTTPException(status_code=400, detail="staff_id is required")

    is_available = SchedulingService.check_staff_availability(
        db=db,
        tenant=tenant,
        staff_id=request.staff_id,
        start_time=request.start_time,
        end_time=request.end_time,
        exclude_appointment_id=request.exclude_appointment_id
    )

    reason = None if is_available else "Staff member is not available at this time"

    return AvailabilityCheckResponse(
        is_available=is_available,
        reason=reason
    )


@router.post("/check-resource-availability", response_model=AvailabilityCheckResponse)
def check_resource_availability(
    request: AvailabilityCheckRequest,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant)
):
    """
    Check if a resource (table, van, room) is available for a specific time slot

    **Use case:** Validate resource selection before creating appointment

    **Parameters in request body:**
    - **resource_id**: Resource ID (required)
    - **start_time**: Proposed start time
    - **end_time**: Proposed end time
    - **exclude_appointment_id**: Optional - for rescheduling

    **Returns:**
    - is_available: Boolean
    - reason: String explaining why not available (if applicable)
    """
    if not request.resource_id:
        raise HTTPException(status_code=400, detail="resource_id is required")

    is_available = SchedulingService.check_resource_availability(
        db=db,
        tenant=tenant,
        resource_id=request.resource_id,
        start_time=request.start_time,
        end_time=request.end_time,
        exclude_appointment_id=request.exclude_appointment_id
    )

    reason = None if is_available else "Resource is not available at this time"

    return AvailabilityCheckResponse(
        is_available=is_available,
        reason=reason
    )


@router.get("/next-available", response_model=NextAvailableSlotResponse)
def find_next_available_slot(
    service_id: UUID,
    start_date: Optional[date] = None,
    staff_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant)
):
    """
    Find the next available time slot for a service

    **Parameters:**
    - **service_id**: ID of the service
    - **start_date**: Optional - date to start searching from (defaults to today)
    - **staff_id**: Optional - filter by specific staff member

    **Returns:**
    - found: Boolean
    - slot: TimeSlotResponse if found
    - message: String message

    **Use case:** "Book next available" feature in booking widget

    **Example:**
    ```
    GET /api/v1/schedule/next-available?service_id=123
    ```
    """
    if not start_date:
        start_date = date.today()

    slot = SchedulingService.find_next_available_slot(
        db=db,
        tenant=tenant,
        service_id=service_id,
        start_date=start_date,
        staff_id=staff_id
    )

    if slot:
        return NextAvailableSlotResponse(
            found=True,
            slot=TimeSlotResponse(**slot),
            message="Next available slot found"
        )
    else:
        return NextAvailableSlotResponse(
            found=False,
            slot=None,
            message="No available slots found in the next 14 days"
        )


@router.get("/staff/{staff_id}/availability")
def get_staff_daily_availability(
    staff_id: UUID,
    date: date,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant)
):
    """
    Get staff member's availability for a specific day

    **Parameters:**
    - **staff_id**: Staff member ID
    - **date**: Date to check

    **Returns:**
    - working_hours: Staff schedule for the day
    - booked_slots: List of existing appointments
    - available_slots: List of free time periods

    **Use case:** Staff scheduling view, drag-and-drop appointment booking
    """
    from ..models.staff import Staff
    from ..models.appointment import Appointment, AppointmentStatus

    # Get staff member
    staff = db.query(Staff).filter(
        Staff.id == staff_id,
        Staff.tenant_id == tenant.id,
        Staff.deleted_at.is_(None)
    ).first()

    if not staff:
        raise HTTPException(status_code=404, detail="Staff member not found")

    # Get day schedule
    day_name = date.strftime("%A").lower()
    day_schedule = None

    if staff.schedule and day_name in staff.schedule:
        day_schedule = staff.schedule[day_name]

    # Get existing appointments for this day
    start_of_day = datetime.combine(date, datetime.min.time())
    end_of_day = datetime.combine(date, datetime.max.time())

    appointments = db.query(Appointment).filter(
        Appointment.staff_id == staff_id,
        Appointment.tenant_id == tenant.id,
        Appointment.scheduled_start >= start_of_day,
        Appointment.scheduled_start < end_of_day,
        Appointment.status.in_([
            AppointmentStatus.PENDING,
            AppointmentStatus.CONFIRMED,
            AppointmentStatus.IN_PROGRESS
        ]),
        Appointment.deleted_at.is_(None)
    ).order_by(Appointment.scheduled_start).all()

    booked_slots = [
        {
            "start": appt.scheduled_start.isoformat(),
            "end": appt.scheduled_end.isoformat(),
            "appointment_id": str(appt.id),
            "service": appt.service.name if appt.service else None
        }
        for appt in appointments
    ]

    return {
        "staff_id": str(staff_id),
        "staff_name": staff.full_name,
        "date": date.isoformat(),
        "day_of_week": day_name.capitalize(),
        "working_hours": day_schedule,
        "booked_slots": booked_slots,
        "total_appointments": len(booked_slots)
    }


@router.get("/resource/{resource_id}/availability")
def get_resource_daily_availability(
    resource_id: UUID,
    date: date,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant)
):
    """
    Get resource availability for a specific day

    **Parameters:**
    - **resource_id**: Resource ID
    - **date**: Date to check

    **Returns:**
    - working_hours: Resource schedule for the day
    - booked_slots: List of existing appointments
    - capacity: How many concurrent appointments allowed

    **Use case:** Resource scheduling view, capacity planning
    """
    from ..models.resource import Resource
    from ..models.appointment import Appointment, AppointmentStatus

    # Get resource
    resource = db.query(Resource).filter(
        Resource.id == resource_id,
        Resource.tenant_id == tenant.id,
        Resource.deleted_at.is_(None)
    ).first()

    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    # Get day schedule
    day_name = date.strftime("%A").lower()
    day_schedule = None

    if resource.schedule and day_name in resource.schedule:
        day_schedule = resource.schedule[day_name]

    # Get existing appointments for this day
    start_of_day = datetime.combine(date, datetime.min.time())
    end_of_day = datetime.combine(date, datetime.max.time())

    appointments = db.query(Appointment).filter(
        Appointment.resource_id == resource_id,
        Appointment.tenant_id == tenant.id,
        Appointment.scheduled_start >= start_of_day,
        Appointment.scheduled_start < end_of_day,
        Appointment.status.in_([
            AppointmentStatus.PENDING,
            AppointmentStatus.CONFIRMED,
            AppointmentStatus.IN_PROGRESS
        ]),
        Appointment.deleted_at.is_(None)
    ).order_by(Appointment.scheduled_start).all()

    booked_slots = [
        {
            "start": appt.scheduled_start.isoformat(),
            "end": appt.scheduled_end.isoformat(),
            "appointment_id": str(appt.id),
            "service": appt.service.name if appt.service else None
        }
        for appt in appointments
    ]

    return {
        "resource_id": str(resource_id),
        "resource_name": resource.name,
        "resource_type": resource.type,
        "date": date.isoformat(),
        "day_of_week": day_name.capitalize(),
        "working_hours": day_schedule,
        "capacity": resource.capacity,
        "booked_slots": booked_slots,
        "total_appointments": len(booked_slots)
    }
