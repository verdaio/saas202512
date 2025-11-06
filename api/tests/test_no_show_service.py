"""
Tests for No-Show Service
Sprint 4 - Automatic no-show detection and penalty system
"""
import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy.orm import Session

from src.models.appointment import Appointment, AppointmentStatus
from src.models.owner import Owner
from src.models.tenant import Tenant
from src.models.staff import Staff
from src.models.service import Service
from src.models.payment import Payment, PaymentStatus, PaymentType
from src.services.no_show_service import NoShowService


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
        phone="+1234567890",
        sms_opted_in=True,
        no_show_count=0
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
def past_appointment_no_arrival(db: Session, tenant, owner, staff, service):
    """Create past appointment with no arrival"""
    scheduled_time = datetime.utcnow() - timedelta(hours=2)
    appointment = Appointment(
        id=uuid4(),
        tenant_id=tenant.id,
        owner_id=owner.id,
        staff_id=staff.id,
        service_id=service.id,
        status=AppointmentStatus.CONFIRMED,
        scheduled_start=scheduled_time,
        scheduled_end=scheduled_time + timedelta(hours=1),
        is_no_show=False,
        arrived_at=None
    )
    db.add(appointment)
    db.commit()
    return appointment


@pytest.fixture
def past_appointment_with_arrival(db: Session, tenant, owner, staff, service):
    """Create past appointment with arrival recorded"""
    scheduled_time = datetime.utcnow() - timedelta(hours=2)
    appointment = Appointment(
        id=uuid4(),
        tenant_id=tenant.id,
        owner_id=owner.id,
        staff_id=staff.id,
        service_id=service.id,
        status=AppointmentStatus.CONFIRMED,
        scheduled_start=scheduled_time,
        scheduled_end=scheduled_time + timedelta(hours=1),
        is_no_show=False,
        arrived_at=scheduled_time + timedelta(minutes=5)
    )
    db.add(appointment)
    db.commit()
    return appointment


class TestDetectNoShows:
    """Test no-show detection"""

    def test_detect_no_show_after_grace_period(self, db, tenant, past_appointment_no_arrival):
        """Test detecting no-show after grace period"""
        no_shows = NoShowService.detect_no_shows(
            db=db,
            tenant_id=tenant.id,
            grace_period_minutes=15
        )

        assert len(no_shows) == 1
        assert no_shows[0].id == past_appointment_no_arrival.id

    def test_no_detection_when_arrived(self, db, tenant, past_appointment_with_arrival):
        """Test that appointments with arrival aren't marked as no-show"""
        no_shows = NoShowService.detect_no_shows(
            db=db,
            tenant_id=tenant.id,
            grace_period_minutes=15
        )

        assert len(no_shows) == 0

    def test_no_detection_during_grace_period(self, db, tenant, owner, staff, service):
        """Test that appointments in grace period aren't detected"""
        # Appointment just 10 minutes ago (within 15 min grace period)
        recent_time = datetime.utcnow() - timedelta(minutes=10)
        appointment = Appointment(
            id=uuid4(),
            tenant_id=tenant.id,
            owner_id=owner.id,
            staff_id=staff.id,
            service_id=service.id,
            status=AppointmentStatus.CONFIRMED,
            scheduled_start=recent_time,
            scheduled_end=recent_time + timedelta(hours=1),
            is_no_show=False,
            arrived_at=None
        )
        db.add(appointment)
        db.commit()

        no_shows = NoShowService.detect_no_shows(
            db=db,
            tenant_id=tenant.id,
            grace_period_minutes=15
        )

        assert len(no_shows) == 0

    def test_already_marked_no_show_excluded(self, db, tenant, owner, staff, service):
        """Test that already marked no-shows aren't re-detected"""
        scheduled_time = datetime.utcnow() - timedelta(hours=2)
        appointment = Appointment(
            id=uuid4(),
            tenant_id=tenant.id,
            owner_id=owner.id,
            staff_id=staff.id,
            service_id=service.id,
            status=AppointmentStatus.NO_SHOW,
            scheduled_start=scheduled_time,
            scheduled_end=scheduled_time + timedelta(hours=1),
            is_no_show=True,  # Already marked
            arrived_at=None
        )
        db.add(appointment)
        db.commit()

        no_shows = NoShowService.detect_no_shows(
            db=db,
            tenant_id=tenant.id,
            grace_period_minutes=15
        )

        assert len(no_shows) == 0


class TestMarkAsNoShow:
    """Test marking appointment as no-show"""

    def test_mark_as_no_show_with_fee(self, db, past_appointment_no_arrival, owner):
        """Test marking appointment as no-show with fee"""
        success, error = NoShowService.mark_as_no_show(
            db=db,
            appointment_id=past_appointment_no_arrival.id,
            apply_fee=True
        )

        assert success is True
        assert error is None

        db.refresh(past_appointment_no_arrival)
        assert past_appointment_no_arrival.is_no_show is True
        assert past_appointment_no_arrival.status == AppointmentStatus.NO_SHOW
        assert past_appointment_no_arrival.no_show_fee_charged > 0

        # Check owner count updated
        db.refresh(owner)
        assert owner.no_show_count == 1

        # Check payment created
        payment = db.query(Payment).filter(
            Payment.appointment_id == past_appointment_no_arrival.id,
            Payment.type == PaymentType.NO_SHOW_FEE
        ).first()
        assert payment is not None
        assert payment.status == PaymentStatus.PENDING

    def test_mark_as_no_show_without_fee(self, db, past_appointment_no_arrival, owner):
        """Test marking appointment as no-show without fee"""
        success, error = NoShowService.mark_as_no_show(
            db=db,
            appointment_id=past_appointment_no_arrival.id,
            apply_fee=False
        )

        assert success is True
        assert error is None

        db.refresh(past_appointment_no_arrival)
        assert past_appointment_no_arrival.is_no_show is True
        assert past_appointment_no_arrival.status == AppointmentStatus.NO_SHOW

        # Check no payment created
        payment = db.query(Payment).filter(
            Payment.appointment_id == past_appointment_no_arrival.id,
            Payment.type == PaymentType.NO_SHOW_FEE
        ).first()
        assert payment is None

    def test_cannot_mark_already_no_show(self, db, owner, staff, service, tenant):
        """Test that already marked no-shows can't be re-marked"""
        appointment = Appointment(
            id=uuid4(),
            tenant_id=tenant.id,
            owner_id=owner.id,
            staff_id=staff.id,
            service_id=service.id,
            status=AppointmentStatus.NO_SHOW,
            scheduled_start=datetime.utcnow() - timedelta(hours=2),
            scheduled_end=datetime.utcnow() - timedelta(hours=1),
            is_no_show=True
        )
        db.add(appointment)
        db.commit()

        success, error = NoShowService.mark_as_no_show(
            db=db,
            appointment_id=appointment.id,
            apply_fee=True
        )

        assert success is False
        assert "already marked as no-show" in error.lower()

    def test_mark_nonexistent_appointment(self, db):
        """Test marking nonexistent appointment fails"""
        fake_id = uuid4()
        success, error = NoShowService.mark_as_no_show(
            db=db,
            appointment_id=fake_id,
            apply_fee=True
        )

        assert success is False
        assert "not found" in error.lower()


class TestCalculateNoShowPenalty:
    """Test no-show penalty calculation"""

    def test_first_no_show_penalty(self, db, owner):
        """Test first no-show penalty is $25"""
        fee = NoShowService.calculate_no_show_penalty(db=db, owner_id=owner.id)
        assert fee == 2500  # $25

    def test_second_no_show_penalty(self, db, owner):
        """Test second no-show penalty is $35"""
        owner.no_show_count = 1
        db.commit()

        fee = NoShowService.calculate_no_show_penalty(db=db, owner_id=owner.id)
        assert fee == 3500  # $35

    def test_third_no_show_penalty(self, db, owner):
        """Test third no-show penalty is $50"""
        owner.no_show_count = 2
        db.commit()

        fee = NoShowService.calculate_no_show_penalty(db=db, owner_id=owner.id)
        assert fee == 5000  # $50

    def test_fourth_and_beyond_penalty(self, db, owner):
        """Test fourth+ no-show penalty is $75"""
        owner.no_show_count = 3
        db.commit()

        fee = NoShowService.calculate_no_show_penalty(db=db, owner_id=owner.id)
        assert fee == 7500  # $75

        # Test fifth
        owner.no_show_count = 4
        db.commit()
        fee = NoShowService.calculate_no_show_penalty(db=db, owner_id=owner.id)
        assert fee == 7500  # Still $75

    def test_penalty_for_nonexistent_owner(self, db):
        """Test penalty for nonexistent owner returns default"""
        fake_id = uuid4()
        fee = NoShowService.calculate_no_show_penalty(db=db, owner_id=fake_id)
        assert fee == NoShowService.DEFAULT_NO_SHOW_FEE


class TestGetNoShowHistory:
    """Test getting no-show history"""

    def test_get_no_show_history(self, db, owner, staff, service, tenant):
        """Test getting comprehensive no-show history"""
        # Create some no-show appointments
        for i in range(3):
            scheduled_time = datetime.utcnow() - timedelta(days=i*10)
            appointment = Appointment(
                id=uuid4(),
                tenant_id=tenant.id,
                owner_id=owner.id,
                staff_id=staff.id,
                service_id=service.id,
                status=AppointmentStatus.NO_SHOW,
                scheduled_start=scheduled_time,
                scheduled_end=scheduled_time + timedelta(hours=1),
                is_no_show=True,
                no_show_fee_charged=2500
            )
            db.add(appointment)
        db.commit()

        history = NoShowService.get_no_show_history(db=db, owner_id=owner.id)

        assert history["total_no_shows"] == 3
        assert history["total_fees_charged"] == 7500  # 3 x $25
        assert len(history["recent_no_shows"]) == 3

    def test_no_show_history_empty(self, db, owner):
        """Test empty no-show history"""
        history = NoShowService.get_no_show_history(db=db, owner_id=owner.id)

        assert history["total_no_shows"] == 0
        assert history["total_fees_charged"] == 0
        assert len(history["recent_no_shows"]) == 0


class TestCalculateNoShowRate:
    """Test no-show rate calculation"""

    def test_calculate_no_show_rate(self, db, owner, staff, service, tenant):
        """Test calculating no-show rate"""
        # Create 10 appointments, 3 no-shows
        for i in range(10):
            scheduled_time = datetime.utcnow() - timedelta(days=i)
            appointment = Appointment(
                id=uuid4(),
                tenant_id=tenant.id,
                owner_id=owner.id,
                staff_id=staff.id,
                service_id=service.id,
                status=AppointmentStatus.NO_SHOW if i < 3 else AppointmentStatus.COMPLETED,
                scheduled_start=scheduled_time,
                scheduled_end=scheduled_time + timedelta(hours=1),
                is_no_show=True if i < 3 else False
            )
            db.add(appointment)
        db.commit()

        rate = NoShowService.calculate_no_show_rate(db=db, owner_id=owner.id)

        assert rate == 30.0  # 3 out of 10 = 30%

    def test_zero_appointments_rate(self, db, owner):
        """Test no-show rate with zero appointments"""
        rate = NoShowService.calculate_no_show_rate(db=db, owner_id=owner.id)
        assert rate == 0.0


class TestWaiveNoShowFee:
    """Test waiving no-show fees"""

    def test_waive_no_show_fee(self, db, past_appointment_no_arrival):
        """Test waiving a no-show fee"""
        # First mark as no-show
        NoShowService.mark_as_no_show(
            db=db,
            appointment_id=past_appointment_no_arrival.id,
            apply_fee=True
        )

        # Then waive the fee
        success, error = NoShowService.waive_no_show_fee(
            db=db,
            appointment_id=past_appointment_no_arrival.id,
            reason="Customer called with emergency"
        )

        assert success is True
        assert error is None

        # Check payment waived
        payment = db.query(Payment).filter(
            Payment.appointment_id == past_appointment_no_arrival.id,
            Payment.type == PaymentType.NO_SHOW_FEE
        ).first()
        assert payment.status == PaymentStatus.WAIVED
        assert "emergency" in payment.notes.lower()

        # Check appointment fee cleared
        db.refresh(past_appointment_no_arrival)
        assert past_appointment_no_arrival.no_show_fee_charged == 0

    def test_waive_non_no_show_fails(self, db, past_appointment_no_arrival):
        """Test cannot waive fee for non-no-show appointment"""
        success, error = NoShowService.waive_no_show_fee(
            db=db,
            appointment_id=past_appointment_no_arrival.id,
            reason="Test"
        )

        assert success is False
        assert "not marked as no-show" in error.lower()


class TestGetHighRiskCustomers:
    """Test getting high-risk customers"""

    def test_get_high_risk_customers(self, db, tenant):
        """Test getting customers with multiple no-shows"""
        # Create 3 owners with different no-show counts
        owners = []
        for i in range(3):
            owner = Owner(
                id=uuid4(),
                tenant_id=tenant.id,
                first_name=f"Customer{i}",
                last_name="Test",
                email=f"customer{i}@test.com",
                phone=f"+123456789{i}",
                no_show_count=i + 2  # 2, 3, 4 no-shows
            )
            owners.append(owner)
            db.add(owner)
        db.commit()

        high_risk = NoShowService.get_high_risk_customers(
            db=db,
            tenant_id=tenant.id,
            min_no_shows=2
        )

        assert len(high_risk) == 3
        # Should be sorted by no-show count descending
        assert high_risk[0]["no_show_count"] == 4
        assert high_risk[1]["no_show_count"] == 3
        assert high_risk[2]["no_show_count"] == 2

    def test_no_high_risk_customers(self, db, tenant, owner):
        """Test when no high-risk customers exist"""
        # Owner has 0 no-shows
        high_risk = NoShowService.get_high_risk_customers(
            db=db,
            tenant_id=tenant.id,
            min_no_shows=2
        )

        assert len(high_risk) == 0


class TestProcessDailyNoShowDetection:
    """Test daily no-show detection task"""

    def test_process_daily_detection(self, db, tenant, owner, staff, service):
        """Test daily processing detects and marks no-shows"""
        # Create 2 no-show appointments
        for i in range(2):
            scheduled_time = datetime.utcnow() - timedelta(hours=2+i)
            appointment = Appointment(
                id=uuid4(),
                tenant_id=tenant.id,
                owner_id=owner.id,
                staff_id=staff.id,
                service_id=service.id,
                status=AppointmentStatus.CONFIRMED,
                scheduled_start=scheduled_time,
                scheduled_end=scheduled_time + timedelta(hours=1),
                is_no_show=False,
                arrived_at=None
            )
            db.add(appointment)
        db.commit()

        results = NoShowService.process_daily_no_show_detection(
            db=db,
            tenant_id=tenant.id
        )

        assert results["total_detected"] == 2
        assert results["fees_applied"] == 2
        assert results["errors"] == 0

    def test_process_daily_detection_no_shows(self, db, tenant):
        """Test daily processing with no no-shows"""
        results = NoShowService.process_daily_no_show_detection(
            db=db,
            tenant_id=tenant.id
        )

        assert results["total_detected"] == 0
        assert results["fees_applied"] == 0


# Integration tests
class TestNoShowServiceIntegration:
    """Integration tests for full no-show workflow"""

    def test_full_no_show_workflow(self, db, tenant, owner, staff, service):
        """Test complete no-show workflow"""
        # 1. Create appointment
        scheduled_time = datetime.utcnow() - timedelta(hours=2)
        appointment = Appointment(
            id=uuid4(),
            tenant_id=tenant.id,
            owner_id=owner.id,
            staff_id=staff.id,
            service_id=service.id,
            status=AppointmentStatus.CONFIRMED,
            scheduled_start=scheduled_time,
            scheduled_end=scheduled_time + timedelta(hours=1),
            is_no_show=False,
            arrived_at=None
        )
        db.add(appointment)
        db.commit()

        # 2. Detect no-shows
        no_shows = NoShowService.detect_no_shows(db=db, tenant_id=tenant.id)
        assert len(no_shows) == 1

        # 3. Mark as no-show with fee
        success, error = NoShowService.mark_as_no_show(
            db=db,
            appointment_id=appointment.id,
            apply_fee=True
        )
        assert success is True

        # 4. Verify fee applied
        db.refresh(owner)
        assert owner.no_show_count == 1

        # 5. Get history
        history = NoShowService.get_no_show_history(db=db, owner_id=owner.id)
        assert history["total_no_shows"] == 1
        assert history["total_fees_charged"] == 2500

        # 6. Calculate rate
        rate = NoShowService.calculate_no_show_rate(db=db, owner_id=owner.id)
        assert rate == 100.0  # 1 of 1 = 100%

    def test_escalating_penalties_workflow(self, db, tenant, owner, staff, service):
        """Test escalating penalties over multiple no-shows"""
        fees_charged = []

        # Create 4 no-shows
        for i in range(4):
            scheduled_time = datetime.utcnow() - timedelta(days=i+1)
            appointment = Appointment(
                id=uuid4(),
                tenant_id=tenant.id,
                owner_id=owner.id,
                staff_id=staff.id,
                service_id=service.id,
                status=AppointmentStatus.CONFIRMED,
                scheduled_start=scheduled_time,
                scheduled_end=scheduled_time + timedelta(hours=1),
                is_no_show=False
            )
            db.add(appointment)
            db.commit()

            # Mark as no-show
            NoShowService.mark_as_no_show(db=db, appointment_id=appointment.id, apply_fee=True)

            # Get fee that was charged
            db.refresh(appointment)
            fees_charged.append(appointment.no_show_fee_charged)

        # Verify escalating fees
        assert fees_charged[0] == 2500  # $25
        assert fees_charged[1] == 3500  # $35
        assert fees_charged[2] == 5000  # $50
        assert fees_charged[3] == 7500  # $75

        # Verify final owner state
        db.refresh(owner)
        assert owner.no_show_count == 4
