"""add_no_show_fields

Revision ID: add_no_show_fields
Revises: add_reputation_fields
Create Date: 2025-11-05 11:01:00.000000

Sprint 4: Add no-show tracking fields to Appointment model
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_no_show_fields'
down_revision: Union[str, None] = 'add_reputation_fields'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add no-show tracking fields to appointments table
    op.add_column('appointments', sa.Column('is_no_show', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('appointments', sa.Column('no_show_fee_charged', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('appointments', sa.Column('arrived_at', sa.DateTime(timezone=True), nullable=True))

    # Create index for no-show detection queries
    op.create_index(
        'idx_appointments_no_show_detection',
        'appointments',
        ['tenant_id', 'status', 'scheduled_start', 'is_no_show'],
        unique=False
    )

    # Create index for arrival tracking
    op.create_index(
        'idx_appointments_arrived_at',
        'appointments',
        ['tenant_id', 'arrived_at'],
        unique=False
    )


def downgrade() -> None:
    # Remove indexes
    op.drop_index('idx_appointments_arrived_at', table_name='appointments')
    op.drop_index('idx_appointments_no_show_detection', table_name='appointments')

    # Remove columns
    op.drop_column('appointments', 'arrived_at')
    op.drop_column('appointments', 'no_show_fee_charged')
    op.drop_column('appointments', 'is_no_show')
