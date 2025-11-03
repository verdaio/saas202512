"""
Tenant model for multi-tenant architecture
"""
from sqlalchemy import Column, String, Boolean, DateTime, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum

from ..db.base import Base


class TenantStatus(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TRIAL = "trial"
    INACTIVE = "inactive"


class Tenant(Base):
    """
    Tenant model - represents a pet care business (salon, mobile groomer, trainer)
    """
    __tablename__ = "tenants"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Business Information
    business_name = Column(String(255), nullable=False)
    subdomain = Column(String(63), unique=True, nullable=False, index=True)

    # Contact Information
    email = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)

    # Address
    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(2), nullable=True)
    zip_code = Column(String(10), nullable=True)

    # Business Settings
    timezone = Column(String(50), default="America/New_York")
    currency = Column(String(3), default="USD")

    # Status
    status = Column(SQLEnum(TenantStatus), default=TenantStatus.TRIAL, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Subscription
    plan_type = Column(String(50), default="trial")  # trial, basic, pro, enterprise
    subscription_expires_at = Column(DateTime(timezone=True), nullable=True)

    # Metadata
    settings = Column(Text, nullable=True)  # JSON settings
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft delete

    def __repr__(self):
        return f"<Tenant(id={self.id}, business_name={self.business_name}, subdomain={self.subdomain})>"
