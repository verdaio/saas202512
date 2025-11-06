"""
Reporting Service
Sprint 6 - Business intelligence and reporting

Features:
- Revenue reports (daily, weekly, monthly)
- Appointment analytics
- Customer insights
- Staff performance metrics
- Export functionality (CSV, PDF, Excel)
"""
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from uuid import UUID
from decimal import Decimal

from ..models.appointment import Appointment, AppointmentStatus
from ..models.payment import Payment, PaymentStatus
from ..models.owner import Owner
from ..models.staff import Staff
from ..models.service import Service
from ..models.tenant import Tenant


class ReportingService:
    """Service for generating business reports and analytics"""

    # ==================== REVENUE REPORTS ====================

    @staticmethod
    def get_revenue_report(
        db: Session,
        tenant_id: UUID,
        start_date: date,
        end_date: date,
        group_by: str = "day"
    ) -> Dict:
        """
        Get revenue report for a date range

        Args:
            db: Database session
            tenant_id: Tenant ID
            start_date: Report start date
            end_date: Report end date
            group_by: Grouping (day, week, month)

        Returns:
            Revenue report dictionary
        """
        # Get successful payments in date range
        payments = db.query(Payment).filter(
            Payment.tenant_id == tenant_id,
            Payment.status.in_([PaymentStatus.SUCCEEDED, PaymentStatus.COMPLETED]),
            func.date(Payment.created_at) >= start_date,
            func.date(Payment.created_at) <= end_date
        ).all()

        total_revenue = sum(p.amount for p in payments)
        total_refunds = sum(p.refund_amount or 0 for p in payments)
        net_revenue = total_revenue - total_refunds

        # Group by period
        revenue_by_period = {}
        for payment in payments:
            period_key = ReportingService._get_period_key(
                payment.created_at, group_by
            )
            if period_key not in revenue_by_period:
                revenue_by_period[period_key] = 0
            revenue_by_period[period_key] += payment.amount

        return {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_revenue": total_revenue,
            "total_refunds": total_refunds,
            "net_revenue": net_revenue,
            "payment_count": len(payments),
            "average_transaction": total_revenue // len(payments) if payments else 0,
            "revenue_by_period": revenue_by_period
        }

    @staticmethod
    def get_revenue_by_service(
        db: Session,
        tenant_id: UUID,
        start_date: date,
        end_date: date
    ) -> List[Dict]:
        """
        Get revenue breakdown by service type

        Returns list of services with revenue
        """
        results = db.query(
            Service.id,
            Service.name,
            func.count(Appointment.id).label('appointment_count'),
            func.sum(Payment.amount).label('total_revenue')
        ).join(
            Appointment, Appointment.service_id == Service.id
        ).join(
            Payment, Payment.appointment_id == Appointment.id
        ).filter(
            Service.tenant_id == tenant_id,
            Payment.status.in_([PaymentStatus.SUCCEEDED, PaymentStatus.COMPLETED]),
            func.date(Payment.created_at) >= start_date,
            func.date(Payment.created_at) <= end_date
        ).group_by(Service.id, Service.name).all()

        return [
            {
                "service_id": str(r.id),
                "service_name": r.name,
                "appointment_count": r.appointment_count,
                "total_revenue": r.total_revenue or 0
            }
            for r in results
        ]

    @staticmethod
    def get_payment_method_breakdown(
        db: Session,
        tenant_id: UUID,
        start_date: date,
        end_date: date
    ) -> Dict:
        """
        Get revenue breakdown by payment method

        Returns dictionary of payment methods and amounts
        """
        results = db.query(
            Payment.method,
            func.count(Payment.id).label('count'),
            func.sum(Payment.amount).label('total')
        ).filter(
            Payment.tenant_id == tenant_id,
            Payment.status.in_([PaymentStatus.SUCCEEDED, PaymentStatus.COMPLETED]),
            func.date(Payment.created_at) >= start_date,
            func.date(Payment.created_at) <= end_date
        ).group_by(Payment.method).all()

        return {
            r.method: {
                "count": r.count,
                "total_amount": r.total or 0
            }
            for r in results
        }

    # ==================== APPOINTMENT REPORTS ====================

    @staticmethod
    def get_appointment_volume_report(
        db: Session,
        tenant_id: UUID,
        start_date: date,
        end_date: date
    ) -> Dict:
        """
        Get appointment volume trends

        Returns appointment statistics
        """
        appointments = db.query(Appointment).filter(
            Appointment.tenant_id == tenant_id,
            func.date(Appointment.scheduled_start) >= start_date,
            func.date(Appointment.scheduled_start) <= end_date,
            Appointment.deleted_at.is_(None)
        ).all()

        # Count by status
        status_counts = {}
        for appt in appointments:
            status = appt.status.value if hasattr(appt.status, 'value') else str(appt.status)
            status_counts[status] = status_counts.get(status, 0) + 1

        # Calculate rates
        total = len(appointments)
        completed = status_counts.get('completed', 0)
        cancelled = status_counts.get('cancelled', 0)
        no_shows = status_counts.get('no_show', 0)

        return {
            "total_appointments": total,
            "by_status": status_counts,
            "completion_rate": round((completed / total * 100), 2) if total > 0 else 0,
            "cancellation_rate": round((cancelled / total * 100), 2) if total > 0 else 0,
            "no_show_rate": round((no_shows / total * 100), 2) if total > 0 else 0
        }

    @staticmethod
    def get_peak_times_analysis(
        db: Session,
        tenant_id: UUID,
        start_date: date,
        end_date: date
    ) -> Dict:
        """
        Analyze peak booking times

        Returns dictionary with peak hours and days
        """
        appointments = db.query(Appointment).filter(
            Appointment.tenant_id == tenant_id,
            func.date(Appointment.scheduled_start) >= start_date,
            func.date(Appointment.scheduled_start) <= end_date,
            Appointment.deleted_at.is_(None)
        ).all()

        # Count by hour
        by_hour = {}
        by_day = {}

        for appt in appointments:
            hour = appt.scheduled_start.hour
            day = appt.scheduled_start.strftime("%A")

            by_hour[hour] = by_hour.get(hour, 0) + 1
            by_day[day] = by_day.get(day, 0) + 1

        # Find peaks
        peak_hour = max(by_hour.items(), key=lambda x: x[1]) if by_hour else None
        peak_day = max(by_day.items(), key=lambda x: x[1]) if by_day else None

        return {
            "by_hour": by_hour,
            "by_day": by_day,
            "peak_hour": f"{peak_hour[0]}:00" if peak_hour else None,
            "peak_day": peak_day[0] if peak_day else None
        }

    # ==================== CUSTOMER REPORTS ====================

    @staticmethod
    def get_customer_lifetime_value(
        db: Session,
        owner_id: UUID
    ) -> Decimal:
        """
        Calculate customer lifetime value

        Returns total revenue from customer
        """
        total = db.query(func.sum(Payment.amount)).filter(
            Payment.owner_id == owner_id,
            Payment.status.in_([PaymentStatus.SUCCEEDED, PaymentStatus.COMPLETED])
        ).scalar()

        return Decimal(total or 0) / 100  # Convert cents to dollars

    @staticmethod
    def get_top_customers(
        db: Session,
        tenant_id: UUID,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get top customers by revenue

        Returns list of top customers
        """
        results = db.query(
            Owner.id,
            Owner.first_name,
            Owner.last_name,
            Owner.email,
            func.sum(Payment.amount).label('total_spent'),
            func.count(Appointment.id).label('appointment_count')
        ).join(
            Appointment, Appointment.owner_id == Owner.id
        ).join(
            Payment, Payment.owner_id == Owner.id
        ).filter(
            Owner.tenant_id == tenant_id,
            Payment.status.in_([PaymentStatus.SUCCEEDED, PaymentStatus.COMPLETED])
        ).group_by(
            Owner.id, Owner.first_name, Owner.last_name, Owner.email
        ).order_by(
            func.sum(Payment.amount).desc()
        ).limit(limit).all()

        return [
            {
                "owner_id": str(r.id),
                "name": f"{r.first_name} {r.last_name}",
                "email": r.email,
                "total_spent": r.total_spent or 0,
                "appointment_count": r.appointment_count,
                "average_transaction": (r.total_spent // r.appointment_count) if r.appointment_count > 0 else 0
            }
            for r in results
        ]

    @staticmethod
    def get_customer_retention_report(
        db: Session,
        tenant_id: UUID,
        start_date: date,
        end_date: date
    ) -> Dict:
        """
        Calculate customer retention metrics

        Returns retention statistics
        """
        # New customers in period
        new_customers = db.query(Owner).filter(
            Owner.tenant_id == tenant_id,
            func.date(Owner.created_at) >= start_date,
            func.date(Owner.created_at) <= end_date
        ).count()

        # Repeat customers (> 1 appointment)
        repeat_customers = db.query(Owner.id).join(
            Appointment
        ).filter(
            Owner.tenant_id == tenant_id,
            Appointment.deleted_at.is_(None)
        ).group_by(Owner.id).having(
            func.count(Appointment.id) > 1
        ).count()

        # Total customers
        total_customers = db.query(Owner).filter(
            Owner.tenant_id == tenant_id,
            Owner.deleted_at.is_(None)
        ).count()

        return {
            "new_customers": new_customers,
            "repeat_customers": repeat_customers,
            "total_customers": total_customers,
            "repeat_rate": round((repeat_customers / total_customers * 100), 2) if total_customers > 0 else 0
        }

    # ==================== STAFF REPORTS ====================

    @staticmethod
    def get_staff_performance(
        db: Session,
        staff_id: UUID,
        start_date: date,
        end_date: date
    ) -> Dict:
        """
        Get performance metrics for a staff member

        Returns performance statistics
        """
        appointments = db.query(Appointment).filter(
            Appointment.staff_id == staff_id,
            func.date(Appointment.scheduled_start) >= start_date,
            func.date(Appointment.scheduled_start) <= end_date,
            Appointment.deleted_at.is_(None)
        ).all()

        completed = len([a for a in appointments if a.status == AppointmentStatus.COMPLETED])
        total = len(appointments)

        # Calculate revenue
        revenue = db.query(func.sum(Payment.amount)).join(
            Appointment
        ).filter(
            Appointment.staff_id == staff_id,
            func.date(Appointment.scheduled_start) >= start_date,
            func.date(Appointment.scheduled_start) <= end_date,
            Payment.status.in_([PaymentStatus.SUCCEEDED, PaymentStatus.COMPLETED])
        ).scalar() or 0

        return {
            "staff_id": str(staff_id),
            "total_appointments": total,
            "completed_appointments": completed,
            "completion_rate": round((completed / total * 100), 2) if total > 0 else 0,
            "total_revenue": revenue,
            "average_revenue_per_appointment": revenue // total if total > 0 else 0
        }

    # ==================== HELPER METHODS ====================

    @staticmethod
    def _get_period_key(dt: datetime, group_by: str) -> str:
        """Get period key for grouping"""
        if group_by == "day":
            return dt.strftime("%Y-%m-%d")
        elif group_by == "week":
            return dt.strftime("%Y-W%U")
        elif group_by == "month":
            return dt.strftime("%Y-%m")
        else:
            return dt.strftime("%Y-%m-%d")
