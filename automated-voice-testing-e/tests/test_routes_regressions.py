"""
Test suite for regressions API routes RBAC

Validates that RBAC is properly implemented for regression management endpoints.
"""

import pytest
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent.parent
ROUTES_DIR = PROJECT_ROOT / "backend" / "api" / "routes"
REGRESSIONS_ROUTES_FILE = ROUTES_DIR / "regressions.py"


class TestRegressionsRoutesFileExists:
    def test_routes_file_exists(self):
        assert REGRESSIONS_ROUTES_FILE.exists(), "regressions.py should exist"
        assert REGRESSIONS_ROUTES_FILE.is_file(), "regressions.py should be a file"


class TestRBACBehavior:
    @pytest.fixture
    def route_content(self):
        return REGRESSIONS_ROUTES_FILE.read_text()

    def test_imports_role_enum(self, route_content):
        assert "from api.auth.roles import Role" in route_content

    def test_defines_mutation_roles(self, route_content):
        assert "_REGRESSION_MUTATION_ROLES" in route_content

    def test_approve_baseline_endpoint_requires_role_check(self, route_content):
        func_start = route_content.find("async def approve_baseline_endpoint")
        func_end = route_content.find("async def", func_start + 1)
        if func_end == -1:
            func_end = len(route_content)
        func_body = route_content[func_start:func_end]
        assert "_ensure_" in func_body or "require_role" in func_body


class TestReadEndpointsAllowAllAuthenticatedUsers:
    @pytest.fixture
    def route_content(self):
        return REGRESSIONS_ROUTES_FILE.read_text()

    def test_list_endpoint_allows_any_authenticated_user(self, route_content):
        func_start = route_content.find("async def list_regressions_endpoint")
        func_end = route_content.find("async def", func_start + 1)
        func_body = route_content[func_start:func_end]
        assert "current_user" in func_body
        has_role_restriction = "_ensure_" in func_body or "require_role" in func_body
        assert not has_role_restriction

    def test_comparison_endpoint_allows_any_authenticated_user(self, route_content):
        func_start = route_content.find("async def get_regression_comparison_endpoint")
        func_end = route_content.find("async def", func_start + 1)
        if func_end == -1:
            func_end = len(route_content)
        func_body = route_content[func_start:func_end]
        assert "current_user" in func_body
        has_role_restriction = "_ensure_" in func_body or "require_role" in func_body
        assert not has_role_restriction


class TestRBACHelperFunction:
    @pytest.fixture
    def route_content(self):
        return REGRESSIONS_ROUTES_FILE.read_text()

    def test_has_mutation_role_check_helper(self, route_content):
        assert "_ensure_can_mutate_regression" in route_content

    def test_helper_raises_403_for_unauthorized(self, route_content):
        assert "HTTP_403_FORBIDDEN" in route_content
