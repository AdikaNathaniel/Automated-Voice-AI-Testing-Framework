"""add_pattern_analysis_configs_table

Revision ID: w0x1y2z3a4b5
Revises: v9w0x1y2z3a4
Create Date: 2025-12-29 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'w0x1y2z3a4b5'
down_revision: Union[str, None] = 'v9w0x1y2z3a4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create pattern_analysis_configs table for tenant-specific pattern analysis settings."""
    op.create_table(
        'pattern_analysis_configs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),

        # Time window settings
        sa.Column('lookback_days_recent', sa.Integer(), nullable=False, server_default='7',
                  comment='Days to look back for recent edge cases (prioritized)'),
        sa.Column('lookback_days_max', sa.Integer(), nullable=False, server_default='90',
                  comment='Maximum age of edge cases to analyze (hard limit)'),

        # Pattern formation settings
        sa.Column('min_pattern_size', sa.Integer(), nullable=False, server_default='3',
                  comment='Minimum edge cases required to form a pattern'),
        sa.Column('similarity_threshold', sa.Float(), nullable=False, server_default='0.85',
                  comment='Semantic similarity threshold (0.0-1.0)'),

        # LLM settings
        sa.Column('enable_llm_analysis', sa.Boolean(), nullable=False, server_default='true',
                  comment='Whether to use LLM-powered analysis'),
        sa.Column('llm_confidence_threshold', sa.Float(), nullable=False, server_default='0.70',
                  comment='Minimum LLM confidence for pattern matching (0.0-1.0)'),
        sa.Column('max_llm_calls_per_run', sa.Integer(), nullable=True,
                  comment='Budget limit: max LLM API calls per analysis run (null = unlimited)'),

        # Scheduling settings
        sa.Column('analysis_schedule', sa.String(length=100), nullable=False, server_default="'0 2 * * *'",
                  comment='Cron expression for analysis schedule (default: daily at 2 AM)'),
        sa.Column('enable_auto_analysis', sa.Boolean(), nullable=False, server_default='true',
                  comment='Whether to run automatic pattern analysis'),

        # Notification settings
        sa.Column('notify_on_new_patterns', sa.Boolean(), nullable=False, server_default='true',
                  comment='Send notifications when new patterns discovered'),
        sa.Column('notify_on_critical_patterns', sa.Boolean(), nullable=False, server_default='true',
                  comment='Send alerts for critical severity patterns'),

        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),

        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', name='uq_pattern_analysis_config_tenant')
    )

    # Create index on tenant_id for fast lookups
    op.create_index('ix_pattern_analysis_configs_tenant_id', 'pattern_analysis_configs', ['tenant_id'])


def downgrade() -> None:
    """Drop pattern_analysis_configs table."""
    op.drop_index('ix_pattern_analysis_configs_tenant_id', table_name='pattern_analysis_configs')
    op.drop_table('pattern_analysis_configs')
