import os
import pytest
from types import SimpleNamespace
from uuid import uuid4
from unittest.mock import AsyncMock

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/testdb")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-123")
os.environ.setdefault("SOUNDHOUND_API_KEY", "test-key")
os.environ.setdefault("SOUNDHOUND_CLIENT_ID", "test-client")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "test-access-key")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test-secret-key")

from api.routes.human_validation import get_validator_statistics


@pytest.mark.asyncio
async def test_get_validator_statistics_returns_payload(monkeypatch):
    current_user = SimpleNamespace(id=uuid4(),
        full_name="QA Validator",
        username="qa.validator",
    )
    fake_payload = {
        "personal": {"completedValidations": 5},
        "leaderboard": [],
        "accuracyTrend": [],
    }
    fake_service = SimpleNamespace(
        build_validator_statistics=AsyncMock(return_value=fake_payload)
    )
    monkeypatch.setattr(
        "api.routes.human_validation.ValidatorStatisticsService",
        lambda: fake_service,
    )

    response = await get_validator_statistics(db=object(), current_user=current_user)

    fake_service.build_validator_statistics.assert_awaited_once()
    assert response.data == fake_payload
