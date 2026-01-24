"""Add organization fields to users table

Revision ID: s6t7u8v9w0x1
Revises: r5s6t7u8v9w0
Create Date: 2024-12-26

Adds:
- is_organization_owner: Boolean flag to mark org accounts
- organization_name: Name of the organization
- organization_settings: JSONB for org-specific settings
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = 's6t7u8v9w0x1'
down_revision = 'r5s6t7u8v9w0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add organization fields to users table
    op.add_column(
        'users',
        sa.Column(
            'is_organization_owner',
            sa.Boolean(),
            nullable=False,
            server_default='false',
            comment='Whether this user represents an organization'
        )
    )
    op.add_column(
        'users',
        sa.Column(
            'organization_name',
            sa.String(255),
            nullable=True,
            comment='Organization name (only set if is_organization_owner=True)'
        )
    )
    op.add_column(
        'users',
        sa.Column(
            'organization_settings',
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment='Organization-specific settings (billing, limits, features)'
        )
    )

    # Create index on organization_name for searching
    op.create_index(
        'ix_users_organization_name',
        'users',
        ['organization_name'],
        unique=False
    )

    # Create partial index for org owners only
    op.create_index(
        'ix_users_is_organization_owner',
        'users',
        ['is_organization_owner'],
        unique=False,
        postgresql_where=sa.text('is_organization_owner = true')
    )


def downgrade() -> None:
    op.drop_index('ix_users_is_organization_owner', table_name='users')
    op.drop_index('ix_users_organization_name', table_name='users')
    op.drop_column('users', 'organization_settings')
    op.drop_column('users', 'organization_name')
    op.drop_column('users', 'is_organization_owner')
