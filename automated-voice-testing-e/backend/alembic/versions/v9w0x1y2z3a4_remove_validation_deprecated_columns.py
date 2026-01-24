"""Remove deprecated validation result columns.

Revision ID: v9w0x1y2z3a4
Revises: u8v9w0x1y2z3
Create Date: 2024-12-26

This migration removes unused columns from validation_results that were
never populated in the actual validation pipeline:

Removed columns:
- accuracy_score: Was planned for weighted accuracy but never populated
- confidence_score: Was planned for ML confidence but never populated
- semantic_similarity_score: Was planned for semantic ML but never populated
- wer_score: Word Error Rate - service existed but never called
- cer_score: Character Error Rate - service existed but never called
- ser_score: Sentence Error Rate - service existed but never called

The current validation architecture uses only:
- Houndify deterministic: command_kind_match_score, asr_confidence_score,
  houndify_passed, houndify_result
- LLM ensemble: llm_passed, ensemble_result
- Combined: final_decision, review_status
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'v9w0x1y2z3a4'
down_revision = 'u8v9w0x1y2z3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Remove deprecated columns from validation_results."""
    # Check if columns exist before dropping (safe for idempotent runs)
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_columns = {col['name'] for col in inspector.get_columns('validation_results')}

    columns_to_drop = [
        'accuracy_score',
        'confidence_score',
        'semantic_similarity_score',
        'wer_score',
        'cer_score',
        'ser_score',
    ]

    for column in columns_to_drop:
        if column in existing_columns:
            op.drop_column('validation_results', column)


def downgrade() -> None:
    """Restore deprecated columns (not recommended - columns were never used)."""
    op.add_column(
        'validation_results',
        sa.Column(
            'ser_score',
            sa.Float(),
            nullable=True,
            comment='Sentence Error Rate - DEPRECATED/UNUSED'
        )
    )
    op.add_column(
        'validation_results',
        sa.Column(
            'cer_score',
            sa.Float(),
            nullable=True,
            comment='Character Error Rate - DEPRECATED/UNUSED'
        )
    )
    op.add_column(
        'validation_results',
        sa.Column(
            'wer_score',
            sa.Float(),
            nullable=True,
            comment='Word Error Rate - DEPRECATED/UNUSED'
        )
    )
    op.add_column(
        'validation_results',
        sa.Column(
            'semantic_similarity_score',
            sa.Float(),
            nullable=True,
            comment='Semantic similarity - DEPRECATED/UNUSED'
        )
    )
    op.add_column(
        'validation_results',
        sa.Column(
            'confidence_score',
            sa.Float(),
            nullable=True,
            comment='Confidence score - DEPRECATED/UNUSED'
        )
    )
    op.add_column(
        'validation_results',
        sa.Column(
            'accuracy_score',
            sa.Float(),
            nullable=True,
            comment='Accuracy score - DEPRECATED/UNUSED'
        )
    )
