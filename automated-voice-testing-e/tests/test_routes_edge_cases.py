"""
Test suite for edge_cases API routes RBAC

Validates that RBAC is properly implemented for edge case management endpoints.
"""

import pytest
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
ROUTES_DIR = PROJECT_ROOT / "backend" / "api" / "routes"
EDGE_CASES_ROUTES_FILE = ROUTES_DIR / "edge_cases.py"


class TestEdgeCasesRoutesFileExists:
    """Test that edge_cases routes file exists"""

    def test_routes_file_exists(self):
        """Test that edge_cases.py exists"""
        assert EDGE_CASES_ROUTES_FILE.exists(), "edge_cases.py should exist"
        assert EDGE_CASES_ROUTES_FILE.is_file(), "edge_cases.py should be a file"


# =============================================================================
# RBAC Behavior Tests
# =============================================================================


class TestRBACBehavior:
    """Test that RBAC is properly implemented for all endpoints"""

    @pytest.fixture
    def route_content(self):
        """Read the edge_cases.py route file content"""
        return EDGE_CASES_ROUTES_FILE.read_text()

    def test_imports_role_enum(self, route_content):
        """Test that routes import Role enum for RBAC"""
        assert "from api.auth.roles import Role" in route_content, (
            "Should import Role enum for RBAC"
        )

    def test_defines_mutation_roles(self, route_content):
        """Test that routes define roles for mutation operations"""
        has_role_definition = (
            "_EDGE_CASE_MUTATION_ROLES" in route_content or
            "_MUTATION_ROLES" in route_content
        )
        assert has_role_definition, (
            "Should define role constants for mutation operations"
        )

    def test_create_endpoint_requires_role_check(self, route_content):
        """Test that POST / (create) endpoint has role authorization"""
        assert "async def create_edge_case_endpoint" in route_content, (
            "Should have create_edge_case_endpoint"
        )

        func_start = route_content.find("async def create_edge_case_endpoint")
        func_end = route_content.find("async def", func_start + 1)
        if func_end == -1:
            func_end = len(route_content)
        func_body = route_content[func_start:func_end]

        has_role_check = (
            "_ensure_" in func_body or
            "require_role" in func_body
        )
        assert has_role_check, (
            "create_edge_case_endpoint must have role check - "
            "admin or qa_lead required for mutations"
        )

    def test_update_endpoint_requires_role_check(self, route_content):
        """Test that PATCH /{id} (update) endpoint has role authorization"""
        assert "async def update_edge_case_endpoint" in route_content, (
            "Should have update_edge_case_endpoint"
        )

        func_start = route_content.find("async def update_edge_case_endpoint")
        func_end = route_content.find("async def", func_start + 1)
        if func_end == -1:
            func_end = len(route_content)
        func_body = route_content[func_start:func_end]

        has_role_check = (
            "_ensure_" in func_body or
            "require_role" in func_body
        )
        assert has_role_check, (
            "update_edge_case_endpoint must have role check - "
            "admin or qa_lead required for mutations"
        )

    def test_categorize_endpoint_requires_role_check(self, route_content):
        """Test that POST /{id}/categorize endpoint has role authorization"""
        assert "async def categorize_edge_case_endpoint" in route_content, (
            "Should have categorize_edge_case_endpoint"
        )

        func_start = route_content.find("async def categorize_edge_case_endpoint")
        func_end = route_content.find("async def", func_start + 1)
        if func_end == -1:
            func_end = len(route_content)
        func_body = route_content[func_start:func_end]

        has_role_check = (
            "_ensure_" in func_body or
            "require_role" in func_body
        )
        assert has_role_check, (
            "categorize_edge_case_endpoint must have role check - "
            "admin or qa_lead required for mutations"
        )

    def test_delete_endpoint_requires_role_check(self, route_content):
        """Test that DELETE /{id} endpoint has role authorization"""
        assert "async def delete_edge_case_endpoint" in route_content, (
            "Should have delete_edge_case_endpoint"
        )

        func_start = route_content.find("async def delete_edge_case_endpoint")
        func_end = route_content.find("async def", func_start + 1)
        if func_end == -1:
            func_end = len(route_content)
        func_body = route_content[func_start:func_end]

        has_role_check = (
            "_ensure_" in func_body or
            "require_role" in func_body
        )
        assert has_role_check, (
            "delete_edge_case_endpoint must have role check - "
            "admin or qa_lead required for mutations"
        )


class TestReadEndpointsAllowAllAuthenticatedUsers:
    """Test that read endpoints allow any authenticated user"""

    @pytest.fixture
    def route_content(self):
        """Read the edge_cases.py route file content"""
        return EDGE_CASES_ROUTES_FILE.read_text()

    def test_get_endpoint_allows_any_authenticated_user(self, route_content):
        """Test that GET /{id} allows any authenticated user"""
        func_start = route_content.find("async def get_edge_case_endpoint")
        func_end = route_content.find("async def", func_start + 1)
        func_body = route_content[func_start:func_end]

        assert "current_user" in func_body, "Should use current_user dependency"

        has_role_restriction = (
            "_ensure_" in func_body or
            "require_role" in func_body
        )
        assert not has_role_restriction, (
            "get_edge_case_endpoint should allow any authenticated user"
        )

    def test_list_endpoint_allows_any_authenticated_user(self, route_content):
        """Test that GET / (list) allows any authenticated user"""
        func_start = route_content.find("async def list_edge_cases_endpoint")
        func_end = route_content.find("async def", func_start + 1)
        func_body = route_content[func_start:func_end]

        assert "current_user" in func_body, "Should use current_user dependency"

        has_role_restriction = (
            "_ensure_" in func_body or
            "require_role" in func_body
        )
        assert not has_role_restriction, (
            "list_edge_cases_endpoint should allow any authenticated user"
        )

    def test_search_endpoint_allows_any_authenticated_user(self, route_content):
        """Test that GET /search allows any authenticated user"""
        func_start = route_content.find("async def search_edge_cases_endpoint")
        func_end = route_content.find("async def", func_start + 1)
        func_body = route_content[func_start:func_end]

        assert "current_user" in func_body, "Should use current_user dependency"

        has_role_restriction = (
            "_ensure_" in func_body or
            "require_role" in func_body
        )
        assert not has_role_restriction, (
            "search_edge_cases_endpoint should allow any authenticated user"
        )


class TestRBACHelperFunction:
    """Test that RBAC helper function is properly defined"""

    @pytest.fixture
    def route_content(self):
        """Read the edge_cases.py route file content"""
        return EDGE_CASES_ROUTES_FILE.read_text()

    def test_has_mutation_role_check_helper(self, route_content):
        """Test that a helper function exists for mutation role checks"""
        has_helper = "_ensure_can_mutate_edge_case" in route_content
        assert has_helper, (
            "Should have _ensure_can_mutate_edge_case helper function"
        )

    def test_helper_raises_403_for_unauthorized(self, route_content):
        """Test that helper function raises 403 for unauthorized users"""
        assert "HTTP_403_FORBIDDEN" in route_content, (
            "Should raise 403 for unauthorized access"
        )
