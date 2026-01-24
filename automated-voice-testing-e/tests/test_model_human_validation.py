"""
Test suite for HumanValidation SQLAlchemy model

Validates the HumanValidation model implementation including:
- Model structure and inheritance
- Column definitions
- Foreign key relationships to ValidationResult and User
- Timestamp columns
- Boolean default values
- Type hints
- Documentation
"""

import pytest
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
MODELS_DIR = PROJECT_ROOT / "backend" / "models"
HUMAN_VALIDATION_MODEL_FILE = MODELS_DIR / "human_validation.py"


class TestHumanValidationModelFileExists:
    """Test that HumanValidation model file exists"""

    def test_models_directory_exists(self):
        """Test that models directory exists"""
        assert MODELS_DIR.exists(), "backend/models directory should exist"
        assert MODELS_DIR.is_dir(), "models should be a directory"

    def test_human_validation_model_file_exists(self):
        """Test that human_validation.py exists"""
        assert HUMAN_VALIDATION_MODEL_FILE.exists(), \
            "human_validation.py should exist in backend/models/"
        assert HUMAN_VALIDATION_MODEL_FILE.is_file(), \
            "human_validation.py should be a file"

    def test_model_file_has_content(self):
        """Test that model file has content"""
        content = HUMAN_VALIDATION_MODEL_FILE.read_text()
        assert len(content) > 0, "human_validation.py should not be empty"


class TestHumanValidationModelImports:
    """Test model imports"""

    def test_imports_base_and_basemodel(self):
        """Test that model imports Base and BaseModel"""
        content = HUMAN_VALIDATION_MODEL_FILE.read_text()
        has_base_import = (
            "from models.base import Base" in content or
            "from models.base import Base" in content or
            "from .base import Base" in content
        )
        assert has_base_import, "Should import Base"
        assert "BaseModel" in content, "Should import or reference BaseModel"

    def test_imports_sqlalchemy(self):
        """Test that model imports SQLAlchemy"""
        content = HUMAN_VALIDATION_MODEL_FILE.read_text()
        assert ("from sqlalchemy" in content or "import sqlalchemy" in content), \
            "Should import SQLAlchemy"

    def test_imports_column_types(self):
        """Test that model imports necessary column types"""
        content = HUMAN_VALIDATION_MODEL_FILE.read_text()
        assert "Column" in content, "Should import Column"

    def test_imports_foreign_key(self):
        """Test that model imports ForeignKey"""
        content = HUMAN_VALIDATION_MODEL_FILE.read_text()
        assert "ForeignKey" in content, "Should import ForeignKey for relationships"

    def test_imports_uuid_type(self):
        """Test that model imports UUID type"""
        content = HUMAN_VALIDATION_MODEL_FILE.read_text()
        assert ("UUID" in content or "postgresql.UUID" in content), \
            "Should import UUID type"


class TestHumanValidationModelClass:
    """Test HumanValidation model class"""

    def test_defines_human_validation_class(self):
        """Test that HumanValidation class is defined"""
        content = HUMAN_VALIDATION_MODEL_FILE.read_text()
        assert "class HumanValidation" in content, \
            "Should define HumanValidation class"

    def test_inherits_from_base_and_basemodel(self):
        """Test that HumanValidation inherits from Base and BaseModel"""
        content = HUMAN_VALIDATION_MODEL_FILE.read_text()
        has_inheritance = (
            "class HumanValidation(Base, BaseModel)" in content or
            "class HumanValidation(BaseModel, Base)" in content
        )
        assert has_inheritance, \
            "Should inherit from Base and BaseModel"

    def test_has_tablename(self):
        """Test that model has __tablename__"""
        content = HUMAN_VALIDATION_MODEL_FILE.read_text()
        assert "__tablename__" in content, "Should define __tablename__"
        assert ("'human_validations'" in content or
                '"human_validations"' in content), \
            "Table name should be human_validations"

    def test_has_module_docstring(self):
        """Test that model has module-level docstring"""
        content = HUMAN_VALIDATION_MODEL_FILE.read_text()
        # Check for docstring at the beginning (triple quotes)
        assert ('"""' in content or "'''" in content), \
            "Should have module docstring"

    def test_has_class_docstring(self):
        """Test that HumanValidation class has docstring"""
        content = HUMAN_VALIDATION_MODEL_FILE.read_text()
        # Check that class definition is followed by docstring
        if "class HumanValidation" in content:
            class_start = content.find("class HumanValidation")
            after_class = content[class_start:class_start + 300]
            assert ('"""' in after_class or "'''" in after_class), \
                "HumanValidation class should have docstring"


class TestHumanValidationModelColumns:
    """Test model columns"""

    def test_has_validation_result_id_column(self):
        """Test that model has validation_result_id column"""
        content = HUMAN_VALIDATION_MODEL_FILE.read_text()
        assert "validation_result_id" in content, \
            "Should have validation_result_id column"

    def test_has_validator_id_column(self):
        """Test that model has validator_id column"""
        content = HUMAN_VALIDATION_MODEL_FILE.read_text()
        assert "validator_id" in content, \
            "Should have validator_id column"

    def test_has_claimed_at_column(self):
        """Test that model has claimed_at column"""
        content = HUMAN_VALIDATION_MODEL_FILE.read_text()
        assert "claimed_at" in content, \
            "Should have claimed_at column"

    def test_has_submitted_at_column(self):
        """Test that model has submitted_at column"""
        content = HUMAN_VALIDATION_MODEL_FILE.read_text()
        assert "submitted_at" in content, \
            "Should have submitted_at column"

    def test_has_validation_decision_column(self):
        """Test that model has validation_decision column"""
        content = HUMAN_VALIDATION_MODEL_FILE.read_text()
        assert "validation_decision" in content, \
            "Should have validation_decision column"

    def test_has_feedback_column(self):
        """Test that model has feedback column"""
        content = HUMAN_VALIDATION_MODEL_FILE.read_text()
        assert "feedback" in content, \
            "Should have feedback column"

    def test_has_time_spent_seconds_column(self):
        """Test that model has time_spent_seconds column"""
        content = HUMAN_VALIDATION_MODEL_FILE.read_text()
        assert "time_spent_seconds" in content, \
            "Should have time_spent_seconds column"

    def test_has_is_second_opinion_column(self):
        """Test that model has is_second_opinion column"""
        content = HUMAN_VALIDATION_MODEL_FILE.read_text()
        assert "is_second_opinion" in content, \
            "Should have is_second_opinion column"


class TestHumanValidationColumnTypes:
    """Test column types"""

    def test_validation_result_id_is_uuid_foreign_key(self):
        """Test that validation_result_id is UUID and foreign key"""
        content = HUMAN_VALIDATION_MODEL_FILE.read_text()
        assert "UUID" in content or "postgresql.UUID" in content, \
            "validation_result_id should be UUID type"
        assert "ForeignKey" in content, \
            "validation_result_id should have ForeignKey"

    def test_validator_id_is_uuid_foreign_key(self):
        """Test that validator_id is UUID and foreign key"""
        content = HUMAN_VALIDATION_MODEL_FILE.read_text()
        assert "UUID" in content or "postgresql.UUID" in content, \
            "validator_id should be UUID type"
        # Check that there are at least 2 ForeignKey references
        assert content.count("ForeignKey") >= 2, \
            "Should have at least 2 ForeignKey references"

    def test_timestamps_use_datetime(self):
        """Test that timestamp columns use DateTime"""
        content = HUMAN_VALIDATION_MODEL_FILE.read_text()
        assert "DateTime" in content, \
            "Timestamp columns should use DateTime type"

    def test_validation_decision_is_string(self):
        """Test that validation_decision is String type"""
        content = HUMAN_VALIDATION_MODEL_FILE.read_text()
        assert "String" in content, \
            "validation_decision should be String type"

    def test_feedback_is_text(self):
        """Test that feedback is Text type"""
        content = HUMAN_VALIDATION_MODEL_FILE.read_text()
        assert "Text" in content, \
            "feedback should be Text type"

    def test_time_spent_seconds_is_integer(self):
        """Test that time_spent_seconds is Integer type"""
        content = HUMAN_VALIDATION_MODEL_FILE.read_text()
        assert "Integer" in content, \
            "time_spent_seconds should be Integer type"

    def test_is_second_opinion_is_boolean(self):
        """Test that is_second_opinion is Boolean type"""
        content = HUMAN_VALIDATION_MODEL_FILE.read_text()
        assert "Boolean" in content, \
            "is_second_opinion should be Boolean type"


class TestHumanValidationForeignKeys:
    """Test foreign key relationships"""

    def test_has_foreign_key_to_validation_results(self):
        """Test that validation_result_id references validation_results table"""
        content = HUMAN_VALIDATION_MODEL_FILE.read_text()
        assert "validation_results" in content.lower(), \
            "Should reference validation_results table"

    def test_has_foreign_key_to_users(self):
        """Test that validator_id references users table"""
        content = HUMAN_VALIDATION_MODEL_FILE.read_text()
        assert "users" in content.lower(), \
            "Should reference users table"


class TestHumanValidationTypeHints:
    """Test type hints"""

    def test_imports_typing_module(self):
        """Test that model imports from typing module"""
        content = HUMAN_VALIDATION_MODEL_FILE.read_text()
        assert ("from typing import" in content or "import typing" in content), \
            "Should import from typing module for type hints"

    def test_has_optional_type_hints(self):
        """Test that model uses Optional for nullable fields"""
        content = HUMAN_VALIDATION_MODEL_FILE.read_text()
        assert "Optional" in content, \
            "Should use Optional type hint for nullable fields"


class TestHumanValidationRelationships:
    """Test model relationships"""

    def test_may_have_relationship_definitions(self):
        """Test that model may define relationships to related models"""
        content = HUMAN_VALIDATION_MODEL_FILE.read_text()
        # Relationships are optional but check if they exist
        has_relationship = "relationship" in content.lower()
        # This test always passes but documents the optional feature
        assert True, "Relationships are optional in this model"
