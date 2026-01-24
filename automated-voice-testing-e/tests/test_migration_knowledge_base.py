"""
Test suite for knowledge_base table migration.

Ensures the Alembic migration responsible for knowledge base articles:
- Exists within the versions directory
- Declares revision metadata and Alembic imports
- Creates the knowledge_base table with expected columns
- Applies appropriate data types, defaults, and constraints
- References the users table for author relationships
- Provides downgrade coverage for table removal
"""

from pathlib import Path
import pytest
import re

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
ALEMBIC_VERSIONS = PROJECT_ROOT / "alembic" / "versions"


def find_migration_file(keyword: str) -> Path | None:
    """Locate the migration file that contains the provided keyword."""
    if not ALEMBIC_VERSIONS.exists():
        return None

    for file in ALEMBIC_VERSIONS.glob("*.py"):
        if keyword in file.name.lower() and file.name != "__pycache__":
            return file
    return None


KNOWLEDGE_BASE_MIGRATION_FILE = find_migration_file("knowledge_base")


class TestKnowledgeBaseMigrationFile:
    """Validate basic migration file characteristics."""

    def test_versions_directory_exists(self):
        assert ALEMBIC_VERSIONS.exists(), "alembic/versions directory should exist"
        assert ALEMBIC_VERSIONS.is_dir(), "alembic/versions should be a directory"

    def test_migration_file_exists(self):
        assert (
            KNOWLEDGE_BASE_MIGRATION_FILE is not None
        ), "knowledge_base migration file should exist"
        assert KNOWLEDGE_BASE_MIGRATION_FILE.exists(), "Migration file must be present"
        assert KNOWLEDGE_BASE_MIGRATION_FILE.is_file(), "Migration path should be a file"

    def test_migration_file_has_content(self):
        if KNOWLEDGE_BASE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        contents = KNOWLEDGE_BASE_MIGRATION_FILE.read_text(encoding="utf-8")
        assert contents.strip(), "Migration file should not be empty"


class TestKnowledgeBaseMigrationStructure:
    """Ensure migration boilerplate and metadata are present."""

    def test_imports_and_metadata(self):
        if KNOWLEDGE_BASE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        contents = KNOWLEDGE_BASE_MIGRATION_FILE.read_text(encoding="utf-8")
        assert "from alembic import op" in contents, "Should import Alembic operations helper"
        assert (
            "import sqlalchemy as sa" in contents
        ), "Should import SQLAlchemy for column definitions"
        assert "revision" in contents, "Migration should declare a revision identifier"
        assert "down_revision" in contents, "Migration should declare down_revision"
        assert "def upgrade" in contents, "Migration must define upgrade()"
        assert "def downgrade" in contents, "Migration must define downgrade()"


class TestKnowledgeBaseTableDefinition:
    """Validate the table schema for knowledge base articles."""

    def _read_contents(self) -> str:
        if KNOWLEDGE_BASE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        return KNOWLEDGE_BASE_MIGRATION_FILE.read_text(encoding="utf-8")

    def test_creates_knowledge_base_table(self):
        contents = self._read_contents()
        assert "create_table" in contents, "Migration should create a table"
        assert "knowledge_base" in contents, "Migration should create knowledge_base table"

    def test_table_includes_required_columns(self):
        contents = self._read_contents()
        required_columns = [
            "id",
            "title",
            "category",
            "content",
            "content_format",
            "author_id",
            "is_published",
            "views",
            "created_at",
            "updated_at",
        ]
        for column in required_columns:
            tokens = (f"'{column}'", f'"{column}"')
            assert any(token in contents for token in tokens), f"Expected column {column} in migration"

    def test_id_is_uuid_primary_key(self):
        contents = self._read_contents()
        assert "postgresql.UUID" in contents or "UUID" in contents, "id should use UUID type"
        assert "primary_key=True" in contents, "id should be a primary key"

    def test_title_column_constraints(self):
        contents = self._read_contents()
        assert "title" in contents, "Should define title column"
        assert "sa.String(length=255)" in contents, "title should limit to 255 characters"
        assert "nullable=False" in contents, "title should be required"

    def test_author_relationship(self):
        contents = self._read_contents()
        assert (
            "sa.ForeignKey(\"users.id\")" in contents or "sa.ForeignKey('users.id')" in contents
        ), "author_id should reference users table"

    def test_boolean_and_numeric_defaults(self):
        contents = self._read_contents()
        bool_default_pattern = re.compile(r"is_published[\s\S]*server_default=sa\.text\(['\"]?false['\"]?\)")
        views_default_pattern = re.compile(r"views[\s\S]*server_default=sa\.text\(['\"]?0['\"]?\)")
        assert bool_default_pattern.search(contents), "is_published should default to false"
        assert views_default_pattern.search(contents), "views should default to 0"

    def test_timestamp_defaults(self):
        contents = self._read_contents()
        assert contents.count("server_default=sa.text(\"now()\")") >= 2 or contents.count(
            "server_default=sa.text('now()')"
        ) >= 2, "created_at and updated_at should default to now()"


class TestKnowledgeBaseDowngrade:
    """Confirm downgrade removes the knowledge_base table."""

    def test_downgrade_drops_table(self):
        if KNOWLEDGE_BASE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        contents = KNOWLEDGE_BASE_MIGRATION_FILE.read_text(encoding="utf-8")
        assert "drop_table" in contents, "downgrade() should drop the knowledge_base table"
        assert (
            "knowledge_base" in contents
        ), "downgrade() should reference knowledge_base table"
