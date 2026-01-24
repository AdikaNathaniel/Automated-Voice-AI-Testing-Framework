"""
Tests for the comments Alembic migration (TASK-365).

Ensures the comments migration:
- exists in alembic/versions with expected metadata
- defines the comments table with required columns and constraints
- creates indexes optimised for fetching entity threads
- cleans up all objects on downgrade
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
    lower_name = file.name.lower()
    if keyword in lower_name and file.name != "__pycache__":
      return file
  return None


COMMENTS_MIGRATION = find_migration_file("comments")


class TestCommentsMigrationPresence:
  """Basic assertions verifying the migration file exists."""

  def test_versions_directory_exists(self):
    assert ALEMBIC_VERSIONS.exists(), "alembic/versions directory must exist"
    assert ALEMBIC_VERSIONS.is_dir(), "alembic/versions should be a directory"

  def test_migration_file_exists(self):
    assert COMMENTS_MIGRATION is not None, "comments migration file should exist"
    assert COMMENTS_MIGRATION.exists()
    assert COMMENTS_MIGRATION.is_file()

  def test_migration_file_not_empty(self):
    if COMMENTS_MIGRATION is None:
      pytest.skip("comments migration missing")
    contents = COMMENTS_MIGRATION.read_text(encoding="utf-8")
    assert contents.strip(), "comments migration file should not be empty"


class TestCommentsMigrationStructure:
  """Ensure the migration declares standard Alembic metadata."""

  def _contents(self) -> str:
    if COMMENTS_MIGRATION is None:
      pytest.skip("comments migration missing")
    return COMMENTS_MIGRATION.read_text(encoding="utf-8")

  def test_imports_and_metadata(self):
    contents = self._contents()
    assert "from alembic import op" in contents, "Alembic operations module should be imported"
    assert "import sqlalchemy as sa" in contents, "SQLAlchemy import expected"
    assert "from sqlalchemy.dialects import postgresql" in contents, "PostgreSQL dialect should be used"
    assert "revision" in contents, "revision identifier must be defined"
    assert "down_revision" in contents, "down_revision must be defined"
    assert "def upgrade" in contents, "upgrade() function missing"
    assert "def downgrade" in contents, "downgrade() function missing"

  def test_down_revision_targets_activity_log(self):
    contents = self._contents()
    assert (
      "down_revision: Union[str, Sequence[str], None] = \"026_create_activity_log\"" in contents
      or "down_revision = '026_create_activity_log'" in contents
    ), "comments migration should follow the activity_log migration"


class TestCommentsTableDefinition:
  """Assert the comments table schema matches expectations."""

  def _contents(self) -> str:
    if COMMENTS_MIGRATION is None:
      pytest.skip("comments migration missing")
    return COMMENTS_MIGRATION.read_text(encoding="utf-8")

  def test_creates_comments_table(self):
    contents = self._contents()
    assert "create_table" in contents, "Migration should create a table"
    assert "comments" in contents, "comments table should be defined"

  def test_required_columns_exist(self):
    contents = self._contents()
    expected_columns = [
      "id",
      "entity_type",
      "entity_id",
      "parent_comment_id",
      "author_id",
      "content",
      "mentions",
      "is_edited",
      "created_at",
      "updated_at",
    ]
    for column in expected_columns:
      tokens = (f"'{column}'", f'"{column}"')
      assert any(token in contents for token in tokens), f"Expected column {column} in comments table"

  def test_column_types_and_constraints(self):
    contents = self._contents()
    assert "postgresql.UUID" in contents, "UUID columns should use PostgreSQL UUID type"
    assert "sa.String(length=50)" in contents, "entity_type should be constrained to 50 characters"
    assert "sa.Text()" in contents, "content should be stored as text"
    assert "postgresql.JSONB" in contents, "mentions metadata should use JSONB"
    assert (
      "sa.ForeignKey('users.id')" in contents or 'sa.ForeignKey("users.id")' in contents
    ), "author_id should reference users table"
    assert (
      "sa.ForeignKey('comments.id'" in contents or 'sa.ForeignKey("comments.id"' in contents
    ), "parent_comment_id should self-reference comments table"

  def test_defaults_applied(self):
    contents = self._contents()
    created_at_default = re.compile(r"created_at[\s\S]*server_default=sa\.text\(['\"]now\(\)['\"]\)")
    updated_at_default = re.compile(r"updated_at[\s\S]*server_default=sa\.text\(['\"]now\(\)['\"]\)")
    assert created_at_default.search(contents), "created_at should default to now()"
    assert updated_at_default.search(contents), "updated_at should default to now()"
    assert "is_edited" in contents and "server_default=sa.text('false')" in contents or "server_default=sa.text(\"false\")" in contents, (
      "is_edited should default to false"
    )

  def test_indexes_created(self):
    contents = self._contents()
    expected_indexes = [
      "ix_comments_entity",
      "ix_comments_parent_comment_id",
      "ix_comments_created_at",
    ]
    for index in expected_indexes:
      assert index in contents, f"Expected index {index} to be created"


class TestCommentsMigrationDowngrade:
  """Verify downgrade removes all created objects."""

  def test_drops_indexes_and_table(self):
    if COMMENTS_MIGRATION is None:
      pytest.skip("comments migration missing")
    contents = COMMENTS_MIGRATION.read_text(encoding="utf-8")
    assert "drop_index" in contents, "downgrade should drop indexes"
    assert "drop_table" in contents, "downgrade should drop comments table"
    assert "comments" in contents, "comments table should be referenced in downgrade"
