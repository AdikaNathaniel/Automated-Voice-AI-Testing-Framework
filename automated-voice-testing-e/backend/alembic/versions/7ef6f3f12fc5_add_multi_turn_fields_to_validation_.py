"""add_multi_turn_fields_to_validation_results

Add multi_turn_execution_id and step_execution_id to validation_results table
to support validation of multi-turn conversation steps.

Revision ID: 7ef6f3f12fc5
Revises: 2c7f20ae9e24
Create Date: 2025-12-12 08:44:42.103908

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from models.base import GUID


# revision identifiers, used by Alembic.
revision: str = '7ef6f3f12fc5'
down_revision: Union[str, Sequence[str], None] = '2c7f20ae9e24'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add multi_turn_execution_id and step_execution_id to validation_results."""
    # Add multi_turn_execution_id column
    op.add_column(
        'validation_results',
        sa.Column(
            'multi_turn_execution_id',
            GUID(),
            nullable=True,
            comment='Multi-turn execution this validation belongs to (for grouping)'
        )
    )

    # Add step_execution_id column
    op.add_column(
        'validation_results',
        sa.Column(
            'step_execution_id',
            GUID(),
            nullable=True,
            comment='Step execution validated in this result (for multi-turn scenarios)'
        )
    )

    # Add foreign key constraint for multi_turn_execution_id
    op.create_foreign_key(
        'fk_validation_results_multi_turn_execution_id',
        'validation_results',
        'multi_turn_executions',
        ['multi_turn_execution_id'],
        ['id']
    )

    # Add foreign key constraint for step_execution_id
    op.create_foreign_key(
        'fk_validation_results_step_execution_id',
        'validation_results',
        'step_executions',
        ['step_execution_id'],
        ['id']
    )

    # Add indexes for query performance
    op.create_index(
        'ix_validation_results_multi_turn_execution_id',
        'validation_results',
        ['multi_turn_execution_id']
    )

    op.create_index(
        'ix_validation_results_step_execution_id',
        'validation_results',
        ['step_execution_id']
    )


def downgrade() -> None:
    """Remove multi_turn_execution_id and step_execution_id from validation_results."""
    # Drop indexes
    op.drop_index('ix_validation_results_step_execution_id', table_name='validation_results')
    op.drop_index('ix_validation_results_multi_turn_execution_id', table_name='validation_results')

    # Drop foreign key constraints
    op.drop_constraint('fk_validation_results_step_execution_id', 'validation_results', type_='foreignkey')
    op.drop_constraint('fk_validation_results_multi_turn_execution_id', 'validation_results', type_='foreignkey')

    # Drop columns
    op.drop_column('validation_results', 'step_execution_id')
    op.drop_column('validation_results', 'multi_turn_execution_id')
