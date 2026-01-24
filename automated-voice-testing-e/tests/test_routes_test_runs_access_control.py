"""
Test suite for test_runs routes resource-level access control.

Validates that tenant_id filtering is enforced on test run endpoints.
"""

import pytest
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent.parent
ROUTES_DIR = PROJECT_ROOT / "backend" / "api" / "routes"
TEST_RUNS_ROUTES_FILE = ROUTES_DIR / "test_runs.py"


class TestTestRunsRoutesFileExists:
    def test_routes_file_exists(self):
        assert TEST_RUNS_ROUTES_FILE.exists(), "test_runs.py should exist"
        assert TEST_RUNS_ROUTES_FILE.is_file(), "test_runs.py should be a file"


class TestImportsAccessControl:
    @pytest.fixture
    def route_content(self):
        return TEST_RUNS_ROUTES_FILE.read_text()

    def test_imports_check_resource_access(self, route_content):
        """Should import check_resource_access from auth module."""
        assert "from api.auth.access_control import check_resource_access" in route_content


class TestGetTestRunTenantIsolation:
    """Test that get_test_run endpoint enforces tenant isolation."""

    @pytest.fixture
    def route_content(self):
        return TEST_RUNS_ROUTES_FILE.read_text()

    def test_get_test_run_calls_check_resource_access(self, route_content):
        """get_test_run should call check_resource_access after fetching."""
        func_start = route_content.find("async def get_test_run(")
        func_end = route_content.find("async def ", func_start + 1)
        if func_end == -1:
            func_end = len(route_content)
        func_body = route_content[func_start:func_end]

        assert "check_resource_access" in func_body, \
            "get_test_run should call check_resource_access to validate tenant"


class TestGetTestExecutionsTenantIsolation:
    """Test that get_test_executions endpoint enforces tenant isolation."""

    @pytest.fixture
    def route_content(self):
        return TEST_RUNS_ROUTES_FILE.read_text()

    def test_get_test_executions_validates_test_run_access(self, route_content):
        """get_test_executions should validate access to parent test run."""
        func_start = route_content.find("async def get_test_executions(")
        func_end = route_content.find("async def ", func_start + 1)
        if func_end == -1:
            func_end = len(route_content)
        func_body = route_content[func_start:func_end]

        # Should either check resource access or filter by tenant
        has_access_check = "check_resource_access" in func_body
        has_tenant_filter = "tenant_id" in func_body

        assert has_access_check or has_tenant_filter, \
            "get_test_executions should validate tenant access"


class TestCancelTestRunOwnershipValidation:
    """Test that cancel_test_run validates ownership before canceling."""

    @pytest.fixture
    def route_content(self):
        return TEST_RUNS_ROUTES_FILE.read_text()

    def test_cancel_validates_test_run_exists_in_tenant(self, route_content):
        """cancel_test_run should validate test run is in user's tenant."""
        func_start = route_content.find("async def cancel_test_run(")
        func_end = route_content.find("async def ", func_start + 1)
        if func_end == -1:
            func_end = len(route_content)
        func_body = route_content[func_start:func_end]

        # Already passes tenant_id to service, which is good
        assert "tenant_id=current_user.tenant_id" in func_body or "check_resource_access" in func_body


class TestRetryFailedTestsOwnershipValidation:
    """Test that retry_failed_tests validates ownership."""

    @pytest.fixture
    def route_content(self):
        return TEST_RUNS_ROUTES_FILE.read_text()

    def test_retry_validates_test_run_exists_in_tenant(self, route_content):
        """retry_failed_tests should validate test run is in user's tenant."""
        func_start = route_content.find("async def retry_failed_tests(")
        func_end = route_content.find("async def ", func_start + 1)
        if func_end == -1:
            func_end = len(route_content)
        func_body = route_content[func_start:func_end]

        # Already passes tenant_id to service
        assert "tenant_id=current_user.tenant_id" in func_body or "check_resource_access" in func_body
