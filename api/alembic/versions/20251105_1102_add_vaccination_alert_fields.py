"""add_vaccination_alert_fields

Revision ID: add_vaccination_alert_fields
Revises: add_no_show_fields
Create Date: 2025-11-05 11:02:00.000000

Sprint 4: Add alert tracking fields to VaccinationRecord model
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_vaccination_alert_fields'
down_revision: Union[str, None] = 'add_no_show_fields'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add alert tracking fields to vaccination_records table
    op.add_column('vaccination_records', sa.Column('last_alert_sent', sa.DateTime(timezone=True), nullable=True))
    op.add_column('vaccination_records', sa.Column('alert_count', sa.Integer(), nullable=False, server_default='0'))

    # Create index for alert scheduling queries
    op.create_index(
        'idx_vaccination_records_expiry_alerts',
        'vaccination_records',
        ['tenant_id', 'expiry_date', 'last_alert_sent'],
        unique=False
    )


def downgrade() -> None:
    # Remove index
    op.drop_index('idx_vaccination_records_expiry_alerts', table_name='vaccination_records')

    # Remove columns
    op.drop_column('vaccination_records', 'alert_count')
    op.drop_column('vaccination_records', 'last_alert_sent')
