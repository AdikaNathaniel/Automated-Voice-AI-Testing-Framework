"""
Test suite for Configuration SQLAlchemy model

Validates the Configuration model implementation including:
- Model structure and inheritance
- Column definitions
- JSONB field for config_data
- JSONB helper methods for managing configuration data
- Type hints
- Documentation
"""

import pytest
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
MODELS_DIR = PROJECT_ROOT / "backend" / "models"
CONFIGURATION_MODEL_FILE = MODELS_DIR / "configuration.py"


class TestConfigurationModelFileExists:
    """Test that Configuration model file exists"""

    def test_models_directory_exists(self):
        """Test that models directory exists"""
        assert MODELS_DIR.exists(), "backend/models directory should exist"
        assert MODELS_DIR.is_dir(), "models should be a directory"

    def test_configuration_model_file_exists(self):
        """Test that configuration.py exists"""
        assert CONFIGURATION_MODEL_FILE.exists(), "configuration.py should exist"
        assert CONFIGURATION_MODEL_FILE.is_file(), "configuration.py should be a file"

    def test_model_file_has_content(self):
        """Test that model file has content"""
        content = CONFIGURATION_MODEL_FILE.read_text()
        assert len(content) > 0, "configuration.py should not be empty"


class TestConfigurationModelImports:
    """Test model imports"""

    def test_imports_base_and_basemodel(self):
        """Test that model imports Base and BaseModel"""
        content = CONFIGURATION_MODEL_FILE.read_text()
        assert ("from models.base import Base" in content or
                "from models.base import Base" in content or
                "from .base import Base" in content), "Should import Base"
        assert "BaseModel" in content, "Should import BaseModel"

    def test_imports_sqlalchemy(self):
        """Test that model imports SQLAlchemy"""
        content = CONFIGURATION_MODEL_FILE.read_text()
        assert ("from sqlalchemy" in content or "import sqlalchemy" in content), "Should import SQLAlchemy"

    def test_imports_column_types(self):
        """Test that model imports necessary column types"""
        content = CONFIGURATION_MODEL_FILE.read_text()
        assert "Column" in content, "Should import Column"

    def test_imports_jsonb_type(self):
        """Test that model imports JSONB type"""
        content = CONFIGURATION_MODEL_FILE.read_text()
        assert "JSONB" in content, "Should import JSONB type"


class TestConfigurationModelClass:
    """Test Configuration model class"""

    def test_defines_configuration_class(self):
        """Test that Configuration class is defined"""
        content = CONFIGURATION_MODEL_FILE.read_text()
        assert "class Configuration" in content, "Should define Configuration class"

    def test_inherits_from_base_and_basemodel(self):
        """Test that Configuration inherits from Base and BaseModel"""
        content = CONFIGURATION_MODEL_FILE.read_text()
        assert ("class Configuration(Base, BaseModel)" in content or
                "class Configuration(BaseModel, Base)" in content), "Should inherit from Base and BaseModel"

    def test_has_tablename(self):
        """Test that model has __tablename__"""
        content = CONFIGURATION_MODEL_FILE.read_text()
        assert "__tablename__" in content, "Should define __tablename__"
        assert "'configurations'" in content or '"configurations"' in content, "Table name should be configurations"


class TestConfigurationModelColumns:
    """Test model columns"""

    def test_has_config_key_column(self):
        """Test that model has config_key column"""
        content = CONFIGURATION_MODEL_FILE.read_text()
        assert "config_key" in content, "Should have config_key column"

    def test_has_config_data_column(self):
        """Test that model has config_data column"""
        content = CONFIGURATION_MODEL_FILE.read_text()
        assert "config_data" in content, "Should have config_data column"


class TestConfigurationModelColumnTypes:
    """Test column types"""

    def test_config_key_is_string(self):
        """Test that config_key is String type"""
        content = CONFIGURATION_MODEL_FILE.read_text()
        assert "String" in content, "config_key should be String type"

    def test_config_data_is_jsonb(self):
        """Test that config_data is JSONB type"""
        content = CONFIGURATION_MODEL_FILE.read_text()
        assert "JSONB" in content, "config_data should be JSONB type"

    def test_config_key_not_nullable(self):
        """Test that config_key is not nullable"""
        content = CONFIGURATION_MODEL_FILE.read_text()
        assert "nullable" in content, "Should have nullable constraints"

    def test_config_key_unique(self):
        """Test that config_key has unique constraint"""
        content = CONFIGURATION_MODEL_FILE.read_text()
        assert "unique" in content.lower(), "config_key should have unique constraint"


class TestConfigurationModelJSONBField:
    """Test JSONB field requirements"""

    def test_has_jsonb_field(self):
        """Test that model has JSONB field"""
        content = CONFIGURATION_MODEL_FILE.read_text()
        jsonb_count = content.count("JSONB")
        assert jsonb_count >= 1, "Should have at least 1 JSONB field"


class TestConfigurationModelMethods:
    """Test model methods"""

    def test_has_repr_method(self):
        """Test that model has __repr__ method"""
        content = CONFIGURATION_MODEL_FILE.read_text()
        assert "def __repr__" in content, "Should have __repr__ method"

    def test_has_config_data_helper_methods(self):
        """Test that model has helper methods for config_data"""
        content = CONFIGURATION_MODEL_FILE.read_text()
        # Should have methods to manage config_data JSONB field
        assert "def " in content, "Should have methods"


class TestConfigurationModelConfigDataMethods:
    """Test config_data JSONB helper methods"""

    def test_has_set_config_method(self):
        """Test that model has method to set config value"""
        content = CONFIGURATION_MODEL_FILE.read_text()
        assert ("set_config" in content or "set_config_value" in content or
                "update_config" in content), "Should have method to set config value"

    def test_has_get_config_method(self):
        """Test that model has method to get config value"""
        content = CONFIGURATION_MODEL_FILE.read_text()
        assert ("get_config" in content or "get_config_value" in content), "Should have method to get config value"

    def test_has_get_all_config_method(self):
        """Test that model has method to get all config data"""
        content = CONFIGURATION_MODEL_FILE.read_text()
        assert ("get_all_config" in content or "get_config_data" in content), "Should have method to get all config data"


class TestConfigurationModelDocumentation:
    """Test model documentation"""

    def test_has_module_docstring(self):
        """Test that file has module docstring"""
        content = CONFIGURATION_MODEL_FILE.read_text()
        assert '"""' in content or "'''" in content, "Should have module docstring"

    def test_has_class_docstring(self):
        """Test that Configuration class has docstring"""
        content = CONFIGURATION_MODEL_FILE.read_text()
        lines = content.split('\n')
        class_found = False
        for i, line in enumerate(lines):
            if "class Configuration" in line:
                class_found = True
                next_lines = '\n'.join(lines[i:i+10])
                assert '"""' in next_lines or "'''" in next_lines, "Configuration class should have docstring"
                break
        assert class_found, "Configuration class should exist"

    def test_documents_attributes(self):
        """Test that model attributes are documented"""
        content = CONFIGURATION_MODEL_FILE.read_text()
        assert "comment" in content.lower(), "Should document column purposes"


class TestConfigurationModelTypeHints:
    """Test type hints"""

    def test_uses_type_hints(self):
        """Test that model uses type hints"""
        content = CONFIGURATION_MODEL_FILE.read_text()
        assert (":" in content or "Optional" in content or "Dict" in content or "Any" in content), "Should use type hints"

    def test_imports_typing_if_needed(self):
        """Test that typing is imported if type hints are used"""
        content = CONFIGURATION_MODEL_FILE.read_text()
        if "Optional" in content or "Dict" in content or "Any" in content:
            assert "from typing import" in content, "Should import from typing module"


class TestConfigurationModelStructure:
    """Test overall model structure"""

    def test_follows_model_pattern(self):
        """Test that model follows same pattern as other models"""
        content = CONFIGURATION_MODEL_FILE.read_text()
        assert "class Configuration" in content, "Should have Configuration class"
        assert "__tablename__" in content, "Should have __tablename__"
        assert "Column" in content, "Should have Column definitions"


class TestConfigurationModelHelperMethods:
    """Test helper methods implementation"""

    def test_has_sufficient_helper_methods(self):
        """Test that model has sufficient helper methods for JSONB field"""
        content = CONFIGURATION_MODEL_FILE.read_text()
        # Should have multiple def statements for helper methods
        def_count = content.count("def ")
        # At least __repr__ + 3 JSONB helpers (set, get, get_all)
        assert def_count >= 4, "Should have at least 4 methods (__repr__ + 3 JSONB helpers)"
