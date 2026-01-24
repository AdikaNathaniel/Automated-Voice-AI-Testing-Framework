"""
Unit tests for test suites API routes.

Tests the test suite management endpoints including list, create, get, update,
and delete operations. Uses mocked services and database sessions to test
route logic without external dependencies.
"""

import pytest
from uuid import uuid4
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from api.routes.test_suites import (
    router,
    list_test_suites,
    create_test_suite,
    get_test_suite,
    update_test_suite,
    delete_test_suite,
)
from api.schemas.test_suite import TestSuiteCreate, TestSuiteUpdate
from api.schemas.auth import UserResponse
from api.auth.roles import Role


class TestListTestSuites:
    """Test GET /test-suites endpoint."""

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
    async def test_list_test_suites_success(self, mock_db, viewer_user):
        """Test successful listing of test suites."""
        mock_suite = MagicMock()
        mock_suite.id = uuid4()
        mock_suite.name = "Suite 1"
        mock_suite.category = "smoke"
        mock_suite.description = "Test suite description"
        mock_suite.is_active = True
        mock_suite.created_by = uuid4()
        mock_suite.created_at = datetime.utcnow()
        mock_suite.updated_at = datetime.utcnow()

        with patch('services.test_suite_service.list_test_suites', new_callable=AsyncMock) as mock_list:
            mock_list.return_value = ([mock_suite], 1)

            result = await list_test_suites(
                db=mock_db, current_user=viewer_user, category=None, is_active=None, skip=0, limit=50
            )

            assert result is not None
            assert "test_suites" in result
            assert len(result["test_suites"]) == 1
            assert result["total"] == 1
            assert mock_list.called

    @pytest.mark.asyncio
    async def test_list_test_suites_empty(self, mock_db, viewer_user):
        """Test listing test suites when none exist."""
        with patch('services.test_suite_service.list_test_suites', new_callable=AsyncMock) as mock_list:
            mock_list.return_value = ([], 0)

            result = await list_test_suites(
                db=mock_db, current_user=viewer_user, category=None, is_active=None, skip=0, limit=50
            )

            assert result is not None
            assert len(result["test_suites"]) == 0
            assert result["total"] == 0

    @pytest.mark.asyncio
    async def test_list_test_suites_with_filters(self, mock_db, viewer_user):
        """Test listing test suites with category filter."""
        with patch('services.test_suite_service.list_test_suites', new_callable=AsyncMock) as mock_list:
            mock_list.return_value = ([], 0)

            result = await list_test_suites(
                db=mock_db, current_user=viewer_user, category="smoke", is_active=True, skip=0, limit=50
            )

            assert result is not None
            assert len(result["test_suites"]) == 0
            assert mock_list.called


class TestCreateTestSuite:
    """Test POST /test-suites endpoint."""

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
    async def test_create_test_suite_permission_denied(self, mock_db, viewer_user):
        """Test that non-admin user cannot create test suite."""
        create_request = TestSuiteCreate(name="New Suite")
        with pytest.raises(HTTPException) as exc_info:
            await create_test_suite(data=create_request, db=mock_db, current_user=viewer_user)
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Admin or QA" in exc_info.value.detail


class TestGetTestSuite:
    """Test GET /test-suites/{id} endpoint."""

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
    async def test_get_test_suite_not_found(self, mock_db, viewer_user):
        """Test that 404 is raised when test suite not found."""
        suite_id = uuid4()
        with patch('services.test_suite_service.get_test_suite', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None

            with pytest.raises(HTTPException) as exc_info:
                await get_test_suite(test_suite_id=suite_id, db=mock_db, current_user=viewer_user)

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


class TestUpdateTestSuite:
    """Test PUT /test-suites/{id} endpoint."""

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
    async def test_update_test_suite_permission_denied(self, mock_db, viewer_user):
        """Test that non-admin user cannot update test suite."""
        suite_id = uuid4()
        update_request = TestSuiteUpdate(name="Updated Suite")
        with pytest.raises(HTTPException) as exc_info:
            await update_test_suite(
                test_suite_id=suite_id, data=update_request, db=mock_db, current_user=viewer_user
            )
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN


class TestDeleteTestSuite:
    """Test DELETE /test-suites/{id} endpoint."""

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
    async def test_delete_test_suite_permission_denied(self, mock_db, viewer_user):
        """Test that non-admin user cannot delete test suite."""
        suite_id = uuid4()
        with pytest.raises(HTTPException) as exc_info:
            await delete_test_suite(test_suite_id=suite_id, db=mock_db, current_user=viewer_user)
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN


class TestTestSuitesRoutesIntegration:
    """Integration tests for test suites routes."""

    def test_router_has_required_endpoints(self):
        """Test that router has all required test suite endpoints."""
        routes = [route.path for route in router.routes]
        assert len(routes) > 0
        assert any("test-suites" in str(route) for route in routes)

    def test_router_methods(self):
        """Test that endpoints use correct HTTP methods."""
        all_methods = set()
        for route in router.routes:
            if hasattr(route, "methods") and route.methods:
                all_methods.update(route.methods)
        assert len(all_methods) > 0, "Router should have HTTP methods defined"

    def test_all_endpoints_exported(self):
        """Test that all required endpoints are properly defined."""
        assert list_test_suites is not None
        assert create_test_suite is not None
        assert get_test_suite is not None
        assert update_test_suite is not None
        assert delete_test_suite is not None
        assert callable(list_test_suites)
        assert callable(create_test_suite)
        assert callable(get_test_suite)
        assert callable(update_test_suite)
        assert callable(delete_test_suite)
