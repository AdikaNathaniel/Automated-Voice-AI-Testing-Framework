"""add_notification_configs_table

Revision ID: 782d67f47f3d
Revises: q4r5s6t7u8v9
Create Date: 2025-12-26 11:52:21.530873

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '782d67f47f3d'
down_revision: Union[str, Sequence[str], None] = 'q4r5s6t7u8v9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create notification_configs table for tenant notification settings."""
    op.create_table(
        'notification_configs',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('tenant_id', sa.UUID(), nullable=True),
        sa.Column('channel_type', sa.String(length=50), nullable=False, server_default='slack'),
        sa.Column('display_name', sa.String(length=255), nullable=True),
        sa.Column('webhook_url_encrypted', sa.Text(), nullable=True),
        sa.Column('bot_token_encrypted', sa.Text(), nullable=True),
        sa.Column('signing_secret_encrypted', sa.Text(), nullable=True),
        sa.Column('is_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_connected', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('workspace_name', sa.String(length=255), nullable=True),
        sa.Column('workspace_icon_url', sa.Text(), nullable=True),
        sa.Column('default_channel', sa.String(length=255), nullable=True),
        sa.Column(
            'notification_preferences',
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            server_default='{}',
        ),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(['tenant_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_notification_configs_channel_type'),
        'notification_configs',
        ['channel_type'],
        unique=False,
    )
    op.create_index(
        op.f('ix_notification_configs_tenant_id'),
        'notification_configs',
        ['tenant_id'],
        unique=False,
    )


def downgrade() -> None:
    """Drop notification_configs table."""
    op.drop_index(op.f('ix_notification_configs_tenant_id'), table_name='notification_configs')
    op.drop_index(op.f('ix_notification_configs_channel_type'), table_name='notification_configs')
    op.drop_table('notification_configs')
