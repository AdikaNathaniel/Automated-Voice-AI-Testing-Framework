"""
Unit tests for authentication API routes.

Tests the authentication endpoints including registration, login,
token refresh, logout, and current user retrieval.
Uses mocked database sessions, services, and authentication components
to test route logic without external dependencies.
"""

import pytest
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from jose import JWTError

from api.routes.auth import (
    router,
    register,
    login,
    refresh_token,
    logout,
    get_me,
)
from api.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    LoginResponse,
    TokenRefreshRequest,
    TokenRefreshResponse,
    UserResponse,
)
from api.auth.roles import Role
from services.login_attempt_tracker import login_attempt_tracker
from services.refresh_token_store import refresh_token_store


class TestRegisterEndpoint:
    """Test POST /register endpoint."""

    @pytest.fixture
    def mock_db(self):
        """Provide mocked async database session."""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def admin_user(self):
        """Provide mock admin user."""
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.email = "admin@example.com"
        user.username = "admin"
        user.role = Role.ORG_ADMIN.value
        user.is_active = True
        return user

    @pytest.fixture
    def regular_user(self):
        """Provide mock regular user."""
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.email = "user@example.com"
        user.username = "user"
        user.role = Role.VIEWER.value
        user.is_active = True
        return user

    @pytest.fixture
    def register_request(self):
        """Provide valid registration request."""
        return RegisterRequest(
            email="newuser@example.com",
            username="newuser",
            password="Secure_Password_123!",
            full_name="New User"
        )

    @pytest.mark.asyncio
    async def test_register_success_by_admin(
        self,
        mock_db,
        admin_user,
        register_request
    ):
        """Test successful user registration by admin."""
        from datetime import datetime
        mock_created_user = MagicMock()
        mock_created_user.id = uuid4()
        mock_created_user.email = register_request.email
        mock_created_user.username = register_request.username
        mock_created_user.full_name = register_request.full_name
        mock_created_user.is_active = True
        mock_created_user.created_at = datetime.utcnow()
        mock_created_user.updated_at = datetime.utcnow()
        mock_created_user.tenant_id = uuid4()
        mock_created_user.role = Role.VIEWER

        with patch('services.user_service.create_user', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_created_user

            result = await register(
                data=register_request,
                db=mock_db,
                current_user=admin_user
            )

            # Verify result
            assert result is not None
            assert "user" in result
            assert "message" in result
            assert result["message"] == "User registered successfully"
            assert mock_create.called

    @pytest.mark.asyncio
    async def test_register_forbidden_non_admin(
        self,
        mock_db,
        regular_user,
        register_request
    ):
        """Test that non-admin user cannot register."""
        with pytest.raises(HTTPException) as exc_info:
            await register(
                data=register_request,
                db=mock_db,
                current_user=regular_user
            )

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Admin privileges required" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_register_email_already_exists(
        self,
        mock_db,
        admin_user,
        register_request
    ):
        """Test registration fails when email already exists."""
        with patch('services.user_service.create_user', new_callable=AsyncMock) as mock_create:
            mock_create.side_effect = IntegrityError("duplicate", "duplicate", "duplicate")

            with pytest.raises(HTTPException) as exc_info:
                await register(
                    data=register_request,
                    db=mock_db,
                    current_user=admin_user
                )

            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
            assert "Email or username already registered" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_register_generic_error(
        self,
        mock_db,
        admin_user,
        register_request
    ):
        """Test registration handles generic errors."""
        with patch('services.user_service.create_user', new_callable=AsyncMock) as mock_create:
            mock_create.side_effect = ValueError("Some error")

            with pytest.raises(HTTPException) as exc_info:
                await register(
                    data=register_request,
                    db=mock_db,
                    current_user=admin_user
                )

            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST


class TestLoginEndpoint:
    """Test POST /login endpoint."""

    @pytest.fixture
    def mock_db(self):
        """Provide mocked async database session."""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def login_request(self):
        """Provide valid login request."""
        return LoginRequest(
            email="user@example.com",
            password="password123"
        )

    @pytest.fixture
    def mock_user(self):
        """Provide mock user."""
        from datetime import datetime
        user = MagicMock()
        user.id = uuid4()
        user.email = "user@example.com"
        user.password_hash = "hashed_password"
        user.is_active = True
        user.role = Role.VIEWER.value
        user.username = "user"
        user.full_name = "Test User"
        user.tenant_id = uuid4()
        user.created_at = datetime.utcnow()
        user.updated_at = datetime.utcnow()
        return user

    @pytest.mark.asyncio
    async def test_login_success(
        self,
        mock_db,
        login_request,
        mock_user
    ):
        """Test successful login."""
        with patch.object(login_attempt_tracker, 'is_locked_out', return_value=False):
            with patch.object(login_attempt_tracker, 'get_wait_time', return_value=0):
                with patch('services.user_service.get_user_by_email', new_callable=AsyncMock) as mock_get_user:
                    with patch('api.routes.auth.verify_password', return_value=True):
                        with patch('api.routes.auth.create_access_token', return_value="access_token_123"):
                            with patch('api.routes.auth.create_refresh_token', return_value="refresh_token_456"):
                                with patch.object(refresh_token_store, 'save') as mock_save:
                                    with patch.object(login_attempt_tracker, 'record_success') as mock_success:
                                        mock_get_user.return_value = mock_user

                                        result = await login(
                                            data=login_request,
                                            db=mock_db
                                        )

                                        # Verify result
                                        assert isinstance(result, LoginResponse)
                                        assert result.access_token == "access_token_123"
                                        assert result.refresh_token == "refresh_token_456"
                                        assert result.token_type == "bearer"
                                        assert mock_save.called
                                        assert mock_success.called

    @pytest.mark.asyncio
    async def test_login_account_locked_out(
        self,
        mock_db,
        login_request
    ):
        """Test login fails when account is locked out."""
        with patch.object(login_attempt_tracker, 'is_locked_out', return_value=True):
            with patch.object(login_attempt_tracker, 'get_remaining_lockout_seconds', return_value=900):
                with pytest.raises(HTTPException) as exc_info:
                    await login(
                        data=login_request,
                        db=mock_db
                    )

                assert exc_info.value.status_code == status.HTTP_429_TOO_MANY_REQUESTS
                assert "Account temporarily locked" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_login_rate_limited(
        self,
        mock_db,
        login_request
    ):
        """Test login fails when rate limited."""
        with patch.object(login_attempt_tracker, 'is_locked_out', return_value=False):
            with patch.object(login_attempt_tracker, 'get_wait_time', return_value=30):
                with pytest.raises(HTTPException) as exc_info:
                    await login(
                        data=login_request,
                        db=mock_db
                    )

                assert exc_info.value.status_code == status.HTTP_429_TOO_MANY_REQUESTS
                assert "Too many login attempts" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_login_user_not_found(
        self,
        mock_db,
        login_request
    ):
        """Test login fails when user not found."""
        with patch.object(login_attempt_tracker, 'is_locked_out', return_value=False):
            with patch.object(login_attempt_tracker, 'get_wait_time', return_value=0):
                with patch('services.user_service.get_user_by_email', new_callable=AsyncMock) as mock_get_user:
                    with patch.object(login_attempt_tracker, 'record_failure') as mock_failure:
                        mock_get_user.return_value = None
                        mock_failure.return_value = {
                            'locked': False,
                            'attempts_remaining': 4,
                            'wait_seconds': 0
                        }

                        with pytest.raises(HTTPException) as exc_info:
                            await login(
                                data=login_request,
                                db=mock_db
                            )

                        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
                        assert "Incorrect email or password" in exc_info.value.detail
                        assert mock_failure.called

    @pytest.mark.asyncio
    async def test_login_wrong_password(
        self,
        mock_db,
        login_request,
        mock_user
    ):
        """Test login fails with incorrect password."""
        with patch.object(login_attempt_tracker, 'is_locked_out', return_value=False):
            with patch.object(login_attempt_tracker, 'get_wait_time', return_value=0):
                with patch('services.user_service.get_user_by_email', new_callable=AsyncMock) as mock_get_user:
                    with patch('api.routes.auth.verify_password', return_value=False):
                        with patch.object(login_attempt_tracker, 'record_failure') as mock_failure:
                            mock_get_user.return_value = mock_user
                            mock_failure.return_value = {
                                'locked': False,
                                'attempts_remaining': 3,
                                'wait_seconds': 0
                            }

                            with pytest.raises(HTTPException) as exc_info:
                                await login(
                                    data=login_request,
                                    db=mock_db
                                )

                            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
                            assert "Incorrect email or password" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_login_inactive_user(
        self,
        mock_db,
        login_request
    ):
        """Test login fails for inactive user."""
        inactive_user = MagicMock()
        inactive_user.id = uuid4()
        inactive_user.is_active = False
        inactive_user.password_hash = "hashed_password"

        with patch.object(login_attempt_tracker, 'is_locked_out', return_value=False):
            with patch.object(login_attempt_tracker, 'get_wait_time', return_value=0):
                with patch('services.user_service.get_user_by_email', new_callable=AsyncMock) as mock_get_user:
                    with patch('api.routes.auth.verify_password', return_value=True):
                        mock_get_user.return_value = inactive_user

                        with pytest.raises(HTTPException) as exc_info:
                            await login(
                                data=login_request,
                                db=mock_db
                            )

                        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
                        assert "Inactive user" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_login_account_lockout_after_failed_attempts(
        self,
        mock_db,
        login_request,
        mock_user
    ):
        """Test that account locks after multiple failed password attempts."""
        with patch.object(login_attempt_tracker, 'is_locked_out', return_value=False):
            with patch.object(login_attempt_tracker, 'get_wait_time', return_value=0):
                with patch('services.user_service.get_user_by_email', new_callable=AsyncMock) as mock_get_user:
                    with patch('api.routes.auth.verify_password', return_value=False):
                        with patch.object(login_attempt_tracker, 'record_failure') as mock_failure:
                            mock_get_user.return_value = mock_user
                            mock_failure.return_value = {
                                'locked': True,
                                'attempts_remaining': 0,
                                'wait_seconds': 900
                            }

                            with pytest.raises(HTTPException) as exc_info:
                                await login(
                                    data=login_request,
                                    db=mock_db
                                )

                            assert exc_info.value.status_code == status.HTTP_429_TOO_MANY_REQUESTS
                            assert "Account locked" in exc_info.value.detail


class TestRefreshTokenEndpoint:
    """Test POST /refresh endpoint."""

    @pytest.fixture
    def mock_db(self):
        """Provide mocked async database session."""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def refresh_request(self):
        """Provide valid refresh token request with JWT-like format."""
        # Token must have 3 dot-separated parts to pass format validation
        return TokenRefreshRequest(
            refresh_token="header.payload.signature"
        )

    @pytest.fixture
    def mock_user(self):
        """Provide mock user."""
        user = MagicMock()
        user.id = uuid4()
        user.email = "user@example.com"
        user.is_active = True
        return user

    @pytest.mark.asyncio
    async def test_refresh_token_success(
        self,
        mock_db,
        refresh_request,
        mock_user
    ):
        """Test successful token refresh."""
        user_id = mock_user.id

        with patch('api.routes.auth.decode_token') as mock_decode:
            with patch.object(refresh_token_store, 'verify', return_value=True):
                with patch.object(refresh_token_store, 'revoke') as mock_revoke:
                    with patch('services.user_service.get_user_by_id', new_callable=AsyncMock) as mock_get_user:
                        with patch('api.routes.auth.create_access_token', return_value="new_access_token"):
                            with patch('api.routes.auth.create_refresh_token', return_value="new_refresh_token"):
                                with patch.object(refresh_token_store, 'save') as mock_save:
                                    mock_decode.return_value = {
                                        "sub": str(user_id),
                                        "type": "refresh"
                                    }
                                    mock_get_user.return_value = mock_user

                                    result = await refresh_token(
                                        data=refresh_request,
                                        db=mock_db
                                    )

                                    # Verify result
                                    assert isinstance(result, TokenRefreshResponse)
                                    assert result.access_token == "new_access_token"
                                    assert result.refresh_token == "new_refresh_token"
                                    assert result.token_type == "bearer"
                                    assert mock_revoke.called
                                    assert mock_save.called

    @pytest.mark.asyncio
    async def test_refresh_token_invalid_token(
        self,
        mock_db,
        refresh_request
    ):
        """Test refresh fails with invalid token."""
        with patch('api.routes.auth.decode_token') as mock_decode:
            mock_decode.side_effect = JWTError()

            with pytest.raises(HTTPException) as exc_info:
                await refresh_token(
                    data=refresh_request,
                    db=mock_db
                )

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert "Invalid refresh token" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_refresh_token_invalid_type(
        self,
        mock_db,
        refresh_request
    ):
        """Test refresh fails when token type is not 'refresh'."""
        with patch('api.routes.auth.decode_token') as mock_decode:
            mock_decode.return_value = {
                "sub": str(uuid4()),
                "type": "access"  # Wrong type
            }

            with pytest.raises(HTTPException) as exc_info:
                await refresh_token(
                    data=refresh_request,
                    db=mock_db
                )

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert "Invalid token type" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_refresh_token_no_sub_claim(
        self,
        mock_db,
        refresh_request
    ):
        """Test refresh fails when sub claim is missing."""
        with patch('api.routes.auth.decode_token') as mock_decode:
            mock_decode.return_value = {
                "type": "refresh"
                # Missing "sub"
            }

            with pytest.raises(HTTPException) as exc_info:
                await refresh_token(
                    data=refresh_request,
                    db=mock_db
                )

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert "Invalid refresh token" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_refresh_token_not_in_store(
        self,
        mock_db,
        refresh_request,
        mock_user
    ):
        """Test refresh fails when token not in store."""
        user_id = mock_user.id

        with patch('api.routes.auth.decode_token') as mock_decode:
            with patch.object(refresh_token_store, 'verify', return_value=False):
                mock_decode.return_value = {
                    "sub": str(user_id),
                    "type": "refresh"
                }

                with pytest.raises(HTTPException) as exc_info:
                    await refresh_token(
                        data=refresh_request,
                        db=mock_db
                    )

                assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
                assert "Invalid or expired refresh token" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_refresh_token_user_not_found(
        self,
        mock_db,
        refresh_request
    ):
        """Test refresh fails when user not found."""
        user_id = uuid4()

        with patch('api.routes.auth.decode_token') as mock_decode:
            with patch.object(refresh_token_store, 'verify', return_value=True):
                with patch('services.user_service.get_user_by_id', new_callable=AsyncMock) as mock_get_user:
                    mock_decode.return_value = {
                        "sub": str(user_id),
                        "type": "refresh"
                    }
                    mock_get_user.return_value = None

                    with pytest.raises(HTTPException) as exc_info:
                        await refresh_token(
                            data=refresh_request,
                            db=mock_db
                        )

                    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
                    assert "User not found or inactive" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_refresh_token_user_inactive(
        self,
        mock_db,
        refresh_request
    ):
        """Test refresh fails when user is inactive."""
        user_id = uuid4()
        inactive_user = MagicMock()
        inactive_user.id = user_id
        inactive_user.is_active = False

        with patch('api.routes.auth.decode_token') as mock_decode:
            with patch.object(refresh_token_store, 'verify', return_value=True):
                with patch('services.user_service.get_user_by_id', new_callable=AsyncMock) as mock_get_user:
                    mock_decode.return_value = {
                        "sub": str(user_id),
                        "type": "refresh"
                    }
                    mock_get_user.return_value = inactive_user

                    with pytest.raises(HTTPException) as exc_info:
                        await refresh_token(
                            data=refresh_request,
                            db=mock_db
                        )

                    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
                    assert "User not found or inactive" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_refresh_token_invalid_format(
        self,
        mock_db
    ):
        """Test refresh fails with token that doesn't have 3 parts."""
        # Create request with invalid format (not 3 dot-separated parts)
        invalid_request = TokenRefreshRequest(refresh_token="not-a-jwt-token")

        with pytest.raises(HTTPException) as exc_info:
            await refresh_token(
                data=invalid_request,
                db=mock_db
            )

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid refresh token" in exc_info.value.detail


class TestLogoutEndpoint:
    """Test POST /logout endpoint."""

    @pytest.fixture
    def logout_request(self):
        """Provide valid logout request with JWT-like format."""
        # Token must have 3 dot-separated parts to pass format validation
        return TokenRefreshRequest(
            refresh_token="header.payload.signature"
        )

    @pytest.mark.asyncio
    async def test_logout_success(self, logout_request):
        """Test successful logout."""
        user_id = uuid4()

        with patch('api.routes.auth.decode_token') as mock_decode:
            with patch.object(refresh_token_store, 'verify', return_value=True):
                with patch.object(refresh_token_store, 'revoke') as mock_revoke:
                    mock_decode.return_value = {
                        "sub": str(user_id),
                        "type": "refresh"
                    }

                    result = await logout(data=logout_request)

                    # Verify result
                    assert result is not None
                    assert "message" in result
                    assert result["message"] == "Logout successful"
                    assert mock_revoke.called

    @pytest.mark.asyncio
    async def test_logout_invalid_token_type(self, logout_request):
        """Test logout fails with invalid token type."""
        with patch('api.routes.auth.decode_token') as mock_decode:
            mock_decode.return_value = {
                "sub": str(uuid4()),
                "type": "access"  # Wrong type
            }

            with pytest.raises(HTTPException) as exc_info:
                await logout(data=logout_request)

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert "Invalid token type" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_logout_no_sub_claim(self, logout_request):
        """Test logout fails when sub claim missing."""
        with patch('api.routes.auth.decode_token') as mock_decode:
            mock_decode.return_value = {
                "type": "refresh"
                # Missing "sub"
            }

            with pytest.raises(HTTPException) as exc_info:
                await logout(data=logout_request)

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert "Invalid refresh token" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_logout_token_not_in_store(self, logout_request):
        """Test logout fails when token not in store."""
        user_id = uuid4()

        with patch('api.routes.auth.decode_token') as mock_decode:
            with patch.object(refresh_token_store, 'verify', return_value=False):
                mock_decode.return_value = {
                    "sub": str(user_id),
                    "type": "refresh"
                }

                with pytest.raises(HTTPException) as exc_info:
                    await logout(data=logout_request)

                assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
                assert "Invalid or expired refresh token" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_logout_invalid_token(self, logout_request):
        """Test logout fails with invalid JWT."""
        with patch('api.routes.auth.decode_token') as mock_decode:
            mock_decode.side_effect = JWTError()

            with pytest.raises(HTTPException) as exc_info:
                await logout(data=logout_request)

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert "Could not validate refresh token" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_logout_invalid_format(self, logout_request):
        """Test logout fails with invalid token format."""
        with patch('api.routes.auth.decode_token') as mock_decode:
            mock_decode.side_effect = ValueError("Invalid format")

            with pytest.raises(HTTPException) as exc_info:
                await logout(data=logout_request)

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert "Invalid token format" in exc_info.value.detail


class TestGetMeEndpoint:
    """Test GET /me endpoint."""

    @pytest.fixture
    def current_user(self):
        """Provide mock current user."""
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.email = "user@example.com"
        user.username = "user"
        user.role = Role.VIEWER.value
        user.is_active = True
        return user

    @pytest.mark.asyncio
    async def test_get_me_success(self, current_user):
        """Test successfully retrieving current user."""
        result = await get_me(current_user=current_user)

        # Verify result is the current user
        assert result == current_user
        assert result.id == current_user.id
        assert result.email == current_user.email


class TestAuthRoutesIntegration:
    """Integration tests for auth routes."""

    def test_router_has_required_endpoints(self):
        """Test that router has all required endpoints."""
        routes = [route.path for route in router.routes]

        # Check for auth endpoints (with /auth prefix)
        assert "/auth/register" in routes
        assert "/auth/login" in routes
        assert "/auth/refresh" in routes
        assert "/auth/logout" in routes
        assert "/auth/me" in routes

    def test_router_methods(self):
        """Test that endpoints use correct HTTP methods."""
        methods_by_path = {}
        for route in router.routes:
            methods_by_path[route.path] = route.methods

        # Verify HTTP methods (with /auth prefix)
        assert "POST" in methods_by_path["/auth/register"]
        assert "POST" in methods_by_path["/auth/login"]
        assert "POST" in methods_by_path["/auth/refresh"]
        assert "POST" in methods_by_path["/auth/logout"]
        assert "GET" in methods_by_path["/auth/me"]

    def test_router_response_models(self):
        """Test that endpoints declare response models."""
        # Verify all endpoints have response models
        for route in router.routes:
            if route.path in ["/auth/register", "/auth/login", "/auth/refresh", "/auth/logout", "/auth/me"]:
                # All auth endpoints should have a response model
                assert route.response_model is not None or route.path == "/auth/register"
