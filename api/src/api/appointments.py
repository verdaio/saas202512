"""
Appointment API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, date
from uuid import UUID
import uuid

from ..db.base import get_db
from ..core.dependencies import get_current_user, get_current_tenant, get_public_tenant, require_staff_or_admin
from ..models.user import User
from ..models.tenant import Tenant
from ..models.appointment import Appointment, AppointmentStatus
from ..models.owner import Owner
from ..models.service import Service
from ..schemas.appointment import AppointmentCreate, AppointmentUpdate, AppointmentResponse
from ..services.scheduling_service import SchedulingService
from ..services.appointment_service import AppointmentService

router = APIRouter()


@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    appointment_data: AppointmentCreate,
    db: Session = Depends(get_db),
    current_tenant: Tenant = Depends(get_public_tenant)
):
    """
    Create new appointment (public endpoint for booking widget)

    Includes comprehensive validation:
    - Staff/resource availability checking
    - Double-booking prevention with row-level locking
    - Vaccination requirement validation
    - Schedule validation (working hours, breaks)
    """
    try:
        appointment = AppointmentService.create_appointment(
            db=db,
            tenant=current_tenant,
            appointment_data=appointment_data
        )
        return appointment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=List[AppointmentResponse])
async def list_appointments(
    skip: int = 0,
    limit: int = 100,
    owner_id: UUID = None,
    staff_id: UUID = None,
    status: str = None,
    start_date: datetime = None,
    end_date: datetime = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    List appointments for current tenant
    """
    query = db.query(Appointment).filter(Appointment.tenant_id == current_tenant.id)

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

    appointments = query.order_by(Appointment.scheduled_start).offset(skip).limit(limit).all()
    return appointments


@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Get appointment by ID
    """
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id,
        Appointment.tenant_id == current_tenant.id
    ).first()

    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )

    return appointment


@router.put("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: UUID,
    appointment_data: AppointmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_admin),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Update appointment (staff/admin/owner)

    If time is changed, re-validates:
    - Staff/resource availability
    - No conflicts with other appointments
    - Schedule compliance
    """
    try:
        appointment = AppointmentService.update_appointment(
            db=db,
            tenant=current_tenant,
            appointment_id=appointment_id,
            appointment_data=appointment_data
        )

        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found"
            )

        return appointment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{appointment_id}/cancel", response_model=AppointmentResponse)
async def cancel_appointment(
    appointment_id: UUID,
    db: Session = Depends(get_db),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Cancel appointment (public endpoint for booking widget)
    """
    try:
        appointment = AppointmentService.cancel_appointment(
            db=db,
            tenant=current_tenant,
            appointment_id=appointment_id
        )

        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found"
            )

        return appointment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{appointment_id}/confirm", response_model=AppointmentResponse)
async def confirm_appointment(
    appointment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_admin),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Confirm appointment (staff/admin/owner)
    """
    appointment = AppointmentService.confirm_appointment(
        db=db,
        tenant=current_tenant,
        appointment_id=appointment_id
    )

    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )

    return appointment


@router.patch("/{appointment_id}/check-in", response_model=AppointmentResponse)
async def check_in_appointment(
    appointment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_admin),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Check in appointment (staff/admin/owner)
    """
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id,
        Appointment.tenant_id == current_tenant.id
    ).first()

    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )

    appointment.status = AppointmentStatus.CHECKED_IN
    appointment.updated_at = datetime.now()
    db.commit()
    db.refresh(appointment)

    return appointment


@router.patch("/{appointment_id}/start", response_model=AppointmentResponse)
async def start_appointment(
    appointment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_admin),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Start appointment (staff/admin/owner)
    """
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id,
        Appointment.tenant_id == current_tenant.id
    ).first()

    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )

    appointment.status = AppointmentStatus.IN_PROGRESS
    appointment.updated_at = datetime.now()
    db.commit()
    db.refresh(appointment)

    return appointment


@router.patch("/{appointment_id}/complete", response_model=AppointmentResponse)
async def complete_appointment(
    appointment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_admin),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Mark appointment as completed (staff/admin/owner)
    """
    appointment = AppointmentService.complete_appointment(
        db=db,
        tenant=current_tenant,
        appointment_id=appointment_id
    )

    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )

    return appointment


@router.patch("/{appointment_id}/no-show", response_model=AppointmentResponse)
async def mark_no_show(
    appointment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_admin),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Mark appointment as no-show (staff/admin/owner)
    """
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id,
        Appointment.tenant_id == current_tenant.id
    ).first()

    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )

    appointment.status = AppointmentStatus.NO_SHOW
    appointment.updated_at = datetime.now()
    db.commit()
    db.refresh(appointment)

    return appointment


@router.patch("/{appointment_id}/cancel", response_model=AppointmentResponse)
async def cancel_appointment_patch(
    appointment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_admin),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Cancel appointment (staff endpoint)
    """
    try:
        appointment = AppointmentService.cancel_appointment(
            db=db,
            tenant=current_tenant,
            appointment_id=appointment_id
        )

        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found"
            )

        return appointment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch("/{appointment_id}/reschedule", response_model=AppointmentResponse)
async def reschedule_appointment(
    appointment_id: UUID,
    reschedule_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_admin),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Reschedule appointment (staff endpoint)
    """
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id,
        Appointment.tenant_id == current_tenant.id
    ).first()

    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )

    # Update scheduled times
    if "scheduled_start" in reschedule_data:
        appointment.scheduled_start = datetime.fromisoformat(reschedule_data["scheduled_start"])

    if "scheduled_end" in reschedule_data:
        appointment.scheduled_end = datetime.fromisoformat(reschedule_data["scheduled_end"])

    # Update staff if provided
    if "staff_id" in reschedule_data and reschedule_data["staff_id"]:
        appointment.staff_id = UUID(reschedule_data["staff_id"])

    appointment.updated_at = datetime.now()
    db.commit()
    db.refresh(appointment)

    return appointment


@router.get("/availability/slots", response_model=List[dict])
async def get_available_slots(
    service_id: UUID = Query(..., description="Service ID"),
    date: date = Query(..., description="Date to check"),
    staff_id: UUID = Query(None, description="Optional staff member ID"),
    db: Session = Depends(get_db),
    current_tenant: Tenant = Depends(get_public_tenant)
):
    """
    Get available time slots for a service on a given date (public endpoint for booking widget)
    """
    slots = SchedulingService.get_available_time_slots(
        db=db,
        tenant=current_tenant,
        date=date,
        service_id=service_id,
        staff_id=staff_id
    )

    return slots


@router.get("/availability/next", response_model=dict)
async def get_next_available_slot(
    service_id: UUID = Query(..., description="Service ID"),
    start_date: date = Query(..., description="Start searching from this date"),
    staff_id: UUID = Query(None, description="Optional staff member ID"),
    db: Session = Depends(get_db),
    current_tenant: Tenant = Depends(get_public_tenant)
):
    """
    Find the next available time slot for a service (public endpoint for booking widget)
    """
    slot = SchedulingService.find_next_available_slot(
        db=db,
        tenant=current_tenant,
        service_id=service_id,
        start_date=start_date,
        staff_id=staff_id
    )

    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No available slots found in the next 14 days"
        )

    return slot
