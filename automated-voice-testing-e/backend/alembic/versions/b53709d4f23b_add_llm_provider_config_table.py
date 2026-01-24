"""add_llm_provider_config_table

Revision ID: b53709d4f23b
Revises: d130fbc33bea
Create Date: 2025-12-18 16:19:20.470926

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b53709d4f23b'
down_revision: Union[str, Sequence[str], None] = 'd130fbc33bea'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create llm_provider_configs table for storing encrypted API keys."""
    op.create_table(
        'llm_provider_configs',
        sa.Column(
            'id',
            postgresql.UUID(as_uuid=True),
            nullable=False,
            comment='Unique identifier for the record'
        ),
        sa.Column(
            'tenant_id',
            postgresql.UUID(as_uuid=True),
            nullable=True,
            comment='Tenant ID for multi-tenant isolation (null = global)'
        ),
        sa.Column(
            'provider',
            sa.String(length=50),
            nullable=False,
            comment='LLM provider name (openai, anthropic, google)'
        ),
        sa.Column(
            'display_name',
            sa.String(length=255),
            nullable=False,
            comment='Human-readable display name'
        ),
        sa.Column(
            'api_key_encrypted',
            sa.Text(),
            nullable=False,
            comment='Encrypted API key'
        ),
        sa.Column(
            'default_model',
            sa.String(length=100),
            nullable=True,
            comment='Default model name (gpt-4o, claude-3-5-sonnet, etc.)'
        ),
        sa.Column(
            'is_active',
            sa.Boolean(),
            nullable=False,
            server_default='true',
            comment='Whether this configuration is active'
        ),
        sa.Column(
            'is_default',
            sa.Boolean(),
            nullable=False,
            server_default='false',
            comment='Whether this is the default config for the provider'
        ),
        sa.Column(
            'temperature',
            sa.Float(),
            nullable=False,
            server_default='0.0',
            comment='Default temperature for API calls (0.0 = deterministic)'
        ),
        sa.Column(
            'max_tokens',
            sa.Float(),
            nullable=False,
            server_default='1024',
            comment='Default max tokens for API calls'
        ),
        sa.Column(
            'timeout_seconds',
            sa.Float(),
            nullable=False,
            server_default='30',
            comment='Request timeout in seconds'
        ),
        sa.Column(
            'config',
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment='Additional configuration (headers, base_url, etc.)'
        ),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
            comment='Timestamp when the record was created'
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
            comment='Timestamp when the record was last updated'
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(
            ['tenant_id'],
            ['users.id'],
            ondelete='CASCADE'
        )
    )

    # Create indexes for common query patterns
    op.create_index(
        'ix_llm_provider_configs_provider',
        'llm_provider_configs',
        ['provider'],
        unique=False
    )
    op.create_index(
        'ix_llm_provider_configs_tenant_id',
        'llm_provider_configs',
        ['tenant_id'],
        unique=False
    )
    op.create_index(
        'ix_llm_provider_configs_is_active',
        'llm_provider_configs',
        ['is_active'],
        unique=False
    )
    # Composite index for finding default config per provider
    op.create_index(
        'ix_llm_provider_configs_provider_is_default',
        'llm_provider_configs',
        ['provider', 'is_default'],
        unique=False
    )


def downgrade() -> None:
    """Drop llm_provider_configs table."""
    op.drop_index(
        'ix_llm_provider_configs_provider_is_default',
        table_name='llm_provider_configs'
    )
    op.drop_index(
        'ix_llm_provider_configs_is_active',
        table_name='llm_provider_configs'
    )
    op.drop_index(
        'ix_llm_provider_configs_tenant_id',
        table_name='llm_provider_configs'
    )
    op.drop_index(
        'ix_llm_provider_configs_provider',
        table_name='llm_provider_configs'
    )
    op.drop_table('llm_provider_configs')
