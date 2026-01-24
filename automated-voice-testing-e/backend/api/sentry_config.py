"""
Voice AI Testing Framework - Sentry Error Tracking Configuration

This module provides Sentry SDK initialization and helper functions
for error tracking in production and staging environments.
"""

import logging
from typing import Optional

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

logger = logging.getLogger(__name__)


def initialize_sentry(
    dsn: Optional[str] = None,
    environment: str = "development",
    sample_rate: float = 1.0,
    release: Optional[str] = None,
) -> None:
    """
    Initialize Sentry SDK for error tracking.

    Only initializes Sentry in production or staging environments
    when a valid DSN is provided.

    Args:
        dsn: Sentry DSN (Data Source Name)
        environment: Current environment (development, staging, production)
        sample_rate: Traces sample rate (0.0 to 1.0)
        release: Application release version

    Example:
        >>> initialize_sentry(
        ...     dsn="https://key@sentry.io/123",
        ...     environment="production",
        ...     sample_rate=0.5
        ... )
    """
    # Don't initialize if no DSN provided
    if not dsn:
        logger.info("Sentry DSN not provided, skipping initialization")
        return

    # Don't initialize in development
    if environment == "development":
        logger.info("Sentry disabled in development environment")
        return

    # Initialize Sentry SDK
    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        traces_sample_rate=sample_rate,
        release=release,
        integrations=[
            FastApiIntegration(transaction_style="endpoint"),
            StarletteIntegration(transaction_style="endpoint"),
            SqlalchemyIntegration(),
            RedisIntegration(),
            CeleryIntegration(),
            LoggingIntegration(
                level=logging.INFO,
                event_level=logging.ERROR
            ),
        ],
        # Set to True to enable performance monitoring
        enable_tracing=True,
        # Include local variables in stack traces
        include_local_variables=True,
        # Attach stacktrace to logs
        attach_stacktrace=True,
        # Send default PII (IP addresses, etc.)
        send_default_pii=False,
    )

    logger.info(
        "Sentry initialized: environment=%s, sample_rate=%.2f",
        environment, sample_rate
    )


def set_sentry_user(
    user_id: Optional[str] = None,
    email: Optional[str] = None,
    username: Optional[str] = None,
    tenant_id: Optional[str] = None,
) -> None:
    """
    Set user context for Sentry error tracking.

    This information will be attached to all subsequent error reports
    until the context is cleared.

    Args:
        user_id: User identifier
        email: User email address
        username: Username
        tenant_id: Tenant identifier for multi-tenant systems

    Example:
        >>> set_sentry_user(
        ...     user_id="user-123",
        ...     email="user@example.com",
        ...     tenant_id="tenant-456"
        ... )
    """
    user_context = {}

    if user_id:
        user_context['id'] = user_id
    if email:
        user_context['email'] = email
    if username:
        user_context['username'] = username
    if tenant_id:
        user_context['tenant_id'] = tenant_id

    if user_context:
        sentry_sdk.set_user(user_context)


def clear_sentry_user() -> None:
    """
    Clear user context from Sentry.

    Should be called at the end of a request or when the user logs out.
    """
    sentry_sdk.set_user(None)


def capture_exception(error: Exception) -> None:
    """
    Capture and send an exception to Sentry.

    Wrapper around sentry_sdk.capture_exception for consistency.

    Args:
        error: The exception to capture

    Example:
        >>> try:
        ...     risky_operation()
        ... except Exception as e:
        ...     capture_exception(e)
        ...     raise
    """
    sentry_sdk.capture_exception(error)


def capture_message(message: str, level: str = "info") -> None:
    """
    Capture and send a message to Sentry.

    Args:
        message: The message to send
        level: Message level (info, warning, error)

    Example:
        >>> capture_message("User performed risky action", level="warning")
    """
    sentry_sdk.capture_message(message, level=level)


def set_sentry_tag(key: str, value: str) -> None:
    """
    Set a tag that will be attached to all subsequent events.

    Args:
        key: Tag key
        value: Tag value

    Example:
        >>> set_sentry_tag("feature", "voice-testing")
    """
    sentry_sdk.set_tag(key, value)


def set_sentry_context(name: str, data: dict) -> None:
    """
    Set additional context for Sentry events.

    Args:
        name: Context name
        data: Context data dictionary

    Example:
        >>> set_sentry_context("suite_run", {
        ...     "suite_run_id": "123",
        ...     "suite_id": "456"
        ... })
    """
    sentry_sdk.set_context(name, data)


# Export public API
__all__ = [
    'initialize_sentry',
    'set_sentry_user',
    'clear_sentry_user',
    'capture_exception',
    'capture_message',
    'set_sentry_tag',
    'set_sentry_context',
]
