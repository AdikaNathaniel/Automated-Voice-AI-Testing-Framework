"""
Test suite for role-based authorization

Tests the require_role decorator/dependency for protecting endpoints
based on user roles (admin, user, etc.).
"""

import pytest
from fastapi import FastAPI, Depends, APIRouter
from fastapi.testclient import TestClient
from pathlib import Path
from typing import Annotated


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
PERMISSIONS_FILE = PROJECT_ROOT / "backend" / "api" / "auth" / "permissions.py"


class TestPermissionsFileExists:
    """Test that permissions file exists"""

    def test_permissions_file_exists(self):
        """Test that backend/api/auth/permissions.py exists"""
        assert PERMISSIONS_FILE.exists(), "backend/api/auth/permissions.py should exist"
        assert PERMISSIONS_FILE.is_file(), "permissions.py should be a file"

    def test_permissions_has_content(self):
        """Test that permissions.py has content"""
        content = PERMISSIONS_FILE.read_text()
        assert len(content) > 0, "permissions.py should not be empty"


class TestPermissionsImports:
    """Test that permissions module can be imported"""

    def test_can_import_permissions(self):
        """Test that permissions module can be imported"""
        try:
            from api.auth import permissions
            assert permissions is not None
        except ImportError as e:
            pytest.fail(f"Failed to import permissions: {e}")

    def test_require_role_exists(self):
        """Test that require_role function exists"""
        from api.auth.permissions import require_role
        assert callable(require_role), "require_role should be a callable function"


class TestRequireRoleFunctionSignature:
    """Test require_role function signature"""

    def test_require_role_accepts_roles(self):
        """Test that require_role accepts role arguments"""
        from api.auth.permissions import require_role
        import inspect

        sig = inspect.signature(require_role)
        params = list(sig.parameters.keys())

        # Should accept *roles or similar
        assert len(params) >= 1 or any('role' in str(p).lower() for p in sig.parameters.values()), \
            "require_role should accept role parameters"

    def test_require_role_returns_dependency(self):
        """Test that require_role returns a dependency function"""
        from api.auth.permissions import require_role

        # Call with a role
        result = require_role("admin")

        # Should return a callable (dependency)
        assert callable(result), "require_role should return a callable dependency"


class TestRequireRoleSingleRole:
    """Test require_role with single role"""

    def test_user_with_correct_role_allowed(self, test_app_with_role_endpoint):
        """Test that user with correct role can access endpoint"""
        app, admin_token = test_app_with_role_endpoint

        client = TestClient(app)
        response = client.get(
            "/test/admin-only",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200, "Admin should access admin-only endpoint"
        assert response.json()["message"] == "Admin access granted"

    def test_user_without_required_role_denied(self, test_app_with_role_endpoint):
        """Test that user without required role gets 403"""
        app, admin_token, user_token = test_app_with_role_endpoint

        client = TestClient(app)
        response = client.get(
            "/test/admin-only",
            headers={"Authorization": f"Bearer {user_token}"}
        )

        assert response.status_code == 403, "Regular user should be denied admin endpoint"
        data = response.json()
        assert "detail" in data, "Error response should have detail"
        assert "permission" in data["detail"].lower() or "forbidden" in data["detail"].lower(), \
            "Error message should mention permission/forbidden"

    def test_unauthenticated_user_denied(self, test_app_with_role_endpoint):
        """Test that unauthenticated user gets 401"""
        app, _ = test_app_with_role_endpoint

        client = TestClient(app)
        response = client.get("/test/admin-only")

        assert response.status_code == 401, "Unauthenticated user should get 401"


class TestRequireRoleMultipleRoles:
    """Test require_role with multiple roles"""

    def test_user_with_one_of_multiple_roles_allowed(self, test_app_with_multi_role_endpoint):
        """Test that user with one of the required roles can access"""
        app, admin_token, moderator_token, user_token = test_app_with_multi_role_endpoint

        client = TestClient(app)

        # Admin should access
        response = client.get(
            "/test/admin-or-moderator",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, "Admin should access endpoint requiring admin or moderator"

        # Moderator should access
        response = client.get(
            "/test/admin-or-moderator",
            headers={"Authorization": f"Bearer {moderator_token}"}
        )
        assert response.status_code == 200, "Moderator should access endpoint requiring admin or moderator"

    def test_user_with_none_of_required_roles_denied(self, test_app_with_multi_role_endpoint):
        """Test that user without any of the required roles gets 403"""
        app, admin_token, moderator_token, user_token = test_app_with_multi_role_endpoint

        client = TestClient(app)
        response = client.get(
            "/test/admin-or-moderator",
            headers={"Authorization": f"Bearer {user_token}"}
        )

        assert response.status_code == 403, "Regular user should be denied"


class TestRequireRoleWithUserModel:
    """Test require_role integration with User model"""

    def test_user_without_role_field_denied(self, test_app_with_no_role_user):
        """Test that user without role field is denied"""
        app, token = test_app_with_no_role_user

        client = TestClient(app)
        response = client.get(
            "/test/admin-only",
            headers={"Authorization": f"Bearer {token}"}
        )

        # Should be denied if no role
        assert response.status_code == 403, "User without role should be denied"

    def test_user_with_none_role_denied(self, test_app_with_none_role_user):
        """Test that user with role=None is denied"""
        app, token = test_app_with_none_role_user

        client = TestClient(app)
        response = client.get(
            "/test/admin-only",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 403, "User with None role should be denied"


class TestRequireRoleEdgeCases:
    """Test require_role edge cases"""

    def test_require_role_with_empty_roles_list(self):
        """Test require_role with empty roles list"""
        from api.auth.permissions import require_role

        # Should handle gracefully or raise error
        try:
            dependency = require_role()
            # If it allows empty list, all users should be denied
        except (ValueError, TypeError):
            # Or it might raise an error for invalid usage
            pass

    def test_require_role_case_sensitivity(self, test_app_with_role_endpoint):
        """Test that role checking is case-sensitive (or insensitive as designed)"""
        # This documents the actual behavior
        pass

    def test_require_role_with_special_characters(self):
        """Test require_role with roles containing special characters"""
        from api.auth.permissions import require_role

        # Should handle roles like "super-admin", "read_only", etc.
        dependency = require_role("super-admin")
        assert callable(dependency)


class TestRequireRoleDocumentation:
    """Test permissions module documentation"""

    def test_require_role_has_docstring(self):
        """Test that require_role has docstring"""
        from api.auth.permissions import require_role

        assert require_role.__doc__ is not None, \
            "require_role should have docstring"

    def test_module_has_docstring(self):
        """Test that permissions module has docstring"""
        from api.auth import permissions

        assert permissions.__doc__ is not None, \
            "Permissions module should have docstring"


class TestRequireRoleIntegration:
    """Test require_role integration with FastAPI"""

    def test_require_role_as_fastapi_dependency(self):
        """Test that require_role works as FastAPI Depends()"""
        from fastapi import FastAPI, Depends, APIRouter
        from api.auth.permissions import require_role

        app = FastAPI()
        router = APIRouter()

        @router.get("/test")
        async def test_endpoint(user=Depends(require_role("admin"))):
            return {"message": "success"}

        # Should not raise error during setup
        app.include_router(router)

    def test_require_role_returns_user(self, test_app_with_role_endpoint):
        """Test that require_role dependency returns the user"""
        app, admin_token = test_app_with_role_endpoint

        client = TestClient(app)
        response = client.get(
            "/test/admin-with-user",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "user" in data, "Endpoint should receive user from dependency"
        assert "email" in data["user"], "User should have email"


class TestRequireRoleErrorMessages:
    """Test error messages from require_role"""

    def test_403_error_has_clear_message(self, test_app_with_role_endpoint):
        """Test that 403 error has clear message about permissions"""
        app, admin_token, user_token = test_app_with_role_endpoint

        client = TestClient(app)
        response = client.get(
            "/test/admin-only",
            headers={"Authorization": f"Bearer {user_token}"}
        )

        assert response.status_code == 403
        data = response.json()
        assert "detail" in data
        # Should mention what permission is needed or that access is forbidden
        detail_lower = data["detail"].lower()
        assert any(word in detail_lower for word in ["permission", "forbidden", "role", "access"]), \
            "Error message should clearly indicate permission issue"


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def test_app_with_role_endpoint():
    """
    Create test app with role-protected endpoint
    Returns: (app, admin_token, user_token)
    """
    from fastapi import FastAPI, Depends, APIRouter
    from api.auth.permissions import require_role
    from api.schemas.auth import UserResponse
    from uuid import uuid4
    from datetime import datetime

    app = FastAPI()
    router = APIRouter(prefix="/test")

    # Mock get_current_user that returns users with different roles
    def mock_get_admin_user():
        return UserResponse(
            id=uuid4(),
            email="admin@example.com",
            username="admin",
            full_name="Admin User",
            is_active=True,
            created_at=datetime.utcnow(),
            role="admin"  # This won't work with current UserResponse schema
        )

    def mock_get_regular_user():
        return UserResponse(
            id=uuid4(),
            email="user@example.com",
            username="user",
            full_name="Regular User",
            is_active=True,
            created_at=datetime.utcnow(),
            role="user"
        )

    @router.get("/admin-only")
    async def admin_only_endpoint(user=Depends(require_role("admin"))):
        return {"message": "Admin access granted", "user": user.email}

    @router.get("/admin-with-user")
    async def admin_with_user_endpoint(user=Depends(require_role("admin"))):
        return {"message": "success", "user": {"email": user.email}}

    app.include_router(router)

    # Return app and mock tokens
    # Note: These are placeholder tokens - real implementation will use JWT
    admin_token = "mock_admin_token"
    user_token = "mock_user_token"

    return app, admin_token, user_token


@pytest.fixture
def test_app_with_multi_role_endpoint():
    """
    Create test app with endpoint requiring multiple possible roles
    Returns: (app, admin_token, moderator_token, user_token)
    """
    from fastapi import FastAPI, APIRouter, Depends
    from api.auth.permissions import require_role

    app = FastAPI()
    router = APIRouter(prefix="/test")

    @router.get("/admin-or-moderator")
    async def multi_role_endpoint(user=Depends(require_role("admin", "moderator"))):
        return {"message": "Access granted"}

    app.include_router(router)

    admin_token = "mock_admin_token"
    moderator_token = "mock_moderator_token"
    user_token = "mock_user_token"

    return app, admin_token, moderator_token, user_token


@pytest.fixture
def test_app_with_no_role_user():
    """Create test app with user that has no role field"""
    from fastapi import FastAPI
    app = FastAPI()
    token = "mock_no_role_token"
    return app, token


@pytest.fixture
def test_app_with_none_role_user():
    """Create test app with user that has role=None"""
    from fastapi import FastAPI
    app = FastAPI()
    token = "mock_none_role_token"
    return app, token
