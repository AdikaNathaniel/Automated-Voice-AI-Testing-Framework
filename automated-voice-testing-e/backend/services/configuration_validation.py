"""
Configuration validation utilities (TASK-251).

Provides JSON Schema validation for known configuration keys to ensure that
configuration payloads remain well-structured and safe to activate.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Mapping

from jsonschema import Draft7Validator


class ConfigurationValidationError(ValueError):
    """Raised when configuration data fails schema validation."""


_DEFAULT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "additionalProperties": True,
}

_CONFIG_SCHEMAS: Dict[str, Dict[str, Any]] = {
    "smtp.settings": {
        "type": "object",
        "required": ["host"],
        "properties": {
            "host": {"type": "string", "minLength": 1},
            "port": {"type": "integer", "minimum": 1, "maximum": 65535},
            "use_tls": {"type": "boolean"},
            "username": {"type": "string", "minLength": 1},
            "password": {"type": "string"},
            "timeout": {"type": "integer", "minimum": 0},
            "retries": {"type": "integer", "minimum": 0},
        },
        "additionalProperties": True,
    },
    "feature.flag": {
        "type": "object",
        "required": ["enabled"],
        "properties": {
            "enabled": {"type": "boolean"},
            "rollout": {"type": "number", "minimum": 0.0, "maximum": 1.0},
            "description": {"type": "string"},
            "targets": {
                "type": "array",
                "items": {"type": "string", "minLength": 1},
            },
        },
        "additionalProperties": True,
    },
    "queue.config": {
        "type": "object",
        "required": ["size"],
        "properties": {
            "size": {"type": "integer", "minimum": 1},
            "priority": {"type": "string", "enum": ["low", "normal", "high"]},
            "timeout_seconds": {"type": "integer", "minimum": 0},
            "retry_limit": {"type": "integer", "minimum": 0},
        },
        "additionalProperties": True,
    },
    "integration.cicd": {
        "type": "object",
        "required": ["providers"],
        "properties": {
            "default_suite_id": {
                "type": "string",
                "pattern": "^[0-9a-fA-F\\-]{36}$",
            },
            "providers": {
                "type": "object",
                "minProperties": 1,
                "additionalProperties": {
                    "type": "object",
                    "required": ["secret"],
                    "properties": {
                        "secret": {"type": "string", "minLength": 1},
                        "suite_id": {
                            "type": "string",
                            "pattern": "^[0-9a-fA-F\\-]{36}$",
                        },
                        "test_case_ids": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "pattern": "^[0-9a-fA-F\\-]{36}$",
                            },
                        },
                        "enabled": {"type": "boolean"},
                    },
                    "additionalProperties": True,
                },
            },
        },
        "additionalProperties": True,
    },
    "integration.jira": {
        "type": "object",
        "required": ["base_url", "api_token", "project_mapping"],
        "properties": {
            "base_url": {"type": "string", "minLength": 1, "format": "uri"},
            "browse_url": {"type": "string", "minLength": 1, "format": "uri"},
            "user_email": {"type": "string", "minLength": 1, "format": "email"},
            "api_token": {"type": "string", "minLength": 1},
            "timeout_seconds": {"type": "number", "minimum": 1},
            "project_mapping": {
                "type": "object",
                "minProperties": 1,
                "additionalProperties": {
                    "type": "object",
                    "required": ["project_key"],
                    "properties": {
                        "project_key": {"type": "string", "minLength": 1},
                        "issue_type": {"type": "string", "minLength": 1},
                        "browse_url": {"type": "string", "minLength": 1, "format": "uri"},
                        "priority_map": {
                            "type": "object",
                            "additionalProperties": {"type": "string", "minLength": 1},
                        },
                        "labels": {
                            "type": "array",
                            "items": {"type": "string", "minLength": 1},
                        },
                        "fields": {"type": "object", "additionalProperties": True},
                    },
                    "additionalProperties": True,
                },
            },
        },
        "additionalProperties": True,
    },
}


def _resolve_schema(config_key: str) -> Dict[str, Any]:
    """Return the JSON schema associated with a configuration key."""
    key = (config_key or "").strip()
    if not key:
        return _DEFAULT_SCHEMA

    if key in _CONFIG_SCHEMAS:
        return _CONFIG_SCHEMAS[key]

    prefix = key.split(".", 1)[0]
    if prefix in _CONFIG_SCHEMAS:
        return _CONFIG_SCHEMAS[prefix]

    return _DEFAULT_SCHEMA


def validate_configuration_data(
    config_key: str,
    config_data: Mapping[str, Any],
) -> Dict[str, Any]:
    """
    Validate configuration payload against the registered JSON schema.

    Args:
        config_key: Identifier for the configuration.
        config_data: Payload to validate.

    Returns:
        Deep copy of the validated payload to prevent unintended mutation.

    Raises:
        ConfigurationValidationError: If validation fails or payload is not a dict.
    """
    if not isinstance(config_data, Mapping):
        raise ConfigurationValidationError(
            f"Configuration '{config_key}' failed validation: payload must be an object."
        )

    schema = _resolve_schema(config_key)
    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(config_data), key=lambda err: err.path)

    if errors:
        fragments = []
        for error in errors:
            path = "/".join(str(part) for part in error.path) or "root"
            fragments.append(f"{path}: {error.message}")
        message = "; ".join(fragments)
        raise ConfigurationValidationError(
            f"Configuration '{config_key}' failed validation: {message}"
        )

    return deepcopy(dict(config_data))
