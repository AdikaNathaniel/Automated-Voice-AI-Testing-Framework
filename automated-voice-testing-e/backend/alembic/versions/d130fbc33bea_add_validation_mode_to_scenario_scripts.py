"""add_validation_mode_to_scenario_scripts

Revision ID: d130fbc33bea
Revises: fcb77e149fd2
Create Date: 2025-12-18 14:07:39.354408

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd130fbc33bea'
down_revision: Union[str, Sequence[str], None] = 'fcb77e149fd2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add validation_mode column to scenario_scripts table."""
    # Add validation_mode column with default 'houndify'
    op.add_column(
        'scenario_scripts',
        sa.Column(
            'validation_mode',
            sa.String(length=50),
            nullable=False,
            server_default='houndify',
            comment='Validation mode: houndify, llm_ensemble, or hybrid'
        )
    )
    op.create_index(
        op.f('ix_scenario_scripts_validation_mode'),
        'scenario_scripts',
        ['validation_mode'],
        unique=False
    )


def downgrade() -> None:
    """Remove validation_mode column from scenario_scripts table."""
    op.drop_index(
        op.f('ix_scenario_scripts_validation_mode'),
        table_name='scenario_scripts'
    )
    op.drop_column('scenario_scripts', 'validation_mode')
