"""Add cicd_runs table

Revision ID: t7u8v9w0x1y2
Revises: s6t7u8v9w0x1
Create Date: 2025-12-26

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 't7u8v9w0x1y2'
down_revision = 's6t7u8v9w0x1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'cicd_runs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('provider', sa.String(50), nullable=False),
        sa.Column('pipeline_name', sa.String(255), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('branch', sa.String(255), nullable=True),
        sa.Column('commit_sha', sa.String(40), nullable=True),
        sa.Column('commit_url', sa.String(500), nullable=True),
        sa.Column('triggered_by', sa.String(255), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('total_tests', sa.Integer(), server_default='0'),
        sa.Column('passed_tests', sa.Integer(), server_default='0'),
        sa.Column('failed_tests', sa.Integer(), server_default='0'),
        sa.Column('raw_payload', sa.Text(), nullable=True),
        sa.Column('event_type', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['tenant_id'], ['users.id'], ondelete='CASCADE'),
    )

    # Create indexes for common queries
    op.create_index('ix_cicd_runs_tenant_id', 'cicd_runs', ['tenant_id'])
    op.create_index('ix_cicd_runs_provider', 'cicd_runs', ['provider'])
    op.create_index('ix_cicd_runs_status', 'cicd_runs', ['status'])
    op.create_index('ix_cicd_runs_created_at', 'cicd_runs', ['created_at'])


def downgrade() -> None:
    op.drop_index('ix_cicd_runs_created_at', table_name='cicd_runs')
    op.drop_index('ix_cicd_runs_status', table_name='cicd_runs')
    op.drop_index('ix_cicd_runs_provider', table_name='cicd_runs')
    op.drop_index('ix_cicd_runs_tenant_id', table_name='cicd_runs')
    op.drop_table('cicd_runs')
