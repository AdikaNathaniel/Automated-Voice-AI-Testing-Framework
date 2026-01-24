"""
Pydantic schemas for configuration management API.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _ensure_dict(value: Optional[Any], *, allow_none: bool = True) -> Optional[Dict[str, Any]]:
    """
    Normalise JSON fields to dictionaries.

    Args:
        value: Incoming value to normalise.
        allow_none: Whether None is permitted.

    Returns:
        Parsed dictionary or optional None.
    """
    if value is None:
        return None if allow_none else {}
    if isinstance(value, dict):
        return value
    raise ValueError("Value must be a JSON object (dictionary).")


def _strip_key(value: str) -> str:
    """
    Trim configuration keys and ensure non-empty value.

    Args:
        value: Incoming configuration key.

    Returns:
        Sanitised configuration key.
    """
    stripped = value.strip()
    if not stripped:
        raise ValueError("config_key must not be empty.")
    return stripped


class ConfigurationCreate(BaseModel):
    """Payload for creating a configuration entry."""

    config_key: str = Field(..., min_length=1, max_length=255, description="Unique configuration key.")
    config_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Configuration payload stored as JSON.",
    )
    description: Optional[str] = Field(
        default=None,
        description="Optional human-readable description for this configuration.",
        max_length=1024,
    )
    is_active: bool = Field(default=True, description="Whether the configuration is active.")

    @field_validator("config_key")
    @classmethod
    def _normalise_key(cls, value: str) -> str:
        return _strip_key(value)

    @field_validator("config_data", mode="before")
    @classmethod
    def _normalise_data(cls, value: Any) -> Dict[str, Any]:
        return _ensure_dict(value, allow_none=False)


class ConfigurationUpdate(BaseModel):
    """Payload for updating an existing configuration entry."""

    config_key: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="New configuration key (optional).",
    )
    config_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Updated configuration payload stored as JSON.",
    )
    description: Optional[str] = Field(
        default=None,
        description="Updated human-readable description.",
        max_length=1024,
    )
    is_active: Optional[bool] = Field(default=None, description="Toggle configuration active state.")
    change_reason: Optional[str] = Field(
        default=None,
        description="Reason for the update (recorded in history).",
        max_length=1024,
    )

    @field_validator("config_key", mode="before")
    @classmethod
    def _normalise_optional_key(cls, value: Any) -> Optional[str]:
        if value is None:
            return None
        return _strip_key(value)

    @field_validator("config_data", mode="before")
    @classmethod
    def _normalise_optional_data(cls, value: Any) -> Optional[Dict[str, Any]]:
        return _ensure_dict(value, allow_none=True)


class ConfigurationResponse(BaseModel):
    """Response schema for configuration entries."""

    id: UUID
    config_key: str
    config_data: Dict[str, Any] = Field(default_factory=dict)
    description: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, extra="ignore")

    @field_validator("config_key")
    @classmethod
    def _response_key(cls, value: str) -> str:
        return _strip_key(value)

    @field_validator("config_data", mode="before")
    @classmethod
    def _response_data(cls, value: Any) -> Dict[str, Any]:
        return _ensure_dict(value, allow_none=False)


class ConfigurationListResponse(BaseModel):
    """Paginated listing response for configurations."""

    total: Optional[int] = Field(None, ge=0, description="Total number of configurations matching the query.")
    items: List[ConfigurationResponse]
    next_cursor: Optional[str] = Field(None, description="Cursor to retrieve the next page of results.")
    limit: Optional[int] = Field(None, ge=1, description="Limit applied to the result set.")
    fields: Optional[List[str]] = Field(None, description="Fields requested via the fields query parameter.")


class ConfigurationHistoryEntry(BaseModel):
    """History entry for configuration changes."""

    id: UUID
    configuration_id: UUID
    config_key: Optional[str] = Field(default=None, description="Configuration key at time of change.")
    old_value: Optional[Dict[str, Any]] = Field(default=None, description="Configuration value prior to change.")
    new_value: Dict[str, Any] = Field(..., description="Configuration value after change.")
    changed_by: Optional[UUID] = Field(default=None, description="User who performed the change.")
    change_reason: Optional[str] = Field(default=None, description="Reason provided for the change.")
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, extra="ignore")

    @field_validator("config_key", mode="before")
    @classmethod
    def _history_key(cls, value: Any) -> Optional[str]:
        if value is None:
            return None
        return _strip_key(value)

    @field_validator("old_value", mode="before")
    @classmethod
    def _history_old_value(cls, value: Any) -> Optional[Dict[str, Any]]:
        return _ensure_dict(value, allow_none=True)

    @field_validator("new_value", mode="before")
    @classmethod
    def _history_new_value(cls, value: Any) -> Dict[str, Any]:
        return _ensure_dict(value, allow_none=False)


class ConfigurationHistoryListResponse(BaseModel):
    """Paginated listing response for configuration history entries."""

    total: int = Field(..., ge=0, description="Total number of history entries.")
    items: List[ConfigurationHistoryEntry]
