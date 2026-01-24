"""
Test suite for WER Statistics Service.

Tests the WER aggregation reporting service which provides
WER metrics grouped by:
- Test suite
- Language
- Time period
"""

import pytest
from pathlib import Path
from datetime import date, datetime, timezone
from uuid import uuid4


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
SERVICES_DIR = PROJECT_ROOT / "backend" / "services"
WER_STATISTICS_SERVICE_FILE = SERVICES_DIR / "wer_statistics_service.py"


class TestWERStatisticsServiceFileStructure:
    """Test WER statistics service file structure"""

    def test_services_directory_exists(self):
        """Test that services directory exists"""
        assert SERVICES_DIR.exists(), "backend/services directory should exist"
        assert SERVICES_DIR.is_dir(), "services should be a directory"

    def test_wer_statistics_service_file_exists(self):
        """Test that wer_statistics_service.py exists"""
        assert WER_STATISTICS_SERVICE_FILE.exists(), (
            "wer_statistics_service.py should exist in backend/services/"
        )

    def test_service_file_has_content(self):
        """Test that service file has content"""
        content = WER_STATISTICS_SERVICE_FILE.read_text()
        assert len(content) > 0, "wer_statistics_service.py should not be empty"


class TestWERStatisticsServiceImports:
    """Test service imports"""

    def test_imports_sqlalchemy_functions(self):
        """Test that service imports SQLAlchemy aggregation functions"""
        content = WER_STATISTICS_SERVICE_FILE.read_text()
        assert "from sqlalchemy" in content, "Should import from sqlalchemy"
        assert "func" in content, "Should import func for aggregations"

    def test_imports_models(self):
        """Test that service imports required models"""
        content = WER_STATISTICS_SERVICE_FILE.read_text()
        assert "ValidationResult" in content, "Should import ValidationResult model"
        assert "TestRun" in content, "Should import TestRun model"

    def test_imports_async_session(self):
        """Test that service imports AsyncSession"""
        content = WER_STATISTICS_SERVICE_FILE.read_text()
        assert "AsyncSession" in content, "Should import AsyncSession"


class TestWERStatisticsServiceClass:
    """Test WERStatisticsService class structure"""

    def test_service_class_exists(self):
        """Test that WERStatisticsService class is defined"""
        content = WER_STATISTICS_SERVICE_FILE.read_text()
        assert "class WERStatisticsService" in content, (
            "Should define WERStatisticsService class"
        )

    def test_class_has_init_method(self):
        """Test that class has __init__ method"""
        content = WER_STATISTICS_SERVICE_FILE.read_text()
        assert "def __init__" in content, "Should have __init__ method"

    def test_init_accepts_db_session(self):
        """Test that __init__ accepts db session parameter"""
        content = WER_STATISTICS_SERVICE_FILE.read_text()
        # Should have db parameter in __init__
        init_start = content.find("def __init__")
        if init_start != -1:
            init_section = content[init_start:init_start + 200]
            assert "db" in init_section, "__init__ should accept db parameter"


class TestWERStatisticsServiceMethods:
    """Test service method definitions"""

    def test_has_get_wer_by_test_suite_method(self):
        """Test that service has get_wer_by_test_suite method"""
        content = WER_STATISTICS_SERVICE_FILE.read_text()
        assert "def get_wer_by_test_suite" in content, (
            "Should have get_wer_by_test_suite method"
        )

    def test_has_get_wer_by_language_method(self):
        """Test that service has get_wer_by_language method"""
        content = WER_STATISTICS_SERVICE_FILE.read_text()
        assert "def get_wer_by_language" in content, (
            "Should have get_wer_by_language method"
        )

    def test_has_get_wer_by_time_period_method(self):
        """Test that service has get_wer_by_time_period method"""
        content = WER_STATISTICS_SERVICE_FILE.read_text()
        assert (
            "def get_wer_by_time_period" in content or
            "def get_wer_trend" in content
        ), "Should have get_wer_by_time_period or get_wer_trend method"

    def test_methods_are_async(self):
        """Test that aggregation methods are async"""
        content = WER_STATISTICS_SERVICE_FILE.read_text()
        # Check for async def patterns
        assert "async def get_wer_by_test_suite" in content, (
            "get_wer_by_test_suite should be async"
        )
        assert "async def get_wer_by_language" in content, (
            "get_wer_by_language should be async"
        )


class TestWERStatisticsServiceMethodSignatures:
    """Test method signatures for proper parameters"""

    def test_get_wer_by_test_suite_accepts_date_params(self):
        """Test that get_wer_by_test_suite accepts date parameters"""
        content = WER_STATISTICS_SERVICE_FILE.read_text()
        method_start = content.find("def get_wer_by_test_suite")
        if method_start != -1:
            method_section = content[method_start:method_start + 500]
            assert (
                "start_date" in method_section or
                "start" in method_section
            ), "Should accept start_date parameter"

    def test_get_wer_by_language_accepts_date_params(self):
        """Test that get_wer_by_language accepts date parameters"""
        content = WER_STATISTICS_SERVICE_FILE.read_text()
        method_start = content.find("def get_wer_by_language")
        if method_start != -1:
            method_section = content[method_start:method_start + 500]
            assert (
                "start_date" in method_section or
                "start" in method_section
            ), "Should accept start_date parameter"


class TestWERStatisticsServiceAggregationQueries:
    """Test that service uses proper SQLAlchemy aggregation"""

    def test_uses_func_avg_for_average_wer(self):
        """Test that service uses func.avg for average WER"""
        content = WER_STATISTICS_SERVICE_FILE.read_text()
        assert "func.avg" in content, "Should use func.avg for average calculation"

    def test_uses_func_count_for_counting(self):
        """Test that service uses func.count for counting"""
        content = WER_STATISTICS_SERVICE_FILE.read_text()
        assert "func.count" in content, "Should use func.count for counting"

    def test_uses_func_min_for_minimum_wer(self):
        """Test that service uses func.min for minimum WER"""
        content = WER_STATISTICS_SERVICE_FILE.read_text()
        assert "func.min" in content, "Should use func.min for minimum value"

    def test_uses_func_max_for_maximum_wer(self):
        """Test that service uses func.max for maximum WER"""
        content = WER_STATISTICS_SERVICE_FILE.read_text()
        assert "func.max" in content, "Should use func.max for maximum value"

    def test_uses_group_by(self):
        """Test that service uses group_by for aggregation"""
        content = WER_STATISTICS_SERVICE_FILE.read_text()
        assert "group_by" in content, "Should use group_by for aggregation"


class TestWERStatisticsServiceFilteringLogic:
    """Test filtering logic in the service"""

    def test_filters_null_wer_scores(self):
        """Test that service filters out null WER scores"""
        content = WER_STATISTICS_SERVICE_FILE.read_text()
        assert (
            "isnot(None)" in content or
            "is_not(None)" in content or
            "!= None" in content
        ), "Should filter out null WER scores"

    def test_filters_by_date_range(self):
        """Test that service filters by date range"""
        content = WER_STATISTICS_SERVICE_FILE.read_text()
        assert (
            "created_at >=" in content or
            "created_at >=" in content.replace(" ", "") or
            "start_time" in content or
            "start_date" in content
        ), "Should filter by date range"


class TestWERStatisticsServiceJoins:
    """Test that service properly joins related tables"""

    def test_joins_test_run_table(self):
        """Test that service joins TestRun table"""
        content = WER_STATISTICS_SERVICE_FILE.read_text()
        assert (
            "join" in content.lower() and "TestRun" in content
        ), "Should join TestRun table"

    def test_joins_test_suite_table(self):
        """Test that service joins TestSuite for suite names"""
        content = WER_STATISTICS_SERVICE_FILE.read_text()
        assert "TestSuite" in content, "Should reference TestSuite for suite names"


class TestWERStatisticsServiceReturnStructure:
    """Test return value structure"""

    def test_returns_list_type(self):
        """Test that methods return List type"""
        content = WER_STATISTICS_SERVICE_FILE.read_text()
        assert "List[" in content, "Should return List type"

    def test_returns_dict_items(self):
        """Test that returned list contains dict items"""
        content = WER_STATISTICS_SERVICE_FILE.read_text()
        assert (
            "Dict[" in content or
            "dict" in content
        ), "Should return dictionaries with metrics"


class TestWERStatisticsServiceDocumentation:
    """Test service documentation"""

    def test_has_module_docstring(self):
        """Test that file has module docstring"""
        content = WER_STATISTICS_SERVICE_FILE.read_text()
        assert '"""' in content or "'''" in content, "Should have module docstring"

    def test_has_class_docstring(self):
        """Test that class has docstring"""
        content = WER_STATISTICS_SERVICE_FILE.read_text()
        class_start = content.find("class WERStatisticsService")
        if class_start != -1:
            class_section = content[class_start:class_start + 500]
            assert '"""' in class_section, "Class should have docstring"

    def test_methods_have_docstrings(self):
        """Test that methods have docstrings"""
        content = WER_STATISTICS_SERVICE_FILE.read_text()
        # Check for docstring after method definitions
        method_count = content.count("async def get_wer")
        docstring_count = content.count('"""')
        # At least one docstring per method plus class and module
        assert docstring_count >= method_count, "Methods should have docstrings"


class TestWERStatisticsServiceTypeHints:
    """Test type hints in the service"""

    def test_uses_type_hints_in_methods(self):
        """Test that methods use type hints"""
        content = WER_STATISTICS_SERVICE_FILE.read_text()
        # Check for return type hints
        assert " -> " in content, "Methods should have return type hints"

    def test_imports_typing_module(self):
        """Test that typing module is imported"""
        content = WER_STATISTICS_SERVICE_FILE.read_text()
        assert (
            "from typing import" in content or
            "import typing" in content
        ), "Should import from typing module"


class TestWERStatisticsServiceErrorHandling:
    """Test error handling in the service"""

    def test_validates_db_session(self):
        """Test that service validates db session"""
        content = WER_STATISTICS_SERVICE_FILE.read_text()
        # Should check for None db or raise error
        assert (
            "if db is None" in content or
            "raise ValueError" in content or
            "if not db" in content
        ), "Should validate db session is not None"


class TestWERStatisticsServiceCanBeImported:
    """Test that service can be imported"""

    def test_can_import_service(self):
        """Test that WERStatisticsService can be imported"""
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

        try:
            from services.wer_statistics_service import WERStatisticsService
            assert WERStatisticsService is not None
        except ImportError as e:
            pytest.fail(f"Cannot import WERStatisticsService: {e}")

    def test_can_instantiate_with_session(self):
        """Test that WERStatisticsService can be instantiated"""
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

        from services.wer_statistics_service import WERStatisticsService
        from unittest.mock import MagicMock

        mock_db = MagicMock()
        service = WERStatisticsService(mock_db)
        assert service is not None


class TestWERStatisticsServiceMetricsReturned:
    """Test that service returns expected metrics"""

    def test_includes_avg_wer_in_metrics(self):
        """Test that avg_wer is included in metrics"""
        content = WER_STATISTICS_SERVICE_FILE.read_text()
        assert "avg_wer" in content, "Should include avg_wer in metrics"

    def test_includes_min_wer_in_metrics(self):
        """Test that min_wer is included in metrics"""
        content = WER_STATISTICS_SERVICE_FILE.read_text()
        assert "min_wer" in content, "Should include min_wer in metrics"

    def test_includes_max_wer_in_metrics(self):
        """Test that max_wer is included in metrics"""
        content = WER_STATISTICS_SERVICE_FILE.read_text()
        assert "max_wer" in content, "Should include max_wer in metrics"

    def test_includes_count_in_metrics(self):
        """Test that count is included in metrics"""
        content = WER_STATISTICS_SERVICE_FILE.read_text()
        assert "count" in content, "Should include count in metrics"


class TestWERStatisticsServiceBySuiteOutput:
    """Test get_wer_by_test_suite output structure"""

    def test_includes_suite_id_in_output(self):
        """Test that suite_id is in the output"""
        content = WER_STATISTICS_SERVICE_FILE.read_text()
        assert (
            "suite_id" in content or
            "test_suite_id" in content
        ), "Should include suite_id in output"

    def test_includes_suite_name_in_output(self):
        """Test that suite_name is in the output"""
        content = WER_STATISTICS_SERVICE_FILE.read_text()
        assert (
            "suite_name" in content or
            "test_suite_name" in content
        ), "Should include suite_name in output"


class TestWERStatisticsServiceByLanguageOutput:
    """Test get_wer_by_language output structure"""

    def test_includes_language_code_in_output(self):
        """Test that language_code is in the output"""
        content = WER_STATISTICS_SERVICE_FILE.read_text()
        assert "language_code" in content, "Should include language_code in output"


class TestWERStatisticsServiceByTimePeriodOutput:
    """Test time period aggregation output"""

    def test_includes_period_in_time_output(self):
        """Test that period is in time aggregation output"""
        content = WER_STATISTICS_SERVICE_FILE.read_text()
        assert (
            "period" in content or
            "date" in content or
            "day" in content
        ), "Should include time period in output"


class TestWERStatisticsServiceUsesWerScore:
    """Test that service references wer_score field"""

    def test_references_wer_score_field(self):
        """Test that service references ValidationResult.wer_score"""
        content = WER_STATISTICS_SERVICE_FILE.read_text()
        assert "wer_score" in content, "Should reference wer_score field"

    def test_aggregates_wer_score_from_validation_result(self):
        """Test that WER score is aggregated from ValidationResult"""
        content = WER_STATISTICS_SERVICE_FILE.read_text()
        assert (
            "ValidationResult.wer_score" in content or
            "ValidationResult" in content and "wer_score" in content
        ), "Should aggregate wer_score from ValidationResult"


class TestWERStatisticsServiceLogging:
    """Test logging usage"""

    def test_imports_logging(self):
        """Test that service imports logging"""
        content = WER_STATISTICS_SERVICE_FILE.read_text()
        assert "import logging" in content, "Should import logging"

    def test_creates_logger(self):
        """Test that service creates logger"""
        content = WER_STATISTICS_SERVICE_FILE.read_text()
        assert (
            "logger = logging.getLogger" in content or
            "getLogger(__name__)" in content
        ), "Should create logger"

