"""
Test suite for test_suites routes resource-level access control.

Validates that tenant_id filtering is enforced on test suite endpoints.
"""

import pytest
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent.parent
ROUTES_DIR = PROJECT_ROOT / "backend" / "api" / "routes"
TEST_SUITES_ROUTES_FILE = ROUTES_DIR / "test_suites.py"


class TestTestSuitesRoutesFileExists:
    def test_routes_file_exists(self):
        assert TEST_SUITES_ROUTES_FILE.exists(), "test_suites.py should exist"


class TestListTestSuitesTenantIsolation:
    """Test that list_test_suites filters by tenant."""

    @pytest.fixture
    def route_content(self):
        return TEST_SUITES_ROUTES_FILE.read_text()

    def test_list_test_suites_passes_tenant_id(self, route_content):
        """list_test_suites should pass tenant_id to service."""
        func_start = route_content.find("async def list_test_suites(")
        func_end = route_content.find("async def ", func_start + 1)
        func_body = route_content[func_start:func_end]

        assert "tenant_id=current_user.tenant_id" in func_body, \
            "list_test_suites should filter by tenant_id"


class TestGetTestSuiteTenantIsolation:
    """Test that get_test_suite enforces tenant isolation."""

    @pytest.fixture
    def route_content(self):
        return TEST_SUITES_ROUTES_FILE.read_text()

    def test_get_test_suite_passes_tenant_id(self, route_content):
        """get_test_suite should pass tenant_id to service."""
        func_start = route_content.find("async def get_test_suite(")
        func_end = route_content.find("async def ", func_start + 1)
        func_body = route_content[func_start:func_end]

        assert "tenant_id=current_user.tenant_id" in func_body, \
            "get_test_suite should filter by tenant_id"


class TestCreateTestSuiteTenantIsolation:
    """Test that create_test_suite associates with user's tenant."""

    @pytest.fixture
    def route_content(self):
        return TEST_SUITES_ROUTES_FILE.read_text()

    def test_create_test_suite_passes_tenant_id(self, route_content):
        """create_test_suite should pass tenant_id to service."""
        func_start = route_content.find("async def create_test_suite(")
        func_end = route_content.find("async def ", func_start + 1)
        func_body = route_content[func_start:func_end]

        assert "tenant_id=current_user.tenant_id" in func_body, \
            "create_test_suite should set tenant_id"


class TestUpdateTestSuiteTenantIsolation:
    """Test that update_test_suite validates tenant."""

    @pytest.fixture
    def route_content(self):
        return TEST_SUITES_ROUTES_FILE.read_text()

    def test_update_test_suite_passes_tenant_id(self, route_content):
        """update_test_suite should pass tenant_id to service."""
        func_start = route_content.find("async def update_test_suite(")
        func_end = route_content.find("async def ", func_start + 1)
        func_body = route_content[func_start:func_end]

        assert "tenant_id=current_user.tenant_id" in func_body, \
            "update_test_suite should filter by tenant_id"


class TestDeleteTestSuiteTenantIsolation:
    """Test that delete_test_suite validates tenant."""

    @pytest.fixture
    def route_content(self):
        return TEST_SUITES_ROUTES_FILE.read_text()

    def test_delete_test_suite_passes_tenant_id(self, route_content):
        """delete_test_suite should pass tenant_id to service."""
        func_start = route_content.find("async def delete_test_suite(")
        func_end = route_content.find("async def ", func_start + 1)
        if func_end == -1:
            func_end = len(route_content)
        func_body = route_content[func_start:func_end]

        assert "tenant_id=current_user.tenant_id" in func_body, \
            "delete_test_suite should filter by tenant_id"
