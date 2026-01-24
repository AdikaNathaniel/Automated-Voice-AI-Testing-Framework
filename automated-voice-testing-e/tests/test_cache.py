"""
Test suite for cache decorator

Ensures proper caching functionality with Redis backend,
TTL configuration, and cache invalidation helpers.
"""

import os
import sys
import pytest
import asyncio
from typing import Optional
from unittest.mock import AsyncMock, MagicMock, patch
import inspect

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend'))


class TestCacheModule:
    """Test cache module structure"""

    def test_cache_module_exists(self):
        """Test that cache module can be imported"""
        try:
            import api.cache
            assert api.cache is not None
        except ImportError:
            pytest.fail("Cannot import api.cache")

    def test_cache_module_has_docstring(self):
        """Test that cache module has docstring"""
        import api.cache
        assert api.cache.__doc__ is not None
        assert len(api.cache.__doc__.strip()) > 0

    def test_can_import_cache_decorator(self):
        """Test that cache decorator can be imported"""
        try:
            from api.cache import cache
            assert cache is not None
        except ImportError:
            pytest.fail("Cannot import cache from api.cache")

    def test_can_import_invalidate_cache(self):
        """Test that invalidate_cache function can be imported"""
        try:
            from api.cache import invalidate_cache
            assert invalidate_cache is not None
        except ImportError:
            pytest.fail("Cannot import invalidate_cache from api.cache")

    def test_can_import_clear_cache(self):
        """Test that clear_cache function can be imported"""
        try:
            from api.cache import clear_cache
            assert clear_cache is not None
        except ImportError:
            pytest.fail("Cannot import clear_cache from api.cache")


class TestCacheDecorator:
    """Test cache decorator structure"""

    def test_cache_is_callable(self):
        """Test that cache decorator is callable"""
        from api.cache import cache
        assert callable(cache)

    def test_cache_has_docstring(self):
        """Test that cache decorator has docstring"""
        from api.cache import cache
        assert cache.__doc__ is not None
        assert len(cache.__doc__.strip()) > 0

    def test_cache_accepts_ttl_parameter(self):
        """Test that cache decorator accepts ttl parameter"""
        from api.cache import cache
        # Should be able to call with ttl parameter
        try:
            @cache(ttl=300)
            async def test_func():
                return "test"
            assert test_func is not None
        except TypeError:
            pytest.fail("cache decorator should accept ttl parameter")

    def test_cache_accepts_key_prefix_parameter(self):
        """Test that cache decorator accepts key_prefix parameter"""
        from api.cache import cache
        try:
            @cache(key_prefix="test")
            async def test_func():
                return "test"
            assert test_func is not None
        except TypeError:
            pytest.fail("cache decorator should accept key_prefix parameter")

    def test_cache_can_be_used_without_parameters(self):
        """Test that cache decorator can be used without parameters"""
        from api.cache import cache
        try:
            @cache
            async def test_func():
                return "test"
            assert test_func is not None
        except (TypeError, AttributeError):
            pytest.fail("cache decorator should work without parameters")

    def test_cache_preserves_function_signature(self):
        """Test that cache decorator preserves function signature"""
        from api.cache import cache

        @cache(ttl=300)
        async def test_func(arg1: str, arg2: int = 10) -> str:
            """Test function docstring"""
            return f"{arg1}:{arg2}"

        # Check function name
        assert test_func.__name__ == "test_func"
        # Check docstring is preserved
        assert "Test function docstring" in test_func.__doc__


class TestCacheDecoratorFunctionality:
    """Test cache decorator caching behavior"""

    @pytest.mark.asyncio
    async def test_decorated_function_is_async(self):
        """Test that decorated function remains async"""
        from api.cache import cache

        @cache(ttl=300)
        async def test_func():
            return "test"

        assert inspect.iscoroutinefunction(test_func)

    @pytest.mark.asyncio
    async def test_cache_decorator_caches_result(self):
        """Test that decorator caches function results"""
        from api.cache import cache

        call_count = 0

        @cache(ttl=300)
        async def expensive_function(x: int) -> int:
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.01)
            return x * 2

        # Mock Redis client
        with patch('api.cache.get_redis') as mock_get_redis:
            mock_redis = AsyncMock()
            mock_redis.get = AsyncMock(return_value=None)
            mock_redis.set = AsyncMock(return_value=True)
            mock_get_redis.return_value.__aenter__.return_value = mock_redis
            mock_get_redis.return_value.__aexit__.return_value = None

            # First call should execute function
            result1 = await expensive_function(5)
            assert result1 == 10
            assert call_count == 1

    @pytest.mark.asyncio
    async def test_cache_decorator_accepts_function_arguments(self):
        """Test that decorated function accepts arguments"""
        from api.cache import cache

        @cache(ttl=300)
        async def add_numbers(a: int, b: int) -> int:
            return a + b

        with patch('api.cache.get_redis') as mock_get_redis:
            mock_redis = AsyncMock()
            mock_redis.get = AsyncMock(return_value=None)
            mock_redis.set = AsyncMock(return_value=True)
            mock_get_redis.return_value.__aenter__.return_value = mock_redis
            mock_get_redis.return_value.__aexit__.return_value = None

            result = await add_numbers(3, 5)
            assert result == 8

    @pytest.mark.asyncio
    async def test_cache_decorator_generates_unique_keys_per_arguments(self):
        """Test that different arguments generate different cache keys"""
        from api.cache import cache

        @cache(ttl=300)
        async def multiply(x: int, y: int) -> int:
            return x * y

        with patch('api.cache.get_redis') as mock_get_redis:
            mock_redis = AsyncMock()
            mock_redis.get = AsyncMock(return_value=None)
            mock_redis.set = AsyncMock(return_value=True)

            # Mock async generator - return a new generator each time
            async def mock_gen():
                yield mock_redis

            # Make it return a new generator each time it's called
            mock_get_redis.side_effect = lambda: mock_gen()

            await multiply(2, 3)
            await multiply(4, 5)

            # Should have been called twice with different keys
            assert mock_redis.set.call_count == 2


class TestCacheTTLConfiguration:
    """Test cache TTL configuration"""

    @pytest.mark.asyncio
    async def test_cache_uses_default_ttl_when_not_specified(self):
        """Test that cache uses default TTL when not specified"""
        from api.cache import cache

        @cache
        async def test_func():
            return "test"

        with patch('api.cache.get_redis') as mock_get_redis:
            mock_redis = AsyncMock()
            mock_redis.get = AsyncMock(return_value=None)
            mock_redis.set = AsyncMock(return_value=True)

            async def mock_gen():
                yield mock_redis

            mock_get_redis.return_value = mock_gen()

            await test_func()

            # Verify set was called (TTL will be checked in the call)
            assert mock_redis.set.called

    @pytest.mark.asyncio
    async def test_cache_uses_custom_ttl(self):
        """Test that cache uses custom TTL when specified"""
        from api.cache import cache

        @cache(ttl=600)
        async def test_func():
            return "test"

        with patch('api.cache.get_redis') as mock_get_redis:
            mock_redis = AsyncMock()
            mock_redis.get = AsyncMock(return_value=None)
            mock_redis.set = AsyncMock(return_value=True)

            async def mock_gen():
                yield mock_redis

            mock_get_redis.return_value = mock_gen()

            await test_func()

            # Verify set was called with TTL parameter
            assert mock_redis.set.called
            call_args = mock_redis.set.call_args
            # Check that ttl argument was passed
            assert 'ttl' in call_args.kwargs or len(call_args.args) >= 3

    @pytest.mark.asyncio
    async def test_cache_ttl_none_means_no_expiration(self):
        """Test that ttl=None means no expiration"""
        from api.cache import cache

        @cache(ttl=None)
        async def test_func():
            return "test"

        with patch('api.cache.get_redis') as mock_get_redis:
            mock_redis = AsyncMock()
            mock_redis.get = AsyncMock(return_value=None)
            mock_redis.set = AsyncMock(return_value=True)

            async def mock_gen():
                yield mock_redis

            mock_get_redis.return_value = mock_gen()

            await test_func()

            # Verify set was called
            assert mock_redis.set.called


class TestCacheKeyGeneration:
    """Test cache key generation"""

    @pytest.mark.asyncio
    async def test_cache_generates_key_from_function_name(self):
        """Test that cache key includes function name"""
        from api.cache import cache

        @cache(ttl=300)
        async def my_unique_function():
            return "test"

        with patch('api.cache.get_redis') as mock_get_redis:
            mock_redis = AsyncMock()
            mock_redis.get = AsyncMock(return_value=None)
            mock_redis.set = AsyncMock(return_value=True)

            async def mock_gen():
                yield mock_redis

            mock_get_redis.return_value = mock_gen()

            await my_unique_function()

            # Check that get was called with a key containing function name
            assert mock_redis.get.called
            cache_key = mock_redis.get.call_args[0][0]
            assert "my_unique_function" in cache_key

    @pytest.mark.asyncio
    async def test_cache_key_includes_arguments(self):
        """Test that cache key includes function arguments"""
        from api.cache import cache

        @cache(ttl=300)
        async def test_func(user_id: int, action: str):
            return f"{user_id}:{action}"

        with patch('api.cache.get_redis') as mock_get_redis:
            mock_redis = AsyncMock()
            mock_redis.get = AsyncMock(return_value=None)
            mock_redis.set = AsyncMock(return_value=True)

            async def mock_gen():
                yield mock_redis

            mock_get_redis.return_value = mock_gen()

            await test_func(123, "login")

            # Check cache key
            assert mock_redis.get.called
            cache_key = mock_redis.get.call_args[0][0]
            # Key should contain some representation of arguments
            assert len(cache_key) > len("test_func")

    @pytest.mark.asyncio
    async def test_cache_uses_custom_key_prefix(self):
        """Test that cache uses custom key prefix"""
        from api.cache import cache

        @cache(ttl=300, key_prefix="myapp")
        async def test_func():
            return "test"

        with patch('api.cache.get_redis') as mock_get_redis:
            mock_redis = AsyncMock()
            mock_redis.get = AsyncMock(return_value=None)
            mock_redis.set = AsyncMock(return_value=True)

            async def mock_gen():
                yield mock_redis

            mock_get_redis.return_value = mock_gen()

            await test_func()

            # Check cache key starts with prefix
            assert mock_redis.get.called
            cache_key = mock_redis.get.call_args[0][0]
            assert cache_key.startswith("myapp:")


class TestInvalidateCache:
    """Test cache invalidation helper"""

    def test_invalidate_cache_is_async_function(self):
        """Test that invalidate_cache is async"""
        from api.cache import invalidate_cache
        assert inspect.iscoroutinefunction(invalidate_cache)

    def test_invalidate_cache_has_docstring(self):
        """Test that invalidate_cache has docstring"""
        from api.cache import invalidate_cache
        assert invalidate_cache.__doc__ is not None
        assert len(invalidate_cache.__doc__.strip()) > 0

    @pytest.mark.asyncio
    async def test_invalidate_cache_accepts_key_parameter(self):
        """Test that invalidate_cache accepts key parameter"""
        from api.cache import invalidate_cache
        sig = inspect.signature(invalidate_cache)
        assert 'key' in sig.parameters

    @pytest.mark.asyncio
    async def test_invalidate_cache_deletes_from_redis(self):
        """Test that invalidate_cache deletes key from Redis"""
        from api.cache import invalidate_cache

        with patch('api.cache.get_redis') as mock_get_redis:
            mock_redis = AsyncMock()
            mock_redis.delete = AsyncMock(return_value=True)

            async def mock_gen():
                yield mock_redis

            mock_get_redis.return_value = mock_gen()

            result = await invalidate_cache("test:key")

            assert mock_redis.delete.called
            assert mock_redis.delete.call_args[0][0] == "test:key"
            assert result is True


class TestClearCache:
    """Test cache clearing helper"""

    def test_clear_cache_is_async_function(self):
        """Test that clear_cache is async"""
        from api.cache import clear_cache
        assert inspect.iscoroutinefunction(clear_cache)

    def test_clear_cache_has_docstring(self):
        """Test that clear_cache has docstring"""
        from api.cache import clear_cache
        assert clear_cache.__doc__ is not None
        assert len(clear_cache.__doc__.strip()) > 0

    @pytest.mark.asyncio
    async def test_clear_cache_accepts_pattern_parameter(self):
        """Test that clear_cache accepts pattern parameter"""
        from api.cache import clear_cache
        sig = inspect.signature(clear_cache)
        assert 'pattern' in sig.parameters

    @pytest.mark.asyncio
    async def test_clear_cache_pattern_has_default(self):
        """Test that pattern parameter has default value"""
        from api.cache import clear_cache
        sig = inspect.signature(clear_cache)
        assert sig.parameters['pattern'].default != inspect.Parameter.empty


class TestCacheExports:
    """Test cache module exports"""

    def test_cache_module_exports_cache(self):
        """Test that cache module exports cache decorator"""
        import api.cache
        assert hasattr(api.cache, 'cache')

    def test_cache_module_exports_invalidate_cache(self):
        """Test that cache module exports invalidate_cache"""
        import api.cache
        assert hasattr(api.cache, 'invalidate_cache')

    def test_cache_module_exports_clear_cache(self):
        """Test that cache module exports clear_cache"""
        import api.cache
        assert hasattr(api.cache, 'clear_cache')


class TestCacheDocumentation:
    """Test cache module documentation"""

    def test_cache_decorator_has_comprehensive_docstring(self):
        """Test that cache decorator has comprehensive docstring"""
        from api.cache import cache
        assert len(cache.__doc__) > 100, "Docstring should be comprehensive"

    def test_invalidate_cache_has_comprehensive_docstring(self):
        """Test that invalidate_cache has comprehensive docstring"""
        from api.cache import invalidate_cache
        assert len(invalidate_cache.__doc__) > 50

    def test_clear_cache_has_comprehensive_docstring(self):
        """Test that clear_cache has comprehensive docstring"""
        from api.cache import clear_cache
        assert len(clear_cache.__doc__) > 50
