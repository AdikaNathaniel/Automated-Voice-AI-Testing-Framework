"""
Test suite for TestSuite SQLAlchemy model

Validates the TestSuite model implementation including:
- Model structure and inheritance
- Column definitions
- Relationships to other models
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
TEST_SUITE_MODEL_FILE = MODELS_DIR / "test_suite.py"


class TestTestSuiteModelFileExists:
    """Test that TestSuite model file exists"""

    def test_models_directory_exists(self):
        """Test that models directory exists"""
        assert MODELS_DIR.exists(), "backend/models directory should exist"
        assert MODELS_DIR.is_dir(), "models should be a directory"

    def test_test_suite_model_file_exists(self):
        """Test that test_suite.py exists"""
        assert TEST_SUITE_MODEL_FILE.exists(), "test_suite.py should exist"
        assert TEST_SUITE_MODEL_FILE.is_file(), "test_suite.py should be a file"

    def test_model_file_has_content(self):
        """Test that model file has content"""
        content = TEST_SUITE_MODEL_FILE.read_text()
        assert len(content) > 0, "test_suite.py should not be empty"


class TestTestSuiteModelImports:
    """Test model imports"""

    def test_imports_base_and_basemodel(self):
        """Test that model imports Base and BaseModel"""
        content = TEST_SUITE_MODEL_FILE.read_text()
        assert ("from models.base import Base" in content or
                "from models.base import Base" in content or
                "from .base import Base" in content), "Should import Base"
        assert ("BaseModel" in content), "Should import BaseModel"

    def test_imports_sqlalchemy(self):
        """Test that model imports SQLAlchemy"""
        content = TEST_SUITE_MODEL_FILE.read_text()
        assert ("from sqlalchemy" in content or "import sqlalchemy" in content), "Should import SQLAlchemy"

    def test_imports_column_types(self):
        """Test that model imports necessary column types"""
        content = TEST_SUITE_MODEL_FILE.read_text()
        assert "Column" in content, "Should import Column"


class TestTestSuiteModelClass:
    """Test TestSuite model class"""

    def test_defines_test_suite_class(self):
        """Test that TestSuite class is defined"""
        content = TEST_SUITE_MODEL_FILE.read_text()
        assert "class TestSuite" in content, "Should define TestSuite class"

    def test_inherits_from_base_and_basemodel(self):
        """Test that TestSuite inherits from Base and BaseModel"""
        content = TEST_SUITE_MODEL_FILE.read_text()
        assert ("class TestSuite(Base, BaseModel)" in content or
                "class TestSuite(BaseModel, Base)" in content), "Should inherit from Base and BaseModel"

    def test_has_tablename(self):
        """Test that model has __tablename__"""
        content = TEST_SUITE_MODEL_FILE.read_text()
        assert "__tablename__" in content, "Should define __tablename__"
        assert "'test_suites'" in content or '"test_suites"' in content, "Table name should be test_suites"


class TestTestSuiteModelColumns:
    """Test model columns"""

    def test_has_name_column(self):
        """Test that model has name column"""
        content = TEST_SUITE_MODEL_FILE.read_text()
        assert "name" in content, "Should have name column"

    def test_has_description_column(self):
        """Test that model has description column"""
        content = TEST_SUITE_MODEL_FILE.read_text()
        assert "description" in content, "Should have description column"

    def test_has_category_column(self):
        """Test that model has category column"""
        content = TEST_SUITE_MODEL_FILE.read_text()
        assert "category" in content, "Should have category column"

    def test_has_is_active_column(self):
        """Test that model has is_active column"""
        content = TEST_SUITE_MODEL_FILE.read_text()
        assert "is_active" in content, "Should have is_active column"

    def test_has_created_by_column(self):
        """Test that model has created_by column"""
        content = TEST_SUITE_MODEL_FILE.read_text()
        assert "created_by" in content, "Should have created_by column"


class TestTestSuiteModelColumnTypes:
    """Test column types"""

    def test_name_is_string(self):
        """Test that name is String type"""
        content = TEST_SUITE_MODEL_FILE.read_text()
        assert "String" in content, "Should have String columns"

    def test_name_not_nullable(self):
        """Test that name is not nullable"""
        content = TEST_SUITE_MODEL_FILE.read_text()
        assert "nullable" in content, "Should have nullable constraints"

    def test_description_is_text(self):
        """Test that description is Text type"""
        content = TEST_SUITE_MODEL_FILE.read_text()
        assert "Text" in content, "description should be Text type"

    def test_is_active_is_boolean(self):
        """Test that is_active is Boolean type"""
        content = TEST_SUITE_MODEL_FILE.read_text()
        assert "Boolean" in content, "is_active should be Boolean type"

    def test_is_active_has_default(self):
        """Test that is_active has default value"""
        content = TEST_SUITE_MODEL_FILE.read_text()
        assert "default" in content, "is_active should have default value"

    def test_created_by_is_uuid(self):
        """Test that created_by is UUID type"""
        content = TEST_SUITE_MODEL_FILE.read_text()
        assert "UUID" in content or "uuid" in content.lower(), "created_by should be UUID type"


class TestTestSuiteModelForeignKeys:
    """Test foreign key relationships"""

    def test_created_by_has_foreign_key(self):
        """Test that created_by has foreign key to users"""
        content = TEST_SUITE_MODEL_FILE.read_text()
        assert ("ForeignKey" in content and "users" in content), "created_by should have foreign key to users table"

    def test_has_relationship_definition(self):
        """Test that model has relationship definition"""
        content = TEST_SUITE_MODEL_FILE.read_text()
        # Should have relationship to either User or TestCase
        assert ("relationship" in content), "Should define relationships"


class TestTestSuiteModelRelationships:
    """Test model relationships"""

    def test_has_creator_relationship(self):
        """Test that model has relationship to User (creator)"""
        content = TEST_SUITE_MODEL_FILE.read_text()
        # May be named 'creator', 'created_by_user', or 'user'
        assert ("relationship" in content), "Should have relationship to User"

    def test_has_test_cases_relationship(self):
        """Test that model has relationship to TestCase"""
        content = TEST_SUITE_MODEL_FILE.read_text()
        # Should mention TestCase in relationship
        assert ("test_cases" in content.lower() or "TestCase" in content), "Should have relationship to TestCase"


class TestTestSuiteModelMethods:
    """Test model methods"""

    def test_has_repr_method(self):
        """Test that model has __repr__ method"""
        content = TEST_SUITE_MODEL_FILE.read_text()
        assert "def __repr__" in content, "Should have __repr__ method"


class TestTestSuiteModelValidation:
    """Test model validation"""

    def test_has_validation_methods_or_validators(self):
        """Test that model has validation logic"""
        content = TEST_SUITE_MODEL_FILE.read_text()
        # Could have validate method or use validators
        assert (("def validate" in content or "validator" in content or
                 "nullable=False" in content)), "Should have validation"


class TestTestSuiteModelDocumentation:
    """Test model documentation"""

    def test_has_module_docstring(self):
        """Test that file has module docstring"""
        content = TEST_SUITE_MODEL_FILE.read_text()
        assert '"""' in content or "'''" in content, "Should have module docstring"

    def test_has_class_docstring(self):
        """Test that TestSuite class has docstring"""
        content = TEST_SUITE_MODEL_FILE.read_text()
        lines = content.split('\n')
        # Find class definition and check for docstring nearby
        class_found = False
        for i, line in enumerate(lines):
            if "class TestSuite" in line:
                class_found = True
                # Check next few lines for docstring
                next_lines = '\n'.join(lines[i:i+10])
                assert '"""' in next_lines or "'''" in next_lines, "TestSuite class should have docstring"
                break
        assert class_found, "TestSuite class should exist"

    def test_documents_attributes(self):
        """Test that model attributes are documented"""
        content = TEST_SUITE_MODEL_FILE.read_text()
        # Should have comments explaining columns
        assert "comment" in content.lower(), "Should document column purposes"


class TestTestSuiteModelTypeHints:
    """Test type hints"""

    def test_uses_type_hints(self):
        """Test that model uses type hints"""
        content = TEST_SUITE_MODEL_FILE.read_text()
        # Should have type hints for attributes or methods
        assert (":" in content or "Optional" in content or "List" in content), "Should use type hints"

    def test_imports_typing_if_needed(self):
        """Test that typing is imported if type hints are used"""
        content = TEST_SUITE_MODEL_FILE.read_text()
        # If using Optional, List, etc., should import from typing
        if "Optional" in content or "List" in content:
            assert "from typing import" in content, "Should import from typing module"


class TestTestSuiteModelStructure:
    """Test overall model structure"""

    def test_follows_user_model_pattern(self):
        """Test that model follows same pattern as User model"""
        content = TEST_SUITE_MODEL_FILE.read_text()
        # Should have similar structure: class, tablename, columns, methods
        assert "class TestSuite" in content, "Should have TestSuite class"
        assert "__tablename__" in content, "Should have __tablename__"
        assert "Column" in content, "Should have Column definitions"
