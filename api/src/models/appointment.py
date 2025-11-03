"""
Appointment model for bookings
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, Text, JSON, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from ..db.base import Base


class AppointmentStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class AppointmentSource(str, enum.Enum):
    ONLINE = "online"
    PHONE = "phone"
    WALK_IN = "walk_in"
    ADMIN = "admin"


class Appointment(Base):
    """
    Appointment model - represents bookings/appointments
    """
    __tablename__ = "appointments"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Tenant (Multi-tenant isolation)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)

    # Related Entities
    owner_id = Column(UUID(as_uuid=True), ForeignKey("owners.id"), nullable=False, index=True)
    pet_ids = Column(ARRAY(UUID(as_uuid=True)), nullable=False)  # Support multi-pet appointments
    service_id = Column(UUID(as_uuid=True), ForeignKey("services.id"), nullable=False)
    staff_id = Column(UUID(as_uuid=True), ForeignKey("staff.id"), nullable=True, index=True)
    resource_id = Column(UUID(as_uuid=True), ForeignKey("resources.id"), nullable=True)

    # Scheduling
    scheduled_start = Column(DateTime(timezone=True), nullable=False, index=True)
    scheduled_end = Column(DateTime(timezone=True), nullable=False)
    actual_start = Column(DateTime(timezone=True), nullable=True)
    actual_end = Column(DateTime(timezone=True), nullable=True)

    # Status
    status = Column(SQLEnum(AppointmentStatus), default=AppointmentStatus.PENDING, nullable=False)
    source = Column(SQLEnum(AppointmentSource), default=AppointmentSource.ONLINE, nullable=False)

    # Confirmation
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    confirmation_sent_at = Column(DateTime(timezone=True), nullable=True)
    reminder_24h_sent_at = Column(DateTime(timezone=True), nullable=True)
    reminder_2h_sent_at = Column(DateTime(timezone=True), nullable=True)

    # Payment
    deposit_required = Column(Integer, nullable=True)  # In cents
    deposit_paid = Column(Integer, default=0, nullable=False)  # In cents
    total_amount = Column(Integer, nullable=False)  # In cents
    amount_paid = Column(Integer, default=0, nullable=False)  # In cents
    tip_amount = Column(Integer, default=0, nullable=False)  # In cents

    # Notes and Instructions
    customer_notes = Column(Text, nullable=True)  # Notes from customer
    staff_notes = Column(Text, nullable=True)  # Internal notes
    special_instructions = Column(Text, nullable=True)

    # Photos
    before_photos = Column(JSON, nullable=True)  # Array of URLs
    after_photos = Column(JSON, nullable=True)  # Array of URLs

    # Vaccination check
    vaccination_verified = Column(Boolean, default=False, nullable=False)
    vaccination_override = Column(Boolean, default=False, nullable=False)
    vaccination_override_reason = Column(Text, nullable=True)

    # Cancellation
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    cancellation_reason = Column(Text, nullable=True)
    cancelled_by = Column(UUID(as_uuid=True), nullable=True)  # User ID who cancelled

    # No-show tracking
    no_show_fee_charged = Column(Integer, default=0, nullable=False)

    # Metadata
    tags = Column(JSON, nullable=True)
    custom_fields = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    tenant = relationship("Tenant", backref="appointments")
    owner = relationship("Owner", backref="appointments")
    service = relationship("Service", backref="appointments")
    staff = relationship("Staff", backref="appointments")
    resource = relationship("Resource", backref="appointments")

    def __repr__(self):
        return f"<Appointment(id={self.id}, status={self.status}, start={self.scheduled_start})>"

    @property
    def duration_minutes(self):
        """Calculate duration in minutes"""
        if self.scheduled_end and self.scheduled_start:
            delta = self.scheduled_end - self.scheduled_start
            return int(delta.total_seconds() / 60)
        return 0

    @property
    def balance_due(self):
        """Calculate remaining balance"""
        return self.total_amount - self.amount_paid
