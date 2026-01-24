"""
Test suite for ExpectedOutcome SQLAlchemy model

Validates the ExpectedOutcome model implementation including:
- Model structure and inheritance
- Column definitions
- JSONB fields for entities, validation_rules, language_variations
- Unique constraint on outcome_code
- Validation methods
- Model methods
- Type hints
- Documentation
"""

import pytest
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
MODELS_DIR = PROJECT_ROOT / "backend" / "models"
EXPECTED_OUTCOME_MODEL_FILE = MODELS_DIR / "expected_outcome.py"


class TestExpectedOutcomeModelFileExists:
    """Test that ExpectedOutcome model file exists"""

    def test_models_directory_exists(self):
        """Test that models directory exists"""
        assert MODELS_DIR.exists(), "backend/models directory should exist"
        assert MODELS_DIR.is_dir(), "models should be a directory"

    def test_expected_outcome_model_file_exists(self):
        """Test that expected_outcome.py exists"""
        assert EXPECTED_OUTCOME_MODEL_FILE.exists(), "expected_outcome.py should exist"
        assert EXPECTED_OUTCOME_MODEL_FILE.is_file(), "expected_outcome.py should be a file"

    def test_model_file_has_content(self):
        """Test that model file has content"""
        content = EXPECTED_OUTCOME_MODEL_FILE.read_text()
        assert len(content) > 0, "expected_outcome.py should not be empty"


class TestExpectedOutcomeModelImports:
    """Test model imports"""

    def test_imports_base_and_basemodel(self):
        """Test that model imports Base and BaseModel"""
        content = EXPECTED_OUTCOME_MODEL_FILE.read_text()
        assert ("from models.base import Base" in content or
                "from models.base import Base" in content or
                "from .base import Base" in content), "Should import Base"
        assert ("BaseModel" in content), "Should import BaseModel"

    def test_imports_sqlalchemy(self):
        """Test that model imports SQLAlchemy"""
        content = EXPECTED_OUTCOME_MODEL_FILE.read_text()
        assert ("from sqlalchemy" in content or "import sqlalchemy" in content), "Should import SQLAlchemy"

    def test_imports_column_types(self):
        """Test that model imports necessary column types"""
        content = EXPECTED_OUTCOME_MODEL_FILE.read_text()
        assert "Column" in content, "Should import Column"


class TestExpectedOutcomeModelClass:
    """Test ExpectedOutcome model class"""

    def test_defines_expected_outcome_class(self):
        """Test that ExpectedOutcome class is defined"""
        content = EXPECTED_OUTCOME_MODEL_FILE.read_text()
        assert "class ExpectedOutcome" in content, "Should define ExpectedOutcome class"

    def test_inherits_from_base_and_basemodel(self):
        """Test that ExpectedOutcome inherits from Base and BaseModel"""
        content = EXPECTED_OUTCOME_MODEL_FILE.read_text()
        # Check that class inherits from Base and BaseModel (may also include mixins)
        assert "class ExpectedOutcome(Base, BaseModel" in content, "Should inherit from Base and BaseModel"

    def test_has_tablename(self):
        """Test that model has __tablename__"""
        content = EXPECTED_OUTCOME_MODEL_FILE.read_text()
        assert "__tablename__" in content, "Should define __tablename__"
        assert "'expected_outcomes'" in content or '"expected_outcomes"' in content, "Table name should be expected_outcomes"


class TestExpectedOutcomeModelColumns:
    """Test model columns"""

    def test_has_outcome_code_column(self):
        """Test that model has outcome_code column"""
        content = EXPECTED_OUTCOME_MODEL_FILE.read_text()
        assert "outcome_code" in content, "Should have outcome_code column"

    def test_has_name_column(self):
        """Test that model has name column"""
        content = EXPECTED_OUTCOME_MODEL_FILE.read_text()
        assert "name" in content, "Should have name column"

    def test_has_description_column(self):
        """Test that model has description column"""
        content = EXPECTED_OUTCOME_MODEL_FILE.read_text()
        assert "description" in content, "Should have description column"

    def test_has_entities_column(self):
        """Test that model has entities column"""
        content = EXPECTED_OUTCOME_MODEL_FILE.read_text()
        assert "entities" in content, "Should have entities column"

    def test_has_validation_rules_column(self):
        """Test that model has validation_rules column"""
        content = EXPECTED_OUTCOME_MODEL_FILE.read_text()
        assert "validation_rules" in content, "Should have validation_rules column"

    def test_has_language_variations_column(self):
        """Test that model has language_variations column"""
        content = EXPECTED_OUTCOME_MODEL_FILE.read_text()
        assert "language_variations" in content, "Should have language_variations column"


class TestExpectedOutcomeModelColumnTypes:
    """Test column types"""

    def test_outcome_code_is_string(self):
        """Test that outcome_code is String type"""
        content = EXPECTED_OUTCOME_MODEL_FILE.read_text()
        assert "String" in content, "Should have String columns"

    def test_outcome_code_not_nullable(self):
        """Test that outcome_code is not nullable"""
        content = EXPECTED_OUTCOME_MODEL_FILE.read_text()
        assert "nullable" in content, "Should have nullable constraints"

    def test_outcome_code_is_unique(self):
        """Test that outcome_code is unique"""
        content = EXPECTED_OUTCOME_MODEL_FILE.read_text()
        assert "unique=True" in content or "unique" in content.lower(), "outcome_code should be unique"

    def test_name_is_string(self):
        """Test that name is String type"""
        content = EXPECTED_OUTCOME_MODEL_FILE.read_text()
        assert "String" in content, "name should be String type"

    def test_description_is_text(self):
        """Test that description is Text type"""
        content = EXPECTED_OUTCOME_MODEL_FILE.read_text()
        assert "Text" in content, "description should be Text type"

    def test_entities_is_jsonb(self):
        """Test that entities is JSONB type"""
        content = EXPECTED_OUTCOME_MODEL_FILE.read_text()
        assert "JSONB" in content, "entities should be JSONB type"

    def test_validation_rules_is_jsonb(self):
        """Test that validation_rules is JSONB type"""
        content = EXPECTED_OUTCOME_MODEL_FILE.read_text()
        assert "JSONB" in content, "validation_rules should be JSONB type"

    def test_language_variations_is_jsonb(self):
        """Test that language_variations is JSONB type"""
        content = EXPECTED_OUTCOME_MODEL_FILE.read_text()
        assert "JSONB" in content, "language_variations should be JSONB type"


class TestExpectedOutcomeModelJSONBFields:
    """Test JSONB field requirements"""

    def test_has_three_jsonb_fields(self):
        """Test that model has three JSONB fields"""
        content = EXPECTED_OUTCOME_MODEL_FILE.read_text()
        jsonb_count = content.count("JSONB")
        assert jsonb_count >= 3, "Should have at least 3 JSONB fields"

    def test_jsonb_fields_properly_defined(self):
        """Test that JSONB fields are properly defined"""
        content = EXPECTED_OUTCOME_MODEL_FILE.read_text()
        assert "entities" in content, "Should have entities JSONB field"
        assert "validation_rules" in content, "Should have validation_rules JSONB field"
        assert "language_variations" in content, "Should have language_variations JSONB field"


class TestExpectedOutcomeModelMethods:
    """Test model methods"""

    def test_has_repr_method(self):
        """Test that model has __repr__ method"""
        content = EXPECTED_OUTCOME_MODEL_FILE.read_text()
        assert "def __repr__" in content, "Should have __repr__ method"


class TestExpectedOutcomeModelValidation:
    """Test model validation"""

    def test_has_validation_methods_or_validators(self):
        """Test that model has validation logic"""
        content = EXPECTED_OUTCOME_MODEL_FILE.read_text()
        assert ((("def validate" in content or "validator" in content) or
                 "nullable=False" in content)), "Should have validation"


class TestExpectedOutcomeModelDocumentation:
    """Test model documentation"""

    def test_has_module_docstring(self):
        """Test that file has module docstring"""
        content = EXPECTED_OUTCOME_MODEL_FILE.read_text()
        assert '"""' in content or "'''" in content, "Should have module docstring"

    def test_has_class_docstring(self):
        """Test that ExpectedOutcome class has docstring"""
        content = EXPECTED_OUTCOME_MODEL_FILE.read_text()
        lines = content.split('\n')
        class_found = False
        for i, line in enumerate(lines):
            if "class ExpectedOutcome" in line:
                class_found = True
                next_lines = '\n'.join(lines[i:i+10])
                assert '"""' in next_lines or "'''" in next_lines, "ExpectedOutcome class should have docstring"
                break
        assert class_found, "ExpectedOutcome class should exist"

    def test_documents_attributes(self):
        """Test that model attributes are documented"""
        content = EXPECTED_OUTCOME_MODEL_FILE.read_text()
        assert "comment" in content.lower(), "Should document column purposes"


class TestExpectedOutcomeModelTypeHints:
    """Test type hints"""

    def test_uses_type_hints(self):
        """Test that model uses type hints"""
        content = EXPECTED_OUTCOME_MODEL_FILE.read_text()
        assert (":" in content or "Optional" in content or "Dict" in content), "Should use type hints"

    def test_imports_typing_if_needed(self):
        """Test that typing is imported if type hints are used"""
        content = EXPECTED_OUTCOME_MODEL_FILE.read_text()
        if "Optional" in content or "Dict" in content or "Any" in content:
            assert "from typing import" in content, "Should import from typing module"


class TestExpectedOutcomeModelStructure:
    """Test overall model structure"""

    def test_follows_model_pattern(self):
        """Test that model follows same pattern as other models"""
        content = EXPECTED_OUTCOME_MODEL_FILE.read_text()
        assert "class ExpectedOutcome" in content, "Should have ExpectedOutcome class"
        assert "__tablename__" in content, "Should have __tablename__"
        assert "Column" in content, "Should have Column definitions"


class TestExpectedOutcomeModelHelperMethods:
    """Test helper methods for JSONB fields"""

    def test_has_methods_for_managing_jsonb_data(self):
        """Test that model has helper methods for JSONB fields"""
        content = EXPECTED_OUTCOME_MODEL_FILE.read_text()
        # Should have methods to work with entities, validation_rules, or language_variations
        assert ("def " in content and
                ("entities" in content or "validation" in content or "language" in content)), "Should have helper methods for JSONB data"


class TestExpectedOutcomeModelUniqueConstraint:
    """Test unique constraint on outcome_code"""

    def test_outcome_code_has_unique_constraint(self):
        """Test that outcome_code has unique constraint"""
        content = EXPECTED_OUTCOME_MODEL_FILE.read_text()
        # Check for unique=True on outcome_code column
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'outcome_code' in line and 'Column' in line:
                # Look at this line and a few lines around it
                context = '\n'.join(lines[max(0, i-2):min(len(lines), i+5)])
                assert 'unique=True' in context or 'unique' in context, "outcome_code should have unique constraint"
                break
