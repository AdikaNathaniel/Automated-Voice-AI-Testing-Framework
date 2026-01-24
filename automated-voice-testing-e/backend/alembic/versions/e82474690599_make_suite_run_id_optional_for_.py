"""make suite_run_id optional for standalone scenarios

Revision ID: e82474690599
Revises: 1586da48ab0f
Create Date: 2025-12-27 17:18:59.669164

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e82474690599'
down_revision: Union[str, Sequence[str], None] = '1586da48ab0f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Make suite_run_id nullable to support standalone scenario executions
    op.alter_column('multi_turn_executions', 'suite_run_id',
                    existing_type=sa.dialects.postgresql.UUID(),
                    nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    # Make suite_run_id non-nullable again
    op.alter_column('multi_turn_executions', 'suite_run_id',
                    existing_type=sa.dialects.postgresql.UUID(),
                    nullable=False)
