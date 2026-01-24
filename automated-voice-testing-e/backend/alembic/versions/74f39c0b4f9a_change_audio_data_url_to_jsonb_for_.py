"""change_audio_data_url_to_jsonb_for_language_variants

Revision ID: 74f39c0b4f9a
Revises: 7ef6f3f12fc5
Create Date: 2025-12-12 17:40:44.649042

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '74f39c0b4f9a'
down_revision: Union[str, Sequence[str], None] = '7ef6f3f12fc5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Change audio_data_url from String to JSONB to support multiple language variants.

    New structure:
    {
        "en-US": "http://localhost:9000/.../step_1_en-US.mp3",
        "es-ES": "http://localhost:9000/.../step_1_es-ES.mp3",
        "fr-FR": "http://localhost:9000/.../step_1_fr-FR.mp3"
    }
    """
    # Step 1: Add new JSONB column
    op.add_column(
        'step_executions',
        sa.Column(
            'audio_data_urls',
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="Map of language codes to S3 audio URLs"
        )
    )

    # Step 2: Migrate existing data (if any)
    # Convert single URL to JSONB with "en" as default language
    op.execute("""
        UPDATE step_executions
        SET audio_data_urls = jsonb_build_object('en', audio_data_url)
        WHERE audio_data_url IS NOT NULL
    """)

    # Step 3: Drop old column
    op.drop_column('step_executions', 'audio_data_url')


def downgrade() -> None:
    """Downgrade schema - convert JSONB back to single URL."""
    # Step 1: Add back the old column
    op.add_column(
        'step_executions',
        sa.Column(
            'audio_data_url',
            sa.String(500),
            nullable=True,
            comment="S3 URL to audio file"
        )
    )

    # Step 2: Migrate data back (take first URL from JSONB)
    op.execute("""
        UPDATE step_executions
        SET audio_data_url = (
            SELECT value
            FROM jsonb_each_text(audio_data_urls)
            LIMIT 1
        )
        WHERE audio_data_urls IS NOT NULL
    """)

    # Step 3: Drop new column
    op.drop_column('step_executions', 'audio_data_urls')
