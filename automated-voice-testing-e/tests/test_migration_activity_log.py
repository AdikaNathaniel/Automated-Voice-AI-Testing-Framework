"""
Tests for the activity_log Alembic migration.

Validates that the migration responsible for the activity log table:
- Exists within the alembic/versions directory
- Declares standard Alembic metadata
- Creates the activity_log table with expected columns, types, and defaults
- Sets up foreign keys to the users table
- Adds helpful indexes for frequent query patterns
- Removes the table and indexes on downgrade
"""

from pathlib import Path
import re

import pytest

PROJECT_ROOT = Path(__file__).parent.parent
ALEMBIC_VERSIONS = PROJECT_ROOT / "alembic" / "versions"


def find_migration_file(keyword: str) -> Path | None:
  """Locate a migration file by keyword within alembic/versions."""
  if not ALEMBIC_VERSIONS.exists():
    return None

  for file in ALEMBIC_VERSIONS.glob("*.py"):
    if keyword in file.name.lower() and file.name != "__pycache__":
      return file
  return None


ACTIVITY_LOG_MIGRATION = find_migration_file("activity_log")


class TestActivityLogMigrationPresence:
  """Ensure the migration file exists and is non-empty."""

  def test_versions_directory_exists(self):
    assert ALEMBIC_VERSIONS.exists(), "alembic/versions directory should exist"
    assert ALEMBIC_VERSIONS.is_dir(), "alembic/versions should be a directory"

  def test_migration_file_exists(self):
    assert ACTIVITY_LOG_MIGRATION is not None, "activity_log migration file should exist"
    assert ACTIVITY_LOG_MIGRATION.exists()
    assert ACTIVITY_LOG_MIGRATION.is_file()

  def test_migration_file_not_empty(self):
    if ACTIVITY_LOG_MIGRATION is None:
      pytest.skip("activity_log migration file missing")
    contents = ACTIVITY_LOG_MIGRATION.read_text(encoding="utf-8")
    assert contents.strip(), "Migration file should contain content"


class TestActivityLogMigrationStructure:
  """Check migration metadata and boilerplate."""

  def _contents(self) -> str:
    if ACTIVITY_LOG_MIGRATION is None:
      pytest.skip("activity_log migration file missing")
    return ACTIVITY_LOG_MIGRATION.read_text(encoding="utf-8")

  def test_imports_and_metadata(self):
    contents = self._contents()
    assert "from alembic import op" in contents, "Alembic operations helper should be imported"
    assert "import sqlalchemy as sa" in contents, "SQLAlchemy import expected"
    assert "from sqlalchemy.dialects import postgresql" in contents, "PostgreSQL dialect should be used"
    assert "revision" in contents, "revision identifier must be present"
    assert "down_revision" in contents, "down_revision identifier must be present"
    assert "def upgrade" in contents, "upgrade() function must exist"
    assert "def downgrade" in contents, "downgrade() function must exist"


class TestActivityLogTableDefinition:
  """Validate the table schema definition."""

  def _contents(self) -> str:
    if ACTIVITY_LOG_MIGRATION is None:
      pytest.skip("activity_log migration file missing")
    return ACTIVITY_LOG_MIGRATION.read_text(encoding="utf-8")

  def test_creates_activity_log_table(self):
    contents = self._contents()
    assert "create_table" in contents, "Migration should create a table"
    assert "activity_log" in contents, "Table name should be activity_log"

  def test_required_columns_present(self):
    contents = self._contents()
    required_columns = [
      "id",
      "user_id",
      "action_type",
      "resource_type",
      "resource_id",
      "action_description",
      "metadata",
      "ip_address",
      "created_at",
    ]
    for column in required_columns:
      tokens = (f"'{column}'", f'"{column}"')
      assert any(token in contents for token in tokens), f"Column {column} expected in migration"

  def test_id_primary_key_and_uuid(self):
    contents = self._contents()
    assert "postgresql.UUID(" in contents, "id should use UUID type"
    assert "primary_key=True" in contents, "id should be a primary key"

  def test_user_foreign_key(self):
    contents = self._contents()
    assert (
      "sa.ForeignKey(\"users.id\")" in contents or "sa.ForeignKey('users.id')" in contents
    ), "user_id should reference users.id"

  def test_metadata_and_ip_address_types(self):
    contents = self._contents()
    assert "postgresql.JSONB" in contents, "metadata column should use JSONB"
    assert "postgresql.INET" in contents, "ip_address column should use INET"

  def test_created_at_default(self):
    contents = self._contents()
    default_pattern = re.compile(r"created_at[\s\S]*server_default=sa\.text\(['\"]now\(\)['\"]\)")
    assert default_pattern.search(contents), "created_at should default to now()"

  def test_action_type_lengths(self):
    contents = self._contents()
    assert "sa.String(length=100)" in contents, "action_type should limit to 100 characters"
    assert "sa.String(length=100)" in contents, "resource_type should limit to 100 characters"

  def test_indexes_created(self):
    contents = self._contents()
    expected_indexes = [
      "ix_activity_log_user_id",
      "ix_activity_log_action_type",
      "ix_activity_log_resource_type",
      "ix_activity_log_created_at",
    ]
    for index in expected_indexes:
      assert index in contents, f"Expected index {index} to be created"


class TestActivityLogDowngrade:
  """Ensure downgrade removes table and indexes."""

  def test_downgrade_drops_indexes_and_table(self):
    if ACTIVITY_LOG_MIGRATION is None:
      pytest.skip("activity_log migration file missing")
    contents = ACTIVITY_LOG_MIGRATION.read_text(encoding="utf-8")
    assert "drop_index" in contents, "downgrade should drop indexes"
    assert "drop_table" in contents, "downgrade should drop the activity_log table"
    assert "activity_log" in contents, "downgrade should reference activity_log table"
