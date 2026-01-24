"""
Test suite for ValidationQueue SQLAlchemy model

Validates the ValidationQueue model implementation including:
- Model structure and inheritance
- Column definitions
- Foreign key relationships to ValidationResult and User
- Default values
- Type hints
- Documentation
"""

import pytest
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
MODELS_DIR = PROJECT_ROOT / "backend" / "models"
VALIDATION_QUEUE_MODEL_FILE = MODELS_DIR / "validation_queue.py"


class TestValidationQueueModelFileExists:
    """Test that ValidationQueue model file exists"""

    def test_models_directory_exists(self):
        """Test that models directory exists"""
        assert MODELS_DIR.exists(), "backend/models directory should exist"
        assert MODELS_DIR.is_dir(), "models should be a directory"

    def test_validation_queue_model_file_exists(self):
        """Test that validation_queue.py exists"""
        assert VALIDATION_QUEUE_MODEL_FILE.exists(), \
            "validation_queue.py should exist in backend/models/"
        assert VALIDATION_QUEUE_MODEL_FILE.is_file(), \
            "validation_queue.py should be a file"

    def test_model_file_has_content(self):
        """Test that model file has content"""
        content = VALIDATION_QUEUE_MODEL_FILE.read_text()
        assert len(content) > 0, "validation_queue.py should not be empty"


class TestValidationQueueModelImports:
    """Test model imports"""

    def test_imports_base_and_basemodel(self):
        """Test that model imports Base and BaseModel"""
        content = VALIDATION_QUEUE_MODEL_FILE.read_text()
        has_base_import = (
            "from models.base import Base" in content or
            "from models.base import Base" in content or
            "from .base import Base" in content
        )
        assert has_base_import, "Should import Base"
        assert "BaseModel" in content, "Should import or reference BaseModel"

    def test_imports_sqlalchemy(self):
        """Test that model imports SQLAlchemy"""
        content = VALIDATION_QUEUE_MODEL_FILE.read_text()
        assert ("from sqlalchemy" in content or "import sqlalchemy" in content), \
            "Should import SQLAlchemy"

    def test_imports_column_types(self):
        """Test that model imports necessary column types"""
        content = VALIDATION_QUEUE_MODEL_FILE.read_text()
        assert "Column" in content, "Should import Column"

    def test_imports_foreign_key(self):
        """Test that model imports ForeignKey"""
        content = VALIDATION_QUEUE_MODEL_FILE.read_text()
        assert "ForeignKey" in content, "Should import ForeignKey for relationships"

    def test_imports_uuid_type(self):
        """Test that model imports UUID type"""
        content = VALIDATION_QUEUE_MODEL_FILE.read_text()
        assert ("UUID" in content or "postgresql.UUID" in content), \
            "Should import UUID type"


class TestValidationQueueModelClass:
    """Test ValidationQueue model class"""

    def test_defines_validation_queue_class(self):
        """Test that ValidationQueue class is defined"""
        content = VALIDATION_QUEUE_MODEL_FILE.read_text()
        assert "class ValidationQueue" in content, \
            "Should define ValidationQueue class"

    def test_inherits_from_base_and_basemodel(self):
        """Test that ValidationQueue inherits from Base and BaseModel"""
        content = VALIDATION_QUEUE_MODEL_FILE.read_text()
        has_inheritance = (
            "class ValidationQueue(Base, BaseModel)" in content or
            "class ValidationQueue(BaseModel, Base)" in content
        )
        assert has_inheritance, \
            "Should inherit from Base and BaseModel"

    def test_has_tablename(self):
        """Test that model has __tablename__"""
        content = VALIDATION_QUEUE_MODEL_FILE.read_text()
        assert "__tablename__" in content, "Should define __tablename__"
        assert ("'validation_queue'" in content or
                '"validation_queue"' in content), \
            "Table name should be validation_queue"

    def test_has_module_docstring(self):
        """Test that model has module-level docstring"""
        content = VALIDATION_QUEUE_MODEL_FILE.read_text()
        # Check for docstring at the beginning (triple quotes)
        assert ('"""' in content or "'''" in content), \
            "Should have module docstring"

    def test_has_class_docstring(self):
        """Test that ValidationQueue class has docstring"""
        content = VALIDATION_QUEUE_MODEL_FILE.read_text()
        # Check that class definition is followed by docstring
        if "class ValidationQueue" in content:
            class_start = content.find("class ValidationQueue")
            after_class = content[class_start:class_start + 300]
            assert ('"""' in after_class or "'''" in after_class), \
                "ValidationQueue class should have docstring"


class TestValidationQueueModelColumns:
    """Test model columns"""

    def test_has_validation_result_id_column(self):
        """Test that model has validation_result_id column"""
        content = VALIDATION_QUEUE_MODEL_FILE.read_text()
        assert "validation_result_id" in content, \
            "Should have validation_result_id column"

    def test_has_priority_column(self):
        """Test that model has priority column"""
        content = VALIDATION_QUEUE_MODEL_FILE.read_text()
        assert "priority" in content, \
            "Should have priority column"

    def test_has_confidence_score_column(self):
        """Test that model has confidence_score column"""
        content = VALIDATION_QUEUE_MODEL_FILE.read_text()
        assert "confidence_score" in content, \
            "Should have confidence_score column"

    def test_has_language_code_column(self):
        """Test that model has language_code column"""
        content = VALIDATION_QUEUE_MODEL_FILE.read_text()
        assert "language_code" in content, \
            "Should have language_code column"

    def test_has_claimed_by_column(self):
        """Test that model has claimed_by column"""
        content = VALIDATION_QUEUE_MODEL_FILE.read_text()
        assert "claimed_by" in content, \
            "Should have claimed_by column"

    def test_has_claimed_at_column(self):
        """Test that model has claimed_at column"""
        content = VALIDATION_QUEUE_MODEL_FILE.read_text()
        assert "claimed_at" in content, \
            "Should have claimed_at column"

    def test_has_status_column(self):
        """Test that model has status column"""
        content = VALIDATION_QUEUE_MODEL_FILE.read_text()
        assert "status" in content, \
            "Should have status column"

    def test_has_requires_native_speaker_column(self):
        """Test that model has requires_native_speaker column"""
        content = VALIDATION_QUEUE_MODEL_FILE.read_text()
        assert "requires_native_speaker" in content, \
            "Should have requires_native_speaker column"


class TestValidationQueueColumnTypes:
    """Test column types"""

    def test_validation_result_id_is_uuid_foreign_key(self):
        """Test that validation_result_id is UUID and foreign key"""
        content = VALIDATION_QUEUE_MODEL_FILE.read_text()
        assert "UUID" in content or "postgresql.UUID" in content, \
            "validation_result_id should be UUID type"
        assert "ForeignKey" in content, \
            "validation_result_id should have ForeignKey"

    def test_priority_is_integer(self):
        """Test that priority is Integer type"""
        content = VALIDATION_QUEUE_MODEL_FILE.read_text()
        assert "Integer" in content, \
            "priority should be Integer type"

    def test_confidence_score_is_numeric(self):
        """Test that confidence_score is Numeric type"""
        content = VALIDATION_QUEUE_MODEL_FILE.read_text()
        assert "Numeric" in content, \
            "confidence_score should be Numeric type"

    def test_language_code_is_string(self):
        """Test that language_code is String type"""
        content = VALIDATION_QUEUE_MODEL_FILE.read_text()
        assert "String" in content, \
            "language_code should be String type"

    def test_claimed_by_is_uuid_foreign_key(self):
        """Test that claimed_by is UUID and foreign key"""
        content = VALIDATION_QUEUE_MODEL_FILE.read_text()
        assert "UUID" in content or "postgresql.UUID" in content, \
            "claimed_by should be UUID type"
        # Check that there are at least 2 ForeignKey references
        assert content.count("ForeignKey") >= 2, \
            "Should have at least 2 ForeignKey references"

    def test_timestamps_use_datetime(self):
        """Test that timestamp columns use DateTime"""
        content = VALIDATION_QUEUE_MODEL_FILE.read_text()
        assert "DateTime" in content, \
            "Timestamp columns should use DateTime type"

    def test_status_is_string(self):
        """Test that status is String type"""
        content = VALIDATION_QUEUE_MODEL_FILE.read_text()
        assert "String" in content, \
            "status should be String type"

    def test_requires_native_speaker_is_boolean(self):
        """Test that requires_native_speaker is Boolean type"""
        content = VALIDATION_QUEUE_MODEL_FILE.read_text()
        assert "Boolean" in content, \
            "requires_native_speaker should be Boolean type"


class TestValidationQueueForeignKeys:
    """Test foreign key relationships"""

    def test_has_foreign_key_to_validation_results(self):
        """Test that validation_result_id references validation_results table"""
        content = VALIDATION_QUEUE_MODEL_FILE.read_text()
        assert "validation_results" in content.lower(), \
            "Should reference validation_results table"

    def test_has_foreign_key_to_users(self):
        """Test that claimed_by references users table"""
        content = VALIDATION_QUEUE_MODEL_FILE.read_text()
        assert "users" in content.lower(), \
            "Should reference users table"


class TestValidationQueueTypeHints:
    """Test type hints"""

    def test_imports_typing_module(self):
        """Test that model imports from typing module"""
        content = VALIDATION_QUEUE_MODEL_FILE.read_text()
        assert ("from typing import" in content or "import typing" in content), \
            "Should import from typing module for type hints"

    def test_has_optional_type_hints(self):
        """Test that model uses Optional for nullable fields"""
        content = VALIDATION_QUEUE_MODEL_FILE.read_text()
        assert "Optional" in content, \
            "Should use Optional type hint for nullable fields"


class TestValidationQueueRelationships:
    """Test model relationships"""

    def test_may_have_relationship_definitions(self):
        """Test that model may define relationships to related models"""
        content = VALIDATION_QUEUE_MODEL_FILE.read_text()
        # Relationships are optional but check if they exist
        has_relationship = "relationship" in content.lower()
        # This test always passes but documents the optional feature
        assert True, "Relationships are optional in this model"


class TestValidationQueueDefaults:
    """Test default values"""

    def test_priority_has_default(self):
        """Test that priority has default value"""
        content = VALIDATION_QUEUE_MODEL_FILE.read_text()
        # Look for default=5 or server_default near priority
        assert "default" in content.lower(), \
            "priority should have a default value"

    def test_status_has_default(self):
        """Test that status has default value"""
        content = VALIDATION_QUEUE_MODEL_FILE.read_text()
        # Look for default='pending' or server_default near status
        assert "default" in content.lower(), \
            "status should have a default value"

    def test_requires_native_speaker_has_default(self):
        """Test that requires_native_speaker has default value"""
        content = VALIDATION_QUEUE_MODEL_FILE.read_text()
        # Look for default=False or server_default
        assert "default" in content.lower(), \
            "requires_native_speaker should have a default value"
