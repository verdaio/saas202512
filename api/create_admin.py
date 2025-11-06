"""
Create admin user for demo tenant
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from passlib.context import CryptContext
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
DATABASE_URL = "postgresql://postgres:postgres@postgres:5432/saas202512"

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    # Get demo tenant ID
    result = conn.execute(text("SELECT id FROM tenants WHERE subdomain='demo'"))
    tenant_row = result.fetchone()

    if not tenant_row:
        print("Error: Demo tenant not found")
        sys.exit(1)

    tenant_id = tenant_row[0]

    # Check if admin user exists
    result = conn.execute(
        text("SELECT id FROM users WHERE email='admin@demo.com' AND tenant_id=:tenant_id"),
        {"tenant_id": str(tenant_id)}
    )

    if result.fetchone():
        print("Admin user already exists")
    else:
        # Create admin user
        user_id = str(uuid.uuid4())
        password_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzQfyg/3dy"  # "password123"

        conn.execute(text("""
            INSERT INTO users (id, tenant_id, email, password_hash, role, first_name, last_name, is_active, is_verified, sms_opted_in, created_at, updated_at)
            VALUES (:id, :tenant_id, :email, :password_hash, 'OWNER', :first_name, :last_name, true, true, false, NOW(), NOW())
        """), {
            "id": user_id,
            "tenant_id": str(tenant_id),
            "email": "admin@demo.com",
            "password_hash": password_hash,
            "first_name": "Admin",
            "last_name": "User"
        })

        conn.commit()
        print(f"✅ Created admin user: admin@demo.com / password123")
        print(f"   User ID: {user_id}")
        print(f"   Tenant: demo")
