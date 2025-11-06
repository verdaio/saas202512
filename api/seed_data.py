"""
Database seed script with mock data for testing
Creates a demo tenant with services, staff, owners, and pets
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta, date
import uuid

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

from src.db.base import Base
from src.models.tenant import Tenant, TenantStatus
from src.models.user import User, UserRole
from src.models.service import Service
from src.models.staff import Staff
from src.models.owner import Owner
from src.models.pet import Pet, PetGender

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database connection
DATABASE_URL = "postgresql://postgres:postgres@localhost:5412/saas202512"


def hash_password(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_demo_data(db):
    """Create comprehensive demo data"""

    print("🌱 Creating demo tenant...")

    # 1. Create Demo Tenant
    tenant = Tenant(
        id=uuid.uuid4(),
        business_name="Paws & Claws Pet Care",
        subdomain="demo",
        email="info@pawsandclaws.com",
        phone="555-123-4567",
        address_line1="123 Pet Street",
        city="Portland",
        state="OR",
        zip_code="97201",
        status=TenantStatus.ACTIVE,
        is_active=True,
        plan_type="pro",
        timezone="America/Los_Angeles",
        currency="USD"
    )
    db.add(tenant)
    db.flush()

    print(f"✅ Created tenant: {tenant.business_name} (subdomain: {tenant.subdomain})")

    # 2. Create Admin User
    admin_user = User(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        email="admin@pawsandclaws.com",
        password_hash=hash_password("password123"),
        role=UserRole.ADMIN,
        first_name="Sarah",
        last_name="Johnson",
        phone="555-123-4567",
        is_active=True,
        is_verified=True,
        email_verified_at=datetime.utcnow()
    )
    db.add(admin_user)
    db.flush()

    print(f"✅ Created admin user: {admin_user.email}")

    # 3. Create Staff Members
    staff_members = [
        {
            "first_name": "Jane",
            "last_name": "Smith",
            "title": "Master Groomer",
            "email": "jane@pawsandclaws.com",
            "phone": "555-234-5678",
            "can_groom": True,
            "can_bathe": True,
            "can_train": False,
            "commission_rate": 4000,  # 40%
            "schedule": {
                "monday": {"start": "09:00", "end": "17:00"},
                "tuesday": {"start": "09:00", "end": "17:00"},
                "wednesday": {"start": "09:00", "end": "17:00"},
                "thursday": {"start": "09:00", "end": "17:00"},
                "friday": {"start": "09:00", "end": "17:00"}
            }
        },
        {
            "first_name": "Mike",
            "last_name": "Davis",
            "title": "Dog Trainer",
            "email": "mike@pawsandclaws.com",
            "phone": "555-345-6789",
            "can_groom": False,
            "can_bathe": False,
            "can_train": True,
            "commission_rate": 5000,  # 50%
            "schedule": {
                "monday": {"start": "10:00", "end": "18:00"},
                "tuesday": {"start": "10:00", "end": "18:00"},
                "wednesday": {"start": "10:00", "end": "18:00"},
                "thursday": {"start": "10:00", "end": "18:00"},
                "friday": {"start": "10:00", "end": "18:00"}
            }
        },
        {
            "first_name": "Emily",
            "last_name": "Rodriguez",
            "title": "Groomer",
            "email": "emily@pawsandclaws.com",
            "phone": "555-456-7890",
            "can_groom": True,
            "can_bathe": True,
            "can_train": False,
            "commission_rate": 3500,  # 35%
            "schedule": {
                "monday": {"start": "08:00", "end": "16:00"},
                "tuesday": {"start": "08:00", "end": "16:00"},
                "wednesday": {"start": "08:00", "end": "16:00"},
                "thursday": {"start": "08:00", "end": "16:00"},
                "friday": {"start": "08:00", "end": "16:00"}
            }
        }
    ]

    for staff_data in staff_members:
        staff = Staff(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            **staff_data
        )
        db.add(staff)
        print(f"✅ Created staff: {staff.full_name} - {staff.title}")

    db.flush()

    # 4. Create Services
    services = [
        {
            "name": "Full Grooming - Small Dog",
            "description": "Complete grooming service for small dogs (up to 25 lbs)",
            "category": "grooming",
            "price": 5000,  # $50.00
            "duration_minutes": 60,
            "setup_buffer_minutes": 10,
            "cleanup_buffer_minutes": 10,
            "requires_vaccination": True,
            "vaccination_types_required": ["rabies", "bordetella"],
            "color": "#3B82F6"
        },
        {
            "name": "Full Grooming - Medium Dog",
            "description": "Complete grooming service for medium dogs (25-50 lbs)",
            "category": "grooming",
            "price": 7000,  # $70.00
            "duration_minutes": 90,
            "setup_buffer_minutes": 10,
            "cleanup_buffer_minutes": 15,
            "requires_vaccination": True,
            "vaccination_types_required": ["rabies", "bordetella"],
            "color": "#3B82F6"
        },
        {
            "name": "Full Grooming - Large Dog",
            "description": "Complete grooming service for large dogs (50+ lbs)",
            "category": "grooming",
            "price": 9000,  # $90.00
            "duration_minutes": 120,
            "setup_buffer_minutes": 15,
            "cleanup_buffer_minutes": 15,
            "requires_vaccination": True,
            "vaccination_types_required": ["rabies", "bordetella"],
            "color": "#3B82F6"
        },
        {
            "name": "Cat Grooming",
            "description": "Full grooming service for cats",
            "category": "grooming",
            "price": 6000,  # $60.00
            "duration_minutes": 75,
            "setup_buffer_minutes": 10,
            "cleanup_buffer_minutes": 10,
            "requires_vaccination": True,
            "vaccination_types_required": ["rabies"],
            "color": "#8B5CF6"
        },
        {
            "name": "Bath & Brush Only",
            "description": "Quick bath and brushing service",
            "category": "bathing",
            "price": 3000,  # $30.00
            "duration_minutes": 30,
            "setup_buffer_minutes": 5,
            "cleanup_buffer_minutes": 10,
            "requires_vaccination": True,
            "vaccination_types_required": ["rabies"],
            "color": "#10B981"
        },
        {
            "name": "Nail Trim",
            "description": "Professional nail trimming service",
            "category": "nail-care",
            "price": 1500,  # $15.00
            "duration_minutes": 15,
            "setup_buffer_minutes": 5,
            "cleanup_buffer_minutes": 5,
            "requires_vaccination": False,
            "color": "#F59E0B"
        },
        {
            "name": "Basic Obedience Training (1 Session)",
            "description": "One-hour obedience training session",
            "category": "training",
            "price": 8000,  # $80.00
            "duration_minutes": 60,
            "setup_buffer_minutes": 10,
            "cleanup_buffer_minutes": 10,
            "requires_vaccination": True,
            "vaccination_types_required": ["rabies", "bordetella"],
            "color": "#EF4444"
        },
        {
            "name": "Puppy Training Package (4 Sessions)",
            "description": "Four-session puppy training program",
            "category": "training",
            "price": 28000,  # $280.00
            "duration_minutes": 60,
            "setup_buffer_minutes": 10,
            "cleanup_buffer_minutes": 10,
            "requires_vaccination": True,
            "vaccination_types_required": ["rabies", "bordetella", "distemper"],
            "color": "#EF4444"
        }
    ]

    for service_data in services:
        service = Service(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            **service_data
        )
        db.add(service)
        print(f"✅ Created service: {service.name} - ${service.price_display}")

    db.flush()

    # 5. Create Demo Owners (Pet Parents)
    owners_data = [
        {
            "first_name": "John",
            "last_name": "Anderson",
            "email": "john.anderson@email.com",
            "phone": "555-111-2222",
            "address_line1": "456 Oak Avenue",
            "city": "Portland",
            "state": "OR",
            "zip_code": "97202",
            "sms_opted_in": True,
            "email_opted_in": True
        },
        {
            "first_name": "Maria",
            "last_name": "Garcia",
            "email": "maria.garcia@email.com",
            "phone": "555-222-3333",
            "address_line1": "789 Pine Street",
            "city": "Portland",
            "state": "OR",
            "zip_code": "97203",
            "sms_opted_in": True,
            "email_opted_in": True
        },
        {
            "first_name": "David",
            "last_name": "Chen",
            "email": "david.chen@email.com",
            "phone": "555-333-4444",
            "address_line1": "321 Maple Drive",
            "city": "Portland",
            "state": "OR",
            "zip_code": "97204",
            "sms_opted_in": True,
            "email_opted_in": False
        },
        {
            "first_name": "Lisa",
            "last_name": "Thompson",
            "email": "lisa.thompson@email.com",
            "phone": "555-444-5555",
            "address_line1": "654 Elm Boulevard",
            "city": "Portland",
            "state": "OR",
            "zip_code": "97205",
            "sms_opted_in": False,
            "email_opted_in": True
        }
    ]

    created_owners = []
    for owner_data in owners_data:
        owner = Owner(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            **owner_data
        )
        db.add(owner)
        created_owners.append(owner)
        print(f"✅ Created owner: {owner.full_name}")

    db.flush()

    # 6. Create Demo Pets
    pets_data = [
        # John Anderson's pets
        {
            "owner_idx": 0,
            "name": "Max",
            "species": "dog",
            "breed": "Golden Retriever",
            "gender": PetGender.MALE,
            "color": "Golden",
            "weight": 65,
            "age_years": 3,
            "vaccination_status": "current",
            "vaccination_expires_at": date.today() + timedelta(days=180)
        },
        {
            "owner_idx": 0,
            "name": "Bella",
            "species": "dog",
            "breed": "Labrador",
            "gender": PetGender.FEMALE,
            "color": "Black",
            "weight": 55,
            "age_years": 2,
            "vaccination_status": "current",
            "vaccination_expires_at": date.today() + timedelta(days=90)
        },
        # Maria Garcia's pets
        {
            "owner_idx": 1,
            "name": "Luna",
            "species": "cat",
            "breed": "Persian",
            "gender": PetGender.FEMALE,
            "color": "White",
            "weight": 10,
            "age_years": 4,
            "vaccination_status": "current",
            "vaccination_expires_at": date.today() + timedelta(days=200)
        },
        # David Chen's pets
        {
            "owner_idx": 2,
            "name": "Rocky",
            "species": "dog",
            "breed": "German Shepherd",
            "gender": PetGender.MALE,
            "color": "Black and Tan",
            "weight": 80,
            "age_years": 5,
            "vaccination_status": "current",
            "vaccination_expires_at": date.today() + timedelta(days=150)
        },
        {
            "owner_idx": 2,
            "name": "Daisy",
            "species": "dog",
            "breed": "Beagle",
            "gender": PetGender.FEMALE,
            "color": "Tri-color",
            "weight": 25,
            "age_years": 1,
            "age_months": 6,
            "vaccination_status": "current",
            "vaccination_expires_at": date.today() + timedelta(days=120)
        },
        # Lisa Thompson's pets
        {
            "owner_idx": 3,
            "name": "Charlie",
            "species": "dog",
            "breed": "Poodle",
            "gender": PetGender.MALE,
            "color": "White",
            "weight": 45,
            "age_years": 6,
            "vaccination_status": "current",
            "vaccination_expires_at": date.today() + timedelta(days=60),
            "special_instructions": "Sensitive to loud noises"
        },
        {
            "owner_idx": 3,
            "name": "Mittens",
            "species": "cat",
            "breed": "Tabby",
            "gender": PetGender.FEMALE,
            "color": "Orange",
            "weight": 12,
            "age_years": 7,
            "vaccination_status": "expired",
            "vaccination_expires_at": date.today() - timedelta(days=30)
        }
    ]

    for pet_data in pets_data:
        owner_idx = pet_data.pop("owner_idx")
        pet = Pet(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            owner_id=created_owners[owner_idx].id,
            **pet_data
        )
        db.add(pet)
        print(f"✅ Created pet: {pet.name} ({pet.breed}) - Owner: {created_owners[owner_idx].full_name}")

    db.commit()
    print("\n🎉 Demo data created successfully!")
    print(f"""
    ╔════════════════════════════════════════╗
    ║       DEMO DATA SUMMARY                ║
    ╠════════════════════════════════════════╣
    ║ Tenant: {tenant.subdomain}                           ║
    ║ Admin: {admin_user.email}      ║
    ║ Password: password123                  ║
    ╠════════════════════════════════════════╣
    ║ Staff: {len(staff_members)} members                      ║
    ║ Services: {len(services)} services                 ║
    ║ Owners: {len(owners_data)} customers                     ║
    ║ Pets: {len(pets_data)} pets                          ║
    ╚════════════════════════════════════════╝

    🌐 Access the UI at: http://localhost:3010
    🔌 API available at: http://localhost:8012
    📚 API Docs: http://localhost:8012/docs
    """)


def main():
    """Main function"""
    print("\n🚀 Starting database seed script...\n")

    # Create engine and session
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db = Session()

    try:
        # Check if demo tenant already exists
        existing = db.query(Tenant).filter(Tenant.subdomain == "demo").first()
        if existing:
            print("⚠️  Demo tenant already exists. Skipping seed.")
            print(f"   If you want to re-seed, delete the tenant first:")
            print(f"   psql -h localhost -p 5412 -U postgres -d saas202512")
            print(f"   DELETE FROM tenants WHERE subdomain='demo';")
            db.close()
            return

        # Create demo data
        create_demo_data(db)

    except Exception as e:
        print(f"\n❌ Error creating demo data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

    print("\n✅ Seed script completed!\n")


if __name__ == "__main__":
    main()
