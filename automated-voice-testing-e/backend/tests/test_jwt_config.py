"""
Tests for JWT configuration hardening (TODO §5.1).

Ensures tokens are signed with the Settings-derived secret key and respect
configured expiration intervals.
"""

from __future__ import annotations

import importlib
import os
from datetime import timedelta
from uuid import uuid4

import pytest
from jose import JWTError, jwt

from api import config as config_module


_BASE_ENV = {
    "DATABASE_URL": "postgresql://tester:tester@localhost:5432/testdb",
    "REDIS_URL": "redis://localhost:6379/0",
    "JWT_SECRET_KEY": "test-default-secret-1234567890",
    "SOUNDHOUND_API_KEY": "test-soundhound-key",
    "SOUNDHOUND_CLIENT_ID": "test-client-id",
    "AWS_ACCESS_KEY_ID": "AKIAFAKEKEY1234567890",
    "AWS_SECRET_ACCESS_KEY": "fake-aws-secret-1234567890",
}


def _reload_jwt_module(monkeypatch: pytest.MonkeyPatch, extra_env: dict[str, str] | None = None):
    """Reload api.auth.jwt with specific environment overrides."""
    for key, value in _BASE_ENV.items():
        monkeypatch.setenv(key, value)
    if extra_env:
        for key, value in extra_env.items():
            monkeypatch.setenv(key, value)

    config_module.get_settings.cache_clear()

    import api.auth.jwt as jwt_module

    return importlib.reload(jwt_module)


def test_access_tokens_use_settings_secret(monkeypatch: pytest.MonkeyPatch):
    """
    When JWT_SECRET_KEY differs from legacy SECRET_KEY env var, tokens
    should use the value defined in application settings.
    """
    jwt_module = _reload_jwt_module(
        monkeypatch,
        {
            "JWT_SECRET_KEY": "settings-secret-1234567890",
            "SECRET_KEY": "legacy-secret-value",
        },
    )

    token = jwt_module.create_access_token(
        user_id=uuid4(),
        expires_delta=timedelta(minutes=5),
    )
    settings = config_module.get_settings()

    # Should decode successfully with the Settings secret.
    decoded = jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[jwt_module.ALGORITHM],
    )
    assert decoded["sub"]

    # Decoding with the legacy SECRET_KEY must fail when value differs.
    with pytest.raises(JWTError):
        jwt.decode(
            token,
            os.environ["SECRET_KEY"],
            algorithms=[jwt_module.ALGORITHM],
        )


def test_default_pilot_token_ttls(monkeypatch: pytest.MonkeyPatch):
    """Pilot defaults should expire access tokens quickly and refresh tokens within two weeks."""
    for key, value in _BASE_ENV.items():
        monkeypatch.setenv(key, value)

    # Ensure we read defaults (no overrides)
    monkeypatch.delenv("JWT_EXPIRATION_MINUTES", raising=False)
    monkeypatch.delenv("JWT_REFRESH_EXPIRATION_DAYS", raising=False)
    config_module.get_settings.cache_clear()

    settings = config_module.get_settings()
    assert settings.JWT_EXPIRATION_MINUTES == 30
    assert settings.JWT_REFRESH_EXPIRATION_DAYS == 14


def test_placeholder_secret_rejected_outside_dev(monkeypatch: pytest.MonkeyPatch):
    """Production-like environments must not allow placeholder JWT secrets."""
    for key, value in _BASE_ENV.items():
        monkeypatch.setenv(key, value)

    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("JWT_SECRET_KEY", "changeMeSecretValue")

    config_module.get_settings.cache_clear()

    with pytest.raises(ValueError) as excinfo:
        config_module.get_settings()

    assert "JWT_SECRET_KEY must be a unique, non-placeholder value" in str(excinfo.value)


def test_placeholder_secret_allowed_in_dev(monkeypatch: pytest.MonkeyPatch):
    """Development environment can use placeholder secrets for convenience."""
    for key, value in _BASE_ENV.items():
        monkeypatch.setenv(key, value)

    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.setenv("JWT_SECRET_KEY", "changeMeSecretValue")

    config_module.get_settings.cache_clear()

    settings = config_module.get_settings()
    assert settings.JWT_SECRET_KEY == "changeMeSecretValue"
