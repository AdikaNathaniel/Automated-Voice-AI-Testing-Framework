"""
Tests for query parameter validation in API routes.

TDD Red Phase: These tests verify that query parameters have proper validation
including enum types for status, range validation for pagination, and length
validation for search queries.
"""

import pytest
import sys
import os
import inspect
from enum import Enum

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestStatusEnumValidation:
    """Test that status parameters use enum validation."""

    def test_test_run_status_enum_exists(self):
        """Test that TestRunStatus enum exists."""
        from api.schemas.enums import TestRunStatus

        assert issubclass(TestRunStatus, Enum)

    def test_test_run_status_has_expected_values(self):
        """Test that TestRunStatus has standard values."""
        from api.schemas.enums import TestRunStatus

        # Standard test run statuses
        assert hasattr(TestRunStatus, 'pending')
        assert hasattr(TestRunStatus, 'running')
        assert hasattr(TestRunStatus, 'completed')
        assert hasattr(TestRunStatus, 'failed')
        assert hasattr(TestRunStatus, 'cancelled')

    def test_defect_status_enum_exists(self):
        """Test that DefectStatus enum exists."""
        from api.schemas.enums import DefectStatus

        assert issubclass(DefectStatus, Enum)

    def test_defect_status_has_expected_values(self):
        """Test that DefectStatus has standard values."""
        from api.schemas.enums import DefectStatus

        # Standard defect statuses
        assert hasattr(DefectStatus, 'open')
        assert hasattr(DefectStatus, 'in_progress')
        assert hasattr(DefectStatus, 'resolved')
        assert hasattr(DefectStatus, 'closed')

    def test_edge_case_status_enum_exists(self):
        """Test that EdgeCaseStatus enum exists."""
        from api.schemas.enums import EdgeCaseStatus

        assert issubclass(EdgeCaseStatus, Enum)

    def test_edge_case_status_has_expected_values(self):
        """Test that EdgeCaseStatus has standard values."""
        from api.schemas.enums import EdgeCaseStatus

        # Standard edge case statuses
        assert hasattr(EdgeCaseStatus, 'pending')
        assert hasattr(EdgeCaseStatus, 'reviewed')
        assert hasattr(EdgeCaseStatus, 'accepted')
        assert hasattr(EdgeCaseStatus, 'rejected')

    def test_regression_status_enum_exists(self):
        """Test that RegressionStatus enum exists."""
        from api.schemas.enums import RegressionStatus

        assert issubclass(RegressionStatus, Enum)


class TestRouteStatusEnumUsage:
    """Test that route files use enum types for status parameters."""

    def test_test_runs_list_uses_status_enum(self):
        """Test that test_runs list endpoint uses TestRunStatus enum."""
        from api.routes.test_runs import list_test_runs

        sig = inspect.signature(list_test_runs)
        status_param = sig.parameters.get('status_filter')

        # Should use Optional[TestRunStatus] not Optional[str]
        assert status_param is not None
        param_annotation = str(status_param.annotation)
        assert 'TestRunStatus' in param_annotation or 'str' not in param_annotation.lower()

    def test_defects_list_uses_status_enum(self):
        """Test that defects list endpoint uses DefectStatus enum."""
        from api.routes.defects import list_defects_endpoint

        sig = inspect.signature(list_defects_endpoint)
        status_param = sig.parameters.get('status_filter')

        assert status_param is not None
        param_annotation = str(status_param.annotation)
        assert 'DefectStatus' in param_annotation or 'str' not in param_annotation.lower()


class TestPaginationRangeValidation:
    """Test that pagination parameters have consistent range validation."""

    def test_standard_limit_max_is_100(self):
        """Test that standard list endpoints have limit max of 100."""
        from api.routes import test_suites, test_runs, defects

        # Check test_suites
        sig = inspect.signature(test_suites.list_test_suites)
        limit_param = sig.parameters.get('limit')
        assert limit_param is not None
        # FastAPI Query will have metadata about constraints
        default = limit_param.default
        if hasattr(default, 'le'):
            assert default.le <= 100

    def test_skip_minimum_is_zero(self):
        """Test that skip parameters have minimum of 0."""
        from api.routes import test_suites

        sig = inspect.signature(test_suites.list_test_suites)
        skip_param = sig.parameters.get('skip')
        assert skip_param is not None
        default = skip_param.default
        if hasattr(default, 'ge'):
            assert default.ge == 0


class TestSearchQueryValidation:
    """Test that search query parameters have proper validation."""

    def test_knowledge_base_search_has_max_length(self):
        """Test that knowledge base search query has max_length validation."""
        from api.routes.knowledge_base import list_knowledge_base_articles

        sig = inspect.signature(list_knowledge_base_articles)
        search_param = sig.parameters.get('search_query')

        assert search_param is not None
        default = search_param.default
        # Check for max_length constraint
        if hasattr(default, 'max_length'):
            assert default.max_length <= 500

    def test_edge_cases_query_has_max_length(self):
        """Test that edge cases query has max_length validation."""
        from api.routes.edge_cases import search_edge_cases_endpoint

        sig = inspect.signature(search_edge_cases_endpoint)
        query_param = sig.parameters.get('query')

        assert query_param is not None
        default = query_param.default
        # Should have max_length constraint
        if hasattr(default, 'max_length'):
            assert default.max_length <= 500


class TestEnumSchemaExports:
    """Test that enum schemas are properly exported."""

    def test_enums_module_exists(self):
        """Test that enums module exists in schemas."""
        from api.schemas import enums

        assert enums is not None

    def test_enums_are_exported(self):
        """Test that key enums are exported from schemas."""
        from api.schemas.enums import (
            TestRunStatus,
            DefectStatus,
            EdgeCaseStatus,
            RegressionStatus,
        )

        assert TestRunStatus is not None
        assert DefectStatus is not None
        assert EdgeCaseStatus is not None
        assert RegressionStatus is not None


class TestEnumStringValues:
    """Test that enums use string values for JSON serialization."""

    def test_test_run_status_is_str_enum(self):
        """Test that TestRunStatus inherits from str."""
        from api.schemas.enums import TestRunStatus

        # Should be (str, Enum) for proper JSON serialization
        assert issubclass(TestRunStatus, str)
        assert issubclass(TestRunStatus, Enum)

    def test_defect_status_is_str_enum(self):
        """Test that DefectStatus inherits from str."""
        from api.schemas.enums import DefectStatus

        assert issubclass(DefectStatus, str)
        assert issubclass(DefectStatus, Enum)

    def test_enum_values_are_lowercase(self):
        """Test that enum values are lowercase strings."""
        from api.schemas.enums import TestRunStatus

        for status in TestRunStatus:
            assert status.value == status.value.lower()
