"""
Configuration tests for automatic regression execution settings (TASK-339).
"""

from __future__ import annotations

from typing import Dict, Any

import pytest

from api.config import Settings


def _minimal_settings_kwargs(**overrides: Any) -> Dict[str, Any]:
    """
    Provide the minimal set of keyword arguments required to instantiate
    the Settings object for tests while allowing overrides.
    """
    base: Dict[str, Any] = {
        "DATABASE_URL": "postgresql://user:pass@localhost:5432/testdb",
        "REDIS_URL": "redis://localhost:6379/0",
        "JWT_SECRET_KEY": "super-secret-key-123",
        "SOUNDHOUND_API_KEY": "test-soundhound-key",
        "SOUNDHOUND_CLIENT_ID": "test-soundhound-client",
        "AWS_ACCESS_KEY_ID": "test-aws-access",
        "AWS_SECRET_ACCESS_KEY": "test-aws-secret",
    }
    base.update(overrides)
    return base


def test_settings_expose_auto_regression_defaults():
    settings = Settings(**_minimal_settings_kwargs())

    assert hasattr(settings, "ENABLE_AUTO_REGRESSION")
    assert settings.ENABLE_AUTO_REGRESSION is False

    assert hasattr(settings, "REGRESSION_SUITE_IDS")
    assert settings.REGRESSION_SUITE_IDS == []


def test_settings_parse_regression_suite_ids_from_env(monkeypatch: pytest.MonkeyPatch):
    env_value = (
        '["8bf8ff5e-4663-4d43-a4f4-c8b0d5eaa7f5", "72a0b559-5570-4baa-a2a8-93821f65416d"]'
    )
    monkeypatch.setenv("REGRESSION_SUITE_IDS", env_value)

    try:
        settings = Settings(**_minimal_settings_kwargs())
    finally:
        monkeypatch.delenv("REGRESSION_SUITE_IDS", raising=False)

    assert settings.REGRESSION_SUITE_IDS == [
        "8bf8ff5e-4663-4d43-a4f4-c8b0d5eaa7f5",
        "72a0b559-5570-4baa-a2a8-93821f65416d",
    ]

    manual_settings = Settings(
        **_minimal_settings_kwargs(REGRESSION_SUITE_IDS="abc123, def456 , ,")
    )
    assert manual_settings.REGRESSION_SUITE_IDS == ["abc123", "def456"]
