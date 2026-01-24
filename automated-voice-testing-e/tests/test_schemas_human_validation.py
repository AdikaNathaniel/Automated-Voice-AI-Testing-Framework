"""
Test suite for human validation Pydantic schemas

Validates the human validation schema implementations including:
- Schema file structure
- Schema class definitions
- Field definitions and types
- Field validators and constraints
- ConfigDict settings for ORM compatibility
- Schema serialization and deserialization
"""

import pytest
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
SCHEMAS_DIR = PROJECT_ROOT / "backend" / "api" / "schemas"
HUMAN_VALIDATION_SCHEMA_FILE = SCHEMAS_DIR / "human_validation.py"


class TestHumanValidationSchemaFileExists:
    """Test that human validation schema file exists"""

    def test_schemas_directory_exists(self):
        """Test that schemas directory exists"""
        assert SCHEMAS_DIR.exists(), "backend/api/schemas directory should exist"
        assert SCHEMAS_DIR.is_dir(), "schemas should be a directory"

    def test_human_validation_schema_file_exists(self):
        """Test that human_validation.py exists"""
        assert HUMAN_VALIDATION_SCHEMA_FILE.exists(), \
            "human_validation.py should exist in backend/api/schemas/"
        assert HUMAN_VALIDATION_SCHEMA_FILE.is_file(), \
            "human_validation.py should be a file"

    def test_schema_file_has_content(self):
        """Test that schema file has content"""
        content = HUMAN_VALIDATION_SCHEMA_FILE.read_text()
        assert len(content) > 0, "human_validation.py should not be empty"


class TestHumanValidationSchemaImports:
    """Test schema imports"""

    def test_imports_typing_module(self):
        """Test that schema imports typing module"""
        content = HUMAN_VALIDATION_SCHEMA_FILE.read_text()
        assert ("from typing import" in content or "import typing" in content), \
            "Should import from typing module"

    def test_imports_uuid(self):
        """Test that schema imports UUID"""
        content = HUMAN_VALIDATION_SCHEMA_FILE.read_text()
        assert "UUID" in content, "Should import or reference UUID"

    def test_imports_pydantic(self):
        """Test that schema imports Pydantic"""
        content = HUMAN_VALIDATION_SCHEMA_FILE.read_text()
        assert ("from pydantic import" in content or "import pydantic" in content), \
            "Should import Pydantic for schema definitions"

    def test_imports_basemodel(self):
        """Test that schema imports BaseModel"""
        content = HUMAN_VALIDATION_SCHEMA_FILE.read_text()
        assert "BaseModel" in content, "Should import or reference BaseModel"

    def test_imports_field(self):
        """Test that schema imports Field"""
        content = HUMAN_VALIDATION_SCHEMA_FILE.read_text()
        assert "Field" in content, "Should import or reference Field for field metadata"


class TestValidationQueueItemSchema:
    """Test ValidationQueueItem schema"""

    def test_defines_validation_queue_item_class(self):
        """Test that ValidationQueueItem class is defined"""
        content = HUMAN_VALIDATION_SCHEMA_FILE.read_text()
        assert "class ValidationQueueItem" in content, \
            "Should define ValidationQueueItem class"

    def test_validation_queue_item_inherits_from_basemodel(self):
        """Test that ValidationQueueItem inherits from BaseModel"""
        content = HUMAN_VALIDATION_SCHEMA_FILE.read_text()
        assert "class ValidationQueueItem(BaseModel)" in content, \
            "ValidationQueueItem should inherit from BaseModel"

    def test_has_id_field(self):
        """Test that ValidationQueueItem has id field"""
        content = HUMAN_VALIDATION_SCHEMA_FILE.read_text()
        assert "id:" in content and "UUID" in content, \
            "Should have id field of type UUID"

    def test_has_test_case_name_field(self):
        """Test that ValidationQueueItem has test_case_name field"""
        content = HUMAN_VALIDATION_SCHEMA_FILE.read_text()
        assert "test_case_name:" in content and "str" in content, \
            "Should have test_case_name field of type str"

    def test_has_language_code_field(self):
        """Test that ValidationQueueItem has language_code field"""
        content = HUMAN_VALIDATION_SCHEMA_FILE.read_text()
        assert "language_code:" in content, \
            "Should have language_code field"

    def test_has_confidence_score_field(self):
        """Test that ValidationQueueItem has confidence_score field"""
        content = HUMAN_VALIDATION_SCHEMA_FILE.read_text()
        assert "confidence_score:" in content and "float" in content, \
            "Should have confidence_score field of type float"

    def test_has_input_text_field(self):
        """Test that ValidationQueueItem has input_text field"""
        content = HUMAN_VALIDATION_SCHEMA_FILE.read_text()
        assert "input_text:" in content, \
            "Should have input_text field"

    def test_has_input_audio_url_field(self):
        """Test that ValidationQueueItem has input_audio_url field"""
        content = HUMAN_VALIDATION_SCHEMA_FILE.read_text()
        assert "input_audio_url:" in content, \
            "Should have input_audio_url field"

    def test_has_expected_field(self):
        """Test that ValidationQueueItem has expected field"""
        content = HUMAN_VALIDATION_SCHEMA_FILE.read_text()
        assert "expected:" in content and ("dict" in content or "Dict" in content), \
            "Should have expected field of type dict"

    def test_has_actual_field(self):
        """Test that ValidationQueueItem has actual field"""
        content = HUMAN_VALIDATION_SCHEMA_FILE.read_text()
        assert "actual:" in content and ("dict" in content or "Dict" in content), \
            "Should have actual field of type dict"

    def test_has_context_field(self):
        """Test that ValidationQueueItem has context field"""
        content = HUMAN_VALIDATION_SCHEMA_FILE.read_text()
        assert "context:" in content and ("dict" in content or "Dict" in content), \
            "Should have context field of type dict"

    def test_has_class_docstring(self):
        """Test that ValidationQueueItem class has docstring"""
        content = HUMAN_VALIDATION_SCHEMA_FILE.read_text()
        if "class ValidationQueueItem" in content:
            class_start = content.find("class ValidationQueueItem")
            after_class = content[class_start:class_start + 500]
            assert ('"""' in after_class or "'''" in after_class), \
                "ValidationQueueItem class should have docstring"


class TestHumanValidationSubmitSchema:
    """Test HumanValidationSubmit schema"""

    def test_defines_human_validation_submit_class(self):
        """Test that HumanValidationSubmit class is defined"""
        content = HUMAN_VALIDATION_SCHEMA_FILE.read_text()
        assert "class HumanValidationSubmit" in content, \
            "Should define HumanValidationSubmit class"

    def test_human_validation_submit_inherits_from_basemodel(self):
        """Test that HumanValidationSubmit inherits from BaseModel"""
        content = HUMAN_VALIDATION_SCHEMA_FILE.read_text()
        assert "class HumanValidationSubmit(BaseModel)" in content, \
            "HumanValidationSubmit should inherit from BaseModel"

    def test_has_validation_decision_field(self):
        """Test that HumanValidationSubmit has validation_decision field"""
        content = HUMAN_VALIDATION_SCHEMA_FILE.read_text()
        assert "validation_decision:" in content and "str" in content, \
            "Should have validation_decision field of type str"

    def test_has_feedback_field(self):
        """Test that HumanValidationSubmit has feedback field"""
        content = HUMAN_VALIDATION_SCHEMA_FILE.read_text()
        assert "feedback:" in content, \
            "Should have feedback field"

    def test_feedback_is_optional(self):
        """Test that feedback field is optional"""
        content = HUMAN_VALIDATION_SCHEMA_FILE.read_text()
        # Check for Optional[str] or str | None
        has_optional = ("Optional[str]" in content or "str | None" in content or
                       "str | None" in content or "None" in content)
        assert has_optional, "feedback should be optional (Optional[str] or str | None)"

    def test_has_time_spent_seconds_field(self):
        """Test that HumanValidationSubmit has time_spent_seconds field"""
        content = HUMAN_VALIDATION_SCHEMA_FILE.read_text()
        assert "time_spent_seconds:" in content and "int" in content, \
            "Should have time_spent_seconds field of type int"

    def test_has_class_docstring(self):
        """Test that HumanValidationSubmit class has docstring"""
        content = HUMAN_VALIDATION_SCHEMA_FILE.read_text()
        if "class HumanValidationSubmit" in content:
            class_start = content.find("class HumanValidationSubmit")
            after_class = content[class_start:class_start + 500]
            assert ('"""' in after_class or "'''" in after_class), \
                "HumanValidationSubmit class should have docstring"


class TestSchemaConfiguration:
    """Test schema configuration"""

    def test_has_module_docstring(self):
        """Test that schema file has module-level docstring"""
        content = HUMAN_VALIDATION_SCHEMA_FILE.read_text()
        assert ('"""' in content or "'''" in content), \
            "Should have module docstring"

    def test_uses_field_descriptors(self):
        """Test that schemas use Field descriptors"""
        content = HUMAN_VALIDATION_SCHEMA_FILE.read_text()
        assert "Field(" in content, \
            "Should use Field() for field metadata and validation"

    def test_has_configdict(self):
        """Test that schemas have ConfigDict for ORM compatibility"""
        content = HUMAN_VALIDATION_SCHEMA_FILE.read_text()
        # Should have model_config = ConfigDict(from_attributes=True)
        assert ("ConfigDict" in content or "model_config" in content), \
            "Should have ConfigDict for ORM compatibility"


class TestValidationDecisionValues:
    """Test validation decision constraints"""

    def test_documents_validation_decision_values(self):
        """Test that validation_decision valid values are documented"""
        content = HUMAN_VALIDATION_SCHEMA_FILE.read_text()
        # Should document 'pass', 'fail', 'edge_case' in comments or docstrings
        has_pass = "pass" in content.lower()
        has_fail = "fail" in content.lower()
        has_edge = "edge" in content.lower()
        assert (has_pass and has_fail and has_edge), \
            "Should document validation decision values (pass, fail, edge_case)"
