"""
Tests for Vaccination Monitoring Service
Sprint 4 - Automated vaccination expiry monitoring
"""
import pytest
from datetime import date, datetime, timedelta
from uuid import uuid4
from sqlalchemy.orm import Session

from src.models.vaccination_record import VaccinationRecord
from src.models.pet import Pet
from src.models.owner import Owner
from src.models.tenant import Tenant
from src.services.vaccination_monitoring_service import VaccinationMonitoringService


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
        sms_opted_in=True
    )
    db.add(owner)
    db.commit()
    return owner


@pytest.fixture
def pet(db: Session, tenant, owner):
    """Create test pet"""
    pet = Pet(
        id=uuid4(),
        tenant_id=tenant.id,
        owner_id=owner.id,
        name="Buddy",
        species="Dog",
        breed="Golden Retriever"
    )
    db.add(pet)
    db.commit()
    return pet


@pytest.fixture
def vaccination_expiring_30_days(db: Session, tenant, pet):
    """Create vaccination expiring in 30 days"""
    expiry_date = date.today() + timedelta(days=30)
    vaccination = VaccinationRecord(
        id=uuid4(),
        tenant_id=tenant.id,
        pet_id=pet.id,
        vaccination_type="Rabies",
        administered_date=date.today() - timedelta(days=335),
        expiry_date=expiry_date,
        is_current=True
    )
    db.add(vaccination)
    db.commit()
    return vaccination


@pytest.fixture
def vaccination_expiring_14_days(db: Session, tenant, pet):
    """Create vaccination expiring in 14 days"""
    expiry_date = date.today() + timedelta(days=14)
    vaccination = VaccinationRecord(
        id=uuid4(),
        tenant_id=tenant.id,
        pet_id=pet.id,
        vaccination_type="Distemper",
        administered_date=date.today() - timedelta(days=351),
        expiry_date=expiry_date,
        is_current=True
    )
    db.add(vaccination)
    db.commit()
    return vaccination


@pytest.fixture
def vaccination_expiring_7_days(db: Session, tenant, pet):
    """Create vaccination expiring in 7 days"""
    expiry_date = date.today() + timedelta(days=7)
    vaccination = VaccinationRecord(
        id=uuid4(),
        tenant_id=tenant.id,
        pet_id=pet.id,
        vaccination_type="Bordetella",
        administered_date=date.today() - timedelta(days=358),
        expiry_date=expiry_date,
        is_current=True
    )
    db.add(vaccination)
    db.commit()
    return vaccination


class TestGetExpiringVaccinations:
    """Test getting expiring vaccinations"""

    def test_get_vaccinations_expiring_30_days(self, db, tenant, vaccination_expiring_30_days):
        """Test finding vaccinations expiring in 30 days"""
        vaccinations = VaccinationMonitoringService.get_expiring_vaccinations(
            db=db,
            tenant_id=tenant.id,
            days_ahead=30
        )

        assert len(vaccinations) == 1
        assert vaccinations[0].id == vaccination_expiring_30_days.id
        assert vaccinations[0].vaccination_type == "Rabies"

    def test_get_vaccinations_expiring_14_days(self, db, tenant, vaccination_expiring_14_days):
        """Test finding vaccinations expiring in 14 days"""
        vaccinations = VaccinationMonitoringService.get_expiring_vaccinations(
            db=db,
            tenant_id=tenant.id,
            days_ahead=14
        )

        assert len(vaccinations) == 1
        assert vaccinations[0].id == vaccination_expiring_14_days.id
        assert vaccinations[0].vaccination_type == "Distemper"

    def test_get_vaccinations_expiring_7_days(self, db, tenant, vaccination_expiring_7_days):
        """Test finding vaccinations expiring in 7 days"""
        vaccinations = VaccinationMonitoringService.get_expiring_vaccinations(
            db=db,
            tenant_id=tenant.id,
            days_ahead=7
        )

        assert len(vaccinations) == 1
        assert vaccinations[0].id == vaccination_expiring_7_days.id
        assert vaccinations[0].vaccination_type == "Bordetella"

    def test_no_expiring_vaccinations(self, db, tenant):
        """Test when no vaccinations are expiring"""
        vaccinations = VaccinationMonitoringService.get_expiring_vaccinations(
            db=db,
            tenant_id=tenant.id,
            days_ahead=30
        )

        assert len(vaccinations) == 0


class TestGetExpiredVaccinations:
    """Test getting expired vaccinations"""

    def test_get_expired_vaccinations(self, db, tenant, pet):
        """Test finding expired vaccinations"""
        # Create expired vaccination
        expired_date = date.today() - timedelta(days=10)
        vaccination = VaccinationRecord(
            id=uuid4(),
            tenant_id=tenant.id,
            pet_id=pet.id,
            vaccination_type="Rabies",
            administered_date=date.today() - timedelta(days=375),
            expiry_date=expired_date,
            is_current=False
        )
        db.add(vaccination)
        db.commit()

        expired_vaccinations = VaccinationMonitoringService.get_expired_vaccinations(
            db=db,
            tenant_id=tenant.id
        )

        assert len(expired_vaccinations) == 1
        assert expired_vaccinations[0].expiry_date < date.today()

    def test_no_expired_vaccinations(self, db, tenant):
        """Test when no vaccinations are expired"""
        expired_vaccinations = VaccinationMonitoringService.get_expired_vaccinations(
            db=db,
            tenant_id=tenant.id
        )

        assert len(expired_vaccinations) == 0


class TestUpdateVaccinationStatuses:
    """Test updating vaccination statuses"""

    def test_update_expired_status(self, db, tenant, pet):
        """Test updating status for expired vaccination"""
        # Create vaccination that expired yesterday
        expired_date = date.today() - timedelta(days=1)
        vaccination = VaccinationRecord(
            id=uuid4(),
            tenant_id=tenant.id,
            pet_id=pet.id,
            vaccination_type="Rabies",
            expiry_date=expired_date,
            is_current=True  # Still marked as current
        )
        db.add(vaccination)
        db.commit()

        # Update statuses
        updated_count = VaccinationMonitoringService.update_vaccination_statuses(
            db=db,
            tenant_id=tenant.id
        )

        assert updated_count == 1
        db.refresh(vaccination)
        assert vaccination.is_current is False

    def test_update_current_status(self, db, tenant, pet):
        """Test vaccination remains current if not expired"""
        future_date = date.today() + timedelta(days=30)
        vaccination = VaccinationRecord(
            id=uuid4(),
            tenant_id=tenant.id,
            pet_id=pet.id,
            vaccination_type="Rabies",
            expiry_date=future_date,
            is_current=True
        )
        db.add(vaccination)
        db.commit()

        updated_count = VaccinationMonitoringService.update_vaccination_statuses(
            db=db,
            tenant_id=tenant.id
        )

        # No updates needed
        db.refresh(vaccination)
        assert vaccination.is_current is True


class TestGetPetsWithExpiringVaccinations:
    """Test getting pets with expiring vaccinations"""

    def test_get_pets_with_expiring_vaccinations(self, db, tenant, pet, vaccination_expiring_30_days, owner):
        """Test getting list of pets with expiring vaccinations"""
        pets = VaccinationMonitoringService.get_pets_with_expiring_vaccinations(
            db=db,
            tenant_id=tenant.id,
            days_ahead=30
        )

        assert len(pets) == 1
        assert pets[0]["pet_id"] == str(pet.id)
        assert pets[0]["pet_name"] == "Buddy"
        assert pets[0]["owner_name"] == "John Doe"
        assert pets[0]["vaccination_type"] == "Rabies"
        assert pets[0]["days_until_expiry"] == 30

    def test_multiple_pets_with_expiring_vaccinations(self, db, tenant, owner):
        """Test multiple pets with expiring vaccinations"""
        # Create two pets
        pet1 = Pet(id=uuid4(), tenant_id=tenant.id, owner_id=owner.id, name="Dog1", species="Dog")
        pet2 = Pet(id=uuid4(), tenant_id=tenant.id, owner_id=owner.id, name="Dog2", species="Dog")
        db.add_all([pet1, pet2])
        db.commit()

        # Create expiring vaccinations for both
        expiry_date = date.today() + timedelta(days=20)
        vacc1 = VaccinationRecord(
            id=uuid4(), tenant_id=tenant.id, pet_id=pet1.id,
            vaccination_type="Rabies", expiry_date=expiry_date, is_current=True
        )
        vacc2 = VaccinationRecord(
            id=uuid4(), tenant_id=tenant.id, pet_id=pet2.id,
            vaccination_type="Distemper", expiry_date=expiry_date, is_current=True
        )
        db.add_all([vacc1, vacc2])
        db.commit()

        pets = VaccinationMonitoringService.get_pets_with_expiring_vaccinations(
            db=db,
            tenant_id=tenant.id,
            days_ahead=30
        )

        assert len(pets) == 2
        pet_names = [p["pet_name"] for p in pets]
        assert "Dog1" in pet_names
        assert "Dog2" in pet_names


class TestRunDailyMonitoring:
    """Test daily monitoring task"""

    def test_run_daily_monitoring_with_expiring_vaccinations(
        self, db, tenant, vaccination_expiring_30_days, vaccination_expiring_14_days
    ):
        """Test daily monitoring detects expiring vaccinations"""
        results = VaccinationMonitoringService.run_daily_monitoring(
            db=db,
            tenant_id=tenant.id
        )

        # Should check all 3 thresholds (30, 14, 7 days)
        assert results["total_checked"] == 2  # Found 2 expiring vaccinations
        assert "alerts_sent" in results
        assert "alerts_failed" in results

    def test_run_daily_monitoring_no_expiring(self, db, tenant):
        """Test daily monitoring with no expiring vaccinations"""
        results = VaccinationMonitoringService.run_daily_monitoring(
            db=db,
            tenant_id=tenant.id
        )

        assert results["total_checked"] == 0
        assert results["alerts_sent"] == 0


class TestAlertScheduling:
    """Test alert scheduling"""

    def test_schedule_vaccination_alerts(self, db, tenant, pet, owner, vaccination_expiring_30_days):
        """Test scheduling alerts for upcoming expiries"""
        scheduled = VaccinationMonitoringService.schedule_vaccination_alerts(
            db=db,
            tenant_id=tenant.id
        )

        assert "30_days" in scheduled
        assert len(scheduled["30_days"]) == 1
        assert scheduled["30_days"][0]["pet_name"] == "Buddy"

    def test_no_alerts_for_sms_opted_out(self, db, tenant, pet, owner, vaccination_expiring_30_days):
        """Test that alerts aren't scheduled for opted-out owners"""
        # Opt out of SMS
        owner.sms_opted_in = False
        db.commit()

        scheduled = VaccinationMonitoringService.schedule_vaccination_alerts(
            db=db,
            tenant_id=tenant.id
        )

        # Should be empty since owner opted out
        assert len(scheduled["30_days"]) == 0


class TestAlertThresholds:
    """Test alert threshold configuration"""

    def test_alert_thresholds(self):
        """Test that alert thresholds are correctly configured"""
        assert VaccinationMonitoringService.ALERT_THRESHOLDS == [30, 14, 7]

    def test_all_thresholds_checked(self, db, tenant, pet):
        """Test that all thresholds are checked in daily monitoring"""
        # Create vaccinations at each threshold
        for days in [30, 14, 7]:
            expiry_date = date.today() + timedelta(days=days)
            vaccination = VaccinationRecord(
                id=uuid4(),
                tenant_id=tenant.id,
                pet_id=pet.id,
                vaccination_type=f"Vaccine_{days}",
                expiry_date=expiry_date,
                is_current=True
            )
            db.add(vaccination)
        db.commit()

        results = VaccinationMonitoringService.run_daily_monitoring(
            db=db,
            tenant_id=tenant.id
        )

        # Should find all 3 vaccinations
        assert results["total_checked"] == 3


# Integration tests
class TestVaccinationMonitoringIntegration:
    """Integration tests for full vaccination monitoring workflow"""

    def test_full_monitoring_workflow(self, db, tenant, pet, owner):
        """Test complete monitoring workflow from creation to alert"""
        # 1. Create vaccination expiring soon
        expiry_date = date.today() + timedelta(days=30)
        vaccination = VaccinationRecord(
            id=uuid4(),
            tenant_id=tenant.id,
            pet_id=pet.id,
            vaccination_type="Rabies",
            administered_date=date.today() - timedelta(days=335),
            expiry_date=expiry_date,
            is_current=True
        )
        db.add(vaccination)
        db.commit()

        # 2. Run monitoring
        results = VaccinationMonitoringService.run_daily_monitoring(
            db=db,
            tenant_id=tenant.id
        )

        assert results["total_checked"] > 0

        # 3. Get expiring vaccinations report
        pets = VaccinationMonitoringService.get_pets_with_expiring_vaccinations(
            db=db,
            tenant_id=tenant.id,
            days_ahead=30
        )

        assert len(pets) == 1
        assert pets[0]["vaccination_type"] == "Rabies"

        # 4. Update statuses (vaccination still current)
        updated = VaccinationMonitoringService.update_vaccination_statuses(
            db=db,
            tenant_id=tenant.id
        )

        db.refresh(vaccination)
        assert vaccination.is_current is True

    def test_expiry_transition_workflow(self, db, tenant, pet):
        """Test workflow when vaccination expires"""
        # Create vaccination that expires today
        expiry_date = date.today()
        vaccination = VaccinationRecord(
            id=uuid4(),
            tenant_id=tenant.id,
            pet_id=pet.id,
            vaccination_type="Rabies",
            expiry_date=expiry_date,
            is_current=True
        )
        db.add(vaccination)
        db.commit()

        # Run status update
        updated = VaccinationMonitoringService.update_vaccination_statuses(
            db=db,
            tenant_id=tenant.id
        )

        assert updated == 1
        db.refresh(vaccination)
        assert vaccination.is_current is False

        # Verify it appears in expired list
        expired = VaccinationMonitoringService.get_expired_vaccinations(
            db=db,
            tenant_id=tenant.id
        )

        assert len(expired) == 1
        assert expired[0].id == vaccination.id
