"""Add name, description, category_name to test_runs

Revision ID: c1d2e3f4g5h6
Revises: a8b9c0d1e2f3
Create Date: 2025-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'c1d2e3f4g5h6'
down_revision: Union[str, None] = '8723280c8610'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add fields to test_runs for better suite run tracking."""
    # Add name column
    op.add_column(
        'test_runs',
        sa.Column(
            'name',
            sa.String(255),
            nullable=True,
            comment="Name of the test run"
        )
    )

    # Add description column
    op.add_column(
        'test_runs',
        sa.Column(
            'description',
            sa.Text(),
            nullable=True,
            comment="Description of what this run covers"
        )
    )

    # Add category_name column for categorical suite runs
    op.add_column(
        'test_runs',
        sa.Column(
            'category_name',
            sa.String(255),
            nullable=True,
            comment="Category name for categorical suite runs"
        )
    )

    # Create index on category_name
    op.create_index(
        'ix_test_runs_category_name',
        'test_runs',
        ['category_name']
    )

    # Make suite_id nullable (if it isn't already)
    # This allows categorical runs without a real suite
    op.alter_column(
        'test_runs',
        'suite_id',
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=True
    )


def downgrade() -> None:
    """Remove the added fields."""
    op.drop_index('ix_test_runs_category_name', table_name='test_runs')
    op.drop_column('test_runs', 'category_name')
    op.drop_column('test_runs', 'description')
    op.drop_column('test_runs', 'name')

    # Note: Not reverting suite_id to nullable=False as it may break existing data
