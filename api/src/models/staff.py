"""
Staff model for groomers, trainers, and other service providers
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from ..db.base import Base


class Staff(Base):
    """
    Staff model - represents groomers, trainers, and other service providers
    """
    __tablename__ = "staff"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Tenant (Multi-tenant isolation)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)

    # Link to User (optional - staff may not have user account)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Personal Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)

    # Employment Information
    title = Column(String(100), nullable=True)  # "Master Groomer", "Dog Trainer", etc.
    bio = Column(Text, nullable=True)
    skills = Column(JSON, nullable=True)  # ["grooming", "training", "bathing"]

    # Availability
    is_active = Column(Boolean, default=True, nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)

    # Working hours (stored as JSON)
    # Format: {"monday": {"start": "09:00", "end": "17:00", "breaks": [...]}, ...}
    schedule = Column(JSON, nullable=True)

    # Service capabilities
    can_groom = Column(Boolean, default=False, nullable=False)
    can_train = Column(Boolean, default=False, nullable=False)
    can_bathe = Column(Boolean, default=False, nullable=False)

    # Commission/Pay (stored in cents)
    commission_rate = Column(Integer, nullable=True)  # Percentage * 100 (e.g., 4000 = 40%)
    hourly_rate = Column(Integer, nullable=True)  # In cents

    # Profile
    photo_url = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    tenant = relationship("Tenant", backref="staff")
    user = relationship("User", backref="staff_profile")

    def __repr__(self):
        return f"<Staff(id={self.id}, name={self.first_name} {self.last_name})>"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
