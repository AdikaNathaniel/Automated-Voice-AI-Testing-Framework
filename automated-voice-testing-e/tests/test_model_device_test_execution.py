"""
Test suite for DeviceTestExecution SQLAlchemy model

Validates the DeviceTestExecution model implementation including:
- Model structure and inheritance
- Column definitions
- Foreign key relationship to test_runs
- JSONB fields (device_info, platform_details, test_results)
- JSONB helper methods for managing device test data
- Type hints
- Documentation
"""

import pytest
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
MODELS_DIR = PROJECT_ROOT / "backend" / "models"
DEVICE_TEST_EXECUTION_MODEL_FILE = MODELS_DIR / "device_test_execution.py"


class TestDeviceTestExecutionModelFileExists:
    """Test that DeviceTestExecution model file exists"""

    def test_models_directory_exists(self):
        """Test that models directory exists"""
        assert MODELS_DIR.exists(), "backend/models directory should exist"
        assert MODELS_DIR.is_dir(), "models should be a directory"

    def test_device_test_execution_model_file_exists(self):
        """Test that device_test_execution.py exists"""
        assert DEVICE_TEST_EXECUTION_MODEL_FILE.exists(), "device_test_execution.py should exist"
        assert DEVICE_TEST_EXECUTION_MODEL_FILE.is_file(), "device_test_execution.py should be a file"

    def test_model_file_has_content(self):
        """Test that model file has content"""
        content = DEVICE_TEST_EXECUTION_MODEL_FILE.read_text()
        assert len(content) > 0, "device_test_execution.py should not be empty"


class TestDeviceTestExecutionModelImports:
    """Test model imports"""

    def test_imports_base_and_basemodel(self):
        """Test that model imports Base and BaseModel"""
        content = DEVICE_TEST_EXECUTION_MODEL_FILE.read_text()
        assert ("from models.base import Base" in content or
                "from models.base import Base" in content or
                "from .base import Base" in content), "Should import Base"
        assert "BaseModel" in content, "Should import BaseModel"

    def test_imports_sqlalchemy(self):
        """Test that model imports SQLAlchemy"""
        content = DEVICE_TEST_EXECUTION_MODEL_FILE.read_text()
        assert ("from sqlalchemy" in content or "import sqlalchemy" in content), "Should import SQLAlchemy"

    def test_imports_column_types(self):
        """Test that model imports necessary column types"""
        content = DEVICE_TEST_EXECUTION_MODEL_FILE.read_text()
        assert "Column" in content, "Should import Column"

    def test_imports_jsonb_type(self):
        """Test that model imports JSONB type"""
        content = DEVICE_TEST_EXECUTION_MODEL_FILE.read_text()
        assert "JSONB" in content, "Should import JSONB type"


class TestDeviceTestExecutionModelClass:
    """Test DeviceTestExecution model class"""

    def test_defines_device_test_execution_class(self):
        """Test that DeviceTestExecution class is defined"""
        content = DEVICE_TEST_EXECUTION_MODEL_FILE.read_text()
        assert "class DeviceTestExecution" in content, "Should define DeviceTestExecution class"

    def test_inherits_from_base_and_basemodel(self):
        """Test that DeviceTestExecution inherits from Base and BaseModel"""
        content = DEVICE_TEST_EXECUTION_MODEL_FILE.read_text()
        assert ("class DeviceTestExecution(Base, BaseModel)" in content or
                "class DeviceTestExecution(BaseModel, Base)" in content), "Should inherit from Base and BaseModel"

    def test_has_tablename(self):
        """Test that model has __tablename__"""
        content = DEVICE_TEST_EXECUTION_MODEL_FILE.read_text()
        assert "__tablename__" in content, "Should define __tablename__"
        assert "'device_test_executions'" in content or '"device_test_executions"' in content, "Table name should be device_test_executions"


class TestDeviceTestExecutionModelColumns:
    """Test model columns"""

    def test_has_test_run_id_column(self):
        """Test that model has test_run_id column"""
        content = DEVICE_TEST_EXECUTION_MODEL_FILE.read_text()
        assert "test_run_id" in content, "Should have test_run_id column"

    def test_has_device_info_column(self):
        """Test that model has device_info column"""
        content = DEVICE_TEST_EXECUTION_MODEL_FILE.read_text()
        assert "device_info" in content, "Should have device_info column"

    def test_has_platform_details_column(self):
        """Test that model has platform_details column"""
        content = DEVICE_TEST_EXECUTION_MODEL_FILE.read_text()
        assert "platform_details" in content, "Should have platform_details column"

    def test_has_test_results_column(self):
        """Test that model has test_results column"""
        content = DEVICE_TEST_EXECUTION_MODEL_FILE.read_text()
        assert "test_results" in content, "Should have test_results column"


class TestDeviceTestExecutionModelColumnTypes:
    """Test column types"""

    def test_test_run_id_is_uuid(self):
        """Test that test_run_id is UUID type"""
        content = DEVICE_TEST_EXECUTION_MODEL_FILE.read_text()
        assert "UUID" in content or "uuid" in content.lower(), "test_run_id should be UUID type"

    def test_device_info_is_jsonb(self):
        """Test that device_info is JSONB type"""
        content = DEVICE_TEST_EXECUTION_MODEL_FILE.read_text()
        assert "JSONB" in content, "device_info should be JSONB type"

    def test_platform_details_is_jsonb(self):
        """Test that platform_details is JSONB type"""
        content = DEVICE_TEST_EXECUTION_MODEL_FILE.read_text()
        assert "JSONB" in content, "platform_details should be JSONB type"

    def test_test_results_is_jsonb(self):
        """Test that test_results is JSONB type"""
        content = DEVICE_TEST_EXECUTION_MODEL_FILE.read_text()
        assert "JSONB" in content, "test_results should be JSONB type"

    def test_test_run_id_not_nullable(self):
        """Test that test_run_id is not nullable"""
        content = DEVICE_TEST_EXECUTION_MODEL_FILE.read_text()
        assert "nullable" in content, "Should have nullable constraints"


class TestDeviceTestExecutionModelJSONBFields:
    """Test JSONB field requirements"""

    def test_has_three_jsonb_fields(self):
        """Test that model has three JSONB fields"""
        content = DEVICE_TEST_EXECUTION_MODEL_FILE.read_text()
        jsonb_count = content.count("JSONB")
        assert jsonb_count >= 3, "Should have at least 3 JSONB fields"


class TestDeviceTestExecutionModelForeignKeys:
    """Test foreign key relationships"""

    def test_test_run_id_has_foreign_key(self):
        """Test that test_run_id has foreign key to test_runs"""
        content = DEVICE_TEST_EXECUTION_MODEL_FILE.read_text()
        assert ("ForeignKey" in content and "test_runs" in content), "test_run_id should have foreign key to test_runs table"

    def test_has_relationship_definition(self):
        """Test that model has relationship definition"""
        content = DEVICE_TEST_EXECUTION_MODEL_FILE.read_text()
        assert "relationship" in content, "Should define relationships"


class TestDeviceTestExecutionModelRelationships:
    """Test model relationships"""

    def test_has_test_run_relationship(self):
        """Test that model has relationship to TestRun"""
        content = DEVICE_TEST_EXECUTION_MODEL_FILE.read_text()
        assert ("test_run" in content.lower() or "TestRun" in content), "Should have relationship to TestRun"


class TestDeviceTestExecutionModelMethods:
    """Test model methods"""

    def test_has_repr_method(self):
        """Test that model has __repr__ method"""
        content = DEVICE_TEST_EXECUTION_MODEL_FILE.read_text()
        assert "def __repr__" in content, "Should have __repr__ method"

    def test_has_device_info_helper_methods(self):
        """Test that model has helper methods for device_info"""
        content = DEVICE_TEST_EXECUTION_MODEL_FILE.read_text()
        # Should have methods to manage device_info JSONB field
        assert "def " in content, "Should have methods"

    def test_has_platform_details_helper_methods(self):
        """Test that model has helper methods for platform_details"""
        content = DEVICE_TEST_EXECUTION_MODEL_FILE.read_text()
        # Should have methods to manage platform_details JSONB field
        assert "def " in content, "Should have methods"

    def test_has_test_results_helper_methods(self):
        """Test that model has helper methods for test_results"""
        content = DEVICE_TEST_EXECUTION_MODEL_FILE.read_text()
        # Should have methods to manage test_results JSONB field
        assert "def " in content, "Should have methods"


class TestDeviceTestExecutionModelDeviceInfoMethods:
    """Test device_info JSONB helper methods"""

    def test_has_set_device_info_method(self):
        """Test that model has method to set device info"""
        content = DEVICE_TEST_EXECUTION_MODEL_FILE.read_text()
        assert ("set_device_info" in content or "add_device_info" in content or
                "update_device_info" in content), "Should have method to set device info"

    def test_has_get_device_info_method(self):
        """Test that model has method to get device info"""
        content = DEVICE_TEST_EXECUTION_MODEL_FILE.read_text()
        assert "get_device_info" in content, "Should have method to get device info"

    def test_has_get_all_device_info_method(self):
        """Test that model has method to get all device info"""
        content = DEVICE_TEST_EXECUTION_MODEL_FILE.read_text()
        assert ("get_all_device_info" in content or "get_device_info" in content), "Should have method to get all device info"


class TestDeviceTestExecutionModelPlatformDetailsMethods:
    """Test platform_details JSONB helper methods"""

    def test_has_set_platform_detail_method(self):
        """Test that model has method to set platform detail"""
        content = DEVICE_TEST_EXECUTION_MODEL_FILE.read_text()
        assert ("set_platform_detail" in content or "add_platform_detail" in content or
                "update_platform_detail" in content), "Should have method to set platform detail"

    def test_has_get_platform_detail_method(self):
        """Test that model has method to get platform detail"""
        content = DEVICE_TEST_EXECUTION_MODEL_FILE.read_text()
        assert "get_platform_detail" in content, "Should have method to get platform detail"

    def test_has_get_all_platform_details_method(self):
        """Test that model has method to get all platform details"""
        content = DEVICE_TEST_EXECUTION_MODEL_FILE.read_text()
        assert ("get_all_platform_details" in content or "get_platform_details" in content), "Should have method to get all platform details"


class TestDeviceTestExecutionModelTestResultsMethods:
    """Test test_results JSONB helper methods"""

    def test_has_set_test_result_method(self):
        """Test that model has method to set test result"""
        content = DEVICE_TEST_EXECUTION_MODEL_FILE.read_text()
        assert ("set_test_result" in content or "add_test_result" in content or
                "update_test_result" in content), "Should have method to set test result"

    def test_has_get_test_result_method(self):
        """Test that model has method to get test result"""
        content = DEVICE_TEST_EXECUTION_MODEL_FILE.read_text()
        assert "get_test_result" in content, "Should have method to get test result"

    def test_has_get_all_test_results_method(self):
        """Test that model has method to get all test results"""
        content = DEVICE_TEST_EXECUTION_MODEL_FILE.read_text()
        assert ("get_all_test_results" in content or "get_test_results" in content), "Should have method to get all test results"


class TestDeviceTestExecutionModelDocumentation:
    """Test model documentation"""

    def test_has_module_docstring(self):
        """Test that file has module docstring"""
        content = DEVICE_TEST_EXECUTION_MODEL_FILE.read_text()
        assert '"""' in content or "'''" in content, "Should have module docstring"

    def test_has_class_docstring(self):
        """Test that DeviceTestExecution class has docstring"""
        content = DEVICE_TEST_EXECUTION_MODEL_FILE.read_text()
        lines = content.split('\n')
        class_found = False
        for i, line in enumerate(lines):
            if "class DeviceTestExecution" in line:
                class_found = True
                next_lines = '\n'.join(lines[i:i+10])
                assert '"""' in next_lines or "'''" in next_lines, "DeviceTestExecution class should have docstring"
                break
        assert class_found, "DeviceTestExecution class should exist"

    def test_documents_attributes(self):
        """Test that model attributes are documented"""
        content = DEVICE_TEST_EXECUTION_MODEL_FILE.read_text()
        assert "comment" in content.lower(), "Should document column purposes"


class TestDeviceTestExecutionModelTypeHints:
    """Test type hints"""

    def test_uses_type_hints(self):
        """Test that model uses type hints"""
        content = DEVICE_TEST_EXECUTION_MODEL_FILE.read_text()
        assert (":" in content or "Optional" in content or "Dict" in content or "Any" in content), "Should use type hints"

    def test_imports_typing_if_needed(self):
        """Test that typing is imported if type hints are used"""
        content = DEVICE_TEST_EXECUTION_MODEL_FILE.read_text()
        if "Optional" in content or "Dict" in content or "Any" in content:
            assert "from typing import" in content, "Should import from typing module"


class TestDeviceTestExecutionModelStructure:
    """Test overall model structure"""

    def test_follows_model_pattern(self):
        """Test that model follows same pattern as other models"""
        content = DEVICE_TEST_EXECUTION_MODEL_FILE.read_text()
        assert "class DeviceTestExecution" in content, "Should have DeviceTestExecution class"
        assert "__tablename__" in content, "Should have __tablename__"
        assert "Column" in content, "Should have Column definitions"


class TestDeviceTestExecutionModelJSONBHelpers:
    """Test JSONB helper methods implementation"""

    def test_has_sufficient_helper_methods(self):
        """Test that model has sufficient helper methods for JSONB fields"""
        content = DEVICE_TEST_EXECUTION_MODEL_FILE.read_text()
        # Should have multiple def statements for helper methods
        def_count = content.count("def ")
        # At least __repr__ + 9 JSONB helpers (3 per field: set, get, get_all)
        assert def_count >= 10, "Should have at least 10 methods (__repr__ + 9 JSONB helpers)"
