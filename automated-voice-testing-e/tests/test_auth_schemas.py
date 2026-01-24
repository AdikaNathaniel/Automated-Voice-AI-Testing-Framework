"""
Test suite for authentication Pydantic schemas

Ensures proper validation and structure for authentication-related
request and response models including login, registration, token refresh, etc.
"""

import pytest
from datetime import datetime
from uuid import uuid4
from pathlib import Path
from pydantic import ValidationError


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
AUTH_SCHEMAS_FILE = PROJECT_ROOT / "backend" / "api" / "schemas" / "auth.py"


class TestAuthSchemasFileExists:
    """Test that auth schemas file exists"""

    def test_auth_schemas_file_exists(self):
        """Test that backend/api/schemas/auth.py exists"""
        assert AUTH_SCHEMAS_FILE.exists(), "backend/api/schemas/auth.py should exist"
        assert AUTH_SCHEMAS_FILE.is_file(), "auth.py should be a file"

    def test_auth_schemas_has_content(self):
        """Test that auth.py has content"""
        content = AUTH_SCHEMAS_FILE.read_text()
        assert len(content) > 0, "auth.py should not be empty"


class TestAuthSchemasImports:
    """Test that auth schemas can be imported"""

    def test_can_import_auth_schemas(self):
        """Test that auth schemas module can be imported"""
        try:
            from api.schemas import auth
            assert auth is not None
        except ImportError as e:
            pytest.fail(f"Failed to import auth schemas: {e}")

    def test_uses_pydantic(self):
        """Test that auth schemas use Pydantic"""
        content = AUTH_SCHEMAS_FILE.read_text()
        assert 'pydantic' in content.lower() or 'BaseModel' in content, \
            "auth.py should use Pydantic"


class TestLoginRequestSchema:
    """Test LoginRequest schema"""

    def test_login_request_schema_exists(self):
        """Test that LoginRequest schema exists"""
        from api.schemas.auth import LoginRequest
        assert LoginRequest is not None

    def test_login_request_has_email_field(self):
        """Test that LoginRequest has email field"""
        from api.schemas.auth import LoginRequest

        login_data = LoginRequest(
            email="user@example.com",
            password="Password12345!"
        )
        assert hasattr(login_data, 'email')
        assert login_data.email == "user@example.com"

    def test_login_request_has_password_field(self):
        """Test that LoginRequest has password field"""
        from api.schemas.auth import LoginRequest

        login_data = LoginRequest(
            email="user@example.com",
            password="Password12345!"
        )
        assert hasattr(login_data, 'password')
        assert login_data.password == "Password12345!"

    def test_login_request_email_validation(self):
        """Test that LoginRequest validates email format"""
        from api.schemas.auth import LoginRequest

        # Valid email should work
        valid_login = LoginRequest(
            email="valid@example.com",
            password="Password12345!"
        )
        assert valid_login.email == "valid@example.com"

        # Invalid email should raise validation error
        with pytest.raises(ValidationError):
            LoginRequest(
                email="not-an-email",
                password="Password12345!"
            )

    def test_login_request_requires_both_fields(self):
        """Test that LoginRequest requires both email and password"""
        from api.schemas.auth import LoginRequest

        # Missing email
        with pytest.raises(ValidationError):
            LoginRequest(password="Password12345!")

        # Missing password
        with pytest.raises(ValidationError):
            LoginRequest(email="user@example.com")


class TestLoginResponseSchema:
    """Test LoginResponse schema"""

    def test_login_response_schema_exists(self):
        """Test that LoginResponse schema exists"""
        from api.schemas.auth import LoginResponse
        assert LoginResponse is not None

    def test_login_response_has_access_token(self):
        """Test that LoginResponse has access_token field"""
        from api.schemas.auth import LoginResponse, UserResponse

        user = UserResponse(
            id=uuid4(),
            email="user@example.com",
            username="testuser",
            full_name="Test User",
            is_active=True,
            created_at=datetime.utcnow()
        )

        response = LoginResponse(
            access_token="access_token_string",
            refresh_token="refresh_token_string",
            token_type="bearer",
            expires_in=900,
            user=user
        )

        assert hasattr(response, 'access_token')
        assert response.access_token == "access_token_string"

    def test_login_response_has_refresh_token(self):
        """Test that LoginResponse has refresh_token field"""
        from api.schemas.auth import LoginResponse, UserResponse

        user = UserResponse(
            id=uuid4(),
            email="user@example.com",
            username="testuser",
            full_name="Test User",
            is_active=True,
            created_at=datetime.utcnow()
        )

        response = LoginResponse(
            access_token="access_token_string",
            refresh_token="refresh_token_string",
            token_type="bearer",
            expires_in=900,
            user=user
        )

        assert hasattr(response, 'refresh_token')
        assert response.refresh_token == "refresh_token_string"

    def test_login_response_has_expires_in(self):
        """Test that LoginResponse has expires_in field"""
        from api.schemas.auth import LoginResponse, UserResponse

        user = UserResponse(
            id=uuid4(),
            email="user@example.com",
            username="testuser",
            full_name="Test User",
            is_active=True,
            created_at=datetime.utcnow()
        )

        response = LoginResponse(
            access_token="access_token_string",
            refresh_token="refresh_token_string",
            token_type="bearer",
            expires_in=900,
            user=user
        )

        assert hasattr(response, 'expires_in')
        assert response.expires_in == 900

    def test_login_response_has_user(self):
        """Test that LoginResponse has user field"""
        from api.schemas.auth import LoginResponse, UserResponse

        user = UserResponse(
            id=uuid4(),
            email="user@example.com",
            username="testuser",
            full_name="Test User",
            is_active=True,
            created_at=datetime.utcnow()
        )

        response = LoginResponse(
            access_token="access_token_string",
            refresh_token="refresh_token_string",
            token_type="bearer",
            expires_in=900,
            user=user
        )

        assert hasattr(response, 'user')
        assert response.user.email == "user@example.com"


class TestRegisterRequestSchema:
    """Test RegisterRequest schema"""

    def test_register_request_schema_exists(self):
        """Test that RegisterRequest schema exists"""
        from api.schemas.auth import RegisterRequest
        assert RegisterRequest is not None

    def test_register_request_has_required_fields(self):
        """Test that RegisterRequest has all required fields"""
        from api.schemas.auth import RegisterRequest

        register_data = RegisterRequest(
            email="newuser@example.com",
            username="newuser",
            password="SecurePassword123!",
            full_name="New User"
        )

        assert register_data.email == "newuser@example.com"
        assert register_data.username == "newuser"
        assert register_data.password == "SecurePassword123!"
        assert register_data.full_name == "New User"

    def test_register_request_email_validation(self):
        """Test that RegisterRequest validates email format"""
        from api.schemas.auth import RegisterRequest

        # Valid email should work
        valid_register = RegisterRequest(
            email="valid@example.com",
            username="testuser",
            password="Password12345!",
            full_name="Test User"
        )
        assert valid_register.email == "valid@example.com"

        # Invalid email should raise validation error
        with pytest.raises(ValidationError):
            RegisterRequest(
                email="not-an-email",
                username="testuser",
                password="Password12345!",
                full_name="Test User"
            )

    def test_register_request_username_validation(self):
        """Test that RegisterRequest validates username"""
        from api.schemas.auth import RegisterRequest

        # Valid username should work
        valid_register = RegisterRequest(
            email="user@example.com",
            username="validusername",
            password="Password12345!",
            full_name="Test User"
        )
        assert valid_register.username == "validusername"

        # Empty username should fail
        with pytest.raises(ValidationError):
            RegisterRequest(
                email="user@example.com",
                username="",
                password="Password12345!",
                full_name="Test User"
            )

    def test_register_request_password_validation(self):
        """Test that RegisterRequest validates password"""
        from api.schemas.auth import RegisterRequest

        # Valid password should work
        valid_register = RegisterRequest(
            email="user@example.com",
            username="testuser",
            password="ValidPassword123!",
            full_name="Test User"
        )
        assert valid_register.password == "ValidPassword123!"

        # Empty password should fail (or too short if there's min length validation)
        with pytest.raises(ValidationError):
            RegisterRequest(
                email="user@example.com",
                username="testuser",
                password="",
                full_name="Test User"
            )

    def test_register_request_defaults_role_to_viewer(self):
        """RegisterRequest should default to viewer role."""
        from api.schemas.auth import RegisterRequest
        from api.auth.roles import Role

        register_data = RegisterRequest(
            email="viewer@example.com",
            username="vieweruser",
            password="Password123!",
            full_name="Viewer User"
        )

        assert register_data.role == Role.VIEWER

    def test_register_request_rejects_invalid_role(self):
        """RegisterRequest should reject unsupported roles."""
        from api.schemas.auth import RegisterRequest

        with pytest.raises(ValidationError):
            RegisterRequest(
                email="hacker@example.com",
                username="badrole",
                password="Password123!",
                full_name="Bad Role",
                role="hacker",
            )


class TestUserResponseSchema:
    """Test UserResponse schema"""

    def test_user_response_schema_exists(self):
        """Test that UserResponse schema exists"""
        from api.schemas.auth import UserResponse
        assert UserResponse is not None

    def test_user_response_has_id(self):
        """Test that UserResponse has id field"""
        from api.schemas.auth import UserResponse

        user_id = uuid4()
        user = UserResponse(
            id=user_id,
            email="user@example.com",
            username="testuser",
            full_name="Test User",
            is_active=True,
            created_at=datetime.utcnow()
        )

        assert hasattr(user, 'id')
        assert user.id == user_id

    def test_user_response_has_email(self):
        """Test that UserResponse has email field"""
        from api.schemas.auth import UserResponse

        user = UserResponse(
            id=uuid4(),
            email="user@example.com",
            username="testuser",
            full_name="Test User",
            is_active=True,
            created_at=datetime.utcnow()
        )

        assert hasattr(user, 'email')
        assert user.email == "user@example.com"

    def test_user_response_accepts_tenant_id(self):
        """Tenant metadata should round-trip through UserResponse."""
        from api.schemas.auth import UserResponse
        tenant_id = uuid4()
        user = UserResponse(
            id=uuid4(),
            email="tenant@example.com",
            username="tenant",
            full_name="Tenant User",
            is_active=True,
            created_at=datetime.utcnow(),
            tenant_id=tenant_id,
        )
        assert user.tenant_id == tenant_id

    def test_user_response_excludes_password(self):
        """Test that UserResponse does not include password"""
        from api.schemas.auth import UserResponse

        user = UserResponse(
            id=uuid4(),
            email="user@example.com",
            username="testuser",
            full_name="Test User",
            is_active=True,
            created_at=datetime.utcnow()
        )

        # Password should not be in the schema
        assert not hasattr(user, 'password')
        assert not hasattr(user, 'hashed_password')


class TestTokenRefreshRequestSchema:
    """Test TokenRefreshRequest schema"""

    def test_token_refresh_request_exists(self):
        """Test that TokenRefreshRequest schema exists"""
        from api.schemas.auth import TokenRefreshRequest
        assert TokenRefreshRequest is not None

    def test_token_refresh_request_has_refresh_token(self):
        """Test that TokenRefreshRequest has refresh_token field"""
        from api.schemas.auth import TokenRefreshRequest

        request = TokenRefreshRequest(
            refresh_token="refresh_token_string"
        )

        assert hasattr(request, 'refresh_token')
        assert request.refresh_token == "refresh_token_string"


class TestTokenRefreshResponseSchema:
    """Test TokenRefreshResponse schema"""

    def test_token_refresh_response_exists(self):
        """Test that TokenRefreshResponse schema exists"""
        from api.schemas.auth import TokenRefreshResponse
        assert TokenRefreshResponse is not None

    def test_token_refresh_response_has_access_token(self):
        """Test that TokenRefreshResponse has access_token field"""
        from api.schemas.auth import TokenRefreshResponse

        response = TokenRefreshResponse(
            access_token="new_access_token",
            refresh_token="new_refresh_token",
            token_type="bearer",
            expires_in=900
        )

        assert hasattr(response, 'access_token')
        assert response.access_token == "new_access_token"


class TestPasswordChangeRequestSchema:
    """Test PasswordChangeRequest schema"""

    def test_password_change_request_exists(self):
        """Test that PasswordChangeRequest schema exists"""
        from api.schemas.auth import PasswordChangeRequest
        assert PasswordChangeRequest is not None

    def test_password_change_request_has_fields(self):
        """Test that PasswordChangeRequest has old and new password fields"""
        from api.schemas.auth import PasswordChangeRequest

        request = PasswordChangeRequest(
            old_password="OldPassword123!",
            new_password="NewPassword456!"
        )

        assert hasattr(request, 'old_password')
        assert hasattr(request, 'new_password')
        assert request.old_password == "OldPassword123!"
        assert request.new_password == "NewPassword456!"


class TestSchemaValidation:
    """Test schema validation rules"""

    def test_email_format_validation(self):
        """Test that email fields validate email format"""
        from api.schemas.auth import LoginRequest

        # Invalid emails should fail
        invalid_emails = [
            "notanemail",
            "@example.com",
            "user@",
            "user space@example.com",
        ]

        for invalid_email in invalid_emails:
            with pytest.raises(ValidationError):
                LoginRequest(email=invalid_email, password="password")

    def test_required_fields_validation(self):
        """Test that required fields are enforced"""
        from api.schemas.auth import RegisterRequest

        # All fields are required
        with pytest.raises(ValidationError):
            RegisterRequest(
                email="user@example.com",
                # Missing username, password, full_name
            )


class TestSchemaDocumentation:
    """Test schema documentation"""

    def test_login_request_has_docstring(self):
        """Test that LoginRequest has docstring"""
        from api.schemas.auth import LoginRequest

        assert LoginRequest.__doc__ is not None, \
            "LoginRequest should have docstring"

    def test_login_response_has_docstring(self):
        """Test that LoginResponse has docstring"""
        from api.schemas.auth import LoginResponse

        assert LoginResponse.__doc__ is not None, \
            "LoginResponse should have docstring"

    def test_register_request_has_docstring(self):
        """Test that RegisterRequest has docstring"""
        from api.schemas.auth import RegisterRequest

        assert RegisterRequest.__doc__ is not None, \
            "RegisterRequest should have docstring"


class TestSchemaIntegration:
    """Test schema integration scenarios"""

    def test_login_to_response_workflow(self):
        """Test login request to response workflow"""
        from api.schemas.auth import LoginRequest, LoginResponse, UserResponse

        # Create login request
        login_request = LoginRequest(
            email="user@example.com",
            password="Password12345!"
        )

        # Simulate creating response after authentication
        user = UserResponse(
            id=uuid4(),
            email=login_request.email,
            username="testuser",
            full_name="Test User",
            is_active=True,
            created_at=datetime.utcnow()
        )

        response = LoginResponse(
            access_token="jwt_access_token",
            refresh_token="jwt_refresh_token",
            token_type="bearer",
            expires_in=900,
            user=user
        )

        assert response.user.email == login_request.email

    def test_register_to_user_workflow(self):
        """Test registration request to user response workflow"""
        from api.schemas.auth import RegisterRequest, UserResponse

        # Create registration request
        register_request = RegisterRequest(
            email="newuser@example.com",
            username="newuser",
            password="SecurePassword123!",
            full_name="New User"
        )

        # Simulate creating user after registration
        user = UserResponse(
            id=uuid4(),
            email=register_request.email,
            username=register_request.username,
            full_name=register_request.full_name,
            is_active=True,
            created_at=datetime.utcnow()
        )

        assert user.email == register_request.email
        assert user.username == register_request.username
        assert not hasattr(user, 'password')
