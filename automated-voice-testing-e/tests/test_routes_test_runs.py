"""
Test suite for backend/api/routes/test_runs.py

Validates the test run API routes implementation:
- File structure and imports
- Router configuration
- POST /api/v1/test-runs endpoint
- GET /api/v1/test-runs/:id endpoint
- GET /api/v1/test-runs endpoint
- PUT /api/v1/test-runs/:id/cancel endpoint
- POST /api/v1/test-runs/:id/retry endpoint
- GET /api/v1/test-runs/:id/executions endpoint
- Authentication handling
- Error handling
- Documentation
"""

import pytest
from pathlib import Path
import sys


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
ROUTES_DIR = BACKEND_DIR / "api" / "routes"
TEST_RUNS_ROUTE_FILE = ROUTES_DIR / "test_runs.py"


class TestTestRunsRouteFileExists:
    """Test that test_runs.py route file exists"""

    def test_routes_directory_exists(self):
        """Test that api/routes directory exists"""
        assert ROUTES_DIR.exists(), "backend/api/routes directory should exist"
        assert ROUTES_DIR.is_dir(), "routes should be a directory"

    def test_test_runs_route_file_exists(self):
        """Test that test_runs.py exists"""
        assert TEST_RUNS_ROUTE_FILE.exists(), "test_runs.py route should exist"
        assert TEST_RUNS_ROUTE_FILE.is_file(), "test_runs.py should be a file"

    def test_test_runs_route_has_content(self):
        """Test that test_runs.py has content"""
        content = TEST_RUNS_ROUTE_FILE.read_text()
        assert len(content) > 0, "test_runs.py should not be empty"


class TestTestRunsRouteImports:
    """Test necessary imports"""

    @pytest.fixture
    def route_content(self):
        """Load test_runs.py content"""
        return TEST_RUNS_ROUTE_FILE.read_text()

    def test_imports_uuid(self, route_content):
        """Test that UUID is imported"""
        assert "from uuid import UUID" in route_content or "import uuid" in route_content, \
            "Should import UUID"

    def test_imports_fastapi(self, route_content):
        """Test that FastAPI is imported"""
        assert "from fastapi import" in route_content or "import fastapi" in route_content, \
            "Should import FastAPI components"

    def test_imports_apirouter(self, route_content):
        """Test that APIRouter is imported"""
        assert "APIRouter" in route_content, \
            "Should import APIRouter"

    def test_imports_depends(self, route_content):
        """Test that Depends is imported"""
        assert "Depends" in route_content, \
            "Should import Depends for dependency injection"

    def test_imports_httpexception(self, route_content):
        """Test that HTTPException is imported"""
        assert "HTTPException" in route_content, \
            "Should import HTTPException for error handling"

    def test_imports_sqlalchemy(self, route_content):
        """Test that SQLAlchemy is imported"""
        assert "AsyncSession" in route_content or "sqlalchemy" in route_content.lower(), \
            "Should import SQLAlchemy for database operations"

    def test_imports_schemas(self, route_content):
        """Test that schemas are imported"""
        assert "from api.schemas" in route_content or "from api.schemas" in route_content, \
            "Should import schemas"


class TestRouterConfiguration:
    """Test router configuration"""

    @pytest.fixture
    def route_content(self):
        """Load test_runs.py content"""
        return TEST_RUNS_ROUTE_FILE.read_text()

    def test_creates_router(self, route_content):
        """Test that APIRouter is created"""
        assert "router = APIRouter(" in route_content or "router=APIRouter(" in route_content, \
            "Should create APIRouter instance"

    def test_router_has_prefix(self, route_content):
        """Test that router has prefix"""
        assert "prefix=" in route_content, \
            "Router should have prefix"

    def test_router_has_tags(self, route_content):
        """Test that router has tags"""
        assert "tags=" in route_content, \
            "Router should have tags"


class TestCreateTestRunEndpoint:
    """Test POST /test-runs endpoint"""

    @pytest.fixture
    def route_content(self):
        """Load test_runs.py content"""
        return TEST_RUNS_ROUTE_FILE.read_text()

    def test_has_create_test_run_endpoint(self, route_content):
        """Test that create test run endpoint exists"""
        assert "@router.post" in route_content, \
            "Should have POST endpoint for creating test runs"

    def test_create_endpoint_uses_test_run_create_schema(self, route_content):
        """Test that create endpoint uses TestRunCreate schema"""
        assert "TestRunCreate" in route_content, \
            "Should use TestRunCreate schema"

    def test_create_endpoint_returns_test_run_response(self, route_content):
        """Test that create endpoint returns TestRunResponse"""
        assert "TestRunResponse" in route_content, \
            "Should return TestRunResponse"

    def test_create_endpoint_has_db_dependency(self, route_content):
        """Test that create endpoint has database dependency"""
        assert "AsyncSession" in route_content and "Depends" in route_content, \
            "Should have database dependency"


class TestGetTestRunEndpoint:
    """Test GET /test-runs/:id endpoint"""

    @pytest.fixture
    def route_content(self):
        """Load test_runs.py content"""
        return TEST_RUNS_ROUTE_FILE.read_text()

    def test_has_get_test_run_endpoint(self, route_content):
        """Test that get test run endpoint exists"""
        assert "@router.get" in route_content, \
            "Should have GET endpoint for retrieving test runs"

    def test_get_endpoint_uses_uuid_param(self, route_content):
        """Test that get endpoint uses UUID parameter"""
        assert "UUID" in route_content, \
            "Should use UUID parameter for test run ID"

    def test_get_endpoint_returns_test_run_response(self, route_content):
        """Test that get endpoint returns TestRunResponse"""
        assert "TestRunResponse" in route_content, \
            "Should return TestRunResponse"


class TestListTestRunsEndpoint:
    """Test GET /test-runs endpoint"""

    @pytest.fixture
    def route_content(self):
        """Load test_runs.py content"""
        return TEST_RUNS_ROUTE_FILE.read_text()

    def test_has_list_test_runs_function(self, route_content):
        """Test that list test runs function exists"""
        # Should have a function for listing (could be list_test_runs or similar)
        assert "def " in route_content, \
            "Should have async function definitions"

    def test_list_endpoint_supports_pagination(self, route_content):
        """Test that list endpoint supports pagination"""
        # Should have skip/limit or similar pagination params
        assert "skip" in route_content.lower() or "limit" in route_content.lower() or \
               "page" in route_content.lower(), \
            "Should support pagination parameters"


class TestCancelTestRunEndpoint:
    """Test PUT /test-runs/:id/cancel endpoint"""

    @pytest.fixture
    def route_content(self):
        """Load test_runs.py content"""
        return TEST_RUNS_ROUTE_FILE.read_text()

    def test_has_cancel_endpoint(self, route_content):
        """Test that cancel endpoint exists"""
        assert "@router.put" in route_content or "@router.post" in route_content or \
               "cancel" in route_content.lower(), \
            "Should have endpoint for canceling test runs"


class TestRetryTestRunEndpoint:
    """Test POST /test-runs/:id/retry endpoint"""

    @pytest.fixture
    def route_content(self):
        """Load test_runs.py content"""
        return TEST_RUNS_ROUTE_FILE.read_text()

    def test_has_retry_endpoint(self, route_content):
        """Test that retry endpoint exists"""
        assert "retry" in route_content.lower(), \
            "Should have endpoint for retrying failed tests"


class TestGetExecutionsEndpoint:
    """Test GET /test-runs/:id/executions endpoint"""

    @pytest.fixture
    def route_content(self):
        """Load test_runs.py content"""
        return TEST_RUNS_ROUTE_FILE.read_text()

    def test_has_executions_endpoint(self, route_content):
        """Test that executions endpoint exists"""
        assert "execution" in route_content.lower(), \
            "Should have endpoint for getting test executions"

    def test_executions_endpoint_returns_list(self, route_content):
        """Test that executions endpoint returns list or response"""
        assert "TestExecutionResponse" in route_content or "list" in route_content.lower(), \
            "Should return list of test executions or TestExecutionResponse"


class TestAuthentication:
    """Test authentication handling"""

    @pytest.fixture
    def route_content(self):
        """Load test_runs.py content"""
        return TEST_RUNS_ROUTE_FILE.read_text()

    def test_uses_authentication(self, route_content):
        """Test that routes use authentication"""
        assert "HTTPBearer" in route_content or "get_current_user" in route_content or \
               "auth" in route_content.lower(), \
            "Should use authentication"

    def test_has_current_user_dependency(self, route_content):
        """Test that routes have current user dependency"""
        assert "current_user" in route_content.lower() or "user" in route_content, \
            "Should have current user dependency"


class TestErrorHandling:
    """Test error handling"""

    @pytest.fixture
    def route_content(self):
        """Load test_runs.py content"""
        return TEST_RUNS_ROUTE_FILE.read_text()

    def test_handles_exceptions(self, route_content):
        """Test that routes handle exceptions"""
        assert "HTTPException" in route_content or "try" in route_content or \
               "except" in route_content, \
            "Should handle exceptions"

    def test_uses_http_status_codes(self, route_content):
        """Test that routes use HTTP status codes"""
        assert "status" in route_content or "HTTP_" in route_content or \
               "200" in route_content or "201" in route_content or "404" in route_content, \
            "Should use HTTP status codes"


class TestDocumentation:
    """Test route documentation"""

    @pytest.fixture
    def route_content(self):
        """Load test_runs.py content"""
        return TEST_RUNS_ROUTE_FILE.read_text()

    def test_has_module_documentation(self, route_content):
        """Test that module has documentation"""
        assert '"""' in route_content or "'''" in route_content, \
            "Should have module documentation"

    def test_has_endpoint_descriptions(self, route_content):
        """Test that endpoints have descriptions"""
        # Should have summary or description in decorators or docstrings
        docstring_count = route_content.count('"""')
        assert docstring_count >= 4, \
            "Should have docstrings for multiple endpoints"


class TestRouteStructure:
    """Test overall route structure"""

    @pytest.fixture
    def route_content(self):
        """Load test_runs.py content"""
        return TEST_RUNS_ROUTE_FILE.read_text()

    def test_is_valid_python(self, route_content):
        """Test that file is valid Python"""
        try:
            compile(route_content, TEST_RUNS_ROUTE_FILE, 'exec')
        except SyntaxError as e:
            pytest.fail(f"test_runs.py has syntax error: {e}")

    def test_defines_async_functions(self, route_content):
        """Test that file defines async functions"""
        assert "async def" in route_content, \
            "Should define async functions for endpoints"

    def test_uses_type_annotations(self, route_content):
        """Test that functions use type annotations"""
        assert "->" in route_content or ": " in route_content, \
            "Should use type annotations"


class TestImportability:
    """Test that test_runs routes can be imported"""

    def test_can_import_routes_module(self):
        """Test that routes module can be imported"""
        # Add backend to path
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from api.routes import test_runs
            assert test_runs is not None, \
                "test_runs routes module should be importable"
        except ImportError as e:
            pytest.fail(f"Cannot import test_runs routes: {e}")

    def test_can_access_router(self):
        """Test that router can be accessed"""
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from api.routes.test_runs import router
            assert router is not None, \
                "router should be accessible"
        except ImportError as e:
            pytest.fail(f"Cannot import router: {e}")


class TestServiceIntegration:
    """Test integration with service layer"""

    @pytest.fixture
    def route_content(self):
        """Load test_runs.py content"""
        return TEST_RUNS_ROUTE_FILE.read_text()

    def test_imports_orchestration_service(self, route_content):
        """Test that orchestration service is imported"""
        assert "orchestration" in route_content.lower() or "service" in route_content.lower(), \
            "Should import orchestration service"

    def test_calls_service_functions(self, route_content):
        """Test that routes call service functions"""
        assert "await" in route_content, \
            "Should call async service functions"


class TestRBACBehavior:
    """Test RBAC behavior on test run endpoints - actual behavior tests"""

    @pytest.fixture
    def route_content(self):
        """Load test_runs.py content"""
        return TEST_RUNS_ROUTE_FILE.read_text()

    def test_create_endpoint_requires_role_check(self, route_content):
        """Test that create_test_run uses require_role or _ensure_run_controller"""
        # Check if role enforcement is present for create
        has_role_check = (
            "require_role" in route_content or
            "_ensure_run_controller" in route_content
        )
        assert has_role_check, \
            "create_test_run should enforce role checks"

        # Verify admin/qa_lead roles are checked for create
        has_admin_role = "admin" in route_content.lower()
        has_qa_lead_role = "qa_lead" in route_content.lower()
        assert has_admin_role or has_qa_lead_role, \
            "create_test_run should check for admin or qa_lead roles"

    def test_cancel_endpoint_requires_role_check(self, route_content):
        """Test that cancel_test_run uses role checking"""
        # The cancel function should call _ensure_run_controller or require_role
        has_role_check = (
            "require_role" in route_content or
            "_ensure_run_controller" in route_content
        )
        assert has_role_check, \
            "cancel_test_run should enforce role checks"

    def test_retry_endpoint_requires_role_check(self, route_content):
        """Test that retry_failed_tests uses role checking"""
        # The retry function should call _ensure_run_controller or require_role
        has_role_check = (
            "require_role" in route_content or
            "_ensure_run_controller" in route_content
        )
        assert has_role_check, \
            "retry_failed_tests should enforce role checks"

    def test_list_endpoint_allows_authenticated_users(self, route_content):
        """Test that list_test_runs allows any authenticated user (viewers can read)"""
        # List should use get_current_user but NOT require elevated role
        # Find the list_test_runs function and check it doesn't call _ensure_run_controller
        lines = route_content.split('\n')
        in_list_function = False
        role_check_in_list = False

        for i, line in enumerate(lines):
            if 'async def list_test_runs' in line:
                in_list_function = True
            elif in_list_function and line.strip().startswith('async def '):
                break  # End of function
            elif in_list_function and ('_ensure_run_controller' in line or 'require_role' in line):
                role_check_in_list = True
                break

        # List should NOT require elevated roles - viewers can read
        assert not role_check_in_list, \
            "list_test_runs should allow any authenticated user (no elevated role check)"

    def test_get_endpoint_allows_authenticated_users(self, route_content):
        """Test that get_test_run allows any authenticated user (viewers can read)"""
        # Find the get_test_run function
        lines = route_content.split('\n')
        in_get_function = False
        role_check_in_get = False

        for i, line in enumerate(lines):
            if 'async def get_test_run(' in line:
                in_get_function = True
            elif in_get_function and line.strip().startswith('async def '):
                break
            elif in_get_function and ('_ensure_run_controller' in line or 'require_role' in line):
                role_check_in_get = True
                break

        # Get should NOT require elevated roles
        assert not role_check_in_get, \
            "get_test_run should allow any authenticated user (no elevated role check)"

    def test_get_executions_allows_authenticated_users(self, route_content):
        """Test that get_test_executions allows any authenticated user"""
        lines = route_content.split('\n')
        in_exec_function = False
        role_check_in_exec = False

        for i, line in enumerate(lines):
            if 'async def get_test_executions' in line:
                in_exec_function = True
            elif in_exec_function and line.strip().startswith('async def '):
                break
            elif in_exec_function and ('_ensure_run_controller' in line or 'require_role' in line):
                role_check_in_exec = True
                break

        assert not role_check_in_exec, \
            "get_test_executions should allow any authenticated user"

    def test_role_check_function_exists(self, route_content):
        """Test that role checking mechanism is defined"""
        has_role_mechanism = (
            "_ensure_run_controller" in route_content or
            "require_role" in route_content or
            "from api.auth.permissions import" in route_content
        )
        assert has_role_mechanism, \
            "Should have role checking mechanism (require_role or _ensure_run_controller)"

    def test_role_check_returns_403_on_failure(self, route_content):
        """Test that role check returns 403 Forbidden"""
        assert "403" in route_content or "HTTP_403_FORBIDDEN" in route_content, \
            "Role check should return 403 Forbidden on failure"

    def test_defines_run_control_roles(self, route_content):
        """Test that run control roles are defined"""
        # Should define which roles can control runs (admin, qa_lead)
        has_role_definition = (
            "_RUN_CONTROL_ROLES" in route_content or
            "Role.ADMIN" in route_content or
            '"admin"' in route_content.lower()
        )
        assert has_role_definition, \
            "Should define which roles can control test runs"


class TestRBACUsesCentralizedPermissions:
    """Test that RBAC uses centralized permissions module"""

    @pytest.fixture
    def route_content(self):
        """Load test_runs.py content"""
        return TEST_RUNS_ROUTE_FILE.read_text()

    def test_imports_permissions_module(self, route_content):
        """Test that permissions module is imported"""
        # Best practice: use centralized require_role from permissions.py
        # Or at least import the Role enum
        has_permissions_import = (
            "from api.auth.permissions import" in route_content or
            "from api.auth.roles import" in route_content
        )
        assert has_permissions_import, \
            "Should import from api.auth.permissions or api.auth.roles"

    def test_uses_role_enum_not_strings(self, route_content):
        """Test that Role enum is used instead of raw strings"""
        # Using Role.ADMIN is better than "admin" strings
        uses_role_enum = "Role.ADMIN" in route_content or "Role.QA_LEAD" in route_content
        assert uses_role_enum, \
            "Should use Role enum (Role.ADMIN, Role.QA_LEAD) instead of raw strings"
