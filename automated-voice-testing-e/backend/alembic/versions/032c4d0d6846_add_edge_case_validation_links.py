"""add_edge_case_validation_links

Revision ID: 032c4d0d6846
Revises: k9l0m1n2o3p4
Create Date: 2025-12-24 17:47:28.138898

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '032c4d0d6846'
down_revision: Union[str, Sequence[str], None] = 'k9l0m1n2o3p4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add validation link fields to edge_cases table."""
    # Add human_validation_id foreign key
    op.add_column(
        'edge_cases',
        sa.Column(
            'human_validation_id',
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey('human_validations.id', ondelete='SET NULL'),
            nullable=True,
            comment='Link to the human validation that created this edge case'
        )
    )
    op.create_index(
        'ix_edge_cases_human_validation_id',
        'edge_cases',
        ['human_validation_id']
    )

    # Add validation_result_id foreign key
    op.add_column(
        'edge_cases',
        sa.Column(
            'validation_result_id',
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey('validation_results.id', ondelete='SET NULL'),
            nullable=True,
            comment='Link to the validation result being reviewed'
        )
    )
    op.create_index(
        'ix_edge_cases_validation_result_id',
        'edge_cases',
        ['validation_result_id']
    )

    # Add auto_created boolean flag
    op.add_column(
        'edge_cases',
        sa.Column(
            'auto_created',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('false'),
            comment='Whether this edge case was auto-created from validation or manually created'
        )
    )


def downgrade() -> None:
    """Remove validation link fields from edge_cases table."""
    op.drop_index('ix_edge_cases_validation_result_id', table_name='edge_cases')
    op.drop_column('edge_cases', 'validation_result_id')

    op.drop_index('ix_edge_cases_human_validation_id', table_name='edge_cases')
    op.drop_column('edge_cases', 'human_validation_id')

    op.drop_column('edge_cases', 'auto_created')
