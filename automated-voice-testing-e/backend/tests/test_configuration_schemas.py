"""
Test suite for configuration API schemas.

Validates that the Pydantic models used by the configuration API enforce the
expected constraints, apply basic normalization, and support ORM integration.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

import pytest
from pydantic import ValidationError

from api.schemas.configuration import (
    ConfigurationCreate,
    ConfigurationUpdate,
    ConfigurationResponse,
    ConfigurationListResponse,
    ConfigurationHistoryEntry,
    ConfigurationHistoryListResponse,
)


class DummyConfig:
    """Simple stand-in object for ORM validation."""

    def __init__(self, **kwargs: Any) -> None:
        self.__dict__.update(kwargs)


def test_configuration_create_strips_and_validates_key() -> None:
    """ConfigurationCreate should strip whitespace and require non-empty key."""
    payload = ConfigurationCreate(config_key="  smtp_settings  ")
    assert payload.config_key == "smtp_settings"
    assert payload.config_data == {}

    with pytest.raises(ValidationError):
        ConfigurationCreate(config_key="   ", config_data={})


def test_configuration_create_accepts_json_payload() -> None:
    """ConfigurationCreate should accept arbitrary JSON-compatible payloads."""
    payload = ConfigurationCreate(
        config_key="notifications",
        config_data={"enabled": True, "threshold": 0.85, "targets": ["ops@example.com"]},
    )
    assert payload.config_data["enabled"] is True
    assert payload.config_data["threshold"] == pytest.approx(0.85)
    assert payload.config_data["targets"] == ["ops@example.com"]


def test_configuration_update_allows_partial_updates() -> None:
    """ConfigurationUpdate should allow partial payloads with validation."""
    update = ConfigurationUpdate(
        config_data={"max_retries": 5},
        change_reason="increase resiliency",
    )
    assert update.config_data == {"max_retries": 5}
    assert update.change_reason == "increase resiliency"


def test_configuration_response_handles_none_config_data() -> None:
    """ConfigurationResponse should normalise None config_data to empty dict."""
    now = datetime.now(timezone.utc)
    orm_obj = DummyConfig(
        id=uuid4(),
        config_key="voice_gateway",
        config_data=None,
        created_at=now,
        updated_at=now,
        description="Voice gateway routing preferences",
        is_active=True,
    )

    response = ConfigurationResponse.model_validate(orm_obj)
    assert response.config_key == "voice_gateway"
    assert response.config_data == {}
    assert response.created_at == now
    assert response.updated_at == now
    assert response.description == "Voice gateway routing preferences"
    assert response.is_active is True


def test_configuration_list_response_encapsulates_items() -> None:
    """ConfigurationListResponse should expose total count and items."""
    now = datetime.now(timezone.utc)
    item = ConfigurationResponse(
        id=uuid4(),
        config_key="api_limits",
        config_data={"burst": 50},
        created_at=now,
        updated_at=now,
        description=None,
        is_active=False,
    )
    listing = ConfigurationListResponse(total=1, items=[item])
    assert listing.total == 1
    assert listing.items[0].config_key == "api_limits"


def test_configuration_history_entry_requires_new_value_dict() -> None:
    """ConfigurationHistoryEntry should require new_value to be a dictionary."""
    now = datetime.now(timezone.utc)
    history = ConfigurationHistoryEntry(
        id=uuid4(),
        configuration_id=uuid4(),
        config_key="notifications",
        old_value={"enabled": False},
        new_value={"enabled": True},
        changed_by=None,
        change_reason="Enabled post-incident review",
        created_at=now,
    )
    assert history.new_value["enabled"] is True
    assert history.change_reason == "Enabled post-incident review"
    assert history.created_at == now

    with pytest.raises(ValidationError):
        ConfigurationHistoryEntry(
            id=uuid4(),
            configuration_id=uuid4(),
            config_key="notifications",
            old_value={"enabled": False},
            new_value="not-a-dict",  # type: ignore[arg-type]
            changed_by=None,
            created_at=now,
        )


def test_configuration_history_list_response_wraps_entries() -> None:
    """ConfigurationHistoryListResponse should aggregate history entries."""
    now = datetime.now(timezone.utc)
    entry = ConfigurationHistoryEntry(
        id=uuid4(),
        configuration_id=uuid4(),
        config_key="queue",
        old_value=None,
        new_value={"size": 10},
        changed_by=uuid4(),
        change_reason=None,
        created_at=now,
    )
    wrapped = ConfigurationHistoryListResponse(total=1, items=[entry])
    assert wrapped.total == 1
    assert wrapped.items[0].config_key == "queue"
