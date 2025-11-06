"""
No-Show Tracking Service
Sprint 4 - Automatic no-show detection and penalty system

Features:
- Automatic no-show detection after grace period
- Configurable no-show fees
- Escalating penalties for repeat offenders
- No-show history tracking
- Integration with reputation scoring
"""
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from sqlalchemy.orm import Session
from uuid import UUID
import uuid

from ..models.appointment import Appointment, AppointmentStatus
from ..models.owner import Owner
from ..models.tenant import Tenant
from ..models.payment import Payment, PaymentStatus, PaymentType
from ..integrations.twilio_service import TwilioService


class NoShowService:
    """Service for managing no-show detection and penalties"""

    # Configuration
    DEFAULT_GRACE_PERIOD_MINUTES = 15
    DEFAULT_NO_SHOW_FEE = 2500  # $25 in cents

    # Escalating penalties for repeat offenders
    PENALTY_SCHEDULE = {
        1: 2500,   # First no-show: $25
        2: 3500,   # Second no-show: $35
        3: 5000,   # Third no-show: $50
        4: 7500,   # Fourth+ no-show: $75
    }

    @staticmethod
    def detect_no_shows(
        db: Session,
        tenant_id: UUID,
        grace_period_minutes: int = DEFAULT_GRACE_PERIOD_MINUTES
    ) -> List[Appointment]:
        """
        Detect no-show appointments

        An appointment is considered a no-show if:
        - Status is CONFIRMED or PENDING
        - Scheduled start time + grace period has passed
        - No arrived_at timestamp

        Args:
            db: Database session
            tenant_id: Tenant ID
            grace_period_minutes: Grace period after scheduled time

        Returns:
            List of no-show appointments
        """
        cutoff_time = datetime.utcnow() - timedelta(minutes=grace_period_minutes)

        no_shows = db.query(Appointment).filter(
            Appointment.tenant_id == tenant_id,
            Appointment.status.in_([AppointmentStatus.CONFIRMED, AppointmentStatus.PENDING]),
            Appointment.scheduled_start < cutoff_time,
            Appointment.arrived_at.is_(None),
            Appointment.is_no_show == False,  # Not already marked
            Appointment.deleted_at.is_(None)
        ).all()

        return no_shows

    @staticmethod
    def mark_as_no_show(
        db: Session,
        appointment_id: UUID,
        apply_fee: bool = True
    ) -> Tuple[bool, Optional[str]]:
        """
        Mark an appointment as no-show

        Args:
            db: Database session
            appointment_id: Appointment ID
            apply_fee: Whether to apply no-show fee

        Returns:
            Tuple of (success, error_message)
        """
        try:
            appointment = db.query(Appointment).filter(
                Appointment.id == appointment_id
            ).first()

            if not appointment:
                return False, "Appointment not found"

            if appointment.is_no_show:
                return False, "Already marked as no-show"

            # Mark as no-show
            appointment.is_no_show = True
            appointment.status = AppointmentStatus.NO_SHOW

            # Apply fee if requested
            if apply_fee:
                owner = db.query(Owner).filter(Owner.id == appointment.owner_id).first()
                if owner:
                    # Calculate fee based on history
                    fee_amount = NoShowService.calculate_no_show_penalty(
                        db, appointment.owner_id
                    )

                    # Create no-show fee payment record
                    payment = Payment(
                        id=uuid.uuid4(),
                        tenant_id=appointment.tenant_id,
                        owner_id=appointment.owner_id,
                        appointment_id=appointment.id,
                        type=PaymentType.NO_SHOW_FEE,
                        method="pending",
                        status=PaymentStatus.PENDING,
                        amount=fee_amount,
                        net_amount=fee_amount,
                        description=f"No-show fee for appointment {appointment.id}"
                    )
                    db.add(payment)

                    appointment.no_show_fee_charged = fee_amount

                    # Update owner no-show count
                    owner.no_show_count = (owner.no_show_count or 0) + 1

                    # Send SMS notification
                    NoShowService.send_no_show_notification(db, appointment, fee_amount)

            db.commit()
            return True, None

        except Exception as e:
            db.rollback()
            return False, str(e)

    @staticmethod
    def calculate_no_show_penalty(
        db: Session,
        owner_id: UUID
    ) -> int:
        """
        Calculate no-show penalty based on history

        Uses escalating penalty schedule for repeat offenders

        Args:
            db: Database session
            owner_id: Owner ID

        Returns:
            Fee amount in cents
        """
        owner = db.query(Owner).filter(Owner.id == owner_id).first()
        if not owner:
            return NoShowService.DEFAULT_NO_SHOW_FEE

        no_show_count = owner.no_show_count or 0

        # Get fee from penalty schedule
        if no_show_count + 1 <= 3:
            fee = NoShowService.PENALTY_SCHEDULE[no_show_count + 1]
        else:
            fee = NoShowService.PENALTY_SCHEDULE[4]

        return fee

    @staticmethod
    def get_no_show_history(
        db: Session,
        owner_id: UUID
    ) -> Dict:
        """
        Get no-show history for a customer

        Args:
            db: Database session
            owner_id: Owner ID

        Returns:
            Dictionary with no-show statistics
        """
        owner = db.query(Owner).filter(Owner.id == owner_id).first()
        if not owner:
            return {"error": "Owner not found"}

        # Get all no-show appointments
        no_shows = db.query(Appointment).filter(
            Appointment.owner_id == owner_id,
            Appointment.is_no_show == True,
            Appointment.deleted_at.is_(None)
        ).order_by(Appointment.scheduled_start.desc()).all()

        # Calculate total fees
        total_fees = sum(appt.no_show_fee_charged or 0 for appt in no_shows)

        # Get unpaid fees
        unpaid_fees_query = db.query(Payment).filter(
            Payment.owner_id == owner_id,
            Payment.type == PaymentType.NO_SHOW_FEE,
            Payment.status.in_([PaymentStatus.PENDING, PaymentStatus.FAILED])
        )
        unpaid_fees = sum(p.amount for p in unpaid_fees_query.all())

        return {
            "owner_id": str(owner_id),
            "total_no_shows": len(no_shows),
            "total_fees_charged": total_fees,
            "unpaid_fees": unpaid_fees,
            "last_no_show": no_shows[0].scheduled_start.isoformat() if no_shows else None,
            "no_show_rate": NoShowService.calculate_no_show_rate(db, owner_id),
            "recent_no_shows": [
                {
                    "appointment_id": str(appt.id),
                    "scheduled_date": appt.scheduled_start.isoformat(),
                    "service": appt.service.name if hasattr(appt, 'service') and appt.service else None,
                    "fee_charged": appt.no_show_fee_charged or 0
                }
                for appt in no_shows[:5]  # Last 5 no-shows
            ]
        }

    @staticmethod
    def calculate_no_show_rate(
        db: Session,
        owner_id: UUID
    ) -> float:
        """
        Calculate no-show rate for a customer

        Args:
            db: Database session
            owner_id: Owner ID

        Returns:
            No-show rate as percentage (0-100)
        """
        total_appointments = db.query(Appointment).filter(
            Appointment.owner_id == owner_id,
            Appointment.deleted_at.is_(None)
        ).count()

        if total_appointments == 0:
            return 0.0

        no_shows = db.query(Appointment).filter(
            Appointment.owner_id == owner_id,
            Appointment.is_no_show == True,
            Appointment.deleted_at.is_(None)
        ).count()

        return round((no_shows / total_appointments) * 100, 2)

    @staticmethod
    def send_no_show_notification(
        db: Session,
        appointment: Appointment,
        fee_amount: int
    ) -> Optional[Dict]:
        """
        Send SMS notification about no-show

        Args:
            db: Database session
            appointment: Appointment that was no-show
            fee_amount: Fee charged in cents

        Returns:
            SMS result or None
        """
        owner = db.query(Owner).filter(Owner.id == appointment.owner_id).first()
        if not owner or not owner.sms_opted_in:
            return None

        # Format fee for display
        fee_display = f"${fee_amount / 100:.2f}"

        message = f"""
Hi {owner.first_name}, you missed your appointment on {appointment.scheduled_start.strftime('%B %d at %I:%M %p')}.

A no-show fee of {fee_display} has been applied to your account.

To avoid future fees, please cancel at least 24 hours in advance.
        """.strip()

        return TwilioService.send_sms(owner.phone, message)

    @staticmethod
    def process_daily_no_show_detection(
        db: Session,
        tenant_id: UUID
    ) -> Dict[str, int]:
        """
        Daily no-show detection task

        Should be run by scheduler once per day

        Args:
            db: Database session
            tenant_id: Tenant ID

        Returns:
            Summary of processing
        """
        no_shows = NoShowService.detect_no_shows(db, tenant_id)

        results = {
            "total_detected": len(no_shows),
            "fees_applied": 0,
            "notifications_sent": 0,
            "errors": 0
        }

        for appointment in no_shows:
            success, error = NoShowService.mark_as_no_show(db, appointment.id)

            if success:
                results["fees_applied"] += 1
                if appointment.owner.sms_opted_in if hasattr(appointment, 'owner') else False:
                    results["notifications_sent"] += 1
            else:
                results["errors"] += 1

        return results

    @staticmethod
    def waive_no_show_fee(
        db: Session,
        appointment_id: UUID,
        reason: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Waive a no-show fee (admin action)

        Args:
            db: Database session
            appointment_id: Appointment ID
            reason: Reason for waiving fee

        Returns:
            Tuple of (success, error_message)
        """
        try:
            appointment = db.query(Appointment).filter(
                Appointment.id == appointment_id
            ).first()

            if not appointment:
                return False, "Appointment not found"

            if not appointment.is_no_show:
                return False, "Appointment is not marked as no-show"

            # Find and cancel the no-show fee payment
            payment = db.query(Payment).filter(
                Payment.appointment_id == appointment_id,
                Payment.type == PaymentType.NO_SHOW_FEE
            ).first()

            if payment:
                payment.status = PaymentStatus.WAIVED
                payment.notes = f"Fee waived: {reason}"

            appointment.no_show_fee_charged = 0
            db.commit()

            return True, None

        except Exception as e:
            db.rollback()
            return False, str(e)

    @staticmethod
    def get_high_risk_customers(
        db: Session,
        tenant_id: UUID,
        min_no_shows: int = 2
    ) -> List[Dict]:
        """
        Get list of high-risk customers (multiple no-shows)

        Args:
            db: Database session
            tenant_id: Tenant ID
            min_no_shows: Minimum no-shows to be considered high risk

        Returns:
            List of high-risk customers
        """
        owners = db.query(Owner).filter(
            Owner.tenant_id == tenant_id,
            Owner.no_show_count >= min_no_shows,
            Owner.deleted_at.is_(None)
        ).all()

        result = []
        for owner in owners:
            no_show_rate = NoShowService.calculate_no_show_rate(db, owner.id)

            result.append({
                "owner_id": str(owner.id),
                "name": f"{owner.first_name} {owner.last_name}",
                "email": owner.email,
                "phone": owner.phone,
                "no_show_count": owner.no_show_count,
                "no_show_rate": no_show_rate,
                "reputation_score": owner.reputation_score if hasattr(owner, 'reputation_score') else None
            })

        # Sort by no-show count (highest first)
        result.sort(key=lambda x: x["no_show_count"], reverse=True)

        return result
