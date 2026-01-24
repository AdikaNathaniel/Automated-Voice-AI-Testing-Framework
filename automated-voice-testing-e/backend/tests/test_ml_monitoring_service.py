"""
Tests for the ML monitoring service which records model predictions against
human validation outcomes.
"""

from __future__ import annotations

from uuid import uuid4

import pytest

from services.ml_monitoring_service import MLMonitoringService


def test_record_prediction_outcome_tracks_prediction_and_actual() -> None:
    service = MLMonitoringService()

    test_run_id = uuid4()
    record = service.record_prediction_outcome(
        model_name="semantic-matcher",
        test_run_id=test_run_id,
        prediction_label="pass",
        human_decision="fail",
        metadata={"confidence": 0.72},
    )

    assert record.model_name == "semantic-matcher"
    assert record.prediction_label == "pass"
    assert record.human_decision == "fail"
    assert record.test_run_id == test_run_id
    assert record.metadata == {"confidence": 0.72}

    history = service.get_prediction_history()
    assert len(history) == 1
    assert history[0] == record

    semantic_history = service.get_prediction_history(model_name="semantic-matcher")
    assert semantic_history == [record]

    other_history = service.get_prediction_history(model_name="intent-classifier")
    assert other_history == []


def test_get_accuracy_summary_returns_match_ratio_per_model() -> None:
    service = MLMonitoringService()

    service.record_prediction_outcome(
        model_name="semantic-matcher",
        test_run_id=uuid4(),
        prediction_label="pass",
        human_decision="pass",
    )
    service.record_prediction_outcome(
        model_name="semantic-matcher",
        test_run_id=uuid4(),
        prediction_label="fail",
        human_decision="pass",
    )
    service.record_prediction_outcome(
        model_name="intent-classifier",
        test_run_id=uuid4(),
        prediction_label="edge_case",
        human_decision="edge_case",
    )

    overall = service.get_accuracy_summary()
    assert overall.total_predictions == 3
    assert overall.matching_predictions == 2
    assert overall.accuracy == pytest.approx(2 / 3)

    semantic = service.get_accuracy_summary(model_name="semantic-matcher")
    assert semantic.total_predictions == 2
    assert semantic.matching_predictions == 1
    assert semantic.accuracy == pytest.approx(0.5)

    missing = service.get_accuracy_summary(model_name="unknown-model")
    assert missing.total_predictions == 0
    assert missing.matching_predictions == 0
    assert missing.accuracy is None
