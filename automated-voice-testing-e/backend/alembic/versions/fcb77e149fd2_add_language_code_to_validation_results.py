"""add_language_code_to_validation_results

Revision ID: fcb77e149fd2
Revises: d2e3f4g5h6i7
Create Date: 2025-12-18 12:54:40.597258

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fcb77e149fd2'
down_revision: Union[str, Sequence[str], None] = 'd2e3f4g5h6i7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add language_code column to validation_results table."""
    op.add_column(
        'validation_results',
        sa.Column(
            'language_code',
            sa.String(length=16),
            nullable=True,
            comment='Language code validated (e.g., en-US, es-ES, fr-FR)'
        )
    )
    op.create_index(
        op.f('ix_validation_results_language_code'),
        'validation_results',
        ['language_code'],
        unique=False
    )


def downgrade() -> None:
    """Remove language_code column from validation_results table."""
    op.drop_index(
        op.f('ix_validation_results_language_code'),
        table_name='validation_results'
    )
    op.drop_column('validation_results', 'language_code')
