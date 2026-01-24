"""
Unit tests for configuration validation rules (TASK-251).

These tests define the expected behaviour for configuration schema validation,
ensuring that known configuration keys enforce structured payloads while still
allowing custom configurations to store arbitrary dictionaries.
"""

from __future__ import annotations

import pytest

from services.configuration_validation import (  # type: ignore[attr-defined]
    ConfigurationValidationError,
    validate_configuration_data,
)


def test_validate_smtp_settings_accepts_valid_payload() -> None:
    payload = {
        "host": "smtp.example.com",
        "port": 587,
        "use_tls": True,
        "retries": 3,
    }
    assert validate_configuration_data("smtp.settings", payload) == payload


def test_validate_smtp_settings_rejects_missing_host() -> None:
    with pytest.raises(ConfigurationValidationError) as exc:
        validate_configuration_data("smtp.settings", {"port": 2525})
    assert "smtp.settings" in str(exc.value)
    assert "host" in str(exc.value)


def test_validate_feature_flag_rollout_range() -> None:
    with pytest.raises(ConfigurationValidationError) as exc:
        validate_configuration_data("feature.flag", {"enabled": True, "rollout": 1.5})
    assert "feature.flag" in str(exc.value)
    assert "rollout" in str(exc.value)


def test_validate_unknown_configuration_allows_any_dict() -> None:
    payload = {"arbitrary": "value", "nested": {"example": 1}}
    assert validate_configuration_data("custom.config", payload) == payload
