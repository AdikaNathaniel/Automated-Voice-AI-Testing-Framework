"""add llm_model_pricing and audit_trail tables

Revision ID: z3a4b5c6d7e8
Revises: y2z3a4b5c6d7
Create Date: 2025-12-29 19:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'z3a4b5c6d7e8'
down_revision = 'y2z3a4b5c6d7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create llm_model_pricing and audit_trail tables."""

    # Create llm_model_pricing table
    op.create_table(
        'llm_model_pricing',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('model_name', sa.String(length=100), nullable=False, comment='Name of the LLM model'),
        sa.Column('provider', sa.String(length=50), nullable=False, comment='API provider'),
        sa.Column('prompt_price_per_1m', sa.Numeric(precision=10, scale=2), nullable=False, comment='Price per 1M prompt tokens in USD'),
        sa.Column('completion_price_per_1m', sa.Numeric(precision=10, scale=2), nullable=False, comment='Price per 1M completion tokens in USD'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true', comment='Whether this pricing is active'),
        sa.Column('effective_date', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), comment='When this pricing became effective'),
        sa.Column('notes', sa.Text(), nullable=True, comment='Optional notes about pricing'),
        sa.Column('created_by', sa.UUID(), nullable=True, comment='User who created this entry'),
        sa.Column('updated_by', sa.UUID(), nullable=True, comment='User who last updated this entry'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('model_name', 'provider', 'effective_date', name='uq_model_provider_date')
    )

    # Create indexes for llm_model_pricing
    op.create_index('ix_llm_model_pricing_model_name', 'llm_model_pricing', ['model_name'])
    op.create_index('ix_llm_model_pricing_provider', 'llm_model_pricing', ['provider'])
    op.create_index('ix_llm_model_pricing_is_active', 'llm_model_pricing', ['is_active'])
    op.create_index('ix_llm_model_pricing_effective_date', 'llm_model_pricing', ['effective_date'])
    op.create_index('ix_llm_pricing_model_active', 'llm_model_pricing', ['model_name', 'is_active'])

    # Create audit_trail table
    op.create_table(
        'audit_trail',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('tenant_id', sa.UUID(), nullable=True, comment='Organization this audit belongs to'),
        sa.Column('user_id', sa.UUID(), nullable=True, comment='User who performed the action'),
        sa.Column('action_type', sa.String(length=50), nullable=False, comment='Type of action'),
        sa.Column('resource_type', sa.String(length=100), nullable=False, comment='Type of resource affected'),
        sa.Column('resource_id', sa.String(length=255), nullable=True, comment='ID of affected resource'),
        sa.Column('old_values', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Previous values'),
        sa.Column('new_values', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='New values'),
        sa.Column('changes_summary', sa.Text(), nullable=True, comment='Human-readable summary'),
        sa.Column('ip_address', sa.String(length=45), nullable=True, comment='IP address'),
        sa.Column('user_agent', sa.String(length=500), nullable=True, comment='User agent'),
        sa.Column('success', sa.Boolean(), nullable=False, server_default='true', comment='Whether action succeeded'),
        sa.Column('error_message', sa.Text(), nullable=True, comment='Error message if failed'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for audit_trail
    op.create_index('ix_audit_trail_tenant_id', 'audit_trail', ['tenant_id'])
    op.create_index('ix_audit_trail_user_id', 'audit_trail', ['user_id'])
    op.create_index('ix_audit_trail_action_type', 'audit_trail', ['action_type'])
    op.create_index('ix_audit_trail_resource_type', 'audit_trail', ['resource_type'])
    op.create_index('ix_audit_trail_resource_id', 'audit_trail', ['resource_id'])
    op.create_index('ix_audit_trail_success', 'audit_trail', ['success'])
    op.create_index('ix_audit_trail_created_at', 'audit_trail', ['created_at'])
    op.create_index('ix_audit_tenant_created', 'audit_trail', ['tenant_id', 'created_at'])
    op.create_index('ix_audit_user_created', 'audit_trail', ['user_id', 'created_at'])
    op.create_index('ix_audit_resource_created', 'audit_trail', ['resource_type', 'resource_id', 'created_at'])
    op.create_index('ix_audit_action_created', 'audit_trail', ['action_type', 'created_at'])


def downgrade() -> None:
    """Drop llm_model_pricing and audit_trail tables."""

    # Drop audit_trail indexes and table
    op.drop_index('ix_audit_action_created', table_name='audit_trail')
    op.drop_index('ix_audit_resource_created', table_name='audit_trail')
    op.drop_index('ix_audit_user_created', table_name='audit_trail')
    op.drop_index('ix_audit_tenant_created', table_name='audit_trail')
    op.drop_index('ix_audit_trail_created_at', table_name='audit_trail')
    op.drop_index('ix_audit_trail_success', table_name='audit_trail')
    op.drop_index('ix_audit_trail_resource_id', table_name='audit_trail')
    op.drop_index('ix_audit_trail_resource_type', table_name='audit_trail')
    op.drop_index('ix_audit_trail_action_type', table_name='audit_trail')
    op.drop_index('ix_audit_trail_user_id', table_name='audit_trail')
    op.drop_index('ix_audit_trail_tenant_id', table_name='audit_trail')
    op.drop_table('audit_trail')

    # Drop llm_model_pricing indexes and table
    op.drop_index('ix_llm_pricing_model_active', table_name='llm_model_pricing')
    op.drop_index('ix_llm_model_pricing_effective_date', table_name='llm_model_pricing')
    op.drop_index('ix_llm_model_pricing_is_active', table_name='llm_model_pricing')
    op.drop_index('ix_llm_model_pricing_provider', table_name='llm_model_pricing')
    op.drop_index('ix_llm_model_pricing_model_name', table_name='llm_model_pricing')
    op.drop_table('llm_model_pricing')
