"""
Tests for the activity feed API routes (TASK-363).

Validates that the activity routes module:
- Exists within backend/api/routes and is populated
- Imports FastAPI, SQLAlchemy, typing helpers, and activity service dependencies
- Configures an APIRouter with /activity prefix and descriptive tags
- Exposes a GET endpoint returning recent activity with filtering/pagination
- Registers the router with the main FastAPI application
"""

from __future__ import annotations

from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).parent.parent
ROUTES_DIR = PROJECT_ROOT / "backend" / "api" / "routes"
ACTIVITY_ROUTE_FILE = ROUTES_DIR / "activity.py"
MAIN_FILE = PROJECT_ROOT / "backend" / "api" / "main.py"


class TestActivityRouteFile:
    """Ensure the activity routes module exists and contains content."""

    def test_routes_directory_exists(self) -> None:
        assert ROUTES_DIR.exists(), "backend/api/routes directory should exist"
        assert ROUTES_DIR.is_dir(), "backend/api/routes should be a directory"

    def test_activity_route_file_exists(self) -> None:
        assert ACTIVITY_ROUTE_FILE.exists(), "activity.py should exist in backend/api/routes"
        assert ACTIVITY_ROUTE_FILE.is_file(), "activity.py should be a file"

    def test_activity_route_file_not_empty(self) -> None:
        if not ACTIVITY_ROUTE_FILE.exists():
            pytest.fail("activity.py should exist before reading content")
        content = ACTIVITY_ROUTE_FILE.read_text(encoding="utf-8")
        assert content.strip(), "activity.py should not be empty"


@pytest.fixture(scope="module")
def route_source() -> str:
    """Return the activity routes source code content."""
    if not ACTIVITY_ROUTE_FILE.exists():
        pytest.fail("activity.py must exist to inspect its contents")
    return ACTIVITY_ROUTE_FILE.read_text(encoding="utf-8")


class TestActivityRouteDocumentation:
    """Validate module-level documentation is present."""

    def test_has_module_docstring(self, route_source: str) -> None:
        assert route_source.lstrip().startswith('"""'), "Activity routes module should include a docstring"


class TestActivityRouteImports:
    """Ensure required imports are declared."""

    def test_imports_fastapi_helpers(self, route_source: str) -> None:
        assert "from fastapi import APIRouter" in route_source, "Routes should import APIRouter"
        assert "Depends" in route_source, "Routes should import Depends for dependency injection"
        assert "Query" in route_source, "Routes should import Query for query parameters"

    def test_imports_typing_utils(self, route_source: str) -> None:
        assert "from typing import Annotated" in route_source or "Annotated" in route_source, \
            "Routes should use typing.Annotated for dependency injection"
        assert "Optional" in route_source, "Routes should import Optional typing helper"

    def test_imports_async_session(self, route_source: str) -> None:
        assert "from sqlalchemy.ext.asyncio import AsyncSession" in route_source, \
            "Routes should import AsyncSession for database access"

    def test_imports_uuid_and_datetime(self, route_source: str) -> None:
        assert "from uuid import UUID" in route_source, "Routes should import UUID for filters"
        assert "from datetime import datetime" in route_source, "Routes should import datetime for since filter"

    def test_imports_activity_service_and_schemas(self, route_source: str) -> None:
        assert "from services import activity_service" in route_source, \
            "Routes should import the activity_service module"
        assert "ActivityFeedResponse" in route_source, \
            "Routes should import ActivityFeedResponse schema for responses"


class TestActivityRouterConfiguration:
    """Verify router configuration matches API contract."""

    def test_router_instance_created(self, route_source: str) -> None:
        assert "router = APIRouter" in route_source, "Routes should instantiate an APIRouter"

    def test_router_prefix(self, route_source: str) -> None:
        has_prefix = ('prefix="/activity"' in route_source or
                      "prefix='/activity'" in route_source or
                      'prefix = "/activity"' in route_source)
        assert has_prefix, "Router should be configured with /activity prefix"

    def test_router_tags(self, route_source: str) -> None:
        assert "tags=" in route_source, "Router should declare descriptive tags"


class TestActivityFeedEndpointDefinition:
    """Ensure the activity feed endpoint is defined with expected behaviour."""

    def test_defines_get_endpoint(self, route_source: str) -> None:
        assert "@router.get" in route_source and '"/"' in route_source, \
            "Activity routes should define a GET endpoint at /activity/"

    def test_endpoint_is_async(self, route_source: str) -> None:
        assert "async def" in route_source, "Activity endpoint should be asynchronous"

    def test_endpoint_uses_dependencies(self, route_source: str) -> None:
        assert "Depends(get_db)" in route_source, "Endpoint should depend on get_db to access the database"
        assert "Depends(get_current_user_with_db)" in route_source, "Endpoint should require authenticated user"

    def test_endpoint_accepts_filters(self, route_source: str) -> None:
        assert "user_id: Optional[UUID] = Query" in route_source, "Endpoint should support user_id filter"
        assert "action_type: Optional[str] = Query" in route_source, "Endpoint should support action_type filter"
        assert "resource_type: Optional[str] = Query" in route_source, "Endpoint should support resource_type filter"
        assert "since: Optional[datetime] = Query" in route_source, "Endpoint should support since timestamp filter"

    def test_endpoint_accepts_pagination(self, route_source: str) -> None:
        assert "limit: int = Query" in route_source, "Endpoint should expose limit pagination parameter"
        assert "offset: int = Query" in route_source, "Endpoint should expose offset pagination parameter"

    def test_endpoint_calls_service(self, route_source: str) -> None:
        assert "await activity_service.list_recent" in route_source, \
            "Endpoint should call activity_service.list_recent to fetch activity entries"

    def test_endpoint_returns_schema(self, route_source: str) -> None:
        assert "response_model=ActivityFeedResponse" in route_source, \
            "Endpoint should declare ActivityFeedResponse as response model"
        assert "ActivityLogResponse" in route_source, \
            "Endpoint should serialise events into ActivityLogResponse schema"


class TestActivityRouterRegistration:
    """Ensure the activity router is registered with the FastAPI application."""

    def test_main_imports_activity_routes(self) -> None:
        assert MAIN_FILE.exists(), "backend/api/main.py should exist"
        content = MAIN_FILE.read_text(encoding="utf-8")
        assert "from api.routes import activity" in content, \
            "main.py should import the activity routes module"

    def test_main_includes_activity_router(self) -> None:
        content = MAIN_FILE.read_text(encoding="utf-8")
        assert "api_router.include_router(activity.router)" in content, \
            "main.py should include the activity router on the API router"
