"""
Tests for knowledge base API schemas (TASK-355).

Ensures the schema module provides request/response models used by the routes:
- KnowledgeBaseCreateRequest
- KnowledgeBaseUpdateRequest
- KnowledgeBaseResponse
- KnowledgeBaseListResponse
"""

from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).parent.parent
SCHEMAS_DIR = PROJECT_ROOT / "backend" / "api" / "schemas"
KNOWLEDGE_BASE_SCHEMA_FILE = SCHEMAS_DIR / "knowledge_base.py"


class TestKnowledgeBaseSchemaFile:
    """Ensure the schema file exists and is populated."""

    def test_schema_directory_exists(self):
        assert SCHEMAS_DIR.exists(), "backend/api/schemas directory should exist"
        assert SCHEMAS_DIR.is_dir(), "backend/api/schemas should be a directory"

    def test_schema_file_exists(self):
        assert KNOWLEDGE_BASE_SCHEMA_FILE.exists(), "knowledge_base.py schema file should exist"
        assert KNOWLEDGE_BASE_SCHEMA_FILE.is_file(), "knowledge_base.py should be a file"

    def test_schema_file_not_empty(self):
        if not KNOWLEDGE_BASE_SCHEMA_FILE.exists():
            pytest.fail("knowledge_base.py schema file must exist before reading content")
        content = KNOWLEDGE_BASE_SCHEMA_FILE.read_text(encoding="utf-8")
        assert content.strip(), "knowledge_base.py schema file should not be empty"


@pytest.fixture(scope="module")
def schema_source() -> str:
    """Provide the schema source for tests."""
    if not KNOWLEDGE_BASE_SCHEMA_FILE.exists():
        pytest.fail("knowledge_base.py schema file must exist for content validation")
    return KNOWLEDGE_BASE_SCHEMA_FILE.read_text(encoding="utf-8")


class TestKnowledgeBaseSchemaDefinitions:
    """Verify required schema classes are defined."""

    def test_defines_create_request(self, schema_source: str):
        assert "class KnowledgeBaseCreateRequest" in schema_source, \
            "Schema module should define KnowledgeBaseCreateRequest"

    def test_defines_update_request(self, schema_source: str):
        assert "class KnowledgeBaseUpdateRequest" in schema_source, \
            "Schema module should define KnowledgeBaseUpdateRequest"

    def test_defines_response_model(self, schema_source: str):
        assert "class KnowledgeBaseResponse" in schema_source, \
            "Schema module should define KnowledgeBaseResponse model"

    def test_defines_list_response(self, schema_source: str):
        assert "class KnowledgeBaseListResponse" in schema_source, \
            "Schema module should define KnowledgeBaseListResponse model"

    def test_uses_pydantic_base_model(self, schema_source: str):
        assert "from pydantic import BaseModel" in schema_source, \
            "Schema module should import BaseModel from pydantic"
