"""Tests for automatic defect categorization heuristics."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

import pytest

from services.defect_categorizer import DefectCategorizer


@dataclass
class DummyExecution:
    """Minimal execution stand-in for categorizer tests."""
    response_entities: Dict[str, Any] = field(default_factory=dict)
    audio_params: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)

    def get_all_response_entities(self) -> Dict[str, Any]:
        return dict(self.response_entities)

    def get_audio_param(self, key: str) -> Optional[Any]:
        return self.audio_params.get(key)

    def get_all_context(self) -> Dict[str, Any]:
        return dict(self.context)


@dataclass
class DummyValidationResult:
    """Minimal validation result stand-in for categorizer tests."""
    command_kind_match_score: Optional[float] = None


@pytest.fixture()
def categorizer() -> DefectCategorizer:
    return DefectCategorizer()


def test_categorizer_flags_command_kind_mismatch(categorizer: DefectCategorizer):
    """Test that low command_kind_match_score is detected as command_mismatch."""
    execution = DummyExecution()
    validation = DummyValidationResult(command_kind_match_score=0.0)

    category = categorizer.categorize(execution=execution, validation_result=validation)

    assert category == "command_mismatch"


def test_categorizer_detects_timing_issue_from_context(categorizer: DefectCategorizer):
    """Test that high response time is detected as timing issue."""
    execution = DummyExecution(context={"response_time_ms": 4200})
    validation = DummyValidationResult(command_kind_match_score=1.0)

    category = categorizer.categorize(execution=execution, validation_result=validation)

    assert category == "timing"


def test_categorizer_detects_audio_issue(categorizer: DefectCategorizer):
    """Test that audio errors in context are detected."""
    execution = DummyExecution(
        audio_params={"language_code": "en-US"},
        context={"audio_error": "microphone_disconnected"},
    )
    validation = DummyValidationResult(command_kind_match_score=1.0)

    category = categorizer.categorize(execution=execution, validation_result=validation)

    assert category == "audio"


def test_categorizer_detects_integration_issue(categorizer: DefectCategorizer):
    """Test that integration errors are detected."""
    execution = DummyExecution(
        context={
            "integration_error": "service_unavailable",
            "http_status": 503,
        }
    )
    validation = DummyValidationResult(command_kind_match_score=1.0)

    category = categorizer.categorize(execution=execution, validation_result=validation)

    assert category == "integration"


def test_categorizer_defaults_to_edge_case(categorizer: DefectCategorizer):
    """Test that when no specific issue is found, category defaults to edge_case."""
    execution = DummyExecution()
    validation = DummyValidationResult(command_kind_match_score=1.0)

    category = categorizer.categorize(execution=execution, validation_result=validation)

    assert category == "edge_case"
