"""
Tests for the model versioning service that tracks model lifecycle and supports rollback.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

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

from services.model_registry_service import (
    ModelRegistryService,
    ModelVersion,
)
from ml import ABTestManager


def _timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value).astimezone(timezone.utc)


def test_register_model_version_creates_and_activates_entry() -> None:
    service = ModelRegistryService()

    version = service.register_model_version(
        model_name="semantic-matcher",
        version_tag="1.0.0",
        artifact_uri="s3://models/semantic/1.0.0",
        metadata={"threshold": 0.8},
        registered_at=_timestamp("2024-05-20T08:00:00+00:00"),
    )

    assert isinstance(version, ModelVersion)
    assert version.model_name == "semantic-matcher"
    assert version.version_tag == "1.0.0"
    assert version.is_active is True
    assert service.get_active_version("semantic-matcher") == version
    history = service.get_version_history("semantic-matcher")
    assert history == [version]


def test_registering_new_active_version_deactivates_previous() -> None:
    service = ModelRegistryService()

    first = service.register_model_version(
        model_name="intent-classifier",
        version_tag="1.0.0",
        artifact_uri="s3://models/intent/1.0.0",
        metadata={"labels": 12},
    )

    second = service.register_model_version(
        model_name="intent-classifier",
        version_tag="1.1.0",
        artifact_uri="s3://models/intent/1.1.0",
        metadata={"labels": 18},
    )

    assert first.is_active is False
    assert second.is_active is True
    assert service.get_active_version("intent-classifier") == second
    history = service.get_version_history("intent-classifier")
    assert history == [first, second]


def test_rollback_to_previous_version_reactivates_last_entry() -> None:
    service = ModelRegistryService()

    v1 = service.register_model_version(
        model_name="semantic-matcher",
        version_tag="1.0.0",
        artifact_uri="s3://models/semantic/1.0.0",
    )
    v2 = service.register_model_version(
        model_name="semantic-matcher",
        version_tag="1.1.0",
        artifact_uri="s3://models/semantic/1.1.0",
    )

    assert service.rollback_model("semantic-matcher") == v1
    assert v1.is_active is True
    assert v2.is_active is False
    assert service.get_active_version("semantic-matcher") == v1


def test_launch_ab_test_creates_experiment_with_active_and_candidate_versions() -> None:
    ab_manager = ABTestManager()
    service = ModelRegistryService(ab_manager=ab_manager)

    service.register_model_version(
        model_name="semantic-matcher",
        version_tag="1.0.0",
        artifact_uri="s3://models/semantic/1.0.0",
    )
    service.register_model_version(
        model_name="semantic-matcher",
        version_tag="1.1.0",
        artifact_uri="s3://models/semantic/1.1.0",
        activate=False,
    )

    experiment = service.launch_ab_test(
        model_name="semantic-matcher",
        candidate_version="1.1.0",
        baseline_weight=2,
        candidate_weight=1,
    )

    assert experiment == "semantic-matcher-ab-test"

    baseline_assignment = ab_manager.assign_variant(experiment)
    second_assignment = ab_manager.assign_variant(experiment)
    candidate_assignment = ab_manager.assign_variant(experiment)
    assert {baseline_assignment.name, second_assignment.name, candidate_assignment.name} == {"baseline", "candidate"}

    service.record_ab_test_outcome(
        experiment=experiment,
        variant=baseline_assignment.name,
        matched=True,
        accuracy=0.91,
    )
    service.record_ab_test_outcome(
        experiment=experiment,
        variant=candidate_assignment.name,
        matched=False,
        accuracy=0.72,
    )

    summary = ab_manager.get_performance_summary(experiment)
    assert summary.total_exposures == 3
    assert summary.variant_metrics["baseline"].matches == 1
    assert summary.variant_metrics["candidate"].matches == 0


def test_launch_ab_test_requires_registered_candidate_version() -> None:
    service = ModelRegistryService(ab_manager=ABTestManager())
    service.register_model_version(
        model_name="semantic-matcher",
        version_tag="1.0.0",
        artifact_uri="s3://models/semantic/1.0.0",
    )

    with pytest.raises(ValueError, match="Candidate version not found"):
        service.launch_ab_test(
            model_name="semantic-matcher",
            candidate_version="1.1.0",
        )
