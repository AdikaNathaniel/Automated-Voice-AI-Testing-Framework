"""create_pattern_groups_and_links

Revision ID: 5a71450d6aac
Revises: 032c4d0d6846
Create Date: 2025-12-24 18:59:16.813357

Phase 2 of Edge Case workflow: Add pattern groups and links.
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
revision: str = '5a71450d6aac'
down_revision: Union[str, Sequence[str], None] = '032c4d0d6846'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Create pattern_groups and edge_case_pattern_links tables."""
    # Create pattern_groups table
    op.create_table(
        'pattern_groups',
        sa.Column('id', GUID(), nullable=False, comment='Primary identifier for the pattern group'),
        sa.Column('name', sa.String(length=200), nullable=False, comment='Short descriptive name of the pattern'),
        sa.Column('description', sa.Text(), nullable=True, comment='Detailed explanation of what the pattern represents'),
        sa.Column('pattern_type', sa.String(length=100), nullable=True, comment='Type of pattern: semantic, entity, context, ambiguity, etc.'),
        sa.Column('severity', sa.String(length=50), server_default=sa.text("'medium'"), nullable=False, comment='Impact level: critical, high, medium, low'),
        sa.Column('first_seen', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='When this pattern was first detected'),
        sa.Column('last_seen', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='When this pattern was last observed'),
        sa.Column('occurrence_count', sa.Integer(), server_default=sa.text('0'), nullable=False, comment='Total number of edge cases matching this pattern'),
        sa.Column('status', sa.String(length=50), server_default=sa.text("'active'"), nullable=False, comment='Lifecycle state: active, resolved, monitoring'),
        sa.Column('suggested_actions', postgresql.JSONB(astext_type=sa.Text()).with_variant(sa.JSON(), 'sqlite'), nullable=True, comment='Recommended actions to address this pattern'),
        sa.Column('pattern_metadata', postgresql.JSONB(astext_type=sa.Text()).with_variant(sa.JSON(), 'sqlite'), nullable=True, comment='Additional pattern-specific data and metrics'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the pattern group was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the pattern group was last updated'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create edge_case_pattern_links table
    op.create_table(
        'edge_case_pattern_links',
        sa.Column('id', GUID(), nullable=False),
        sa.Column('edge_case_id', GUID(), nullable=False, comment='Edge case in this pattern group'),
        sa.Column('pattern_group_id', GUID(), nullable=False, comment='Pattern group this edge case belongs to'),
        sa.Column('similarity_score', sa.Float(), nullable=True, comment='Similarity score (0.0-1.0) indicating pattern match strength'),
        sa.Column('added_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='When this edge case was added to the pattern group'),
        sa.ForeignKeyConstraint(['edge_case_id'], ['edge_cases.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['pattern_group_id'], ['pattern_groups.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('edge_case_id', 'pattern_group_id', name='uix_edge_case_pattern')
    )

    # Create indexes
    op.create_index(op.f('ix_edge_case_pattern_links_edge_case_id'), 'edge_case_pattern_links', ['edge_case_id'], unique=False)
    op.create_index(op.f('ix_edge_case_pattern_links_pattern_group_id'), 'edge_case_pattern_links', ['pattern_group_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema - Drop pattern_groups and edge_case_pattern_links tables."""
    op.drop_index(op.f('ix_edge_case_pattern_links_pattern_group_id'), table_name='edge_case_pattern_links')
    op.drop_index(op.f('ix_edge_case_pattern_links_edge_case_id'), table_name='edge_case_pattern_links')
    op.drop_table('edge_case_pattern_links')
    op.drop_table('pattern_groups')
