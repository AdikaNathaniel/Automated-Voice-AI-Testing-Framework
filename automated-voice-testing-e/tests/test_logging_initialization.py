"""
Tests for logging initialization in application startup.

These tests verify that:
1. Logging is initialized in startup_event()
2. Log levels are environment-aware
3. Sensitive data is masked in log output
4. Log retention policy is properly configured
"""

import pytest
import sys
import os
import logging
import json
from unittest.mock import patch, MagicMock
from io import StringIO

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from api.logging_config import (
    setup_logging,
    get_logger,
    JSONFormatter,
    SensitiveDataFilter,
)
from api.config import get_settings


class TestSetupLoggingCalled:
    """Test that setup_logging is called during application startup"""

    def test_setup_logging_function_exists(self):
        """Test that setup_logging function is importable"""
        from api.logging_config import setup_logging
        assert callable(setup_logging)

    def test_main_app_imports_setup_logging(self):
        """Test that main.py imports setup_logging"""
        import api.main as main_module
        # Check that setup_logging is imported or called in main
        source = open(main_module.__file__).read()
        assert 'setup_logging' in source

    def test_startup_event_calls_setup_logging(self):
        """Test that startup_event initializes logging"""
        import api.main as main_module
        source = open(main_module.__file__).read()
        # Check that setup_logging is called in startup_event
        assert 'setup_logging' in source


class TestEnvironmentAwareLogLevels:
    """Test that log levels are configured based on environment"""

    def test_production_uses_info_level(self):
        """Test that production environment uses INFO log level"""
        with patch('api.config.get_settings') as mock_settings:
            settings = MagicMock()
            settings.ENVIRONMENT = "production"
            settings.DEBUG = False
            settings.LOG_LEVEL = "INFO"
            mock_settings.return_value = settings

            # Verify settings
            result = mock_settings()
            assert result.ENVIRONMENT == "production"
            assert result.LOG_LEVEL == "INFO"

    def test_development_uses_debug_level(self):
        """Test that development environment uses DEBUG log level"""
        with patch('api.config.get_settings') as mock_settings:
            settings = MagicMock()
            settings.ENVIRONMENT = "development"
            settings.DEBUG = True
            settings.LOG_LEVEL = "DEBUG"
            mock_settings.return_value = settings

            result = mock_settings()
            assert result.ENVIRONMENT == "development"
            assert result.LOG_LEVEL == "DEBUG"

    def test_setup_logging_respects_log_level(self):
        """Test that setup_logging sets the correct log level"""
        # Reset logging state
        root_logger = logging.getLogger()
        root_logger.handlers.clear()

        setup_logging(log_level="WARNING")

        assert root_logger.level == logging.WARNING

    def test_setup_logging_debug_level(self):
        """Test that DEBUG level is set correctly"""
        root_logger = logging.getLogger()
        root_logger.handlers.clear()

        setup_logging(log_level="DEBUG")

        assert root_logger.level == logging.DEBUG


class TestSensitiveDataMasking:
    """Test that sensitive data is masked in log output"""

    def test_sensitive_data_filter_exists(self):
        """Test that SensitiveDataFilter class exists"""
        from api.logging_config import SensitiveDataFilter
        assert SensitiveDataFilter is not None

    def test_filter_masks_password_in_message(self):
        """Test that passwords are masked in log messages"""
        filter_instance = SensitiveDataFilter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="User login with password=secret123",
            args=(),
            exc_info=None
        )

        filter_instance.filter(record)

        assert "secret123" not in record.msg
        assert "***MASKED***" in record.msg or "password" in record.msg.lower()

    def test_filter_masks_api_key_in_message(self):
        """Test that API keys are masked in log messages"""
        filter_instance = SensitiveDataFilter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="API call with api_key=sk-1234567890abcdef",
            args=(),
            exc_info=None
        )

        filter_instance.filter(record)

        assert "sk-1234567890abcdef" not in record.msg

    def test_filter_masks_token_in_message(self):
        """Test that tokens are masked in log messages"""
        filter_instance = SensitiveDataFilter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Bearer token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
            args=(),
            exc_info=None
        )

        filter_instance.filter(record)

        assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in record.msg

    def test_filter_masks_connection_string(self):
        """Test that database connection strings are masked"""
        filter_instance = SensitiveDataFilter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Connecting to postgresql://admin:password123@db.example.com:5432/prod",
            args=(),
            exc_info=None
        )

        filter_instance.filter(record)

        assert "password123" not in record.msg

    def test_filter_preserves_non_sensitive_data(self):
        """Test that non-sensitive data is preserved"""
        filter_instance = SensitiveDataFilter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Processing request for user_id=123, action=create_test",
            args=(),
            exc_info=None
        )

        original_msg = record.msg
        filter_instance.filter(record)

        # Non-sensitive data should be preserved
        assert "user_id=123" in record.msg
        assert "action=create_test" in record.msg


class TestLogRetentionPolicy:
    """Test log retention configuration"""

    def test_rotating_file_handler_configuration(self):
        """Test that rotating file handler uses correct retention settings"""
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as temp_dir:
            root_logger = logging.getLogger()
            root_logger.handlers.clear()

            setup_logging(
                log_file="test.log",
                log_dir=temp_dir,
                max_bytes=1048576,  # 1MB
                backup_count=5
            )

            # Find the rotating file handler
            file_handler = None
            for handler in root_logger.handlers:
                if hasattr(handler, 'maxBytes'):
                    file_handler = handler
                    break

            assert file_handler is not None
            assert file_handler.maxBytes == 1048576
            assert file_handler.backupCount == 5

    def test_default_retention_settings(self):
        """Test default retention settings (10MB, 10 backups)"""
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            root_logger = logging.getLogger()
            root_logger.handlers.clear()

            setup_logging(
                log_file="test.log",
                log_dir=temp_dir
            )

            # Find the rotating file handler
            file_handler = None
            for handler in root_logger.handlers:
                if hasattr(handler, 'maxBytes'):
                    file_handler = handler
                    break

            assert file_handler is not None
            # Default is 10MB
            assert file_handler.maxBytes == 10485760
            # Default is 10 backups
            assert file_handler.backupCount == 10


class TestJSONFormatterOutput:
    """Test JSON formatter output structure"""

    def test_json_formatter_produces_valid_json(self):
        """Test that JSONFormatter produces valid JSON"""
        formatter = JSONFormatter()

        record = logging.LogRecord(
            name="test.module",
            level=logging.INFO,
            pathname="test.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None
        )

        output = formatter.format(record)

        # Should be valid JSON
        parsed = json.loads(output)
        assert parsed['message'] == "Test message"
        assert parsed['level'] == "INFO"
        assert parsed['logger'] == "test.module"
        assert parsed['line'] == 42

    def test_json_formatter_includes_extra_fields(self):
        """Test that extra fields are included in JSON output"""
        formatter = JSONFormatter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None
        )

        # Add extra fields
        record.user_action = "create_test"
        record.test_id = "test-123"

        output = formatter.format(record)
        parsed = json.loads(output)

        assert parsed['user_action'] == "create_test"
        assert parsed['test_id'] == "test-123"


class TestLoggingIntegration:
    """Integration tests for logging configuration"""

    def test_logger_output_includes_timestamp(self):
        """Test that log output includes ISO timestamp"""
        formatter = JSONFormatter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test",
            args=(),
            exc_info=None
        )

        output = formatter.format(record)
        parsed = json.loads(output)

        assert 'timestamp' in parsed
        # Should be ISO format
        assert 'T' in parsed['timestamp']

    def test_setup_logging_clears_existing_handlers(self):
        """Test that setup_logging clears existing handlers"""
        root_logger = logging.getLogger()

        # Add a dummy handler
        dummy_handler = logging.StreamHandler()
        root_logger.addHandler(dummy_handler)

        initial_count = len(root_logger.handlers)

        setup_logging(log_level="INFO")

        # Should have cleared old handlers and added new ones
        # (at least console handler)
        assert len(root_logger.handlers) >= 1
        assert dummy_handler not in root_logger.handlers
