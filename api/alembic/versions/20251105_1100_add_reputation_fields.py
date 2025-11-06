"""add_reputation_fields

Revision ID: add_reputation_fields
Revises: 20251103_1447
Create Date: 2025-11-05 11:00:00.000000

Sprint 4: Add reputation scoring fields to Owner model
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_reputation_fields'
down_revision: Union[str, None] = '20251103_1447'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add reputation scoring fields to owners table
    op.add_column('owners', sa.Column('reputation_score', sa.Integer(), nullable=False, server_default='100'))
    op.add_column('owners', sa.Column('no_show_count', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('owners', sa.Column('late_cancellation_count', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('owners', sa.Column('completed_appointment_count', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('owners', sa.Column('last_reputation_update', sa.DateTime(timezone=True), nullable=True))

    # Create index for reputation score lookups
    op.create_index(
        'idx_owners_reputation_score',
        'owners',
        ['tenant_id', 'reputation_score'],
        unique=False
    )


def downgrade() -> None:
    # Remove index
    op.drop_index('idx_owners_reputation_score', table_name='owners')

    # Remove columns
    op.drop_column('owners', 'last_reputation_update')
    op.drop_column('owners', 'completed_appointment_count')
    op.drop_column('owners', 'late_cancellation_count')
    op.drop_column('owners', 'no_show_count')
    op.drop_column('owners', 'reputation_score')
