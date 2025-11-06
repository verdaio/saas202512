"""add_waived_payment_status

Revision ID: add_waived_payment_status
Revises: add_vaccination_alert_fields
Create Date: 2025-11-05 11:03:00.000000

Sprint 4: Add WAIVED status to PaymentStatus enum
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_waived_payment_status'
down_revision: Union[str, None] = 'add_vaccination_alert_fields'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add WAIVED and COMPLETED to PaymentStatus enum
    # PostgreSQL requires special handling for enum updates
    op.execute("ALTER TYPE paymentstatus ADD VALUE IF NOT EXISTS 'waived'")
    op.execute("ALTER TYPE paymentstatus ADD VALUE IF NOT EXISTS 'completed'")


def downgrade() -> None:
    # Note: PostgreSQL doesn't support removing enum values directly
    # This would require recreating the enum type, which is complex
    # For production, consider creating a new enum type if rollback is needed
    pass  # Cannot easily remove enum value in PostgreSQL
