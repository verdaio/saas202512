"""
Stripe payment integration service
Sprint 3 implementation
"""
import stripe
from typing import Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session

from ..core.config import settings
from ..models.payment import Payment, PaymentStatus, PaymentType
from ..models.owner import Owner
from ..models.appointment import Appointment
from ..models.tenant import Tenant

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    """Stripe payment processing service"""

    @staticmethod
    def create_customer(
        email: str,
        name: str,
        phone: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Create a Stripe customer
        Returns customer_id
        """
        customer = stripe.Customer.create(
            email=email,
            name=name,
            phone=phone,
            metadata=metadata or {}
        )

        return customer.id

    @staticmethod
    def create_payment_intent(
        amount: int,  # in cents
        customer_id: Optional[str] = None,
        payment_method_id: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        automatic_payment_methods: bool = True
    ) -> Dict[str, Any]:
        """
        Create a Stripe payment intent
        Returns payment intent data
        """
        intent_data = {
            "amount": amount,
            "currency": "usd",
            "description": description,
            "metadata": metadata or {}
        }

        if customer_id:
            intent_data["customer"] = customer_id

        if payment_method_id:
            intent_data["payment_method"] = payment_method_id
            intent_data["confirm"] = True
        elif automatic_payment_methods:
            intent_data["automatic_payment_methods"] = {"enabled": True}

        payment_intent = stripe.PaymentIntent.create(**intent_data)

        return {
            "id": payment_intent.id,
            "client_secret": payment_intent.client_secret,
            "status": payment_intent.status,
            "amount": payment_intent.amount,
            "currency": payment_intent.currency
        }

    @staticmethod
    def retrieve_payment_intent(payment_intent_id: str) -> Dict[str, Any]:
        """
        Retrieve a payment intent from Stripe
        """
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)

        return {
            "id": payment_intent.id,
            "status": payment_intent.status,
            "amount": payment_intent.amount,
            "currency": payment_intent.currency,
            "payment_method": payment_intent.payment_method,
            "charges": payment_intent.charges
        }

    @staticmethod
    def confirm_payment_intent(
        payment_intent_id: str,
        payment_method_id: str
    ) -> Dict[str, Any]:
        """
        Confirm a payment intent
        """
        payment_intent = stripe.PaymentIntent.confirm(
            payment_intent_id,
            payment_method=payment_method_id
        )

        return {
            "id": payment_intent.id,
            "status": payment_intent.status,
            "amount": payment_intent.amount
        }

    @staticmethod
    def create_refund(
        payment_intent_id: str,
        amount: Optional[int] = None,  # in cents, None = full refund
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a refund for a payment intent
        """
        refund_data = {
            "payment_intent": payment_intent_id
        }

        if amount:
            refund_data["amount"] = amount

        if reason:
            refund_data["reason"] = reason

        refund = stripe.Refund.create(**refund_data)

        return {
            "id": refund.id,
            "status": refund.status,
            "amount": refund.amount,
            "reason": refund.reason
        }

    @staticmethod
    def attach_payment_method(
        payment_method_id: str,
        customer_id: str
    ) -> Dict[str, Any]:
        """
        Attach a payment method to a customer
        """
        payment_method = stripe.PaymentMethod.attach(
            payment_method_id,
            customer=customer_id
        )

        return {
            "id": payment_method.id,
            "type": payment_method.type,
            "card": payment_method.card if payment_method.type == "card" else None
        }

    @staticmethod
    def get_or_create_customer(
        db: Session,
        owner: Owner
    ) -> str:
        """
        Get existing Stripe customer ID or create new customer
        Returns customer_id
        """
        # Check if owner has stripe_customer_id stored
        # TODO: Add stripe_customer_id field to Owner model
        # For now, create new customer each time

        customer_id = StripeService.create_customer(
            email=owner.email,
            name=f"{owner.first_name} {owner.last_name}",
            phone=owner.phone,
            metadata={
                "owner_id": str(owner.id),
                "tenant_id": str(owner.tenant_id)
            }
        )

        return customer_id

    @staticmethod
    def process_deposit_payment(
        db: Session,
        tenant: Tenant,
        appointment: Appointment,
        payment_method_id: str
    ) -> Payment:
        """
        Process deposit payment for an appointment
        """
        if not appointment.deposit_required:
            raise ValueError("No deposit required for this appointment")

        # Get or create Stripe customer
        owner = db.query(Owner).filter(Owner.id == appointment.owner_id).first()
        if not owner:
            raise ValueError("Owner not found")

        customer_id = StripeService.get_or_create_customer(db, owner)

        # Create payment intent
        intent_data = StripeService.create_payment_intent(
            amount=appointment.deposit_required,
            customer_id=customer_id,
            payment_method_id=payment_method_id,
            description=f"Deposit for appointment {appointment.id}",
            metadata={
                "appointment_id": str(appointment.id),
                "tenant_id": str(tenant.id),
                "owner_id": str(owner.id),
                "payment_type": "deposit"
            }
        )

        # Create payment record
        from datetime import datetime
        payment = Payment(
            id=UUID(int=0),  # Will be generated
            tenant_id=tenant.id,
            owner_id=owner.id,
            appointment_id=appointment.id,
            type=PaymentType.DEPOSIT,
            method="card",
            status=PaymentStatus.PROCESSING if intent_data["status"] == "processing" else PaymentStatus.SUCCEEDED if intent_data["status"] == "succeeded" else PaymentStatus.PENDING,
            amount=appointment.deposit_required,
            net_amount=appointment.deposit_required,
            stripe_payment_intent_id=intent_data["id"],
            stripe_customer_id=customer_id,
            description=f"Deposit for appointment {appointment.id}"
        )

        db.add(payment)
        db.commit()
        db.refresh(payment)

        # Update appointment
        appointment.deposit_paid = appointment.deposit_required
        db.commit()

        return payment

    @staticmethod
    def handle_webhook_event(
        event_type: str,
        event_data: Dict[str, Any],
        db: Session
    ) -> bool:
        """
        Handle Stripe webhook events
        Returns True if handled successfully
        """
        if event_type == "payment_intent.succeeded":
            return StripeService._handle_payment_succeeded(event_data, db)
        elif event_type == "payment_intent.payment_failed":
            return StripeService._handle_payment_failed(event_data, db)
        elif event_type == "charge.refunded":
            return StripeService._handle_charge_refunded(event_data, db)

        return False

    @staticmethod
    def _handle_payment_succeeded(event_data: Dict[str, Any], db: Session) -> bool:
        """Handle payment_intent.succeeded webhook"""
        payment_intent = event_data.get("object")
        if not payment_intent:
            return False

        payment_intent_id = payment_intent.get("id")

        # Find payment record
        payment = db.query(Payment).filter(
            Payment.stripe_payment_intent_id == payment_intent_id
        ).first()

        if not payment:
            return False

        # Update payment status
        from datetime import datetime
        payment.status = PaymentStatus.SUCCEEDED
        payment.succeeded_at = datetime.utcnow()

        # Extract card details from payment method
        if payment_intent.get("charges") and payment_intent["charges"].get("data"):
            charge = payment_intent["charges"]["data"][0]
            payment_method = charge.get("payment_method_details", {})
            if payment_method.get("card"):
                card = payment_method["card"]
                payment.card_last4 = card.get("last4")
                payment.card_brand = card.get("brand")
                payment.card_exp_month = card.get("exp_month")
                payment.card_exp_year = card.get("exp_year")

        db.commit()

        return True

    @staticmethod
    def _handle_payment_failed(event_data: Dict[str, Any], db: Session) -> bool:
        """Handle payment_intent.payment_failed webhook"""
        payment_intent = event_data.get("object")
        if not payment_intent:
            return False

        payment_intent_id = payment_intent.get("id")

        # Find payment record
        payment = db.query(Payment).filter(
            Payment.stripe_payment_intent_id == payment_intent_id
        ).first()

        if not payment:
            return False

        # Update payment status
        from datetime import datetime
        payment.status = PaymentStatus.FAILED
        payment.failed_at = datetime.utcnow()
        payment.failure_code = payment_intent.get("last_payment_error", {}).get("code")
        payment.failure_message = payment_intent.get("last_payment_error", {}).get("message")

        db.commit()

        return True

    @staticmethod
    def _handle_charge_refunded(event_data: Dict[str, Any], db: Session) -> bool:
        """Handle charge.refunded webhook"""
        charge = event_data.get("object")
        if not charge:
            return False

        payment_intent_id = charge.get("payment_intent")

        # Find payment record
        payment = db.query(Payment).filter(
            Payment.stripe_payment_intent_id == payment_intent_id
        ).first()

        if not payment:
            return False

        # Update payment status
        from datetime import datetime
        refund_amount = charge.get("amount_refunded", 0)
        payment.refund_amount = refund_amount
        payment.net_amount = payment.amount - refund_amount

        if refund_amount >= payment.amount:
            payment.status = PaymentStatus.REFUNDED
        else:
            payment.status = PaymentStatus.PARTIALLY_REFUNDED

        payment.refunded_at = datetime.utcnow()

        db.commit()

        return True
