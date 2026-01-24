"""add_test_suite_scenarios_and_suite_id

Revision ID: 8723280c8610
Revises: a8b9c0d1e2f3
Create Date: 2025-12-16 09:15:26.673781

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '8723280c8610'
down_revision: Union[str, Sequence[str], None] = 'a8b9c0d1e2f3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create test_suite_scenarios association table
    op.create_table('test_suite_scenarios',
    sa.Column('suite_id', postgresql.UUID(as_uuid=True), nullable=False, comment='Test suite this scenario belongs to'),
    sa.Column('scenario_id', postgresql.UUID(as_uuid=True), nullable=False, comment='Scenario script in this suite'),
    sa.Column('order', sa.Integer(), nullable=False, default=0, comment='Order of scenario in suite for execution sequence'),
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, comment='Unique identifier for the record'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
    sa.ForeignKeyConstraint(['scenario_id'], ['scenario_scripts.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['suite_id'], ['test_suites.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('suite_id', 'scenario_id', name='uq_suite_scenario')
    )
    op.create_index(op.f('ix_test_suite_scenarios_scenario_id'), 'test_suite_scenarios', ['scenario_id'], unique=False)
    op.create_index(op.f('ix_test_suite_scenarios_suite_id'), 'test_suite_scenarios', ['suite_id'], unique=False)

    # Add suite_id column to multi_turn_executions
    op.add_column('multi_turn_executions', sa.Column('suite_id', postgresql.UUID(as_uuid=True), nullable=True, comment='Test suite this execution belongs to (nullable - not all executions are from suites)'))
    op.create_index(op.f('ix_multi_turn_executions_suite_id'), 'multi_turn_executions', ['suite_id'], unique=False)
    op.create_foreign_key('fk_multi_turn_executions_suite_id', 'multi_turn_executions', 'test_suites', ['suite_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop foreign key and index from multi_turn_executions
    op.drop_constraint('fk_multi_turn_executions_suite_id', 'multi_turn_executions', type_='foreignkey')
    op.drop_index(op.f('ix_multi_turn_executions_suite_id'), table_name='multi_turn_executions')
    op.drop_column('multi_turn_executions', 'suite_id')

    # Drop test_suite_scenarios table
    op.drop_index(op.f('ix_test_suite_scenarios_suite_id'), table_name='test_suite_scenarios')
    op.drop_index(op.f('ix_test_suite_scenarios_scenario_id'), table_name='test_suite_scenarios')
    op.drop_table('test_suite_scenarios')
