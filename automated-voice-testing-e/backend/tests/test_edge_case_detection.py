"""
Unit tests for the automatic edge case detection service.

Validates that failure patterns are analysed and converted into EdgeCase
records with the correct categorisation, severity, and scenario metadata.
"""

from __future__ import annotations

from types import SimpleNamespace
from uuid import uuid4
from typing import Any, Dict, List

import pytest

from services.edge_case_detection import EdgeCaseDetectionService


class FakeEdgeCaseService:
    """Simple stand-in that records create_edge_case invocations."""

    def __init__(self) -> None:
        self.calls: List[Dict[str, Any]] = []

    def create_edge_case(self, **kwargs: Any):
        self.calls.append(kwargs)
        return SimpleNamespace(id=uuid4(), **kwargs)


@pytest.fixture()
def detector():
    service = FakeEdgeCaseService()
    detection = EdgeCaseDetectionService(edge_case_service=service)
    return detection, service


def test_detect_timeouts_creates_edge_case(detector):
    detection, service = detector
    test_case_id = uuid4()

    failures = [
        {
            "test_case_id": test_case_id,
            "failure_reason": "Execution timeout after 30s of silence",
            "error_type": "timeout",
            "transcript": "User said 'Navigate home' but no reply",
            "step": "device_response",
            "metadata": {"elapsed_ms": 30000},
        }
    ]

    results = detection.detect_from_failures(
        failures,
        discovered_by=uuid4(),
    )

    assert len(results) == 1
    assert len(service.calls) == 1
    payload = service.calls[0]
    assert payload["category"] == "timeout"
    assert payload["severity"] == "high"
    assert payload["status"] == "active"
    assert "auto-detected" in payload["tags"]
    assert payload["scenario_definition"]["error_type"] == "timeout"
    assert "timeout" in payload["title"].lower()


def test_detect_ambiguity_flags_multiple_matches(detector):
    detection, service = detector
    test_case_id = uuid4()

    failures = [
        {
            "test_case_id": test_case_id,
            "failure_reason": "Assistant returned ambiguous result for 'Play Skyline'",
            "error_type": "assertion_failed",
            "transcript": "Play Skyline",
            "metadata": {"candidates": ["Skyline by Khalid", "Skyline Radio"], "confidence_gap": 0.05},
        }
    ]

    results = detection.detect_from_failures(failures)

    assert len(results) == 1
    payload = service.calls[-1]
    assert payload["category"] == "ambiguity"
    assert payload["severity"] == "medium"
    assert "ambiguity" in payload["tags"]
    assert payload["scenario_definition"]["metadata"]["candidates"] == ["Skyline by Khalid", "Skyline Radio"]


def test_detect_context_loss_uses_signal_metadata(detector):
    detection, service = detector
    test_case_id = uuid4()

    failures = [
        {
            "test_case_id": test_case_id,
            "failure_reason": "Assistant forgot previous step when asked follow-up question",
            "error_type": "context_lost",
            "transcript": "Follow-up question about previous destination",
            "metadata": {"context_shift": True, "turn_index": 4},
        }
    ]

    detection.detect_from_failures(failures, discovered_by=uuid4())

    payload = service.calls[-1]
    assert payload["category"] == "context_loss"
    assert payload["severity"] == "high"
    assert payload["scenario_definition"]["metadata"]["context_shift"] is True


def test_duplicates_are_not_created_for_same_failure_signature(detector):
    detection, service = detector
    test_case_id = uuid4()

    failure = {
        "test_case_id": test_case_id,
        "failure_reason": "Execution timeout after 30s of silence",
        "error_type": "timeout",
        "metadata": {"elapsed_ms": 30000},
    }

    failures = [failure, dict(failure)]
    detection.detect_from_failures(failures)

    assert len(service.calls) == 1, "Duplicate failures should be coalesced into one edge case"
