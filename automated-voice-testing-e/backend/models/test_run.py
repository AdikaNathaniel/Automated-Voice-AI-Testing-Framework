"""
Backward compatibility module for TestRun.

DEPRECATED: Use models.suite_run.SuiteRun instead.

This module provides backward compatibility for code that still imports
TestRun from models.test_run. New code should import SuiteRun from
models.suite_run instead.

Example:
    # Old way (deprecated):
    from models.test_run import TestRun

    # New way (preferred):
    from models.suite_run import SuiteRun
"""

import warnings

from models.suite_run import SuiteRun

# Issue a deprecation warning when this module is imported
warnings.warn(
    "Importing TestRun from models.test_run is deprecated. "
    "Use 'from models.suite_run import SuiteRun' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Backward compatibility alias
TestRun = SuiteRun

__all__ = ['TestRun']
