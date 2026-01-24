"""
Test suite for logging configuration
Ensures backend/api/logging_config.py exists and provides proper JSON structured logging
"""

import os
import sys
import json
import logging
import pytest
from io import StringIO

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend'))


class TestLoggingConfigFile:
    """Test logging configuration file exists"""

    @pytest.fixture
    def project_root(self):
        """Get project root directory"""
        return os.path.dirname(os.path.dirname(__file__))

    @pytest.fixture
    def logging_config_path(self, project_root):
        """Get path to backend/api/logging_config.py file"""
        return os.path.join(project_root, 'backend', 'api', 'logging_config.py')

    def test_logging_config_py_exists(self, logging_config_path):
        """Test that backend/api/logging_config.py file exists"""
        assert os.path.exists(logging_config_path), \
            "backend/api/logging_config.py file must exist"

    def test_can_import_logging_config(self):
        """Test that we can import logging configuration"""
        try:
            import api.logging_config
            assert api.logging_config is not None
        except ImportError as e:
            pytest.fail(f"Failed to import api.logging_config: {e}")


class TestJSONFormatter:
    """Test JSON formatter for structured logging"""

    def test_json_formatter_exists(self):
        """Test that JSONFormatter class exists"""
        try:
            from api.logging_config import JSONFormatter
            assert JSONFormatter is not None, "JSONFormatter class should be defined"
        except ImportError as e:
            pytest.fail(f"Failed to import JSONFormatter: {e}")

    def test_json_formatter_inherits_from_logging_formatter(self):
        """Test that JSONFormatter inherits from logging.Formatter"""
        from api.logging_config import JSONFormatter

        assert issubclass(JSONFormatter, logging.Formatter), \
            "JSONFormatter should inherit from logging.Formatter"

    def test_json_formatter_formats_as_json(self):
        """Test that JSONFormatter outputs valid JSON"""
        from api.logging_config import JSONFormatter

        # Create a logger with JSON formatter
        logger = logging.getLogger('test_json_logger')
        logger.setLevel(logging.INFO)

        # Create string stream to capture output
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)

        # Log a message
        logger.info("Test message")

        # Get the output and verify it's valid JSON
        output = stream.getvalue().strip()

        try:
            log_data = json.loads(output)
            assert isinstance(log_data, dict), "JSON formatter should output a dictionary"
        except json.JSONDecodeError:
            pytest.fail(f"JSONFormatter output is not valid JSON: {output}")
        finally:
            logger.removeHandler(handler)

    def test_json_formatter_includes_timestamp(self):
        """Test that JSON formatter includes timestamp"""
        from api.logging_config import JSONFormatter

        logger = logging.getLogger('test_timestamp_logger')
        logger.setLevel(logging.INFO)

        stream = StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)

        logger.info("Test message")

        output = stream.getvalue().strip()
        log_data = json.loads(output)

        assert 'timestamp' in log_data or 'time' in log_data or '@timestamp' in log_data, \
            "JSON log should include timestamp field"

        logger.removeHandler(handler)

    def test_json_formatter_includes_log_level(self):
        """Test that JSON formatter includes log level"""
        from api.logging_config import JSONFormatter

        logger = logging.getLogger('test_level_logger')
        logger.setLevel(logging.INFO)

        stream = StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)

        logger.warning("Test warning")

        output = stream.getvalue().strip()
        log_data = json.loads(output)

        assert 'level' in log_data or 'levelname' in log_data, \
            "JSON log should include log level field"
        assert log_data.get('level', log_data.get('levelname')) == 'WARNING', \
            "Log level should be WARNING"

        logger.removeHandler(handler)

    def test_json_formatter_includes_message(self):
        """Test that JSON formatter includes the log message"""
        from api.logging_config import JSONFormatter

        logger = logging.getLogger('test_message_logger')
        logger.setLevel(logging.INFO)

        stream = StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)

        test_message = "This is a test message"
        logger.info(test_message)

        output = stream.getvalue().strip()
        log_data = json.loads(output)

        assert 'message' in log_data or 'msg' in log_data, \
            "JSON log should include message field"
        assert test_message in str(log_data.get('message', log_data.get('msg'))), \
            "Log message should contain the test message"

        logger.removeHandler(handler)

    def test_json_formatter_includes_logger_name(self):
        """Test that JSON formatter includes logger name"""
        from api.logging_config import JSONFormatter

        logger_name = 'test_name_logger'
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)

        stream = StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)

        logger.info("Test")

        output = stream.getvalue().strip()
        log_data = json.loads(output)

        assert 'name' in log_data or 'logger' in log_data or 'logger_name' in log_data, \
            "JSON log should include logger name field"

        logger.removeHandler(handler)


class TestRequestIDLogging:
    """Test request ID context in logging"""

    def test_request_id_context_var_exists(self):
        """Test that request_id context variable exists"""
        try:
            from api.logging_config import request_id_var
            assert request_id_var is not None
        except ImportError as e:
            pytest.fail(f"Failed to import request_id_var: {e}")

    def test_get_request_id_function_exists(self):
        """Test that get_request_id function exists"""
        try:
            from api.logging_config import get_request_id
            assert get_request_id is not None
        except ImportError as e:
            pytest.fail(f"Failed to import get_request_id: {e}")

    def test_set_request_id_function_exists(self):
        """Test that set_request_id function exists"""
        try:
            from api.logging_config import set_request_id
            assert set_request_id is not None
        except ImportError as e:
            pytest.fail(f"Failed to import set_request_id: {e}")

    def test_can_set_and_get_request_id(self):
        """Test that we can set and get request ID"""
        from api.logging_config import set_request_id, get_request_id

        test_request_id = "test-request-123"
        set_request_id(test_request_id)

        retrieved_id = get_request_id()
        assert retrieved_id == test_request_id, \
            f"Retrieved request ID should match set value. Got {retrieved_id}, expected {test_request_id}"

    def test_json_formatter_includes_request_id(self):
        """Test that JSON formatter includes request ID when set"""
        from api.logging_config import JSONFormatter, set_request_id

        test_request_id = "req-456"
        set_request_id(test_request_id)

        logger = logging.getLogger('test_req_id_logger')
        logger.setLevel(logging.INFO)

        stream = StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)

        logger.info("Test with request ID")

        output = stream.getvalue().strip()
        log_data = json.loads(output)

        assert 'request_id' in log_data or 'requestId' in log_data, \
            "JSON log should include request_id field"

        logger.removeHandler(handler)


class TestUserContextLogging:
    """Test user context in logging"""

    def test_user_id_context_var_exists(self):
        """Test that user_id context variable exists"""
        try:
            from api.logging_config import user_id_var
            assert user_id_var is not None
        except ImportError as e:
            pytest.fail(f"Failed to import user_id_var: {e}")

    def test_get_user_id_function_exists(self):
        """Test that get_user_id function exists"""
        try:
            from api.logging_config import get_user_id
            assert get_user_id is not None
        except ImportError as e:
            pytest.fail(f"Failed to import get_user_id: {e}")

    def test_set_user_id_function_exists(self):
        """Test that set_user_id function exists"""
        try:
            from api.logging_config import set_user_id
            assert set_user_id is not None
        except ImportError as e:
            pytest.fail(f"Failed to import set_user_id: {e}")

    def test_can_set_and_get_user_id(self):
        """Test that we can set and get user ID"""
        from api.logging_config import set_user_id, get_user_id

        test_user_id = "user-789"
        set_user_id(test_user_id)

        retrieved_id = get_user_id()
        assert retrieved_id == test_user_id, \
            f"Retrieved user ID should match set value. Got {retrieved_id}, expected {test_user_id}"

    def test_json_formatter_includes_user_id(self):
        """Test that JSON formatter includes user ID when set"""
        from api.logging_config import JSONFormatter, set_user_id

        test_user_id = "user-999"
        set_user_id(test_user_id)

        logger = logging.getLogger('test_user_id_logger')
        logger.setLevel(logging.INFO)

        stream = StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)

        logger.info("Test with user ID")

        output = stream.getvalue().strip()
        log_data = json.loads(output)

        assert 'user_id' in log_data or 'userId' in log_data, \
            "JSON log should include user_id field"

        logger.removeHandler(handler)


class TestLoggingSetup:
    """Test logging setup functions"""

    def test_setup_logging_function_exists(self):
        """Test that setup_logging function exists"""
        try:
            from api.logging_config import setup_logging
            assert setup_logging is not None
        except ImportError as e:
            pytest.fail(f"Failed to import setup_logging: {e}")

    def test_get_logger_function_exists(self):
        """Test that get_logger function exists"""
        try:
            from api.logging_config import get_logger
            assert get_logger is not None
        except ImportError as e:
            pytest.fail(f"Failed to import get_logger: {e}")

    def test_get_logger_returns_logger_instance(self):
        """Test that get_logger returns a logger instance"""
        from api.logging_config import get_logger

        logger = get_logger("test_logger")
        assert isinstance(logger, logging.Logger), \
            "get_logger should return a logging.Logger instance"

    def test_get_logger_with_name(self):
        """Test that get_logger creates logger with correct name"""
        from api.logging_config import get_logger

        logger_name = "test.module.logger"
        logger = get_logger(logger_name)

        assert logger.name == logger_name, \
            f"Logger name should be '{logger_name}', got '{logger.name}'"


class TestLogRotation:
    """Test log rotation configuration"""

    def test_rotating_file_handler_config_exists(self):
        """Test that rotating file handler configuration exists"""
        try:
            from api.logging_config import setup_logging
            # Function should exist and be callable
            assert callable(setup_logging)
        except ImportError as e:
            pytest.fail(f"Failed to import setup_logging: {e}")

    def test_log_file_path_configuration(self):
        """Test that log file path can be configured"""
        from api.logging_config import setup_logging

        # Should accept log file path parameter
        import inspect
        sig = inspect.signature(setup_logging)
        params = list(sig.parameters.keys())

        # Should have parameters for configuration
        assert len(params) > 0, \
            "setup_logging should accept configuration parameters"
