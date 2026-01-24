import os
import sys
import types
from typing import Dict, Any, List
from uuid import uuid4

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/testdb")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-123")
os.environ.setdefault("SOUNDHOUND_API_KEY", "test-key")
os.environ.setdefault("SOUNDHOUND_CLIENT_ID", "test-client")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "test-access-key")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test-secret-key")

if "sentence_transformers" not in sys.modules:
    sentence_module = types.ModuleType("sentence_transformers")
    sentence_module.SentenceTransformer = object
    sys.modules["sentence_transformers"] = sentence_module

if "spacy" not in sys.modules:
    spacy_module = types.ModuleType("spacy")
    spacy_cli_module = types.ModuleType("spacy.cli")
    spacy_cli_module.download = lambda name: None
    spacy_module.cli = spacy_cli_module
    spacy_module.load = lambda name: None
    sys.modules["spacy"] = spacy_module
    sys.modules["spacy.cli"] = spacy_cli_module

if "transformers" not in sys.modules:
    transformers_module = types.ModuleType("transformers")
    transformers_module.pipeline = lambda *args, **kwargs: None
    sys.modules["transformers"] = transformers_module

import pytest
from unittest.mock import AsyncMock, MagicMock

from services.validation_service import ValidationService
# NOTE: Intent classification is deprecated - Houndify uses CommandKind only
# The import below is kept for backwards compatibility with existing test structure


class DummyExecution:
    def __init__(self, suite_run_id, response_entities):
        self.suite_run_id = suite_run_id
        self._response_entities = response_entities
        self._context = {}

    def get_all_response_entities(self) -> Dict[str, Any]:
        return dict(self._response_entities)

    def get_all_context(self) -> Dict[str, Any]:
        return dict(self._context)


class DummyExpectedOutcome:
    def __init__(self, entities=None, validation_rules=None, description=""):
        self.entities = entities or {}
        self.validation_rules = validation_rules or {}
        self.description = description


class DummyValidationResult:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class FakeSemanticMatcher:
    def __init__(self, score: float):
        self.score = score
        self.calls: List[tuple[str, str]] = []

    def calculate_similarity(self, text1: str, text2: str) -> float:
        self.calls.append((text1, text2))
        return self.score


# NOTE: FakeIntentClassifier removed - intent classification is deprecated
# Houndify uses CommandKind only, not intent


class FakeEntityExtractor:
    def __init__(self, entities: List[Dict[str, Any]]):
        self.entities = entities
        self.calls: List[tuple[str, str | None]] = []

    def extract(self, text: str, *, locale: str | None = None) -> List[Dict[str, Any]]:
        self.calls.append((text, locale))
        return self.entities


@pytest.mark.skip(reason="Legacy ML-based validation removed. ValidationService now uses hybrid approach (Houndify + LLM)")
@pytest.mark.asyncio
async def test_validate_voice_response_uses_ml_scores(monkeypatch):
    """Test that validation uses ML scores correctly.

    DEPRECATED: This test is for the old ML-based validation approach.
    The ValidationService now uses:
    - Houndify deterministic checks (CommandKind, ASR, response patterns)
    - LLM ensemble behavioral evaluation

    Legacy fields (semantic_matcher, entity_extractor) have been removed.
    """
    execution = DummyExecution(
        uuid4(),
        {
            "transcript": "please approve the refund request",
            "locale": "en-US",
            "confidence": 0.6,
        },
    )
    expected = DummyExpectedOutcome(
        entities={
            "destination": "account",
        },
        validation_rules={
            "expected_transcript": "approve the refund request please",
            "required_entities": ["destination"],
        },
        description="Approve refund flow",
    )

    semantic = FakeSemanticMatcher(score=0.8)
    extractor = FakeEntityExtractor(
        [
            {"label": "destination", "text": "account", "start": 7, "end": 14},
        ]
    )

    monkeypatch.setattr("services.validation_service.ValidationResult", DummyValidationResult)

    service = ValidationService(
        semantic_matcher=semantic,
        entity_extractor=extractor,
    )

    monkeypatch.setattr(service, "_fetch_execution", AsyncMock(return_value=execution))
    monkeypatch.setattr(service, "_fetch_expected_outcome", AsyncMock(return_value=expected))

    result = await service.validate_voice_response(uuid4(), uuid4())

    assert semantic.calls == [
        ("please approve the refund request", "approve the refund request please")
    ]
    assert extractor.calls == [("please approve the refund request", "en-US")]

    # NOTE: This test is for legacy ML-based validation which is now deprecated.
    # The assertions below document the OLD behavior - don't un-skip this test.
    assert result.semantic_similarity_score == pytest.approx(0.8)
    assert result.confidence_score == pytest.approx(0.8)


@pytest.mark.skip(reason="Legacy ML-based validation removed. ValidationService now uses hybrid approach (Houndify + LLM)")
@pytest.mark.asyncio
async def test_validate_voice_response_records_metrics(monkeypatch):
    """Test that validation records metrics correctly - DEPRECATED."""
    execution = DummyExecution(
        uuid4(),
        {
            "transcript": "book a table for two",
            "locale": "en-GB",
        },
    )
    expected = DummyExpectedOutcome(
        entities={},
        validation_rules={
            "expected_transcript": "book a table for two",
        },
    )

    semantic = FakeSemanticMatcher(score=0.9)
    extractor = FakeEntityExtractor([])

    metrics_recorder = AsyncMock()
    monkeypatch.setattr("services.validation_service.ValidationResult", DummyValidationResult)

    service = ValidationService(
        semantic_matcher=semantic,
        entity_extractor=extractor,
        metrics_recorder=metrics_recorder,
    )

    execution.get_all_response_entities = lambda: {
        "transcript": "book a table for two",
        "locale": "en-GB",
    }

    monkeypatch.setattr(service, "_fetch_execution", AsyncMock(return_value=execution))
    monkeypatch.setattr(service, "_fetch_expected_outcome", AsyncMock(return_value=expected))

    await service.validate_voice_response(uuid4(), uuid4())

    metrics_recorder.record_execution_metrics.assert_awaited_once()
    args, kwargs = metrics_recorder.record_execution_metrics.await_args
    assert kwargs["execution"] is execution
    # accuracy = semantic*0.6 + entity*0.4 = 0.54 + 0.4 = 0.94
    assert kwargs["validation_result"].accuracy_score == pytest.approx(0.94)


class DummyAsyncResult:
    def __init__(self, value):
        self.value = value

    def scalar_one_or_none(self):
        return self.value


class DummyAsyncSession:
    def __init__(self, result):
        self._result = result
        self.executed = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def execute(self, stmt):
        self.executed = stmt
        return self._result


@pytest.mark.asyncio
async def test_fetch_execution_returns_execution(monkeypatch):
    service = ValidationService()
    execution = MagicMock(response_entities=None)
    result = DummyAsyncResult(execution)
    session = DummyAsyncSession(result)

    monkeypatch.setattr("services.validation_service.get_async_session", lambda: session)
    fetched = await service._fetch_execution(uuid4())

    assert fetched is execution
    assert fetched.response_entities == {}
    assert session.executed is not None


@pytest.mark.asyncio
async def test_fetch_expected_outcome_requires_entities(monkeypatch):
    service = ValidationService()
    outcome = MagicMock(entities=None, validation_rules={"expected_transcript": "hi"})
    session = DummyAsyncSession(DummyAsyncResult(outcome))
    monkeypatch.setattr("services.validation_service.get_async_session", lambda: session)

    with pytest.raises(ValueError):
        await service._fetch_expected_outcome(uuid4())


@pytest.mark.asyncio
async def test_fetch_expected_outcome_returns_when_valid(monkeypatch):
    service = ValidationService()
    outcome = MagicMock(entities={"command_kind": "MusicCommand"}, validation_rules={"expected_transcript": "play music"})
    session = DummyAsyncSession(DummyAsyncResult(outcome))
    monkeypatch.setattr("services.validation_service.get_async_session", lambda: session)

    fetched = await service._fetch_expected_outcome(uuid4())
    assert fetched is outcome


@pytest.mark.skip(reason="Legacy ML-based validation removed. ValidationService now uses hybrid approach (Houndify + LLM)")
@pytest.mark.asyncio
async def test_validate_voice_response_delegates_to_defect_auto_creator(monkeypatch):
    """Validation should forward outcomes to the defect auto-creation helper - DEPRECATED."""
    execution = DummyExecution(
        uuid4(),
        {
            "transcript": "utterly wrong phrase",
            "locale": "en-US",
        },
    )
    expected = DummyExpectedOutcome(
        entities={},
        validation_rules={
            "expected_transcript": "some expected transcript",
        },
    )

    # Low semantic score triggers auto_fail
    semantic = FakeSemanticMatcher(score=0.2)
    extractor = FakeEntityExtractor([])

    metrics_recorder = AsyncMock()
    defect_auto_creator = AsyncMock()
    monkeypatch.setattr("services.validation_service.ValidationResult", DummyValidationResult)

    service = ValidationService(
        semantic_matcher=semantic,
        entity_extractor=extractor,
        metrics_recorder=metrics_recorder,
        defect_auto_creator=defect_auto_creator,
    )

    execution.get_all_response_entities = lambda: {
        "transcript": "utterly wrong phrase",
        "locale": "en-US",
    }

    monkeypatch.setattr(service, "_fetch_execution", AsyncMock(return_value=execution))
    monkeypatch.setattr(service, "_fetch_expected_outcome", AsyncMock(return_value=expected))

    await service.validate_voice_response(uuid4(), uuid4())

    defect_auto_creator.record_validation_outcome.assert_awaited_once()
    kwargs = defect_auto_creator.record_validation_outcome.await_args.kwargs
    assert kwargs["execution"] is execution
    # confidence = semantic = 0.2 -> auto_fail (< 40%)
    assert kwargs["review_status"] == "auto_fail"


@pytest.mark.skip(reason="Legacy ML-based validation removed. ValidationService now uses hybrid approach (Houndify + LLM)")
@pytest.mark.asyncio
async def test_validate_voice_response_handles_entity_mismatch(monkeypatch):
    """Test validation with entity mismatches - DEPRECATED.

    Note: This test is for the old ML-based validation approach.
    The ValidationService now uses Houndify + LLM ensemble.
    """
    execution = DummyExecution(
        uuid4(),
        {
            "transcript": "no action needed for this request",
            "locale": "es-ES",
        },
    )
    expected = DummyExpectedOutcome(
        entities={
            "destination": "account",
            "account_type": "savings",
        },
        validation_rules={
            "expected_transcript": "approve the refund request please",
        },
        description="Approval flow",
    )

    semantic = FakeSemanticMatcher(score=0.3)
    extractor = FakeEntityExtractor(
        [
            {"label": "destination", "text": "account"},
            # account_type entity is missing - partial match
        ]
    )

    monkeypatch.setattr("services.validation_service.ValidationResult", DummyValidationResult)

    service = ValidationService(
        semantic_matcher=semantic,
        entity_extractor=extractor,
    )

    monkeypatch.setattr(service, "_fetch_execution", AsyncMock(return_value=execution))
    monkeypatch.setattr(service, "_fetch_expected_outcome", AsyncMock(return_value=expected))

    result = await service.validate_voice_response(uuid4(), uuid4())

    # NOTE: This test is for legacy ML-based validation which is now deprecated.
    # The assertions below document the OLD behavior - don't un-skip this test.
    assert result.semantic_similarity_score == pytest.approx(0.3)
    assert result.confidence_score == pytest.approx(0.3)
