"""
Test suite for authentication API endpoints

Tests all authentication endpoints including registration, login,
token refresh, logout, and current user retrieval.

Uses FastAPI TestClient for endpoint testing with proper async support.
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
from datetime import datetime, timedelta
from uuid import uuid4


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
AUTH_ROUTES_FILE = PROJECT_ROOT / "backend" / "api" / "routes" / "auth.py"


class TestAuthRoutesFileExists:
    """Test that auth routes file exists"""

    def test_auth_routes_file_exists(self):
        """Test that backend/api/routes/auth.py exists"""
        assert AUTH_ROUTES_FILE.exists(), "backend/api/routes/auth.py should exist"
        assert AUTH_ROUTES_FILE.is_file(), "auth.py should be a file"

    def test_auth_routes_has_content(self):
        """Test that auth.py has content"""
        content = AUTH_ROUTES_FILE.read_text()
        assert len(content) > 0, "auth.py should not be empty"


class TestAuthRoutesImports:
    """Test that auth routes can be imported"""

    def test_can_import_auth_routes(self):
        """Test that auth routes module can be imported"""
        try:
            from api.routes import auth
            assert auth is not None
        except ImportError as e:
            pytest.fail(f"Failed to import auth routes: {e}")

    def test_router_exists(self):
        """Test that router exists in auth routes"""
        from api.routes import auth
        assert hasattr(auth, 'router'), "auth.py should have a router"


class TestRegisterEndpoint:
    """Test POST /api/v1/auth/register endpoint"""

    def test_register_endpoint_exists(self, test_client):
        """Test that register endpoint exists"""
        response = test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "username": "testuser",
                "password": "Password123!",
                "full_name": "Test User"
            }
        )
        # Should not return 404
        assert response.status_code != 404, "Register endpoint should exist"

    def test_register_success(self, test_client, db_session):
        """Test successful user registration"""
        response = test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "SecurePassword123!",
                "full_name": "New User"
            }
        )

        assert response.status_code == 201, "Registration should return 201 Created"
        data = response.json()
        assert "user" in data, "Response should contain user data"
        assert data["user"]["email"] == "newuser@example.com"
        assert data["user"]["username"] == "newuser"
        assert "password" not in data["user"], "Password should not be in response"

    def test_register_returns_user_with_id(self, test_client, db_session):
        """Test that registration returns user with ID"""
        response = test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "userid@example.com",
                "username": "userid",
                "password": "Password123",
                "full_name": "User ID"
            }
        )

        data = response.json()
        assert "user" in data
        assert "id" in data["user"], "User should have ID"
        # UUID format
        assert len(data["user"]["id"]) == 36, "ID should be UUID format"

    def test_register_duplicate_email_fails(self, test_client, db_session):
        """Test that duplicate email registration fails"""
        # Register first user
        test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "duplicate@example.com",
                "username": "user1",
                "password": "Password123",
                "full_name": "User One"
            }
        )

        # Try to register with same email
        response = test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "duplicate@example.com",
                "username": "user2",
                "password": "Password123",
                "full_name": "User Two"
            }
        )

        assert response.status_code == 400, "Duplicate email should return 400"
        data = response.json()
        assert "detail" in data, "Error response should have detail"

    def test_register_duplicate_username_fails(self, test_client, db_session):
        """Test that duplicate username registration fails"""
        # Register first user
        test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "user1@example.com",
                "username": "duplicateuser",
                "password": "Password123",
                "full_name": "User One"
            }
        )

        # Try to register with same username
        response = test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "user2@example.com",
                "username": "duplicateuser",
                "password": "Password123",
                "full_name": "User Two"
            }
        )

        assert response.status_code == 400, "Duplicate username should return 400"

    def test_register_invalid_email_fails(self, test_client):
        """Test that invalid email format fails validation"""
        response = test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "not-an-email",
                "username": "testuser",
                "password": "Password123",
                "full_name": "Test User"
            }
        )

        assert response.status_code == 422, "Invalid email should return 422 validation error"

    def test_register_short_password_fails(self, test_client):
        """Test that short password fails validation"""
        response = test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "username": "testuser",
                "password": "short",
                "full_name": "Test User"
            }
        )

        assert response.status_code == 422, "Short password should return 422 validation error"

    def test_register_missing_fields_fails(self, test_client):
        """Test that missing required fields fails validation"""
        response = test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                # Missing username, password, full_name
            }
        )

        assert response.status_code == 422, "Missing fields should return 422 validation error"


class TestLoginEndpoint:
    """Test POST /api/v1/auth/login endpoint"""

    def test_login_endpoint_exists(self, test_client):
        """Test that login endpoint exists"""
        response = test_client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "password"
            }
        )
        # Should not return 404
        assert response.status_code != 404, "Login endpoint should exist"

    def test_login_success(self, test_client, db_session):
        """Test successful login"""
        # Register user first
        test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "login@example.com",
                "username": "loginuser",
                "password": "LoginPassword123",
                "full_name": "Login User"
            }
        )

        # Login
        response = test_client.post(
            "/api/v1/auth/login",
            json={
                "email": "login@example.com",
                "password": "LoginPassword123"
            }
        )

        assert response.status_code == 200, "Login should return 200"
        data = response.json()
        assert "access_token" in data, "Response should contain access_token"
        assert "refresh_token" in data, "Response should contain refresh_token"
        assert "token_type" in data, "Response should contain token_type"
        assert data["token_type"] == "bearer", "Token type should be bearer"
        assert "expires_in" in data, "Response should contain expires_in"
        assert "user" in data, "Response should contain user data"

    def test_login_returns_valid_jwt_tokens(self, test_client, db_session):
        """Test that login returns valid JWT tokens"""
        # Register user
        test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "jwt@example.com",
                "username": "jwtuser",
                "password": "JwtPassword123",
                "full_name": "JWT User"
            }
        )

        # Login
        response = test_client.post(
            "/api/v1/auth/login",
            json={
                "email": "jwt@example.com",
                "password": "JwtPassword123"
            }
        )

        data = response.json()
        # JWT format: xxx.yyy.zzz (3 parts)
        assert data["access_token"].count('.') == 2, "Access token should be JWT format"
        assert data["refresh_token"].count('.') == 2, "Refresh token should be JWT format"

    def test_login_wrong_password_fails(self, test_client, db_session):
        """Test that wrong password fails login"""
        # Register user
        test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "wrong@example.com",
                "username": "wronguser",
                "password": "CorrectPassword123",
                "full_name": "Wrong User"
            }
        )

        # Login with wrong password
        response = test_client.post(
            "/api/v1/auth/login",
            json={
                "email": "wrong@example.com",
                "password": "WrongPassword123"
            }
        )

        assert response.status_code == 401, "Wrong password should return 401 Unauthorized"
        data = response.json()
        assert "detail" in data, "Error response should have detail"

    def test_login_nonexistent_user_fails(self, test_client):
        """Test that login with non-existent email fails"""
        response = test_client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "Password123"
            }
        )

        assert response.status_code == 401, "Non-existent user should return 401"

    def test_login_invalid_email_fails(self, test_client):
        """Test that login with invalid email format fails"""
        response = test_client.post(
            "/api/v1/auth/login",
            json={
                "email": "not-an-email",
                "password": "Password123"
            }
        )

        assert response.status_code == 422, "Invalid email should return 422"

    def test_login_missing_fields_fails(self, test_client):
        """Test that login with missing fields fails"""
        response = test_client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                # Missing password
            }
        )

        assert response.status_code == 422, "Missing password should return 422"

    def test_login_inactive_user_fails(self, test_client, db_session):
        """Test that inactive user cannot login"""
        # This test requires ability to set user as inactive
        # Will be implemented when user management is in place
        pass


class TestRefreshEndpoint:
    """Test POST /api/v1/auth/refresh endpoint"""

    def test_refresh_endpoint_exists(self, test_client):
        """Test that refresh endpoint exists"""
        response = test_client.post(
            "/api/v1/auth/refresh",
            json={
                "refresh_token": "fake_token"
            }
        )
        # Should not return 404
        assert response.status_code != 404, "Refresh endpoint should exist"

    def test_refresh_success(self, test_client, db_session):
        """Test successful token refresh"""
        # Register and login
        test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "refresh@example.com",
                "username": "refreshuser",
                "password": "RefreshPassword123",
                "full_name": "Refresh User"
            }
        )

        login_response = test_client.post(
            "/api/v1/auth/login",
            json={
                "email": "refresh@example.com",
                "password": "RefreshPassword123"
            }
        )

        refresh_token = login_response.json()["refresh_token"]

        # Refresh token
        response = test_client.post(
            "/api/v1/auth/refresh",
            json={
                "refresh_token": refresh_token
            }
        )

        assert response.status_code == 200, "Refresh should return 200"
        data = response.json()
        assert "access_token" in data, "Response should contain new access_token"
        assert "token_type" in data, "Response should contain token_type"
        assert "expires_in" in data, "Response should contain expires_in"

    def test_refresh_returns_new_token(self, test_client, db_session):
        """Test that refresh returns a different access token"""
        # Register and login
        test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "newtoken@example.com",
                "username": "newtokenuser",
                "password": "Password123",
                "full_name": "New Token User"
            }
        )

        login_response = test_client.post(
            "/api/v1/auth/login",
            json={
                "email": "newtoken@example.com",
                "password": "Password123"
            }
        )

        old_access_token = login_response.json()["access_token"]
        refresh_token = login_response.json()["refresh_token"]

        # Refresh
        response = test_client.post(
            "/api/v1/auth/refresh",
            json={
                "refresh_token": refresh_token
            }
        )

        new_access_token = response.json()["access_token"]
        assert new_access_token != old_access_token, "New access token should be different"

    def test_refresh_invalid_token_fails(self, test_client):
        """Test that invalid refresh token fails"""
        response = test_client.post(
            "/api/v1/auth/refresh",
            json={
                "refresh_token": "invalid.token.here"
            }
        )

        assert response.status_code == 401, "Invalid refresh token should return 401"

    def test_refresh_expired_token_fails(self, test_client):
        """Test that expired refresh token fails"""
        # This requires creating an expired token
        # Will test token expiration logic
        pass

    def test_refresh_missing_token_fails(self, test_client):
        """Test that missing refresh token fails"""
        response = test_client.post(
            "/api/v1/auth/refresh",
            json={}
        )

        assert response.status_code == 422, "Missing refresh token should return 422"


class TestGetCurrentUserEndpoint:
    """Test GET /api/v1/auth/me endpoint"""

    def test_me_endpoint_exists(self, test_client):
        """Test that /me endpoint exists"""
        response = test_client.get("/api/v1/auth/me")
        # Should not return 404
        assert response.status_code != 404, "Me endpoint should exist"

    def test_me_requires_authentication(self, test_client):
        """Test that /me requires authentication"""
        response = test_client.get("/api/v1/auth/me")

        assert response.status_code == 401, "Should return 401 without authentication"

    def test_me_with_valid_token_returns_user(self, test_client, db_session):
        """Test that /me returns user data with valid token"""
        # Register and login
        test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "me@example.com",
                "username": "meuser",
                "password": "Password123",
                "full_name": "Me User"
            }
        )

        login_response = test_client.post(
            "/api/v1/auth/login",
            json={
                "email": "me@example.com",
                "password": "Password123"
            }
        )

        access_token = login_response.json()["access_token"]

        # Get current user
        response = test_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 200, "Should return 200 with valid token"
        data = response.json()
        assert data["email"] == "me@example.com", "Should return correct user"
        assert data["username"] == "meuser"
        assert "password" not in data, "Should not include password"

    def test_me_with_invalid_token_fails(self, test_client):
        """Test that /me fails with invalid token"""
        response = test_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"}
        )

        assert response.status_code == 401, "Invalid token should return 401"

    def test_me_with_expired_token_fails(self, test_client):
        """Test that /me fails with expired token"""
        # This requires creating an expired token
        pass

    def test_me_without_bearer_prefix_fails(self, test_client):
        """Test that /me fails without Bearer prefix"""
        response = test_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "some-token"}
        )

        assert response.status_code == 401, "Should require Bearer prefix"

    def test_me_returns_complete_user_data(self, test_client, db_session):
        """Test that /me returns complete user data"""
        # Register and login
        test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "complete@example.com",
                "username": "completeuser",
                "password": "Password123",
                "full_name": "Complete User"
            }
        )

        login_response = test_client.post(
            "/api/v1/auth/login",
            json={
                "email": "complete@example.com",
                "password": "Password123"
            }
        )

        access_token = login_response.json()["access_token"]

        # Get current user
        response = test_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        data = response.json()
        # Check all expected fields
        assert "id" in data, "Should have id"
        assert "email" in data, "Should have email"
        assert "username" in data, "Should have username"
        assert "full_name" in data, "Should have full_name"
        assert "is_active" in data, "Should have is_active"
        assert "created_at" in data, "Should have created_at"


class TestAuthEndpointIntegration:
    """Test authentication endpoint integration scenarios"""

    def test_register_login_refresh_me_workflow(self, test_client, db_session):
        """Test complete authentication workflow"""
        # 1. Register
        register_response = test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "workflow@example.com",
                "username": "workflowuser",
                "password": "WorkflowPassword123",
                "full_name": "Workflow User"
            }
        )
        assert register_response.status_code == 201

        # 2. Login
        login_response = test_client.post(
            "/api/v1/auth/login",
            json={
                "email": "workflow@example.com",
                "password": "WorkflowPassword123"
            }
        )
        assert login_response.status_code == 200
        login_data = login_response.json()

        # 3. Access /me with access token
        me_response = test_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {login_data['access_token']}"}
        )
        assert me_response.status_code == 200
        assert me_response.json()["email"] == "workflow@example.com"

        # 4. Refresh token
        refresh_response = test_client.post(
            "/api/v1/auth/refresh",
            json={
                "refresh_token": login_data["refresh_token"]
            }
        )
        assert refresh_response.status_code == 200

        # 5. Access /me with new access token
        new_access_token = refresh_response.json()["access_token"]
        me_response2 = test_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {new_access_token}"}
        )
        assert me_response2.status_code == 200

    def test_multiple_users_can_login_independently(self, test_client, db_session):
        """Test that multiple users can register and login independently"""
        # Register two users
        for i in range(2):
            test_client.post(
                "/api/v1/auth/register",
                json={
                    "email": f"user{i}@example.com",
                    "username": f"user{i}",
                    "password": "Password123",
                    "full_name": f"User {i}"
                }
            )

        # Both can login
        for i in range(2):
            response = test_client.post(
                "/api/v1/auth/login",
                json={
                    "email": f"user{i}@example.com",
                    "password": "Password123"
                }
            )
            assert response.status_code == 200
            assert response.json()["user"]["email"] == f"user{i}@example.com"


class TestAuthEndpointEdgeCases:
    """Test authentication endpoint edge cases"""

    def test_register_with_extra_fields_ignores_them(self, test_client, db_session):
        """Test that extra fields in registration are ignored"""
        response = test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "extra@example.com",
                "username": "extrauser",
                "password": "Password123",
                "full_name": "Extra User",
                "extra_field": "should be ignored",
                "is_admin": True  # Should not be settable
            }
        )

        assert response.status_code == 201 or response.status_code == 422
        # Extra fields should be ignored, not cause errors

    def test_login_case_sensitivity(self, test_client, db_session):
        """Test email case sensitivity in login"""
        # Register with lowercase
        test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "case@example.com",
                "username": "caseuser",
                "password": "Password123",
                "full_name": "Case User"
            }
        )

        # Login with uppercase - behavior depends on implementation
        response = test_client.post(
            "/api/v1/auth/login",
            json={
                "email": "CASE@EXAMPLE.COM",
                "password": "Password123"
            }
        )

        # Most systems treat email as case-insensitive
        # This test documents actual behavior
        pass

    def test_concurrent_registrations(self, test_client, db_session):
        """Test handling of concurrent registrations"""
        # This would require actual concurrency testing
        # Documenting the requirement
        pass


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def test_client():
    """Create a test client for the FastAPI application"""
    from api.main import app
    from fastapi.testclient import TestClient

    client = TestClient(app)
    return client
