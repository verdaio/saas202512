"""
Payment service with business logic
Sprint 3: Stripe integration implemented
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
import uuid

from ..models.payment import Payment, PaymentStatus, PaymentType
from ..models.owner import Owner
from ..models.tenant import Tenant
from ..schemas.payment import PaymentCreate, PaymentUpdate
from ..integrations.stripe_service import StripeService


class PaymentService:
    """Business logic for payment management"""

    @staticmethod
    def create_payment(
        db: Session,
        tenant: Tenant,
        payment_data: PaymentCreate
    ) -> Payment:
        """
        Create new payment
        TODO Sprint 3: Add Stripe payment intent creation
        """
        # Verify owner exists
        owner = db.query(Owner).filter(
            Owner.id == payment_data.owner_id,
            Owner.tenant_id == tenant.id
        ).first()

        if not owner:
            raise ValueError("Owner not found")

        # TODO Sprint 3: Create Stripe payment intent
        # TODO Sprint 3: Store stripe_payment_intent_id

        payment = Payment(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            status=PaymentStatus.PENDING,
            net_amount=payment_data.amount + payment_data.tip_amount,
            **payment_data.model_dump()
        )

        db.add(payment)
        db.commit()
        db.refresh(payment)

        return payment

    @staticmethod
    def get_payment(
        db: Session,
        tenant: Tenant,
        payment_id: UUID
    ) -> Optional[Payment]:
        """Get payment by ID"""
        return db.query(Payment).filter(
            Payment.id == payment_id,
            Payment.tenant_id == tenant.id
        ).first()

    @staticmethod
    def list_payments(
        db: Session,
        tenant: Tenant,
        skip: int = 0,
        limit: int = 100,
        owner_id: UUID = None,
        appointment_id: UUID = None,
        status: str = None,
        type: str = None
    ) -> List[Payment]:
        """List payments with filters"""
        query = db.query(Payment).filter(Payment.tenant_id == tenant.id)

        if owner_id:
            query = query.filter(Payment.owner_id == owner_id)

        if appointment_id:
            query = query.filter(Payment.appointment_id == appointment_id)

        if status:
            query = query.filter(Payment.status == status)

        if type:
            query = query.filter(Payment.type == type)

        return query.order_by(Payment.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def update_payment(
        db: Session,
        tenant: Tenant,
        payment_id: UUID,
        payment_data: PaymentUpdate
    ) -> Optional[Payment]:
        """Update payment status"""
        payment = PaymentService.get_payment(db, tenant, payment_id)

        if not payment:
            return None

        # Update fields
        for field, value in payment_data.model_dump(exclude_unset=True).items():
            setattr(payment, field, value)

        # Recalculate net amount if refund changed
        if payment_data.refund_amount is not None:
            payment.net_amount = payment.amount - payment.refund_amount

        db.commit()
        db.refresh(payment)

        return payment

    @staticmethod
    def refund_payment(
        db: Session,
        tenant: Tenant,
        payment_id: UUID,
        refund_amount: int
    ) -> Optional[Payment]:
        """
        Refund payment
        TODO Sprint 3: Process Stripe refund
        """
        payment = PaymentService.get_payment(db, tenant, payment_id)

        if not payment:
            return None

        if payment.status != PaymentStatus.SUCCEEDED:
            raise ValueError("Can only refund succeeded payments")

        if refund_amount > payment.amount:
            raise ValueError("Refund amount cannot exceed payment amount")

        # TODO Sprint 3: Create Stripe refund
        # TODO Sprint 3: Store stripe_refund_id

        from datetime import datetime
        payment.refund_amount = refund_amount
        payment.net_amount = payment.amount - refund_amount

        if refund_amount == payment.amount:
            payment.status = PaymentStatus.REFUNDED
        else:
            payment.status = PaymentStatus.PARTIALLY_REFUNDED

        payment.refunded_at = datetime.utcnow()

        db.commit()
        db.refresh(payment)

        return payment

    # TODO Sprint 3: Add these methods
    # @staticmethod
    # def process_stripe_payment(tenant, payment_method_id, amount): pass
    # @staticmethod
    # def handle_stripe_webhook(event): pass
    # @staticmethod
    # def create_payment_intent(tenant, amount, customer_id): pass
