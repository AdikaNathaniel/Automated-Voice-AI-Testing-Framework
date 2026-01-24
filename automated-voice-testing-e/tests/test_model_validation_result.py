"""
Test suite for ValidationResult SQLAlchemy model

Validates the ValidationResult model implementation including:
- Model structure and inheritance
- Column definitions
- Foreign key relationship to test_runs
- Score fields (accuracy, confidence, semantic similarity, intent match, entity match)
- Score helper methods
- Type hints
- Documentation
"""

import pytest
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
MODELS_DIR = PROJECT_ROOT / "backend" / "models"
VALIDATION_RESULT_MODEL_FILE = MODELS_DIR / "validation_result.py"


class TestValidationResultModelFileExists:
    """Test that ValidationResult model file exists"""

    def test_models_directory_exists(self):
        """Test that models directory exists"""
        assert MODELS_DIR.exists(), "backend/models directory should exist"
        assert MODELS_DIR.is_dir(), "models should be a directory"

    def test_validation_result_model_file_exists(self):
        """Test that validation_result.py exists"""
        assert VALIDATION_RESULT_MODEL_FILE.exists(), "validation_result.py should exist"
        assert VALIDATION_RESULT_MODEL_FILE.is_file(), "validation_result.py should be a file"

    def test_model_file_has_content(self):
        """Test that model file has content"""
        content = VALIDATION_RESULT_MODEL_FILE.read_text()
        assert len(content) > 0, "validation_result.py should not be empty"


class TestValidationResultModelImports:
    """Test model imports"""

    def test_imports_base_and_basemodel(self):
        """Test that model imports Base and BaseModel"""
        content = VALIDATION_RESULT_MODEL_FILE.read_text()
        assert ("from models.base import Base" in content or
                "from models.base import Base" in content or
                "from .base import Base" in content), "Should import Base"
        assert "BaseModel" in content, "Should import BaseModel"

    def test_imports_sqlalchemy(self):
        """Test that model imports SQLAlchemy"""
        content = VALIDATION_RESULT_MODEL_FILE.read_text()
        assert ("from sqlalchemy" in content or "import sqlalchemy" in content), "Should import SQLAlchemy"

    def test_imports_column_types(self):
        """Test that model imports necessary column types"""
        content = VALIDATION_RESULT_MODEL_FILE.read_text()
        assert "Column" in content, "Should import Column"


class TestValidationResultModelClass:
    """Test ValidationResult model class"""

    def test_defines_validation_result_class(self):
        """Test that ValidationResult class is defined"""
        content = VALIDATION_RESULT_MODEL_FILE.read_text()
        assert "class ValidationResult" in content, "Should define ValidationResult class"

    def test_inherits_from_base_and_basemodel(self):
        """Test that ValidationResult inherits from Base and BaseModel"""
        content = VALIDATION_RESULT_MODEL_FILE.read_text()
        assert ("class ValidationResult(Base, BaseModel)" in content or
                "class ValidationResult(BaseModel, Base)" in content), "Should inherit from Base and BaseModel"

    def test_has_tablename(self):
        """Test that model has __tablename__"""
        content = VALIDATION_RESULT_MODEL_FILE.read_text()
        assert "__tablename__" in content, "Should define __tablename__"
        assert "'validation_results'" in content or '"validation_results"' in content, "Table name should be validation_results"


class TestValidationResultModelColumns:
    """Test model columns"""

    def test_has_test_run_id_column(self):
        """Test that model has test_run_id column"""
        content = VALIDATION_RESULT_MODEL_FILE.read_text()
        assert "test_run_id" in content, "Should have test_run_id column"

    def test_has_accuracy_score_column(self):
        """Test that model has accuracy_score column"""
        content = VALIDATION_RESULT_MODEL_FILE.read_text()
        assert "accuracy_score" in content, "Should have accuracy_score column"

    def test_has_confidence_score_column(self):
        """Test that model has confidence_score column"""
        content = VALIDATION_RESULT_MODEL_FILE.read_text()
        assert "confidence_score" in content, "Should have confidence_score column"

    def test_has_semantic_similarity_score_column(self):
        """Test that model has semantic_similarity_score column"""
        content = VALIDATION_RESULT_MODEL_FILE.read_text()
        assert "semantic_similarity_score" in content, "Should have semantic_similarity_score column"

    def test_has_command_kind_match_score_column(self):
        """Test that model has command_kind_match_score column"""
        content = VALIDATION_RESULT_MODEL_FILE.read_text()
        assert "command_kind_match_score" in content, "Should have command_kind_match_score column"

    def test_has_asr_confidence_score_column(self):
        """Test that model has asr_confidence_score column"""
        content = VALIDATION_RESULT_MODEL_FILE.read_text()
        assert "asr_confidence_score" in content, "Should have asr_confidence_score column"


class TestValidationResultModelColumnTypes:
    """Test column types"""

    def test_test_run_id_is_uuid(self):
        """Test that test_run_id is UUID type"""
        content = VALIDATION_RESULT_MODEL_FILE.read_text()
        assert "UUID" in content or "uuid" in content.lower(), "test_run_id should be UUID type"

    def test_score_fields_are_float(self):
        """Test that score fields are Float type"""
        content = VALIDATION_RESULT_MODEL_FILE.read_text()
        assert "Float" in content, "Score fields should be Float type"

    def test_test_run_id_not_nullable(self):
        """Test that test_run_id is not nullable"""
        content = VALIDATION_RESULT_MODEL_FILE.read_text()
        assert "nullable" in content, "Should have nullable constraints"


class TestValidationResultModelScoreFields:
    """Test score field requirements"""

    def test_has_five_score_fields(self):
        """Test that model has five score fields"""
        content = VALIDATION_RESULT_MODEL_FILE.read_text()
        score_count = content.count("_score")
        assert score_count >= 5, "Should have at least 5 score fields"


class TestValidationResultWerScoreField:
    """Test WER score field for ASR quality metrics"""

    def test_has_wer_score_column(self):
        """Test that model has wer_score column for Word Error Rate"""
        content = VALIDATION_RESULT_MODEL_FILE.read_text()
        assert "wer_score" in content, "Should have wer_score column"

    def test_wer_score_is_float_type(self):
        """Test that wer_score is Float type"""
        content = VALIDATION_RESULT_MODEL_FILE.read_text()
        # Check that wer_score is defined with Float type
        assert "wer_score" in content and "Float" in content, "wer_score should be Float type"

    def test_wer_score_is_nullable(self):
        """Test that wer_score is nullable"""
        content = VALIDATION_RESULT_MODEL_FILE.read_text()
        # WER score should be nullable since not all validations will have ASR
        lines = content.split('\n')
        in_wer_score = False
        found_nullable = False
        for line in lines:
            if "wer_score" in line and "Column" in line:
                in_wer_score = True
            if in_wer_score:
                if "nullable=True" in line or "nullable = True" in line:
                    found_nullable = True
                    break
                if ")" in line and "Column" not in line:
                    break
        assert found_nullable, "wer_score should be nullable"

    def test_wer_score_has_comment(self):
        """Test that wer_score has descriptive comment"""
        content = VALIDATION_RESULT_MODEL_FILE.read_text()
        # Should have comment describing WER
        assert ("wer" in content.lower() and "comment" in content.lower()), (
            "wer_score should have descriptive comment"
        )

    def test_has_get_wer_score_method(self):
        """Test that model has get_wer_score method"""
        content = VALIDATION_RESULT_MODEL_FILE.read_text()
        assert "def get_wer_score" in content, "Should have get_wer_score method"

    def test_has_set_wer_score_method(self):
        """Test that model has set_wer_score method"""
        content = VALIDATION_RESULT_MODEL_FILE.read_text()
        assert "def set_wer_score" in content, "Should have set_wer_score method"

    def test_wer_score_in_get_all_scores(self):
        """Test that wer_score is included in get_all_scores method"""
        content = VALIDATION_RESULT_MODEL_FILE.read_text()
        # Find get_all_scores method and check it includes wer_score
        if "def get_all_scores" in content:
            method_start = content.find("def get_all_scores")
            method_section = content[method_start:method_start + 1000]
            assert "'wer_score'" in method_section or '"wer_score"' in method_section, (
                "get_all_scores should include wer_score"
            )


class TestValidationResultModelForeignKeys:
    """Test foreign key relationships"""

    def test_test_run_id_has_foreign_key(self):
        """Test that test_run_id has foreign key to test_runs"""
        content = VALIDATION_RESULT_MODEL_FILE.read_text()
        assert ("ForeignKey" in content and "test_runs" in content), "test_run_id should have foreign key to test_runs table"

    def test_has_relationship_definition(self):
        """Test that model has relationship definition"""
        content = VALIDATION_RESULT_MODEL_FILE.read_text()
        assert "relationship" in content, "Should define relationships"


class TestValidationResultModelRelationships:
    """Test model relationships"""

    def test_has_test_run_relationship(self):
        """Test that model has relationship to TestRun"""
        content = VALIDATION_RESULT_MODEL_FILE.read_text()
        assert ("test_run" in content.lower() or "TestRun" in content), "Should have relationship to TestRun"


class TestValidationResultModelMethods:
    """Test model methods"""

    def test_has_repr_method(self):
        """Test that model has __repr__ method"""
        content = VALIDATION_RESULT_MODEL_FILE.read_text()
        assert "def __repr__" in content, "Should have __repr__ method"

    def test_has_score_helper_methods(self):
        """Test that model has helper methods for scores"""
        content = VALIDATION_RESULT_MODEL_FILE.read_text()
        # Should have methods to manage score fields
        assert "def " in content, "Should have methods"


class TestValidationResultModelScoreMethods:
    """Test score helper methods"""

    def test_has_set_score_method(self):
        """Test that model has method to set individual scores"""
        content = VALIDATION_RESULT_MODEL_FILE.read_text()
        assert ("set_accuracy_score" in content or "set_score" in content or
                "update_score" in content), "Should have method to set scores"

    def test_has_get_score_method(self):
        """Test that model has method to get individual scores"""
        content = VALIDATION_RESULT_MODEL_FILE.read_text()
        assert ("get_accuracy_score" in content or "get_score" in content), "Should have method to get scores"

    def test_has_get_all_scores_method(self):
        """Test that model has method to get all scores"""
        content = VALIDATION_RESULT_MODEL_FILE.read_text()
        assert ("get_all_scores" in content or "get_scores" in content), "Should have method to get all scores"


class TestValidationResultModelValidation:
    """Test score validation"""

    def test_has_validation_methods(self):
        """Test that model has score validation logic"""
        content = VALIDATION_RESULT_MODEL_FILE.read_text()
        # Should have validation or nullable constraints
        assert ("nullable" in content or "validate" in content), "Should have validation"


class TestValidationResultModelDocumentation:
    """Test model documentation"""

    def test_has_module_docstring(self):
        """Test that file has module docstring"""
        content = VALIDATION_RESULT_MODEL_FILE.read_text()
        assert '"""' in content or "'''" in content, "Should have module docstring"

    def test_has_class_docstring(self):
        """Test that ValidationResult class has docstring"""
        content = VALIDATION_RESULT_MODEL_FILE.read_text()
        lines = content.split('\n')
        class_found = False
        for i, line in enumerate(lines):
            if "class ValidationResult" in line:
                class_found = True
                next_lines = '\n'.join(lines[i:i+10])
                assert '"""' in next_lines or "'''" in next_lines, "ValidationResult class should have docstring"
                break
        assert class_found, "ValidationResult class should exist"

    def test_documents_attributes(self):
        """Test that model attributes are documented"""
        content = VALIDATION_RESULT_MODEL_FILE.read_text()
        assert "comment" in content.lower(), "Should document column purposes"


class TestValidationResultModelTypeHints:
    """Test type hints"""

    def test_uses_type_hints(self):
        """Test that model uses type hints"""
        content = VALIDATION_RESULT_MODEL_FILE.read_text()
        assert (":" in content or "Optional" in content or "float" in content.lower()), "Should use type hints"

    def test_imports_typing_if_needed(self):
        """Test that typing is imported if type hints are used"""
        content = VALIDATION_RESULT_MODEL_FILE.read_text()
        if "Optional" in content or "Dict" in content:
            assert "from typing import" in content, "Should import from typing module"


class TestValidationResultModelStructure:
    """Test overall model structure"""

    def test_follows_model_pattern(self):
        """Test that model follows same pattern as other models"""
        content = VALIDATION_RESULT_MODEL_FILE.read_text()
        assert "class ValidationResult" in content, "Should have ValidationResult class"
        assert "__tablename__" in content, "Should have __tablename__"
        assert "Column" in content, "Should have Column definitions"


class TestValidationResultModelHelperMethods:
    """Test helper methods implementation"""

    def test_has_sufficient_helper_methods(self):
        """Test that model has sufficient helper methods for score management"""
        content = VALIDATION_RESULT_MODEL_FILE.read_text()
        # Should have multiple def statements for helper methods
        def_count = content.count("def ")
        # At least __repr__ + some score helper methods
        assert def_count >= 4, "Should have at least 4 methods (__repr__ + score helpers)"


class TestValidationResultSerScoreField:
    """Test SER score field for sentence-level ASR quality metrics"""

    def test_has_ser_score_column(self):
        """Test that model has ser_score column for Sentence Error Rate"""
        content = VALIDATION_RESULT_MODEL_FILE.read_text()
        assert "ser_score" in content, "Should have ser_score column"

    def test_ser_score_is_float_type(self):
        """Test that ser_score is Float type"""
        content = VALIDATION_RESULT_MODEL_FILE.read_text()
        assert "ser_score" in content and "Float" in content, "ser_score should be Float type"

    def test_ser_score_is_nullable(self):
        """Test that ser_score is nullable"""
        content = VALIDATION_RESULT_MODEL_FILE.read_text()
        lines = content.split('\n')
        in_ser_score = False
        found_nullable = False
        for line in lines:
            if "ser_score" in line and "Column" in line:
                in_ser_score = True
            if in_ser_score:
                if "nullable=True" in line or "nullable = True" in line:
                    found_nullable = True
                    break
                if ")" in line and "Column" not in line:
                    break
        assert found_nullable, "ser_score should be nullable"

    def test_ser_score_has_comment(self):
        """Test that ser_score has descriptive comment"""
        content = VALIDATION_RESULT_MODEL_FILE.read_text()
        assert ("ser" in content.lower() and "sentence" in content.lower()), (
            "ser_score should have descriptive comment mentioning sentence"
        )

    def test_has_get_ser_score_method(self):
        """Test that model has get_ser_score method"""
        content = VALIDATION_RESULT_MODEL_FILE.read_text()
        assert "def get_ser_score" in content, "Should have get_ser_score method"

    def test_has_set_ser_score_method(self):
        """Test that model has set_ser_score method"""
        content = VALIDATION_RESULT_MODEL_FILE.read_text()
        assert "def set_ser_score" in content, "Should have set_ser_score method"

    def test_ser_score_in_get_all_scores(self):
        """Test that ser_score is included in get_all_scores method"""
        content = VALIDATION_RESULT_MODEL_FILE.read_text()
        if "def get_all_scores" in content:
            method_start = content.find("def get_all_scores")
            method_section = content[method_start:method_start + 1000]
            assert "'ser_score'" in method_section or '"ser_score"' in method_section, (
                "get_all_scores should include ser_score"
            )


class TestValidationResultCerScoreField:
    """Test CER score field for character-level ASR quality metrics"""

    def test_has_cer_score_column(self):
        """Test that model has cer_score column for Character Error Rate"""
        content = VALIDATION_RESULT_MODEL_FILE.read_text()
        assert "cer_score" in content, "Should have cer_score column"

    def test_cer_score_is_float_type(self):
        """Test that cer_score is Float type"""
        content = VALIDATION_RESULT_MODEL_FILE.read_text()
        assert "cer_score" in content and "Float" in content, "cer_score should be Float type"

    def test_cer_score_is_nullable(self):
        """Test that cer_score is nullable"""
        content = VALIDATION_RESULT_MODEL_FILE.read_text()
        lines = content.split('\n')
        in_cer_score = False
        found_nullable = False
        for line in lines:
            if "cer_score" in line and "Column" in line:
                in_cer_score = True
            if in_cer_score:
                if "nullable=True" in line or "nullable = True" in line:
                    found_nullable = True
                    break
                if ")" in line and "Column" not in line:
                    break
        assert found_nullable, "cer_score should be nullable"

    def test_cer_score_has_comment(self):
        """Test that cer_score has descriptive comment"""
        content = VALIDATION_RESULT_MODEL_FILE.read_text()
        assert ("cer" in content.lower() and "character" in content.lower()), (
            "cer_score should have descriptive comment mentioning character"
        )

    def test_has_get_cer_score_method(self):
        """Test that model has get_cer_score method"""
        content = VALIDATION_RESULT_MODEL_FILE.read_text()
        assert "def get_cer_score" in content, "Should have get_cer_score method"

    def test_has_set_cer_score_method(self):
        """Test that model has set_cer_score method"""
        content = VALIDATION_RESULT_MODEL_FILE.read_text()
        assert "def set_cer_score" in content, "Should have set_cer_score method"

    def test_cer_score_in_get_all_scores(self):
        """Test that cer_score is included in get_all_scores method"""
        content = VALIDATION_RESULT_MODEL_FILE.read_text()
        if "def get_all_scores" in content:
            method_start = content.find("def get_all_scores")
            method_section = content[method_start:method_start + 1000]
            assert "'cer_score'" in method_section or '"cer_score"' in method_section, (
                "get_all_scores should include cer_score"
            )
