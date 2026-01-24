"""
Test suite for human_validation API routes RBAC

Validates that RBAC is properly implemented for human validation workflow endpoints.
"""

import pytest
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
ROUTES_DIR = PROJECT_ROOT / "backend" / "api" / "routes"
HUMAN_VALIDATION_ROUTES_FILE = ROUTES_DIR / "human_validation.py"


class TestHumanValidationRoutesFileExists:
    """Test that human_validation routes file exists"""

    def test_routes_file_exists(self):
        """Test that human_validation.py exists"""
        assert HUMAN_VALIDATION_ROUTES_FILE.exists(), "human_validation.py should exist"
        assert HUMAN_VALIDATION_ROUTES_FILE.is_file(), "human_validation.py should be a file"


# =============================================================================
# RBAC Behavior Tests
# =============================================================================


class TestRBACBehavior:
    """Test that RBAC is properly implemented for validation workflow endpoints"""

    @pytest.fixture
    def route_content(self):
        """Read the human_validation.py route file content"""
        return HUMAN_VALIDATION_ROUTES_FILE.read_text()

    def test_imports_role_enum(self, route_content):
        """Test that routes import Role enum for RBAC"""
        assert "from api.auth.roles import Role" in route_content, (
            "Should import Role enum for RBAC"
        )

    def test_defines_validator_roles(self, route_content):
        """Test that routes define roles for validation operations"""
        has_role_definition = (
            "_VALIDATION_ROLES" in route_content or
            "_VALIDATOR_ROLES" in route_content
        )
        assert has_role_definition, (
            "Should define role constants for validation operations"
        )

    def test_claim_endpoint_requires_role_check(self, route_content):
        """Test that POST /{id}/claim endpoint has role authorization"""
        assert "async def claim_validation_task" in route_content, (
            "Should have claim_validation_task"
        )

        func_start = route_content.find("async def claim_validation_task")
        func_end = route_content.find("async def", func_start + 1)
        if func_end == -1:
            func_end = len(route_content)
        func_body = route_content[func_start:func_end]

        has_role_check = (
            "_ensure_" in func_body or
            "require_role" in func_body
        )
        assert has_role_check, (
            "claim_validation_task must have role check - "
            "validator role required for validation operations"
        )

    def test_submit_endpoint_requires_role_check(self, route_content):
        """Test that POST /{id}/submit endpoint has role authorization"""
        assert "async def submit_validation_decision" in route_content, (
            "Should have submit_validation_decision"
        )

        func_start = route_content.find("async def submit_validation_decision")
        func_end = route_content.find("async def", func_start + 1)
        if func_end == -1:
            func_end = len(route_content)
        func_body = route_content[func_start:func_end]

        has_role_check = (
            "_ensure_" in func_body or
            "require_role" in func_body
        )
        assert has_role_check, (
            "submit_validation_decision must have role check - "
            "validator role required for validation operations"
        )

    def test_release_endpoint_requires_role_check(self, route_content):
        """Test that POST /{id}/release endpoint has role authorization"""
        assert "async def release_validation_task" in route_content, (
            "Should have release_validation_task"
        )

        func_start = route_content.find("async def release_validation_task")
        func_end = route_content.find("async def", func_start + 1)
        if func_end == -1:
            func_end = len(route_content)
        func_body = route_content[func_start:func_end]

        has_role_check = (
            "_ensure_" in func_body or
            "require_role" in func_body
        )
        assert has_role_check, (
            "release_validation_task must have role check - "
            "validator role required for validation operations"
        )


class TestReadEndpointsAllowAllAuthenticatedUsers:
    """Test that read endpoints allow any authenticated user"""

    @pytest.fixture
    def route_content(self):
        """Read the human_validation.py route file content"""
        return HUMAN_VALIDATION_ROUTES_FILE.read_text()

    def test_get_queue_allows_any_authenticated_user(self, route_content):
        """Test that GET /queue allows any authenticated user"""
        func_start = route_content.find("async def get_next_validation_task")
        func_end = route_content.find("async def", func_start + 1)
        func_body = route_content[func_start:func_end]

        assert "current_user" in func_body, "Should use current_user dependency"

        has_role_restriction = (
            "_ensure_" in func_body or
            "require_role" in func_body
        )
        assert not has_role_restriction, (
            "get_next_validation_task should allow any authenticated user"
        )

    def test_get_stats_allows_any_authenticated_user(self, route_content):
        """Test that GET /stats allows any authenticated user"""
        func_start = route_content.find("async def get_queue_statistics")
        func_end = route_content.find("async def", func_start + 1)
        func_body = route_content[func_start:func_end]

        assert "current_user" in func_body, "Should use current_user dependency"

        has_role_restriction = (
            "_ensure_" in func_body or
            "require_role" in func_body
        )
        assert not has_role_restriction, (
            "get_queue_statistics should allow any authenticated user"
        )

    def test_get_validator_stats_allows_any_authenticated_user(self, route_content):
        """Test that GET /validators/stats allows any authenticated user"""
        func_start = route_content.find("async def get_validator_statistics")
        func_end = route_content.find("async def", func_start + 1)
        if func_end == -1:
            func_end = len(route_content)
        func_body = route_content[func_start:func_end]

        assert "current_user" in func_body, "Should use current_user dependency"

        has_role_restriction = (
            "_ensure_" in func_body or
            "require_role" in func_body
        )
        assert not has_role_restriction, (
            "get_validator_statistics should allow any authenticated user"
        )


class TestRBACHelperFunction:
    """Test that RBAC helper function is properly defined"""

    @pytest.fixture
    def route_content(self):
        """Read the human_validation.py route file content"""
        return HUMAN_VALIDATION_ROUTES_FILE.read_text()

    def test_has_validator_role_check_helper(self, route_content):
        """Test that a helper function exists for validator role checks"""
        has_helper = "_ensure_can_validate" in route_content
        assert has_helper, (
            "Should have _ensure_can_validate helper function"
        )

    def test_helper_raises_403_for_unauthorized(self, route_content):
        """Test that helper function raises 403 for unauthorized users"""
        assert "HTTP_403_FORBIDDEN" in route_content, (
            "Should raise 403 for unauthorized access"
        )
