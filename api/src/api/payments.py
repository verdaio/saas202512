"""
Payment API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import uuid

from ..db.base import get_db
from ..core.dependencies import get_current_user, get_current_tenant, require_staff_or_admin
from ..models.user import User
from ..models.tenant import Tenant
from ..models.payment import Payment, PaymentStatus
from ..models.owner import Owner
from ..schemas.payment import PaymentCreate, PaymentUpdate, PaymentResponse

router = APIRouter()


@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Create new payment (public endpoint for booking widget)
    """
    # Verify owner exists
    owner = db.query(Owner).filter(
        Owner.id == payment_data.owner_id,
        Owner.tenant_id == current_tenant.id
    ).first()

    if not owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Owner not found"
        )

    # TODO: Add Stripe payment processing (Sprint 3)
    # For now, just create payment record

    payment = Payment(
        id=uuid.uuid4(),
        tenant_id=current_tenant.id,
        status=PaymentStatus.PENDING,
        net_amount=payment_data.amount + payment_data.tip_amount,
        **payment_data.model_dump()
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return payment


@router.get("/", response_model=List[PaymentResponse])
async def list_payments(
    skip: int = 0,
    limit: int = 100,
    owner_id: UUID = None,
    appointment_id: UUID = None,
    status: str = None,
    type: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    List payments for current tenant
    """
    query = db.query(Payment).filter(Payment.tenant_id == current_tenant.id)

    if owner_id:
        query = query.filter(Payment.owner_id == owner_id)

    if appointment_id:
        query = query.filter(Payment.appointment_id == appointment_id)

    if status:
        query = query.filter(Payment.status == status)

    if type:
        query = query.filter(Payment.type == type)

    payments = query.order_by(Payment.created_at.desc()).offset(skip).limit(limit).all()
    return payments


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Get payment by ID
    """
    payment = db.query(Payment).filter(
        Payment.id == payment_id,
        Payment.tenant_id == current_tenant.id
    ).first()

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )

    return payment


@router.put("/{payment_id}", response_model=PaymentResponse)
async def update_payment(
    payment_id: UUID,
    payment_data: PaymentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_admin),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Update payment status (staff/admin/owner)
    """
    payment = db.query(Payment).filter(
        Payment.id == payment_id,
        Payment.tenant_id == current_tenant.id
    ).first()

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )

    # Update fields
    for field, value in payment_data.model_dump(exclude_unset=True).items():
        setattr(payment, field, value)

    # Recalculate net amount if refund changed
    if payment_data.refund_amount is not None:
        payment.net_amount = payment.amount - payment.refund_amount

    db.commit()
    db.refresh(payment)

    return payment


@router.post("/{payment_id}/refund", response_model=PaymentResponse)
async def refund_payment(
    payment_id: UUID,
    refund_amount: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_admin),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Refund payment (staff/admin/owner)
    """
    payment = db.query(Payment).filter(
        Payment.id == payment_id,
        Payment.tenant_id == current_tenant.id
    ).first()

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )

    if payment.status != PaymentStatus.SUCCEEDED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only refund succeeded payments"
        )

    if refund_amount > payment.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refund amount cannot exceed payment amount"
        )

    # TODO: Process Stripe refund (Sprint 3)

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
