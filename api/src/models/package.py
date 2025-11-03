"""
Package model for punch cards, class credits, and memberships
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from ..db.base import Base


class PackageType(str, enum.Enum):
    PUNCH_CARD = "punch_card"  # X services for Y price
    CLASS_CREDITS = "class_credits"  # X class credits
    MEMBERSHIP = "membership"  # Monthly/annual membership
    GIFT_CARD = "gift_card"


class PackageStatus(str, enum.Enum):
    ACTIVE = "active"
    EXHAUSTED = "exhausted"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class Package(Base):
    """
    Package model - punch cards, class credits, memberships, gift cards
    """
    __tablename__ = "packages"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Tenant (Multi-tenant isolation)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)

    # Owner
    owner_id = Column(UUID(as_uuid=True), ForeignKey("owners.id"), nullable=False, index=True)

    # Package Information
    name = Column(String(200), nullable=False)
    type = Column(SQLEnum(PackageType), nullable=False)
    description = Column(Text, nullable=True)

    # Pricing (in cents)
    price_paid = Column(Integer, nullable=False)
    value = Column(Integer, nullable=True)  # Actual value if different from price

    # Credits/Sessions
    total_credits = Column(Integer, nullable=False)  # Total number of sessions/credits
    remaining_credits = Column(Integer, nullable=False)  # Remaining
    unlimited = Column(Boolean, default=False, nullable=False)  # For memberships

    # Validity
    valid_from = Column(DateTime(timezone=True), nullable=True)
    valid_until = Column(DateTime(timezone=True), nullable=True)
    never_expires = Column(Boolean, default=False, nullable=False)

    # Status
    status = Column(SQLEnum(PackageStatus), default=PackageStatus.ACTIVE, nullable=False)

    # Payment
    payment_id = Column(UUID(as_uuid=True), ForeignKey("payments.id"), nullable=True)
    stripe_payment_intent_id = Column(String(255), nullable=True)

    # Usage tracking
    first_used_at = Column(DateTime(timezone=True), nullable=True)
    last_used_at = Column(DateTime(timezone=True), nullable=True)

    # Gift card specific
    gift_code = Column(String(50), unique=True, nullable=True, index=True)
    recipient_name = Column(String(200), nullable=True)
    recipient_email = Column(String(255), nullable=True)
    message = Column(Text, nullable=True)

    # Metadata
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    tenant = relationship("Tenant", backref="packages")
    owner = relationship("Owner", backref="packages")

    def __repr__(self):
        return f"<Package(id={self.id}, type={self.type}, credits={self.remaining_credits}/{self.total_credits})>"

    def use_credit(self):
        """Use one credit from the package"""
        if self.remaining_credits > 0:
            self.remaining_credits -= 1
            self.last_used_at = func.now()
            if not self.first_used_at:
                self.first_used_at = func.now()
            if self.remaining_credits == 0:
                self.status = PackageStatus.EXHAUSTED
            return True
        return False

    @property
    def is_valid(self):
        """Check if package is currently valid"""
        if self.status != PackageStatus.ACTIVE:
            return False
        if self.remaining_credits == 0 and not self.unlimited:
            return False
        if self.valid_until and self.valid_until < func.now():
            return False
        return True
