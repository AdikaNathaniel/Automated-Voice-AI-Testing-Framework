"""add_categories_table_simple

Revision ID: 1586da48ab0f
Revises: v9w0x1y2z3a4
Create Date: 2025-12-27 13:17:08.589003

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1586da48ab0f'
down_revision: Union[str, Sequence[str], None] = 'v9w0x1y2z3a4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add categories table for scenario organization."""
    op.create_table(
        'categories',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False, comment='Category name (unique within tenant)'),
        sa.Column('display_name', sa.String(length=150), nullable=True, comment='Human-readable display name for the category'),
        sa.Column('description', sa.Text(), nullable=True, comment='Description of what scenarios belong to this category'),
        sa.Column('color', sa.String(length=7), nullable=True, comment='Hex color code for UI display (e.g., #FF5733)'),
        sa.Column('icon', sa.String(length=50), nullable=True, comment='Icon name/identifier for UI display'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true', comment='Whether this category is active and available for use'),
        sa.Column('is_system', sa.Boolean(), nullable=False, server_default='false', comment='Whether this is a system-defined category (cannot be deleted)'),
        sa.Column('tenant_id', sa.UUID(), nullable=True, comment='Tenant identifier for multi-tenant scoping'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', 'tenant_id', name='uq_category_name_tenant')
    )

    # Create indexes
    op.create_index(op.f('ix_categories_name'), 'categories', ['name'], unique=False)
    op.create_index(op.f('ix_categories_tenant_id'), 'categories', ['tenant_id'], unique=False)


def downgrade() -> None:
    """Remove categories table."""
    op.drop_index(op.f('ix_categories_tenant_id'), table_name='categories')
    op.drop_index(op.f('ix_categories_name'), table_name='categories')
    op.drop_table('categories')
