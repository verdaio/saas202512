"""
Service model for grooming, training, and other services
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from ..db.base import Base


class Service(Base):
    """
    Service model - represents services offered (grooming, training, bathing, etc.)
    """
    __tablename__ = "services"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Tenant (Multi-tenant isolation)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)

    # Service Information
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)  # grooming, training, bathing, nail-trim, etc.

    # Pricing (stored in cents)
    price = Column(Integer, nullable=False)  # Base price in cents
    deposit_amount = Column(Integer, nullable=True)  # Required deposit in cents
    deposit_percentage = Column(Integer, nullable=True)  # Or percentage * 100

    # Duration (in minutes)
    duration_minutes = Column(Integer, nullable=False)

    # Buffer times (in minutes)
    setup_buffer_minutes = Column(Integer, default=0, nullable=False)
    cleanup_buffer_minutes = Column(Integer, default=0, nullable=False)

    # Capacity
    max_pets_per_session = Column(Integer, default=1, nullable=False)

    # Requirements
    requires_vaccination = Column(Boolean, default=True, nullable=False)
    vaccination_types_required = Column(JSON, nullable=True)  # ["rabies", "distemper", "bordetella"]

    # Resource requirements
    requires_table = Column(Boolean, default=False, nullable=False)
    requires_van = Column(Boolean, default=False, nullable=False)
    requires_room = Column(Boolean, default=False, nullable=False)

    # Availability
    is_active = Column(Boolean, default=True, nullable=False)
    is_bookable_online = Column(Boolean, default=True, nullable=False)

    # Staff assignment
    staff_assignment = Column(String(20), default="any")  # any, specific, prefer

    # Metadata
    color = Column(String(7), nullable=True)  # Hex color for calendar display
    icon = Column(String(50), nullable=True)
    display_order = Column(Integer, default=0, nullable=False)
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    tenant = relationship("Tenant", backref="services")

    def __repr__(self):
        return f"<Service(id={self.id}, name={self.name}, duration={self.duration_minutes}m)>"

    @property
    def total_duration_minutes(self):
        """Total duration including buffers"""
        return self.duration_minutes + self.setup_buffer_minutes + self.cleanup_buffer_minutes

    @property
    def price_display(self):
        """Price in dollars"""
        return self.price / 100.0
