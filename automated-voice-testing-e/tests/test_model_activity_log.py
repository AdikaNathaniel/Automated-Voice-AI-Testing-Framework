"""
Test suite for the ActivityLog SQLAlchemy model.

Ensures the implementation:
- Exists and follows project import conventions
- Declares ActivityLog class inheriting from Base & BaseModel
- Mirrors the activity_log migration schema (columns, constraints, types)
- Provides relationship to the User model
- Exposes helpful dunder helpers for debugging/serialisation
"""

from __future__ import annotations

from pathlib import Path
import re

import pytest

PROJECT_ROOT = Path(__file__).parent.parent
MODELS_DIR = PROJECT_ROOT / "backend" / "models"
ACTIVITY_LOG_MODEL_FILE = MODELS_DIR / "activity_log.py"


class TestActivityLogModelFile:
    """Validate the ActivityLog model module exists and is populated."""

    def test_models_directory_exists(self) -> None:
        assert MODELS_DIR.exists(), "backend/models directory should exist"
        assert MODELS_DIR.is_dir(), "backend/models should be a directory"

    def test_model_file_exists(self) -> None:
        assert ACTIVITY_LOG_MODEL_FILE.exists(), "activity_log.py should exist"
        assert ACTIVITY_LOG_MODEL_FILE.is_file(), "activity_log.py should be a file"

    def test_model_file_has_content(self) -> None:
        content = ACTIVITY_LOG_MODEL_FILE.read_text(encoding="utf-8")
        assert content.strip(), "activity_log.py should not be empty"


@pytest.fixture(scope="module")
def model_source() -> str:
    """Load the ActivityLog model source for downstream assertions."""
    return ACTIVITY_LOG_MODEL_FILE.read_text(encoding="utf-8")


class TestActivityLogModelImports:
    """Verify the model follows import conventions."""

    def test_imports_base(self, model_source: str) -> None:
        assert (
            "from models.base import Base" in model_source
            or "from models.base import Base" in model_source
        ), "Model should import Base"

    def test_imports_sqlalchemy_alias(self, model_source: str) -> None:
        assert "import sqlalchemy as sa" in model_source, "Model should import SQLAlchemy as sa"

    def test_imports_postgresql_dialects(self, model_source: str) -> None:
        assert "from sqlalchemy.dialects import postgresql" in model_source, "Model should import PostgreSQL dialect helpers"

    def test_imports_relationship(self, model_source: str) -> None:
        assert "from sqlalchemy.orm import relationship" in model_source, "Model should import relationship helper"


class TestActivityLogModelClassDefinition:
    """Validate core class declaration metadata."""

    def test_class_is_declared(self, model_source: str) -> None:
        assert "class ActivityLog" in model_source, "ActivityLog class should be defined"

    def test_inheritance_structure(self, model_source: str) -> None:
        patterns = [
            re.compile(r"class ActivityLog\((BaseModel, Base|Base, BaseModel)\)"),
            re.compile(r"class ActivityLog\((Base,)\)"),
            re.compile(r"class ActivityLog\((Base)\)"),
        ]
        assert any(pattern.search(model_source) for pattern in patterns), (
            "ActivityLog should inherit from Base (optionally BaseModel for shared helpers)"
        )

    def test_tablename_is_activity_log(self, model_source: str) -> None:
        assert "__tablename__" in model_source, "Model should declare __tablename__"
        assert (
            "'activity_log'" in model_source or '"activity_log"' in model_source
        ), "__tablename__ should be set to 'activity_log'"

    def test_has_docstring(self, model_source: str) -> None:
        assert '"""' in model_source, "Model should include a descriptive docstring"


class TestActivityLogModelColumns:
    """Ensure columns mirror the migration schema."""

    @pytest.mark.parametrize(
        "column_name",
        [
            "id",
            "user_id",
            "action_type",
            "resource_type",
            "resource_id",
            "action_description",
            "metadata",
            "ip_address",
            "created_at",
        ],
    )
    def test_column_defined(self, column_name: str, model_source: str) -> None:
        assert column_name in model_source, f"{column_name} column should be defined"

    def test_id_uuid_primary_key(self, model_source: str) -> None:
        assert "id" in model_source
        assert "postgresql.UUID" in model_source, "id should use PostgreSQL UUID type"
        pattern = re.compile(r"id[\s\S]*primary_key=True")
        assert pattern.search(model_source), "id should be a primary key"

    def test_user_id_foreign_key(self, model_source: str) -> None:
        assert "user_id" in model_source
        assert "ForeignKey" in model_source and "users.id" in model_source, "user_id should reference users.id"
        pattern = re.compile(r"user_id[\s\S]*nullable=False")
        assert pattern.search(model_source), "user_id should be non-nullable"

    def test_action_type_constraints(self, model_source: str) -> None:
        assert "action_type" in model_source
        assert "sa.String" in model_source and "length=100" in model_source, "action_type should be String(100)"
        pattern = re.compile(r"action_type[\s\S]*nullable=False")
        assert pattern.search(model_source), "action_type should be non-nullable"

    def test_resource_type_optional_string(self, model_source: str) -> None:
        assert "resource_type" in model_source
        assert "sa.String" in model_source and "length=100" in model_source, "resource_type should be String(100)"
        pattern = re.compile(r"resource_type[\s\S]*nullable=True")
        assert pattern.search(model_source), "resource_type should be nullable"

    def test_resource_id_uuid(self, model_source: str) -> None:
        assert "resource_id" in model_source
        assert "postgresql.UUID" in model_source, "resource_id should use PostgreSQL UUID type"

    def test_action_description_text(self, model_source: str) -> None:
        assert "action_description" in model_source
        assert "sa.Text" in model_source, "action_description should be stored as Text"

    def test_metadata_jsonb(self, model_source: str) -> None:
        assert "metadata" in model_source
        assert "postgresql.JSONB" in model_source, "metadata should be JSONB column"

    def test_ip_address_inet(self, model_source: str) -> None:
        assert "ip_address" in model_source
        assert "postgresql.INET" in model_source, "ip_address should use INET type"

    def test_created_at_default(self, model_source: str) -> None:
        pattern = re.compile(r"created_at[\s\S]*server_default=sa\.text\([\"']now\(\)[\"']\)")
        assert pattern.search(model_source), "created_at should default to now()"


class TestActivityLogModelRelationshipsAndHelpers:
    """Check relationships and helper methods exist."""

    def test_user_relationship_defined(self, model_source: str) -> None:
        assert "relationship(" in model_source, "Model should define SQLAlchemy relationship"
        assert "user" in model_source, "Model should expose a user relationship"

    def test_has_repr_method(self, model_source: str) -> None:
        assert "def __repr__" in model_source, "Model should implement __repr__"

    def test_has_to_dict_helper(self, model_source: str) -> None:
        assert "def to_dict" in model_source, "Model should expose to_dict helper"
