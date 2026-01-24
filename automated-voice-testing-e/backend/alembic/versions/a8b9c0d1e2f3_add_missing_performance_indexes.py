"""Add missing performance indexes

Revision ID: a8b9c0d1e2f3
Revises: 74f39c0b4f9a
Create Date: 2025-12-13 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'a8b9c0d1e2f3'
down_revision: Union[str, Sequence[str], None] = '74f39c0b4f9a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add missing indexes for commonly queried columns."""
    # Add index on voice_test_executions.language_code
    op.create_index(
        'ix_voice_test_executions_language_code',
        'voice_test_executions',
        ['language_code'],
        unique=False
    )

    # Add index on voice_test_executions.status
    op.create_index(
        'ix_voice_test_executions_status',
        'voice_test_executions',
        ['status'],
        unique=False
    )

    # Add index on validation_results.review_status
    op.create_index(
        'ix_validation_results_review_status',
        'validation_results',
        ['review_status'],
        unique=False
    )


def downgrade() -> None:
    """Remove the added indexes."""
    op.drop_index('ix_validation_results_review_status', table_name='validation_results')
    op.drop_index('ix_voice_test_executions_status', table_name='voice_test_executions')
    op.drop_index('ix_voice_test_executions_language_code', table_name='voice_test_executions')
