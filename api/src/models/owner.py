"""
Owner (pet parent) model
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from ..db.base import Base


class Owner(Base):
    """
    Owner model - represents pet parents/customers
    """
    __tablename__ = "owners"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Tenant (Multi-tenant isolation)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)

    # Link to User
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Personal Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(20), nullable=False)

    # Address
    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(2), nullable=True)
    zip_code = Column(String(10), nullable=True)

    # Emergency Contact
    emergency_contact_name = Column(String(200), nullable=True)
    emergency_contact_phone = Column(String(20), nullable=True)

    # Communication Preferences
    sms_opted_in = Column(Boolean, default=True, nullable=False)
    email_opted_in = Column(Boolean, default=True, nullable=False)
    preferred_contact_method = Column(String(20), default="sms")  # sms, email, phone

    # Payment
    stripe_customer_id = Column(String(255), nullable=True, index=True)
    has_payment_method = Column(Boolean, default=False, nullable=False)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_blocked = Column(Boolean, default=False, nullable=False)  # For no-show repeat offenders

    # Metadata
    notes = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True)  # ["vip", "regular", "first-time"]

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_booking_at = Column(DateTime(timezone=True), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    tenant = relationship("Tenant", backref="owners")
    user = relationship("User", backref="owner_profile")

    def __repr__(self):
        return f"<Owner(id={self.id}, name={self.first_name} {self.last_name}, email={self.email})>"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
