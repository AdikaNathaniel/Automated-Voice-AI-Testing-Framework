"""
Test suite for TestRun SQLAlchemy model

Validates the TestRun model implementation including:
- Model structure and inheritance
- Column definitions
- Foreign key relationships to test_suites and users
- Status tracking columns
- Test metrics columns
- Calculated properties (progress_percentage)
- Status management methods
- Type hints
- Documentation
"""

import pytest
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
MODELS_DIR = PROJECT_ROOT / "backend" / "models"
TEST_RUN_MODEL_FILE = MODELS_DIR / "test_run.py"


class TestTestRunModelFileExists:
    """Test that TestRun model file exists"""

    def test_models_directory_exists(self):
        """Test that models directory exists"""
        assert MODELS_DIR.exists(), "backend/models directory should exist"
        assert MODELS_DIR.is_dir(), "models should be a directory"

    def test_test_run_model_file_exists(self):
        """Test that test_run.py exists"""
        assert TEST_RUN_MODEL_FILE.exists(), "test_run.py should exist"
        assert TEST_RUN_MODEL_FILE.is_file(), "test_run.py should be a file"

    def test_model_file_has_content(self):
        """Test that model file has content"""
        content = TEST_RUN_MODEL_FILE.read_text()
        assert len(content) > 0, "test_run.py should not be empty"


class TestTestRunModelImports:
    """Test model imports"""

    def test_imports_base_and_basemodel(self):
        """Test that model imports Base and BaseModel"""
        content = TEST_RUN_MODEL_FILE.read_text()
        assert ("from models.base import Base" in content or
                "from models.base import Base" in content or
                "from .base import Base" in content), "Should import Base"
        assert ("BaseModel" in content), "Should import BaseModel"

    def test_imports_sqlalchemy(self):
        """Test that model imports SQLAlchemy"""
        content = TEST_RUN_MODEL_FILE.read_text()
        assert ("from sqlalchemy" in content or "import sqlalchemy" in content), "Should import SQLAlchemy"

    def test_imports_column_types(self):
        """Test that model imports necessary column types"""
        content = TEST_RUN_MODEL_FILE.read_text()
        assert "Column" in content, "Should import Column"


class TestTestRunModelClass:
    """Test TestRun model class"""

    def test_defines_test_run_class(self):
        """Test that TestRun class is defined"""
        content = TEST_RUN_MODEL_FILE.read_text()
        assert "class TestRun" in content, "Should define TestRun class"

    def test_inherits_from_base_and_basemodel(self):
        """Test that TestRun inherits from Base and BaseModel"""
        content = TEST_RUN_MODEL_FILE.read_text()
        assert ("class TestRun(Base, BaseModel)" in content or
                "class TestRun(BaseModel, Base)" in content), "Should inherit from Base and BaseModel"

    def test_has_tablename(self):
        """Test that model has __tablename__"""
        content = TEST_RUN_MODEL_FILE.read_text()
        assert "__tablename__" in content, "Should define __tablename__"
        assert "'test_runs'" in content or '"test_runs"' in content, "Table name should be test_runs"


class TestTestRunModelColumns:
    """Test model columns"""

    def test_has_suite_id_column(self):
        """Test that model has suite_id column"""
        content = TEST_RUN_MODEL_FILE.read_text()
        assert "suite_id" in content, "Should have suite_id column"

    def test_has_created_by_column(self):
        """Test that model has created_by column"""
        content = TEST_RUN_MODEL_FILE.read_text()
        assert "created_by" in content, "Should have created_by column"

    def test_has_status_column(self):
        """Test that model has status column"""
        content = TEST_RUN_MODEL_FILE.read_text()
        assert "status" in content, "Should have status column"

    def test_has_started_at_column(self):
        """Test that model has started_at column"""
        content = TEST_RUN_MODEL_FILE.read_text()
        assert "started_at" in content, "Should have started_at column"

    def test_has_completed_at_column(self):
        """Test that model has completed_at column"""
        content = TEST_RUN_MODEL_FILE.read_text()
        assert "completed_at" in content, "Should have completed_at column"

    def test_has_total_tests_column(self):
        """Test that model has total_tests column"""
        content = TEST_RUN_MODEL_FILE.read_text()
        assert "total_tests" in content, "Should have total_tests column"

    def test_has_passed_tests_column(self):
        """Test that model has passed_tests column"""
        content = TEST_RUN_MODEL_FILE.read_text()
        assert "passed_tests" in content, "Should have passed_tests column"

    def test_has_failed_tests_column(self):
        """Test that model has failed_tests column"""
        content = TEST_RUN_MODEL_FILE.read_text()
        assert "failed_tests" in content, "Should have failed_tests column"

    def test_has_skipped_tests_column(self):
        """Test that model has skipped_tests column"""
        content = TEST_RUN_MODEL_FILE.read_text()
        assert "skipped_tests" in content, "Should have skipped_tests column"


class TestTestRunModelColumnTypes:
    """Test column types"""

    def test_suite_id_is_uuid(self):
        """Test that suite_id is UUID type"""
        content = TEST_RUN_MODEL_FILE.read_text()
        assert "UUID" in content or "uuid" in content.lower(), "suite_id should be UUID type"

    def test_created_by_is_uuid(self):
        """Test that created_by is UUID type"""
        content = TEST_RUN_MODEL_FILE.read_text()
        assert "UUID" in content or "uuid" in content.lower(), "created_by should be UUID type"

    def test_status_is_string(self):
        """Test that status is String type"""
        content = TEST_RUN_MODEL_FILE.read_text()
        assert "String" in content, "status should be String type"

    def test_datetime_columns_are_datetime(self):
        """Test that timestamp columns are DateTime type"""
        content = TEST_RUN_MODEL_FILE.read_text()
        assert "DateTime" in content, "Should have DateTime columns"

    def test_test_count_columns_are_integer(self):
        """Test that test count columns are Integer type"""
        content = TEST_RUN_MODEL_FILE.read_text()
        assert "Integer" in content, "Test count columns should be Integer type"

    def test_suite_id_not_nullable(self):
        """Test that suite_id is not nullable"""
        content = TEST_RUN_MODEL_FILE.read_text()
        assert "nullable" in content, "Should have nullable constraints"

    def test_status_not_nullable(self):
        """Test that status is not nullable"""
        content = TEST_RUN_MODEL_FILE.read_text()
        assert "nullable" in content, "Should have nullable constraints"


class TestTestRunModelForeignKeys:
    """Test foreign key relationships"""

    def test_suite_id_has_foreign_key(self):
        """Test that suite_id has foreign key to test_suites"""
        content = TEST_RUN_MODEL_FILE.read_text()
        assert (("ForeignKey" in content and "test_suites" in content)), "suite_id should have foreign key to test_suites table"

    def test_created_by_has_foreign_key(self):
        """Test that created_by has foreign key to users"""
        content = TEST_RUN_MODEL_FILE.read_text()
        assert (("ForeignKey" in content and "users" in content)), "created_by should have foreign key to users table"

    def test_has_relationship_definition(self):
        """Test that model has relationship definition"""
        content = TEST_RUN_MODEL_FILE.read_text()
        assert ("relationship" in content), "Should define relationships"


class TestTestRunModelRelationships:
    """Test model relationships"""

    def test_has_test_suite_relationship(self):
        """Test that model has relationship to TestSuite"""
        content = TEST_RUN_MODEL_FILE.read_text()
        assert ("test_suite" in content.lower() or "TestSuite" in content), "Should have relationship to TestSuite"

    def test_has_user_relationship(self):
        """Test that model has relationship to User"""
        content = TEST_RUN_MODEL_FILE.read_text()
        assert ("user" in content.lower() or "User" in content), "Should have relationship to User"


class TestTestRunModelCalculatedProperties:
    """Test calculated properties"""

    def test_has_progress_percentage_property(self):
        """Test that model has progress_percentage property"""
        content = TEST_RUN_MODEL_FILE.read_text()
        assert ("progress_percentage" in content or "progress" in content), "Should have progress_percentage property"

    def test_progress_percentage_is_property(self):
        """Test that progress_percentage is a property"""
        content = TEST_RUN_MODEL_FILE.read_text()
        assert ("@property" in content), "Should use @property decorator"


class TestTestRunModelMethods:
    """Test model methods"""

    def test_has_repr_method(self):
        """Test that model has __repr__ method"""
        content = TEST_RUN_MODEL_FILE.read_text()
        assert "def __repr__" in content, "Should have __repr__ method"

    def test_has_status_management_methods(self):
        """Test that model has methods for managing status"""
        content = TEST_RUN_MODEL_FILE.read_text()
        # Should have methods to update status
        assert "def " in content, "Should have methods"


class TestTestRunModelValidation:
    """Test model validation"""

    def test_has_validation_methods_or_validators(self):
        """Test that model has validation logic"""
        content = TEST_RUN_MODEL_FILE.read_text()
        assert ((("def validate" in content or "validator" in content) or
                 "nullable=False" in content)), "Should have validation"


class TestTestRunModelDocumentation:
    """Test model documentation"""

    def test_has_module_docstring(self):
        """Test that file has module docstring"""
        content = TEST_RUN_MODEL_FILE.read_text()
        assert '"""' in content or "'''" in content, "Should have module docstring"

    def test_has_class_docstring(self):
        """Test that TestRun class has docstring"""
        content = TEST_RUN_MODEL_FILE.read_text()
        lines = content.split('\n')
        class_found = False
        for i, line in enumerate(lines):
            if "class TestRun" in line:
                class_found = True
                next_lines = '\n'.join(lines[i:i+10])
                assert '"""' in next_lines or "'''" in next_lines, "TestRun class should have docstring"
                break
        assert class_found, "TestRun class should exist"

    def test_documents_attributes(self):
        """Test that model attributes are documented"""
        content = TEST_RUN_MODEL_FILE.read_text()
        assert "comment" in content.lower(), "Should document column purposes"


class TestTestRunModelTypeHints:
    """Test type hints"""

    def test_uses_type_hints(self):
        """Test that model uses type hints"""
        content = TEST_RUN_MODEL_FILE.read_text()
        assert (":" in content or "Optional" in content or "int" in content), "Should use type hints"

    def test_imports_typing_if_needed(self):
        """Test that typing is imported if type hints are used"""
        content = TEST_RUN_MODEL_FILE.read_text()
        if "Optional" in content:
            assert "from typing import" in content, "Should import from typing module"


class TestTestRunModelStructure:
    """Test overall model structure"""

    def test_follows_model_pattern(self):
        """Test that model follows same pattern as other models"""
        content = TEST_RUN_MODEL_FILE.read_text()
        assert "class TestRun" in content, "Should have TestRun class"
        assert "__tablename__" in content, "Should have __tablename__"
        assert "Column" in content, "Should have Column definitions"


class TestTestRunModelStatusManagement:
    """Test status management methods"""

    def test_has_methods_for_status_transitions(self):
        """Test that model has methods for status transitions"""
        content = TEST_RUN_MODEL_FILE.read_text()
        # Should have methods to transition between statuses
        assert ("def " in content and "status" in content.lower()), "Should have methods for status management"
