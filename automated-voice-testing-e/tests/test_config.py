"""
Test suite for application configuration management
Ensures backend/api/config.py exists and provides proper configuration
"""

import os
import sys
import pytest
from unittest.mock import patch

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend'))


class TestConfigFile:
    """Test configuration file exists"""

    @pytest.fixture
    def project_root(self):
        """Get project root directory"""
        return os.path.dirname(os.path.dirname(__file__))

    @pytest.fixture
    def config_py_path(self, project_root):
        """Get path to backend/api/config.py file"""
        return os.path.join(project_root, 'backend', 'api', 'config.py')

    def test_config_py_exists(self, config_py_path):
        """Test that backend/api/config.py file exists"""
        assert os.path.exists(config_py_path), \
            "backend/api/config.py file must exist"

    def test_can_import_settings(self):
        """Test that we can import Settings class"""
        try:
            from api.config import Settings
            assert Settings is not None, "Settings class should be defined"
        except ImportError as e:
            pytest.fail(f"Failed to import Settings from api.config: {e}")


class TestSettingsClass:
    """Test Settings class structure and inheritance"""

    def test_settings_inherits_from_base_settings(self):
        """Test that Settings inherits from Pydantic BaseSettings"""
        from api.config import Settings
        from pydantic_settings import BaseSettings

        assert issubclass(Settings, BaseSettings), \
            "Settings should inherit from pydantic_settings.BaseSettings"

    def test_settings_has_model_config(self):
        """Test that Settings has proper model configuration"""
        from api.config import Settings

        # Check if Settings has model_config for env file loading
        assert hasattr(Settings, 'model_config'), \
            "Settings should have model_config"


class TestDatabaseConfiguration:
    """Test database configuration fields"""

    @pytest.fixture
    def settings_with_env(self):
        """Create settings instance with environment variables"""
        with patch.dict(os.environ, {
            'DATABASE_URL': 'postgresql://user:pass@localhost:5432/testdb',
            'REDIS_URL': 'redis://localhost:6379/0',
            'JWT_SECRET_KEY': 'test-secret-key-1234567890',
            'JWT_ALGORITHM': 'HS256',
            'SOUNDHOUND_API_KEY': 'test-soundhound-key',
            'SOUNDHOUND_CLIENT_ID': 'test-client-id',
            'AWS_ACCESS_KEY_ID': 'test-aws-key',
            'AWS_SECRET_ACCESS_KEY': 'test-aws-secret',
            'AWS_REGION': 'us-east-1',
            'ENVIRONMENT': 'development',
        }):
            from api.config import Settings
            return Settings()

    def test_settings_has_database_url(self, settings_with_env):
        """Test that Settings has DATABASE_URL field"""
        assert hasattr(settings_with_env, 'DATABASE_URL'), \
            "Settings should have DATABASE_URL field"
        assert settings_with_env.DATABASE_URL == 'postgresql://user:pass@localhost:5432/testdb'

    def test_database_url_is_required(self):
        """Test that DATABASE_URL is required"""
        from api.config import Settings
        from pydantic import ValidationError

        # Try to create settings without DATABASE_URL
        with patch.dict(os.environ, {}, clear=True):
            try:
                Settings()
                pytest.fail("Settings should raise ValidationError without DATABASE_URL")
            except ValidationError:
                pass  # Expected

    def test_settings_has_database_fields(self, settings_with_env):
        """Test that Settings has optional database-related fields"""
        # These might be optional if DATABASE_URL is provided
        from api.config import Settings

        # Check that Settings class has these fields defined
        assert 'DB_HOST' in Settings.model_fields or hasattr(Settings, 'DB_HOST'), \
            "Settings should have DB_HOST field"


class TestRedisConfiguration:
    """Test Redis configuration fields"""

    @pytest.fixture
    def settings_with_env(self):
        """Create settings instance with environment variables"""
        with patch.dict(os.environ, {
            'DATABASE_URL': 'postgresql://user:pass@localhost:5432/testdb',
            'REDIS_URL': 'redis://localhost:6379/0',
            'JWT_SECRET_KEY': 'test-secret-key-1234567890',
            'JWT_ALGORITHM': 'HS256',
            'SOUNDHOUND_API_KEY': 'test-soundhound-key',
            'SOUNDHOUND_CLIENT_ID': 'test-client-id',
            'AWS_ACCESS_KEY_ID': 'test-aws-key',
            'AWS_SECRET_ACCESS_KEY': 'test-aws-secret',
            'AWS_REGION': 'us-east-1',
            'ENVIRONMENT': 'development',
        }):
            from api.config import Settings
            return Settings()

    def test_settings_has_redis_url(self, settings_with_env):
        """Test that Settings has REDIS_URL field"""
        assert hasattr(settings_with_env, 'REDIS_URL'), \
            "Settings should have REDIS_URL field"
        assert settings_with_env.REDIS_URL == 'redis://localhost:6379/0'

    def test_redis_url_is_required(self):
        """Test that REDIS_URL is required"""
        from api.config import Settings
        from pydantic import ValidationError

        with patch.dict(os.environ, {
            'DATABASE_URL': 'postgresql://user:pass@localhost:5432/testdb',
        }, clear=True):
            try:
                Settings()
                pytest.fail("Settings should raise ValidationError without REDIS_URL")
            except ValidationError:
                pass  # Expected


class TestJWTConfiguration:
    """Test JWT/Authentication configuration fields"""

    @pytest.fixture
    def settings_with_env(self):
        """Create settings instance with environment variables"""
        with patch.dict(os.environ, {
            'DATABASE_URL': 'postgresql://user:pass@localhost:5432/testdb',
            'REDIS_URL': 'redis://localhost:6379/0',
            'JWT_SECRET_KEY': 'test-secret-key-123456789',
            'JWT_ALGORITHM': 'HS256',
            'SOUNDHOUND_API_KEY': 'test-soundhound-key',
            'SOUNDHOUND_CLIENT_ID': 'test-client-id',
            'AWS_ACCESS_KEY_ID': 'test-aws-key',
            'AWS_SECRET_ACCESS_KEY': 'test-aws-secret',
            'AWS_REGION': 'us-east-1',
            'ENVIRONMENT': 'development',
        }):
            from api.config import Settings
            return Settings()

    def test_settings_has_jwt_secret_key(self, settings_with_env):
        """Test that Settings has JWT_SECRET_KEY field"""
        assert hasattr(settings_with_env, 'JWT_SECRET_KEY'), \
            "Settings should have JWT_SECRET_KEY field"
        assert settings_with_env.JWT_SECRET_KEY == 'test-secret-key-123456789'

    def test_jwt_secret_key_is_required(self):
        """Test that JWT_SECRET_KEY is required"""
        from api.config import Settings
        from pydantic import ValidationError

        with patch.dict(os.environ, {
            'DATABASE_URL': 'postgresql://user:pass@localhost:5432/testdb',
            'REDIS_URL': 'redis://localhost:6379/0',
        }, clear=True):
            try:
                Settings()
                pytest.fail("Settings should raise ValidationError without JWT_SECRET_KEY")
            except ValidationError:
                pass  # Expected


class TestTenancyConfiguration:
    """Tenant mode configuration tests."""

    def _env(self):
        return {
            'DATABASE_URL': 'postgresql://user:pass@localhost:5432/testdb',
            'REDIS_URL': 'redis://localhost:6379/0',
            'JWT_SECRET_KEY': 'test-secret-key-1234567890',
            'SOUNDHOUND_API_KEY': 'test-soundhound-key',
            'SOUNDHOUND_CLIENT_ID': 'test-client-id',
            'AWS_ACCESS_KEY_ID': 'test-aws-key',
            'AWS_SECRET_ACCESS_KEY': 'test-aws-secret',
        }

    @pytest.fixture
    def settings_with_env(self):
        """Create settings with environment variables for testing"""
        from api.config import Settings

        with patch.dict(os.environ, self._env(), clear=True):
            yield Settings()

    def test_default_tenancy_mode_is_soft(self):
        env = self._env()
        with patch.dict(os.environ, env, clear=True):
            from api.config import Settings
            settings = Settings()
            assert settings.TENANCY_MODE == "soft_multi_tenant"

    def test_invalid_tenancy_mode_rejected(self):
        env = self._env()
        env['TENANCY_MODE'] = 'unsupported'
        with patch.dict(os.environ, env, clear=True):
            from api.config import Settings
            from pydantic import ValidationError
            with pytest.raises(ValidationError):
                Settings()

    def test_settings_has_jwt_algorithm(self, settings_with_env):
        """Test that Settings has JWT_ALGORITHM field"""
        assert hasattr(settings_with_env, 'JWT_ALGORITHM'), \
            "Settings should have JWT_ALGORITHM field"
        assert settings_with_env.JWT_ALGORITHM == 'HS256'

    def test_production_env_rejects_placeholder_jwt_secret(self):
        """Non-development environments must not use placeholder JWT secrets."""
        from api.config import Settings
        from pydantic import ValidationError

        insecure_secret = 'change-me-default-secret-123456'
        env_vars = {
            'DATABASE_URL': 'postgresql://user:pass@localhost:5432/testdb',
            'REDIS_URL': 'redis://localhost:6379/0',
            'JWT_SECRET_KEY': insecure_secret,
            'JWT_ALGORITHM': 'HS256',
            'SOUNDHOUND_API_KEY': 'test-soundhound-key',
            'SOUNDHOUND_CLIENT_ID': 'test-client-id',
            'AWS_ACCESS_KEY_ID': 'test-aws-key',
            'AWS_SECRET_ACCESS_KEY': 'test-aws-secret',
            'AWS_REGION': 'us-east-1',
            'ENVIRONMENT': 'production',
        }

        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValidationError):
                Settings()

    def test_jwt_algorithm_has_default(self):
        """Test that JWT_ALGORITHM has a default value"""
        from api.config import Settings

        with patch.dict(os.environ, {
            'DATABASE_URL': 'postgresql://user:pass@localhost:5432/testdb',
            'REDIS_URL': 'redis://localhost:6379/0',
            'JWT_SECRET_KEY': 'test-secret-key-1234567890',
            'SOUNDHOUND_API_KEY': 'test-soundhound-key',
            'SOUNDHOUND_CLIENT_ID': 'test-client-id',
            'AWS_ACCESS_KEY_ID': 'test-aws-key',
            'AWS_SECRET_ACCESS_KEY': 'test-aws-secret',
            'ENVIRONMENT': 'development',
        }, clear=True):
            settings = Settings()
            # Should have a default algorithm
            assert settings.JWT_ALGORITHM is not None


class TestSoundHoundConfiguration:
    """Test SoundHound API configuration fields"""

    @pytest.fixture
    def settings_with_env(self):
        """Create settings instance with environment variables"""
        with patch.dict(os.environ, {
            'DATABASE_URL': 'postgresql://user:pass@localhost:5432/testdb',
            'REDIS_URL': 'redis://localhost:6379/0',
            'JWT_SECRET_KEY': 'test-secret-key-1234567890',
            'JWT_ALGORITHM': 'HS256',
            'SOUNDHOUND_API_KEY': 'test-soundhound-key',
            'SOUNDHOUND_CLIENT_ID': 'test-soundhound-client-id',
            'AWS_ACCESS_KEY_ID': 'test-aws-key',
            'AWS_SECRET_ACCESS_KEY': 'test-aws-secret',
            'AWS_REGION': 'us-east-1',
            'ENVIRONMENT': 'development',
        }):
            from api.config import Settings
            return Settings()

    def test_settings_has_soundhound_api_key(self, settings_with_env):
        """Test that Settings has SOUNDHOUND_API_KEY field"""
        assert hasattr(settings_with_env, 'SOUNDHOUND_API_KEY'), \
            "Settings should have SOUNDHOUND_API_KEY field"
        assert settings_with_env.SOUNDHOUND_API_KEY == 'test-soundhound-key'

    def test_settings_has_soundhound_client_id(self, settings_with_env):
        """Test that Settings has SOUNDHOUND_CLIENT_ID field"""
        assert hasattr(settings_with_env, 'SOUNDHOUND_CLIENT_ID'), \
            "Settings should have SOUNDHOUND_CLIENT_ID field"
        assert settings_with_env.SOUNDHOUND_CLIENT_ID == 'test-soundhound-client-id'

    def test_soundhound_api_key_is_required(self):
        """Test that SOUNDHOUND_API_KEY is required"""
        from api.config import Settings
        from pydantic import ValidationError

        with patch.dict(os.environ, {
            'DATABASE_URL': 'postgresql://user:pass@localhost:5432/testdb',
            'REDIS_URL': 'redis://localhost:6379/0',
            'JWT_SECRET_KEY': 'test-secret-key-1234567890',
        }, clear=True):
            try:
                Settings()
                pytest.fail("Settings should raise ValidationError without SOUNDHOUND_API_KEY")
            except ValidationError:
                pass  # Expected


class TestAWSConfiguration:
    """Test AWS configuration fields"""

    @pytest.fixture
    def settings_with_env(self):
        """Create settings instance with environment variables"""
        with patch.dict(os.environ, {
            'DATABASE_URL': 'postgresql://user:pass@localhost:5432/testdb',
            'REDIS_URL': 'redis://localhost:6379/0',
            'JWT_SECRET_KEY': 'test-secret-key-1234567890',
            'JWT_ALGORITHM': 'HS256',
            'SOUNDHOUND_API_KEY': 'test-soundhound-key',
            'SOUNDHOUND_CLIENT_ID': 'test-client-id',
            'AWS_ACCESS_KEY_ID': 'test-aws-access-key',
            'AWS_SECRET_ACCESS_KEY': 'test-aws-secret-key',
            'AWS_REGION': 'us-west-2',
            'ENVIRONMENT': 'development',
        }):
            from api.config import Settings
            return Settings()

    def test_settings_has_aws_access_key_id(self, settings_with_env):
        """Test that Settings has AWS_ACCESS_KEY_ID field"""
        assert hasattr(settings_with_env, 'AWS_ACCESS_KEY_ID'), \
            "Settings should have AWS_ACCESS_KEY_ID field"
        assert settings_with_env.AWS_ACCESS_KEY_ID == 'test-aws-access-key'

    def test_settings_has_aws_secret_access_key(self, settings_with_env):
        """Test that Settings has AWS_SECRET_ACCESS_KEY field"""
        assert hasattr(settings_with_env, 'AWS_SECRET_ACCESS_KEY'), \
            "Settings should have AWS_SECRET_ACCESS_KEY field"
        assert settings_with_env.AWS_SECRET_ACCESS_KEY == 'test-aws-secret-key'

    def test_settings_has_aws_region(self, settings_with_env):
        """Test that Settings has AWS_REGION field"""
        assert hasattr(settings_with_env, 'AWS_REGION'), \
            "Settings should have AWS_REGION field"
        assert settings_with_env.AWS_REGION == 'us-west-2'


class TestApplicationConfiguration:
    """Test general application configuration fields"""

    @pytest.fixture
    def settings_with_env(self):
        """Create settings instance with environment variables"""
        with patch.dict(os.environ, {
            'DATABASE_URL': 'postgresql://user:pass@localhost:5432/testdb',
            'REDIS_URL': 'redis://localhost:6379/0',
            'JWT_SECRET_KEY': 'super-secure-production-jwt-key-abcd1234',
            'JWT_ALGORITHM': 'HS256',
            'SOUNDHOUND_API_KEY': 'prod-soundhound-key',
            'SOUNDHOUND_CLIENT_ID': 'prod-client-id',
            'AWS_ACCESS_KEY_ID': 'prod-aws-key',
            'AWS_SECRET_ACCESS_KEY': 'prod-aws-secret',
            'AWS_REGION': 'us-east-1',
            'ENVIRONMENT': 'production',
            'LOG_LEVEL': 'INFO',
            'DEBUG': 'false',
        }, clear=True):
            from api.config import Settings
            yield Settings()

    def test_settings_has_environment_field(self, settings_with_env):
        """Test that Settings has ENVIRONMENT field"""
        assert hasattr(settings_with_env, 'ENVIRONMENT'), \
            "Settings should have ENVIRONMENT field"
        assert settings_with_env.ENVIRONMENT == 'production'

    def test_environment_has_default(self):
        """Test that ENVIRONMENT has a default value"""
        from api.config import Settings

        with patch.dict(os.environ, {
            'DATABASE_URL': 'postgresql://user:pass@localhost:5432/testdb',
            'REDIS_URL': 'redis://localhost:6379/0',
            'JWT_SECRET_KEY': 'test-secret-key-1234567890',
            'SOUNDHOUND_API_KEY': 'test-soundhound-key',
            'SOUNDHOUND_CLIENT_ID': 'test-client-id',
            'AWS_ACCESS_KEY_ID': 'test-aws-key',
            'AWS_SECRET_ACCESS_KEY': 'test-aws-secret',
        }, clear=True):
            settings = Settings()
            # Should have a default environment
            assert settings.ENVIRONMENT in ['development', 'staging', 'production']

    def test_settings_has_log_level_field(self, settings_with_env):
        """Test that Settings has LOG_LEVEL field"""
        assert hasattr(settings_with_env, 'LOG_LEVEL'), \
            "Settings should have LOG_LEVEL field"


class TestGetSettingsFunction:
    """Test get_settings singleton function"""

    def test_get_settings_function_exists(self):
        """Test that get_settings function exists"""
        try:
            from api.config import get_settings
            assert get_settings is not None, "get_settings function should be defined"
        except ImportError as e:
            pytest.fail(f"Failed to import get_settings from api.config: {e}")

    def test_get_settings_returns_settings_instance(self):
        """Test that get_settings returns Settings instance"""
        with patch.dict(os.environ, {
            'DATABASE_URL': 'postgresql://user:pass@localhost:5432/testdb',
            'REDIS_URL': 'redis://localhost:6379/0',
            'JWT_SECRET_KEY': 'test-secret-key-1234567890',
            'SOUNDHOUND_API_KEY': 'test-soundhound-key',
            'SOUNDHOUND_CLIENT_ID': 'test-client-id',
            'AWS_ACCESS_KEY_ID': 'test-aws-key',
            'AWS_SECRET_ACCESS_KEY': 'test-aws-secret',
            'ENVIRONMENT': 'development',
        }):
            from api.config import get_settings, Settings

            settings = get_settings()
            assert isinstance(settings, Settings), \
                "get_settings should return Settings instance"

    def test_get_settings_returns_same_instance(self):
        """Test that get_settings returns the same instance (singleton)"""
        with patch.dict(os.environ, {
            'DATABASE_URL': 'postgresql://user:pass@localhost:5432/testdb',
            'REDIS_URL': 'redis://localhost:6379/0',
            'JWT_SECRET_KEY': 'test-secret-key-1234567890',
            'SOUNDHOUND_API_KEY': 'test-soundhound-key',
            'SOUNDHOUND_CLIENT_ID': 'test-client-id',
            'AWS_ACCESS_KEY_ID': 'test-aws-key',
            'AWS_SECRET_ACCESS_KEY': 'test-aws-secret',
            'ENVIRONMENT': 'development',
        }):
            from api.config import get_settings

            settings1 = get_settings()
            settings2 = get_settings()

            assert settings1 is settings2, \
                "get_settings should return the same instance (singleton pattern)"
