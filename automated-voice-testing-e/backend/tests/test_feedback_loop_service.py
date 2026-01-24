"""
Tests for the feedback loop service ensuring human overrides are captured for
retraining and retraining triggers fire when thresholds are met.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4


import sys
import types

if "sentence_transformers" not in sys.modules:
    sentence_module = types.ModuleType("sentence_transformers")
    sentence_module.SentenceTransformer = object
    sys.modules["sentence_transformers"] = sentence_module

if "spacy" not in sys.modules:
    spacy_module = types.ModuleType("spacy")
    spacy_cli_module = types.ModuleType("spacy.cli")
    spacy_cli_module.download = lambda name: None
    spacy_module.cli = spacy_cli_module
    sys.modules["spacy"] = spacy_module
    sys.modules["spacy.cli"] = spacy_cli_module

if "transformers" not in sys.modules:
    transformers_module = types.ModuleType("transformers")
    transformers_module.pipeline = lambda *args, **kwargs: None
    sys.modules["transformers"] = transformers_module

from ml.training_data_collector import TrainingDataCollector
from services.feedback_loop_service import FeedbackLoopService


def _dt(value: str) -> datetime:
    return datetime.fromisoformat(value).astimezone(timezone.utc)


def test_record_human_feedback_captures_override() -> None:
    collector = TrainingDataCollector()
    service = FeedbackLoopService(
        collector=collector,
        retrain_threshold=3,
    )

    sample = service.record_human_feedback(
        test_run_id=uuid4(),
        utterance="transfer fifty dollars to savings",
        expected_outcome="transfer funds",
        automated_label="pass",
        human_decision="fail",
        locale="en-US",
        feedback="Amount misheard",
        recorded_at=_dt("2024-05-22T10:00:00+00:00"),
    )

    assert sample is not None
    assert sample.human_decision == "fail"
    assert sample.prediction_label == "pass"
    assert sample.metadata["feedback"] == "Amount misheard"
    assert collector.get_samples() == [sample]
    assert service.overrides_since_last_retrain == 1


def test_record_human_feedback_ignores_matching_decisions() -> None:
    collector = TrainingDataCollector()
    service = FeedbackLoopService(collector=collector, retrain_threshold=2)

    sample = service.record_human_feedback(
        test_run_id=uuid4(),
        utterance="what's the weather like tomorrow",
        expected_outcome="weather_forecast",
        automated_label="pass",
        human_decision="pass",
        locale="en-GB",
    )

    assert sample is None
    assert collector.get_samples() == []
    assert service.overrides_since_last_retrain == 0


def test_retraining_trigger_resets_after_marking_complete() -> None:
    collector = TrainingDataCollector()
    service = FeedbackLoopService(collector=collector, retrain_threshold=2)

    service.record_human_feedback(
        test_run_id=uuid4(),
        utterance="play jazz music",
        expected_outcome="play_music",
        automated_label="pass",
        human_decision="fail",
        locale="en-US",
    )
    assert service.should_trigger_retraining() is False

    service.record_human_feedback(
        test_run_id=uuid4(),
        utterance="mute the tv",
        expected_outcome="mute_device",
        automated_label="pass",
        human_decision="fail",
        locale="en-US",
    )
    assert service.should_trigger_retraining() is True
    reset_time = _dt("2024-05-23T09:00:00+00:00")
    service.mark_retraining_complete(timestamp=reset_time)
    assert service.overrides_since_last_retrain == 0
    assert service.should_trigger_retraining() is False
    assert service.last_retrain_at == reset_time
