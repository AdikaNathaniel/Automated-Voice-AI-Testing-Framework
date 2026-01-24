"""add_language_config_to_test_suites

Revision ID: daee381e2a66
Revises: 6c9ca7e0033c
Create Date: 2025-12-27 19:33:55.649746

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'daee381e2a66'
down_revision: Union[str, Sequence[str], None] = '6c9ca7e0033c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add language_config column to test_suites table."""
    op.add_column(
        'test_suites',
        sa.Column(
            'language_config',
            sa.dialects.postgresql.JSONB(),
            nullable=True,
            comment='Language execution configuration: mode, languages, fallback_behavior'
        )
    )


def downgrade() -> None:
    """Remove language_config column from test_suites table."""
    op.drop_column('test_suites', 'language_config')
