"""
Test suite for the KnowledgeBase SQLAlchemy model.

Validates that the model implementation:
- Exists with non-empty content
- Imports Base, BaseModel, and SQLAlchemy primitives
- Defines KnowledgeBase class inheriting from Base & BaseModel
- Declares expected columns and constraints mirroring the migration schema
- Configures sensible defaults (content format, published flag, view counter)
- Establishes relationship to the User author
- Provides helpful dunder helpers (__repr__, to_dict)
"""

from pathlib import Path
import re

import pytest

PROJECT_ROOT = Path(__file__).parent.parent
MODELS_DIR = PROJECT_ROOT / "backend" / "models"
KNOWLEDGE_BASE_MODEL_FILE = MODELS_DIR / "knowledge_base.py"


class TestKnowledgeBaseModelFile:
    """Ensure the KnowledgeBase model module exists and is populated."""

    def test_models_directory_exists(self):
        assert MODELS_DIR.exists(), "backend/models directory should exist"
        assert MODELS_DIR.is_dir(), "backend/models should be a directory"

    def test_model_file_exists(self):
        assert KNOWLEDGE_BASE_MODEL_FILE.exists(), "knowledge_base.py should exist"
        assert KNOWLEDGE_BASE_MODEL_FILE.is_file(), "knowledge_base.py should be a file"

    def test_model_file_has_content(self):
        content = KNOWLEDGE_BASE_MODEL_FILE.read_text(encoding="utf-8")
        assert content.strip(), "knowledge_base.py should not be empty"


@pytest.fixture(scope="module")
def model_source() -> str:
    """Load the KnowledgeBase model source once for downstream structural tests."""
    return KNOWLEDGE_BASE_MODEL_FILE.read_text(encoding="utf-8")


class TestKnowledgeBaseModelImports:
    """Validate import statements meet project conventions."""

    def test_imports_base_and_basemodel(self, model_source: str):
        assert (
            "from models.base import Base, BaseModel" in model_source
            or "from models.base import Base, BaseModel" in model_source
        ), "Model should import Base and BaseModel"

    def test_imports_sqlalchemy(self, model_source: str):
        assert "import sqlalchemy as sa" in model_source, "Model should import SQLAlchemy as sa"

    def test_imports_relationship(self, model_source: str):
        assert "from sqlalchemy.orm import relationship" in model_source, "Model should import relationship helper"


class TestKnowledgeBaseModelClassDefinition:
    """Verify the KnowledgeBase class structure."""

    def test_class_is_declared(self, model_source: str):
        assert "class KnowledgeBase" in model_source, "KnowledgeBase class should be defined"

    def test_inherits_from_base_and_basemodel(self, model_source: str):
        pattern = re.compile(r"class KnowledgeBase\((BaseModel, Base|Base, BaseModel)\)")
        assert pattern.search(model_source), "KnowledgeBase should inherit from Base and BaseModel"

    def test_tablename_is_set(self, model_source: str):
        assert "__tablename__" in model_source, "Model should declare __tablename__"
        assert (
            "'knowledge_base'" in model_source or '"knowledge_base"' in model_source
        ), "__tablename__ should be knowledge_base"

    def test_has_docstring(self, model_source: str):
        assert '"""' in model_source, "Model should provide a descriptive module/class docstring"


class TestKnowledgeBaseModelColumns:
    """Ensure expected columns are present and configured."""

    @pytest.mark.parametrize(
        "column_name",
        [
            "title",
            "category",
            "content",
            "content_format",
            "author_id",
            "is_published",
            "views",
        ],
    )
    def test_column_present(self, column_name: str, model_source: str):
        assert column_name in model_source, f"{column_name} column should be defined"

    def test_title_column_constraints(self, model_source: str):
        assert "title" in model_source
        assert "String" in model_source and "length=255" in model_source
        assert "nullable=False" in model_source, "title should be required"

    def test_category_length(self, model_source: str):
        assert "category" in model_source
        assert "String" in model_source and "length=100" in model_source

    def test_content_is_text(self, model_source: str):
        assert "content" in model_source
        assert "sa.Text" in model_source or "Text)" in model_source
        assert "nullable=False" in model_source, "content should be required"

    def test_author_id_foreign_key(self, model_source: str):
        assert "author_id" in model_source
        assert "ForeignKey" in model_source
        assert "users.id" in model_source, "author_id should reference users.id"


class TestKnowledgeBaseModelDefaults:
    """Check server defaults mirror migration guarantees."""

    def test_content_format_default(self, model_source: str):
        pattern = re.compile(r"content_format[\s\S]*server_default=sa\.text\([\"']*markdown[\"']*\)")
        assert pattern.search(model_source), "content_format should default to 'markdown'"

    def test_is_published_default(self, model_source: str):
        pattern = re.compile(r"is_published[\s\S]*server_default=sa\.text\([\"']*false[\"']*\)")
        assert pattern.search(model_source), "is_published should default to false"

    def test_views_default(self, model_source: str):
        pattern = re.compile(r"views[\s\S]*server_default=sa\.text\([\"']*0[\"']*\)")
        assert pattern.search(model_source), "views should default to 0"


class TestKnowledgeBaseModelRelationshipsAndHelpers:
    """Confirm nice-to-have helpers align with other models."""

    def test_author_relationship_defined(self, model_source: str):
        assert "relationship(" in model_source, "Model should declare SQLAlchemy relationship"
        assert (
            "author" in model_source and "relationship(" in model_source
        ), "Model should expose an author relationship"

    def test_has_repr_method(self, model_source: str):
        assert "def __repr__" in model_source, "Model should implement __repr__"

    def test_has_to_dict_helper(self, model_source: str):
        assert "def to_dict" in model_source, "Model should expose to_dict helper"
