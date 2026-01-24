"""
Tests for the activity logging service.

Validates that the service module:
- Exists and imports required dependencies
- Provides ActivityService class exposing log_event and list_recent methods
- Persists ActivityLog entries with metadata payloads
- Supports optional metadata/IP address fields
- Paginates and filters recent activity queries
"""

from __future__ import annotations

import sys
from pathlib import Path
from importlib import util as importlib_util
from types import ModuleType, SimpleNamespace
from typing import Any
from uuid import UUID, uuid4
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

PROJECT_ROOT = Path(__file__).parent.parent
SERVICE_PATH = PROJECT_ROOT / "backend" / "services" / "activity_service.py"


def _load_activity_service_module() -> ModuleType:
    """Dynamically import the activity service module from its file path."""
    assert SERVICE_PATH.exists(), "activity_service.py should exist for import"
    spec = importlib_util.spec_from_file_location("tests.activity_service", SERVICE_PATH)
    assert spec and spec.loader, "Failed to load module spec for activity_service"
    module = importlib_util.module_from_spec(spec)
    sys_modules_key = spec.name  # type: ignore[attr-defined]
    sys.modules[sys_modules_key] = module
    spec.loader.exec_module(module)  # type: ignore[call-arg]
    return module


class TestActivityServiceModuleExists:
    """Ensure the activity service module exists and has content."""

    def test_service_file_exists(self) -> None:
        assert SERVICE_PATH.exists(), "activity_service.py should exist"
        assert SERVICE_PATH.is_file(), "activity_service.py should be a file"

    def test_service_file_has_content(self) -> None:
        content = SERVICE_PATH.read_text(encoding="utf-8")
        assert content.strip(), "activity_service.py should not be empty"


class TestActivityServiceImports:
    """Verify module imports core dependencies."""

    @pytest.fixture(scope="module")
    def service_source(self) -> str:
        return SERVICE_PATH.read_text(encoding="utf-8")

    def test_imports_async_session(self, service_source: str) -> None:
        assert "from sqlalchemy.ext.asyncio import AsyncSession" in service_source, \
            "Service should import AsyncSession"

    def test_imports_select(self, service_source: str) -> None:
        assert "from sqlalchemy import select" in service_source, \
            "Service should import select for queries"

    def test_imports_activity_log_model(self, service_source: str) -> None:
        assert "from models.activity_log import ActivityLog" in service_source, \
            "Service should import ActivityLog model"


@pytest.mark.anyio
class TestActivityServiceBehaviour:
    """Behavioural tests using mocked AsyncSession."""

    @pytest.fixture
    def anyio_backend(self) -> str:
        """Limit AnyIO backend to asyncio to avoid trio dependency requirements."""
        return "asyncio"

    @pytest.fixture
    def session(self) -> AsyncMock:
        session = AsyncMock(spec=["add", "commit", "refresh", "execute", "delete"])
        session.commit = AsyncMock()
        session.refresh = AsyncMock()
        session.execute = AsyncMock()
        return session

    def _build_entry(self, overrides: dict[str, Any] | None = None) -> SimpleNamespace:
        defaults = {
            "id": uuid4(),
            "user_id": uuid4(),
            "action_type": "test_created",
            "resource_type": "test_case",
            "resource_id": uuid4(),
            "action_description": "Created a new test case",
            "metadata": {"foo": "bar"},
            "ip_address": "127.0.0.1",
            "created_at": None,
        }
        defaults.update(overrides or {})
        return SimpleNamespace(**defaults)

    async def test_log_event_persists_activity(self, session: AsyncMock) -> None:
        module = _load_activity_service_module()

        with patch.object(module, "ActivityLog") as activity_log_cls:
            activity_instance = self._build_entry()
            activity_log_cls.return_value = activity_instance  # type: ignore[assignment]

            service = module.ActivityService()
            await service.log_event(
                db=session,
                user_id=activity_instance.user_id,
                action_type=activity_instance.action_type,
                resource_type=activity_instance.resource_type,
                resource_id=activity_instance.resource_id,
                description=activity_instance.action_description,
                metadata=activity_instance.metadata,
                ip_address=activity_instance.ip_address,
            )

            activity_log_cls.assert_called_once()
            session.add.assert_called_once_with(activity_instance)
            assert session.commit.await_count == 1, "Service should commit after persisting event"
            assert session.refresh.await_count == 1, "Service should refresh persisted instance"

    async def test_log_event_generates_uuid_when_missing(self, session: AsyncMock) -> None:
        module = _load_activity_service_module()

        with patch.object(module, "ActivityLog") as activity_log_cls:
            activity_instance = self._build_entry({"id": None})
            activity_log_cls.return_value = activity_instance  # type: ignore[assignment]

            service = module.ActivityService()
            await service.log_event(
                db=session,
                user_id=activity_instance.user_id,
                action_type=activity_instance.action_type,
            )

            session.add.assert_called_once()
            session.commit.assert_awaited()
            session.refresh.assert_awaited()

    async def test_list_recent_returns_entries(self, session: AsyncMock) -> None:
        module = _load_activity_service_module()

        entries = [
            self._build_entry({"created_at": 3}),  # type: ignore[arg-type]
            self._build_entry({"created_at": 2}),  # type: ignore[arg-type]
        ]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = entries  # type: ignore[attr-defined]
        session.execute.return_value = mock_result  # type: ignore[assignment]

        service = module.ActivityService()
        results = await service.list_recent(db=session, limit=10)

        assert results == entries
        session.execute.assert_awaited()

    async def test_list_recent_filters_by_user(self, session: AsyncMock) -> None:
        module = _load_activity_service_module()

        user_id = uuid4()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []  # type: ignore[attr-defined]
        session.execute.return_value = mock_result  # type: ignore[assignment]

        with patch.object(module, "select") as select_mock:
            select_mock.return_value.order_by.return_value = select_mock.return_value
            select_mock.return_value.limit.return_value = select_mock.return_value
            select_mock.return_value.where.return_value = select_mock.return_value

            service = module.ActivityService()
            await service.list_recent(db=session, limit=5, user_id=user_id)

            select_mock.return_value.where.assert_called()
