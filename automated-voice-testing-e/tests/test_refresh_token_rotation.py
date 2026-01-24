"""
Test suite for refresh token rotation with Redis

Tests refresh token storage, validation, and rotation functionality
including Redis integration for token blacklisting and TTL management.
"""

import pytest
import pytest_asyncio
from pathlib import Path
from uuid import uuid4
from datetime import timedelta


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
REFRESH_TOKEN_FILE = PROJECT_ROOT / "backend" / "api" / "auth" / "refresh_token.py"


class TestRefreshTokenFileExists:
    """Test that refresh token module exists"""

    def test_refresh_token_file_exists(self):
        """Test that backend/api/auth/refresh_token.py exists"""
        assert REFRESH_TOKEN_FILE.exists(), "backend/api/auth/refresh_token.py should exist"
        assert REFRESH_TOKEN_FILE.is_file(), "refresh_token.py should be a file"

    def test_refresh_token_has_content(self):
        """Test that refresh_token.py has content"""
        content = REFRESH_TOKEN_FILE.read_text()
        assert len(content) > 0, "refresh_token.py should not be empty"


class TestRefreshTokenImports:
    """Test that refresh token module can be imported"""

    def test_can_import_refresh_token_module(self):
        """Test that refresh token module can be imported"""
        try:
            from api.auth import refresh_token
            assert refresh_token is not None
        except ImportError as e:
            pytest.fail(f"Failed to import refresh_token: {e}")


class TestStoreRefreshTokenFunction:
    """Test store_refresh_token function"""

    def test_store_refresh_token_exists(self):
        """Test that store_refresh_token function exists"""
        from api.auth.refresh_token import store_refresh_token
        assert callable(store_refresh_token), "store_refresh_token should be callable"

    @pytest.mark.asyncio
    async def test_store_refresh_token_signature(self):
        """Test store_refresh_token function signature"""
        from api.auth.refresh_token import store_refresh_token
        import inspect

        sig = inspect.signature(store_refresh_token)
        params = list(sig.parameters.keys())

        # Should have redis, token, and user_id parameters
        assert any('redis' in p.lower() for p in params), "Should have redis parameter"
        assert any('token' in p.lower() for p in params), "Should have token parameter"
        assert any('user' in p.lower() for p in params), "Should have user_id parameter"

    @pytest.mark.asyncio
    async def test_store_refresh_token_stores_in_redis(self, mock_redis):
        """Test that store_refresh_token stores token in Redis"""
        from api.auth.refresh_token import store_refresh_token

        user_id = uuid4()
        token = "test_refresh_token_123"

        await store_refresh_token(mock_redis, token, user_id)

        # Verify token was stored
        stored = await mock_redis.get(f"refresh_token:{token}")
        assert stored is not None, "Token should be stored in Redis"

    @pytest.mark.asyncio
    async def test_store_refresh_token_with_ttl(self, mock_redis):
        """Test that store_refresh_token sets TTL on token"""
        from api.auth.refresh_token import store_refresh_token

        user_id = uuid4()
        token = "test_token_with_ttl"

        await store_refresh_token(mock_redis, token, user_id)

        # Verify TTL is set (should be 7 days by default)
        ttl = await mock_redis.ttl(f"refresh_token:{token}")
        assert ttl > 0, "Token should have TTL set"
        # Should be close to 7 days (604800 seconds)
        assert ttl <= 604800, "TTL should not exceed 7 days"
        assert ttl >= 604700, "TTL should be close to 7 days"

    @pytest.mark.asyncio
    async def test_store_refresh_token_stores_user_id(self, mock_redis):
        """Test that stored token includes user_id"""
        from api.auth.refresh_token import store_refresh_token

        user_id = uuid4()
        token = "test_token_user_id"

        await store_refresh_token(mock_redis, token, user_id)

        # Verify user_id is stored with token
        stored = await mock_redis.get(f"refresh_token:{token}")
        assert str(user_id) in str(stored), "User ID should be stored with token"


class TestValidateRefreshTokenFunction:
    """Test validate_refresh_token function"""

    def test_validate_refresh_token_exists(self):
        """Test that validate_refresh_token function exists"""
        from api.auth.refresh_token import validate_refresh_token
        assert callable(validate_refresh_token), "validate_refresh_token should be callable"

    @pytest.mark.asyncio
    async def test_validate_refresh_token_returns_bool(self, mock_redis):
        """Test that validate_refresh_token returns boolean"""
        from api.auth.refresh_token import validate_refresh_token

        token = "test_token"
        result = await validate_refresh_token(mock_redis, token)

        assert isinstance(result, bool), "validate_refresh_token should return boolean"

    @pytest.mark.asyncio
    async def test_validate_valid_token_returns_true(self, mock_redis):
        """Test that valid token returns True"""
        from api.auth.refresh_token import store_refresh_token, validate_refresh_token

        user_id = uuid4()
        token = "valid_token_123"

        # Store token first
        await store_refresh_token(mock_redis, token, user_id)

        # Validate it
        is_valid = await validate_refresh_token(mock_redis, token)
        assert is_valid is True, "Valid stored token should return True"

    @pytest.mark.asyncio
    async def test_validate_invalid_token_returns_false(self, mock_redis):
        """Test that non-existent token returns False"""
        from api.auth.refresh_token import validate_refresh_token

        token = "nonexistent_token_xyz"

        is_valid = await validate_refresh_token(mock_redis, token)
        assert is_valid is False, "Non-existent token should return False"

    @pytest.mark.asyncio
    async def test_validate_blacklisted_token_returns_false(self, mock_redis):
        """Test that blacklisted token returns False"""
        from api.auth.refresh_token import (
            store_refresh_token,
            invalidate_refresh_token,
            validate_refresh_token
        )

        user_id = uuid4()
        token = "token_to_blacklist"

        # Store and then invalidate
        await store_refresh_token(mock_redis, token, user_id)
        await invalidate_refresh_token(mock_redis, token)

        # Should now be invalid
        is_valid = await validate_refresh_token(mock_redis, token)
        assert is_valid is False, "Blacklisted token should return False"


class TestInvalidateRefreshTokenFunction:
    """Test invalidate_refresh_token function"""

    def test_invalidate_refresh_token_exists(self):
        """Test that invalidate_refresh_token function exists"""
        from api.auth.refresh_token import invalidate_refresh_token
        assert callable(invalidate_refresh_token), "invalidate_refresh_token should be callable"

    @pytest.mark.asyncio
    async def test_invalidate_token_removes_from_redis(self, mock_redis):
        """Test that invalidate_refresh_token removes token from Redis"""
        from api.auth.refresh_token import (
            store_refresh_token,
            invalidate_refresh_token
        )

        user_id = uuid4()
        token = "token_to_invalidate"

        # Store token
        await store_refresh_token(mock_redis, token, user_id)

        # Verify it exists
        exists_before = await mock_redis.exists(f"refresh_token:{token}")
        assert exists_before, "Token should exist before invalidation"

        # Invalidate token
        await invalidate_refresh_token(mock_redis, token)

        # Verify it's gone or blacklisted
        exists_after = await mock_redis.exists(f"refresh_token:{token}")
        blacklisted = await mock_redis.exists(f"blacklist:{token}")

        assert not exists_after or blacklisted, "Token should be removed or blacklisted"

    @pytest.mark.asyncio
    async def test_invalidate_nonexistent_token_no_error(self, mock_redis):
        """Test that invalidating non-existent token doesn't raise error"""
        from api.auth.refresh_token import invalidate_refresh_token

        token = "nonexistent_token"

        # Should not raise error
        try:
            await invalidate_refresh_token(mock_redis, token)
        except Exception as e:
            pytest.fail(f"Invalidating non-existent token should not raise error: {e}")


class TestRotateRefreshTokenFunction:
    """Test rotate_refresh_token function"""

    def test_rotate_refresh_token_exists(self):
        """Test that rotate_refresh_token function exists"""
        from api.auth.refresh_token import rotate_refresh_token
        assert callable(rotate_refresh_token), "rotate_refresh_token should be callable"

    @pytest.mark.asyncio
    async def test_rotate_token_returns_new_token(self, mock_redis):
        """Test that rotate_refresh_token returns new token"""
        from api.auth.refresh_token import (
            store_refresh_token,
            rotate_refresh_token
        )

        user_id = uuid4()
        old_token = "old_refresh_token"

        # Store old token
        await store_refresh_token(mock_redis, old_token, user_id)

        # Rotate token
        new_token = await rotate_refresh_token(mock_redis, old_token, user_id)

        assert new_token is not None, "Should return new token"
        assert isinstance(new_token, str), "New token should be string"
        assert new_token != old_token, "New token should be different from old"

    @pytest.mark.asyncio
    async def test_rotate_token_invalidates_old_token(self, mock_redis):
        """Test that rotating token invalidates the old one"""
        from api.auth.refresh_token import (
            store_refresh_token,
            rotate_refresh_token,
            validate_refresh_token
        )

        user_id = uuid4()
        old_token = "old_token_to_rotate"

        # Store old token
        await store_refresh_token(mock_redis, old_token, user_id)

        # Verify old token is valid
        is_valid_before = await validate_refresh_token(mock_redis, old_token)
        assert is_valid_before is True, "Old token should be valid before rotation"

        # Rotate token
        new_token = await rotate_refresh_token(mock_redis, old_token, user_id)

        # Old token should now be invalid
        is_valid_after = await validate_refresh_token(mock_redis, old_token)
        assert is_valid_after is False, "Old token should be invalid after rotation"

    @pytest.mark.asyncio
    async def test_rotate_token_stores_new_token(self, mock_redis):
        """Test that rotating token stores the new token"""
        from api.auth.refresh_token import (
            store_refresh_token,
            rotate_refresh_token,
            validate_refresh_token
        )

        user_id = uuid4()
        old_token = "old_token_123"

        # Store old token
        await store_refresh_token(mock_redis, old_token, user_id)

        # Rotate token
        new_token = await rotate_refresh_token(mock_redis, old_token, user_id)

        # New token should be valid
        is_valid = await validate_refresh_token(mock_redis, new_token)
        assert is_valid is True, "New token should be valid after rotation"


class TestRefreshTokenWorkflow:
    """Test complete refresh token workflow"""

    @pytest.mark.asyncio
    async def test_store_validate_invalidate_workflow(self, mock_redis):
        """Test complete token lifecycle"""
        from api.auth.refresh_token import (
            store_refresh_token,
            validate_refresh_token,
            invalidate_refresh_token
        )

        user_id = uuid4()
        token = "workflow_token"

        # 1. Store token
        await store_refresh_token(mock_redis, token, user_id)

        # 2. Validate it works
        is_valid = await validate_refresh_token(mock_redis, token)
        assert is_valid is True, "Stored token should be valid"

        # 3. Invalidate token
        await invalidate_refresh_token(mock_redis, token)

        # 4. Verify it's now invalid
        is_valid_after = await validate_refresh_token(mock_redis, token)
        assert is_valid_after is False, "Invalidated token should be invalid"

    @pytest.mark.asyncio
    async def test_rotation_workflow(self, mock_redis):
        """Test token rotation workflow"""
        from api.auth.refresh_token import (
            store_refresh_token,
            validate_refresh_token,
            rotate_refresh_token
        )

        user_id = uuid4()
        token1 = "first_token"

        # 1. Store first token
        await store_refresh_token(mock_redis, token1, user_id)

        # 2. Rotate to get second token
        token2 = await rotate_refresh_token(mock_redis, token1, user_id)

        # 3. First token should be invalid
        assert await validate_refresh_token(mock_redis, token1) is False

        # 4. Second token should be valid
        assert await validate_refresh_token(mock_redis, token2) is True

        # 5. Rotate again
        token3 = await rotate_refresh_token(mock_redis, token2, user_id)

        # 6. Second token should now be invalid
        assert await validate_refresh_token(mock_redis, token2) is False

        # 7. Third token should be valid
        assert await validate_refresh_token(mock_redis, token3) is True


class TestRefreshTokenEdgeCases:
    """Test edge cases"""

    @pytest.mark.asyncio
    async def test_store_token_with_empty_string(self, mock_redis):
        """Test storing empty token string"""
        from api.auth.refresh_token import store_refresh_token

        user_id = uuid4()
        token = ""

        # Should handle gracefully or raise ValueError
        try:
            await store_refresh_token(mock_redis, token, user_id)
        except ValueError:
            # Expected behavior for empty token
            pass

    @pytest.mark.asyncio
    async def test_validate_empty_token(self, mock_redis):
        """Test validating empty token"""
        from api.auth.refresh_token import validate_refresh_token

        token = ""
        is_valid = await validate_refresh_token(mock_redis, token)
        assert is_valid is False, "Empty token should be invalid"

    @pytest.mark.asyncio
    async def test_multiple_tokens_for_same_user(self, mock_redis):
        """Test storing multiple tokens for same user"""
        from api.auth.refresh_token import (
            store_refresh_token,
            validate_refresh_token
        )

        user_id = uuid4()
        token1 = "user_token_1"
        token2 = "user_token_2"

        # Store multiple tokens for same user
        await store_refresh_token(mock_redis, token1, user_id)
        await store_refresh_token(mock_redis, token2, user_id)

        # Both should be valid
        assert await validate_refresh_token(mock_redis, token1) is True
        assert await validate_refresh_token(mock_redis, token2) is True


class TestRefreshTokenDocumentation:
    """Test module documentation"""

    def test_module_has_docstring(self):
        """Test that refresh_token module has docstring"""
        from api.auth import refresh_token

        assert refresh_token.__doc__ is not None, \
            "refresh_token module should have docstring"

    def test_store_refresh_token_has_docstring(self):
        """Test that store_refresh_token has docstring"""
        from api.auth.refresh_token import store_refresh_token

        assert store_refresh_token.__doc__ is not None, \
            "store_refresh_token should have docstring"

    def test_validate_refresh_token_has_docstring(self):
        """Test that validate_refresh_token has docstring"""
        from api.auth.refresh_token import validate_refresh_token

        assert validate_refresh_token.__doc__ is not None, \
            "validate_refresh_token should have docstring"

    def test_invalidate_refresh_token_has_docstring(self):
        """Test that invalidate_refresh_token has docstring"""
        from api.auth.refresh_token import invalidate_refresh_token

        assert invalidate_refresh_token.__doc__ is not None, \
            "invalidate_refresh_token should have docstring"


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest_asyncio.fixture
async def mock_redis():
    """
    Create a mock Redis client for testing
    Uses in-memory dictionary to simulate Redis operations
    """
    class MockRedis:
        def __init__(self):
            self.data = {}
            self.ttls = {}

        async def set(self, key: str, value: str, ex: int = None):
            """Set a key-value pair with optional TTL"""
            self.data[key] = value
            if ex:
                self.ttls[key] = ex
            return True

        async def get(self, key: str):
            """Get value by key"""
            return self.data.get(key)

        async def delete(self, key: str):
            """Delete a key"""
            if key in self.data:
                del self.data[key]
                if key in self.ttls:
                    del self.ttls[key]
                return True
            return False

        async def exists(self, key: str):
            """Check if key exists"""
            return key in self.data

        async def ttl(self, key: str):
            """Get TTL for a key"""
            return self.ttls.get(key, -1)

        async def setex(self, key: str, seconds: int, value: str):
            """Set key with expiration in seconds"""
            self.data[key] = value
            self.ttls[key] = seconds
            return True

    return MockRedis()
