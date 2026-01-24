"""add_suite_run_id_to_defects

Revision ID: 86ad0dfb433b
Revises: daee381e2a66
Create Date: 2025-12-27 20:20:43.048818

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '86ad0dfb433b'
down_revision: Union[str, Sequence[str], None] = 'daee381e2a66'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add suite_run_id column to defects table."""
    # Add suite_run_id column
    op.add_column(
        'defects',
        sa.Column(
            'suite_run_id',
            sa.dialects.postgresql.UUID(),
            nullable=True,
            comment='Suite run in which the defect was detected'
        )
    )

    # Create index
    op.create_index('ix_defects_suite_run_id', 'defects', ['suite_run_id'])

    # Create foreign key constraint
    op.create_foreign_key(
        'fk_defects_suite_run_id',
        'defects',
        'suite_runs',
        ['suite_run_id'],
        ['id'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    """Remove suite_run_id column from defects table."""
    # Drop foreign key constraint
    op.drop_constraint('fk_defects_suite_run_id', 'defects', type_='foreignkey')

    # Drop index
    op.drop_index('ix_defects_suite_run_id', table_name='defects')

    # Drop column
    op.drop_column('defects', 'suite_run_id')
