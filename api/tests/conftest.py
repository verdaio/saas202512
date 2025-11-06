"""
Pytest Configuration and Shared Fixtures
Provides common test fixtures for all test suites
"""
import pytest
from datetime import datetime, date, timedelta
from uuid import uuid4
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

from src.db.base import Base
from src.main import app
from src.models.tenant import Tenant
from src.models.owner import Owner
from src.models.staff import Staff
from src.models.service import Service
from src.models.pet import Pet
from src.models.appointment import Appointment, AppointmentStatus
from src.models.payment import Payment, PaymentStatus, PaymentType
from src.models.vaccination_record import VaccinationRecord


# Test database configuration
TEST_DATABASE_URL = "postgresql://postgres:postgres@localhost:5412/saas202512_test"

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Create test database tables before any tests run"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db() -> Session:
    """
    Create a fresh database session for each test
    Rolls back after test completes
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db: Session):
    """FastAPI test client with database override"""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    from src.db.session import get_db
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


# ==================== MODEL FACTORIES ====================

@pytest.fixture
def tenant_factory(db: Session):
    """Factory for creating test tenants"""
    def create_tenant(**kwargs):
        defaults = {
            "id": uuid4(),
            "name": "Test Clinic",
            "subdomain": f"testclinic{uuid4().hex[:8]}",
            "is_active": True
        }
        defaults.update(kwargs)
        tenant = Tenant(**defaults)
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
        return tenant
    return create_tenant


@pytest.fixture
def tenant(tenant_factory):
    """Default test tenant"""
    return tenant_factory()


@pytest.fixture
def owner_factory(db: Session):
    """Factory for creating test owners"""
    def create_owner(tenant_id, **kwargs):
        defaults = {
            "id": uuid4(),
            "tenant_id": tenant_id,
            "first_name": "John",
            "last_name": "Doe",
            "email": f"test{uuid4().hex[:8]}@example.com",
            "phone": f"+1{uuid4().hex[:10]}",
            "sms_opted_in": True,
            "reputation_score": 100,
            "no_show_count": 0,
            "late_cancellation_count": 0,
            "completed_appointment_count": 0
        }
        defaults.update(kwargs)
        owner = Owner(**defaults)
        db.add(owner)
        db.commit()
        db.refresh(owner)
        return owner
    return create_owner


@pytest.fixture
def owner(owner_factory, tenant):
    """Default test owner"""
    return owner_factory(tenant.id)


@pytest.fixture
def staff_factory(db: Session):
    """Factory for creating test staff members"""
    def create_staff(tenant_id, **kwargs):
        defaults = {
            "id": uuid4(),
            "tenant_id": tenant_id,
            "first_name": "Jane",
            "last_name": "Smith",
            "email": f"staff{uuid4().hex[:8]}@clinic.com",
            "role": "groomer"
        }
        defaults.update(kwargs)
        staff = Staff(**defaults)
        db.add(staff)
        db.commit()
        db.refresh(staff)
        return staff
    return create_staff


@pytest.fixture
def staff(staff_factory, tenant):
    """Default test staff member"""
    return staff_factory(tenant.id)


@pytest.fixture
def service_factory(db: Session):
    """Factory for creating test services"""
    def create_service(tenant_id, **kwargs):
        defaults = {
            "id": uuid4(),
            "tenant_id": tenant_id,
            "name": "Dog Grooming",
            "duration_minutes": 60,
            "price": 5000  # $50
        }
        defaults.update(kwargs)
        service = Service(**defaults)
        db.add(service)
        db.commit()
        db.refresh(service)
        return service
    return create_service


@pytest.fixture
def service(service_factory, tenant):
    """Default test service"""
    return service_factory(tenant.id)


@pytest.fixture
def pet_factory(db: Session):
    """Factory for creating test pets"""
    def create_pet(tenant_id, owner_id, **kwargs):
        defaults = {
            "id": uuid4(),
            "tenant_id": tenant_id,
            "owner_id": owner_id,
            "name": "Buddy",
            "species": "Dog",
            "breed": "Golden Retriever"
        }
        defaults.update(kwargs)
        pet = Pet(**defaults)
        db.add(pet)
        db.commit()
        db.refresh(pet)
        return pet
    return create_pet


@pytest.fixture
def pet(pet_factory, tenant, owner):
    """Default test pet"""
    return pet_factory(tenant.id, owner.id)


@pytest.fixture
def appointment_factory(db: Session):
    """Factory for creating test appointments"""
    def create_appointment(tenant_id, owner_id, staff_id, service_id, **kwargs):
        scheduled_start = datetime.utcnow() + timedelta(days=1)
        defaults = {
            "id": uuid4(),
            "tenant_id": tenant_id,
            "owner_id": owner_id,
            "staff_id": staff_id,
            "service_id": service_id,
            "status": AppointmentStatus.CONFIRMED,
            "scheduled_start": scheduled_start,
            "scheduled_end": scheduled_start + timedelta(hours=1),
            "is_no_show": False
        }
        defaults.update(kwargs)
        appointment = Appointment(**defaults)
        db.add(appointment)
        db.commit()
        db.refresh(appointment)
        return appointment
    return create_appointment


@pytest.fixture
def appointment(appointment_factory, tenant, owner, staff, service):
    """Default test appointment"""
    return appointment_factory(tenant.id, owner.id, staff.id, service.id)


@pytest.fixture
def payment_factory(db: Session):
    """Factory for creating test payments"""
    def create_payment(tenant_id, owner_id, **kwargs):
        defaults = {
            "id": uuid4(),
            "tenant_id": tenant_id,
            "owner_id": owner_id,
            "amount": 5000,
            "status": PaymentStatus.SUCCEEDED,
            "type": PaymentType.FULL_PAYMENT,
            "method": "card",
            "net_amount": 5000,
            "created_at": datetime.utcnow()
        }
        defaults.update(kwargs)
        payment = Payment(**defaults)
        db.add(payment)
        db.commit()
        db.refresh(payment)
        return payment
    return create_payment


@pytest.fixture
def payment(payment_factory, tenant, owner):
    """Default test payment"""
    return payment_factory(tenant.id, owner.id)


@pytest.fixture
def vaccination_factory(db: Session):
    """Factory for creating test vaccination records"""
    def create_vaccination(tenant_id, pet_id, **kwargs):
        defaults = {
            "id": uuid4(),
            "tenant_id": tenant_id,
            "pet_id": pet_id,
            "vaccination_type": "Rabies",
            "administered_date": date.today() - timedelta(days=335),
            "expiry_date": date.today() + timedelta(days=30),
            "is_current": True,
            "alert_count": 0
        }
        defaults.update(kwargs)
        vaccination = VaccinationRecord(**defaults)
        db.add(vaccination)
        db.commit()
        db.refresh(vaccination)
        return vaccination
    return create_vaccination


@pytest.fixture
def vaccination(vaccination_factory, tenant, pet):
    """Default test vaccination record"""
    return vaccination_factory(tenant.id, pet.id)


# ==================== SCENARIO FIXTURES ====================

@pytest.fixture
def past_appointment_no_show(appointment_factory, tenant, owner, staff, service):
    """Appointment that should be detected as no-show"""
    scheduled_time = datetime.utcnow() - timedelta(hours=2)
    return appointment_factory(
        tenant.id, owner.id, staff.id, service.id,
        status=AppointmentStatus.CONFIRMED,
        scheduled_start=scheduled_time,
        scheduled_end=scheduled_time + timedelta(hours=1),
        is_no_show=False,
        arrived_at=None
    )


@pytest.fixture
def expiring_vaccination(vaccination_factory, tenant, pet):
    """Vaccination expiring in 30 days"""
    return vaccination_factory(
        tenant.id, pet.id,
        vaccination_type="Rabies",
        expiry_date=date.today() + timedelta(days=30),
        is_current=True
    )


@pytest.fixture
def low_reputation_owner(owner_factory, tenant):
    """Owner with low reputation score"""
    return owner_factory(
        tenant.id,
        reputation_score=20,
        no_show_count=5,
        late_cancellation_count=3,
        completed_appointment_count=2
    )


@pytest.fixture
def completed_appointment_with_payment(appointment_factory, payment_factory, tenant, owner, staff, service):
    """Completed appointment with successful payment"""
    appointment = appointment_factory(
        tenant.id, owner.id, staff.id, service.id,
        status=AppointmentStatus.COMPLETED,
        scheduled_start=datetime.utcnow() - timedelta(days=1),
        scheduled_end=datetime.utcnow() - timedelta(days=1, hours=-1)
    )
    payment = payment_factory(
        tenant.id, owner.id,
        appointment_id=appointment.id,
        amount=5000,
        status=PaymentStatus.SUCCEEDED
    )
    return appointment, payment


# ==================== AUTHENTICATION FIXTURES ====================

@pytest.fixture
def auth_headers(tenant):
    """Generate authentication headers for API requests"""
    # This would normally generate a JWT token
    # For now, returning basic headers
    return {
        "Authorization": "Bearer test_token",
        "X-Tenant-ID": str(tenant.id)
    }


@pytest.fixture
def admin_headers(tenant):
    """Generate admin authentication headers"""
    return {
        "Authorization": "Bearer admin_test_token",
        "X-Tenant-ID": str(tenant.id),
        "X-User-Role": "admin"
    }


# ==================== UTILITY FIXTURES ====================

@pytest.fixture
def freeze_time():
    """Utility to freeze time for testing"""
    from unittest.mock import patch

    def _freeze(frozen_datetime):
        return patch('datetime.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = frozen_datetime
            mock_datetime.now.return_value = frozen_datetime
            yield mock_datetime

    return _freeze


@pytest.fixture
def clear_cache():
    """Clear Redis cache before test"""
    # Would implement Redis cache clearing here
    yield
    # Clean up after test
    pass
