"""Tests for ValidationResult model structure."""

from sqlalchemy import Boolean, Float, String

from models.validation_result import ValidationResult


def test_validation_result_has_execution_and_expected_columns():
    """Test that ValidationResult has required foreign key columns."""
    table = ValidationResult.__table__
    assert "multi_turn_execution_id" in table.c, "Missing multi_turn_execution_id column"
    assert "expected_outcome_id" in table.c, "Missing expected_outcome_id column"


def test_validation_result_has_indexes_for_fk_columns():
    """Test that foreign key columns are indexed."""
    table = ValidationResult.__table__
    index_names = {index.name for index in table.indexes}
    assert f"ix_{table.name}_multi_turn_execution_id" in index_names
    assert f"ix_{table.name}_expected_outcome_id" in index_names
    assert f"ix_{table.name}_suite_run_id" in index_names


def test_validation_result_has_houndify_columns():
    """Test that ValidationResult has Houndify validation columns."""
    table = ValidationResult.__table__
    expected_columns = {
        "command_kind_match_score": Float,
        "asr_confidence_score": Float,
        "houndify_passed": Boolean,
    }

    for column_name, type_cls in expected_columns.items():
        assert column_name in table.c, f"Missing column {column_name}"
        assert isinstance(table.c[column_name].type, type_cls)


def test_validation_result_has_llm_ensemble_columns():
    """Test that ValidationResult has LLM ensemble validation columns."""
    table = ValidationResult.__table__
    assert "llm_passed" in table.c, "Missing llm_passed column"
    assert "ensemble_result" in table.c, "Missing ensemble_result column"
    assert isinstance(table.c["llm_passed"].type, Boolean)


def test_validation_result_has_decision_columns():
    """Test that ValidationResult has combined decision columns."""
    table = ValidationResult.__table__
    expected_columns = {
        "final_decision": String,
        "review_status": String,
    }

    for column_name, type_cls in expected_columns.items():
        assert column_name in table.c, f"Missing column {column_name}"
        assert isinstance(table.c[column_name].type, type_cls)
