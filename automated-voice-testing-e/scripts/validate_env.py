#!/usr/bin/env python3
"""
Environment variable validation script.

Validates that required environment variables are set before application startup.
Provides helpful error messages for missing or invalid configurations.
"""

import os
import sys
from typing import List, Tuple


def validate_required_vars() -> Tuple[List[str], List[str]]:
    """
    Validate required environment variables.

    Returns:
        Tuple of (errors, warnings) lists
    """
    errors = []
    warnings = []

    # Required variables (app will not start without these)
    required_vars = [
        ("DATABASE_URL", "PostgreSQL connection string"),
        ("SECRET_KEY", "Application secret key for JWT/sessions"),
    ]

    # Optional but recommended (app will run with degraded functionality)
    optional_vars = [
        ("REDIS_URL", "Redis connection for caching/sessions"),
        ("CELERY_BROKER_URL", "Celery task queue broker"),
        ("CELERY_RESULT_BACKEND", "Celery result backend"),
    ]

    # Optional service-specific variables
    service_vars = [
        ("SOUNDHOUND_API_KEY", "SoundHound Voice AI integration"),
        ("AWS_ACCESS_KEY_ID", "AWS S3 file storage"),
        ("AWS_SECRET_ACCESS_KEY", "AWS S3 file storage"),
    ]

    # Check required variables
    for var_name, description in required_vars:
        value = os.environ.get(var_name)
        if not value:
            errors.append(f"REQUIRED: {var_name} - {description}")

    # Check optional but recommended variables
    for var_name, description in optional_vars:
        value = os.environ.get(var_name)
        if not value:
            warnings.append(f"OPTIONAL: {var_name} - {description}")

    # Check service-specific variables (informational)
    for var_name, description in service_vars:
        value = os.environ.get(var_name)
        if not value:
            warnings.append(f"SERVICE: {var_name} - {description} (disabled)")

    return errors, warnings


def validate_database_url() -> List[str]:
    """Validate DATABASE_URL format."""
    errors = []
    database_url = os.environ.get("DATABASE_URL", "")

    if database_url:
        if not database_url.startswith(("postgresql://", "postgres://")):
            errors.append(
                "DATABASE_URL must be a PostgreSQL connection string "
                "(e.g., postgresql://user:pass@host:port/dbname)"
            )

    return errors


def validate_redis_url() -> List[str]:
    """Validate REDIS_URL format."""
    errors = []
    redis_url = os.environ.get("REDIS_URL", "")

    if redis_url and not redis_url.startswith("redis://"):
        errors.append(
            "REDIS_URL must be a Redis connection string "
            "(e.g., redis://localhost:6379/0)"
        )

    return errors


def validate_environment() -> List[str]:
    """Validate ENVIRONMENT value."""
    warnings = []
    environment = os.environ.get("ENVIRONMENT", "development")

    valid_envs = ["development", "staging", "production", "test"]
    if environment not in valid_envs:
        warnings.append(
            f"ENVIRONMENT '{environment}' is not standard. "
            f"Expected one of: {', '.join(valid_envs)}"
        )

    return warnings


def main() -> int:
    """
    Main validation entry point.

    Returns:
        0 if validation passes, 1 if critical errors found
    """
    print("Validating environment variables...")
    print("-" * 50)

    all_errors = []
    all_warnings = []

    # Run all validations
    errors, warnings = validate_required_vars()
    all_errors.extend(errors)
    all_warnings.extend(warnings)

    all_errors.extend(validate_database_url())
    all_errors.extend(validate_redis_url())
    all_warnings.extend(validate_environment())

    # Print warnings
    if all_warnings:
        print("\nWARNINGS:")
        for warning in all_warnings:
            print(f"  - {warning}")

    # Print errors
    if all_errors:
        print("\nERRORS:")
        for error in all_errors:
            print(f"  - {error}")
        print("\nValidation FAILED!")
        print("Please set the required environment variables and try again.")
        return 1

    print("\nValidation PASSED!")
    if all_warnings:
        print(f"({len(all_warnings)} warnings - some features may be disabled)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
