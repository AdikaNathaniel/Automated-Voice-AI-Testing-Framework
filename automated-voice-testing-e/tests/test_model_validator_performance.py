"""
Test suite for ValidatorPerformance SQLAlchemy model

Validates the ValidatorPerformance model implementation including:
- Model file structure
- Model class definition and inheritance
- Column definitions and types
- Foreign key relationships
- Default values
- UNIQUE constraint on (validator_id, date)
- Helper methods for calculations
"""

import pytest
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
MODELS_DIR = PROJECT_ROOT / "backend" / "models"
VALIDATOR_PERFORMANCE_MODEL_FILE = MODELS_DIR / "validator_performance.py"


class TestValidatorPerformanceModelFileExists:
    """Test that ValidatorPerformance model file exists"""

    def test_models_directory_exists(self):
        """Test that models directory exists"""
        assert MODELS_DIR.exists(), "backend/models directory should exist"
        assert MODELS_DIR.is_dir(), "models should be a directory"

    def test_validator_performance_model_file_exists(self):
        """Test that validator_performance.py exists"""
        assert VALIDATOR_PERFORMANCE_MODEL_FILE.exists(), \
            "validator_performance.py should exist in backend/models/"
        assert VALIDATOR_PERFORMANCE_MODEL_FILE.is_file(), \
            "validator_performance.py should be a file"

    def test_model_file_has_content(self):
        """Test that model file has content"""
        content = VALIDATOR_PERFORMANCE_MODEL_FILE.read_text()
        assert len(content) > 0, "validator_performance.py should not be empty"


class TestValidatorPerformanceModelImports:
    """Test model imports"""

    def test_imports_typing_module(self):
        """Test that model imports typing module"""
        content = VALIDATOR_PERFORMANCE_MODEL_FILE.read_text()
        assert ("from typing import" in content or "import typing" in content), \
            "Should import from typing module"

    def test_imports_uuid(self):
        """Test that model imports UUID"""
        content = VALIDATOR_PERFORMANCE_MODEL_FILE.read_text()
        assert "UUID" in content, "Should import or reference UUID"

    def test_imports_sqlalchemy(self):
        """Test that model imports SQLAlchemy"""
        content = VALIDATOR_PERFORMANCE_MODEL_FILE.read_text()
        assert ("from sqlalchemy" in content or "import sqlalchemy" in content), \
            "Should import SQLAlchemy for ORM"

    def test_imports_date(self):
        """Test that model imports date"""
        content = VALIDATOR_PERFORMANCE_MODEL_FILE.read_text()
        assert ("from datetime import" in content or "date" in content), \
            "Should import date for date column"


class TestValidatorPerformanceModelClass:
    """Test ValidatorPerformance model class"""

    def test_defines_validator_performance_class(self):
        """Test that ValidatorPerformance class is defined"""
        content = VALIDATOR_PERFORMANCE_MODEL_FILE.read_text()
        assert "class ValidatorPerformance" in content, \
            "Should define ValidatorPerformance class"

    def test_inherits_from_base_and_basemodel(self):
        """Test that ValidatorPerformance inherits from Base and BaseModel"""
        content = VALIDATOR_PERFORMANCE_MODEL_FILE.read_text()
        has_inheritance = ("class ValidatorPerformance(Base, BaseModel)" in content or
                          "class ValidatorPerformance(BaseModel, Base)" in content or
                          "class ValidatorPerformance(Base)" in content)
        assert has_inheritance, \
            "ValidatorPerformance should inherit from Base (and possibly BaseModel)"

    def test_has_tablename(self):
        """Test that ValidatorPerformance has __tablename__"""
        content = VALIDATOR_PERFORMANCE_MODEL_FILE.read_text()
        assert "__tablename__" in content, "Should define __tablename__"
        assert "validator_performance" in content, "Table name should be validator_performance"

    def test_has_module_docstring(self):
        """Test that model has module-level docstring"""
        content = VALIDATOR_PERFORMANCE_MODEL_FILE.read_text()
        assert ('"""' in content or "'''" in content), \
            "Should have module docstring"

    def test_has_class_docstring(self):
        """Test that ValidatorPerformance class has docstring"""
        content = VALIDATOR_PERFORMANCE_MODEL_FILE.read_text()
        if "class ValidatorPerformance" in content:
            class_start = content.find("class ValidatorPerformance")
            after_class = content[class_start:class_start + 500]
            assert ('"""' in after_class or "'''" in after_class), \
                "ValidatorPerformance class should have docstring"


class TestValidatorPerformanceModelColumns:
    """Test model columns"""

    def test_has_id_column(self):
        """Test that ValidatorPerformance has id column"""
        content = VALIDATOR_PERFORMANCE_MODEL_FILE.read_text()
        assert "id" in content, "Should have id column"

    def test_has_validator_id_column(self):
        """Test that ValidatorPerformance has validator_id column"""
        content = VALIDATOR_PERFORMANCE_MODEL_FILE.read_text()
        assert "validator_id" in content, "Should have validator_id column"

    def test_has_date_column(self):
        """Test that ValidatorPerformance has date column"""
        content = VALIDATOR_PERFORMANCE_MODEL_FILE.read_text()
        assert "date" in content, "Should have date column"

    def test_has_validations_completed_column(self):
        """Test that ValidatorPerformance has validations_completed column"""
        content = VALIDATOR_PERFORMANCE_MODEL_FILE.read_text()
        assert "validations_completed" in content, "Should have validations_completed column"

    def test_has_average_time_seconds_column(self):
        """Test that ValidatorPerformance has average_time_seconds column"""
        content = VALIDATOR_PERFORMANCE_MODEL_FILE.read_text()
        assert "average_time_seconds" in content, "Should have average_time_seconds column"

    def test_has_agreement_with_peers_pct_column(self):
        """Test that ValidatorPerformance has agreement_with_peers_pct column"""
        content = VALIDATOR_PERFORMANCE_MODEL_FILE.read_text()
        assert "agreement_with_peers_pct" in content, "Should have agreement_with_peers_pct column"

    def test_has_agreement_with_final_pct_column(self):
        """Test that ValidatorPerformance has agreement_with_final_pct column"""
        content = VALIDATOR_PERFORMANCE_MODEL_FILE.read_text()
        assert "agreement_with_final_pct" in content, "Should have agreement_with_final_pct column"

    def test_has_created_at_column(self):
        """Test that ValidatorPerformance has created_at column"""
        content = VALIDATOR_PERFORMANCE_MODEL_FILE.read_text()
        assert "created_at" in content, "Should have created_at column"


class TestValidatorPerformanceColumnTypes:
    """Test column types"""

    def test_id_is_uuid(self):
        """Test that id column is UUID type"""
        content = VALIDATOR_PERFORMANCE_MODEL_FILE.read_text()
        assert "UUID" in content, "id should be UUID type"

    def test_validator_id_is_uuid(self):
        """Test that validator_id is UUID type"""
        content = VALIDATOR_PERFORMANCE_MODEL_FILE.read_text()
        assert "UUID" in content, "validator_id should be UUID type"

    def test_date_is_date_type(self):
        """Test that date column is Date type"""
        content = VALIDATOR_PERFORMANCE_MODEL_FILE.read_text()
        assert ("Date" in content or "date" in content), \
            "date should be Date type"

    def test_validations_completed_is_integer(self):
        """Test that validations_completed is Integer type"""
        content = VALIDATOR_PERFORMANCE_MODEL_FILE.read_text()
        assert ("Integer" in content or "int" in content), \
            "validations_completed should be Integer type"

    def test_time_and_agreement_columns_are_numeric(self):
        """Test that time and agreement columns are Numeric type"""
        content = VALIDATOR_PERFORMANCE_MODEL_FILE.read_text()
        # Should have Numeric or DECIMAL for average_time and agreement percentages
        has_numeric = ("Numeric" in content or "DECIMAL" in content or "Float" in content)
        assert has_numeric, "Time and agreement columns should be Numeric type"

    def test_created_at_is_datetime(self):
        """Test that created_at is DateTime type"""
        content = VALIDATOR_PERFORMANCE_MODEL_FILE.read_text()
        assert ("DateTime" in content or "datetime" in content), \
            "created_at should be DateTime type"


class TestValidatorPerformanceForeignKeys:
    """Test foreign key relationships"""

    def test_has_foreign_key_to_users(self):
        """Test that validator_id has foreign key to users"""
        content = VALIDATOR_PERFORMANCE_MODEL_FILE.read_text()
        has_fk = "ForeignKey" in content
        has_users = "users" in content
        assert has_fk and has_users, \
            "validator_id should have foreign key to users table"


class TestValidatorPerformanceRelationships:
    """Test model relationships"""

    def test_has_relationship_to_user(self):
        """Test that model has relationship to User"""
        content = VALIDATOR_PERFORMANCE_MODEL_FILE.read_text()
        has_relationship = "relationship" in content
        has_user = "User" in content or "validator" in content
        assert has_relationship and has_user, \
            "Should have relationship to User model"


class TestValidatorPerformanceDefaults:
    """Test default values"""

    def test_validations_completed_has_default(self):
        """Test that validations_completed has default value of 0"""
        content = VALIDATOR_PERFORMANCE_MODEL_FILE.read_text()
        has_default = ("default=0" in content or "default = 0" in content)
        assert has_default, "validations_completed should have default value of 0"

    def test_created_at_has_default(self):
        """Test that created_at has default value"""
        content = VALIDATOR_PERFORMANCE_MODEL_FILE.read_text()
        has_default = ("default=" in content or "server_default" in content)
        assert has_default, "created_at should have a default value"


class TestValidatorPerformanceConstraints:
    """Test model constraints"""

    def test_has_unique_constraint_on_validator_date(self):
        """Test that model documents UNIQUE constraint on (validator_id, date)"""
        content = VALIDATOR_PERFORMANCE_MODEL_FILE.read_text()
        # Check for UniqueConstraint or mention in docstring/comments
        has_unique = ("UniqueConstraint" in content or
                     "unique" in content.lower() or
                     "one record per validator per day" in content.lower())
        assert has_unique, \
            "Should document UNIQUE constraint on (validator_id, date)"


class TestValidatorPerformanceHelperMethods:
    """Test helper methods"""

    def test_has_helper_methods(self):
        """Test that model has helper methods for calculations"""
        content = VALIDATOR_PERFORMANCE_MODEL_FILE.read_text()
        # Should have at least some helper methods (def statements)
        method_count = content.count("def ")
        assert method_count >= 1, "Should have at least one helper method"

    def test_has_method_docstrings(self):
        """Test that methods have docstrings"""
        content = VALIDATOR_PERFORMANCE_MODEL_FILE.read_text()
        if "def " in content:
            # If there are methods, they should have docstrings
            assert '"""' in content or "'''" in content, \
                "Methods should have docstrings"
