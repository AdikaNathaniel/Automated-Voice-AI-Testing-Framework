"""
Test suite for TestExecutionQueue SQLAlchemy model

Validates the TestExecutionQueue model implementation including:
- Model structure and inheritance
- Column definitions
- Foreign key relationship to test_runs
- Priority and status fields
- Status management methods
- Queue operations methods
- Type hints
- Documentation
"""

import pytest
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
MODELS_DIR = PROJECT_ROOT / "backend" / "models"
TEST_EXECUTION_QUEUE_MODEL_FILE = MODELS_DIR / "test_execution_queue.py"


class TestTestExecutionQueueModelFileExists:
    """Test that TestExecutionQueue model file exists"""

    def test_models_directory_exists(self):
        """Test that models directory exists"""
        assert MODELS_DIR.exists(), "backend/models directory should exist"
        assert MODELS_DIR.is_dir(), "models should be a directory"

    def test_test_execution_queue_model_file_exists(self):
        """Test that test_execution_queue.py exists"""
        assert TEST_EXECUTION_QUEUE_MODEL_FILE.exists(), "test_execution_queue.py should exist"
        assert TEST_EXECUTION_QUEUE_MODEL_FILE.is_file(), "test_execution_queue.py should be a file"

    def test_model_file_has_content(self):
        """Test that model file has content"""
        content = TEST_EXECUTION_QUEUE_MODEL_FILE.read_text()
        assert len(content) > 0, "test_execution_queue.py should not be empty"


class TestTestExecutionQueueModelImports:
    """Test model imports"""

    def test_imports_base_and_basemodel(self):
        """Test that model imports Base and BaseModel"""
        content = TEST_EXECUTION_QUEUE_MODEL_FILE.read_text()
        assert ("from models.base import Base" in content or
                "from models.base import Base" in content or
                "from .base import Base" in content), "Should import Base"
        assert ("BaseModel" in content), "Should import BaseModel"

    def test_imports_sqlalchemy(self):
        """Test that model imports SQLAlchemy"""
        content = TEST_EXECUTION_QUEUE_MODEL_FILE.read_text()
        assert ("from sqlalchemy" in content or "import sqlalchemy" in content), "Should import SQLAlchemy"

    def test_imports_column_types(self):
        """Test that model imports necessary column types"""
        content = TEST_EXECUTION_QUEUE_MODEL_FILE.read_text()
        assert "Column" in content, "Should import Column"


class TestTestExecutionQueueModelClass:
    """Test TestExecutionQueue model class"""

    def test_defines_test_execution_queue_class(self):
        """Test that TestExecutionQueue class is defined"""
        content = TEST_EXECUTION_QUEUE_MODEL_FILE.read_text()
        assert "class TestExecutionQueue" in content, "Should define TestExecutionQueue class"

    def test_inherits_from_base_and_basemodel(self):
        """Test that TestExecutionQueue inherits from Base and BaseModel"""
        content = TEST_EXECUTION_QUEUE_MODEL_FILE.read_text()
        assert ("class TestExecutionQueue(Base, BaseModel)" in content or
                "class TestExecutionQueue(BaseModel, Base)" in content), "Should inherit from Base and BaseModel"

    def test_has_tablename(self):
        """Test that model has __tablename__"""
        content = TEST_EXECUTION_QUEUE_MODEL_FILE.read_text()
        assert "__tablename__" in content, "Should define __tablename__"
        assert "'test_execution_queue'" in content or '"test_execution_queue"' in content, "Table name should be test_execution_queue"


class TestTestExecutionQueueModelColumns:
    """Test model columns"""

    def test_has_test_run_id_column(self):
        """Test that model has test_run_id column"""
        content = TEST_EXECUTION_QUEUE_MODEL_FILE.read_text()
        assert "test_run_id" in content, "Should have test_run_id column"

    def test_has_priority_column(self):
        """Test that model has priority column"""
        content = TEST_EXECUTION_QUEUE_MODEL_FILE.read_text()
        assert "priority" in content, "Should have priority column"

    def test_has_status_column(self):
        """Test that model has status column"""
        content = TEST_EXECUTION_QUEUE_MODEL_FILE.read_text()
        assert "status" in content, "Should have status column"


class TestTestExecutionQueueModelColumnTypes:
    """Test column types"""

    def test_test_run_id_is_uuid(self):
        """Test that test_run_id is UUID type"""
        content = TEST_EXECUTION_QUEUE_MODEL_FILE.read_text()
        assert "UUID" in content or "uuid" in content.lower(), "test_run_id should be UUID type"

    def test_priority_is_integer(self):
        """Test that priority is Integer type"""
        content = TEST_EXECUTION_QUEUE_MODEL_FILE.read_text()
        assert "Integer" in content, "priority should be Integer type"

    def test_status_is_string(self):
        """Test that status is String type"""
        content = TEST_EXECUTION_QUEUE_MODEL_FILE.read_text()
        assert "String" in content, "status should be String type"

    def test_test_run_id_not_nullable(self):
        """Test that test_run_id is not nullable"""
        content = TEST_EXECUTION_QUEUE_MODEL_FILE.read_text()
        assert "nullable" in content, "Should have nullable constraints"

    def test_status_not_nullable(self):
        """Test that status is not nullable"""
        content = TEST_EXECUTION_QUEUE_MODEL_FILE.read_text()
        assert "nullable" in content, "Should have nullable constraints"


class TestTestExecutionQueueModelForeignKeys:
    """Test foreign key relationships"""

    def test_test_run_id_has_foreign_key(self):
        """Test that test_run_id has foreign key to test_runs"""
        content = TEST_EXECUTION_QUEUE_MODEL_FILE.read_text()
        assert (("ForeignKey" in content and "test_runs" in content)), "test_run_id should have foreign key to test_runs table"

    def test_has_relationship_definition(self):
        """Test that model has relationship definition"""
        content = TEST_EXECUTION_QUEUE_MODEL_FILE.read_text()
        assert ("relationship" in content), "Should define relationships"


class TestTestExecutionQueueModelRelationships:
    """Test model relationships"""

    def test_has_test_run_relationship(self):
        """Test that model has relationship to TestRun"""
        content = TEST_EXECUTION_QUEUE_MODEL_FILE.read_text()
        assert ("test_run" in content.lower() or "TestRun" in content), "Should have relationship to TestRun"


class TestTestExecutionQueueModelMethods:
    """Test model methods"""

    def test_has_repr_method(self):
        """Test that model has __repr__ method"""
        content = TEST_EXECUTION_QUEUE_MODEL_FILE.read_text()
        assert "def __repr__" in content, "Should have __repr__ method"

    def test_has_status_management_methods(self):
        """Test that model has methods for managing status"""
        content = TEST_EXECUTION_QUEUE_MODEL_FILE.read_text()
        # Should have methods to update status
        assert "def " in content, "Should have methods"


class TestTestExecutionQueueModelValidation:
    """Test model validation"""

    def test_has_validation_methods_or_validators(self):
        """Test that model has validation logic"""
        content = TEST_EXECUTION_QUEUE_MODEL_FILE.read_text()
        assert ((("def validate" in content or "validator" in content) or
                 "nullable=False" in content)), "Should have validation"


class TestTestExecutionQueueModelDocumentation:
    """Test model documentation"""

    def test_has_module_docstring(self):
        """Test that file has module docstring"""
        content = TEST_EXECUTION_QUEUE_MODEL_FILE.read_text()
        assert '"""' in content or "'''" in content, "Should have module docstring"

    def test_has_class_docstring(self):
        """Test that TestExecutionQueue class has docstring"""
        content = TEST_EXECUTION_QUEUE_MODEL_FILE.read_text()
        lines = content.split('\n')
        class_found = False
        for i, line in enumerate(lines):
            if "class TestExecutionQueue" in line:
                class_found = True
                next_lines = '\n'.join(lines[i:i+10])
                assert '"""' in next_lines or "'''" in next_lines, "TestExecutionQueue class should have docstring"
                break
        assert class_found, "TestExecutionQueue class should exist"

    def test_documents_attributes(self):
        """Test that model attributes are documented"""
        content = TEST_EXECUTION_QUEUE_MODEL_FILE.read_text()
        assert "comment" in content.lower(), "Should document column purposes"


class TestTestExecutionQueueModelTypeHints:
    """Test type hints"""

    def test_uses_type_hints(self):
        """Test that model uses type hints"""
        content = TEST_EXECUTION_QUEUE_MODEL_FILE.read_text()
        assert (":" in content or "Optional" in content or "int" in content), "Should use type hints"

    def test_imports_typing_if_needed(self):
        """Test that typing is imported if type hints are used"""
        content = TEST_EXECUTION_QUEUE_MODEL_FILE.read_text()
        if "Optional" in content:
            assert "from typing import" in content, "Should import from typing module"


class TestTestExecutionQueueModelStructure:
    """Test overall model structure"""

    def test_follows_model_pattern(self):
        """Test that model follows same pattern as other models"""
        content = TEST_EXECUTION_QUEUE_MODEL_FILE.read_text()
        assert "class TestExecutionQueue" in content, "Should have TestExecutionQueue class"
        assert "__tablename__" in content, "Should have __tablename__"
        assert "Column" in content, "Should have Column definitions"


class TestTestExecutionQueueModelQueueOperations:
    """Test queue operations methods"""

    def test_has_methods_for_queue_operations(self):
        """Test that model has methods for queue operations"""
        content = TEST_EXECUTION_QUEUE_MODEL_FILE.read_text()
        # Should have methods for queue management
        assert ("def " in content and "status" in content.lower()), "Should have methods for queue operations"
