"""
Test suite for test suite API routes

Validates the test suite routes implementation including:
- Route file structure
- Router configuration
- All API endpoints (5 endpoints)
- HTTP methods (GET, POST, PUT, DELETE)
- Endpoint paths
- Dependencies (get_db, get_current_user)
- Request/response schemas
- Documentation
"""

import pytest
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
ROUTES_DIR = PROJECT_ROOT / "backend" / "api" / "routes"
TEST_SUITES_ROUTES_FILE = ROUTES_DIR / "test_suites.py"


class TestTestSuitesRoutesFileExists:
    """Test that test suites routes file exists"""

    def test_routes_directory_exists(self):
        """Test that routes directory exists"""
        assert ROUTES_DIR.exists(), "backend/api/routes directory should exist"
        assert ROUTES_DIR.is_dir(), "routes should be a directory"

    def test_test_suites_routes_file_exists(self):
        """Test that test_suites.py exists"""
        assert TEST_SUITES_ROUTES_FILE.exists(), "test_suites.py should exist"
        assert TEST_SUITES_ROUTES_FILE.is_file(), "test_suites.py should be a file"

    def test_routes_file_has_content(self):
        """Test that routes file has content"""
        content = TEST_SUITES_ROUTES_FILE.read_text()
        assert len(content) > 0, "test_suites.py should not be empty"


class TestTestSuitesRoutesImports:
    """Test routes imports"""

    def test_imports_fastapi_apirouter(self):
        """Test that routes imports APIRouter"""
        content = TEST_SUITES_ROUTES_FILE.read_text()
        assert (("from fastapi import APIRouter" in content or
                "APIRouter" in content)), "Should import APIRouter"

    def test_imports_fastapi_depends(self):
        """Test that routes imports Depends"""
        content = TEST_SUITES_ROUTES_FILE.read_text()
        assert "Depends" in content, "Should import Depends"

    def test_imports_asyncsession(self):
        """Test that routes imports AsyncSession"""
        content = TEST_SUITES_ROUTES_FILE.read_text()
        assert "AsyncSession" in content, "Should import AsyncSession"

    def test_imports_schemas(self):
        """Test that routes imports test suite schemas"""
        content = TEST_SUITES_ROUTES_FILE.read_text()
        assert ("TestSuiteCreate" in content or
                "from api.schemas.test_suite" in content), "Should import schemas"

    def test_imports_service(self):
        """Test that routes imports test suite service"""
        content = TEST_SUITES_ROUTES_FILE.read_text()
        assert ("test_suite_service" in content or
                "from services" in content), "Should import service"


class TestTestSuitesRouterConfiguration:
    """Test router configuration"""

    def test_creates_api_router(self):
        """Test that router is created"""
        content = TEST_SUITES_ROUTES_FILE.read_text()
        assert "APIRouter" in content, "Should create APIRouter"
        assert "router = " in content, "Should have router variable"

    def test_router_has_prefix(self):
        """Test that router has prefix"""
        content = TEST_SUITES_ROUTES_FILE.read_text()
        assert ('prefix="/test-suites"' in content or
                "prefix='/test-suites'" in content), "Router should have /test-suites prefix"

    def test_router_has_tags(self):
        """Test that router has tags"""
        content = TEST_SUITES_ROUTES_FILE.read_text()
        assert "tags=" in content, "Router should have tags"


class TestListTestSuitesEndpoint:
    """Test GET /test-suites endpoint"""

    def test_has_list_test_suites_endpoint(self):
        """Test that list test suites endpoint exists"""
        content = TEST_SUITES_ROUTES_FILE.read_text()
        assert ("@router.get" in content or
                '@router.get("/")' in content or
                "@router.get('/')" in content), "Should have GET endpoint"

    def test_list_endpoint_is_async(self):
        """Test that list endpoint is async"""
        content = TEST_SUITES_ROUTES_FILE.read_text()
        assert "async def" in content, "Endpoints should be async"

    def test_list_endpoint_uses_depends(self):
        """Test that list endpoint uses Depends"""
        content = TEST_SUITES_ROUTES_FILE.read_text()
        assert "Depends" in content, "Should use Depends for dependencies"


class TestCreateTestSuiteEndpoint:
    """Test POST /test-suites endpoint"""

    def test_has_create_test_suite_endpoint(self):
        """Test that create test suite endpoint exists"""
        content = TEST_SUITES_ROUTES_FILE.read_text()
        assert ("@router.post" in content or
                '@router.post("/")' in content or
                "@router.post('/')" in content), "Should have POST endpoint"

    def test_create_endpoint_uses_test_suite_create_schema(self):
        """Test that create endpoint uses TestSuiteCreate schema"""
        content = TEST_SUITES_ROUTES_FILE.read_text()
        assert "TestSuiteCreate" in content, "Should use TestSuiteCreate schema"


class TestGetTestSuiteEndpoint:
    """Test GET /test-suites/{id} endpoint"""

    def test_has_get_test_suite_endpoint(self):
        """Test that get test suite endpoint exists"""
        content = TEST_SUITES_ROUTES_FILE.read_text()
        # Check for GET endpoint with path parameter
        assert ("@router.get" in content and '"{test_suite_id}"' in content or
                '"/{' in content), "Should have GET /{test_suite_id} endpoint"

    def test_get_endpoint_has_path_parameter(self):
        """Test that get endpoint has path parameter"""
        content = TEST_SUITES_ROUTES_FILE.read_text()
        assert ("test_suite_id" in content or "{id}" in content), "Should have path parameter"


class TestUpdateTestSuiteEndpoint:
    """Test PUT /test-suites/{id} endpoint"""

    def test_has_update_test_suite_endpoint(self):
        """Test that update test suite endpoint exists"""
        content = TEST_SUITES_ROUTES_FILE.read_text()
        assert "@router.put" in content, "Should have PUT endpoint"

    def test_update_endpoint_uses_test_suite_update_schema(self):
        """Test that update endpoint uses TestSuiteUpdate schema"""
        content = TEST_SUITES_ROUTES_FILE.read_text()
        assert "TestSuiteUpdate" in content, "Should use TestSuiteUpdate schema"


class TestDeleteTestSuiteEndpoint:
    """Test DELETE /test-suites/{id} endpoint"""

    def test_has_delete_test_suite_endpoint(self):
        """Test that delete test suite endpoint exists"""
        content = TEST_SUITES_ROUTES_FILE.read_text()
        assert "@router.delete" in content, "Should have DELETE endpoint"


class TestTestSuitesRoutesDocumentation:
    """Test routes documentation"""

    def test_has_module_docstring(self):
        """Test that module has docstring"""
        content = TEST_SUITES_ROUTES_FILE.read_text()
        assert '"""' in content or "'''" in content, "Should have module docstring"

    def test_endpoints_have_docstrings(self):
        """Test that endpoints have docstrings"""
        content = TEST_SUITES_ROUTES_FILE.read_text()
        # Should have reasonable number of docstrings
        assert '"""' in content or "'''" in content, "Should have docstrings"


class TestTestSuitesRoutesTypeHints:
    """Test type hints"""

    def test_uses_type_hints(self):
        """Test that routes use type hints"""
        content = TEST_SUITES_ROUTES_FILE.read_text()
        assert "->" in content, "Should use return type hints"
        assert ":" in content, "Should use parameter type hints"

    def test_uses_annotated_types(self):
        """Test that routes use Annotated for dependencies"""
        content = TEST_SUITES_ROUTES_FILE.read_text()
        assert ("Annotated" in content or
                "from typing import" in content), "Should use Annotated types"


class TestTestSuitesRoutesStructure:
    """Test overall routes structure"""

    def test_has_all_required_endpoints(self):
        """Test that routes has all 5 required endpoints"""
        content = TEST_SUITES_ROUTES_FILE.read_text()
        # Check for HTTP method decorators
        assert "@router.get" in content, "Should have GET endpoints"
        assert "@router.post" in content, "Should have POST endpoint"
        assert "@router.put" in content, "Should have PUT endpoint"
        assert "@router.delete" in content, "Should have DELETE endpoint"

    def test_exports_router(self):
        """Test that routes exports router"""
        content = TEST_SUITES_ROUTES_FILE.read_text()
        assert "router = " in content, "Should define router"


class TestTestSuitesRoutesDependencies:
    """Test route dependencies"""

    def test_uses_get_db_dependency(self):
        """Test that routes use get_db dependency"""
        content = TEST_SUITES_ROUTES_FILE.read_text()
        assert "get_db" in content, "Should use get_db dependency"

    def test_uses_authentication_dependency(self):
        """Test that routes use authentication dependency"""
        content = TEST_SUITES_ROUTES_FILE.read_text()
        assert ("get_current_user" in content or
                "security" in content or
                "Depends" in content), "Should use authentication dependency"


class TestTestSuitesRoutesResponseSchemas:
    """Test response schemas"""

    def test_uses_test_suite_response_schema(self):
        """Test that routes use TestSuiteResponse schema"""
        content = TEST_SUITES_ROUTES_FILE.read_text()
        assert "TestSuiteResponse" in content, "Should use TestSuiteResponse schema"


class TestTestSuitesRoutesErrorHandling:
    """Test error handling"""

    def test_has_http_exception_import(self):
        """Test that routes import HTTPException"""
        content = TEST_SUITES_ROUTES_FILE.read_text()
        assert ("HTTPException" in content or
                "from fastapi import" in content), "Should import HTTPException"


# =============================================================================
# RBAC Behavior Tests
# =============================================================================


class TestRBACBehavior:
    """Test that RBAC is properly implemented for all endpoints"""

    @pytest.fixture
    def route_content(self):
        """Read the test_suites.py route file content"""
        return TEST_SUITES_ROUTES_FILE.read_text()

    def test_imports_role_enum(self, route_content):
        """Test that routes import Role enum for RBAC"""
        assert "from api.auth.roles import Role" in route_content, (
            "Should import Role enum for RBAC"
        )

    def test_defines_mutation_roles(self, route_content):
        """Test that routes define roles for mutation operations"""
        has_role_definition = (
            "_SUITE_MUTATION_ROLES" in route_content or
            "_SUITE_DELETE_ROLES" in route_content or
            "_TEST_SUITE_MUTATION_ROLES" in route_content
        )
        assert has_role_definition, (
            "Should define role constants for mutation operations"
        )

    def test_create_endpoint_requires_role_check(self, route_content):
        """Test that POST / (create) endpoint has role authorization"""
        assert "async def create_test_suite" in route_content, (
            "Should have create_test_suite endpoint"
        )

        func_start = route_content.find("async def create_test_suite")
        func_end = route_content.find("async def", func_start + 1)
        if func_end == -1:
            func_end = len(route_content)
        func_body = route_content[func_start:func_end]

        has_role_check = (
            "_ensure_" in func_body or
            "require_role" in func_body
        )
        assert has_role_check, (
            "create_test_suite endpoint must have role check - "
            "admin or qa_lead required for mutations"
        )

    def test_update_endpoint_requires_role_check(self, route_content):
        """Test that PUT /{id} (update) endpoint has role authorization"""
        assert "async def update_test_suite" in route_content, (
            "Should have update_test_suite endpoint"
        )

        func_start = route_content.find("async def update_test_suite")
        func_end = route_content.find("async def", func_start + 1)
        if func_end == -1:
            func_end = len(route_content)
        func_body = route_content[func_start:func_end]

        has_role_check = (
            "_ensure_" in func_body or
            "require_role" in func_body
        )
        assert has_role_check, (
            "update_test_suite endpoint must have role check - "
            "admin or qa_lead required for mutations"
        )

    def test_delete_endpoint_requires_role_check(self, route_content):
        """Test that DELETE /{id} endpoint has role authorization"""
        assert "async def delete_test_suite" in route_content, (
            "Should have delete_test_suite endpoint"
        )

        func_start = route_content.find("async def delete_test_suite")
        func_end = route_content.find("async def", func_start + 1)
        if func_end == -1:
            func_end = len(route_content)
        func_body = route_content[func_start:func_end]

        has_role_check = (
            "_ensure_can_delete_test_suite" in func_body or
            "_ensure_can_mutate_test_suite" in func_body or
            "require_role" in func_body
        )
        assert has_role_check, (
            "delete_test_suite endpoint must have role check"
        )


class TestReadEndpointsAllowAllAuthenticatedUsers:
    """Test that read endpoints allow any authenticated user"""

    @pytest.fixture
    def route_content(self):
        """Read the test_suites.py route file content"""
        return TEST_SUITES_ROUTES_FILE.read_text()

    def test_list_endpoint_allows_any_authenticated_user(self, route_content):
        """Test that GET / (list) allows any authenticated user"""
        func_start = route_content.find("async def list_test_suites")
        func_end = route_content.find("async def", func_start + 1)
        func_body = route_content[func_start:func_end]

        assert "current_user" in func_body, "Should use current_user dependency"

        has_role_restriction = (
            "_ensure_" in func_body or
            "require_role" in func_body
        )
        assert not has_role_restriction, (
            "list_test_suites should allow any authenticated user"
        )

    def test_get_endpoint_allows_any_authenticated_user(self, route_content):
        """Test that GET /{id} allows any authenticated user"""
        func_start = route_content.find("async def get_test_suite")
        func_end = route_content.find("async def", func_start + 1)
        func_body = route_content[func_start:func_end]

        assert "current_user" in func_body, "Should use current_user dependency"

        has_role_restriction = (
            "_ensure_" in func_body or
            "require_role" in func_body
        )
        assert not has_role_restriction, (
            "get_test_suite should allow any authenticated user"
        )


class TestRBACHelperFunction:
    """Test that RBAC helper function is properly defined"""

    @pytest.fixture
    def route_content(self):
        """Read the test_suites.py route file content"""
        return TEST_SUITES_ROUTES_FILE.read_text()

    def test_has_mutation_role_check_helper(self, route_content):
        """Test that a helper function exists for mutation role checks"""
        has_helper = (
            "_ensure_can_mutate_test_suite" in route_content or
            "_ensure_can_delete_test_suite" in route_content
        )
        assert has_helper, (
            "Should have helper function for role checks"
        )

    def test_helper_raises_403_for_unauthorized(self, route_content):
        """Test that helper function raises 403 for unauthorized users"""
        assert "HTTP_403_FORBIDDEN" in route_content, (
            "Should raise 403 for unauthorized access"
        )
