"""Migrate quality tables to use script_id, drop test_case_id

This migration:
1. Adds script_id and execution_id to defects table
2. Adds script_id to edge_cases table
3. Creates regression_baselines table with script_id
4. Drops test_case_id from defects and edge_cases (complete migration to scenario-based)

Revision ID: e4f5g6h7i8j9
Revises: b53709d4f23b
Create Date: 2025-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'e4f5g6h7i8j9'
down_revision = 'b53709d4f23b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    # Helper to check if constraint exists
    def constraint_exists(constraint_name: str, table_name: str) -> bool:
        result = conn.execute(sa.text("""
            SELECT 1 FROM information_schema.table_constraints
            WHERE constraint_name = :constraint_name
            AND table_name = :table_name
        """), {"constraint_name": constraint_name, "table_name": table_name})
        return result.fetchone() is not None

    # Helper to check if index exists
    def index_exists(index_name: str) -> bool:
        result = conn.execute(sa.text("""
            SELECT 1 FROM pg_indexes
            WHERE indexname = :index_name
        """), {"index_name": index_name})
        return result.fetchone() is not None

    # Helper to check if column exists
    def column_exists(table_name: str, column_name: str) -> bool:
        result = conn.execute(sa.text("""
            SELECT 1 FROM information_schema.columns
            WHERE table_name = :table_name AND column_name = :column_name
        """), {"table_name": table_name, "column_name": column_name})
        return result.fetchone() is not None

    # Add script_id and execution_id to defects table (if not already present)
    if not column_exists('defects', 'script_id'):
        op.add_column(
            'defects',
            sa.Column(
                'script_id',
                postgresql.UUID(as_uuid=True),
                nullable=True,
                comment='Scenario script that produced the defect'
            )
        )
    if not column_exists('defects', 'execution_id'):
        op.add_column(
            'defects',
            sa.Column(
                'execution_id',
                postgresql.UUID(as_uuid=True),
                nullable=True,
                comment='Multi-turn execution where the defect was detected'
            )
        )
    if not index_exists('ix_defects_script_id'):
        op.create_index('ix_defects_script_id', 'defects', ['script_id'])
    if not index_exists('ix_defects_execution_id'):
        op.create_index('ix_defects_execution_id', 'defects', ['execution_id'])
    if not constraint_exists('fk_defects_script_id', 'defects'):
        op.create_foreign_key(
            'fk_defects_script_id',
            'defects',
            'scenario_scripts',
            ['script_id'],
            ['id'],
            ondelete='SET NULL'
        )
    if not constraint_exists('fk_defects_execution_id', 'defects'):
        op.create_foreign_key(
            'fk_defects_execution_id',
            'defects',
            'multi_turn_executions',
            ['execution_id'],
            ['id'],
            ondelete='SET NULL'
        )

    # Drop test_case_id from defects (complete migration to scenario-based)
    # First drop foreign key if exists
    if constraint_exists('defects_test_case_id_fkey', 'defects'):
        op.drop_constraint('defects_test_case_id_fkey', 'defects', type_='foreignkey')
    if index_exists('ix_defects_test_case_id'):
        op.drop_index('ix_defects_test_case_id', table_name='defects')
    if column_exists('defects', 'test_case_id'):
        op.drop_column('defects', 'test_case_id')

    # Add script_id to edge_cases table (if not already present)
    if not column_exists('edge_cases', 'script_id'):
        op.add_column(
            'edge_cases',
            sa.Column(
                'script_id',
                postgresql.UUID(as_uuid=True),
                nullable=True,
                comment='Scenario script that exhibits this edge case'
            )
        )
    if not index_exists('ix_edge_cases_script_id'):
        op.create_index('ix_edge_cases_script_id', 'edge_cases', ['script_id'])
    if not constraint_exists('fk_edge_cases_script_id', 'edge_cases'):
        op.create_foreign_key(
            'fk_edge_cases_script_id',
            'edge_cases',
            'scenario_scripts',
            ['script_id'],
            ['id'],
            ondelete='SET NULL'
        )

    # Drop test_case_id from edge_cases (complete migration to scenario-based)
    if constraint_exists('edge_cases_test_case_id_fkey', 'edge_cases'):
        op.drop_constraint('edge_cases_test_case_id_fkey', 'edge_cases', type_='foreignkey')
    if column_exists('edge_cases', 'test_case_id'):
        op.drop_column('edge_cases', 'test_case_id')

    # Helper to check if table exists
    def table_exists(table_name: str) -> bool:
        result = conn.execute(sa.text("""
            SELECT 1 FROM information_schema.tables
            WHERE table_name = :table_name
        """), {"table_name": table_name})
        return result.fetchone() is not None

    # Create regression_baselines table (didn't exist before)
    if table_exists('regression_baselines'):
        return  # Table already exists, skip creation

    op.create_table(
        'regression_baselines',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column('script_id', sa.String(36), nullable=False, unique=True, index=True,
                  comment='Scenario script whose baseline is stored'),
        sa.Column('result_status', sa.String(32), nullable=False,
                  comment='Status associated with the approved baseline'),
        sa.Column('metrics', sa.JSON, nullable=False, server_default='{}',
                  comment='Numeric metrics captured for the baseline run'),
        sa.Column('version', sa.Integer, nullable=False, server_default='1',
                  comment='Monotonic version number incremented on each approval'),
        sa.Column('approved_by', sa.String(36), nullable=True,
                  comment='Identifier of the user who approved the baseline'),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True,
                  comment='Timestamp when the baseline was approved'),
        sa.Column('note', sa.Text, nullable=True,
                  comment='Optional justification or note'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now(), onupdate=sa.func.now()),
    )


def downgrade() -> None:
    # Drop regression_baselines table
    op.drop_table('regression_baselines')

    # Restore test_case_id to edge_cases and remove script_id
    op.add_column(
        'edge_cases',
        sa.Column('test_case_id', postgresql.UUID(as_uuid=True), nullable=True)
    )
    op.drop_constraint('fk_edge_cases_script_id', 'edge_cases', type_='foreignkey')
    op.drop_index('ix_edge_cases_script_id', table_name='edge_cases')
    op.drop_column('edge_cases', 'script_id')

    # Restore test_case_id to defects and remove script_id/execution_id
    op.add_column(
        'defects',
        sa.Column('test_case_id', postgresql.UUID(as_uuid=True), nullable=True)
    )
    op.drop_constraint('fk_defects_execution_id', 'defects', type_='foreignkey')
    op.drop_constraint('fk_defects_script_id', 'defects', type_='foreignkey')
    op.drop_index('ix_defects_execution_id', table_name='defects')
    op.drop_index('ix_defects_script_id', table_name='defects')
    op.drop_column('defects', 'execution_id')
    op.drop_column('defects', 'script_id')
