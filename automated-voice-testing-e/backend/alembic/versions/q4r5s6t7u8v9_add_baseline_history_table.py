"""Add baseline_history table for audit trail.

Revision ID: q4r5s6t7u8v9
Revises: p3k1b2a3c4d5
Create Date: 2025-12-26

Creates baseline_history table to store historical versions of baselines
when they are updated. This provides an audit trail for baseline changes.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = 'q4r5s6t7u8v9'
down_revision = 'p3k1b2a3c4d5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create baseline_history table
    op.create_table(
        'baseline_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column('baseline_id', postgresql.UUID(as_uuid=True), nullable=False,
                  comment='Reference to the parent baseline record'),
        sa.Column('script_id', sa.String(36), nullable=False,
                  comment='Scenario script ID (denormalized for query efficiency)'),
        sa.Column('version', sa.Integer, nullable=False,
                  comment='Version number at time of archival'),
        sa.Column('result_status', sa.String(32), nullable=False,
                  comment='Status at this version'),
        sa.Column('metrics', sa.JSON, nullable=False, server_default='{}',
                  comment='Metrics at this version'),
        sa.Column('approved_by', sa.String(36), nullable=True,
                  comment='User who approved this version'),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True,
                  comment='When this version was approved'),
        sa.Column('note', sa.Text, nullable=True,
                  comment='Note for this version'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now(), onupdate=sa.func.now()),
        # Foreign key to regression_baselines
        sa.ForeignKeyConstraint(
            ['baseline_id'],
            ['regression_baselines.id'],
            name='fk_baseline_history_baseline_id',
            ondelete='CASCADE'
        ),
        # Unique constraint on baseline_id + version
        sa.UniqueConstraint('baseline_id', 'version', name='uq_baseline_history_version'),
    )

    # Create indexes
    op.create_index('ix_baseline_history_baseline_id', 'baseline_history', ['baseline_id'])
    op.create_index('ix_baseline_history_script_id', 'baseline_history', ['script_id'])


def downgrade() -> None:
    op.drop_index('ix_baseline_history_script_id', table_name='baseline_history')
    op.drop_index('ix_baseline_history_baseline_id', table_name='baseline_history')
    op.drop_table('baseline_history')
