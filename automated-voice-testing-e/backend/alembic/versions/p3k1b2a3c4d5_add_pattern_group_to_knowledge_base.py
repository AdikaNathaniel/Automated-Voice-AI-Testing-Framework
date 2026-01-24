"""add_pattern_group_to_knowledge_base

Revision ID: p3k1b2a3c4d5
Revises: 5a71450d6aac
Create Date: 2024-12-25 18:00:00.000000

Phase 3 of Edge Case workflow: Link Knowledge Base articles to Pattern Groups.
Adds pattern_group_id, source_type, and tags columns to knowledge_base table.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import sys
import os

# Add backend to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from models.base import GUID

# revision identifiers, used by Alembic.
revision: str = 'p3k1b2a3c4d5'
down_revision: Union[str, Sequence[str], None] = '5a71450d6aac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add pattern group integration fields to knowledge_base table."""
    # Add pattern_group_id column with foreign key
    op.add_column(
        'knowledge_base',
        sa.Column(
            'pattern_group_id',
            GUID(),
            nullable=True,
            comment='Link to pattern group if auto-generated from pattern analysis'
        )
    )

    # Add source_type column
    op.add_column(
        'knowledge_base',
        sa.Column(
            'source_type',
            sa.String(length=50),
            server_default=sa.text("'manual'"),
            nullable=False,
            comment='Article source: manual, auto_generated, pattern_derived'
        )
    )

    # Add tags array column
    op.add_column(
        'knowledge_base',
        sa.Column(
            'tags',
            postgresql.ARRAY(sa.String(100)),
            server_default=sa.text("'{}'::varchar[]"),
            nullable=False,
            comment='Array of tags for multi-label categorization'
        )
    )

    # Create foreign key constraint
    op.create_foreign_key(
        'fk_knowledge_base_pattern_group_id',
        'knowledge_base',
        'pattern_groups',
        ['pattern_group_id'],
        ['id'],
        ondelete='SET NULL'
    )

    # Create index for pattern_group_id lookups
    op.create_index(
        'ix_knowledge_base_pattern_group_id',
        'knowledge_base',
        ['pattern_group_id'],
        unique=False
    )

    # Create index for source_type filtering
    op.create_index(
        'ix_knowledge_base_source_type',
        'knowledge_base',
        ['source_type'],
        unique=False
    )


def downgrade() -> None:
    """Remove pattern group integration fields from knowledge_base table."""
    op.drop_index('ix_knowledge_base_source_type', table_name='knowledge_base')
    op.drop_index('ix_knowledge_base_pattern_group_id', table_name='knowledge_base')
    op.drop_constraint('fk_knowledge_base_pattern_group_id', 'knowledge_base', type_='foreignkey')
    op.drop_column('knowledge_base', 'tags')
    op.drop_column('knowledge_base', 'source_type')
    op.drop_column('knowledge_base', 'pattern_group_id')
