"""simplify_lookback_days_field

Revision ID: c2d3e4f5g6h7
Revises: b1c2d3e4f5g6
Create Date: 2026-01-02 12:00:00.000000

Simplifies pattern analysis configuration by replacing two time window fields
(lookback_days_recent and lookback_days_max) with a single lookback_days field.

This change removes unnecessary complexity since the two-tier approach
(prioritization + hard limit) wasn't providing meaningful value.

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c2d3e4f5g6h7'
down_revision: Union[str, Sequence[str], None] = 'b1c2d3e4f5g6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Simplify lookback days fields:
    1. Add new lookback_days column
    2. Migrate data from lookback_days_max to lookback_days
    3. Drop old lookback_days_recent and lookback_days_max columns
    """
    # Step 1: Add new lookback_days column with default
    op.add_column(
        'pattern_analysis_configs',
        sa.Column(
            'lookback_days',
            sa.Integer(),
            server_default=sa.text('30'),
            nullable=False,
            comment='Maximum age of edge cases to analyze (in days)'
        )
    )

    # Step 2: Migrate data - use lookback_days_max as the new value
    # This preserves the "maximum age" behavior
    op.execute(
        """
        UPDATE pattern_analysis_configs
        SET lookback_days = lookback_days_max
        """
    )

    # Step 3: Drop old columns
    op.drop_column('pattern_analysis_configs', 'lookback_days_recent')
    op.drop_column('pattern_analysis_configs', 'lookback_days_max')


def downgrade() -> None:
    """
    Restore original two-field approach:
    1. Add back lookback_days_recent and lookback_days_max columns
    2. Migrate data from lookback_days to both columns
    3. Drop lookback_days column
    """
    # Step 1: Add back the old columns
    op.add_column(
        'pattern_analysis_configs',
        sa.Column(
            'lookback_days_recent',
            sa.Integer(),
            server_default=sa.text('7'),
            nullable=False,
            comment='Days to look back for recent edge cases (prioritized)'
        )
    )
    op.add_column(
        'pattern_analysis_configs',
        sa.Column(
            'lookback_days_max',
            sa.Integer(),
            server_default=sa.text('90'),
            nullable=False,
            comment='Maximum age of edge cases to analyze (hard limit)'
        )
    )

    # Step 2: Migrate data - set lookback_days_max to current lookback_days
    # Set lookback_days_recent to a reasonable default (7 days)
    op.execute(
        """
        UPDATE pattern_analysis_configs
        SET lookback_days_max = lookback_days,
            lookback_days_recent = LEAST(7, lookback_days)
        """
    )

    # Step 3: Drop the new column
    op.drop_column('pattern_analysis_configs', 'lookback_days')
