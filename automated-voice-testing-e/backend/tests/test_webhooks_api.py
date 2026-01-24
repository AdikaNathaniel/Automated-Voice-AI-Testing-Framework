"""
Webhook receiver API tests (TASK-262).
"""

from __future__ import annotations

from uuid import uuid4
from unittest.mock import AsyncMock

import hmac
import hashlib
import json
import os

import pytest
from fastapi.testclient import TestClient


GITHUB_SECRET = "test-gh-secret"
GITLAB_SECRET = "test-gl-token"
JENKINS_SECRET = "test-jenkins-secret"

# Ensure required environment variables exist before importing the app
os.environ.setdefault("DATABASE_URL", "postgresql://user:pass@localhost:5432/testdb")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("JWT_SECRET_KEY", "supersecretkey1234")
os.environ.setdefault("SOUNDHOUND_API_KEY", "test-key")
os.environ.setdefault("SOUNDHOUND_CLIENT_ID", "test-client")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "test-access")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test-secret")
os.environ.setdefault("GITHUB_WEBHOOK_SECRET", GITHUB_SECRET)
os.environ.setdefault("GITLAB_WEBHOOK_SECRET", GITLAB_SECRET)
os.environ.setdefault("JENKINS_WEBHOOK_SECRET", JENKINS_SECRET)

from api.main import app
from api.database import get_db
from services import webhook_service, orchestration_service


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(autouse=True)
def override_dependencies():
    """
    Webhook endpoints do not require authentication, but the DB dependency must be overridden.
    """

    async def fake_db():
        yield None

    app.dependency_overrides[get_db] = fake_db

    yield

    app.dependency_overrides.clear()


def _payload(**overrides):
    base = {
        "id": str(uuid4()),
        "status": "success",
        "repository": {"name": "voice-ai", "url": "https://example.com/voice-ai.git"},
        "commit": {"sha": "abc123", "message": "Add webhook receiver", "author": "qa-bot"},
    }
    base.update(overrides)
    return base


def test_github_webhook_is_accepted(client: TestClient, monkeypatch):
    mock_dispatch = AsyncMock()
    monkeypatch.setattr(webhook_service, "dispatch_ci_cd_event", mock_dispatch)

    payload = _payload()
    body = json.dumps(payload).encode("utf-8")
    signature = hmac.new(GITHUB_SECRET.encode("utf-8"), body, hashlib.sha256).hexdigest()
    response = client.post(
        "/api/v1/webhooks/ci-cd",
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-GitHub-Event": "push",
            "X-Hub-Signature-256": f"sha256={signature}",
        },
    )

    assert response.status_code == 202
    body = response.json()
    assert body == {"status": "accepted", "provider": "github"}
    mock_dispatch.assert_awaited_once()
    kwargs = mock_dispatch.await_args.kwargs
    assert kwargs["provider"] == "github"
    assert kwargs["event_type"] == "push"
    assert kwargs["payload"] == payload


def test_gitlab_webhook_is_accepted(client: TestClient, monkeypatch):
    mock_dispatch = AsyncMock()
    monkeypatch.setattr(webhook_service, "dispatch_ci_cd_event", mock_dispatch)

    body = json.dumps(_payload(pipeline={"status": "running"})).encode("utf-8")
    response = client.post(
        "/api/v1/webhooks/ci-cd",
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-Gitlab-Event": "Pipeline Hook",
            "X-Gitlab-Token": GITLAB_SECRET,
        },
    )

    assert response.status_code == 202
    assert response.json()["provider"] == "gitlab"
    mock_dispatch.assert_awaited_once()
    kwargs = mock_dispatch.await_args.kwargs
    assert kwargs["provider"] == "gitlab"
    assert kwargs["event_type"] == "Pipeline Hook"


def test_jenkins_webhook_is_accepted(client: TestClient, monkeypatch):
    mock_dispatch = AsyncMock()
    monkeypatch.setattr(webhook_service, "dispatch_ci_cd_event", mock_dispatch)

    payload = _payload(build={"status": "SUCCESS"})
    body = json.dumps(payload).encode("utf-8")
    signature = hmac.new(JENKINS_SECRET.encode("utf-8"), body, hashlib.sha256).hexdigest()
    response = client.post(
        "/api/v1/webhooks/ci-cd",
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-Jenkins-Event": "job_completed",
            "X-Jenkins-Signature": signature,
        },
    )

    assert response.status_code == 202
    assert response.json()["provider"] == "jenkins"
    mock_dispatch.assert_awaited_once()
    kwargs = mock_dispatch.await_args.kwargs
    assert kwargs["provider"] == "jenkins"
    assert kwargs["event_type"] == "job_completed"


def test_unknown_webhook_source_returns_400(client: TestClient, monkeypatch):
    mock_dispatch = AsyncMock()
    monkeypatch.setattr(webhook_service, "dispatch_ci_cd_event", mock_dispatch)

    response = client.post(
        "/api/v1/webhooks/ci-cd",
        data=json.dumps(_payload()).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Unsupported webhook provider"
    mock_dispatch.assert_not_awaited()


def test_github_invalid_signature_returns_401(client: TestClient, monkeypatch):
    mock_dispatch = AsyncMock()
    monkeypatch.setattr(webhook_service, "dispatch_ci_cd_event", mock_dispatch)

    body = json.dumps(_payload()).encode("utf-8")
    response = client.post(
        "/api/v1/webhooks/ci-cd",
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-GitHub-Event": "push",
            "X-Hub-Signature-256": "sha256=deadbeef",
        },
    )

    assert response.status_code == 401
    assert "Invalid" in response.json()["detail"]
    mock_dispatch.assert_not_awaited()


def test_gitlab_missing_token_returns_401(client: TestClient, monkeypatch):
    mock_dispatch = AsyncMock()
    monkeypatch.setattr(webhook_service, "dispatch_ci_cd_event", mock_dispatch)

    response = client.post(
        "/api/v1/webhooks/ci-cd",
        data=json.dumps(_payload()).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "X-Gitlab-Event": "Pipeline Hook",
        },
    )

    assert response.status_code == 401
    assert "Missing" in response.json()["detail"]
    mock_dispatch.assert_not_awaited()


def test_jenkins_signature_missing_returns_401(client: TestClient, monkeypatch):
    mock_dispatch = AsyncMock()
    monkeypatch.setattr(webhook_service, "dispatch_ci_cd_event", mock_dispatch)

    response = client.post(
        "/api/v1/webhooks/ci-cd",
        data=json.dumps(_payload()).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "X-Jenkins-Event": "job_completed",
        },
    )

    assert response.status_code == 401
    assert "Missing" in response.json()["detail"]
    mock_dispatch.assert_not_awaited()


@pytest.mark.parametrize(
    ("provider", "headers_factory", "payload"),
    [
        (
            "github",
            lambda body: {
                "Content-Type": "application/json",
                "X-GitHub-Event": "push",
                "X-Hub-Signature-256": f"sha256={hmac.new(GITHUB_SECRET.encode(), body, hashlib.sha256).hexdigest()}",
            },
            {
                "repository": {"name": "voice-ai", "url": "https://github.com/acme/voice-ai"},
                "ref": "refs/heads/main",
                "after": "abcdef1234567890",
                "head_commit": {
                    "author": {"name": "QA Bot", "email": "qa@example.com"},
                },
            },
        ),
        (
            "gitlab",
            lambda body: {
                "Content-Type": "application/json",
                "X-Gitlab-Event": "Pipeline Hook",
                "X-Gitlab-Token": GITLAB_SECRET,
            },
            {
                "project": {"name": "voice-ai", "web_url": "https://gitlab.example.com/voice-ai"},
                "ref": "refs/heads/release",
                "checkout_sha": "123abc456def",
                "user_name": "CI User",
                "object_attributes": {"source": "pipeline"},
            },
        ),
        (
            "jenkins",
            lambda body: {
                "Content-Type": "application/json",
                "X-Jenkins-Event": "job_completed",
                "X-Jenkins-Signature": hmac.new(JENKINS_SECRET.encode(), body, hashlib.sha256).hexdigest(),
            },
            {
                "name": "voice-ai-pipeline",
                "build": {
                    "full_url": "https://jenkins.example.com/job/voice-ai/42/",
                    "parameters": {"GIT_BRANCH": "feature/voice-ci", "GIT_COMMIT": "fedcba654321"},
                    "scm": {"branch": "feature/voice-ci", "commit": "fedcba654321"},
                },
            },
        ),
    ],
)
def test_webhook_processor_triggers_orchestration(client: TestClient, monkeypatch, provider, headers_factory, payload):
    mock_create_run = AsyncMock(return_value={"id": str(uuid4())})
    monkeypatch.setattr(orchestration_service, "create_test_run", mock_create_run)

    body = json.dumps(payload).encode("utf-8")
    headers = headers_factory(body)

    response = client.post(
        "/api/v1/webhooks/ci-cd",
        data=body,
        headers=headers,
    )

    assert response.status_code == 202
    mock_create_run.assert_awaited_once()
    kwargs = mock_create_run.await_args.kwargs
    assert kwargs["trigger_type"] == "webhook"
    metadata = kwargs["trigger_metadata"]
    assert metadata["provider"] == provider
    assert metadata["commit_sha"]
    assert metadata["branch"]
    assert metadata["source_url"]


def test_config_secret_overrides_environment(monkeypatch, client: TestClient):
    config_secret = "config-secret-123"
    monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", "env-secret")

    monkeypatch.setattr(
        webhook_service,
        "load_integration_config",
        AsyncMock(return_value={"providers": {"github": {"secret": config_secret}}}),
    )

    mock_create_run = AsyncMock(return_value={"id": str(uuid4())})
    monkeypatch.setattr(
        webhook_service.orchestration_service,
        "create_test_run",
        mock_create_run,
    )

    body = json.dumps(_payload()).encode("utf-8")
    signature = hmac.new(config_secret.encode(), body, hashlib.sha256).hexdigest()

    response = client.post(
        "/api/v1/webhooks/ci-cd",
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-GitHub-Event": "push",
            "X-Hub-Signature-256": f"sha256={signature}",
        },
    )

    assert response.status_code == 202
    mock_create_run.assert_awaited_once()


def test_provider_suite_configuration_used(monkeypatch, client: TestClient):
    suite_id = str(uuid4())
    monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", "env-secret")

    monkeypatch.setattr(
        webhook_service,
        "load_integration_config",
        AsyncMock(
            return_value={
                "providers": {"github": {"secret": "env-secret", "suite_id": suite_id}}
            }
        ),
    )

    mock_create_run = AsyncMock(return_value={"id": str(uuid4())})
    monkeypatch.setattr(webhook_service.orchestration_service, "create_test_run", mock_create_run)

    body = json.dumps(_payload()).encode("utf-8")
    signature = hmac.new("env-secret".encode(), body, hashlib.sha256).hexdigest()

    response = client.post(
        "/api/v1/webhooks/ci-cd",
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-GitHub-Event": "push",
            "X-Hub-Signature-256": f"sha256={signature}",
        },
    )

    assert response.status_code == 202
    mock_create_run.assert_awaited_once()
    kwargs = mock_create_run.await_args.kwargs
    assert str(kwargs["suite_id"]) == suite_id
