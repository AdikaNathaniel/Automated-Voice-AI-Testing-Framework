"""
Tests for centralized authentication dependency

This module tests the centralized get_current_user_with_db function
that replaces duplicate implementations across route files.
"""

import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import pytest
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4


class TestGetCurrentUserWithDbExists:
    """Test get_current_user_with_db function exists in dependencies."""

    def test_function_exists(self):
        """Test that get_current_user_with_db can be imported."""
        from api.dependencies import get_current_user_with_db
        assert get_current_user_with_db is not None

    def test_function_is_async(self):
        """Test that get_current_user_with_db is an async function."""
        import asyncio
        from api.dependencies import get_current_user_with_db
        assert asyncio.iscoroutinefunction(get_current_user_with_db)


class TestGetCurrentUserWithDbBehavior:
    """Test get_current_user_with_db behavior."""

    @pytest.fixture
    def mock_credentials(self):
        """Create mock HTTP credentials."""
        mock = Mock()
        mock.credentials = "valid.jwt.token"
        return mock

    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        return AsyncMock()

    @pytest.fixture
    def mock_user(self):
        """Create mock user object."""
        from datetime import datetime
        user = Mock()
        user.id = uuid4()
        user.tenant_id = None
        user.username = "testuser"
        user.email = "test@example.com"
        user.role = "validator"
        user.is_active = True
        user.full_name = "Test User"
        user.created_at = datetime.now()
        user.updated_at = datetime.now()
        return user

    @pytest.mark.asyncio
    async def test_returns_user_response_on_valid_token(
        self, mock_credentials, mock_db, mock_user
    ):
        """Test that valid token returns UserResponse."""
        from api.dependencies import get_current_user_with_db
        from api.schemas.auth import UserResponse

        user_id = mock_user.id

        with patch('api.dependencies.decode_token') as mock_decode, \
             patch('api.dependencies.user_service') as mock_service:

            mock_decode.return_value = {"sub": str(user_id)}
            mock_service.get_user_by_id = AsyncMock(return_value=mock_user)

            result = await get_current_user_with_db(mock_credentials, mock_db)

            assert isinstance(result, UserResponse)
            assert result.username == "testuser"

    @pytest.mark.asyncio
    async def test_raises_401_on_missing_sub_claim(self, mock_credentials, mock_db):
        """Test that missing sub claim raises 401."""
        from fastapi import HTTPException
        from api.dependencies import get_current_user_with_db

        with patch('api.dependencies.decode_token') as mock_decode:
            mock_decode.return_value = {}  # Missing "sub" claim

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user_with_db(mock_credentials, mock_db)

            assert exc_info.value.status_code == 401
            assert "Could not validate credentials" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_raises_401_on_user_not_found(self, mock_credentials, mock_db):
        """Test that user not found raises 401."""
        from fastapi import HTTPException
        from api.dependencies import get_current_user_with_db

        with patch('api.dependencies.decode_token') as mock_decode, \
             patch('api.dependencies.user_service') as mock_service:

            mock_decode.return_value = {"sub": str(uuid4())}
            mock_service.get_user_by_id = AsyncMock(return_value=None)

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user_with_db(mock_credentials, mock_db)

            assert exc_info.value.status_code == 401
            assert "User not found" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_raises_401_on_inactive_user(
        self, mock_credentials, mock_db, mock_user
    ):
        """Test that inactive user raises 401."""
        from fastapi import HTTPException
        from api.dependencies import get_current_user_with_db

        mock_user.is_active = False

        with patch('api.dependencies.decode_token') as mock_decode, \
             patch('api.dependencies.user_service') as mock_service:

            mock_decode.return_value = {"sub": str(mock_user.id)}
            mock_service.get_user_by_id = AsyncMock(return_value=mock_user)

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user_with_db(mock_credentials, mock_db)

            assert exc_info.value.status_code == 401
            assert "Inactive user" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_raises_401_on_jwt_error(self, mock_credentials, mock_db):
        """Test that JWTError raises 401."""
        from fastapi import HTTPException
        from jose import JWTError
        from api.dependencies import get_current_user_with_db

        with patch('api.dependencies.decode_token') as mock_decode:
            mock_decode.side_effect = JWTError("Invalid token")

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user_with_db(mock_credentials, mock_db)

            assert exc_info.value.status_code == 401


class TestGetCurrentUserWithDbIntegration:
    """Test get_current_user_with_db can be used as FastAPI dependency."""

    def test_can_be_used_as_dependency(self):
        """Test that function can be used with Depends()."""
        from fastapi import Depends
        from api.dependencies import get_current_user_with_db

        # Should not raise any errors
        dependency = Depends(get_current_user_with_db)
        assert dependency is not None
