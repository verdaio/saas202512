"""initial schema

Revision ID: 001
Revises:
Create Date: 2025-11-03 14:47:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create tenants table
    op.create_table('tenants',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('business_name', sa.String(length=255), nullable=False),
        sa.Column('subdomain', sa.String(length=63), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('address_line1', sa.String(length=255), nullable=True),
        sa.Column('address_line2', sa.String(length=255), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('state', sa.String(length=2), nullable=True),
        sa.Column('zip_code', sa.String(length=10), nullable=True),
        sa.Column('timezone', sa.String(length=50), nullable=True),
        sa.Column('currency', sa.String(length=3), nullable=True),
        sa.Column('status', sa.Enum('ACTIVE', 'SUSPENDED', 'TRIAL', 'INACTIVE', name='tenantstatus'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('plan_type', sa.String(length=50), nullable=True),
        sa.Column('subscription_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('settings', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tenants_subdomain'), 'tenants', ['subdomain'], unique=True)

    # Create users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.Enum('OWNER', 'ADMIN', 'STAFF', 'CUSTOMER', name='userrole'), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_verified', sa.Boolean(), nullable=False),
        sa.Column('email_verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('sms_opted_in', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=False)
    op.create_index(op.f('ix_users_tenant_id'), 'users', ['tenant_id'], unique=False)

    # Create staff table
    op.create_table('staff',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('title', sa.String(length=100), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('skills', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_available', sa.Boolean(), nullable=False),
        sa.Column('schedule', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('can_groom', sa.Boolean(), nullable=False),
        sa.Column('can_train', sa.Boolean(), nullable=False),
        sa.Column('can_bathe', sa.Boolean(), nullable=False),
        sa.Column('commission_rate', sa.Integer(), nullable=True),
        sa.Column('hourly_rate', sa.Integer(), nullable=True),
        sa.Column('photo_url', sa.String(length=500), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_staff_tenant_id'), 'staff', ['tenant_id'], unique=False)

    # Create owners table
    op.create_table('owners',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=False),
        sa.Column('address_line1', sa.String(length=255), nullable=True),
        sa.Column('address_line2', sa.String(length=255), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('state', sa.String(length=2), nullable=True),
        sa.Column('zip_code', sa.String(length=10), nullable=True),
        sa.Column('emergency_contact_name', sa.String(length=200), nullable=True),
        sa.Column('emergency_contact_phone', sa.String(length=20), nullable=True),
        sa.Column('sms_opted_in', sa.Boolean(), nullable=False),
        sa.Column('email_opted_in', sa.Boolean(), nullable=False),
        sa.Column('preferred_contact_method', sa.String(length=20), nullable=True),
        sa.Column('stripe_customer_id', sa.String(length=255), nullable=True),
        sa.Column('has_payment_method', sa.Boolean(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_blocked', sa.Boolean(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_booking_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_owners_email'), 'owners', ['email'], unique=False)
    op.create_index(op.f('ix_owners_stripe_customer_id'), 'owners', ['stripe_customer_id'], unique=False)
    op.create_index(op.f('ix_owners_tenant_id'), 'owners', ['tenant_id'], unique=False)

    # Create pets table
    op.create_table('pets',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('species', sa.String(length=50), nullable=False),
        sa.Column('breed', sa.String(length=100), nullable=True),
        sa.Column('gender', sa.Enum('MALE', 'FEMALE', 'UNKNOWN', name='petgender'), nullable=True),
        sa.Column('color', sa.String(length=100), nullable=True),
        sa.Column('weight', sa.Integer(), nullable=True),
        sa.Column('date_of_birth', sa.Date(), nullable=True),
        sa.Column('age_years', sa.Integer(), nullable=True),
        sa.Column('age_months', sa.Integer(), nullable=True),
        sa.Column('microchip_number', sa.String(length=50), nullable=True),
        sa.Column('license_number', sa.String(length=50), nullable=True),
        sa.Column('allergies', sa.Text(), nullable=True),
        sa.Column('medical_conditions', sa.Text(), nullable=True),
        sa.Column('medications', sa.Text(), nullable=True),
        sa.Column('veterinarian_name', sa.String(length=200), nullable=True),
        sa.Column('veterinarian_phone', sa.String(length=20), nullable=True),
        sa.Column('temperament', sa.Text(), nullable=True),
        sa.Column('special_instructions', sa.Text(), nullable=True),
        sa.Column('is_aggressive', sa.Boolean(), nullable=False),
        sa.Column('needs_muzzle', sa.Boolean(), nullable=False),
        sa.Column('vaccination_status', sa.String(length=20), nullable=True),
        sa.Column('vaccination_expires_at', sa.Date(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_deceased', sa.Boolean(), nullable=False),
        sa.Column('photo_url', sa.String(length=500), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['owners.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pets_owner_id'), 'pets', ['owner_id'], unique=False)
    op.create_index(op.f('ix_pets_tenant_id'), 'pets', ['tenant_id'], unique=False)

    # Create services table
    op.create_table('services',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('price', sa.Integer(), nullable=False),
        sa.Column('deposit_amount', sa.Integer(), nullable=True),
        sa.Column('deposit_percentage', sa.Integer(), nullable=True),
        sa.Column('duration_minutes', sa.Integer(), nullable=False),
        sa.Column('setup_buffer_minutes', sa.Integer(), nullable=False),
        sa.Column('cleanup_buffer_minutes', sa.Integer(), nullable=False),
        sa.Column('max_pets_per_session', sa.Integer(), nullable=False),
        sa.Column('requires_vaccination', sa.Boolean(), nullable=False),
        sa.Column('vaccination_types_required', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('requires_table', sa.Boolean(), nullable=False),
        sa.Column('requires_van', sa.Boolean(), nullable=False),
        sa.Column('requires_room', sa.Boolean(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_bookable_online', sa.Boolean(), nullable=False),
        sa.Column('staff_assignment', sa.String(length=20), nullable=True),
        sa.Column('color', sa.String(length=7), nullable=True),
        sa.Column('icon', sa.String(length=50), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_services_tenant_id'), 'services', ['tenant_id'], unique=False)

    # Create resources table
    op.create_table('resources',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('type', sa.Enum('TABLE', 'VAN', 'ROOM', 'CAGE', 'OTHER', name='resourcetype'), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('capacity', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_bookable', sa.Boolean(), nullable=False),
        sa.Column('schedule', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('travel_time_minutes', sa.Integer(), nullable=False),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('color', sa.String(length=7), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_resources_tenant_id'), 'resources', ['tenant_id'], unique=False)

    # Create payments table (must be before appointments and packages that reference it)
    op.create_table('payments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('appointment_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('package_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('type', sa.Enum('DEPOSIT', 'FULL_PAYMENT', 'TIP', 'PACKAGE', 'GIFT_CARD', 'NO_SHOW_FEE', 'REFUND', name='paymenttype'), nullable=False),
        sa.Column('method', sa.Enum('CARD', 'CASH', 'CHECK', 'OTHER', name='paymentmethod'), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'PROCESSING', 'SUCCEEDED', 'FAILED', 'CANCELLED', 'REFUNDED', 'PARTIALLY_REFUNDED', name='paymentstatus'), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('tip_amount', sa.Integer(), nullable=False),
        sa.Column('refund_amount', sa.Integer(), nullable=False),
        sa.Column('net_amount', sa.Integer(), nullable=False),
        sa.Column('stripe_payment_intent_id', sa.String(length=255), nullable=True),
        sa.Column('stripe_charge_id', sa.String(length=255), nullable=True),
        sa.Column('stripe_refund_id', sa.String(length=255), nullable=True),
        sa.Column('stripe_customer_id', sa.String(length=255), nullable=True),
        sa.Column('stripe_payment_method_id', sa.String(length=255), nullable=True),
        sa.Column('card_last4', sa.String(length=4), nullable=True),
        sa.Column('card_brand', sa.String(length=20), nullable=True),
        sa.Column('card_exp_month', sa.Integer(), nullable=True),
        sa.Column('card_exp_year', sa.Integer(), nullable=True),
        sa.Column('processor_response', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('failure_code', sa.String(length=100), nullable=True),
        sa.Column('failure_message', sa.Text(), nullable=True),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('succeeded_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('failed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('refunded_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('receipt_email', sa.String(length=255), nullable=True),
        sa.Column('receipt_url', sa.String(length=500), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['owners.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_payments_owner_id'), 'payments', ['owner_id'], unique=False)
    op.create_index(op.f('ix_payments_stripe_payment_intent_id'), 'payments', ['stripe_payment_intent_id'], unique=True)
    op.create_index(op.f('ix_payments_tenant_id'), 'payments', ['tenant_id'], unique=False)

    # Now create appointments table (references payments)
    op.create_table('appointments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('pet_ids', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=False),
        sa.Column('service_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('staff_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('scheduled_start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('scheduled_end', sa.DateTime(timezone=True), nullable=False),
        sa.Column('actual_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('actual_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'CONFIRMED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED', 'NO_SHOW', name='appointmentstatus'), nullable=False),
        sa.Column('source', sa.Enum('ONLINE', 'PHONE', 'WALK_IN', 'ADMIN', name='appointmentsource'), nullable=False),
        sa.Column('confirmed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('confirmation_sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('reminder_24h_sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('reminder_2h_sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deposit_required', sa.Integer(), nullable=True),
        sa.Column('deposit_paid', sa.Integer(), nullable=False),
        sa.Column('total_amount', sa.Integer(), nullable=False),
        sa.Column('amount_paid', sa.Integer(), nullable=False),
        sa.Column('tip_amount', sa.Integer(), nullable=False),
        sa.Column('customer_notes', sa.Text(), nullable=True),
        sa.Column('staff_notes', sa.Text(), nullable=True),
        sa.Column('special_instructions', sa.Text(), nullable=True),
        sa.Column('before_photos', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('after_photos', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('vaccination_verified', sa.Boolean(), nullable=False),
        sa.Column('vaccination_override', sa.Boolean(), nullable=False),
        sa.Column('vaccination_override_reason', sa.Text(), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancellation_reason', sa.Text(), nullable=True),
        sa.Column('cancelled_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('no_show_fee_charged', sa.Integer(), nullable=False),
        sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('custom_fields', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['owners.id'], ),
        sa.ForeignKeyConstraint(['resource_id'], ['resources.id'], ),
        sa.ForeignKeyConstraint(['service_id'], ['services.id'], ),
        sa.ForeignKeyConstraint(['staff_id'], ['staff.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_appointments_owner_id'), 'appointments', ['owner_id'], unique=False)
    op.create_index(op.f('ix_appointments_scheduled_start'), 'appointments', ['scheduled_start'], unique=False)
    op.create_index(op.f('ix_appointments_staff_id'), 'appointments', ['staff_id'], unique=False)
    op.create_index(op.f('ix_appointments_tenant_id'), 'appointments', ['tenant_id'], unique=False)

    # Add foreign key from payments to appointments (circular reference handled via nullable)
    op.create_foreign_key('fk_payments_appointment', 'payments', 'appointments', ['appointment_id'], ['id'])

    # Create packages table
    op.create_table('packages',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('type', sa.Enum('PUNCH_CARD', 'CLASS_CREDITS', 'MEMBERSHIP', 'GIFT_CARD', name='packagetype'), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('price_paid', sa.Integer(), nullable=False),
        sa.Column('value', sa.Integer(), nullable=True),
        sa.Column('total_credits', sa.Integer(), nullable=False),
        sa.Column('remaining_credits', sa.Integer(), nullable=False),
        sa.Column('unlimited', sa.Boolean(), nullable=False),
        sa.Column('valid_from', sa.DateTime(timezone=True), nullable=True),
        sa.Column('valid_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('never_expires', sa.Boolean(), nullable=False),
        sa.Column('status', sa.Enum('ACTIVE', 'EXHAUSTED', 'EXPIRED', 'CANCELLED', name='packagestatus'), nullable=False),
        sa.Column('payment_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('stripe_payment_intent_id', sa.String(length=255), nullable=True),
        sa.Column('first_used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('gift_code', sa.String(length=50), nullable=True),
        sa.Column('recipient_name', sa.String(length=200), nullable=True),
        sa.Column('recipient_email', sa.String(length=255), nullable=True),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['owners.id'], ),
        sa.ForeignKeyConstraint(['payment_id'], ['payments.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_packages_gift_code'), 'packages', ['gift_code'], unique=True)
    op.create_index(op.f('ix_packages_owner_id'), 'packages', ['owner_id'], unique=False)
    op.create_index(op.f('ix_packages_tenant_id'), 'packages', ['tenant_id'], unique=False)

    # Add foreign key from payments to packages
    op.create_foreign_key('fk_payments_package', 'payments', 'packages', ['package_id'], ['id'])

    # Create vaccination_records table
    op.create_table('vaccination_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('pet_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('type', sa.Enum('RABIES', 'DISTEMPER', 'PARVO', 'BORDETELLA', 'LEUKEMIA', 'LYME', 'DHPP', 'FVRCP', 'OTHER', name='vaccinationtype'), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=True),
        sa.Column('status', sa.Enum('CURRENT', 'EXPIRING_SOON', 'EXPIRED', 'UNKNOWN', name='vaccinationstatus'), nullable=False),
        sa.Column('administered_date', sa.Date(), nullable=False),
        sa.Column('expiry_date', sa.Date(), nullable=False),
        sa.Column('reminder_sent_30d', sa.Boolean(), nullable=False),
        sa.Column('reminder_sent_14d', sa.Boolean(), nullable=False),
        sa.Column('reminder_sent_7d', sa.Boolean(), nullable=False),
        sa.Column('veterinarian_name', sa.String(length=200), nullable=True),
        sa.Column('veterinarian_clinic', sa.String(length=200), nullable=True),
        sa.Column('veterinarian_phone', sa.String(length=20), nullable=True),
        sa.Column('license_number', sa.String(length=100), nullable=True),
        sa.Column('certificate_url', sa.String(length=500), nullable=True),
        sa.Column('lot_number', sa.String(length=100), nullable=True),
        sa.Column('manufacturer', sa.String(length=200), nullable=True),
        sa.Column('verified_by_staff', sa.Boolean(), nullable=False),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('verified_by_user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['pet_id'], ['pets.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.ForeignKeyConstraint(['verified_by_user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_vaccination_records_pet_id'), 'vaccination_records', ['pet_id'], unique=False)
    op.create_index(op.f('ix_vaccination_records_tenant_id'), 'vaccination_records', ['tenant_id'], unique=False)


def downgrade() -> None:
    op.drop_table('vaccination_records')
    op.drop_table('packages')
    op.drop_table('appointments')
    op.drop_table('payments')
    op.drop_table('resources')
    op.drop_table('services')
    op.drop_table('pets')
    op.drop_table('owners')
    op.drop_table('staff')
    op.drop_table('users')
    op.drop_table('tenants')
