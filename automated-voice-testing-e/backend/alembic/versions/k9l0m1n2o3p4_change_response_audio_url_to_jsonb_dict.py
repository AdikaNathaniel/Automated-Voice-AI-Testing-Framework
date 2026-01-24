"""change_response_audio_url_to_jsonb_dict

Revision ID: k9l0m1n2o3p4
Revises: j8k9l0m1n2o3
Create Date: 2024-12-22

Changes response_audio_url from Text to JSONB dict (response_audio_urls)
to support multiple language variants, matching the structure of audio_data_urls.

This allows each language variant to have its own response audio URL:
- Before: response_audio_url = "http://s3.../audio.wav"  (only primary language)
- After: response_audio_urls = {"en-US": "http://...", "es-ES": "http://...", ...}
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'k9l0m1n2o3p4'
down_revision = 'j8k9l0m1n2o3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Change response_audio_url to response_audio_urls (JSONB dict).

    Migration strategy:
    1. Add new response_audio_urls column as JSONB
    2. Migrate existing data (if any exists, assume it's en-US)
    3. Drop old response_audio_url column
    """
    # Add new JSONB column
    op.add_column(
        'step_executions',
        sa.Column(
            'response_audio_urls',
            postgresql.JSONB().with_variant(sa.JSON(), "sqlite"),
            nullable=True,
            comment='Map of language codes to S3 response audio URLs (e.g., {"en-US": "http://...", "es-ES": "http://..."})'
        )
    )

    # Migrate existing data: wrap single URL in dict with 'en-US' key
    # Using raw SQL for PostgreSQL-specific operations
    op.execute("""
        UPDATE step_executions
        SET response_audio_urls = jsonb_build_object('en-US', response_audio_url)
        WHERE response_audio_url IS NOT NULL
    """)

    # Drop old column
    op.drop_column('step_executions', 'response_audio_url')


def downgrade() -> None:
    """
    Revert response_audio_urls back to response_audio_url (Text).

    Note: This will lose multi-language data, keeping only the first URL found.
    """
    # Add back the old Text column
    op.add_column(
        'step_executions',
        sa.Column(
            'response_audio_url',
            sa.Text(),
            nullable=True,
            comment='S3/MinIO URL for response audio from Houndify TTS'
        )
    )

    # Migrate data back: extract first URL from the JSONB dict
    # This will lose multi-language variants
    op.execute("""
        UPDATE step_executions
        SET response_audio_url = (
            SELECT value::text
            FROM jsonb_each_text(response_audio_urls)
            LIMIT 1
        )
        WHERE response_audio_urls IS NOT NULL
    """)

    # Drop the JSONB column
    op.drop_column('step_executions', 'response_audio_urls')
