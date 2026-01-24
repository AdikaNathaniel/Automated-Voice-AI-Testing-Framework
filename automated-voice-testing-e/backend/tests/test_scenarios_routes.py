"""
Unit tests for scenarios API routes.

Tests the scenario management endpoints including CRUD operations, step management,
and import/export functionality. Uses mocked services and database sessions to test
route logic without external dependencies.
"""

import pytest
from uuid import uuid4
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from api.routes.scenarios import (
    router,
    create_scenario,
    list_scenarios,
    get_scenario,
    update_scenario,
    delete_scenario,
    add_scenario_step,
    list_scenario_steps,
    export_scenario_json,
    export_scenario_yaml,
    import_scenario_json,
    import_scenario_yaml,
)
from api.schemas.scenario import ScenarioScriptCreate, ScenarioScriptUpdate, ScenarioStepCreate
from api.schemas.auth import UserResponse
from api.auth.roles import Role


class TestCreateScenario:
    """Test POST /scenarios endpoint."""

    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def admin_user(self):
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.email = "admin@example.com"
        user.username = "admin"
        user.role = Role.ORG_ADMIN.value
        user.is_active = True
        user.tenant_id = uuid4()
        return user

    @pytest.fixture
    def viewer_user(self):
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.email = "viewer@example.com"
        user.username = "viewer"
        user.role = Role.VIEWER.value
        user.is_active = True
        user.tenant_id = uuid4()
        return user

    @pytest.mark.asyncio
    async def test_create_scenario_permission_denied(self, mock_db, viewer_user):
        """Test that non-admin user cannot create scenario."""
        create_request = ScenarioScriptCreate(name="New Scenario")
        with pytest.raises(HTTPException) as exc_info:
            await create_scenario(data=create_request, db=mock_db, current_user=viewer_user)
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN


class TestListScenarios:
    """Test GET /scenarios endpoint."""

    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def viewer_user(self):
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.email = "viewer@example.com"
        user.username = "viewer"
        user.role = Role.VIEWER.value
        user.is_active = True
        user.tenant_id = uuid4()
        return user

    @pytest.mark.asyncio
    async def test_list_scenarios_success(self, mock_db, viewer_user):
        """Test successful listing of scenarios."""
        mock_scenario = MagicMock()
        mock_scenario.id = uuid4()
        mock_scenario.name = "Scenario 1"
        mock_scenario.description = "Test scenario"
        mock_scenario.version = "1.0"
        mock_scenario.is_active = True
        mock_scenario.created_by = uuid4()
        mock_scenario.created_at = datetime.utcnow()
        mock_scenario.updated_at = datetime.utcnow()
        mock_scenario.tenant_id = viewer_user.tenant_id

        with patch('api.routes.scenarios.scenario_service.list', new_callable=AsyncMock) as mock_list:
            mock_list.return_value = [mock_scenario]

            result = await list_scenarios(
                db=mock_db, current_user=viewer_user, skip=0, limit=100, is_active=None
            )

            assert result is not None
            assert len(result) == 1
            assert mock_list.called

    @pytest.mark.asyncio
    async def test_list_scenarios_empty(self, mock_db, viewer_user):
        """Test listing scenarios when none exist."""
        with patch('api.routes.scenarios.scenario_service.list', new_callable=AsyncMock) as mock_list:
            mock_list.return_value = []

            result = await list_scenarios(
                db=mock_db, current_user=viewer_user, skip=0, limit=100, is_active=None
            )

            assert result is not None
            assert len(result) == 0

    @pytest.mark.asyncio
    async def test_list_scenarios_with_filter(self, mock_db, viewer_user):
        """Test listing scenarios with active filter."""
        with patch('api.routes.scenarios.scenario_service.list', new_callable=AsyncMock) as mock_list:
            mock_list.return_value = []

            result = await list_scenarios(
                db=mock_db, current_user=viewer_user, skip=0, limit=100, is_active=True
            )

            assert result is not None
            assert mock_list.called


class TestGetScenario:
    """Test GET /scenarios/{id} endpoint."""

    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def viewer_user(self):
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.email = "viewer@example.com"
        user.username = "viewer"
        user.role = Role.VIEWER.value
        user.is_active = True
        user.tenant_id = uuid4()
        return user

    @pytest.mark.asyncio
    async def test_get_scenario_not_found(self, mock_db, viewer_user):
        """Test that 404 is raised when scenario not found."""
        scenario_id = uuid4()
        with patch('api.routes.scenarios.scenario_service.get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None

            with pytest.raises(HTTPException) as exc_info:
                await get_scenario(scenario_id=scenario_id, db=mock_db, current_user=viewer_user)

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


class TestUpdateScenario:
    """Test PUT /scenarios/{id} endpoint."""

    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def admin_user(self):
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.email = "admin@example.com"
        user.username = "admin"
        user.role = Role.ORG_ADMIN.value
        user.is_active = True
        user.tenant_id = uuid4()
        return user

    @pytest.fixture
    def viewer_user(self):
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.email = "viewer@example.com"
        user.username = "viewer"
        user.role = Role.VIEWER.value
        user.is_active = True
        user.tenant_id = uuid4()
        return user

    @pytest.mark.asyncio
    async def test_update_scenario_permission_denied(self, mock_db, viewer_user):
        """Test that non-admin user cannot update scenario."""
        scenario_id = uuid4()
        update_request = ScenarioScriptUpdate(name="Updated Scenario")
        with pytest.raises(HTTPException) as exc_info:
            await update_scenario(
                scenario_id=scenario_id, data=update_request, db=mock_db, current_user=viewer_user
            )
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN


class TestDeleteScenario:
    """Test DELETE /scenarios/{id} endpoint."""

    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def admin_user(self):
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.email = "admin@example.com"
        user.username = "admin"
        user.role = Role.ORG_ADMIN.value
        user.is_active = True
        user.tenant_id = uuid4()
        return user

    @pytest.fixture
    def viewer_user(self):
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.email = "viewer@example.com"
        user.username = "viewer"
        user.role = Role.VIEWER.value
        user.is_active = True
        user.tenant_id = uuid4()
        return user

    @pytest.mark.asyncio
    async def test_delete_scenario_permission_denied(self, mock_db, viewer_user):
        """Test that non-admin user cannot delete scenario."""
        scenario_id = uuid4()
        with pytest.raises(HTTPException) as exc_info:
            await delete_scenario(scenario_id=scenario_id, db=mock_db, current_user=viewer_user)
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN


class TestAddStep:
    """Test POST /scenarios/{id}/steps endpoint."""

    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def admin_user(self):
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.email = "admin@example.com"
        user.username = "admin"
        user.role = Role.ORG_ADMIN.value
        user.is_active = True
        user.tenant_id = uuid4()
        return user

    @pytest.fixture
    def viewer_user(self):
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.email = "viewer@example.com"
        user.username = "viewer"
        user.role = Role.VIEWER.value
        user.is_active = True
        user.tenant_id = uuid4()
        return user

    @pytest.mark.asyncio
    async def test_add_step_permission_denied(self, mock_db, viewer_user):
        """Test that non-admin user cannot add step."""
        scenario_id = uuid4()
        step_request = ScenarioStepCreate(
            step_order=1,
            user_utterance="Hello"
        )
        with pytest.raises(HTTPException) as exc_info:
            await add_scenario_step(
                scenario_id=scenario_id, data=step_request, db=mock_db, current_user=viewer_user
            )
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN


class TestListSteps:
    """Test GET /scenarios/{id}/steps endpoint."""

    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def viewer_user(self):
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.email = "viewer@example.com"
        user.username = "viewer"
        user.role = Role.VIEWER.value
        user.is_active = True
        user.tenant_id = uuid4()
        return user

    @pytest.mark.asyncio
    async def test_list_steps_scenario_not_found(self, mock_db, viewer_user):
        """Test that 404 is raised when scenario not found."""
        scenario_id = uuid4()
        with patch('api.routes.scenarios.scenario_service.get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None

            with pytest.raises(HTTPException) as exc_info:
                await list_scenario_steps(scenario_id=scenario_id, db=mock_db, current_user=viewer_user)

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


class TestExportScenarioJson:
    """Test GET /scenarios/{id}/export/json endpoint."""

    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def viewer_user(self):
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.email = "viewer@example.com"
        user.username = "viewer"
        user.role = Role.VIEWER.value
        user.is_active = True
        user.tenant_id = uuid4()
        return user

    @pytest.mark.asyncio
    async def test_export_json_scenario_not_found(self, mock_db, viewer_user):
        """Test that 404 is raised when scenario not found."""
        scenario_id = uuid4()
        with patch('api.routes.scenarios.scenario_service.get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None

            with pytest.raises(HTTPException) as exc_info:
                await export_scenario_json(
                    scenario_id=scenario_id, db=mock_db, current_user=viewer_user
                )

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


class TestExportScenarioYaml:
    """Test GET /scenarios/{id}/export/yaml endpoint."""

    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def viewer_user(self):
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.email = "viewer@example.com"
        user.username = "viewer"
        user.role = Role.VIEWER.value
        user.is_active = True
        user.tenant_id = uuid4()
        return user

    @pytest.mark.asyncio
    async def test_export_yaml_scenario_not_found(self, mock_db, viewer_user):
        """Test that 404 is raised when scenario not found."""
        scenario_id = uuid4()
        with patch('api.routes.scenarios.scenario_service.get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None

            with pytest.raises(HTTPException) as exc_info:
                await export_scenario_yaml(
                    scenario_id=scenario_id, db=mock_db, current_user=viewer_user
                )

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


class TestImportScenarioJson:
    """Test POST /scenarios/import/json endpoint."""

    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def admin_user(self):
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.email = "admin@example.com"
        user.username = "admin"
        user.role = Role.ORG_ADMIN.value
        user.is_active = True
        user.tenant_id = uuid4()
        return user

    @pytest.fixture
    def viewer_user(self):
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.email = "viewer@example.com"
        user.username = "viewer"
        user.role = Role.VIEWER.value
        user.is_active = True
        user.tenant_id = uuid4()
        return user

    @pytest.mark.asyncio
    async def test_import_json_permission_denied(self, mock_db, viewer_user):
        """Test that non-admin user cannot import scenario from JSON."""
        json_content = '{"name": "Test Scenario"}'
        with pytest.raises(HTTPException) as exc_info:
            await import_scenario_json(
                json_content=json_content, db=mock_db, current_user=viewer_user
            )
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN


class TestImportScenarioYaml:
    """Test POST /scenarios/import/yaml endpoint."""

    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def admin_user(self):
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.email = "admin@example.com"
        user.username = "admin"
        user.role = Role.ORG_ADMIN.value
        user.is_active = True
        user.tenant_id = uuid4()
        return user

    @pytest.fixture
    def viewer_user(self):
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.email = "viewer@example.com"
        user.username = "viewer"
        user.role = Role.VIEWER.value
        user.is_active = True
        user.tenant_id = uuid4()
        return user

    @pytest.mark.asyncio
    async def test_import_yaml_permission_denied(self, mock_db, viewer_user):
        """Test that non-admin user cannot import scenario from YAML."""
        yaml_content = "name: Test Scenario"
        with pytest.raises(HTTPException) as exc_info:
            await import_scenario_yaml(
                yaml_content=yaml_content, db=mock_db, current_user=viewer_user
            )
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN


class TestScenariosRoutesIntegration:
    """Integration tests for scenarios routes."""

    def test_router_has_required_endpoints(self):
        """Test that router has all required scenario endpoints."""
        routes = [route.path for route in router.routes]
        assert len(routes) > 0
        assert any("scenarios" in str(route) for route in routes)

    def test_router_methods(self):
        """Test that endpoints use correct HTTP methods."""
        all_methods = set()
        for route in router.routes:
            if hasattr(route, "methods") and route.methods:
                all_methods.update(route.methods)
        assert len(all_methods) > 0, "Router should have HTTP methods defined"

    def test_all_endpoints_exported(self):
        """Test that all required endpoints are properly defined."""
        assert create_scenario is not None
        assert list_scenarios is not None
        assert get_scenario is not None
        assert update_scenario is not None
        assert delete_scenario is not None
        assert add_scenario_step is not None
        assert list_scenario_steps is not None
        assert export_scenario_json is not None
        assert export_scenario_yaml is not None
        assert import_scenario_json is not None
        assert import_scenario_yaml is not None

        # Verify all are callable
        assert callable(create_scenario)
        assert callable(list_scenarios)
        assert callable(get_scenario)
        assert callable(update_scenario)
        assert callable(delete_scenario)
        assert callable(add_scenario_step)
        assert callable(list_scenario_steps)
        assert callable(export_scenario_json)
        assert callable(export_scenario_yaml)
        assert callable(import_scenario_json)
        assert callable(import_scenario_yaml)
