"""
Test suite for knowledge base service layer (TASK-354).

Validates the knowledge base service implementation including:
- File structure and documentation
- Required imports (AsyncSession, SQLAlchemy helpers, KnowledgeBase model)
- CRUD async functions (create, get, list, update, delete)
- Full-text search helper with PostgreSQL functions
- Type hints and return annotations
"""

from pathlib import Path

import pytest

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
SERVICES_DIR = PROJECT_ROOT / "backend" / "services"
KNOWLEDGE_BASE_SERVICE_FILE = SERVICES_DIR / "knowledge_base_service.py"


class TestKnowledgeBaseServiceFileExists:
    """Ensure the service module exists and is populated."""

    def test_services_directory_exists(self):
        assert SERVICES_DIR.exists(), "backend/services directory should exist"
        assert SERVICES_DIR.is_dir(), "backend/services should be a directory"

    def test_service_file_exists(self):
        assert KNOWLEDGE_BASE_SERVICE_FILE.exists(), "knowledge_base_service.py should exist"
        assert KNOWLEDGE_BASE_SERVICE_FILE.is_file(), "knowledge_base_service.py should be a file"

    def test_service_file_has_content(self):
        content = KNOWLEDGE_BASE_SERVICE_FILE.read_text(encoding="utf-8")
        assert content.strip(), "knowledge_base_service.py should not be empty"


@pytest.fixture(scope="module")
def service_source() -> str:
    """Return the knowledge base service source code."""
    return KNOWLEDGE_BASE_SERVICE_FILE.read_text(encoding="utf-8")


class TestKnowledgeBaseServiceImports:
    """Validate the module imports required dependencies."""

    def test_imports_asyncsession(self, service_source: str):
        assert "from sqlalchemy.ext.asyncio import AsyncSession" in service_source, "Should import AsyncSession"

    def test_imports_sqlalchemy_helpers(self, service_source: str):
        assert "from sqlalchemy import select" in service_source, "Should import select for queries"
        assert "func" in service_source, "Should reference SQLAlchemy func helper"
        assert "or_" in service_source, "Should import or_ for filter combinations"

    def test_imports_typing(self, service_source: str):
        assert "from typing import" in service_source, "Should use typing annotations"

    def test_imports_model(self, service_source: str):
        assert "from models.knowledge_base import KnowledgeBase" in service_source, "Should import KnowledgeBase model"


class TestKnowledgeBaseServiceDocumentation:
    """Check for module docstring describing responsibilities."""

    def test_has_module_docstring(self, service_source: str):
        assert service_source.lstrip().startswith('"""'), "Service should include a module docstring"


class TestCreateArticleFunction:
    """Verify create_article definition."""

    def test_create_article_function_exists(self, service_source: str):
        assert "def create_article" in service_source, "Should define create_article function"

    def test_create_article_is_async(self, service_source: str):
        assert "async def create_article" in service_source, "create_article should be async"

    def test_create_article_signature(self, service_source: str):
        assert "create_article(db: AsyncSession" in service_source, "create_article should accept AsyncSession"
        assert "data" in service_source, "create_article should accept data payload"
        assert "author_id" in service_source, "create_article should accept author_id"
        assert "-> KnowledgeBase" in service_source, "create_article should return KnowledgeBase"


class TestGetArticleFunction:
    """Verify get_article definition."""

    def test_get_article_exists(self, service_source: str):
        assert "def get_article" in service_source, "Should define get_article function"

    def test_get_article_is_async(self, service_source: str):
        assert "async def get_article" in service_source, "get_article should be async"

    def test_get_article_signature(self, service_source: str):
        assert "get_article(db: AsyncSession" in service_source, "get_article should accept AsyncSession"
        assert "article_id" in service_source, "get_article should accept article_id parameter"


class TestListArticlesFunction:
    """Verify list_articles definition."""

    def test_list_articles_exists(self, service_source: str):
        assert "def list_articles" in service_source, "Should define list_articles function"

    def test_list_articles_is_async(self, service_source: str):
        assert "async def list_articles" in service_source, "list_articles should be async"

    def test_list_articles_signature(self, service_source: str):
        assert "list_articles(db: AsyncSession" in service_source, "list_articles should accept AsyncSession"
        assert "filters" in service_source, "list_articles should accept filters argument"
        assert "pagination" in service_source, "list_articles should accept pagination argument"
        assert "-> tuple[list[KnowledgeBase]," in service_source or "Tuple[List[KnowledgeBase]," in service_source, (
            "list_articles should return articles and metadata"
        )


class TestUpdateArticleFunction:
    """Verify update_article definition."""

    def test_update_article_exists(self, service_source: str):
        assert "def update_article" in service_source, "Should define update_article function"

    def test_update_article_is_async(self, service_source: str):
        assert "async def update_article" in service_source, "update_article should be async"

    def test_update_article_signature(self, service_source: str):
        assert "update_article(db: AsyncSession" in service_source, "update_article should accept AsyncSession"
        assert "article_id" in service_source, "update_article should accept article_id"
        assert "data" in service_source, "update_article should accept data payload"
        assert "-> KnowledgeBase" in service_source, "update_article should return KnowledgeBase"


class TestDeleteArticleFunction:
    """Verify delete_article definition."""

    def test_delete_article_exists(self, service_source: str):
        assert "def delete_article" in service_source, "Should define delete_article function"

    def test_delete_article_is_async(self, service_source: str):
        assert "async def delete_article" in service_source, "delete_article should be async"

    def test_delete_article_signature(self, service_source: str):
        assert "delete_article(db: AsyncSession" in service_source, "delete_article should accept AsyncSession"
        assert "article_id" in service_source, "delete_article should accept article_id"
        assert "-> bool" in service_source, "delete_article should return bool"


class TestSearchArticlesFunction:
    """Verify full-text search helper."""

    def test_search_articles_exists(self, service_source: str):
        assert "def search_articles" in service_source, "Should define search_articles function"

    def test_search_articles_is_async(self, service_source: str):
        assert "async def search_articles" in service_source, "search_articles should be async"

    def test_search_articles_signature(self, service_source: str):
        assert "search_articles(db: AsyncSession" in service_source, "search_articles should accept AsyncSession"
        assert "search_query" in service_source, "search_articles should accept search_query"
        assert "pagination" in service_source, "search_articles should accept pagination argument"

    def test_search_articles_uses_full_text(self, service_source: str):
        assert "to_tsvector" in service_source, "search_articles should leverage PostgreSQL full-text search"
        assert "websearch_to_tsquery" in service_source or "plainto_tsquery" in service_source, (
            "search_articles should build a tsquery"
        )


class TestHelperUtilities:
    """Ensure helper utilities follow conventions."""

    def test_includes_pagination_defaults(self, service_source: str):
        assert "DEFAULT_PAGE_SIZE" in service_source, "Service should define pagination defaults"

    def test_returns_metadata(self, service_source: str):
        assert "return articles, {" in service_source or "return articles, {" in service_source, (
            "list/search functions should return metadata dictionaries"
        )
