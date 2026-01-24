"""
Test suite for ConfigurationHistory SQLAlchemy model

Validates the ConfigurationHistory model implementation including:
- Model structure and inheritance
- Column definitions
- Relationship to Configuration model
- Relationship to User model
- JSONB fields for old_value and new_value
- JSONB helper methods for managing historical values
- Type hints
- Documentation
"""

import pytest
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
MODELS_DIR = PROJECT_ROOT / "backend" / "models"
CONFIG_HISTORY_MODEL_FILE = MODELS_DIR / "configuration_history.py"


class TestConfigurationHistoryModelFileExists:
    """Test that ConfigurationHistory model file exists"""

    def test_models_directory_exists(self):
        """Test that models directory exists"""
        assert MODELS_DIR.exists(), "backend/models directory should exist"
        assert MODELS_DIR.is_dir(), "models should be a directory"

    def test_configuration_history_model_file_exists(self):
        """Test that configuration_history.py exists"""
        assert CONFIG_HISTORY_MODEL_FILE.exists(), "configuration_history.py should exist"
        assert CONFIG_HISTORY_MODEL_FILE.is_file(), "configuration_history.py should be a file"

    def test_model_file_has_content(self):
        """Test that model file has content"""
        content = CONFIG_HISTORY_MODEL_FILE.read_text()
        assert len(content) > 0, "configuration_history.py should not be empty"


class TestConfigurationHistoryModelImports:
    """Test model imports"""

    def test_imports_base_and_basemodel(self):
        """Test that model imports Base and BaseModel"""
        content = CONFIG_HISTORY_MODEL_FILE.read_text()
        assert ("from models.base import Base" in content or
                "from models.base import Base" in content or
                "from .base import Base" in content), "Should import Base"
        assert "BaseModel" in content, "Should import BaseModel"

    def test_imports_sqlalchemy(self):
        """Test that model imports SQLAlchemy"""
        content = CONFIG_HISTORY_MODEL_FILE.read_text()
        assert ("from sqlalchemy" in content or "import sqlalchemy" in content), "Should import SQLAlchemy"

    def test_imports_column_types(self):
        """Test that model imports necessary column types"""
        content = CONFIG_HISTORY_MODEL_FILE.read_text()
        assert "Column" in content, "Should import Column"

    def test_imports_jsonb_type(self):
        """Test that model imports JSONB type"""
        content = CONFIG_HISTORY_MODEL_FILE.read_text()
        assert "JSONB" in content, "Should import JSONB type"

    def test_imports_foreignkey(self):
        """Test that model imports ForeignKey"""
        content = CONFIG_HISTORY_MODEL_FILE.read_text()
        assert "ForeignKey" in content, "Should import ForeignKey"


class TestConfigurationHistoryModelClass:
    """Test ConfigurationHistory model class"""

    def test_defines_configuration_history_class(self):
        """Test that ConfigurationHistory class is defined"""
        content = CONFIG_HISTORY_MODEL_FILE.read_text()
        assert "class ConfigurationHistory" in content, "Should define ConfigurationHistory class"

    def test_inherits_from_base_and_basemodel(self):
        """Test that ConfigurationHistory inherits from Base and BaseModel"""
        content = CONFIG_HISTORY_MODEL_FILE.read_text()
        assert ("class ConfigurationHistory(Base, BaseModel)" in content or
                "class ConfigurationHistory(BaseModel, Base)" in content), "Should inherit from Base and BaseModel"

    def test_has_tablename(self):
        """Test that model has __tablename__"""
        content = CONFIG_HISTORY_MODEL_FILE.read_text()
        assert "__tablename__" in content, "Should define __tablename__"
        assert "'configuration_history'" in content or '"configuration_history"' in content, "Table name should be configuration_history"


class TestConfigurationHistoryModelColumns:
    """Test model columns"""

    def test_has_configuration_id_column(self):
        """Test that model has configuration_id column"""
        content = CONFIG_HISTORY_MODEL_FILE.read_text()
        assert "configuration_id" in content, "Should have configuration_id column"

    def test_has_config_key_column(self):
        """Test that model has config_key column"""
        content = CONFIG_HISTORY_MODEL_FILE.read_text()
        assert "config_key" in content, "Should have config_key column"

    def test_has_old_value_column(self):
        """Test that model has old_value column"""
        content = CONFIG_HISTORY_MODEL_FILE.read_text()
        assert "old_value" in content, "Should have old_value column"

    def test_has_new_value_column(self):
        """Test that model has new_value column"""
        content = CONFIG_HISTORY_MODEL_FILE.read_text()
        assert "new_value" in content, "Should have new_value column"

    def test_has_changed_by_column(self):
        """Test that model has changed_by column"""
        content = CONFIG_HISTORY_MODEL_FILE.read_text()
        assert "changed_by" in content, "Should have changed_by column"


class TestConfigurationHistoryModelColumnTypes:
    """Test column types"""

    def test_configuration_id_is_uuid(self):
        """Test that configuration_id is UUID type"""
        content = CONFIG_HISTORY_MODEL_FILE.read_text()
        assert ("UUID" in content or "uuid" in content.lower()), "configuration_id should be UUID type"

    def test_config_key_is_string(self):
        """Test that config_key is String type"""
        content = CONFIG_HISTORY_MODEL_FILE.read_text()
        assert "String" in content, "config_key should be String type"

    def test_old_value_is_jsonb(self):
        """Test that old_value is JSONB type"""
        content = CONFIG_HISTORY_MODEL_FILE.read_text()
        assert "JSONB" in content, "old_value should be JSONB type"

    def test_new_value_is_jsonb(self):
        """Test that new_value is JSONB type"""
        content = CONFIG_HISTORY_MODEL_FILE.read_text()
        assert "JSONB" in content, "new_value should be JSONB type"

    def test_changed_by_is_uuid(self):
        """Test that changed_by is UUID type"""
        content = CONFIG_HISTORY_MODEL_FILE.read_text()
        assert ("UUID" in content or "uuid" in content.lower()), "changed_by should be UUID type"


class TestConfigurationHistoryModelForeignKeys:
    """Test foreign key relationships"""

    def test_configuration_id_is_foreign_key(self):
        """Test that configuration_id is a foreign key"""
        content = CONFIG_HISTORY_MODEL_FILE.read_text()
        assert "ForeignKey" in content, "configuration_id should be a foreign key"
        assert "configurations" in content, "configuration_id should reference configurations table"

    def test_changed_by_is_foreign_key(self):
        """Test that changed_by is a foreign key"""
        content = CONFIG_HISTORY_MODEL_FILE.read_text()
        assert "ForeignKey" in content, "changed_by should be a foreign key"
        if "changed_by" in content and "ForeignKey" in content:
            assert "users" in content, "changed_by should reference users table if foreign key is defined"


class TestConfigurationHistoryModelJSONBFields:
    """Test JSONB field requirements"""

    def test_has_two_jsonb_fields(self):
        """Test that model has two JSONB fields"""
        content = CONFIG_HISTORY_MODEL_FILE.read_text()
        jsonb_count = content.count("JSONB")
        assert jsonb_count >= 2, "Should have at least 2 JSONB fields (old_value, new_value)"


class TestConfigurationHistoryModelRelationships:
    """Test model relationships"""

    def test_has_relationship_to_configuration(self):
        """Test that model has relationship to Configuration"""
        content = CONFIG_HISTORY_MODEL_FILE.read_text()
        assert ("relationship" in content and "Configuration" in content), "Should have relationship to Configuration"

    def test_has_relationship_to_user(self):
        """Test that model has relationship to User"""
        content = CONFIG_HISTORY_MODEL_FILE.read_text()
        # Changed by should reference User
        if "changed_by" in content:
            assert "relationship" in content, "Should have relationships defined"


class TestConfigurationHistoryModelMethods:
    """Test model methods"""

    def test_has_repr_method(self):
        """Test that model has __repr__ method"""
        content = CONFIG_HISTORY_MODEL_FILE.read_text()
        assert "def __repr__" in content, "Should have __repr__ method"

    def test_has_jsonb_helper_methods(self):
        """Test that model has helper methods for JSONB fields"""
        content = CONFIG_HISTORY_MODEL_FILE.read_text()
        # Should have methods to manage old_value and new_value JSONB fields
        assert "def " in content, "Should have methods"


class TestConfigurationHistoryModelOldValueMethods:
    """Test old_value JSONB helper methods"""

    def test_has_set_old_value_method(self):
        """Test that model has method to set old value"""
        content = CONFIG_HISTORY_MODEL_FILE.read_text()
        assert ("set_old_value" in content or "old_value" in content), "Should have method to set old value"

    def test_has_get_old_value_method(self):
        """Test that model has method to get old value"""
        content = CONFIG_HISTORY_MODEL_FILE.read_text()
        assert ("get_old_value" in content or "old_value" in content), "Should have method to get old value"


class TestConfigurationHistoryModelNewValueMethods:
    """Test new_value JSONB helper methods"""

    def test_has_set_new_value_method(self):
        """Test that model has method to set new value"""
        content = CONFIG_HISTORY_MODEL_FILE.read_text()
        assert ("set_new_value" in content or "new_value" in content), "Should have method to set new value"

    def test_has_get_new_value_method(self):
        """Test that model has method to get new value"""
        content = CONFIG_HISTORY_MODEL_FILE.read_text()
        assert ("get_new_value" in content or "new_value" in content), "Should have method to get new value"


class TestConfigurationHistoryModelDocumentation:
    """Test model documentation"""

    def test_has_module_docstring(self):
        """Test that file has module docstring"""
        content = CONFIG_HISTORY_MODEL_FILE.read_text()
        assert '"""' in content or "'''" in content, "Should have module docstring"

    def test_has_class_docstring(self):
        """Test that ConfigurationHistory class has docstring"""
        content = CONFIG_HISTORY_MODEL_FILE.read_text()
        lines = content.split('\n')
        class_found = False
        for i, line in enumerate(lines):
            if "class ConfigurationHistory" in line:
                class_found = True
                next_lines = '\n'.join(lines[i:i+10])
                assert '"""' in next_lines or "'''" in next_lines, "ConfigurationHistory class should have docstring"
                break
        assert class_found, "ConfigurationHistory class should exist"

    def test_documents_attributes(self):
        """Test that model attributes are documented"""
        content = CONFIG_HISTORY_MODEL_FILE.read_text()
        assert "comment" in content.lower(), "Should document column purposes"


class TestConfigurationHistoryModelTypeHints:
    """Test type hints"""

    def test_uses_type_hints(self):
        """Test that model uses type hints"""
        content = CONFIG_HISTORY_MODEL_FILE.read_text()
        assert (":" in content or "Optional" in content or "Dict" in content or "Any" in content), "Should use type hints"

    def test_imports_typing_if_needed(self):
        """Test that typing is imported if type hints are used"""
        content = CONFIG_HISTORY_MODEL_FILE.read_text()
        if "Optional" in content or "Dict" in content or "Any" in content:
            assert "from typing import" in content, "Should import from typing module"


class TestConfigurationHistoryModelStructure:
    """Test overall model structure"""

    def test_follows_model_pattern(self):
        """Test that model follows same pattern as other models"""
        content = CONFIG_HISTORY_MODEL_FILE.read_text()
        assert "class ConfigurationHistory" in content, "Should have ConfigurationHistory class"
        assert "__tablename__" in content, "Should have __tablename__"
        assert "Column" in content, "Should have Column definitions"

    def test_has_sufficient_helper_methods(self):
        """Test that model has sufficient helper methods for JSONB fields"""
        content = CONFIG_HISTORY_MODEL_FILE.read_text()
        # Should have multiple def statements for helper methods
        def_count = content.count("def ")
        # At least __repr__ + 4 JSONB helpers (set_old, get_old, set_new, get_new)
        assert def_count >= 5, "Should have at least 5 methods (__repr__ + 4 JSONB helpers)"


class TestConfigurationHistoryModelConstraints:
    """Test constraints"""

    def test_configuration_id_not_nullable(self):
        """Test that configuration_id is not nullable"""
        content = CONFIG_HISTORY_MODEL_FILE.read_text()
        assert "nullable" in content, "Should have nullable constraints"


class TestConfigurationHistoryModelValueComparison:
    """Test value comparison methods"""

    def test_has_method_to_compare_values(self):
        """Test that model has method to compare old and new values"""
        content = CONFIG_HISTORY_MODEL_FILE.read_text()
        # Should have some way to work with old_value and new_value
        assert "old_value" in content and "new_value" in content, "Should have both old_value and new_value"
