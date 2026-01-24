"""add regressions table for persistent regression tracking

Revision ID: a4b5c6d7e8f9
Revises: z3a4b5c6d7e8, f08a802b96db
Create Date: 2025-12-29 15:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a4b5c6d7e8f9'
down_revision: Union[str, Sequence[str], None] = ('z3a4b5c6d7e8', 'f08a802b96db')
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create regressions table for persistent tracking of detected regressions."""
    op.create_table(
        'regressions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False,
                  comment='Primary identifier for the regression record'),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True, index=True,
                  comment='Tenant identifier for multi-tenant scoping'),
        sa.Column('script_id', postgresql.UUID(as_uuid=True), nullable=False, index=True,
                  comment='Scenario script where regression was detected'),
        sa.Column('category', sa.String(length=50), nullable=False,
                  comment='Regression category: status, metric, or llm'),
        sa.Column('severity', sa.String(length=50), nullable=False, server_default='medium',
                  comment='Severity: low, medium, high, critical'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='active',
                  comment='Regression status: active, resolved, ignored, investigating'),
        sa.Column('baseline_version', sa.Integer(), nullable=True,
                  comment='Version of baseline used for detection'),
        sa.Column('detection_date', sa.DateTime(timezone=True), nullable=False,
                  comment='When the regression was first detected'),
        sa.Column('resolution_date', sa.DateTime(timezone=True), nullable=True,
                  comment='When the regression was resolved'),
        sa.Column('last_seen_date', sa.DateTime(timezone=True), nullable=False,
                  comment='Most recent occurrence of this regression'),
        sa.Column('occurrence_count', sa.Integer(), nullable=False, server_default='1',
                  comment='Number of times this regression has been detected'),
        sa.Column('details', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}',
                  comment='Regression details: baseline values, current values, deltas, etc.'),
        sa.Column('linked_defect_id', postgresql.UUID(as_uuid=True), nullable=True, index=True,
                  comment='Defect created to track this regression'),
        sa.Column('resolved_by', postgresql.UUID(as_uuid=True), nullable=True,
                  comment='User who resolved this regression'),
        sa.Column('resolution_note', sa.Text(), nullable=True,
                  comment='Note explaining how regression was resolved'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(),
                  comment='Record creation timestamp'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(),
                  comment='Record last update timestamp'),
    )

    # Add foreign key constraints
    op.create_foreign_key(
        'fk_regressions_script_id',
        'regressions', 'scenario_scripts',
        ['script_id'], ['id'],
        ondelete='CASCADE'
    )

    op.create_foreign_key(
        'fk_regressions_linked_defect_id',
        'regressions', 'defects',
        ['linked_defect_id'], ['id'],
        ondelete='SET NULL'
    )

    op.create_foreign_key(
        'fk_regressions_resolved_by',
        'regressions', 'users',
        ['resolved_by'], ['id'],
        ondelete='SET NULL'
    )

    # Create indexes for common queries
    op.create_index('ix_regressions_status', 'regressions', ['status'])
    op.create_index('ix_regressions_category', 'regressions', ['category'])
    op.create_index('ix_regressions_detection_date', 'regressions', ['detection_date'])
    op.create_index('ix_regressions_script_status', 'regressions', ['script_id', 'status'])


def downgrade() -> None:
    """Drop regressions table."""
    op.drop_index('ix_regressions_script_status', 'regressions')
    op.drop_index('ix_regressions_detection_date', 'regressions')
    op.drop_index('ix_regressions_category', 'regressions')
    op.drop_index('ix_regressions_status', 'regressions')
    op.drop_table('regressions')
