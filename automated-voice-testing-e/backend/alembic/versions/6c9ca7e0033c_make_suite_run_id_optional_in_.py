"""make suite_run_id optional in validation_results

Revision ID: 6c9ca7e0033c
Revises: e82474690599
Create Date: 2025-12-27 17:32:25.974826

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6c9ca7e0033c'
down_revision: Union[str, Sequence[str], None] = 'e82474690599'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Make suite_run_id nullable to support standalone scenario executions
    op.alter_column('validation_results', 'suite_run_id',
                    existing_type=sa.dialects.postgresql.UUID(),
                    nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    # Make suite_run_id non-nullable again
    op.alter_column('validation_results', 'suite_run_id',
                    existing_type=sa.dialects.postgresql.UUID(),
                    nullable=False)
