"""
Comment service specification tests (TASK-366).

Validates that the comment service module:
- Exists with documentation and expected imports
- Defines supported entity types for comments (test_case, defect, validation)
- Exposes a CommentService class with CRUD async helpers
- Provides convenience module-level functions delegating to the singleton
"""

from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent
SERVICES_DIR = PROJECT_ROOT / "backend" / "services"
COMMENT_SERVICE_FILE = SERVICES_DIR / "comment_service.py"


class TestCommentServicePresence:
  """Ensure the comment service module exists and is non-empty."""

  def test_services_directory_exists(self):
    assert SERVICES_DIR.exists(), "backend/services directory should exist"
    assert SERVICES_DIR.is_dir(), "backend/services should be a directory"

  def test_service_file_exists(self):
    assert COMMENT_SERVICE_FILE.exists(), "comment_service.py should exist"
    assert COMMENT_SERVICE_FILE.is_file(), "comment_service.py should be a file"

  def test_service_file_has_content(self):
    contents = COMMENT_SERVICE_FILE.read_text(encoding="utf-8")
    assert contents.strip(), "comment_service.py should not be empty"


@pytest.fixture(scope="module")
def comment_service_source() -> str:
  """Return the comment service source code."""
  return COMMENT_SERVICE_FILE.read_text(encoding="utf-8")


class TestCommentServiceStructure:
  """Assert module-level metadata and imports."""

  def test_has_module_docstring(self, comment_service_source: str):
    assert comment_service_source.lstrip().startswith('"""'), "Service module should begin with a docstring"

  def test_imports_asyncsession(self, comment_service_source: str):
    assert "from sqlalchemy.ext.asyncio import AsyncSession" in comment_service_source, "AsyncSession import required"

  def test_imports_sqlalchemy_helpers(self, comment_service_source: str):
    assert "from sqlalchemy import select" in comment_service_source, "select helper should be imported"
    assert "from sqlalchemy import delete" in comment_service_source, "delete helper should be imported"
    assert "selectinload" in comment_service_source, "selectinload should be imported for eager loading replies"

  def test_imports_typing_and_uuid(self, comment_service_source: str):
    assert "from typing import" in comment_service_source, "typing utilities should be imported"
    assert "from uuid import UUID" in comment_service_source, "UUID type should be imported"

  def test_imports_comment_model(self, comment_service_source: str):
    assert "from models.comment import Comment" in comment_service_source, "Service should import Comment model"

  def test_defines_supported_entity_types(self, comment_service_source: str):
    assert "SUPPORTED_ENTITY_TYPES" in comment_service_source, "Supported entity types constant expected"
    for entity_type in ("'test_case'", "'defect'", "'validation'"):
      assert entity_type in comment_service_source, f"{entity_type} should be included in SUPPORTED_ENTITY_TYPES"


class TestCommentServiceClass:
  """Validate the CommentService class definition and API surface."""

  def test_comment_service_class_exists(self, comment_service_source: str):
    assert "class CommentService" in comment_service_source, "CommentService class should be defined"

  def test_create_comment_signature(self, comment_service_source: str):
    assert "async def create_comment" in comment_service_source, "create_comment coroutine expected"
    assert "create_comment(self, *, db: AsyncSession" in comment_service_source, "create_comment should accept AsyncSession via keyword-only arguments"
    assert "entity_type: str" in comment_service_source, "create_comment should require entity_type"
    assert "entity_id: UUID" in comment_service_source, "create_comment should require entity_id"
    assert "author_id: UUID" in comment_service_source, "create_comment should require author_id"
    assert "content: str" in comment_service_source, "create_comment should accept content"
    assert "mentions: " in comment_service_source, "create_comment should accept mentions payload"
    assert "-> Comment" in comment_service_source, "create_comment should return Comment"

  def test_reply_to_comment_signature(self, comment_service_source: str):
    assert "async def reply_to_comment" in comment_service_source, "reply_to_comment coroutine expected"
    assert "parent_comment_id: UUID" in comment_service_source, "reply_to_comment should include parent_comment_id"
    assert "-> Comment" in comment_service_source, "reply_to_comment should return Comment"

  def test_list_comments_signature(self, comment_service_source: str):
    assert "async def list_comments" in comment_service_source, "list_comments coroutine expected"
    assert "list_comments(self, *, db: AsyncSession" in comment_service_source, "list_comments should accept AsyncSession"
    assert "entity_type: str" in comment_service_source, "list_comments should filter by entity_type"
    assert "entity_id: UUID" in comment_service_source, "list_comments should filter by entity_id"
    assert "-> list[Comment]" in comment_service_source or "-> List[Comment]" in comment_service_source, (
      "list_comments should return a list of Comment instances"
    )

  def test_update_comment_signature(self, comment_service_source: str):
    assert "async def update_comment" in comment_service_source, "update_comment coroutine expected"
    assert "comment_id: UUID" in comment_service_source, "update_comment should accept comment_id"
    assert "editor_id: UUID" in comment_service_source, "update_comment should include editor_id parameter"
    assert "-> Comment" in comment_service_source, "update_comment should return Comment"

  def test_delete_comment_signature(self, comment_service_source: str):
    assert "async def delete_comment" in comment_service_source, "delete_comment coroutine expected"
    assert "comment_id: UUID" in comment_service_source, "delete_comment should accept comment_id"
    assert "requester_id: UUID" in comment_service_source, "delete_comment should include requester_id parameter"
    assert "-> bool" in comment_service_source, "delete_comment should return bool"

  def test_normalize_mentions_helper_exists(self, comment_service_source: str):
    assert "def _normalise_mentions(" in comment_service_source or "def _normalize_mentions(" in comment_service_source, (
      "Service should expose a helper to normalise mentions payloads"
    )

  def test_includes_singleton_export(self, comment_service_source: str):
    assert "comment_service = CommentService()" in comment_service_source, "comment_service singleton should be exposed"

  def test_module_level_shortcuts(self, comment_service_source: str):
    for helper in ("create_comment", "reply_to_comment", "list_comments", "update_comment", "delete_comment"):
      assert f"async def {helper}(" in comment_service_source, f"{helper} convenience function expected"
      assert f"return await comment_service.{helper}" in comment_service_source, f"{helper} should delegate to singleton"
