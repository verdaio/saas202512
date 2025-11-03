"""
Webhook endpoints for external integrations
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Header, status
from sqlalchemy.orm import Session
import stripe
import json

from ..db.base import get_db
from ..core.config import settings
from ..integrations.stripe_service import StripeService

router = APIRouter()


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="stripe-signature"),
    db: Session = Depends(get_db)
):
    """
    Handle Stripe webhook events
    """
    payload = await request.body()

    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload,
            stripe_signature,
            settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        # Invalid payload
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payload"
        )
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid signature"
        )

    # Handle the event
    event_type = event["type"]
    event_data = event["data"]

    handled = StripeService.handle_webhook_event(
        event_type=event_type,
        event_data=event_data,
        db=db
    )

    if handled:
        return {"status": "success", "event_type": event_type}
    else:
        return {"status": "ignored", "event_type": event_type}


@router.post("/twilio")
async def twilio_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Handle Twilio webhook events (delivery status, replies)
    TODO Sprint 3: Implement Twilio webhook handling
    """
    # Get form data (Twilio sends as form-encoded)
    form_data = await request.form()

    # Extract relevant fields
    message_sid = form_data.get("MessageSid")
    message_status = form_data.get("MessageStatus")
    from_number = form_data.get("From")
    to_number = form_data.get("To")
    body = form_data.get("Body")

    # TODO: Update SMS delivery status in database
    # TODO: Handle customer replies

    return {"status": "success"}
