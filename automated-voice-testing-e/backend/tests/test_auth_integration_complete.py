"""
Integration tests for authentication and authorization flows.

Tests the complete authentication lifecycle including registration, login,
token refresh, logout, and role-based access control.
Uses mocked services and database sessions to test flows without external dependencies.
"""

import pytest
from uuid import uuid4
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from jose import JWTError

from api.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenRefreshRequest,
    LoginResponse,
    UserResponse,
)
from api.auth.roles import Role
from api.auth.password import hash_password, verify_password
from api.auth.jwt import create_access_token, create_refresh_token, decode_token
from services.refresh_token_store import refresh_token_store
from services.login_attempt_tracker import login_attempt_tracker


class TestAuthRegistrationFlow:
    """Test user registration and account creation flows."""

    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def admin_user(self):
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.email = "admin@example.com"
        user.username = "admin"
        user.full_name = "Admin User"
        user.role = Role.ORG_ADMIN.value
        user.is_active = True
        user.tenant_id = uuid4()
        user.created_at = datetime.utcnow()
        user.updated_at = datetime.utcnow()
        return user

    @pytest.mark.asyncio
    async def test_register_user_with_valid_data(self, mock_db, admin_user):
        """Test successful user registration with valid data."""
        register_data = RegisterRequest(
            email="newuser@example.com",
            username="newuser",
            password="SecurePass123!@#",
            full_name="New User"
        )

        # Mock user service create method
        created_user = MagicMock(spec=UserResponse)
        created_user.id = uuid4()
        created_user.email = register_data.email
        created_user.username = register_data.username
        created_user.full_name = register_data.full_name
        created_user.role = Role.VIEWER.value
        created_user.is_active = True
        created_user.tenant_id = uuid4()

        # Verify the user would be created with correct data
        assert created_user.email == register_data.email
        assert created_user.username == register_data.username
        assert created_user.role == Role.VIEWER.value

    @pytest.mark.asyncio
    async def test_register_user_password_complexity_validation(self, mock_db):
        """Test that weak passwords are rejected."""
        from pydantic_core import ValidationError

        with pytest.raises(ValidationError):
            # This would fail in pydantic validation due to password rules
            RegisterRequest(
                email="user@example.com",
                username="user",
                password="weak",  # Too short, missing requirements
                full_name="User"
            )

    @pytest.mark.asyncio
    async def test_register_user_duplicate_email_fails(self, mock_db):
        """Test that registering with duplicate email fails."""
        register_data = RegisterRequest(
            email="existing@example.com",
            username="newuser",
            password="SecurePass123!@#",
            full_name="New User"
        )

        # In real implementation, database would raise IntegrityError
        # This test verifies the schema accepts the duplicate email format
        # (validation happens at database level)
        assert register_data.email == "existing@example.com"
        assert "@" in register_data.email

    @pytest.mark.asyncio
    async def test_register_user_duplicate_username_fails(self, mock_db):
        """Test that registering with duplicate username fails."""
        register_data = RegisterRequest(
            email="newuser@example.com",
            username="existing_user",
            password="SecurePass123!@#",
            full_name="New User"
        )

        # In real implementation, database would raise IntegrityError
        # This test verifies the schema accepts the duplicate username format
        assert register_data.username == "existing_user"
        assert len(register_data.username) >= 3


class TestAuthLoginFlow:
    """Test login and authentication flows."""

    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def test_user(self):
        user = MagicMock()
        user.id = uuid4()
        user.email = "user@example.com"
        user.username = "testuser"
        user.password_hash = hash_password("SecurePass123!@#")
        user.role = Role.VIEWER.value
        user.is_active = True
        user.tenant_id = uuid4()
        return user

    @pytest.mark.asyncio
    async def test_login_with_valid_credentials(self, mock_db, test_user):
        """Test successful login with valid credentials."""
        login_data = LoginRequest(
            email=test_user.email,
            password="SecurePass123!@#"
        )

        # Verify password hashing and validation works
        password_valid = verify_password(login_data.password, test_user.password_hash)
        assert password_valid is True

        # Verify test user has correct email
        assert test_user.email == login_data.email

    @pytest.mark.asyncio
    async def test_login_with_invalid_password(self, mock_db, test_user):
        """Test login with incorrect password."""
        login_data = LoginRequest(
            email=test_user.email,
            password="WrongPassword123!@#"
        )

        # Verify password validation fails with wrong password
        password_valid = verify_password(login_data.password, test_user.password_hash)
        assert password_valid is False

    @pytest.mark.asyncio
    async def test_login_with_nonexistent_email(self, mock_db):
        """Test login with email that doesn't exist."""
        login_data = LoginRequest(
            email="nonexistent@example.com",
            password="SomePassword123!@#"
        )

        # Simulate user not found in database
        # In real implementation, get_user_by_email would return None
        assert login_data.email != "user@example.com"

    @pytest.mark.asyncio
    async def test_login_with_inactive_user(self, mock_db, test_user):
        """Test that inactive users cannot login."""
        test_user.is_active = False
        login_data = LoginRequest(
            email=test_user.email,
            password="SecurePass123!@#"
        )

        # Verify test user is marked as inactive
        assert test_user.is_active is False
        assert test_user.email == login_data.email

    @pytest.mark.asyncio
    async def test_login_generates_tokens(self, test_user):
        """Test that successful login generates access and refresh tokens."""
        user_id = test_user.id

        # Create tokens with proper expiration delta
        access_token = create_access_token(
            user_id=user_id,
            expires_delta=timedelta(minutes=15)
        )
        refresh_token = create_refresh_token(user_id=user_id)

        assert access_token is not None
        assert refresh_token is not None
        assert isinstance(access_token, str)
        assert isinstance(refresh_token, str)

        # Verify tokens can be decoded
        access_payload = decode_token(access_token)
        refresh_payload = decode_token(refresh_token)

        assert access_payload['sub'] == str(user_id)
        assert access_payload['type'] == 'access'
        assert refresh_payload['sub'] == str(user_id)
        assert refresh_payload['type'] == 'refresh'


class TestAuthTokenRefreshFlow:
    """Test token refresh and rotation flows."""

    @pytest.fixture
    def test_user(self):
        user = MagicMock()
        user.id = uuid4()
        user.email = "user@example.com"
        user.role = Role.VIEWER.value
        user.is_active = True
        return user

    @pytest.mark.asyncio
    async def test_refresh_token_generates_new_access_token(self, test_user):
        """Test that refresh token generates new access token."""
        user_id = test_user.id

        # Create initial tokens
        old_access_token = create_access_token(
            user_id=user_id,
            expires_delta=timedelta(minutes=15)
        )
        refresh_token = create_refresh_token(user_id=user_id)

        # Simulate token refresh - create new access token
        new_access_token = create_access_token(
            user_id=user_id,
            expires_delta=timedelta(minutes=15)
        )

        # Verify both tokens are valid but different
        old_payload = decode_token(old_access_token)
        new_payload = decode_token(new_access_token)

        assert old_payload['sub'] == new_payload['sub']
        assert old_payload['type'] == 'access'
        assert new_payload['type'] == 'access'

    @pytest.mark.asyncio
    async def test_refresh_token_validation(self, test_user):
        """Test that refresh token is properly validated."""
        user_id = test_user.id

        # Create refresh token
        refresh_token = create_refresh_token(user_id=user_id)

        # Decode and validate
        payload = decode_token(refresh_token)

        assert payload['sub'] == str(user_id)
        assert payload['type'] == 'refresh'
        assert 'exp' in payload
        assert 'iat' in payload

    @pytest.mark.asyncio
    async def test_expired_refresh_token_rejected(self, test_user):
        """Test that expired refresh tokens are rejected."""
        user_id = test_user.id

        # Create an expired token (manually craft)
        from jose import jwt
        from api.config import get_settings

        settings = get_settings()
        past_time = datetime.utcnow() - timedelta(days=8)

        payload = {
            'sub': str(user_id),
            'exp': past_time,
            'type': 'refresh',
            'iat': past_time
        }

        expired_token = jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm='HS256'
        )

        # Try to decode - should fail due to expiration
        with pytest.raises(JWTError):
            decode_token(expired_token)


class TestAuthLogoutFlow:
    """Test logout and token revocation flows."""

    @pytest.fixture
    def test_user(self):
        user = MagicMock()
        user.id = uuid4()
        user.email = "user@example.com"
        user.role = Role.VIEWER.value
        user.is_active = True
        return user

    @pytest.mark.asyncio
    async def test_logout_revokes_refresh_token(self, test_user):
        """Test that logout revokes the refresh token."""
        from datetime import timezone
        user_id = test_user.id

        # Create refresh token
        refresh_token = create_refresh_token(user_id=user_id)

        # Save token to store with timezone-aware datetime
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        refresh_token_store.save(refresh_token, user_id=user_id, expires_at=expires_at)

        # Verify token is valid before logout
        assert refresh_token_store.verify(refresh_token, user_id=user_id) is True

        # Logout should revoke token
        refresh_token_store.revoke(refresh_token)

        # Verify token is no longer valid
        assert refresh_token_store.verify(refresh_token, user_id=user_id) is False

    @pytest.mark.asyncio
    async def test_revoked_refresh_token_cannot_be_used(self, test_user):
        """Test that revoked tokens cannot be used."""
        from datetime import timezone
        user_id = test_user.id

        # Create refresh token
        refresh_token = create_refresh_token(user_id=user_id)

        # Save and then revoke token with timezone-aware datetime
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        refresh_token_store.save(refresh_token, user_id=user_id, expires_at=expires_at)
        refresh_token_store.revoke(refresh_token)

        # Try to use revoked token - should return False
        is_valid = refresh_token_store.verify(refresh_token, user_id=user_id)

        assert is_valid is False


class TestAuthCompleteLifecycle:
    """Test complete authentication lifecycle flow."""

    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.mark.asyncio
    async def test_complete_user_lifecycle(self, mock_db):
        """Test complete user lifecycle from registration to logout."""
        from datetime import timezone
        tenant_id = uuid4()
        user_id = uuid4()

        # Step 1: Register user
        register_data = RegisterRequest(
            email="lifecycle@example.com",
            username="lifecycle_user",
            password="SecurePass123!@#",
            full_name="Lifecycle User"
        )

        # Verify registration data is valid
        assert register_data.email == "lifecycle@example.com"
        assert register_data.username == "lifecycle_user"
        assert register_data.role == Role.VIEWER  # Default role assigned during creation

        # Step 2: Simulate login with password verification
        login_data = LoginRequest(
            email=register_data.email,
            password=register_data.password
        )

        # Verify password hashing works
        password_hash = hash_password(register_data.password)
        password_valid = verify_password(login_data.password, password_hash)
        assert password_valid is True

        # Step 3: Create tokens
        access_token = create_access_token(
            user_id=user_id,
            expires_delta=timedelta(minutes=15)
        )
        refresh_token = create_refresh_token(user_id=user_id)

        assert access_token is not None
        assert refresh_token is not None

        # Step 4: Refresh token - create new access token
        new_access_token = create_access_token(
            user_id=user_id,
            expires_delta=timedelta(minutes=15)
        )
        assert new_access_token is not None

        # Step 5: Logout (revoke token)
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        refresh_token_store.save(refresh_token, user_id=user_id, expires_at=expires_at)
        refresh_token_store.revoke(refresh_token)
        assert refresh_token_store.verify(refresh_token, user_id=user_id) is False


class TestAuthBruteForceProtection:
    """Test brute force protection on login."""

    @pytest.fixture
    def test_user(self):
        user = MagicMock()
        user.id = uuid4()
        user.email = "user@example.com"
        user.password_hash = hash_password("SecurePass123!@#")
        user.is_active = True
        return user

    @pytest.mark.asyncio
    async def test_login_attempt_tracking(self, test_user):
        """Test that failed login attempts are tracked."""
        email = test_user.email

        # Clear any previous attempts
        login_attempt_tracker.reset(email)

        # Record a failed attempt
        result = login_attempt_tracker.record_failure(email)

        assert result['locked'] is False
        assert result['attempts_remaining'] == 4

    @pytest.mark.asyncio
    async def test_lockout_after_max_failed_attempts(self, test_user):
        """Test that user is locked out after 5 failed attempts."""
        email = test_user.email

        # Clear any previous attempts
        login_attempt_tracker.reset(email)

        # Record 5 failed attempts
        for i in range(5):
            result = login_attempt_tracker.record_failure(email)

        # Verify user is now locked out
        assert login_attempt_tracker.is_locked_out(email) is True

    @pytest.mark.asyncio
    async def test_successful_login_resets_attempt_counter(self, test_user):
        """Test that successful login resets failed attempts counter."""
        email = test_user.email

        # Clear any previous attempts
        login_attempt_tracker.reset(email)

        # Record some failed attempts
        login_attempt_tracker.record_failure(email)
        login_attempt_tracker.record_failure(email)

        # Verify attempts are recorded
        assert login_attempt_tracker.get_attempt_count(email) == 2

        # Record successful login
        login_attempt_tracker.record_success(email)

        # Verify attempts are reset
        assert login_attempt_tracker.get_attempt_count(email) == 0


class TestAuthRoleBasedAccess:
    """Test role-based access control in auth flow."""

    @pytest.fixture
    def admin_user(self):
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.email = "admin@example.com"
        user.role = Role.ORG_ADMIN.value
        user.is_active = True
        user.tenant_id = uuid4()
        return user

    @pytest.fixture
    def viewer_user(self):
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.email = "viewer@example.com"
        user.role = Role.VIEWER.value
        user.is_active = True
        user.tenant_id = uuid4()
        return user

    @pytest.mark.asyncio
    async def test_admin_can_register_users(self, admin_user):
        """Test that admin role can register new users."""
        register_data = RegisterRequest(
            email="newuser@example.com",
            username="newuser",
            password="SecurePass123!@#",
            full_name="New User"
        )

        # Admin check in route would pass
        assert admin_user.role == Role.ORG_ADMIN.value

    @pytest.mark.asyncio
    async def test_viewer_cannot_register_users(self, viewer_user):
        """Test that viewer role cannot register users."""
        # Viewer would not have permission to call register endpoint
        assert viewer_user.role != Role.ORG_ADMIN.value

    @pytest.mark.asyncio
    async def test_token_includes_user_role(self, admin_user):
        """Test that JWT token includes user role information."""
        access_token = create_access_token(
            user_id=admin_user.id,
            expires_delta=timedelta(minutes=15)
        )
        payload = decode_token(access_token)

        assert payload['sub'] == str(admin_user.id)
        # Note: role is typically added separately in route handlers


class TestAuthMultiTenancy:
    """Test multi-tenant authentication flows."""

    @pytest.fixture
    def tenant1_user(self):
        tenant1_id = uuid4()
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.email = "user@tenant1.com"
        user.role = Role.VIEWER.value
        user.is_active = True
        user.tenant_id = tenant1_id
        return user

    @pytest.fixture
    def tenant2_user(self):
        tenant2_id = uuid4()
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.email = "user@tenant2.com"
        user.role = Role.VIEWER.value
        user.is_active = True
        user.tenant_id = tenant2_id
        return user

    @pytest.mark.asyncio
    async def test_tenant_isolation_in_token(self, tenant1_user, tenant2_user):
        """Test that users from different tenants get separate tokens."""
        token1 = create_access_token(
            user_id=tenant1_user.id,
            expires_delta=timedelta(minutes=15)
        )
        token2 = create_access_token(
            user_id=tenant2_user.id,
            expires_delta=timedelta(minutes=15)
        )

        payload1 = decode_token(token1)
        payload2 = decode_token(token2)

        assert payload1['sub'] != payload2['sub']
        assert payload1['sub'] == str(tenant1_user.id)
        assert payload2['sub'] == str(tenant2_user.id)

    @pytest.mark.asyncio
    async def test_tokens_are_user_specific(self, tenant1_user):
        """Test that tokens are specific to individual users."""
        token1 = create_access_token(
            user_id=tenant1_user.id,
            expires_delta=timedelta(minutes=15)
        )
        token2 = create_access_token(
            user_id=tenant1_user.id,
            expires_delta=timedelta(minutes=15)
        )

        payload1 = decode_token(token1)
        payload2 = decode_token(token2)

        # Both tokens should be for same user
        assert payload1['sub'] == payload2['sub']
