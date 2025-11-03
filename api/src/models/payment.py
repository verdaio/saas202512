"""
Payment model for transactions
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, Text, JSON, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from ..db.base import Base


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class PaymentType(str, enum.Enum):
    DEPOSIT = "deposit"
    FULL_PAYMENT = "full_payment"
    TIP = "tip"
    PACKAGE = "package"
    GIFT_CARD = "gift_card"
    NO_SHOW_FEE = "no_show_fee"
    REFUND = "refund"


class PaymentMethod(str, enum.Enum):
    CARD = "card"
    CASH = "cash"
    CHECK = "check"
    OTHER = "other"


class Payment(Base):
    """
    Payment model - tracks all financial transactions
    """
    __tablename__ = "payments"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Tenant (Multi-tenant isolation)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)

    # Related Entities
    owner_id = Column(UUID(as_uuid=True), ForeignKey("owners.id"), nullable=False, index=True)
    appointment_id = Column(UUID(as_uuid=True), ForeignKey("appointments.id"), nullable=True)
    package_id = Column(UUID(as_uuid=True), ForeignKey("packages.id"), nullable=True)

    # Payment Information
    type = Column(SQLEnum(PaymentType), nullable=False)
    method = Column(SQLEnum(PaymentMethod), nullable=False)
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)

    # Amounts (in cents)
    amount = Column(Integer, nullable=False)
    tip_amount = Column(Integer, default=0, nullable=False)
    refund_amount = Column(Integer, default=0, nullable=False)
    net_amount = Column(Integer, nullable=False)  # amount - refund_amount

    # Stripe Integration
    stripe_payment_intent_id = Column(String(255), unique=True, nullable=True, index=True)
    stripe_charge_id = Column(String(255), nullable=True)
    stripe_refund_id = Column(String(255), nullable=True)
    stripe_customer_id = Column(String(255), nullable=True)
    stripe_payment_method_id = Column(String(255), nullable=True)

    # Card Information (last 4 digits only for security)
    card_last4 = Column(String(4), nullable=True)
    card_brand = Column(String(20), nullable=True)  # visa, mastercard, amex, etc.
    card_exp_month = Column(Integer, nullable=True)
    card_exp_year = Column(Integer, nullable=True)

    # Processing
    processor_response = Column(JSON, nullable=True)  # Full response from Stripe
    failure_code = Column(String(100), nullable=True)
    failure_message = Column(Text, nullable=True)

    # Timestamps
    processed_at = Column(DateTime(timezone=True), nullable=True)
    succeeded_at = Column(DateTime(timezone=True), nullable=True)
    failed_at = Column(DateTime(timezone=True), nullable=True)
    refunded_at = Column(DateTime(timezone=True), nullable=True)

    # Metadata
    description = Column(String(500), nullable=True)
    receipt_email = Column(String(255), nullable=True)
    receipt_url = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    tenant = relationship("Tenant", backref="payments")
    owner = relationship("Owner", backref="payments")
    appointment = relationship("Appointment", backref="payments")
    package = relationship("Package", backref="payment", uselist=False)

    def __repr__(self):
        return f"<Payment(id={self.id}, type={self.type}, amount=${self.amount/100:.2f}, status={self.status})>"

    @property
    def amount_display(self):
        """Amount in dollars"""
        return self.amount / 100.0

    @property
    def net_amount_display(self):
        """Net amount in dollars"""
        return self.net_amount / 100.0

    @property
    def is_successful(self):
        """Check if payment was successful"""
        return self.status == PaymentStatus.SUCCEEDED
