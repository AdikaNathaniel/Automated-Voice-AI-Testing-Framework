"""add defect_auto_creation_threshold to pattern_analysis_configs

Revision ID: f08a802b96db
Revises: w0x1y2z3a4b5
Create Date: 2025-12-29 14:39:27.502440

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f08a802b96db'
down_revision: Union[str, Sequence[str], None] = 'w0x1y2z3a4b5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add defect_auto_creation_threshold column to pattern_analysis_configs table."""
    op.add_column(
        'pattern_analysis_configs',
        sa.Column(
            'defect_auto_creation_threshold',
            sa.Integer(),
            nullable=False,
            server_default=sa.text('3'),
            comment='Number of consecutive auto_fail results before creating defect (minimum: 1)'
        )
    )


def downgrade() -> None:
    """Remove defect_auto_creation_threshold column from pattern_analysis_configs table."""
    op.drop_column('pattern_analysis_configs', 'defect_auto_creation_threshold')
