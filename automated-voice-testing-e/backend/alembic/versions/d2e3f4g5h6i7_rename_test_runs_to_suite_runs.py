"""Rename test_runs to suite_runs

Revision ID: d2e3f4g5h6i7
Revises: c1d2e3f4g5h6
Create Date: 2025-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'd2e3f4g5h6i7'
down_revision: Union[str, None] = 'c1d2e3f4g5h6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Rename test_runs table and related columns to suite_runs."""
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

    # Helper to check if table exists
    def table_exists(table_name: str) -> bool:
        result = conn.execute(sa.text("""
            SELECT 1 FROM information_schema.tables
            WHERE table_name = :table_name
        """), {"table_name": table_name})
        return result.fetchone() is not None

    # Helper to check if column exists
    def column_exists(table_name: str, column_name: str) -> bool:
        result = conn.execute(sa.text("""
            SELECT 1 FROM information_schema.columns
            WHERE table_name = :table_name AND column_name = :column_name
        """), {"table_name": table_name, "column_name": column_name})
        return result.fetchone() is not None

    # Skip if already migrated (suite_runs exists)
    if table_exists('suite_runs'):
        print("Migration already applied - suite_runs table exists")
        return

    # Skip if test_runs doesn't exist
    if not table_exists('test_runs'):
        print("Nothing to migrate - test_runs table doesn't exist")
        return

    # Step 1: Drop foreign key constraints that reference test_runs
    fk_constraints = [
        ('multi_turn_executions_test_run_id_fkey', 'multi_turn_executions'),
        ('voice_test_executions_test_run_id_fkey', 'voice_test_executions'),
        ('test_cases_test_run_id_fkey', 'test_cases'),
        ('validation_results_test_run_id_fkey', 'validation_results'),
    ]

    for constraint_name, fk_table_name in fk_constraints:
        if table_exists(fk_table_name) and constraint_exists(constraint_name, fk_table_name):
            op.drop_constraint(constraint_name, fk_table_name, type_='foreignkey')
            print(f"Dropped constraint {constraint_name}")

    # Step 2: Drop indexes on test_run_id columns (use IF EXISTS via raw SQL)
    indexes_to_drop = [
        'ix_multi_turn_executions_test_run_id',
        'ix_voice_test_executions_test_run_id',
    ]

    for index_name in indexes_to_drop:
        if index_exists(index_name):
            op.execute(sa.text(f'DROP INDEX IF EXISTS {index_name}'))
            print(f"Dropped index {index_name}")

    # Step 3: Rename the main table
    op.rename_table('test_runs', 'suite_runs')
    print("Renamed test_runs to suite_runs")

    # Step 4: Rename indexes on the suite_runs table (if they exist)
    index_renames = [
        ('ix_test_runs_suite_id', 'ix_suite_runs_suite_id'),
        ('ix_test_runs_created_by', 'ix_suite_runs_created_by'),
        ('ix_test_runs_status', 'ix_suite_runs_status'),
        ('ix_test_runs_tenant_id', 'ix_suite_runs_tenant_id'),
        ('ix_test_runs_category_name', 'ix_suite_runs_category_name'),
    ]

    for old_name, new_name in index_renames:
        if index_exists(old_name):
            op.execute(sa.text(f'ALTER INDEX {old_name} RENAME TO {new_name}'))
            print(f"Renamed index {old_name} to {new_name}")

    # Step 5: Rename the primary key constraint (if exists)
    if index_exists('test_runs_pkey'):
        op.execute(sa.text('ALTER INDEX test_runs_pkey RENAME TO suite_runs_pkey'))
        print("Renamed primary key")

    # Step 6: Rename foreign key columns in referencing tables
    if column_exists('multi_turn_executions', 'test_run_id'):
        op.alter_column(
            'multi_turn_executions',
            'test_run_id',
            new_column_name='suite_run_id'
        )
        print("Renamed multi_turn_executions.test_run_id to suite_run_id")

    if table_exists('voice_test_executions') and column_exists('voice_test_executions', 'test_run_id'):
        op.alter_column(
            'voice_test_executions',
            'test_run_id',
            new_column_name='suite_run_id'
        )
        print("Renamed voice_test_executions.test_run_id to suite_run_id")

    # Handle validation_results - may need rename or add
    if column_exists('validation_results', 'test_run_id'):
        op.alter_column(
            'validation_results',
            'test_run_id',
            new_column_name='suite_run_id'
        )
        print("Renamed validation_results.test_run_id to suite_run_id")
    elif not column_exists('validation_results', 'suite_run_id'):
        # Column doesn't exist at all - add it
        op.add_column(
            'validation_results',
            sa.Column('suite_run_id', postgresql.UUID(as_uuid=True), nullable=True)
        )
        print("Added validation_results.suite_run_id column")

    # Step 7: Recreate indexes with new names
    if column_exists('multi_turn_executions', 'suite_run_id'):
        if not index_exists('ix_multi_turn_executions_suite_run_id'):
            op.create_index(
                'ix_multi_turn_executions_suite_run_id',
                'multi_turn_executions',
                ['suite_run_id']
            )
            print("Created index ix_multi_turn_executions_suite_run_id")

    if table_exists('voice_test_executions') and column_exists('voice_test_executions', 'suite_run_id'):
        if not index_exists('ix_voice_test_executions_suite_run_id'):
            op.create_index(
                'ix_voice_test_executions_suite_run_id',
                'voice_test_executions',
                ['suite_run_id']
            )
            print("Created index ix_voice_test_executions_suite_run_id")

    # Step 8: Recreate foreign key constraints with new names
    if column_exists('multi_turn_executions', 'suite_run_id'):
        if not constraint_exists('multi_turn_executions_suite_run_id_fkey', 'multi_turn_executions'):
            op.create_foreign_key(
                'multi_turn_executions_suite_run_id_fkey',
                'multi_turn_executions',
                'suite_runs',
                ['suite_run_id'],
                ['id']
            )
            print("Created FK multi_turn_executions_suite_run_id_fkey")

    if table_exists('voice_test_executions') and column_exists('voice_test_executions', 'suite_run_id'):
        if not constraint_exists('voice_test_executions_suite_run_id_fkey', 'voice_test_executions'):
            op.create_foreign_key(
                'voice_test_executions_suite_run_id_fkey',
                'voice_test_executions',
                'suite_runs',
                ['suite_run_id'],
                ['id']
            )
            print("Created FK voice_test_executions_suite_run_id_fkey")

    # Handle validation_results index and FK
    if column_exists('validation_results', 'suite_run_id'):
        if not index_exists('ix_validation_results_suite_run_id'):
            op.create_index(
                'ix_validation_results_suite_run_id',
                'validation_results',
                ['suite_run_id']
            )
            print("Created index ix_validation_results_suite_run_id")

        if not constraint_exists('validation_results_suite_run_id_fkey', 'validation_results'):
            op.create_foreign_key(
                'validation_results_suite_run_id_fkey',
                'validation_results',
                'suite_runs',
                ['suite_run_id'],
                ['id']
            )
            print("Created FK validation_results_suite_run_id_fkey")


def downgrade() -> None:
    """Revert suite_runs back to test_runs."""
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

    # Helper to check if table exists
    def table_exists(table_name: str) -> bool:
        result = conn.execute(sa.text("""
            SELECT 1 FROM information_schema.tables
            WHERE table_name = :table_name
        """), {"table_name": table_name})
        return result.fetchone() is not None

    # Helper to check if column exists
    def column_exists(table_name: str, column_name: str) -> bool:
        result = conn.execute(sa.text("""
            SELECT 1 FROM information_schema.columns
            WHERE table_name = :table_name AND column_name = :column_name
        """), {"table_name": table_name, "column_name": column_name})
        return result.fetchone() is not None

    # Skip if already downgraded
    if table_exists('test_runs'):
        print("Already downgraded - test_runs table exists")
        return

    if not table_exists('suite_runs'):
        print("Nothing to downgrade - suite_runs table doesn't exist")
        return

    # Drop new foreign key constraints
    if constraint_exists('multi_turn_executions_suite_run_id_fkey', 'multi_turn_executions'):
        op.drop_constraint(
            'multi_turn_executions_suite_run_id_fkey',
            'multi_turn_executions',
            type_='foreignkey'
        )

    if constraint_exists('voice_test_executions_suite_run_id_fkey', 'voice_test_executions'):
        op.drop_constraint(
            'voice_test_executions_suite_run_id_fkey',
            'voice_test_executions',
            type_='foreignkey'
        )

    # Drop new indexes
    if index_exists('ix_multi_turn_executions_suite_run_id'):
        op.execute(sa.text('DROP INDEX IF EXISTS ix_multi_turn_executions_suite_run_id'))

    if index_exists('ix_voice_test_executions_suite_run_id'):
        op.execute(sa.text('DROP INDEX IF EXISTS ix_voice_test_executions_suite_run_id'))

    # Rename columns back
    if column_exists('multi_turn_executions', 'suite_run_id'):
        op.alter_column(
            'multi_turn_executions',
            'suite_run_id',
            new_column_name='test_run_id'
        )

    if column_exists('voice_test_executions', 'suite_run_id'):
        op.alter_column(
            'voice_test_executions',
            'suite_run_id',
            new_column_name='test_run_id'
        )

    # Rename indexes back
    index_renames = [
        ('ix_suite_runs_suite_id', 'ix_test_runs_suite_id'),
        ('ix_suite_runs_created_by', 'ix_test_runs_created_by'),
        ('ix_suite_runs_status', 'ix_test_runs_status'),
        ('ix_suite_runs_tenant_id', 'ix_test_runs_tenant_id'),
        ('ix_suite_runs_category_name', 'ix_test_runs_category_name'),
    ]

    for old_name, new_name in index_renames:
        if index_exists(old_name):
            op.execute(sa.text(f'ALTER INDEX {old_name} RENAME TO {new_name}'))

    if index_exists('suite_runs_pkey'):
        op.execute(sa.text('ALTER INDEX suite_runs_pkey RENAME TO test_runs_pkey'))

    # Rename table back
    op.rename_table('suite_runs', 'test_runs')

    # Recreate old indexes
    if column_exists('multi_turn_executions', 'test_run_id'):
        if not index_exists('ix_multi_turn_executions_test_run_id'):
            op.create_index(
                'ix_multi_turn_executions_test_run_id',
                'multi_turn_executions',
                ['test_run_id']
            )

    if column_exists('voice_test_executions', 'test_run_id'):
        if not index_exists('ix_voice_test_executions_test_run_id'):
            op.create_index(
                'ix_voice_test_executions_test_run_id',
                'voice_test_executions',
                ['test_run_id']
            )

    # Recreate old foreign key constraints
    if column_exists('multi_turn_executions', 'test_run_id'):
        if not constraint_exists('multi_turn_executions_test_run_id_fkey', 'multi_turn_executions'):
            op.create_foreign_key(
                'multi_turn_executions_test_run_id_fkey',
                'multi_turn_executions',
                'test_runs',
                ['test_run_id'],
                ['id']
            )

    if column_exists('voice_test_executions', 'test_run_id'):
        if not constraint_exists('voice_test_executions_test_run_id_fkey', 'voice_test_executions'):
            op.create_foreign_key(
                'voice_test_executions_test_run_id_fkey',
                'voice_test_executions',
                'test_runs',
                ['test_run_id'],
                ['id']
            )
