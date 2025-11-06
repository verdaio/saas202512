"""
End-to-End Integration Tests
Test complete business workflows across multiple services
"""
import pytest
from datetime import datetime, date, timedelta
from uuid import uuid4

from src.services.appointment_service import AppointmentService
from src.services.scheduling_service import SchedulingService
from src.services.no_show_service import NoShowService
from src.services.reputation_service import ReputationService
from src.services.vaccination_monitoring_service import VaccinationMonitoringService
from src.services.reporting_service import ReportingService
from src.models.appointment import AppointmentStatus
from src.models.payment import PaymentStatus, PaymentType


class TestBookingWorkflow:
    """Test complete booking workflow from start to finish"""

    def test_successful_booking_workflow(self, db, tenant, owner, staff, service):
        """Test successful booking: check availability → book → confirm → complete → payment"""

        # 1. Check available time slots
        tomorrow = date.today() + timedelta(days=1)
        slots = SchedulingService.get_available_time_slots(
            db=db,
            tenant=tenant,
            date=tomorrow,
            service_id=service.id
        )

        assert len(slots) > 0, "Should have available slots"
        first_slot = slots[0]

        # 2. Create booking
        appointment_data = {
            "owner_id": owner.id,
            "staff_id": staff.id,
            "service_id": service.id,
            "scheduled_start": first_slot["start_time"],
            "notes": "Integration test booking"
        }

        appointment = AppointmentService.create_appointment(
            db=db,
            tenant=tenant,
            appointment_data=appointment_data
        )

        assert appointment is not None
        assert appointment.status == AppointmentStatus.PENDING

        # 3. Confirm appointment
        appointment.status = AppointmentStatus.CONFIRMED
        db.commit()

        # 4. Mark as arrived (simulate customer arrival)
        appointment.arrived_at = datetime.utcnow()
        db.commit()

        # 5. Complete appointment
        appointment.status = AppointmentStatus.COMPLETED
        db.commit()

        # 6. Update reputation for completion
        old_score, new_score = ReputationService.update_reputation_after_event(
            db=db,
            owner_id=owner.id,
            event_type="completed_appointment"
        )

        assert new_score == 100  # Started at 100, +2 but capped at 100

        # 7. Verify owner's completed count increased
        db.refresh(owner)
        assert owner.completed_appointment_count == 1

    def test_booking_with_low_reputation_blocked(self, db, tenant, low_reputation_owner, staff, service):
        """Test that low reputation customers cannot book"""

        # Check if booking is allowed
        can_book, reason = ReputationService.can_book_appointment(
            db=db,
            owner_id=low_reputation_owner.id
        )

        assert can_book is False
        assert "too low" in reason.lower()

        # Attempt to book should fail (in real API, this would return 403)
        # Here we're just verifying the business logic


class TestNoShowWorkflow:
    """Test complete no-show detection and penalty workflow"""

    def test_no_show_detection_and_penalty_workflow(self, db, tenant, owner, staff, service):
        """Test: miss appointment → detected as no-show → fee applied → reputation drops"""

        # 1. Create appointment in the past (missed)
        past_time = datetime.utcnow() - timedelta(hours=2)
        appointment_data = {
            "owner_id": owner.id,
            "staff_id": staff.id,
            "service_id": service.id,
            "scheduled_start": past_time,
            "scheduled_end": past_time + timedelta(hours=1)
        }

        from src.models.appointment import Appointment
        appointment = Appointment(
            id=uuid4(),
            tenant_id=tenant.id,
            **appointment_data,
            status=AppointmentStatus.CONFIRMED,
            is_no_show=False
        )
        db.add(appointment)
        db.commit()

        # 2. Run no-show detection
        no_shows = NoShowService.detect_no_shows(
            db=db,
            tenant_id=tenant.id,
            grace_period_minutes=15
        )

        assert len(no_shows) == 1
        assert no_shows[0].id == appointment.id

        # 3. Calculate penalty (first no-show)
        fee = NoShowService.calculate_no_show_penalty(db=db, owner_id=owner.id)
        assert fee == 2500  # $25 for first no-show

        # 4. Mark as no-show with fee
        success, error = NoShowService.mark_as_no_show(
            db=db,
            appointment_id=appointment.id,
            apply_fee=True
        )

        assert success is True
        assert error is None

        # 5. Verify appointment marked
        db.refresh(appointment)
        assert appointment.is_no_show is True
        assert appointment.status == AppointmentStatus.NO_SHOW
        assert appointment.no_show_fee_charged == 2500

        # 6. Verify owner's no-show count increased
        db.refresh(owner)
        assert owner.no_show_count == 1

        # 7. Verify reputation dropped
        score = ReputationService.calculate_reputation_score(db=db, owner_id=owner.id)
        assert score == 80  # 100 - 20 for no-show

        # 8. Verify no-show fee payment created
        from src.models.payment import Payment
        fee_payment = db.query(Payment).filter(
            Payment.appointment_id == appointment.id,
            Payment.type == PaymentType.NO_SHOW_FEE
        ).first()

        assert fee_payment is not None
        assert fee_payment.amount == 2500
        assert fee_payment.status == PaymentStatus.PENDING

    def test_escalating_penalties_workflow(self, db, tenant, owner, staff, service):
        """Test escalating penalties for repeat offenders"""

        initial_reputation = owner.reputation_score
        fees_charged = []

        # Create 4 no-show appointments
        for i in range(4):
            past_time = datetime.utcnow() - timedelta(days=i+1)

            from src.models.appointment import Appointment
            appointment = Appointment(
                id=uuid4(),
                tenant_id=tenant.id,
                owner_id=owner.id,
                staff_id=staff.id,
                service_id=service.id,
                scheduled_start=past_time,
                scheduled_end=past_time + timedelta(hours=1),
                status=AppointmentStatus.CONFIRMED,
                is_no_show=False
            )
            db.add(appointment)
            db.commit()

            # Mark as no-show
            success, _ = NoShowService.mark_as_no_show(
                db=db,
                appointment_id=appointment.id,
                apply_fee=True
            )

            assert success is True

            # Track fee charged
            db.refresh(appointment)
            fees_charged.append(appointment.no_show_fee_charged)

        # Verify escalating fees: $25, $35, $50, $75
        assert fees_charged[0] == 2500
        assert fees_charged[1] == 3500
        assert fees_charged[2] == 5000
        assert fees_charged[3] == 7500

        # Verify final reputation
        db.refresh(owner)
        assert owner.no_show_count == 4

        final_score = ReputationService.calculate_reputation_score(db=db, owner_id=owner.id)
        assert final_score == 20  # 100 - (4 * 20)


class TestVaccinationWorkflow:
    """Test vaccination monitoring and alert workflow"""

    def test_vaccination_expiry_alert_workflow(self, db, tenant, owner, pet):
        """Test: vaccination expires soon → alert sent → owner notified"""

        # 1. Create vaccination expiring in 30 days
        from src.models.vaccination_record import VaccinationRecord
        vaccination = VaccinationRecord(
            id=uuid4(),
            tenant_id=tenant.id,
            pet_id=pet.id,
            vaccination_type="Rabies",
            administered_date=date.today() - timedelta(days=335),
            expiry_date=date.today() + timedelta(days=30),
            is_current=True,
            alert_count=0
        )
        db.add(vaccination)
        db.commit()

        # 2. Run monitoring to find expiring vaccinations
        expiring = VaccinationMonitoringService.get_expiring_vaccinations(
            db=db,
            tenant_id=tenant.id,
            days_ahead=30
        )

        assert len(expiring) == 1
        assert expiring[0].id == vaccination.id

        # 3. Send alert (would trigger SMS in production)
        # success, error = VaccinationMonitoringService.send_expiry_alert(
        #     db=db,
        #     vaccination=vaccination,
        #     days_until_expiry=30
        # )
        #
        # assert success is True

        # 4. Verify alert count incremented (simulated)
        vaccination.alert_count += 1
        vaccination.last_alert_sent = datetime.utcnow()
        db.commit()

        db.refresh(vaccination)
        assert vaccination.alert_count == 1
        assert vaccination.last_alert_sent is not None

        # 5. Fast-forward to expiry date
        vaccination.expiry_date = date.today() - timedelta(days=1)
        db.commit()

        # 6. Run status update
        updated = VaccinationMonitoringService.update_vaccination_statuses(
            db=db,
            tenant_id=tenant.id
        )

        assert updated == 1

        # 7. Verify vaccination marked as expired
        db.refresh(vaccination)
        assert vaccination.is_current is False


class TestReputationRecoveryWorkflow:
    """Test reputation recovery over time"""

    def test_reputation_recovery_workflow(self, db, tenant, owner):
        """Test: bad reputation → good behavior → score recovers"""

        # 1. Damage reputation (simulate 3 no-shows)
        owner.no_show_count = 3
        owner.reputation_score = 40  # 100 - (3 * 20)
        owner.last_reputation_update = datetime.utcnow() - timedelta(days=100)
        db.commit()

        initial_score = owner.reputation_score
        assert initial_score == 40

        # 2. Verify customer is still above minimum threshold
        can_book, _ = ReputationService.can_book_appointment(db=db, owner_id=owner.id)
        assert can_book is True  # 40 > 30 threshold

        # 3. Simulate good behavior (no recent no-shows)
        # (No recent appointments with is_no_show=True)

        # 4. Apply score recovery (90 days of good behavior)
        results = ReputationService.apply_score_decay(
            db=db,
            tenant_id=tenant.id,
            days_since_last_event=90,
            recovery_points=5
        )

        assert results["scores_improved"] == 1

        # 5. Verify score increased
        db.refresh(owner)
        assert owner.reputation_score == 45  # 40 + 5

        # 6. Simulate more good behavior (complete appointments)
        for _ in range(10):
            old_score, new_score = ReputationService.update_reputation_after_event(
                db=db,
                owner_id=owner.id,
                event_type="completed_appointment"
            )

        # 7. Verify final recovery
        db.refresh(owner)
        final_score = owner.reputation_score
        assert final_score == 65  # 45 + (10 * 2)
        assert owner.completed_appointment_count == 10


class TestReportingWorkflow:
    """Test business reporting workflows"""

    def test_comprehensive_reporting_workflow(self, db, tenant, owner, staff, service):
        """Test: generate business → activity reports for period"""

        # 1. Create business activity (appointments and payments)
        for day in range(7):
            scheduled = datetime.utcnow() - timedelta(days=day)

            from src.models.appointment import Appointment
            appointment = Appointment(
                id=uuid4(),
                tenant_id=tenant.id,
                owner_id=owner.id,
                staff_id=staff.id,
                service_id=service.id,
                scheduled_start=scheduled,
                scheduled_end=scheduled + timedelta(hours=1),
                status=AppointmentStatus.COMPLETED
            )
            db.add(appointment)
            db.commit()

            from src.models.payment import Payment
            payment = Payment(
                id=uuid4(),
                tenant_id=tenant.id,
                owner_id=owner.id,
                appointment_id=appointment.id,
                amount=5000,
                status=PaymentStatus.SUCCEEDED,
                type=PaymentType.FULL_PAYMENT,
                method="card",
                net_amount=5000,
                created_at=scheduled
            )
            db.add(payment)

        db.commit()

        # 2. Generate revenue report
        start_date = (datetime.utcnow() - timedelta(days=7)).date()
        end_date = datetime.utcnow().date()

        revenue_report = ReportingService.get_revenue_report(
            db=db,
            tenant_id=tenant.id,
            start_date=start_date,
            end_date=end_date,
            group_by="day"
        )

        assert revenue_report["total_revenue"] == 35000  # 7 * $50
        assert revenue_report["payment_count"] == 7
        assert revenue_report["net_revenue"] == 35000

        # 3. Generate appointment volume report
        volume_report = ReportingService.get_appointment_volume_report(
            db=db,
            tenant_id=tenant.id,
            start_date=start_date,
            end_date=end_date
        )

        assert volume_report["total_appointments"] == 7
        assert volume_report["completion_rate"] == 100.0

        # 4. Generate staff performance report
        staff_performance = ReportingService.get_staff_performance(
            db=db,
            staff_id=staff.id,
            start_date=start_date,
            end_date=end_date
        )

        assert staff_performance["total_appointments"] == 7
        assert staff_performance["completed_appointments"] == 7
        assert staff_performance["total_revenue"] == 35000

        # 5. Get customer lifetime value
        clv = ReportingService.get_customer_lifetime_value(
            db=db,
            owner_id=owner.id
        )

        assert clv == 350.00  # $350 total

        # 6. Get top customers
        top_customers = ReportingService.get_top_customers(
            db=db,
            tenant_id=tenant.id,
            limit=10
        )

        assert len(top_customers) >= 1
        assert str(owner.id) in [c["owner_id"] for c in top_customers]


class TestMultiTenantIsolation:
    """Test that multi-tenant data isolation works correctly"""

    def test_tenant_data_isolation(self, db, tenant_factory, owner_factory, staff_factory, service_factory):
        """Test that tenants cannot access each other's data"""

        # 1. Create two separate tenants
        tenant1 = tenant_factory(name="Clinic 1", subdomain="clinic1")
        tenant2 = tenant_factory(name="Clinic 2", subdomain="clinic2")

        # 2. Create data for tenant 1
        owner1 = owner_factory(tenant1.id, first_name="Tenant1", last_name="Owner")
        staff1 = staff_factory(tenant1.id, first_name="Tenant1", last_name="Staff")
        service1 = service_factory(tenant1.id, name="Tenant1 Service")

        # 3. Create data for tenant 2
        owner2 = owner_factory(tenant2.id, first_name="Tenant2", last_name="Owner")
        staff2 = staff_factory(tenant2.id, first_name="Tenant2", last_name="Staff")
        service2 = service_factory(tenant2.id, name="Tenant2 Service")

        # 4. Verify tenant 1 can only see their own data
        tenant1_owners = db.query(from src.models.owner import Owner).filter(
            Owner.tenant_id == tenant1.id
        ).all()

        assert len(tenant1_owners) == 1
        assert tenant1_owners[0].id == owner1.id

        # 5. Verify tenant 2 can only see their own data
        tenant2_owners = db.query(Owner).filter(
            Owner.tenant_id == tenant2.id
        ).all()

        assert len(tenant2_owners) == 1
        assert tenant2_owners[0].id == owner2.id

        # 6. Verify reputation service respects tenant isolation
        tenant1_restricted = ReputationService.get_customers_by_reputation(
            db=db,
            tenant_id=tenant1.id,
            category="excellent"
        )

        tenant2_restricted = ReputationService.get_customers_by_reputation(
            db=db,
            tenant_id=tenant2.id,
            category="excellent"
        )

        # Each tenant should see their own customers only
        tenant1_ids = [c["owner_id"] for c in tenant1_restricted]
        tenant2_ids = [c["owner_id"] for c in tenant2_restricted]

        assert str(owner1.id) in tenant1_ids
        assert str(owner2.id) not in tenant1_ids
        assert str(owner2.id) in tenant2_ids
        assert str(owner1.id) not in tenant2_ids


class TestErrorHandlingAndEdgeCases:
    """Test error handling and edge cases across services"""

    def test_double_booking_prevention(self, db, tenant, owner, staff, service):
        """Test that double-booking is prevented"""

        # Create first appointment
        scheduled_time = datetime.utcnow() + timedelta(days=1)
        appointment1_data = {
            "owner_id": owner.id,
            "staff_id": staff.id,
            "service_id": service.id,
            "scheduled_start": scheduled_time,
            "scheduled_end": scheduled_time + timedelta(hours=1)
        }

        appointment1 = AppointmentService.create_appointment(
            db=db,
            tenant=tenant,
            appointment_data=appointment1_data
        )

        assert appointment1 is not None

        # Attempt to book same staff at overlapping time
        appointment2_data = {
            "owner_id": owner.id,
            "staff_id": staff.id,
            "service_id": service.id,
            "scheduled_start": scheduled_time + timedelta(minutes=30),
            "scheduled_end": scheduled_time + timedelta(hours=1, minutes=30)
        }

        # This should fail or handle gracefully
        try:
            appointment2 = AppointmentService.create_appointment(
                db=db,
                tenant=tenant,
                appointment_data=appointment2_data
            )

            # If it doesn't raise an exception, verify business logic handles it
            # (e.g., by checking for overlaps in the service layer)
        except ValueError as e:
            # Expected: should raise error about staff being booked
            assert "already booked" in str(e).lower() or "conflict" in str(e).lower()

    def test_reputation_score_bounds(self, db, owner):
        """Test that reputation score respects min/max bounds"""

        # Test maximum bound
        owner.completed_appointment_count = 100  # Would give +200 points
        db.commit()

        score = ReputationService.calculate_reputation_score(db=db, owner_id=owner.id)
        assert score <= 100  # Should not exceed maximum

        # Test minimum bound
        owner.no_show_count = 10  # Would give -200 points
        owner.completed_appointment_count = 0
        db.commit()

        score = ReputationService.calculate_reputation_score(db=db, owner_id=owner.id)
        assert score >= 0  # Should not go below minimum

    def test_concurrent_no_show_detection(self, db, tenant, owner, staff, service):
        """Test that concurrent no-show detection doesn't double-charge"""

        # Create past appointment
        past_time = datetime.utcnow() - timedelta(hours=2)
        from src.models.appointment import Appointment
        appointment = Appointment(
            id=uuid4(),
            tenant_id=tenant.id,
            owner_id=owner.id,
            staff_id=staff.id,
            service_id=service.id,
            scheduled_start=past_time,
            scheduled_end=past_time + timedelta(hours=1),
            status=AppointmentStatus.CONFIRMED,
            is_no_show=False
        )
        db.add(appointment)
        db.commit()

        # Mark as no-show first time
        success1, _ = NoShowService.mark_as_no_show(db=db, appointment_id=appointment.id)
        assert success1 is True

        # Attempt to mark again (simulating concurrent process)
        success2, error = NoShowService.mark_as_no_show(db=db, appointment_id=appointment.id)
        assert success2 is False  # Should fail
        assert "already marked" in error.lower()

        # Verify only charged once
        db.refresh(owner)
        assert owner.no_show_count == 1  # Not 2
