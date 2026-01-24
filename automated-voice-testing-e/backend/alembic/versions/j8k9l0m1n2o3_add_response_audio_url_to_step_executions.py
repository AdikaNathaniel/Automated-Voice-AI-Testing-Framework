"""add_response_audio_url_to_step_executions

Revision ID: j8k9l0m1n2o3
Revises: i7j8k9l0m1n2
Create Date: 2024-12-22

Adds response_audio_url column to step_executions table to store
the URL of the TTS audio response from Houndify.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'j8k9l0m1n2o3'
down_revision = 'i7j8k9l0m1n2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add response_audio_url column to step_executions table."""
    op.add_column(
        'step_executions',
        sa.Column(
            'response_audio_url',
            sa.Text(),
            nullable=True,
            comment='S3/MinIO URL for response audio from Houndify TTS'
        )
    )


def downgrade() -> None:
    """Remove response_audio_url column from step_executions table."""
    op.drop_column('step_executions', 'response_audio_url')
