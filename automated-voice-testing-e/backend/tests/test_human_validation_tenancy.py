from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest

from api.routes import human_validation as hv_routes
from api.schemas.auth import UserResponse
from api.schemas.human_validation import HumanValidationSubmit


def _tenant_user() -> UserResponse:
    return UserResponse(
        id=uuid4(),
        email="validator@example.com",
        username="validator",
        full_name="Tenant Validator",
        role="validator",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        tenant_id=uuid4(),
    )


@pytest.mark.asyncio
async def test_get_next_validation_task_passes_tenant(monkeypatch: pytest.MonkeyPatch):
    user = _tenant_user()

    async def fake_get_next(self, db, validator_id, language_code=None, tenant_id=None):
        assert tenant_id == user.tenant_id
        return SimpleNamespace(id=uuid4(),
            validation_result_id=uuid4(),
            priority=1,
            confidence_score=None,
            language_code="en",
            status="pending",
            requires_native_speaker=False,
            created_at=datetime.now(timezone.utc),
        )

    monkeypatch.setattr(
        hv_routes.validation_queue_service.ValidationQueueService,
        "get_next_validation",
        fake_get_next,
    )

    response = await hv_routes.get_next_validation_task(
        db=object(),
        current_user=user,
        language_code=None,
    )
    assert response.model_dump()["data"]["language_code"] == "en"


@pytest.mark.asyncio
async def test_claim_validation_task_passes_tenant(monkeypatch: pytest.MonkeyPatch):
    user = _tenant_user()

    async def fake_claim(self, db, queue_id, validator_id, tenant_id=None):
        assert tenant_id == user.tenant_id
        return True

    monkeypatch.setattr(
        hv_routes.validation_queue_service.ValidationQueueService,
        "claim_validation",
        fake_claim,
    )

    response = await hv_routes.claim_validation_task(
        queue_id=uuid4(),
        db=object(),
        current_user=user,
    )
    assert response.data is not None


@pytest.mark.asyncio
async def test_release_validation_task_passes_tenant(monkeypatch: pytest.MonkeyPatch):
    user = _tenant_user()

    async def fake_release(self, db, queue_id, tenant_id=None):
        assert tenant_id == user.tenant_id
        return True

    monkeypatch.setattr(
        hv_routes.validation_queue_service.ValidationQueueService,
        "release_validation",
        fake_release,
    )

    response = await hv_routes.release_validation_task(
        queue_id=uuid4(),
        db=object(),
        current_user=user,
    )
    assert response.model_dump()["success"] is True


@pytest.mark.asyncio
async def test_submit_validation_decision_passes_tenant(monkeypatch: pytest.MonkeyPatch):
    user = _tenant_user()
    submit_payload = HumanValidationSubmit(
        validation_decision="pass",
        feedback="Looks good",
        time_spent_seconds=10,
    )

    async def fake_submit(self, db, queue_id, validator_id, validation_data, tenant_id=None):
        assert tenant_id == user.tenant_id
        return {"queue_id": str(queue_id)}

    monkeypatch.setattr(
        hv_routes.HumanValidationService,
        "submit_decision",
        fake_submit,
    )

    response = await hv_routes.submit_validation_decision(
        queue_id=uuid4(),
        validation_data=submit_payload,
        db=object(),
        current_user=user,
    )
    assert response.data["queue_id"]


@pytest.mark.asyncio
async def test_queue_stats_passes_tenant(monkeypatch: pytest.MonkeyPatch):
    user = _tenant_user()

    async def fake_stats(self, db, tenant_id=None):
        assert tenant_id == user.tenant_id
        return {"pending_count": 0}

    monkeypatch.setattr(
        hv_routes.validation_queue_service.ValidationQueueService,
        "get_queue_stats",
        fake_stats,
    )

    response = await hv_routes.get_queue_statistics(db=object(), current_user=user)
    assert response.data["pending_count"] == 0
