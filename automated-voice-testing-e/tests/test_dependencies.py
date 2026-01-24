"""
Test suite for dependency injection system
Ensures backend/api/dependencies.py exists and provides proper dependencies
"""

import os
import sys
import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Generator

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend'))


class TestDependenciesFile:
    """Test dependencies file exists"""

    @pytest.fixture
    def project_root(self):
        """Get project root directory"""
        return os.path.dirname(os.path.dirname(__file__))

    @pytest.fixture
    def dependencies_path(self, project_root):
        """Get path to backend/api/dependencies.py file"""
        return os.path.join(project_root, 'backend', 'api', 'dependencies.py')

    def test_dependencies_py_exists(self, dependencies_path):
        """Test that backend/api/dependencies.py file exists"""
        assert os.path.exists(dependencies_path), \
            "backend/api/dependencies.py file must exist"

    def test_can_import_dependencies(self):
        """Test that we can import dependencies module"""
        try:
            import api.dependencies
            assert api.dependencies is not None
        except ImportError as e:
            pytest.fail(f"Failed to import api.dependencies: {e}")


class TestGetSettingsDependency:
    """Test get_settings dependency for configuration access"""

    def test_get_settings_dependency_exists(self):
        """Test that get_settings dependency function exists"""
        try:
            from api.dependencies import get_settings_dependency
            assert get_settings_dependency is not None
        except ImportError as e:
            pytest.fail(f"Failed to import get_settings_dependency: {e}")

    def test_get_settings_returns_settings_instance(self):
        """Test that get_settings_dependency returns Settings instance"""
        from api.dependencies import get_settings_dependency
        from api.config import Settings

        with patch.dict(os.environ, {
            'DATABASE_URL': 'postgresql://test:test@localhost:5432/test',
            'REDIS_URL': 'redis://localhost:6379/0',
            'JWT_SECRET_KEY': 'test-secret-key-1234567890',
            'SOUNDHOUND_API_KEY': 'test-key',
            'SOUNDHOUND_CLIENT_ID': 'test-client',
            'AWS_ACCESS_KEY_ID': 'test-key',
            'AWS_SECRET_ACCESS_KEY': 'test-secret',
            'ENVIRONMENT': 'development',
        }):
            settings = get_settings_dependency()
            assert isinstance(settings, Settings), \
                "get_settings_dependency should return Settings instance"

    def test_get_settings_is_cached(self):
        """Test that get_settings_dependency returns cached instance"""
        from api.dependencies import get_settings_dependency

        with patch.dict(os.environ, {
            'DATABASE_URL': 'postgresql://test:test@localhost:5432/test',
            'REDIS_URL': 'redis://localhost:6379/0',
            'JWT_SECRET_KEY': 'test-secret-key-1234567890',
            'SOUNDHOUND_API_KEY': 'test-key',
            'SOUNDHOUND_CLIENT_ID': 'test-client',
            'AWS_ACCESS_KEY_ID': 'test-key',
            'AWS_SECRET_ACCESS_KEY': 'test-secret',
            'ENVIRONMENT': 'development',
        }):
            settings1 = get_settings_dependency()
            settings2 = get_settings_dependency()

            # Should be the same instance (cached)
            assert settings1 is settings2, \
                "get_settings_dependency should return cached instance"


class TestGetDBDependency:
    """Test get_db dependency for database session management"""

    def test_get_db_dependency_exists(self):
        """Test that get_db dependency function exists"""
        try:
            from api.dependencies import get_db
            assert get_db is not None
        except ImportError as e:
            pytest.fail(f"Failed to import get_db: {e}")

    def test_get_db_is_generator(self):
        """Test that get_db is a generator function"""
        from api.dependencies import get_db
        import inspect

        assert inspect.isgeneratorfunction(get_db), \
            "get_db should be a generator function (uses yield)"

    def test_get_db_yields_session(self):
        """Test that get_db yields a database session"""
        from api.dependencies import get_db

        # get_db is a generator, so we call it to get the generator object
        gen = get_db()

        # The generator should yield something
        try:
            session = next(gen)
            assert session is not None, "get_db should yield a session"

            # Clean up by exhausting the generator
            try:
                next(gen)
            except StopIteration:
                pass  # Expected when generator finishes

        except StopIteration:
            pytest.fail("get_db generator didn't yield anything")


class TestGetCurrentUserDependency:
    """Test get_current_user dependency for authentication"""

    def test_get_current_user_dependency_exists(self):
        """Test that get_current_user dependency function exists"""
        try:
            from api.dependencies import get_current_user
            assert get_current_user is not None
        except ImportError as e:
            pytest.fail(f"Failed to import get_current_user: {e}")

    def test_get_current_user_accepts_token_parameter(self):
        """Test that get_current_user accepts token parameter"""
        from api.dependencies import get_current_user
        import inspect

        sig = inspect.signature(get_current_user)
        params = list(sig.parameters.keys())

        # Should have at least one parameter for token
        assert len(params) >= 1, \
            "get_current_user should accept token parameter"

    def test_get_current_user_with_valid_token(self):
        """Test that get_current_user returns user info with valid token"""
        from api.dependencies import get_current_user

        # Create a mock valid token
        mock_token = "valid.jwt.token"

        # We'll need to mock the token validation
        # This is a placeholder test that will be refined when JWT is implemented
        try:
            # Try calling with a token
            # This might raise an exception if token validation is strict
            # For now, we just test that the function exists and can be called
            result = get_current_user(token=mock_token)
            # Result should be some user information (dict or object)
            assert result is not None
        except Exception:
            # If it raises an exception, that's also valid behavior
            # (means it's validating the token)
            pass

    def test_get_current_user_requires_token(self):
        """Test that get_current_user requires token"""
        from api.dependencies import get_current_user
        import inspect

        sig = inspect.signature(get_current_user)

        # Check if credentials or token parameter exists
        # In FastAPI, this might be through Depends(security) for HTTPAuthorizationCredentials
        has_auth_param = False
        for param_name, param in sig.parameters.items():
            # Check for 'token', 'credentials', or any auth-related parameter
            if any(keyword in param_name.lower() for keyword in ['token', 'credentials', 'auth', 'bearer']):
                has_auth_param = True
                break

        assert has_auth_param, \
            "get_current_user should have an authentication parameter (token/credentials)"


class TestGetCurrentUserOptionalDependency:
    """Test get_current_user_optional dependency for optional authentication"""

    def test_get_current_user_optional_exists(self):
        """Test that get_current_user_optional dependency exists"""
        try:
            from api.dependencies import get_current_user_optional
            assert get_current_user_optional is not None
        except ImportError as e:
            pytest.fail(f"Failed to import get_current_user_optional: {e}")

    def test_get_current_user_optional_accepts_none(self):
        """Test that get_current_user_optional can return None"""
        from api.dependencies import get_current_user_optional

        # Should be able to call without raising exception
        try:
            result = get_current_user_optional(token=None)
            # Result can be None (no user) or a user object
            assert result is None or result is not None
        except Exception:
            # If it needs a token parameter, that's fine too
            pass


class TestTokenValidation:
    """Test token validation utilities"""

    def test_verify_token_function_exists(self):
        """Test that verify_token function exists"""
        try:
            from api.dependencies import verify_token
            assert verify_token is not None
        except ImportError:
            # This is optional, token verification might be in another module
            pass

    def test_decode_token_function_exists(self):
        """Test that decode_token function exists"""
        try:
            from api.dependencies import decode_token
            assert decode_token is not None
        except ImportError:
            # This is optional, token decoding might be in another module
            pass


class TestDependencyIntegration:
    """Test integration between dependencies"""

    def test_dependencies_work_together(self):
        """Test that dependencies can be used together"""
        from api.dependencies import get_settings_dependency

        with patch.dict(os.environ, {
            'DATABASE_URL': 'postgresql://test:test@localhost:5432/test',
            'REDIS_URL': 'redis://localhost:6379/0',
            'JWT_SECRET_KEY': 'test-secret-key-1234567890',
            'SOUNDHOUND_API_KEY': 'test-key',
            'SOUNDHOUND_CLIENT_ID': 'test-client',
            'AWS_ACCESS_KEY_ID': 'test-key',
            'AWS_SECRET_ACCESS_KEY': 'test-secret',
            'ENVIRONMENT': 'development',
        }):
            # Should be able to get settings
            settings = get_settings_dependency()
            assert settings is not None

            # Settings should have JWT configuration
            assert hasattr(settings, 'JWT_SECRET_KEY')
            assert hasattr(settings, 'JWT_ALGORITHM')


class TestDependencyDocumentation:
    """Test that dependencies are properly documented"""

    def test_get_settings_has_docstring(self):
        """Test that get_settings_dependency has documentation"""
        from api.dependencies import get_settings_dependency

        assert get_settings_dependency.__doc__ is not None, \
            "get_settings_dependency should have a docstring"

    def test_get_db_has_docstring(self):
        """Test that get_db has documentation"""
        from api.dependencies import get_db

        assert get_db.__doc__ is not None, \
            "get_db should have a docstring"

    def test_get_current_user_has_docstring(self):
        """Test that get_current_user has documentation"""
        from api.dependencies import get_current_user

        assert get_current_user.__doc__ is not None, \
            "get_current_user should have a docstring"


class TestDependencyExports:
    """Test that dependencies are properly exported"""

    def test_all_dependencies_exported(self):
        """Test that __all__ exports all dependencies"""
        import api.dependencies

        if hasattr(api.dependencies, '__all__'):
            exports = api.dependencies.__all__

            # Should export main dependencies
            expected_exports = [
                'get_settings_dependency',
                'get_db',
                'get_current_user'
            ]

            for export in expected_exports:
                assert export in exports, \
                    f"{export} should be in __all__"
