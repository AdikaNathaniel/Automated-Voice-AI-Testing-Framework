"""
API tests for language statistics endpoint.
"""

from __future__ import annotations

from types import SimpleNamespace
from uuid import uuid4
from unittest.mock import Mock

import os
import pytest
from fastapi.testclient import TestClient

# Minimal settings required to import FastAPI app during tests
os.environ.setdefault("DATABASE_URL", "postgresql://user:pass@localhost:5432/testdb")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("JWT_SECRET_KEY", "supersecretkey1234")
os.environ.setdefault("SOUNDHOUND_API_KEY", "test-key")
os.environ.setdefault("SOUNDHOUND_CLIENT_ID", "test-client")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "test-access")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test-secret")

from api.main import app
from api.database import get_db
from api.dependencies import get_current_user_with_db


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def override_dependencies():
    fake_user = SimpleNamespace(id=uuid4(), email="user@example.com", is_active=True, role="admin", tenant_id=None)
    app.dependency_overrides[get_current_user_with_db] = lambda: fake_user

    async def fake_db():
        yield Mock()

    app.dependency_overrides[get_db] = fake_db

    yield

    app.dependency_overrides.clear()


def test_get_language_statistics(client, monkeypatch):
    expected_stats = [
        {
            "language_code": "en-US",
            "language_name": "English (United States)",
            "native_name": "English",
            "soundhound_model": "en-US-v3.2",
            "coverage": {"test_cases": 12},
            "pass_rate": 0.94,
            "executions": 20,
            "common_issues": [],
        },
        {
            "language_code": "ja-JP",
            "language_name": "Japanese (Japan)",
            "native_name": "日本語",
            "soundhound_model": "ja-JP-v2.4",
            "coverage": {"test_cases": 5},
            "pass_rate": 0.71,
            "executions": 9,
            "common_issues": ["semantic_drift", "intent_mismatch"],
        },
    ]

    mock_service = Mock()
    mock_service.get_language_statistics.return_value = expected_stats

    def fake_service(db):
        return mock_service

    monkeypatch.setattr(
        "api.routes.language_statistics.LanguageStatisticsService",
        fake_service,
    )

    response = client.get("/api/v1/languages/stats")

    assert response.status_code == 200
    data = response.json()
    assert data["total_languages"] == len(expected_stats)
    assert data["languages"] == expected_stats
    mock_service.get_language_statistics.assert_called_once()
