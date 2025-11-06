"""
Appointment Reminder Task
Sprint 3/4 - Hourly task to send appointment reminders

Usage:
    python -m src.tasks.appointment_reminders
    or
    python src/tasks/appointment_reminders.py
"""
import sys
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from ..db.session import SessionLocal
from ..models.tenant import Tenant
from ..models.appointment import Appointment, AppointmentStatus
from ..models.owner import Owner
from ..integrations.twilio_service import TwilioService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def send_24_hour_reminders(db: Session) -> dict:
    """
    Send reminders for appointments in 24 hours

    Returns:
        Summary of reminders sent
    """
    logger.info("Sending 24-hour appointment reminders")

    results = {
        "total_checked": 0,
        "reminders_sent": 0,
        "skipped": 0,
        "errors": 0
    }

    # Get all active tenants
    tenants = db.query(Tenant).filter(
        Tenant.is_active == True,
        Tenant.deleted_at.is_(None)
    ).all()

    for tenant in tenants:
        # Get appointments starting in 23-25 hours (1-hour window)
        window_start = datetime.utcnow() + timedelta(hours=23)
        window_end = datetime.utcnow() + timedelta(hours=25)

        appointments = db.query(Appointment).filter(
            Appointment.tenant_id == tenant.id,
            Appointment.status.in_([AppointmentStatus.CONFIRMED, AppointmentStatus.PENDING]),
            Appointment.scheduled_start >= window_start,
            Appointment.scheduled_start < window_end,
            Appointment.deleted_at.is_(None)
        ).all()

        results["total_checked"] += len(appointments)

        for appointment in appointments:
            try:
                # Get owner
                owner = db.query(Owner).filter(Owner.id == appointment.owner_id).first()

                if not owner or not owner.sms_opted_in:
                    results["skipped"] += 1
                    continue

                # Send 24-hour reminder
                TwilioService.send_24_hour_reminder(db, appointment)

                results["reminders_sent"] += 1
                logger.info(f"Sent 24h reminder for appointment {appointment.id}")

            except Exception as e:
                results["errors"] += 1
                logger.error(f"Error sending 24h reminder for appointment {appointment.id}: {e}")

    return results


def send_2_hour_reminders(db: Session) -> dict:
    """
    Send reminders for appointments in 2 hours

    Returns:
        Summary of reminders sent
    """
    logger.info("Sending 2-hour appointment reminders")

    results = {
        "total_checked": 0,
        "reminders_sent": 0,
        "skipped": 0,
        "errors": 0
    }

    # Get all active tenants
    tenants = db.query(Tenant).filter(
        Tenant.is_active == True,
        Tenant.deleted_at.is_(None)
    ).all()

    for tenant in tenants:
        # Get appointments starting in 1.5-2.5 hours (1-hour window)
        window_start = datetime.utcnow() + timedelta(hours=1.5)
        window_end = datetime.utcnow() + timedelta(hours=2.5)

        appointments = db.query(Appointment).filter(
            Appointment.tenant_id == tenant.id,
            Appointment.status.in_([AppointmentStatus.CONFIRMED, AppointmentStatus.PENDING]),
            Appointment.scheduled_start >= window_start,
            Appointment.scheduled_start < window_end,
            Appointment.deleted_at.is_(None)
        ).all()

        results["total_checked"] += len(appointments)

        for appointment in appointments:
            try:
                # Get owner
                owner = db.query(Owner).filter(Owner.id == appointment.owner_id).first()

                if not owner or not owner.sms_opted_in:
                    results["skipped"] += 1
                    continue

                # Send 2-hour reminder
                TwilioService.send_2_hour_reminder(db, appointment)

                results["reminders_sent"] += 1
                logger.info(f"Sent 2h reminder for appointment {appointment.id}")

            except Exception as e:
                results["errors"] += 1
                logger.error(f"Error sending 2h reminder for appointment {appointment.id}: {e}")

    return results


def main():
    """Main entry point for appointment reminders task"""
    logger.info("=" * 80)
    logger.info(f"Appointment Reminders Task - Started at {datetime.utcnow()}")
    logger.info("=" * 80)

    db = SessionLocal()
    try:
        # Send both 24-hour and 2-hour reminders
        results_24h = send_24_hour_reminders(db)
        results_2h = send_2_hour_reminders(db)

        logger.info("=" * 80)
        logger.info("Task completed successfully")
        logger.info(f"24h reminders: {results_24h['reminders_sent']} sent, "
                   f"{results_24h['skipped']} skipped, {results_24h['errors']} errors")
        logger.info(f"2h reminders: {results_2h['reminders_sent']} sent, "
                   f"{results_2h['skipped']} skipped, {results_2h['errors']} errors")
        logger.info("=" * 80)

        total_errors = results_24h['errors'] + results_2h['errors']
        return 0 if total_errors == 0 else 1

    except Exception as e:
        logger.error(f"Error in appointment reminders task: {e}", exc_info=True)
        db.rollback()
        return 1

    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
