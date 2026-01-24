"""
Enum types for API query parameters and schema validation.

This module provides standardized enum types for status fields and other
constrained values used across the API.
"""

from enum import Enum


class SuiteRunStatus(str, Enum):
    """Status values for suite runs."""

    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


class DefectStatus(str, Enum):
    """Status values for defects."""

    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"
    closed = "closed"
    wont_fix = "wont_fix"


class EdgeCaseStatus(str, Enum):
    """Status values for edge cases."""

    pending = "pending"
    reviewed = "reviewed"
    accepted = "accepted"
    rejected = "rejected"


class RegressionStatus(str, Enum):
    """Status values for regressions."""

    detected = "detected"
    investigating = "investigating"
    confirmed = "confirmed"
    resolved = "resolved"
    false_positive = "false_positive"


class ExecutionStatus(str, Enum):
    """Status values for test executions."""

    pending = "pending"
    running = "running"
    passed = "passed"
    failed = "failed"
    error = "error"
    skipped = "skipped"


class ValidationQueueStatus(str, Enum):
    """Status values for validation queue items."""

    pending = "pending"
    claimed = "claimed"
    completed = "completed"


__all__ = [
    "SuiteRunStatus",
    "DefectStatus",
    "EdgeCaseStatus",
    "RegressionStatus",
    "ExecutionStatus",
    "ValidationQueueStatus",
]
