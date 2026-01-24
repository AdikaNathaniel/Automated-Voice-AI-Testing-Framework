"""
Service layer for managing system configurations.

Provides CRUD helpers, activation toggles, and history/version tracking using
the Configuration and ConfigurationHistory ORM models.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from models.configuration import Configuration
from models.configuration_history import ConfigurationHistory
from services.configuration_validation import (
    ConfigurationValidationError,
    validate_configuration_data,
)


def _normalize_key(config_key: str) -> str:
    """Trim whitespace and ensure configuration keys are not empty."""
    normalized = (config_key or "").strip()
    if not normalized:
        raise ValueError("Configuration key must not be empty.")
    return normalized


def _normalize_data(config_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Ensure configuration data is a dictionary."""
    if config_data is None:
        return {}
    if not isinstance(config_data, dict):
        raise ValueError("config_data must be provided as a dictionary.")
    return deepcopy(config_data)


def _normalize_description(description: Optional[str]) -> Optional[str]:
    if description is None:
        return None
    trimmed = description.strip()
    return trimmed or None


class ConfigurationService:
    """Service encapsulating configuration CRUD and history operations."""

    def __init__(self, session: Session) -> None:
        if session is None:
            raise ValueError("ConfigurationService requires a database session.")
        self.session = session

    # ------------------------------------------------------------------ CRUD --
    def create_configuration(
        self,
        *,
        tenant_id: UUID,
        config_key: str,
        config_data: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
        is_active: bool = True,
        changed_by: Optional[UUID] = None,
        change_reason: Optional[str] = None,
    ) -> Configuration:
        """Create a new configuration entry and record an initial history item."""
        key = _normalize_key(config_key)
        normalized_data = _normalize_data(config_data)
        try:
            validated_data = validate_configuration_data(key, normalized_data)
        except ConfigurationValidationError as exc:
            raise ValueError(str(exc)) from exc

        payload = Configuration(
            tenant_id=tenant_id,
            config_key=key,
            config_data=validated_data,
            description=_normalize_description(description),
            is_active=is_active,
        )

        self.session.add(payload)
        self.session.flush()

        self._record_history(
            configuration=payload,
            old_snapshot=None,
            new_snapshot=self._snapshot(payload),
            changed_by=changed_by,
            change_reason=change_reason or "Created configuration",
        )

        self.session.commit()
        self.session.refresh(payload)
        return payload

    def get_configuration(
        self,
        tenant_id: UUID,
        configuration_id: UUID,
        *,
        include_inactive: bool = False,
    ) -> Optional[Configuration]:
        """Retrieve a configuration by identifier, scoped to tenant."""
        config = self.session.get(Configuration, configuration_id)
        if config is None:
            return None
        # Tenant isolation check
        if config.tenant_id != tenant_id:
            return None
        if not include_inactive and not config.is_active:
            return None
        return config

    def get_configuration_by_key(
        self,
        tenant_id: UUID,
        config_key: str,
        *,
        include_inactive: bool = False,
    ) -> Optional[Configuration]:
        """Retrieve a configuration by its key, scoped to tenant."""
        key = _normalize_key(config_key)
        stmt = select(Configuration).where(
            Configuration.tenant_id == tenant_id,
            Configuration.config_key == key
        )
        if not include_inactive:
            stmt = stmt.where(Configuration.is_active.is_(True))
        result = self.session.execute(stmt)
        return result.scalars().first()

    def list_configurations(
        self,
        tenant_id: UUID,
        *,
        is_active: Optional[bool] = None,
        cursor: Optional[str] = None,
        limit: int = 50,
        fields: Optional[List[str]] = None,  # noqa: ARG002 - reserved for future optimizations
    ) -> Tuple[List[Configuration], Dict[str, Any]]:
        """List configurations optionally filtered by active flag with cursor pagination."""

        # Always filter by tenant_id first
        stmt = select(Configuration).where(Configuration.tenant_id == tenant_id)
        if is_active is not None:
            stmt = stmt.where(Configuration.is_active.is_(bool(is_active)))

        count_query = select(func.count()).select_from(stmt.subquery())
        total = self.session.execute(count_query).scalar() or 0

        ordered_stmt = stmt.order_by(Configuration.config_key.asc())

        if cursor:
            ordered_stmt = ordered_stmt.where(Configuration.config_key > cursor)

        limit = max(1, min(int(limit or 50), 200))
        fetch_limit = limit + 1

        result = self.session.execute(ordered_stmt.limit(fetch_limit))
        items = list(result.scalars())

        next_cursor = None
        if len(items) > limit:
            next_cursor = items[-1].config_key
            items = items[:limit]

        metadata = {
            "total": total,
            "next_cursor": next_cursor,
            "limit": limit,
        }

        return items, metadata

    def update_configuration(
        self,
        *,
        tenant_id: UUID,
        configuration_id: UUID,
        config_key: Optional[str] = None,
        config_data: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
        is_active: Optional[bool] = None,
        changed_by: Optional[UUID] = None,
        change_reason: Optional[str] = None,
    ) -> Configuration:
        """Update configuration metadata and persist history."""
        config = self._get_or_raise(tenant_id, configuration_id)
        old_snapshot = self._snapshot(config)

        target_key = config.config_key
        if config_key is not None:
            target_key = _normalize_key(config_key)

        if config_data is not None:
            normalized_data = _normalize_data(config_data)
            try:
                config.config_data = validate_configuration_data(target_key, normalized_data)
                # Mark JSONB field as modified
                from sqlalchemy.orm.attributes import flag_modified
                flag_modified(config, "config_data")
            except ConfigurationValidationError as exc:
                raise ValueError(str(exc)) from exc

        if config_key is not None:
            config.config_key = target_key

        if description is not None:
            config.description = _normalize_description(description)

        # Revalidate if the key changed but payload was not updated.
        if config_key is not None and config_data is None:
            try:
                validate_configuration_data(config.config_key, config.config_data or {})
            except ConfigurationValidationError as exc:
                raise ValueError(str(exc)) from exc

        if is_active is not None:
            if is_active:
                try:
                    validate_configuration_data(config.config_key, config.config_data or {})
                except ConfigurationValidationError as exc:
                    raise ValueError(str(exc)) from exc
            config.is_active = bool(is_active)

        # Ensure active configurations remain valid after any mutation.
        if config.is_active:
            try:
                validate_configuration_data(config.config_key, config.config_data or {})
            except ConfigurationValidationError as exc:
                raise ValueError(str(exc)) from exc

        self.session.flush()
        new_snapshot = self._snapshot(config)

        if new_snapshot != old_snapshot:
            self._record_history(
                configuration=config,
                old_snapshot=old_snapshot,
                new_snapshot=new_snapshot,
                changed_by=changed_by,
                change_reason=change_reason or "Updated configuration",
            )

        self.session.commit()
        self.session.refresh(config)
        return config

    def set_active_state(
        self,
        *,
        tenant_id: UUID,
        configuration_id: UUID,
        is_active: bool,
        changed_by: Optional[UUID] = None,
        change_reason: Optional[str] = None,
    ) -> Configuration:
        """Enable or disable a configuration."""
        return self.update_configuration(
            tenant_id=tenant_id,
            configuration_id=configuration_id,
            is_active=is_active,
            changed_by=changed_by,
            change_reason=change_reason or ("Activated" if is_active else "Deactivated"),
        )

    def delete_configuration(
        self,
        tenant_id: UUID,
        configuration_id: UUID,
        *,
        changed_by: Optional[UUID] = None,
        change_reason: Optional[str] = None,
    ) -> Configuration:
        """
        Soft-delete a configuration by disabling it and clearing data.

        Maintains a history entry indicating the deletion event.
        """
        config = self._get_or_raise(tenant_id, configuration_id)
        old_snapshot = self._snapshot(config)

        config.is_active = False
        config.config_data = {}
        # Mark JSONB field as modified
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(config, "config_data")
        self.session.flush()
        new_snapshot = self._snapshot(config)

        if new_snapshot != old_snapshot:
            self._record_history(
                configuration=config,
                old_snapshot=old_snapshot,
                new_snapshot=new_snapshot,
                changed_by=changed_by,
                change_reason=change_reason or "Deleted configuration",
            )

        self.session.commit()
        self.session.refresh(config)
        return config

    # -------------------------------------------------------------- HISTORY --
    def list_history(self, tenant_id: UUID, configuration_id: UUID) -> List[ConfigurationHistory]:
        """Return history entries for a configuration ordered by creation time."""
        # Verify configuration belongs to tenant
        config = self._get_or_raise(tenant_id, configuration_id)
        stmt = (
            select(ConfigurationHistory)
            .where(ConfigurationHistory.configuration_id == config.id)
            .order_by(ConfigurationHistory.created_at.asc())
        )
        result = self.session.execute(stmt)
        return list(result.scalars())

    # --------------------------------------------------------------- INTERNAL --
    def _get_or_raise(self, tenant_id: UUID, configuration_id: UUID) -> Configuration:
        config = self.session.get(Configuration, configuration_id)
        if config is None:
            raise ValueError(f"Configuration not found: {configuration_id}")
        # Tenant isolation check
        if config.tenant_id != tenant_id:
            raise ValueError(f"Configuration not found: {configuration_id}")
        return config

    @staticmethod
    def _snapshot(config: Configuration) -> Dict[str, Any]:
        """Produce an immutable snapshot of the configuration state."""
        return {
            "config_key": config.config_key,
            "config_data": deepcopy(config.config_data) if config.config_data else {},
            "description": config.description,
            "is_active": bool(config.is_active),
        }

    def _record_history(
        self,
        *,
        configuration: Configuration,
        old_snapshot: Optional[Dict[str, Any]],
        new_snapshot: Optional[Dict[str, Any]],
        changed_by: Optional[UUID],
        change_reason: Optional[str],
    ) -> None:
        """Persist a history entry capturing configuration changes."""
        history = ConfigurationHistory(
            configuration_id=configuration.id,
            config_key=configuration.config_key,
            old_value=deepcopy(old_snapshot) if old_snapshot is not None else None,
            new_value=deepcopy(new_snapshot) if new_snapshot is not None else None,
            changed_by=changed_by,
            change_reason=change_reason,
        )
        self.session.add(history)
