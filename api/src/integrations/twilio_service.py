"""
Twilio SMS integration service
Sprint 3 implementation
"""
from twilio.rest import Client
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from uuid import UUID
from sqlalchemy.orm import Session

from ..core.config import settings
from ..models.appointment import Appointment
from ..models.owner import Owner
from ..models.tenant import Tenant

# Initialize Twilio client
twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)


class TwilioService:
    """Twilio SMS notification service"""

    # SMS Templates
    TEMPLATES = {
        "appointment_confirmation": """
Hi {owner_name}! Your appointment for {pet_names} is confirmed for {date} at {time}.

Service: {service_name}
Location: {business_name}

Reply CANCEL to cancel.
        """.strip(),

        "appointment_reminder_24h": """
Reminder: {pet_names} has an appointment tomorrow at {time} with {business_name}.

Service: {service_name}
Address: {address}

Reply CONFIRM to confirm or CANCEL to cancel.
        """.strip(),

        "appointment_reminder_2h": """
Upcoming appointment in 2 hours! {pet_names} at {time}.

Service: {service_name}
{business_name}

See you soon!
        """.strip(),

        "appointment_cancelled": """
Your appointment for {pet_names} on {date} at {time} has been cancelled.

To reschedule, visit {booking_url}
        """.strip(),

        "appointment_rescheduled": """
Your appointment for {pet_names} has been rescheduled to {new_date} at {new_time}.

Service: {service_name}
{business_name}

Reply CONFIRM to acknowledge.
        """.strip(),

        "vaccination_expiring": """
Hi {owner_name}! {pet_name}'s {vaccination_type} vaccination expires in {days} days ({expiry_date}).

Please update vaccination records to continue booking appointments.
        """.strip(),

        "vaccination_expired": """
Hi {owner_name}! {pet_name}'s {vaccination_type} vaccination has expired.

Please update vaccination records before your next appointment.
        """.strip(),
    }

    @staticmethod
    def send_sms(
        to_phone: str,
        message: str,
        from_phone: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Send an SMS message
        Returns message SID and status
        """
        if not from_phone:
            from_phone = settings.TWILIO_PHONE_NUMBER

        message = twilio_client.messages.create(
            to=to_phone,
            from_=from_phone,
            body=message
        )

        return {
            "sid": message.sid,
            "status": message.status,
            "to": to_phone,
            "from": from_phone
        }

    @staticmethod
    def render_template(
        template_name: str,
        variables: Dict[str, str]
    ) -> str:
        """
        Render SMS template with variables
        """
        template = TwilioService.TEMPLATES.get(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' not found")

        return template.format(**variables)

    @staticmethod
    def send_appointment_confirmation(
        db: Session,
        appointment: Appointment
    ) -> Optional[Dict[str, any]]:
        """
        Send appointment confirmation SMS
        """
        # Get owner
        owner = db.query(Owner).filter(Owner.id == appointment.owner_id).first()
        if not owner or not owner.sms_opted_in:
            return None

        # Get tenant
        tenant = db.query(Tenant).filter(Tenant.id == appointment.tenant_id).first()
        if not tenant:
            return None

        # Get pet names
        pet_names = ", ".join([pet.name for pet in appointment.pets]) if hasattr(appointment, 'pets') else "your pet"

        # Render message
        message = TwilioService.render_template(
            "appointment_confirmation",
            {
                "owner_name": owner.first_name,
                "pet_names": pet_names,
                "date": appointment.scheduled_start.strftime("%B %d, %Y"),
                "time": appointment.scheduled_start.strftime("%I:%M %p"),
                "service_name": appointment.service.name if hasattr(appointment, 'service') else "service",
                "business_name": tenant.business_name
            }
        )

        # Send SMS
        return TwilioService.send_sms(owner.phone, message)

    @staticmethod
    def send_appointment_reminder_24h(
        db: Session,
        appointment: Appointment
    ) -> Optional[Dict[str, any]]:
        """
        Send 24-hour reminder SMS
        """
        # Get owner
        owner = db.query(Owner).filter(Owner.id == appointment.owner_id).first()
        if not owner or not owner.sms_opted_in:
            return None

        # Get tenant
        tenant = db.query(Tenant).filter(Tenant.id == appointment.tenant_id).first()
        if not tenant:
            return None

        # Get pet names
        pet_names = ", ".join([pet.name for pet in appointment.pets]) if hasattr(appointment, 'pets') else "your pet"

        # Render message
        message = TwilioService.render_template(
            "appointment_reminder_24h",
            {
                "pet_names": pet_names,
                "time": appointment.scheduled_start.strftime("%I:%M %p"),
                "business_name": tenant.business_name,
                "service_name": appointment.service.name if hasattr(appointment, 'service') else "service",
                "address": f"{tenant.address_line1}, {tenant.city}, {tenant.state}" if tenant.address_line1 else tenant.business_name
            }
        )

        # Send SMS
        return TwilioService.send_sms(owner.phone, message)

    @staticmethod
    def send_appointment_reminder_2h(
        db: Session,
        appointment: Appointment
    ) -> Optional[Dict[str, any]]:
        """
        Send 2-hour reminder SMS
        """
        # Get owner
        owner = db.query(Owner).filter(Owner.id == appointment.owner_id).first()
        if not owner or not owner.sms_opted_in:
            return None

        # Get tenant
        tenant = db.query(Tenant).filter(Tenant.id == appointment.tenant_id).first()
        if not tenant:
            return None

        # Get pet names
        pet_names = ", ".join([pet.name for pet in appointment.pets]) if hasattr(appointment, 'pets') else "your pet"

        # Render message
        message = TwilioService.render_template(
            "appointment_reminder_2h",
            {
                "pet_names": pet_names,
                "time": appointment.scheduled_start.strftime("%I:%M %p"),
                "business_name": tenant.business_name,
                "service_name": appointment.service.name if hasattr(appointment, 'service') else "service"
            }
        )

        # Send SMS
        return TwilioService.send_sms(owner.phone, message)

    @staticmethod
    def send_appointment_cancelled(
        db: Session,
        appointment: Appointment
    ) -> Optional[Dict[str, any]]:
        """
        Send appointment cancellation SMS
        """
        # Get owner
        owner = db.query(Owner).filter(Owner.id == appointment.owner_id).first()
        if not owner or not owner.sms_opted_in:
            return None

        # Get tenant
        tenant = db.query(Tenant).filter(Tenant.id == appointment.tenant_id).first()
        if not tenant:
            return None

        # Get pet names
        pet_names = ", ".join([pet.name for pet in appointment.pets]) if hasattr(appointment, 'pets') else "your pet"

        # Render message
        message = TwilioService.render_template(
            "appointment_cancelled",
            {
                "pet_names": pet_names,
                "date": appointment.scheduled_start.strftime("%B %d, %Y"),
                "time": appointment.scheduled_start.strftime("%I:%M %p"),
                "booking_url": f"https://{tenant.subdomain}.yourdomain.com"
            }
        )

        # Send SMS
        return TwilioService.send_sms(owner.phone, message)

    @staticmethod
    def send_vaccination_reminder(
        db: Session,
        owner: Owner,
        pet_name: str,
        vaccination_type: str,
        expiry_date: datetime,
        days_until_expiry: int
    ) -> Optional[Dict[str, any]]:
        """
        Send vaccination expiration reminder
        """
        if not owner.sms_opted_in:
            return None

        # Choose template based on whether expired
        if days_until_expiry < 0:
            template_name = "vaccination_expired"
        else:
            template_name = "vaccination_expiring"

        # Render message
        message = TwilioService.render_template(
            template_name,
            {
                "owner_name": owner.first_name,
                "pet_name": pet_name,
                "vaccination_type": vaccination_type,
                "days": abs(days_until_expiry),
                "expiry_date": expiry_date.strftime("%B %d, %Y")
            }
        )

        # Send SMS
        return TwilioService.send_sms(owner.phone, message)

    @staticmethod
    def get_appointments_needing_reminders(
        db: Session,
        hours_ahead: int = 24
    ) -> List[Appointment]:
        """
        Get appointments that need reminders
        Returns appointments scheduled in X hours
        """
        from ..models.appointment import AppointmentStatus

        target_time = datetime.utcnow() + timedelta(hours=hours_ahead)
        time_window_start = target_time - timedelta(minutes=30)
        time_window_end = target_time + timedelta(minutes=30)

        appointments = db.query(Appointment).filter(
            Appointment.status == AppointmentStatus.CONFIRMED,
            Appointment.scheduled_start >= time_window_start,
            Appointment.scheduled_start <= time_window_end
        ).all()

        return appointments

    @staticmethod
    def send_batch_reminders(
        db: Session,
        hours_ahead: int = 24
    ) -> Dict[str, int]:
        """
        Send reminder SMS to all appointments in X hours
        Returns count of sent messages
        """
        appointments = TwilioService.get_appointments_needing_reminders(db, hours_ahead)

        sent_count = 0
        failed_count = 0

        for appointment in appointments:
            try:
                if hours_ahead == 24:
                    result = TwilioService.send_appointment_reminder_24h(db, appointment)
                elif hours_ahead == 2:
                    result = TwilioService.send_appointment_reminder_2h(db, appointment)
                else:
                    continue

                if result:
                    sent_count += 1
            except Exception as e:
                failed_count += 1
                print(f"Failed to send reminder for appointment {appointment.id}: {e}")

        return {
            "sent": sent_count,
            "failed": failed_count,
            "total": len(appointments)
        }
