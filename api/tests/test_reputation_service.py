"""
Tests for Reputation Service
Sprint 4 - Customer reputation management
"""
import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy.orm import Session

from src.models.owner import Owner
from src.models.appointment import Appointment, AppointmentStatus
from src.models.tenant import Tenant
from src.services.reputation_service import ReputationService, ReputationEventType


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
    """Create test owner with default reputation"""
    owner = Owner(
        id=uuid4(),
        tenant_id=tenant.id,
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="+1234567890",
        reputation_score=100,
        no_show_count=0,
        late_cancellation_count=0,
        completed_appointment_count=0
    )
    db.add(owner)
    db.commit()
    return owner


class TestCalculateReputationScore:
    """Test reputation score calculation"""

    def test_default_score(self, db, owner):
        """Test new customer has default score of 100"""
        score = ReputationService.calculate_reputation_score(db=db, owner_id=owner.id)
        assert score == 100

    def test_score_after_no_show(self, db, owner):
        """Test score decreases after no-show"""
        owner.no_show_count = 1
        db.commit()

        score = ReputationService.calculate_reputation_score(db=db, owner_id=owner.id)
        assert score == 80  # 100 - 20

    def test_score_after_multiple_no_shows(self, db, owner):
        """Test score decreases after multiple no-shows"""
        owner.no_show_count = 3
        db.commit()

        score = ReputationService.calculate_reputation_score(db=db, owner_id=owner.id)
        assert score == 40  # 100 - (3 * 20)

    def test_score_after_late_cancellation(self, db, owner):
        """Test score decreases after late cancellation"""
        owner.late_cancellation_count = 1
        db.commit()

        score = ReputationService.calculate_reputation_score(db=db, owner_id=owner.id)
        assert score == 90  # 100 - 10

    def test_score_with_completed_appointments(self, db, owner):
        """Test score increases with completed appointments"""
        owner.completed_appointment_count = 10
        db.commit()

        score = ReputationService.calculate_reputation_score(db=db, owner_id=owner.id)
        assert score == 100  # 100 + (10 * 2) capped at 100

    def test_score_with_mixed_events(self, db, owner):
        """Test score with combination of events"""
        owner.no_show_count = 2  # -40
        owner.late_cancellation_count = 1  # -10
        owner.completed_appointment_count = 10  # +20
        db.commit()

        score = ReputationService.calculate_reputation_score(db=db, owner_id=owner.id)
        assert score == 70  # 100 - 40 - 10 + 20

    def test_score_minimum_bound(self, db, owner):
        """Test score cannot go below 0"""
        owner.no_show_count = 10  # -200 (would be negative)
        db.commit()

        score = ReputationService.calculate_reputation_score(db=db, owner_id=owner.id)
        assert score == 0

    def test_score_maximum_bound(self, db, owner):
        """Test score cannot exceed 100"""
        owner.completed_appointment_count = 100  # +200 (would exceed 100)
        db.commit()

        score = ReputationService.calculate_reputation_score(db=db, owner_id=owner.id)
        assert score == 100

    def test_score_for_nonexistent_owner(self, db):
        """Test score for nonexistent owner returns default"""
        fake_id = uuid4()
        score = ReputationService.calculate_reputation_score(db=db, owner_id=fake_id)
        assert score == ReputationService.DEFAULT_SCORE


class TestUpdateReputationAfterEvent:
    """Test reputation updates after events"""

    def test_update_after_no_show(self, db, owner):
        """Test reputation update after no-show"""
        old_score, new_score = ReputationService.update_reputation_after_event(
            db=db,
            owner_id=owner.id,
            event_type=ReputationEventType.NO_SHOW
        )

        assert old_score == 100
        assert new_score == 80
        db.refresh(owner)
        assert owner.no_show_count == 1
        assert owner.reputation_score == 80

    def test_update_after_late_cancellation(self, db, owner):
        """Test reputation update after late cancellation"""
        old_score, new_score = ReputationService.update_reputation_after_event(
            db=db,
            owner_id=owner.id,
            event_type=ReputationEventType.LATE_CANCELLATION
        )

        assert old_score == 100
        assert new_score == 90
        db.refresh(owner)
        assert owner.late_cancellation_count == 1
        assert owner.reputation_score == 90

    def test_update_after_completed_appointment(self, db, owner):
        """Test reputation update after completed appointment"""
        old_score, new_score = ReputationService.update_reputation_after_event(
            db=db,
            owner_id=owner.id,
            event_type=ReputationEventType.COMPLETED_APPOINTMENT
        )

        assert old_score == 100
        assert new_score == 100  # Capped at 100
        db.refresh(owner)
        assert owner.completed_appointment_count == 1
        assert owner.reputation_score == 100

    def test_update_sets_timestamp(self, db, owner):
        """Test that update sets last_reputation_update timestamp"""
        before = datetime.utcnow()

        ReputationService.update_reputation_after_event(
            db=db,
            owner_id=owner.id,
            event_type=ReputationEventType.COMPLETED_APPOINTMENT
        )

        db.refresh(owner)
        assert owner.last_reputation_update is not None
        assert owner.last_reputation_update >= before

    def test_update_nonexistent_owner_fails(self, db):
        """Test updating reputation for nonexistent owner fails"""
        fake_id = uuid4()
        with pytest.raises(ValueError, match="Owner not found"):
            ReputationService.update_reputation_after_event(
                db=db,
                owner_id=fake_id,
                event_type=ReputationEventType.NO_SHOW
            )


class TestCanBookAppointment:
    """Test booking restriction logic"""

    def test_can_book_with_good_reputation(self, db, owner):
        """Test customer with good reputation can book"""
        owner.reputation_score = 80
        db.commit()

        can_book, reason = ReputationService.can_book_appointment(
            db=db,
            owner_id=owner.id
        )

        assert can_book is True
        assert reason is None

    def test_cannot_book_with_low_reputation(self, db, owner):
        """Test customer with low reputation cannot book"""
        owner.reputation_score = 20  # Below threshold of 30
        db.commit()

        can_book, reason = ReputationService.can_book_appointment(
            db=db,
            owner_id=owner.id
        )

        assert can_book is False
        assert "too low" in reason.lower()
        assert "20" in reason

    def test_can_book_at_threshold(self, db, owner):
        """Test customer at threshold can book"""
        owner.reputation_score = 30  # Exactly at threshold
        db.commit()

        can_book, reason = ReputationService.can_book_appointment(
            db=db,
            owner_id=owner.id
        )

        assert can_book is True
        assert reason is None

    def test_cannot_book_nonexistent_owner(self, db):
        """Test booking check for nonexistent owner fails"""
        fake_id = uuid4()
        can_book, reason = ReputationService.can_book_appointment(
            db=db,
            owner_id=fake_id
        )

        assert can_book is False
        assert "not found" in reason.lower()


class TestGetReputationSummary:
    """Test getting reputation summary"""

    def test_get_reputation_summary(self, db, owner, tenant):
        """Test getting comprehensive reputation summary"""
        # Set up owner with some history
        owner.no_show_count = 2
        owner.late_cancellation_count = 1
        owner.completed_appointment_count = 10
        owner.reputation_score = 72  # 100 - 40 - 10 + 20
        db.commit()

        summary = ReputationService.get_reputation_summary(
            db=db,
            owner_id=owner.id
        )

        assert summary["reputation_score"] == 72
        assert summary["score_category"] == "Good"
        assert summary["can_book"] is True
        assert summary["no_show_count"] == 2
        assert summary["late_cancellation_count"] == 1
        assert summary["completed_appointment_count"] == 10

    def test_summary_for_restricted_customer(self, db, owner):
        """Test summary shows restriction for low-score customer"""
        owner.reputation_score = 20
        db.commit()

        summary = ReputationService.get_reputation_summary(
            db=db,
            owner_id=owner.id
        )

        assert summary["can_book"] is False
        assert summary["restriction_reason"] is not None
        assert summary["score_category"] == "Restricted"

    def test_summary_for_nonexistent_owner(self, db):
        """Test summary for nonexistent owner returns error"""
        fake_id = uuid4()
        summary = ReputationService.get_reputation_summary(
            db=db,
            owner_id=fake_id
        )

        assert "error" in summary


class TestGetScoreCategory:
    """Test score categorization"""

    def test_excellent_category(self):
        """Test excellent category (90-100)"""
        assert ReputationService.get_score_category(100) == "Excellent"
        assert ReputationService.get_score_category(95) == "Excellent"
        assert ReputationService.get_score_category(90) == "Excellent"

    def test_good_category(self):
        """Test good category (70-89)"""
        assert ReputationService.get_score_category(89) == "Good"
        assert ReputationService.get_score_category(80) == "Good"
        assert ReputationService.get_score_category(70) == "Good"

    def test_fair_category(self):
        """Test fair category (50-69)"""
        assert ReputationService.get_score_category(69) == "Fair"
        assert ReputationService.get_score_category(60) == "Fair"
        assert ReputationService.get_score_category(50) == "Fair"

    def test_poor_category(self):
        """Test poor category (30-49)"""
        assert ReputationService.get_score_category(49) == "Poor"
        assert ReputationService.get_score_category(40) == "Poor"
        assert ReputationService.get_score_category(30) == "Poor"

    def test_restricted_category(self):
        """Test restricted category (0-29)"""
        assert ReputationService.get_score_category(29) == "Restricted"
        assert ReputationService.get_score_category(20) == "Restricted"
        assert ReputationService.get_score_category(0) == "Restricted"


class TestApplyScoreDecay:
    """Test score recovery over time"""

    def test_score_recovery_for_inactive_customer(self, db, tenant, owner):
        """Test score recovers for customers with no recent issues"""
        # Set low score and old update timestamp
        owner.reputation_score = 60
        owner.last_reputation_update = datetime.utcnow() - timedelta(days=100)
        db.commit()

        results = ReputationService.apply_score_decay(
            db=db,
            tenant_id=tenant.id,
            days_since_last_event=90,
            recovery_points=5
        )

        assert results["scores_improved"] == 1
        db.refresh(owner)
        assert owner.reputation_score == 65  # 60 + 5

    def test_no_recovery_for_recent_no_shows(self, db, tenant, owner):
        """Test no recovery if customer has recent no-shows"""
        owner.reputation_score = 60
        owner.last_reputation_update = datetime.utcnow() - timedelta(days=100)
        db.commit()

        # Create recent no-show appointment
        appointment = Appointment(
            id=uuid4(),
            tenant_id=tenant.id,
            owner_id=owner.id,
            scheduled_start=datetime.utcnow() - timedelta(days=50),
            scheduled_end=datetime.utcnow() - timedelta(days=50, hours=-1),
            is_no_show=True,
            status=AppointmentStatus.NO_SHOW
        )
        db.add(appointment)
        db.commit()

        results = ReputationService.apply_score_decay(
            db=db,
            tenant_id=tenant.id,
            days_since_last_event=90,
            recovery_points=5
        )

        assert results["scores_improved"] == 0
        db.refresh(owner)
        assert owner.reputation_score == 60  # No change

    def test_recovery_caps_at_max_score(self, db, tenant, owner):
        """Test recovery doesn't exceed maximum score"""
        owner.reputation_score = 98
        owner.last_reputation_update = datetime.utcnow() - timedelta(days=100)
        db.commit()

        results = ReputationService.apply_score_decay(
            db=db,
            tenant_id=tenant.id,
            days_since_last_event=90,
            recovery_points=5
        )

        assert results["scores_improved"] == 1
        db.refresh(owner)
        assert owner.reputation_score == 100  # Capped at max


class TestGetCustomersByReputation:
    """Test filtering customers by reputation category"""

    def test_get_excellent_customers(self, db, tenant):
        """Test getting customers with excellent reputation"""
        # Create owners with different scores
        owner1 = Owner(
            id=uuid4(), tenant_id=tenant.id, first_name="Excellent", last_name="Customer",
            email="excellent@test.com", phone="+1111111111", reputation_score=95
        )
        owner2 = Owner(
            id=uuid4(), tenant_id=tenant.id, first_name="Good", last_name="Customer",
            email="good@test.com", phone="+2222222222", reputation_score=75
        )
        db.add_all([owner1, owner2])
        db.commit()

        excellent = ReputationService.get_customers_by_reputation(
            db=db,
            tenant_id=tenant.id,
            category="excellent"
        )

        assert len(excellent) == 1
        assert excellent[0]["owner_id"] == str(owner1.id)
        assert excellent[0]["category"] == "Excellent"

    def test_get_restricted_customers(self, db, tenant):
        """Test getting restricted customers"""
        owner = Owner(
            id=uuid4(), tenant_id=tenant.id, first_name="Restricted", last_name="Customer",
            email="restricted@test.com", phone="+3333333333", reputation_score=20,
            no_show_count=5, late_cancellation_count=2
        )
        db.add(owner)
        db.commit()

        restricted = ReputationService.get_customers_by_reputation(
            db=db,
            tenant_id=tenant.id,
            category="restricted"
        )

        assert len(restricted) == 1
        assert restricted[0]["reputation_score"] == 20
        assert restricted[0]["no_shows"] == 5
        assert restricted[0]["late_cancellations"] == 2

    def test_invalid_category(self, db, tenant):
        """Test invalid category returns empty list"""
        customers = ReputationService.get_customers_by_reputation(
            db=db,
            tenant_id=tenant.id,
            category="invalid"
        )

        assert len(customers) == 0


class TestReputationEventType:
    """Test reputation event types and points"""

    def test_no_show_points(self):
        """Test no-show penalty value"""
        assert ReputationEventType.POINTS[ReputationEventType.NO_SHOW] == -20

    def test_late_cancellation_points(self):
        """Test late cancellation penalty value"""
        assert ReputationEventType.POINTS[ReputationEventType.LATE_CANCELLATION] == -10

    def test_completed_appointment_points(self):
        """Test completed appointment bonus value"""
        assert ReputationEventType.POINTS[ReputationEventType.COMPLETED_APPOINTMENT] == 2

    def test_on_time_arrival_points(self):
        """Test on-time arrival bonus value"""
        assert ReputationEventType.POINTS[ReputationEventType.ON_TIME_ARRIVAL] == 5

    def test_early_cancellation_points(self):
        """Test early cancellation has no penalty"""
        assert ReputationEventType.POINTS[ReputationEventType.EARLY_CANCELLATION] == 0


# Integration tests
class TestReputationServiceIntegration:
    """Integration tests for reputation service"""

    def test_full_reputation_lifecycle(self, db, tenant, owner):
        """Test complete reputation management lifecycle"""
        # 1. Start with perfect score
        score = ReputationService.calculate_reputation_score(db=db, owner_id=owner.id)
        assert score == 100

        # 2. Customer misses appointment
        old_score, new_score = ReputationService.update_reputation_after_event(
            db=db,
            owner_id=owner.id,
            event_type=ReputationEventType.NO_SHOW
        )
        assert new_score == 80

        # 3. Check if they can still book
        can_book, _ = ReputationService.can_book_appointment(db=db, owner_id=owner.id)
        assert can_book is True  # Still above threshold

        # 4. Another no-show
        ReputationService.update_reputation_after_event(
            db=db,
            owner_id=owner.id,
            event_type=ReputationEventType.NO_SHOW
        )
        score = ReputationService.calculate_reputation_score(db=db, owner_id=owner.id)
        assert score == 60

        # 5. Late cancellation
        ReputationService.update_reputation_after_event(
            db=db,
            owner_id=owner.id,
            event_type=ReputationEventType.LATE_CANCELLATION
        )
        score = ReputationService.calculate_reputation_score(db=db, owner_id=owner.id)
        assert score == 50

        # 6. One more no-show - should restrict booking
        ReputationService.update_reputation_after_event(
            db=db,
            owner_id=owner.id,
            event_type=ReputationEventType.NO_SHOW
        )
        score = ReputationService.calculate_reputation_score(db=db, owner_id=owner.id)
        assert score == 30  # At threshold

        # 7. Can still book at threshold
        can_book, _ = ReputationService.can_book_appointment(db=db, owner_id=owner.id)
        assert can_book is True

        # 8. One more issue pushes below threshold
        ReputationService.update_reputation_after_event(
            db=db,
            owner_id=owner.id,
            event_type=ReputationEventType.LATE_CANCELLATION
        )
        score = ReputationService.calculate_reputation_score(db=db, owner_id=owner.id)
        assert score == 20

        # 9. Now cannot book
        can_book, reason = ReputationService.can_book_appointment(db=db, owner_id=owner.id)
        assert can_book is False
        assert "too low" in reason.lower()

        # 10. Recovery through completed appointments
        for _ in range(10):
            ReputationService.update_reputation_after_event(
                db=db,
                owner_id=owner.id,
                event_type=ReputationEventType.COMPLETED_APPOINTMENT
            )

        score = ReputationService.calculate_reputation_score(db=db, owner_id=owner.id)
        assert score == 40  # 20 + (10 * 2)

        # 11. Can book again
        can_book, _ = ReputationService.can_book_appointment(db=db, owner_id=owner.id)
        assert can_book is True

    def test_reputation_summary_workflow(self, db, tenant, owner):
        """Test reputation summary at different stages"""
        # Initial state
        summary = ReputationService.get_reputation_summary(db=db, owner_id=owner.id)
        assert summary["score_category"] == "Excellent"
        assert summary["can_book"] is True

        # After deterioration
        owner.no_show_count = 3
        owner.late_cancellation_count = 2
        owner.reputation_score = 30
        db.commit()

        summary = ReputationService.get_reputation_summary(db=db, owner_id=owner.id)
        assert summary["score_category"] == "Poor"
        assert summary["can_book"] is True  # Still at threshold

        # After restriction
        owner.reputation_score = 20
        db.commit()

        summary = ReputationService.get_reputation_summary(db=db, owner_id=owner.id)
        assert summary["score_category"] == "Restricted"
        assert summary["can_book"] is False
        assert summary["restriction_reason"] is not None
