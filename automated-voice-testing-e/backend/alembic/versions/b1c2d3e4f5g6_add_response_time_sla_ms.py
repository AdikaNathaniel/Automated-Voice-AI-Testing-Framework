"""add_response_time_sla_ms to pattern_analysis_configs

Revision ID: b1c2d3e4f5g6
Revises: a4b5c6d7e8f9
Create Date: 2025-12-30 12:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b1c2d3e4f5g6'
down_revision: Union[str, Sequence[str], None] = 'a4b5c6d7e8f9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add response_time_sla_ms column to pattern_analysis_configs."""
    op.add_column(
        'pattern_analysis_configs',
        sa.Column(
            'response_time_sla_ms',
            sa.Integer(),
            server_default=sa.text('2000'),
            nullable=False,
            comment='Response time SLA threshold in milliseconds'
        )
    )


def downgrade() -> None:
    """Remove response_time_sla_ms column from pattern_analysis_configs."""
    op.drop_column('pattern_analysis_configs', 'response_time_sla_ms')
