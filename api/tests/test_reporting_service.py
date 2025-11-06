"""
Tests for Reporting Service
Sprint 6 - Business intelligence and reporting
"""
import pytest
from datetime import datetime, date, timedelta
from uuid import uuid4
from decimal import Decimal
from sqlalchemy.orm import Session

from src.models.payment import Payment, PaymentStatus
from src.models.appointment import Appointment, AppointmentStatus
from src.models.owner import Owner
from src.models.staff import Staff
from src.models.service import Service
from src.models.tenant import Tenant
from src.services.reporting_service import ReportingService


@pytest.fixture
def tenant(db: Session):
    """Create test tenant"""
    tenant = Tenant(
        id=uuid4(),
        name="Test Clinic",
        subdomain="testclinic",
        is_active=True
    )
    db.add(tenant)
    db.commit()
    return tenant


@pytest.fixture
def owner(db: Session, tenant):
    """Create test owner"""
    owner = Owner(
        id=uuid4(),
        tenant_id=tenant.id,
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="+1234567890"
    )
    db.add(owner)
    db.commit()
    return owner


@pytest.fixture
def staff(db: Session, tenant):
    """Create test staff member"""
    staff = Staff(
        id=uuid4(),
        tenant_id=tenant.id,
        first_name="Jane",
        last_name="Smith",
        email="jane@clinic.com",
        role="groomer"
    )
    db.add(staff)
    db.commit()
    return staff


@pytest.fixture
def service(db: Session, tenant):
    """Create test service"""
    service = Service(
        id=uuid4(),
        tenant_id=tenant.id,
        name="Dog Grooming",
        duration_minutes=60,
        price=5000  # $50
    )
    db.add(service)
    db.commit()
    return service


@pytest.fixture
def payments_last_week(db: Session, tenant, owner):
    """Create payments from last week"""
    payments = []
    for i in range(5):
        payment = Payment(
            id=uuid4(),
            tenant_id=tenant.id,
            owner_id=owner.id,
            amount=5000 + (i * 1000),  # $50, $60, $70, $80, $90
            status=PaymentStatus.SUCCEEDED,
            method="card",
            created_at=datetime.utcnow() - timedelta(days=7-i)
        )
        payments.append(payment)
        db.add(payment)
    db.commit()
    return payments


class TestGetRevenueReport:
    """Test revenue report generation"""

    def test_revenue_report_basic(self, db, tenant, payments_last_week):
        """Test basic revenue report"""
        start_date = (datetime.utcnow() - timedelta(days=7)).date()
        end_date = datetime.utcnow().date()

        report = ReportingService.get_revenue_report(
            db=db,
            tenant_id=tenant.id,
            start_date=start_date,
            end_date=end_date,
            group_by="day"
        )

        assert report["total_revenue"] == 35000  # $50+$60+$70+$80+$90 = $350
        assert report["payment_count"] == 5
        assert report["net_revenue"] == 35000  # No refunds

    def test_revenue_report_with_refunds(self, db, tenant, owner):
        """Test revenue report with refunds"""
        # Create payment with refund
        payment = Payment(
            id=uuid4(),
            tenant_id=tenant.id,
            owner_id=owner.id,
            amount=10000,
            refund_amount=2000,
            status=PaymentStatus.PARTIALLY_REFUNDED,
            method="card",
            created_at=datetime.utcnow()
        )
        db.add(payment)
        db.commit()

        today = date.today()
        report = ReportingService.get_revenue_report(
            db=db,
            tenant_id=tenant.id,
            start_date=today,
            end_date=today,
            group_by="day"
        )

        assert report["total_revenue"] == 10000
        assert report["total_refunds"] == 2000
        assert report["net_revenue"] == 8000

    def test_revenue_report_only_successful_payments(self, db, tenant, owner):
        """Test report only includes successful/completed payments"""
        # Create payments with different statuses
        Payment(
            id=uuid4(), tenant_id=tenant.id, owner_id=owner.id,
            amount=5000, status=PaymentStatus.SUCCEEDED, method="card",
            created_at=datetime.utcnow()
        )
        Payment(
            id=uuid4(), tenant_id=tenant.id, owner_id=owner.id,
            amount=5000, status=PaymentStatus.PENDING, method="card",
            created_at=datetime.utcnow()
        )
        Payment(
            id=uuid4(), tenant_id=tenant.id, owner_id=owner.id,
            amount=5000, status=PaymentStatus.FAILED, method="card",
            created_at=datetime.utcnow()
        )
        db.commit()

        today = date.today()
        report = ReportingService.get_revenue_report(
            db=db,
            tenant_id=tenant.id,
            start_date=today,
            end_date=today,
            group_by="day"
        )

        assert report["total_revenue"] == 5000  # Only succeeded payment
        assert report["payment_count"] == 1

    def test_revenue_by_period_grouping(self, db, tenant, owner):
        """Test revenue grouping by different periods"""
        # Create payments over 3 days
        for i in range(3):
            Payment(
                id=uuid4(), tenant_id=tenant.id, owner_id=owner.id,
                amount=5000, status=PaymentStatus.SUCCEEDED, method="card",
                created_at=datetime.utcnow() - timedelta(days=i)
            )
        db.commit()

        start_date = (datetime.utcnow() - timedelta(days=3)).date()
        end_date = datetime.utcnow().date()

        report = ReportingService.get_revenue_report(
            db=db,
            tenant_id=tenant.id,
            start_date=start_date,
            end_date=end_date,
            group_by="day"
        )

        assert len(report["revenue_by_period"]) == 3


class TestGetRevenueByService:
    """Test revenue breakdown by service"""

    def test_revenue_by_service(self, db, tenant, owner, staff, service):
        """Test revenue breakdown by service type"""
        # Create second service
        service2 = Service(
            id=uuid4(), tenant_id=tenant.id, name="Dog Walking",
            duration_minutes=30, price=3000
        )
        db.add(service2)
        db.commit()

        # Create appointments and payments
        for svc, count in [(service, 3), (service2, 2)]:
            for i in range(count):
                appt = Appointment(
                    id=uuid4(), tenant_id=tenant.id, owner_id=owner.id,
                    staff_id=staff.id, service_id=svc.id,
                    status=AppointmentStatus.COMPLETED,
                    scheduled_start=datetime.utcnow(),
                    scheduled_end=datetime.utcnow() + timedelta(hours=1)
                )
                db.add(appt)
                db.commit()

                payment = Payment(
                    id=uuid4(), tenant_id=tenant.id, owner_id=owner.id,
                    appointment_id=appt.id, amount=svc.price,
                    status=PaymentStatus.SUCCEEDED, method="card",
                    created_at=datetime.utcnow()
                )
                db.add(payment)
        db.commit()

        today = date.today()
        report = ReportingService.get_revenue_by_service(
            db=db,
            tenant_id=tenant.id,
            start_date=today,
            end_date=today
        )

        assert len(report) == 2
        # Find grooming service
        grooming = next(r for r in report if r["service_name"] == "Dog Grooming")
        assert grooming["appointment_count"] == 3
        assert grooming["total_revenue"] == 15000  # 3 x $50


class TestGetPaymentMethodBreakdown:
    """Test payment method breakdown"""

    def test_payment_method_breakdown(self, db, tenant, owner):
        """Test breakdown of revenue by payment method"""
        # Create payments with different methods
        methods = [("card", 3), ("cash", 2), ("check", 1)]
        for method, count in methods:
            for _ in range(count):
                payment = Payment(
                    id=uuid4(), tenant_id=tenant.id, owner_id=owner.id,
                    amount=5000, status=PaymentStatus.SUCCEEDED, method=method,
                    created_at=datetime.utcnow()
                )
                db.add(payment)
        db.commit()

        today = date.today()
        breakdown = ReportingService.get_payment_method_breakdown(
            db=db,
            tenant_id=tenant.id,
            start_date=today,
            end_date=today
        )

        assert breakdown["card"]["count"] == 3
        assert breakdown["card"]["total_amount"] == 15000
        assert breakdown["cash"]["count"] == 2
        assert breakdown["cash"]["total_amount"] == 10000
        assert breakdown["check"]["count"] == 1
        assert breakdown["check"]["total_amount"] == 5000


class TestGetAppointmentVolumeReport:
    """Test appointment volume reporting"""

    def test_appointment_volume_report(self, db, tenant, owner, staff, service):
        """Test appointment volume and status breakdown"""
        # Create appointments with different statuses
        statuses = [
            (AppointmentStatus.COMPLETED, 7),
            (AppointmentStatus.CANCELLED, 2),
            (AppointmentStatus.NO_SHOW, 1)
        ]

        for status, count in statuses:
            for _ in range(count):
                appt = Appointment(
                    id=uuid4(), tenant_id=tenant.id, owner_id=owner.id,
                    staff_id=staff.id, service_id=service.id, status=status,
                    scheduled_start=datetime.utcnow(),
                    scheduled_end=datetime.utcnow() + timedelta(hours=1),
                    is_no_show=(status == AppointmentStatus.NO_SHOW)
                )
                db.add(appt)
        db.commit()

        today = date.today()
        report = ReportingService.get_appointment_volume_report(
            db=db,
            tenant_id=tenant.id,
            start_date=today,
            end_date=today
        )

        assert report["total_appointments"] == 10
        assert report["by_status"]["completed"] == 7
        assert report["by_status"]["cancelled"] == 2
        assert report["by_status"]["no_show"] == 1
        assert report["completion_rate"] == 70.0
        assert report["cancellation_rate"] == 20.0
        assert report["no_show_rate"] == 10.0


class TestGetPeakTimesAnalysis:
    """Test peak times analysis"""

    def test_peak_times_analysis(self, db, tenant, owner, staff, service):
        """Test analysis of peak booking times"""
        # Create appointments at different hours
        hours = [9, 9, 10, 10, 10, 14, 14, 15]  # Peak at 10 AM

        for hour in hours:
            scheduled = datetime.utcnow().replace(hour=hour, minute=0)
            appt = Appointment(
                id=uuid4(), tenant_id=tenant.id, owner_id=owner.id,
                staff_id=staff.id, service_id=service.id,
                status=AppointmentStatus.COMPLETED,
                scheduled_start=scheduled,
                scheduled_end=scheduled + timedelta(hours=1)
            )
            db.add(appt)
        db.commit()

        today = date.today()
        analysis = ReportingService.get_peak_times_analysis(
            db=db,
            tenant_id=tenant.id,
            start_date=today,
            end_date=today
        )

        assert analysis["by_hour"][9] == 2
        assert analysis["by_hour"][10] == 3
        assert analysis["peak_hour"] == "10:00"

    def test_peak_day_analysis(self, db, tenant, owner, staff, service):
        """Test peak day of week analysis"""
        # Create appointments on different days
        for days_ago in range(7):
            scheduled = datetime.utcnow() - timedelta(days=days_ago)
            # Create 2 appointments on day 0, 1 on others
            count = 2 if days_ago == 0 else 1
            for _ in range(count):
                appt = Appointment(
                    id=uuid4(), tenant_id=tenant.id, owner_id=owner.id,
                    staff_id=staff.id, service_id=service.id,
                    status=AppointmentStatus.COMPLETED,
                    scheduled_start=scheduled,
                    scheduled_end=scheduled + timedelta(hours=1)
                )
                db.add(appt)
        db.commit()

        start_date = (datetime.utcnow() - timedelta(days=7)).date()
        end_date = datetime.utcnow().date()

        analysis = ReportingService.get_peak_times_analysis(
            db=db,
            tenant_id=tenant.id,
            start_date=start_date,
            end_date=end_date
        )

        peak_day = datetime.utcnow().strftime("%A")
        assert analysis["peak_day"] == peak_day


class TestGetCustomerLifetimeValue:
    """Test customer lifetime value calculation"""

    def test_customer_lifetime_value(self, db, owner):
        """Test CLV calculation for a customer"""
        # Create payments totaling $150
        for i in range(3):
            payment = Payment(
                id=uuid4(), tenant_id=owner.tenant_id, owner_id=owner.id,
                amount=5000, status=PaymentStatus.SUCCEEDED, method="card",
                created_at=datetime.utcnow() - timedelta(days=i*30)
            )
            db.add(payment)
        db.commit()

        clv = ReportingService.get_customer_lifetime_value(db=db, owner_id=owner.id)

        assert clv == Decimal('150.00')  # $150 total

    def test_customer_lifetime_value_only_successful(self, db, owner):
        """Test CLV only includes successful payments"""
        # Successful payment
        Payment(
            id=uuid4(), tenant_id=owner.tenant_id, owner_id=owner.id,
            amount=5000, status=PaymentStatus.SUCCEEDED, method="card"
        )
        # Failed payment (should not count)
        Payment(
            id=uuid4(), tenant_id=owner.tenant_id, owner_id=owner.id,
            amount=5000, status=PaymentStatus.FAILED, method="card"
        )
        db.commit()

        clv = ReportingService.get_customer_lifetime_value(db=db, owner_id=owner.id)

        assert clv == Decimal('50.00')  # Only successful payment


class TestGetTopCustomers:
    """Test top customers report"""

    def test_get_top_customers(self, db, tenant):
        """Test getting top customers by revenue"""
        # Create 5 customers with different spend
        for i in range(5):
            owner = Owner(
                id=uuid4(), tenant_id=tenant.id,
                first_name=f"Customer{i}", last_name="Test",
                email=f"customer{i}@test.com", phone=f"+123456789{i}"
            )
            db.add(owner)
            db.commit()

            # Create appointments
            appt = Appointment(
                id=uuid4(), tenant_id=tenant.id, owner_id=owner.id,
                scheduled_start=datetime.utcnow(),
                scheduled_end=datetime.utcnow() + timedelta(hours=1),
                status=AppointmentStatus.COMPLETED
            )
            db.add(appt)
            db.commit()

            # Create payments (increasing amounts)
            payment = Payment(
                id=uuid4(), tenant_id=tenant.id, owner_id=owner.id,
                amount=(i+1) * 5000,  # $50, $100, $150, $200, $250
                status=PaymentStatus.SUCCEEDED, method="card"
            )
            db.add(payment)
        db.commit()

        top_customers = ReportingService.get_top_customers(
            db=db,
            tenant_id=tenant.id,
            limit=3
        )

        assert len(top_customers) == 3
        # Should be sorted by total spent (descending)
        assert top_customers[0]["total_spent"] == 25000  # $250
        assert top_customers[1]["total_spent"] == 20000  # $200
        assert top_customers[2]["total_spent"] == 15000  # $150


class TestGetCustomerRetentionReport:
    """Test customer retention reporting"""

    def test_customer_retention_report(self, db, tenant):
        """Test retention metrics calculation"""
        # Create new customers in date range
        for i in range(3):
            owner = Owner(
                id=uuid4(), tenant_id=tenant.id,
                first_name=f"New{i}", last_name="Customer",
                email=f"new{i}@test.com", phone=f"+111111111{i}",
                created_at=datetime.utcnow()
            )
            db.add(owner)
        db.commit()

        # Create repeat customer (2 appointments)
        repeat_owner = Owner(
            id=uuid4(), tenant_id=tenant.id,
            first_name="Repeat", last_name="Customer",
            email="repeat@test.com", phone="+9999999999",
            created_at=datetime.utcnow() - timedelta(days=30)
        )
        db.add(repeat_owner)
        db.commit()

        for _ in range(2):
            appt = Appointment(
                id=uuid4(), tenant_id=tenant.id, owner_id=repeat_owner.id,
                scheduled_start=datetime.utcnow(),
                scheduled_end=datetime.utcnow() + timedelta(hours=1),
                status=AppointmentStatus.COMPLETED
            )
            db.add(appt)
        db.commit()

        today = date.today()
        report = ReportingService.get_customer_retention_report(
            db=db,
            tenant_id=tenant.id,
            start_date=today,
            end_date=today
        )

        assert report["new_customers"] == 3
        assert report["repeat_customers"] >= 1  # At least the one we created
        assert report["total_customers"] >= 4


class TestGetStaffPerformance:
    """Test staff performance reporting"""

    def test_staff_performance(self, db, staff, owner, service, tenant):
        """Test individual staff performance metrics"""
        # Create appointments for staff
        for i in range(10):
            scheduled = datetime.utcnow() - timedelta(days=i)
            appt = Appointment(
                id=uuid4(), tenant_id=tenant.id, owner_id=owner.id,
                staff_id=staff.id, service_id=service.id,
                status=AppointmentStatus.COMPLETED if i < 8 else AppointmentStatus.CANCELLED,
                scheduled_start=scheduled,
                scheduled_end=scheduled + timedelta(hours=1)
            )
            db.add(appt)
            db.commit()

            # Create payment for completed appointments
            if i < 8:
                payment = Payment(
                    id=uuid4(), tenant_id=tenant.id, owner_id=owner.id,
                    appointment_id=appt.id, amount=5000,
                    status=PaymentStatus.SUCCEEDED, method="card",
                    created_at=scheduled
                )
                db.add(payment)
        db.commit()

        start_date = (datetime.utcnow() - timedelta(days=10)).date()
        end_date = datetime.utcnow().date()

        performance = ReportingService.get_staff_performance(
            db=db,
            staff_id=staff.id,
            start_date=start_date,
            end_date=end_date
        )

        assert performance["total_appointments"] == 10
        assert performance["completed_appointments"] == 8
        assert performance["completion_rate"] == 80.0
        assert performance["total_revenue"] == 40000  # 8 x $50

    def test_staff_performance_average_revenue(self, db, staff, owner, service, tenant):
        """Test average revenue per appointment calculation"""
        # Create 5 appointments with varying prices
        for i in range(5):
            scheduled = datetime.utcnow()
            appt = Appointment(
                id=uuid4(), tenant_id=tenant.id, owner_id=owner.id,
                staff_id=staff.id, service_id=service.id,
                status=AppointmentStatus.COMPLETED,
                scheduled_start=scheduled,
                scheduled_end=scheduled + timedelta(hours=1)
            )
            db.add(appt)
            db.commit()

            payment = Payment(
                id=uuid4(), tenant_id=tenant.id, owner_id=owner.id,
                appointment_id=appt.id, amount=5000,
                status=PaymentStatus.SUCCEEDED, method="card"
            )
            db.add(payment)
        db.commit()

        today = date.today()
        performance = ReportingService.get_staff_performance(
            db=db,
            staff_id=staff.id,
            start_date=today,
            end_date=today
        )

        assert performance["average_revenue_per_appointment"] == 5000  # $50


# Integration tests
class TestReportingServiceIntegration:
    """Integration tests for reporting service"""

    def test_comprehensive_reporting_workflow(self, db, tenant, owner, staff, service):
        """Test generating multiple reports for a business"""
        # Set up test data - 1 week of business
        for day in range(7):
            scheduled = datetime.utcnow() - timedelta(days=day)
            scheduled = scheduled.replace(hour=10, minute=0)

            # 3 appointments per day
            for _ in range(3):
                appt = Appointment(
                    id=uuid4(), tenant_id=tenant.id, owner_id=owner.id,
                    staff_id=staff.id, service_id=service.id,
                    status=AppointmentStatus.COMPLETED,
                    scheduled_start=scheduled,
                    scheduled_end=scheduled + timedelta(hours=1)
                )
                db.add(appt)
                db.commit()

                payment = Payment(
                    id=uuid4(), tenant_id=tenant.id, owner_id=owner.id,
                    appointment_id=appt.id, amount=5000,
                    status=PaymentStatus.SUCCEEDED, method="card",
                    created_at=scheduled
                )
                db.add(payment)
        db.commit()

        start_date = (datetime.utcnow() - timedelta(days=7)).date()
        end_date = datetime.utcnow().date()

        # 1. Revenue report
        revenue = ReportingService.get_revenue_report(
            db=db, tenant_id=tenant.id,
            start_date=start_date, end_date=end_date
        )
        assert revenue["total_revenue"] == 105000  # 21 x $50

        # 2. Appointment volume
        volume = ReportingService.get_appointment_volume_report(
            db=db, tenant_id=tenant.id,
            start_date=start_date, end_date=end_date
        )
        assert volume["total_appointments"] == 21
        assert volume["completion_rate"] == 100.0

        # 3. Peak times
        peak = ReportingService.get_peak_times_analysis(
            db=db, tenant_id=tenant.id,
            start_date=start_date, end_date=end_date
        )
        assert peak["peak_hour"] == "10:00"

        # 4. Staff performance
        staff_perf = ReportingService.get_staff_performance(
            db=db, staff_id=staff.id,
            start_date=start_date, end_date=end_date
        )
        assert staff_perf["total_appointments"] == 21
        assert staff_perf["total_revenue"] == 105000
