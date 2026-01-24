"""
Tests for Sentry error tracking integration.

These tests verify that:
1. Sentry SDK is properly initialized in startup_event()
2. Error sampling rate is configurable
3. User context is added to errors
4. Sentry is only enabled in production with valid DSN
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock, AsyncMock

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestSentryConfiguration:
    """Test Sentry configuration settings"""

    def test_sentry_dsn_setting_exists(self):
        """Test that SENTRY_DSN setting is available"""
        from api.config import Settings

        # Should be able to access SENTRY_DSN field
        assert hasattr(Settings, 'model_fields')
        fields = Settings.model_fields
        assert 'SENTRY_DSN' in fields

    def test_sentry_sample_rate_setting_exists(self):
        """Test that SENTRY_SAMPLE_RATE setting is available"""
        from api.config import Settings

        fields = Settings.model_fields
        assert 'SENTRY_SAMPLE_RATE' in fields

    def test_sentry_dsn_optional(self):
        """Test that SENTRY_DSN is optional (can be None)"""
        from api.config import Settings

        fields = Settings.model_fields
        # SENTRY_DSN should have a default value (None or empty)
        assert fields['SENTRY_DSN'].default is None or fields['SENTRY_DSN'].default == ""

    def test_sentry_sample_rate_default(self):
        """Test that SENTRY_SAMPLE_RATE has reasonable default"""
        from api.config import Settings

        fields = Settings.model_fields
        # Should have a default between 0 and 1
        default = fields['SENTRY_SAMPLE_RATE'].default
        assert 0 <= default <= 1


class TestSentryInitialization:
    """Test Sentry SDK initialization"""

    def test_sentry_initialization_function_exists(self):
        """Test that initialize_sentry function exists"""
        from api.sentry_config import initialize_sentry
        assert callable(initialize_sentry)

    def test_sentry_not_initialized_without_dsn(self):
        """Test that Sentry is not initialized when DSN is not set"""
        from api.sentry_config import initialize_sentry

        with patch('sentry_sdk.init') as mock_init:
            initialize_sentry(dsn=None, environment="production")

            # Should not call sentry_sdk.init if no DSN
            mock_init.assert_not_called()

    def test_sentry_not_initialized_in_development(self):
        """Test that Sentry is not initialized in development environment"""
        from api.sentry_config import initialize_sentry

        with patch('sentry_sdk.init') as mock_init:
            initialize_sentry(
                dsn="https://test@sentry.io/123",
                environment="development"
            )

            # Should not initialize Sentry in development
            mock_init.assert_not_called()

    def test_sentry_initialized_in_production_with_dsn(self):
        """Test that Sentry is initialized in production with valid DSN"""
        from api.sentry_config import initialize_sentry

        with patch('sentry_sdk.init') as mock_init:
            initialize_sentry(
                dsn="https://test@sentry.io/123",
                environment="production",
                sample_rate=0.5
            )

            # Should call sentry_sdk.init in production with DSN
            mock_init.assert_called_once()
            call_kwargs = mock_init.call_args[1]
            assert call_kwargs['dsn'] == "https://test@sentry.io/123"
            assert call_kwargs['environment'] == "production"
            assert call_kwargs['traces_sample_rate'] == 0.5

    def test_sentry_initialized_in_staging_with_dsn(self):
        """Test that Sentry is initialized in staging environment"""
        from api.sentry_config import initialize_sentry

        with patch('sentry_sdk.init') as mock_init:
            initialize_sentry(
                dsn="https://test@sentry.io/123",
                environment="staging",
                sample_rate=0.3
            )

            # Should initialize in staging
            mock_init.assert_called_once()


class TestSentrySamplingRate:
    """Test error sampling rate configuration"""

    def test_custom_sample_rate_applied(self):
        """Test that custom sample rate is applied"""
        from api.sentry_config import initialize_sentry

        with patch('sentry_sdk.init') as mock_init:
            initialize_sentry(
                dsn="https://test@sentry.io/123",
                environment="production",
                sample_rate=0.25
            )

            call_kwargs = mock_init.call_args[1]
            assert call_kwargs['traces_sample_rate'] == 0.25

    def test_sample_rate_defaults_to_1_if_not_set(self):
        """Test that sample rate defaults to 1.0 if not explicitly set"""
        from api.sentry_config import initialize_sentry

        with patch('sentry_sdk.init') as mock_init:
            initialize_sentry(
                dsn="https://test@sentry.io/123",
                environment="production"
            )

            call_kwargs = mock_init.call_args[1]
            # Default should be 1.0 (capture all)
            assert call_kwargs['traces_sample_rate'] == 1.0


class TestSentryUserContext:
    """Test user context in Sentry errors"""

    def test_set_sentry_user_function_exists(self):
        """Test that set_sentry_user function exists"""
        from api.sentry_config import set_sentry_user
        assert callable(set_sentry_user)

    def test_set_sentry_user_with_id(self):
        """Test setting user context with user ID"""
        from api.sentry_config import set_sentry_user

        with patch('sentry_sdk.set_user') as mock_set_user:
            set_sentry_user(user_id="user-123")

            mock_set_user.assert_called_once()
            call_args = mock_set_user.call_args[0][0]
            assert call_args['id'] == "user-123"

    def test_set_sentry_user_with_email(self):
        """Test setting user context with email"""
        from api.sentry_config import set_sentry_user

        with patch('sentry_sdk.set_user') as mock_set_user:
            set_sentry_user(
                user_id="user-123",
                email="test@example.com"
            )

            call_args = mock_set_user.call_args[0][0]
            assert call_args['email'] == "test@example.com"

    def test_set_sentry_user_with_tenant_id(self):
        """Test setting user context with tenant ID"""
        from api.sentry_config import set_sentry_user

        with patch('sentry_sdk.set_user') as mock_set_user:
            set_sentry_user(
                user_id="user-123",
                tenant_id="tenant-456"
            )

            call_args = mock_set_user.call_args[0][0]
            assert 'tenant_id' in call_args or call_args.get('tenant_id') == "tenant-456"


class TestSentryFastAPIIntegration:
    """Test Sentry integration with FastAPI"""

    def test_fastapi_integration_enabled(self):
        """Test that FastAPI integration is included"""
        from api.sentry_config import initialize_sentry

        with patch('sentry_sdk.init') as mock_init:
            initialize_sentry(
                dsn="https://test@sentry.io/123",
                environment="production"
            )

            call_kwargs = mock_init.call_args[1]
            # Should include integrations
            assert 'integrations' in call_kwargs
            integrations = call_kwargs['integrations']

            # Check for FastAPI or Starlette integration
            integration_types = [type(i).__name__ for i in integrations]
            assert any(
                'FastApi' in name or 'Starlette' in name
                for name in integration_types
            )


class TestSentryStartupIntegration:
    """Test Sentry initialization during app startup"""

    def test_startup_imports_initialize_sentry(self):
        """Test that main.py imports initialize_sentry"""
        import inspect
        from api import main

        source = inspect.getsource(main)

        # Should import initialize_sentry
        assert "from api.sentry_config import initialize_sentry" in source
        # Should call initialize_sentry in startup
        assert "initialize_sentry(" in source

    def test_startup_passes_settings_to_sentry(self):
        """Test that startup_event passes correct settings to Sentry"""
        import inspect
        from api import main

        source = inspect.getsource(main.startup_event)

        # Should pass DSN, environment, sample_rate
        assert "settings.SENTRY_DSN" in source
        assert "settings.ENVIRONMENT" in source
        assert "settings.SENTRY_SAMPLE_RATE" in source


class TestSentryModule:
    """Test that sentry_config module has required exports"""

    def test_module_exports(self):
        """Test that sentry_config exports required functions"""
        from api import sentry_config

        assert hasattr(sentry_config, 'initialize_sentry')
        assert hasattr(sentry_config, 'set_sentry_user')
        assert hasattr(sentry_config, 'capture_exception')

    def test_capture_exception_wrapper(self):
        """Test capture_exception wrapper function"""
        from api.sentry_config import capture_exception

        with patch('sentry_sdk.capture_exception') as mock_capture:
            test_error = ValueError("test error")
            capture_exception(test_error)

            mock_capture.assert_called_once_with(test_error)

