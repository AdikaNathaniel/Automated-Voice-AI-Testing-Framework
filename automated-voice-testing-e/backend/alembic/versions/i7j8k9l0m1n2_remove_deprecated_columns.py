"""Remove deprecated expected_response and related columns

Revision ID: i7j8k9l0m1n2
Revises: h6i7j8k9l0m1
Create Date: 2024-12-21

This migration removes deprecated columns:
- expected_response from scenario_steps (use ExpectedOutcome instead)
- alternate_responses from scenario_steps
- tolerances from scenario_steps
- expected_intent from expected_outcomes (Houndify uses CommandKind only)
- enforce_command_intent_consistency from expected_outcomes
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'i7j8k9l0m1n2'
down_revision = ('h6i7j8k9l0m1', 'e4f5g6h7i8j9')  # Merge multiple heads
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Remove deprecated columns."""
    # Remove columns from scenario_steps
    op.drop_column('scenario_steps', 'expected_response')
    op.drop_column('scenario_steps', 'alternate_responses')
    op.drop_column('scenario_steps', 'tolerances')

    # Remove columns from expected_outcomes
    op.drop_column('expected_outcomes', 'expected_intent')
    op.drop_column('expected_outcomes', 'enforce_command_intent_consistency')


def downgrade() -> None:
    """Restore deprecated columns (data will be lost)."""
    # Restore columns to expected_outcomes
    op.add_column(
        'expected_outcomes',
        sa.Column(
            'enforce_command_intent_consistency',
            sa.Boolean(),
            nullable=False,
            server_default='true'
        )
    )
    op.add_column(
        'expected_outcomes',
        sa.Column(
            'expected_intent',
            sa.String(100),
            nullable=True
        )
    )

    # Restore columns to scenario_steps
    op.add_column(
        'scenario_steps',
        sa.Column(
            'tolerances',
            postgresql.JSONB(),
            nullable=True
        )
    )
    op.add_column(
        'scenario_steps',
        sa.Column(
            'alternate_responses',
            postgresql.JSONB(),
            nullable=True
        )
    )
    op.add_column(
        'scenario_steps',
        sa.Column(
            'expected_response',
            sa.Text(),
            nullable=True
        )
    )
