"""
Voice AI Testing Framework - Logging Configuration
JSON structured logging with request ID and user context tracking
"""

import logging
import json
import sys
import re
from datetime import datetime, timezone
from typing import Optional
from contextvars import ContextVar
from logging.handlers import RotatingFileHandler
from pathlib import Path


# ============================================================================
# Context Variables for Request and User Tracking
# ============================================================================

# Context variable to store request ID across async contexts
request_id_var: ContextVar[Optional[str]] = ContextVar('request_id', default=None)

# Context variable to store user ID across async contexts
user_id_var: ContextVar[Optional[str]] = ContextVar('user_id', default=None)


# ============================================================================
# Context Management Functions
# ============================================================================

def set_request_id(request_id: str) -> None:
    """
    Set the request ID for the current context

    Args:
        request_id: The request ID to set (e.g., from X-Request-ID header)

    Example:
        ```python
        from api.logging_config import set_request_id

        set_request_id("req-12345")
        ```
    """
    request_id_var.set(request_id)


def get_request_id() -> Optional[str]:
    """
    Get the request ID from the current context

    Returns:
        The current request ID, or None if not set

    Example:
        ```python
        from api.logging_config import get_request_id

        request_id = get_request_id()
        ```
    """
    return request_id_var.get()


def set_user_id(user_id: str) -> None:
    """
    Set the user ID for the current context

    Args:
        user_id: The user ID to set (e.g., from authenticated user)

    Example:
        ```python
        from api.logging_config import set_user_id

        set_user_id("user-789")
        ```
    """
    user_id_var.set(user_id)


def get_user_id() -> Optional[str]:
    """
    Get the user ID from the current context

    Returns:
        The current user ID, or None if not set

    Example:
        ```python
        from api.logging_config import get_user_id

        user_id = get_user_id()
        ```
    """
    return user_id_var.get()


# ============================================================================
# JSON Formatter
# ============================================================================

class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging

    Formats log records as JSON with additional context information:
    - timestamp: ISO 8601 formatted timestamp
    - level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - message: Log message
    - logger: Logger name
    - request_id: Current request ID (if set)
    - user_id: Current user ID (if set)
    - Additional fields from the log record
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Format a log record as JSON

        Args:
            record: The log record to format

        Returns:
            JSON formatted string
        """
        # Base log data
        log_data = {
            'timestamp': datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'logger': record.name,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }

        # Add request ID if available
        request_id = get_request_id()
        if request_id:
            log_data['request_id'] = request_id

        # Add user ID if available
        user_id = get_user_id()
        if user_id:
            log_data['user_id'] = user_id

        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        # Add stack info if present
        if record.stack_info:
            log_data['stack_info'] = record.stack_info

        # Add any extra fields from the record
        # These are fields added via logger.info("msg", extra={...})
        if hasattr(record, '__dict__'):
            for key, value in record.__dict__.items():
                # Skip standard logging fields
                if key not in [
                    'name', 'msg', 'args', 'created', 'filename', 'funcName',
                    'levelname', 'levelno', 'lineno', 'module', 'msecs',
                    'message', 'pathname', 'process', 'processName',
                    'relativeCreated', 'thread', 'threadName', 'exc_info',
                    'exc_text', 'stack_info', 'taskName'
                ]:
                    # Skip private attributes
                    if not key.startswith('_'):
                        try:
                            # Try to serialize the value
                            json.dumps(value)
                            log_data[key] = value
                        except (TypeError, ValueError):
                            # If not serializable, convert to string
                            log_data[key] = str(value)

        # Convert to JSON string
        return json.dumps(log_data)


# ============================================================================
# Sensitive Data Masking Filter
# ============================================================================

class SensitiveDataFilter(logging.Filter):
    """
    Filter to mask sensitive data in log messages.

    Masks passwords, API keys, tokens, and connection strings
    to prevent sensitive information from being logged.
    """

    # Patterns to match and mask
    SENSITIVE_PATTERNS = [
        # Password patterns
        (r'password[=:\s]+[^\s,}"\'\]]+', r'password=***MASKED***'),
        (r'pwd[=:\s]+[^\s,}"\'\]]+', r'pwd=***MASKED***'),
        # API key patterns
        (r'api[_-]?key[=:\s]+[^\s,}"\'\]]+', r'api_key=***MASKED***'),
        (r'sk-[a-zA-Z0-9]+', r'***MASKED***'),
        (r'AKIA[A-Z0-9]+', r'***MASKED***'),
        # Token patterns
        (r'token[=:\s]+[^\s,}"\'\]]+', r'token=***MASKED***'),
        (r'bearer[=:\s]+[^\s,}"\'\]]+', r'bearer=***MASKED***'),
        # Secret patterns
        (r'secret[=:\s]+[^\s,}"\'\]]+', r'secret=***MASKED***'),
        # Connection string passwords
        (r'://[^:]+:[^@]+@', r'://***:***@'),
    ]

    # Compiled patterns for performance
    _compiled_patterns = None

    def __init__(self):
        super().__init__()
        if SensitiveDataFilter._compiled_patterns is None:
            SensitiveDataFilter._compiled_patterns = [
                (re.compile(pattern, re.IGNORECASE), replacement)
                for pattern, replacement in self.SENSITIVE_PATTERNS
            ]

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filter and mask sensitive data in the log record.

        Args:
            record: The log record to filter

        Returns:
            True (always allows the record through after masking)
        """
        # Mask sensitive data in the message
        if record.msg:
            masked_msg = str(record.msg)
            for pattern, replacement in self._compiled_patterns:
                masked_msg = pattern.sub(replacement, masked_msg)
            record.msg = masked_msg

        # Also mask in args if they exist
        if record.args:
            masked_args = []
            for arg in record.args:
                if isinstance(arg, str):
                    masked_arg = arg
                    for pattern, replacement in self._compiled_patterns:
                        masked_arg = pattern.sub(replacement, masked_arg)
                    masked_args.append(masked_arg)
                else:
                    masked_args.append(arg)
            record.args = tuple(masked_args)

        return True


# ============================================================================
# Logging Setup
# ============================================================================

def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    log_dir: str = "logs",
    max_bytes: int = 10485760,  # 10MB
    backup_count: int = 10,
    json_format: bool = True,
) -> None:
    """
    Set up application logging with JSON formatting and rotation

    Args:
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Log file name (if None, logs to console only)
        log_dir: Directory to store log files
        max_bytes: Maximum size of log file before rotation (default: 10MB)
        backup_count: Number of backup log files to keep (default: 10)
        json_format: Use JSON formatting (default: True)

    Example:
        ```python
        from api.logging_config import setup_logging

        # Set up logging with JSON format and file rotation
        setup_logging(
            log_level="INFO",
            log_file="app.log",
            max_bytes=10485760,  # 10MB
            backup_count=10
        )
        ```
    """
    # Get root logger
    root_logger = logging.getLogger()

    # Set log level
    level = getattr(logging, log_level.upper(), logging.INFO)
    root_logger.setLevel(level)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Choose formatter
    if json_format:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    # Create sensitive data filter
    sensitive_filter = SensitiveDataFilter()

    # Console handler (always add)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(sensitive_filter)
    root_logger.addHandler(console_handler)

    # File handler with rotation (if log_file specified)
    if log_file:
        # Create log directory if it doesn't exist
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)

        # Full path to log file
        log_file_path = log_path / log_file

        # Create rotating file handler
        file_handler = RotatingFileHandler(
            filename=str(log_file_path),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        file_handler.addFilter(sensitive_filter)
        root_logger.addHandler(file_handler)

    # Silence noisy third-party libraries
    # botocore has a bug in debug logging that causes formatting errors
    logging.getLogger('botocore').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('boto3').setLevel(logging.WARNING)
    logging.getLogger('s3transfer').setLevel(logging.WARNING)

    # Log that logging is configured
    root_logger.info(
        f"Logging configured: level={log_level}, json_format={json_format}, "
        f"log_file={log_file or 'console only'}"
    )


# ============================================================================
# Convenience Functions
# ============================================================================

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name

    Args:
        name: Logger name (typically __name__ from the calling module)

    Returns:
        Logger instance

    Example:
        ```python
        from api.logging_config import get_logger

        logger = get_logger(__name__)
        logger.info("Application started")
        ```
    """
    return logging.getLogger(name)


# ============================================================================
# Utility Functions for Structured Logging
# ============================================================================

def log_with_context(
    logger: logging.Logger,
    level: str,
    message: str,
    **kwargs
) -> None:
    """
    Log a message with additional context

    Args:
        logger: Logger instance
        level: Log level (debug, info, warning, error, critical)
        message: Log message
        **kwargs: Additional context fields

    Example:
        ```python
        from api.logging_config import get_logger, log_with_context

        logger = get_logger(__name__)
        log_with_context(
            logger,
            "info",
            "User action completed",
            action="create_test",
            test_id="test-123",
            duration_ms=150
        )
        ```
    """
    log_method = getattr(logger, level.lower())
    log_method(message, extra=kwargs)


# ============================================================================
# Export public API
# ============================================================================

__all__ = [
    'JSONFormatter',
    'SensitiveDataFilter',
    'setup_logging',
    'get_logger',
    'set_request_id',
    'get_request_id',
    'set_user_id',
    'get_user_id',
    'request_id_var',
    'user_id_var',
    'log_with_context',
]
