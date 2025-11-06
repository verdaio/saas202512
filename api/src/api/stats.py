"""
Stats API endpoints
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime
from typing import Optional

from ..db.base import get_db
from ..core.dependencies import get_current_user, get_current_tenant
from ..models.user import User
from ..models.tenant import Tenant
from ..models.appointment import Appointment, AppointmentStatus

router = APIRouter()


@router.get("/daily")
async def get_daily_stats(
    target_date: Optional[date] = Query(None, alias="date", description="Date to get stats for (default: today)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Get daily statistics for appointments
    """
    if not target_date:
        target_date = date.today()

    # Query appointments for the target date
    start_datetime = datetime.combine(target_date, datetime.min.time())
    end_datetime = datetime.combine(target_date, datetime.max.time())

    appointments = db.query(Appointment).filter(
        Appointment.tenant_id == current_tenant.id,
        Appointment.scheduled_start >= start_datetime,
        Appointment.scheduled_start <= end_datetime
    ).all()

    # Calculate stats
    total_appointments = len(appointments)
    completed = sum(1 for a in appointments if a.status == AppointmentStatus.COMPLETED)
    pending = sum(1 for a in appointments if a.status in [AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED])
    cancelled = sum(1 for a in appointments if a.status == AppointmentStatus.CANCELLED)
    no_shows = sum(1 for a in appointments if a.status == AppointmentStatus.NO_SHOW)

    # Calculate revenue (only from completed appointments)
    revenue = 0
    for appointment in appointments:
        if appointment.status == AppointmentStatus.COMPLETED and appointment.service:
            revenue += appointment.service.price

    return {
        "date": target_date.isoformat(),
        "total_appointments": total_appointments,
        "completed": completed,
        "pending": pending,
        "cancelled": cancelled,
        "no_shows": no_shows,
        "revenue": revenue
    }
