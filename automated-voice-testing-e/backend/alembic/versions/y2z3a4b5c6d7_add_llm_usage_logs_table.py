"""add llm_usage_logs table for cost tracking

Revision ID: y2z3a4b5c6d7
Revises: w0x1y2z3a4b5, 86ad0dfb433b
Create Date: 2025-12-29 18:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'y2z3a4b5c6d7'
down_revision: Union[str, Sequence[str], None] = ('w0x1y2z3a4b5', '86ad0dfb433b')
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create llm_usage_logs table for tracking LLM API usage and costs."""
    op.create_table(
        'llm_usage_logs',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('tenant_id', sa.UUID(), nullable=False, comment='Organization that made this LLM call'),
        sa.Column('service_name', sa.String(length=100), nullable=False, comment='Service that made the call (pattern_analysis, validation, etc.)'),
        sa.Column('operation', sa.String(length=100), nullable=False, comment='Specific operation (analyze_edge_case, match_pattern, etc.)'),
        sa.Column('model', sa.String(length=100), nullable=False, comment='LLM model used (claude-sonnet-4.5, gpt-4, etc.)'),
        sa.Column('provider', sa.String(length=50), nullable=False, comment='API provider (openrouter, anthropic, openai, etc.)'),
        sa.Column('prompt_tokens', sa.Integer(), nullable=True, comment='Number of tokens in the prompt'),
        sa.Column('completion_tokens', sa.Integer(), nullable=True, comment='Number of tokens in the completion'),
        sa.Column('total_tokens', sa.Integer(), nullable=True, comment='Total tokens used (prompt + completion)'),
        sa.Column('estimated_cost_usd', sa.Numeric(precision=10, scale=6), nullable=True, comment='Estimated cost in USD (based on current pricing)'),
        sa.Column('request_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Additional request context (task_id, edge_case_id, pattern_id, etc.)'),
        sa.Column('response_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Provider response metadata (request_id, model_version, etc.)'),
        sa.Column('duration_ms', sa.Integer(), nullable=True, comment='API call duration in milliseconds'),
        sa.Column('success', sa.Boolean(), nullable=False, server_default='true', comment='Whether the API call succeeded'),
        sa.Column('error_message', sa.Text(), nullable=True, comment='Error message if call failed'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), comment='When this call was made'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for common query patterns
    op.create_index('ix_llm_usage_logs_tenant_id', 'llm_usage_logs', ['tenant_id'])
    op.create_index('ix_llm_usage_logs_service_name', 'llm_usage_logs', ['service_name'])
    op.create_index('ix_llm_usage_logs_model', 'llm_usage_logs', ['model'])
    op.create_index('ix_llm_usage_logs_provider', 'llm_usage_logs', ['provider'])
    op.create_index('ix_llm_usage_logs_total_tokens', 'llm_usage_logs', ['total_tokens'])
    op.create_index('ix_llm_usage_logs_success', 'llm_usage_logs', ['success'])
    op.create_index('ix_llm_usage_logs_created_at', 'llm_usage_logs', ['created_at'])

    # Composite indexes for common analytics queries
    op.create_index('ix_llm_usage_tenant_created', 'llm_usage_logs', ['tenant_id', 'created_at'])
    op.create_index('ix_llm_usage_service_created', 'llm_usage_logs', ['service_name', 'created_at'])
    op.create_index('ix_llm_usage_model_created', 'llm_usage_logs', ['model', 'created_at'])
    op.create_index('ix_llm_usage_success_created', 'llm_usage_logs', ['success', 'created_at'])


def downgrade() -> None:
    """Drop llm_usage_logs table."""
    op.drop_index('ix_llm_usage_success_created', table_name='llm_usage_logs')
    op.drop_index('ix_llm_usage_model_created', table_name='llm_usage_logs')
    op.drop_index('ix_llm_usage_service_created', table_name='llm_usage_logs')
    op.drop_index('ix_llm_usage_tenant_created', table_name='llm_usage_logs')
    op.drop_index('ix_llm_usage_logs_created_at', table_name='llm_usage_logs')
    op.drop_index('ix_llm_usage_logs_success', table_name='llm_usage_logs')
    op.drop_index('ix_llm_usage_logs_total_tokens', table_name='llm_usage_logs')
    op.drop_index('ix_llm_usage_logs_provider', table_name='llm_usage_logs')
    op.drop_index('ix_llm_usage_logs_model', table_name='llm_usage_logs')
    op.drop_index('ix_llm_usage_logs_service_name', table_name='llm_usage_logs')
    op.drop_index('ix_llm_usage_logs_tenant_id', table_name='llm_usage_logs')
    op.drop_table('llm_usage_logs')
