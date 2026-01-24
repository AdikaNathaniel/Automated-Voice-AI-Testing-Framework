"""
Celery Tasks Module

This module contains all Celery task definitions for the Voice AI Testing Framework.
Tasks are organized into three main categories:

- orchestration: High-level test orchestration and coordination
- execution: Individual test case execution
- validation: Test result validation and reporting

Usage:
    from tasks import orchestration, execution, validation
    from tasks.orchestration import create_test_run
    from tasks.execution import execute_test_case
    from tasks.validation import validate_test_results
"""

# Import celery app to make it available to task modules
from celery_app import celery

# Import task modules for easy access
from . import orchestration
from . import execution
from . import validation
from . import worker_scaling
from . import reporting
from . import regression

# Export commonly used tasks
__all__ = [
    'celery',
    'orchestration',
    'execution',
    'validation',
    'worker_scaling',
    'reporting',
    'regression',
]
