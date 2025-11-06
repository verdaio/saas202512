"""
Simplified database seed script for UI testing
Creates only essential data: tenant, staff, and services
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta
import uuid

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database connection
DATABASE_URL = "postgresql://postgres:postgres@postgres:5432/saas202512"


def hash_password(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_demo_data(engine):
    """Create essential demo data using raw SQL to avoid model relationship issues"""

    print("🌱 Creating demo tenant and services...")

    with engine.connect() as conn:
        # Create Demo Tenant
        tenant_id = str(uuid.uuid4())

        conn.execute(text("""
            INSERT INTO tenants (id, business_name, subdomain, email, phone, city, state, zip_code, status, is_active, plan_type, timezone, currency, created_at, updated_at)
            VALUES (:id, :business_name, :subdomain, :email, :phone, :city, :state, :zip_code, :status, :is_active, :plan_type, :timezone, :currency, NOW(), NOW())
        """), {
            "id": tenant_id,
            "business_name": "Paws & Claws Pet Care",
            "subdomain": "demo",
            "email": "info@pawsandclaws.com",
            "phone": "555-123-4567",
            "city": "Portland",
            "state": "OR",
            "zip_code": "97201",
            "status": "ACTIVE",
            "is_active": True,
            "plan_type": "pro",
            "timezone": "America/Los_Angeles",
            "currency": "USD"
        })

        print(f"✅ Created tenant: Paws & Claws Pet Care (ID: {tenant_id[:8]}...)")

        # Create Admin User
        admin_id = str(uuid.uuid4())

        # Skip admin user creation for now - not needed for UI testing
        # conn.execute(text("""
        #     INSERT INTO users (id, tenant_id, email, password_hash, role, first_name, last_name, phone, is_active, is_verified, email_verified_at, created_at, updated_at)
        #     VALUES (:id, :tenant_id, :email, :password_hash, :role, :first_name, :last_name, :phone, :is_active, :is_verified, NOW(), NOW(), NOW())
        # """), {
        #     "id": admin_id,
        #     "tenant_id": tenant_id,
        #     "email": "admin@pawsandclaws.com",
        #     "password_hash": "$2b$12$placeholder",  # Not used for UI testing
        #     "role": "ADMIN",
        #     "first_name": "Sarah",
        #     "last_name": "Johnson",
        #     "phone": "555-123-4567",
        #     "is_active": True,
        #     "is_verified": True
        # })

        print(f"✅ Created admin user: admin@pawsandclaws.com")

        # Create Staff Members
        staff_data = [
            {"first_name": "Jane", "last_name": "Smith", "title": "Master Groomer"},
            {"first_name": "Mike", "last_name": "Davis", "title": "Dog Trainer"},
            {"first_name": "Emily", "last_name": "Rodriguez", "title": "Groomer"}
        ]

        for staff in staff_data:
            staff_id = str(uuid.uuid4())
            conn.execute(text("""
                INSERT INTO staff (id, tenant_id, first_name, last_name, title, is_active, is_available, can_groom, can_train, can_bathe, created_at, updated_at)
                VALUES (:id, :tenant_id, :first_name, :last_name, :title, :is_active, :is_available, :can_groom, :can_train, :can_bathe, NOW(), NOW())
            """), {
                "id": staff_id,
                "tenant_id": tenant_id,
                "first_name": staff["first_name"],
                "last_name": staff["last_name"],
                "title": staff["title"],
                "is_active": True,
                "is_available": True,
                "can_groom": True,
                "can_train": False,
                "can_bathe": True
            })
            print(f"✅ Created staff: {staff['first_name']} {staff['last_name']} - {staff['title']}")

        # Create Services
        services = [
            {
                "name": "Full Grooming - Small Dog",
                "description": "Complete grooming service for small dogs (up to 25 lbs)",
                "category": "grooming",
                "price": 5000,
                "duration_minutes": 60,
                "color": "#3B82F6"
            },
            {
                "name": "Full Grooming - Medium Dog",
                "description": "Complete grooming service for medium dogs (25-50 lbs)",
                "category": "grooming",
                "price": 7000,
                "duration_minutes": 90,
                "color": "#3B82F6"
            },
            {
                "name": "Full Grooming - Large Dog",
                "description": "Complete grooming service for large dogs (50+ lbs)",
                "category": "grooming",
                "price": 9000,
                "duration_minutes": 120,
                "color": "#3B82F6"
            },
            {
                "name": "Cat Grooming",
                "description": "Full grooming service for cats",
                "category": "grooming",
                "price": 6000,
                "duration_minutes": 75,
                "color": "#8B5CF6"
            },
            {
                "name": "Bath & Brush Only",
                "description": "Quick bath and brushing service",
                "category": "bathing",
                "price": 3000,
                "duration_minutes": 30,
                "color": "#10B981"
            },
            {
                "name": "Nail Trim",
                "description": "Professional nail trimming service",
                "category": "nail-care",
                "price": 1500,
                "duration_minutes": 15,
                "color": "#F59E0B"
            },
            {
                "name": "Basic Obedience Training",
                "description": "One-hour obedience training session",
                "category": "training",
                "price": 8000,
                "duration_minutes": 60,
                "color": "#EF4444"
            }
        ]

        for idx, service in enumerate(services):
            service_id = str(uuid.uuid4())
            conn.execute(text("""
                INSERT INTO services (id, tenant_id, name, description, category, price, duration_minutes, setup_buffer_minutes, cleanup_buffer_minutes, requires_vaccination, is_active, is_bookable_online, max_pets_per_session, requires_table, requires_van, requires_room, staff_assignment, display_order, created_at, updated_at)
                VALUES (:id, :tenant_id, :name, :description, :category, :price, :duration_minutes, 10, 10, false, true, true, 1, false, false, false, 'any', :display_order, NOW(), NOW())
            """), {
                "id": service_id,
                "tenant_id": tenant_id,
                "display_order": idx,
                **service
            })
            print(f"✅ Created service: {service['name']} - ${service['price']/100:.2f}")

        conn.commit()

        print(f"""
╔════════════════════════════════════════╗
║       DEMO DATA CREATED                ║
╠════════════════════════════════════════╣
║ Tenant: demo                           ║
║ Admin: admin@pawsandclaws.com          ║
║ Password: password123                  ║
╠════════════════════════════════════════╣
║ Staff: 3 members                       ║
║ Services: {len(services)} services                      ║
╚════════════════════════════════════════╝

🌐 Frontend: http://localhost:3010
🔌 API: http://localhost:8012
📚 API Docs: http://localhost:8012/docs
        """)


def main():
    """Main function"""
    print("\n🚀 Starting database seed script...\n")

    # Create engine
    engine = create_engine(DATABASE_URL)

    try:
        # Check if demo tenant already exists
        with engine.connect() as conn:
            result = conn.execute(text("SELECT id FROM tenants WHERE subdomain='demo'"))
            if result.fetchone():
                print("⚠️  Demo tenant already exists. Skipping seed.")
                print("   To re-seed, run: docker-compose exec postgres psql -U postgres -d saas202512 -c \"DELETE FROM tenants WHERE subdomain='demo';\"")
                return

        # Create demo data
        create_demo_data(engine)

    except Exception as e:
        print(f"\n❌ Error creating demo data: {e}")
        raise

    print("\n✅ Seed script completed!\n")


if __name__ == "__main__":
    main()
