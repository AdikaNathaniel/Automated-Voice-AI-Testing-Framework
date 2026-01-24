"""Add tenant_id to models for multi-tenancy support.

Revision ID: r5s6t7u8v9w0
Revises: q4r5s6t7u8v9
Create Date: 2025-12-26

Adds tenant_id foreign key to the following tables:
- edge_cases
- knowledge_base
- configurations (with unique constraint on tenant_id + config_key)
- expected_outcomes (with unique constraint on tenant_id + outcome_code)
- multi_turn_executions
- human_validations
- configuration_history
- escalation_policies

This enables proper multi-tenant data isolation.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = 'r5s6t7u8v9w0'
down_revision = '782d67f47f3d'  # Comes after notification_configs migration
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add tenant_id columns and update constraints."""

    # Get database connection for data migration
    connection = op.get_bind()

    # Find the first user to use as default tenant for existing data
    # This is a migration helper - in production, you'd want to properly
    # assign tenants before running this migration
    result = connection.execute(
        sa.text("SELECT id FROM users LIMIT 1")
    ).fetchone()
    default_tenant_id = result[0] if result else None

    # List of tables to add tenant_id
    tables_simple = [
        'edge_cases',
        'knowledge_base',
        'multi_turn_executions',
        'human_validations',
        'configuration_history',
        'escalation_policies',
    ]

    # Add tenant_id to simple tables (no constraint changes needed)
    for table in tables_simple:
        # Add column as nullable first
        op.add_column(
            table,
            sa.Column(
                'tenant_id',
                postgresql.UUID(as_uuid=True),
                nullable=True,
                comment='Tenant (organization or user) that owns this record'
            )
        )

        # Set default tenant for existing rows
        if default_tenant_id:
            connection.execute(
                sa.text(f"UPDATE {table} SET tenant_id = :tenant_id WHERE tenant_id IS NULL"),
                {'tenant_id': default_tenant_id}
            )

        # Make column non-nullable
        op.alter_column(table, 'tenant_id', nullable=False)

        # Add foreign key and index
        op.create_foreign_key(
            f'fk_{table}_tenant_id',
            table,
            'users',
            ['tenant_id'],
            ['id'],
            ondelete='CASCADE'
        )
        op.create_index(f'ix_{table}_tenant_id', table, ['tenant_id'])

    # Handle configurations table - needs unique constraint update
    # Drop the existing unique constraint on config_key (created by initial migration as UniqueConstraint)
    # PostgreSQL auto-generates constraint name as {table}_{column}_key
    op.drop_constraint('configurations_config_key_key', 'configurations', type_='unique')

    # Add tenant_id column
    op.add_column(
        'configurations',
        sa.Column(
            'tenant_id',
            postgresql.UUID(as_uuid=True),
            nullable=True,
            comment='Tenant (organization or user) that owns this configuration'
        )
    )

    # Set default tenant for existing rows
    if default_tenant_id:
        connection.execute(
            sa.text("UPDATE configurations SET tenant_id = :tenant_id WHERE tenant_id IS NULL"),
            {'tenant_id': default_tenant_id}
        )

    # Make column non-nullable
    op.alter_column('configurations', 'tenant_id', nullable=False)

    # Add foreign key and index
    op.create_foreign_key(
        'fk_configurations_tenant_id',
        'configurations',
        'users',
        ['tenant_id'],
        ['id'],
        ondelete='CASCADE'
    )
    op.create_index('ix_configurations_tenant_id', 'configurations', ['tenant_id'])

    # Add new unique constraint on (tenant_id, config_key)
    op.create_unique_constraint(
        'uq_configuration_tenant_key',
        'configurations',
        ['tenant_id', 'config_key']
    )

    # Handle expected_outcomes table - needs unique index update
    # Drop the existing unique index on outcome_code (created by initial migration as index, not constraint)
    op.drop_index('ix_expected_outcomes_outcome_code', table_name='expected_outcomes')

    # Add tenant_id column
    op.add_column(
        'expected_outcomes',
        sa.Column(
            'tenant_id',
            postgresql.UUID(as_uuid=True),
            nullable=True,
            comment='Tenant (organization or user) that owns this expected outcome'
        )
    )

    # Set default tenant for existing rows
    if default_tenant_id:
        connection.execute(
            sa.text("UPDATE expected_outcomes SET tenant_id = :tenant_id WHERE tenant_id IS NULL"),
            {'tenant_id': default_tenant_id}
        )

    # Make column non-nullable
    op.alter_column('expected_outcomes', 'tenant_id', nullable=False)

    # Add foreign key and index
    op.create_foreign_key(
        'fk_expected_outcomes_tenant_id',
        'expected_outcomes',
        'users',
        ['tenant_id'],
        ['id'],
        ondelete='CASCADE'
    )
    op.create_index('ix_expected_outcomes_tenant_id', 'expected_outcomes', ['tenant_id'])

    # Add new unique constraint on (tenant_id, outcome_code)
    op.create_unique_constraint(
        'uq_expected_outcome_tenant_code',
        'expected_outcomes',
        ['tenant_id', 'outcome_code']
    )


def downgrade() -> None:
    """Remove tenant_id columns and restore original constraints."""

    # Restore expected_outcomes original unique index
    op.drop_constraint('uq_expected_outcome_tenant_code', 'expected_outcomes', type_='unique')
    op.drop_index('ix_expected_outcomes_tenant_id', table_name='expected_outcomes')
    op.drop_constraint('fk_expected_outcomes_tenant_id', 'expected_outcomes', type_='foreignkey')
    op.drop_column('expected_outcomes', 'tenant_id')
    op.create_index(
        'ix_expected_outcomes_outcome_code',
        'expected_outcomes',
        ['outcome_code'],
        unique=True
    )

    # Restore configurations original unique constraint
    op.drop_constraint('uq_configuration_tenant_key', 'configurations', type_='unique')
    op.drop_index('ix_configurations_tenant_id', table_name='configurations')
    op.drop_constraint('fk_configurations_tenant_id', 'configurations', type_='foreignkey')
    op.drop_column('configurations', 'tenant_id')
    op.create_unique_constraint(
        'configurations_config_key_key',
        'configurations',
        ['config_key']
    )

    # Remove tenant_id from simple tables
    tables_simple = [
        'escalation_policies',
        'configuration_history',
        'human_validations',
        'multi_turn_executions',
        'knowledge_base',
        'edge_cases',
    ]

    for table in tables_simple:
        op.drop_index(f'ix_{table}_tenant_id', table_name=table)
        op.drop_constraint(f'fk_{table}_tenant_id', table, type_='foreignkey')
        op.drop_column(table, 'tenant_id')
