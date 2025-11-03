"""
Appointment API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from uuid import UUID
import uuid

from ..db.base import get_db
from ..core.dependencies import get_current_user, get_current_tenant, require_staff_or_admin
from ..models.user import User
from ..models.tenant import Tenant
from ..models.appointment import Appointment, AppointmentStatus
from ..models.owner import Owner
from ..models.service import Service
from ..schemas.appointment import AppointmentCreate, AppointmentUpdate, AppointmentResponse

router = APIRouter()


@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    appointment_data: AppointmentCreate,
    db: Session = Depends(get_db),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Create new appointment (public endpoint for booking widget)
    """
    # Verify owner exists
    owner = db.query(Owner).filter(
        Owner.id == appointment_data.owner_id,
        Owner.tenant_id == current_tenant.id
    ).first()

    if not owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Owner not found"
        )

    # Verify service exists
    service = db.query(Service).filter(
        Service.id == appointment_data.service_id,
        Service.tenant_id == current_tenant.id
    ).first()

    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )

    # TODO: Add scheduling validation (double-booking prevention, availability check)
    # This will be implemented in Sprint 2

    appointment = Appointment(
        id=uuid.uuid4(),
        tenant_id=current_tenant.id,
        status=AppointmentStatus.PENDING,
        source="online",
        total_amount=service.price,
        **appointment_data.model_dump()
    )

    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    return appointment


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

    # TODO: Add scheduling validation if time is changed

    # Update fields
    for field, value in appointment_data.model_dump(exclude_unset=True).items():
        setattr(appointment, field, value)

    db.commit()
    db.refresh(appointment)

    return appointment


@router.post("/{appointment_id}/cancel", response_model=AppointmentResponse)
async def cancel_appointment(
    appointment_id: UUID,
    db: Session = Depends(get_db),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Cancel appointment (public endpoint for booking widget)
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

    if appointment.status in [AppointmentStatus.COMPLETED, AppointmentStatus.CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel completed or already cancelled appointment"
        )

    appointment.status = AppointmentStatus.CANCELLED
    appointment.cancelled_at = datetime.utcnow()

    db.commit()
    db.refresh(appointment)

    return appointment


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
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id,
        Appointment.tenant_id == current_tenant.id
    ).first()

    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )

    appointment.status = AppointmentStatus.CONFIRMED
    appointment.confirmed_at = datetime.utcnow()

    db.commit()
    db.refresh(appointment)

    return appointment


@router.post("/{appointment_id}/complete", response_model=AppointmentResponse)
async def complete_appointment(
    appointment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_admin),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Mark appointment as completed (staff/admin/owner)
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

    appointment.status = AppointmentStatus.COMPLETED
    appointment.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(appointment)

    return appointment
