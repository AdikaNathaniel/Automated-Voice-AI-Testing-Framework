"""Make expected_response nullable on scenario_steps

Revision ID: h6i7j8k9l0m1
Revises: g5h6i7j8k9l0
Create Date: 2024-12-21

This migration makes the expected_response column on scenario_steps nullable,
allowing steps to rely solely on ExpectedOutcome.expected_response_content
for validation configuration.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'h6i7j8k9l0m1'
down_revision = 'g5h6i7j8k9l0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Make expected_response nullable."""
    # PostgreSQL
    op.alter_column(
        'scenario_steps',
        'expected_response',
        existing_type=sa.Text(),
        nullable=True,
        comment='Legacy: Primary expected system response (use ExpectedOutcome.expected_response_content instead)'
    )


def downgrade() -> None:
    """Revert expected_response to not nullable."""
    # First, set any NULL values to empty string to avoid constraint violation
    op.execute(
        "UPDATE scenario_steps SET expected_response = '' WHERE expected_response IS NULL"
    )

    op.alter_column(
        'scenario_steps',
        'expected_response',
        existing_type=sa.Text(),
        nullable=False,
        comment='Primary expected system response'
    )
