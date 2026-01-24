"""
Tests for gzip compression middleware (TASK-278).
"""

from __future__ import annotations

import os
from typing import Iterator

import pytest
from fastapi.testclient import TestClient

# Ensure required environment variables exist before importing the app
os.environ.setdefault("DATABASE_URL", "postgresql://user:pass@localhost:5432/testdb")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("JWT_SECRET_KEY", "supersecretkey1234")
os.environ.setdefault("SOUNDHOUND_API_KEY", "test-key")
os.environ.setdefault("SOUNDHOUND_CLIENT_ID", "test-client")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "test-access")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test-secret")

from api.main import app  # noqa: E402


@pytest.fixture()
def client() -> Iterator[TestClient]:
    """
    Provide a TestClient instance for gzip middleware tests.
    """
    with TestClient(app) as test_client:
        yield test_client


def test_health_endpoint_returns_gzip_when_requested(client: TestClient) -> None:
    """
    Ensure responses are gzip-compressed when the client requests it.
    """
    response = client.get("/health", headers={"Accept-Encoding": "gzip"})
    assert response.status_code == 200
    assert response.headers.get("Content-Encoding") == "gzip"
    assert "Accept-Encoding" in (response.headers.get("Vary") or "")

    payload = response.json()
    assert payload["status"] == "healthy"


def test_health_endpoint_plain_response_without_gzip_header(client: TestClient) -> None:
    """
    Ensure responses remain uncompressed when the header is not provided.
    """
    response = client.get("/health", headers={"Accept-Encoding": "identity"})
    assert response.status_code == 200
    assert response.headers.get("Content-Encoding") is None
