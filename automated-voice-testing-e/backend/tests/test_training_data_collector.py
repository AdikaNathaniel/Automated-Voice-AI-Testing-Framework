"""
Tests for the training data collector which aggregates human validation
decisions to build datasets for model retraining.
"""

from __future__ import annotations

from uuid import uuid4
from datetime import datetime


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

from ml.training_data_collector import TrainingDataCollector, TrainingDataSample


def test_record_validation_stores_sample() -> None:
    collector = TrainingDataCollector()

    sample = collector.record_validation(
        test_run_id=uuid4(),
        utterance="please approve the refund",
        expected_outcome="approve refund request",
        prediction_label="pass",
        human_decision="fail",
        locale="en-US",
        metadata={"reason": "incorrect amount"},
    )

    assert isinstance(sample, TrainingDataSample)
    assert sample.human_decision == "fail"
    assert sample.locale == "en-US"
    assert sample.metadata == {"reason": "incorrect amount"}

    samples = collector.get_samples()
    assert len(samples) == 1
    stored = samples[0]
    assert stored.test_run_id == sample.test_run_id
    assert stored.utterance == "please approve the refund"
    assert stored.expected_outcome == "approve refund request"
    assert stored.prediction_label == "pass"
    assert stored.human_decision == "fail"
    assert stored.metadata["reason"] == "incorrect amount"


def test_export_dataset_returns_serializable_records() -> None:
    collector = TrainingDataCollector()
    test_run_id = uuid4()

    collector.record_validation(
        test_run_id=test_run_id,
        utterance="set an alarm for tomorrow at 8am",
        expected_outcome="alarm_set",
        prediction_label="pass",
        human_decision="pass",
        locale="en-GB",
        recorded_at=datetime(2024, 5, 21, 12, 0, 0),
        metadata={"duration": 12.5},
    )

    dataset = collector.export_dataset()
    assert len(dataset) == 1
    row = dataset[0]
    assert row["test_run_id"] == str(test_run_id)
    assert row["utterance"] == "set an alarm for tomorrow at 8am"
    assert row["expected_outcome"] == "alarm_set"
    assert row["prediction_label"] == "pass"
    assert row["human_decision"] == "pass"
    assert row["locale"] == "en-GB"
    assert row["recorded_at"] == "2024-05-21T12:00:00+00:00"
    assert row["metadata"] == {"duration": 12.5}
