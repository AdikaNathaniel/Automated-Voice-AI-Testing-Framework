"""Add integration_configs table

Revision ID: u8v9w0x1y2z3
Revises: t7u8v9w0x1y2
Create Date: 2025-12-26

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'u8v9w0x1y2z3'
down_revision = 't7u8v9w0x1y2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'integration_configs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('integration_type', sa.String(50), nullable=False),
        sa.Column('display_name', sa.String(255), nullable=True),
        sa.Column('is_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_connected', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('access_token_encrypted', sa.Text(), nullable=True),
        sa.Column('secret_encrypted', sa.Text(), nullable=True),
        sa.Column('settings', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('last_sync_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['tenant_id'], ['users.id'], ondelete='CASCADE'),
    )

    # Create indexes for common queries
    op.create_index('ix_integration_configs_tenant_id', 'integration_configs', ['tenant_id'])
    op.create_index('ix_integration_configs_integration_type', 'integration_configs', ['integration_type'])
    op.create_index(
        'ix_integration_configs_tenant_type',
        'integration_configs',
        ['tenant_id', 'integration_type'],
        unique=True
    )


def downgrade() -> None:
    op.drop_index('ix_integration_configs_tenant_type', table_name='integration_configs')
    op.drop_index('ix_integration_configs_integration_type', table_name='integration_configs')
    op.drop_index('ix_integration_configs_tenant_id', table_name='integration_configs')
    op.drop_table('integration_configs')
