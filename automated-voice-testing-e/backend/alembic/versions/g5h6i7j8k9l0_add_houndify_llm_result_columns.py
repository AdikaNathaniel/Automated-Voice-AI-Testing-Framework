"""add_houndify_llm_result_columns

Add separate columns for Houndify and LLM validation results to support
hybrid validation mode where both run and their results are preserved.

Revision ID: g5h6i7j8k9l0
Revises: fcb77e149fd2
Create Date: 2025-12-21 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'g5h6i7j8k9l0'
down_revision: Union[str, Sequence[str], None] = 'fcb77e149fd2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add Houndify and LLM result columns to validation_results table."""
    # Add houndify_passed column
    op.add_column(
        'validation_results',
        sa.Column(
            'houndify_passed',
            sa.Boolean(),
            nullable=True,
            comment='Whether Houndify validation passed (before LLM evaluation)'
        )
    )
    op.create_index(
        op.f('ix_validation_results_houndify_passed'),
        'validation_results',
        ['houndify_passed'],
        unique=False
    )

    # Add houndify_result JSONB column
    op.add_column(
        'validation_results',
        sa.Column(
            'houndify_result',
            postgresql.JSONB(astext_type=sa.Text()).with_variant(
                sa.JSON(), 'sqlite'
            ),
            nullable=True,
            comment='Full Houndify validation result with all details'
        )
    )

    # Add llm_passed column
    op.add_column(
        'validation_results',
        sa.Column(
            'llm_passed',
            sa.Boolean(),
            nullable=True,
            comment='Whether LLM ensemble validation passed'
        )
    )
    op.create_index(
        op.f('ix_validation_results_llm_passed'),
        'validation_results',
        ['llm_passed'],
        unique=False
    )

    # Add final_decision column
    op.add_column(
        'validation_results',
        sa.Column(
            'final_decision',
            sa.String(length=32),
            nullable=True,
            comment='Final combined decision: pass, fail, or uncertain'
        )
    )
    op.create_index(
        op.f('ix_validation_results_final_decision'),
        'validation_results',
        ['final_decision'],
        unique=False
    )


def downgrade() -> None:
    """Remove Houndify and LLM result columns from validation_results table."""
    op.drop_index(
        op.f('ix_validation_results_final_decision'),
        table_name='validation_results'
    )
    op.drop_column('validation_results', 'final_decision')

    op.drop_index(
        op.f('ix_validation_results_llm_passed'),
        table_name='validation_results'
    )
    op.drop_column('validation_results', 'llm_passed')

    op.drop_column('validation_results', 'houndify_result')

    op.drop_index(
        op.f('ix_validation_results_houndify_passed'),
        table_name='validation_results'
    )
    op.drop_column('validation_results', 'houndify_passed')
