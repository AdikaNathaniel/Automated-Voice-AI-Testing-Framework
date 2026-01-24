import os
from types import SimpleNamespace
from uuid import uuid4

import pytest
from unittest.mock import AsyncMock

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/testdb")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-123")
os.environ.setdefault("SOUNDHOUND_API_KEY", "test-key")
os.environ.setdefault("SOUNDHOUND_CLIENT_ID", "test-client")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "test-access-key")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test-secret-key")

from fastapi import HTTPException
from api.schemas.human_validation import HumanValidationSubmit
from api.routes.human_validation import submit_validation_decision


class DummyResult:
    def __init__(self, value):
        self.value = value

    def scalar_one_or_none(self):
        return self.value


class DummyAsyncSession:
    def __init__(self, results):
        self._results = list(results)
        self.added = []
        self.committed = False
        self.refreshed = []

    async def execute(self, stmt):
        value = self._results.pop(0) if self._results else None
        return DummyResult(value)

    def add(self, obj):
        self.added.append(obj)

    async def commit(self):
        self.committed = True

    async def refresh(self, obj):
        self.refreshed.append(obj)



@pytest.mark.asyncio
async def test_submit_validation_decision_calls_service(monkeypatch):
    queue_id = uuid4()
    validator_id = uuid4()
    payload = HumanValidationSubmit(
        validation_decision="fail",
        feedback="Intent mismatch",
        time_spent_seconds=35,
    )
    current_user = SimpleNamespace(id=validator_id, role="admin", tenant_id=None)

    fake_service = SimpleNamespace(
        submit_decision=AsyncMock(
            return_value={
                "queue_id": str(queue_id),
                "validator_id": str(validator_id),
                "decision": "fail",
                "time_spent_seconds": 35,
                "human_validation_id": str(uuid4()),
            }
        )
    )
    monkeypatch.setattr("api.routes.human_validation.HumanValidationService", lambda: fake_service)

    response = await submit_validation_decision(queue_id, payload, object(), current_user)

    fake_service.submit_decision.assert_awaited_once()
    args, kwargs = fake_service.submit_decision.await_args
    assert kwargs["queue_id"] == queue_id
    assert kwargs["validator_id"] == validator_id
    assert response.data["queue_id"] == str(queue_id)


@pytest.mark.asyncio
async def test_submit_validation_decision_rejects_invalid_decision():
    current_user = SimpleNamespace(id=uuid4(), role="admin", tenant_id=None)
    session = DummyAsyncSession([None])
    payload = HumanValidationSubmit(
        validation_decision="invalid",
        feedback=None,
        time_spent_seconds=10,
    )

    with pytest.raises(HTTPException):
        await submit_validation_decision(uuid4(), payload, session, current_user)
