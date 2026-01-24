"""
Tests for the ML model A/B testing framework.
"""

from __future__ import annotations

import sys
import types

import pytest

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

from ml.ab_testing import (
    ABTestManager,
    ABTestVariant,
)


def test_ab_test_manager_assigns_variants_and_tracks_exposures() -> None:
    manager = ABTestManager()

    manager.create_experiment(
        name="semantic-thresholds",
        variants=[
            ABTestVariant(name="baseline", model_name="semantic_v1", threshold=0.75, weight=1),
            ABTestVariant(name="tuned", model_name="semantic_v2", threshold=0.82, weight=1),
        ],
    )

    assignment_one = manager.assign_variant("semantic-thresholds")
    assignment_two = manager.assign_variant("semantic-thresholds")

    assert assignment_one.name == "baseline"
    assert assignment_two.name == "tuned"

    manager.record_outcome(
        experiment="semantic-thresholds",
        variant=assignment_one.name,
        matched=True,
        accuracy=0.92,
    )
    manager.record_outcome(
        experiment="semantic-thresholds",
        variant=assignment_two.name,
        matched=False,
        accuracy=0.61,
    )

    exposures = manager.get_exposure_counts("semantic-thresholds")
    assert exposures == {"baseline": 1, "tuned": 1}


def test_get_performance_summary_returns_metrics_per_variant() -> None:
    manager = ABTestManager()

    manager.create_experiment(
        name="semantic-thresholds",
        variants=[
            ABTestVariant(name="baseline", model_name="semantic_v1", threshold=0.75, weight=1),
            ABTestVariant(name="tuned", model_name="semantic_v2", threshold=0.82, weight=1),
        ],
    )

    first = manager.assign_variant("semantic-thresholds")
    second = manager.assign_variant("semantic-thresholds")
    third = manager.assign_variant("semantic-thresholds")

    manager.record_outcome(
        experiment="semantic-thresholds",
        variant=first.name,
        matched=True,
        accuracy=0.92,
    )
    manager.record_outcome(
        experiment="semantic-thresholds",
        variant=second.name,
        matched=False,
        accuracy=0.61,
    )
    manager.record_outcome(
        experiment="semantic-thresholds",
        variant=third.name,
        matched=False,
        accuracy=0.55,
    )

    summary = manager.get_performance_summary("semantic-thresholds")

    baseline_metrics = summary.variant_metrics["baseline"]
    assert baseline_metrics.exposures == 2
    assert baseline_metrics.matches == 1
    assert baseline_metrics.match_rate == pytest.approx(0.5)
    assert baseline_metrics.average_accuracy == pytest.approx((0.92 + 0.55) / 2)

    tuned_metrics = summary.variant_metrics["tuned"]
    assert tuned_metrics.exposures == 1
    assert tuned_metrics.matches == 0
    assert tuned_metrics.match_rate == pytest.approx(0.0)
    assert tuned_metrics.average_accuracy == pytest.approx(0.61)

    assert summary.total_exposures == 3
    assert summary.total_matches == 1
    assert summary.overall_match_rate == pytest.approx(1 / 3)
