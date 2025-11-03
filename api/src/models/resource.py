"""
Resource model for tables, vans, rooms, etc.
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, Text, JSON, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from ..db.base import Base


class ResourceType(str, enum.Enum):
    TABLE = "table"
    VAN = "van"
    ROOM = "room"
    CAGE = "cage"
    OTHER = "other"


class Resource(Base):
    """
    Resource model - represents physical resources (grooming tables, mobile vans, training rooms)
    """
    __tablename__ = "resources"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Tenant (Multi-tenant isolation)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)

    # Resource Information
    name = Column(String(200), nullable=False)
    type = Column(SQLEnum(ResourceType), nullable=False)
    description = Column(Text, nullable=True)

    # Capacity
    capacity = Column(Integer, default=1, nullable=False)  # How many appointments can use simultaneously

    # Availability
    is_active = Column(Boolean, default=True, nullable=False)
    is_bookable = Column(Boolean, default=True, nullable=False)

    # Schedule (stored as JSON)
    # Format: {"monday": {"start": "09:00", "end": "17:00", "breaks": [...]}, ...}
    schedule = Column(JSON, nullable=True)

    # Travel time (for mobile vans - in minutes)
    travel_time_minutes = Column(Integer, default=0, nullable=False)

    # Metadata
    location = Column(String(255), nullable=True)  # Physical location
    color = Column(String(7), nullable=True)  # Hex color for calendar
    display_order = Column(Integer, default=0, nullable=False)
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    tenant = relationship("Tenant", backref="resources")

    def __repr__(self):
        return f"<Resource(id={self.id}, name={self.name}, type={self.type})>"
