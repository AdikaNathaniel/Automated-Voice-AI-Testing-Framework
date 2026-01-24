import os
import pytest
from types import SimpleNamespace
from uuid import uuid4

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/testdb")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-123")
os.environ.setdefault("SOUNDHOUND_API_KEY", "test-key")
os.environ.setdefault("SOUNDHOUND_CLIENT_ID", "test-client")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "test-access-key")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test-secret-key")

from services.validation_service import ValidationService


class DummyResult:
    def __init__(self, value):
        self._value = value

    def scalar_one_or_none(self):
        return self._value


class DummyAsyncSession:
    def __init__(self, result):
        self._result = result
        self.executed = []

    async def execute(self, stmt):
        self.executed.append(stmt)
        return self._result


class DummySessionContext:
    def __init__(self, session):
        self.session = session

    async def __aenter__(self):
        return self.session

    async def __aexit__(self, exc_type, exc, tb):
        return False


@pytest.mark.asyncio
async def test_fetch_execution_defaults_response_entities(monkeypatch):
    execution_id = uuid4()
    execution = SimpleNamespace(id=execution_id,
        test_run_id=uuid4(),
        response_entities=None,
    )
    dummy_session = DummyAsyncSession(DummyResult(execution))

    monkeypatch.setattr(
        "services.validation_service.get_async_session",
        lambda: DummySessionContext(dummy_session),
    )

    service = ValidationService()
    loaded = await service._fetch_execution(execution_id)

    assert loaded is execution
    assert loaded.response_entities == {}
    assert dummy_session.executed, "Expected SELECT to be executed"


@pytest.mark.asyncio
async def test_fetch_expected_outcome_requires_entities_and_rules(monkeypatch):
    outcome_id = uuid4()
    empty_outcome = SimpleNamespace(id=outcome_id,
        entities=None,
        validation_rules=None, role="admin", tenant_id=None)
    dummy_session = DummyAsyncSession(DummyResult(empty_outcome))
    monkeypatch.setattr(
        "services.validation_service.get_async_session",
        lambda: DummySessionContext(dummy_session),
    )

    service = ValidationService()
    with pytest.raises(ValueError, match="validation_rules"):
        await service._fetch_expected_outcome(outcome_id)


@pytest.mark.asyncio
async def test_fetch_expected_outcome_returns_record(monkeypatch):
    outcome_id = uuid4()
    outcome = SimpleNamespace(id=outcome_id,
        entities={"intent": "book"},
        validation_rules={"expected_transcript": "book a ride"}, role="admin", tenant_id=None)
    dummy_session = DummyAsyncSession(DummyResult(outcome))
    monkeypatch.setattr(
        "services.validation_service.get_async_session",
        lambda: DummySessionContext(dummy_session),
    )

    service = ValidationService()
    loaded = await service._fetch_expected_outcome(outcome_id)

    assert loaded is outcome
