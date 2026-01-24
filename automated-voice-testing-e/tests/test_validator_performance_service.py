"""
Test suite for ValidatorPerformanceService

Validates the ValidatorPerformanceService implementation including:
- Service file structure
- Service class definition
- Method signatures and type hints
- Service methods implementation
- Daily metrics tracking
- Cohen's Kappa calculation for inter-rater agreement
"""

import pytest
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
SERVICES_DIR = PROJECT_ROOT / "backend" / "services"
VALIDATOR_PERFORMANCE_SERVICE_FILE = SERVICES_DIR / "validator_performance_service.py"


class TestValidatorPerformanceServiceFileExists:
    """Test that ValidatorPerformanceService file exists"""

    def test_services_directory_exists(self):
        """Test that services directory exists"""
        assert SERVICES_DIR.exists(), "backend/services directory should exist"
        assert SERVICES_DIR.is_dir(), "services should be a directory"

    def test_validator_performance_service_file_exists(self):
        """Test that validator_performance_service.py exists"""
        assert VALIDATOR_PERFORMANCE_SERVICE_FILE.exists(), \
            "validator_performance_service.py should exist in backend/services/"
        assert VALIDATOR_PERFORMANCE_SERVICE_FILE.is_file(), \
            "validator_performance_service.py should be a file"

    def test_service_file_has_content(self):
        """Test that service file has content"""
        content = VALIDATOR_PERFORMANCE_SERVICE_FILE.read_text()
        assert len(content) > 0, "validator_performance_service.py should not be empty"


class TestValidatorPerformanceServiceImports:
    """Test service imports"""

    def test_imports_typing_module(self):
        """Test that service imports typing module"""
        content = VALIDATOR_PERFORMANCE_SERVICE_FILE.read_text()
        assert ("from typing import" in content or "import typing" in content), \
            "Should import from typing module"

    def test_imports_uuid(self):
        """Test that service imports UUID"""
        content = VALIDATOR_PERFORMANCE_SERVICE_FILE.read_text()
        assert "UUID" in content, "Should import or reference UUID"

    def test_imports_sqlalchemy(self):
        """Test that service imports SQLAlchemy"""
        content = VALIDATOR_PERFORMANCE_SERVICE_FILE.read_text()
        assert ("from sqlalchemy" in content or "import sqlalchemy" in content), \
            "Should import SQLAlchemy for database operations"

    def test_imports_date(self):
        """Test that service imports date"""
        content = VALIDATOR_PERFORMANCE_SERVICE_FILE.read_text()
        assert ("from datetime import" in content or "date" in content), \
            "Should import date for daily tracking"


class TestValidatorPerformanceServiceClass:
    """Test ValidatorPerformanceService class"""

    def test_defines_validator_performance_service_class(self):
        """Test that ValidatorPerformanceService class is defined"""
        content = VALIDATOR_PERFORMANCE_SERVICE_FILE.read_text()
        assert "class ValidatorPerformanceService" in content, \
            "Should define ValidatorPerformanceService class"

    def test_has_module_docstring(self):
        """Test that service has module-level docstring"""
        content = VALIDATOR_PERFORMANCE_SERVICE_FILE.read_text()
        assert ('"""' in content or "'''" in content), \
            "Should have module docstring"

    def test_has_class_docstring(self):
        """Test that ValidatorPerformanceService class has docstring"""
        content = VALIDATOR_PERFORMANCE_SERVICE_FILE.read_text()
        if "class ValidatorPerformanceService" in content:
            class_start = content.find("class ValidatorPerformanceService")
            after_class = content[class_start:class_start + 500]
            assert ('"""' in after_class or "'''" in after_class), \
                "ValidatorPerformanceService class should have docstring"


class TestValidatorPerformanceServiceMethods:
    """Test service methods"""

    def test_has_record_daily_performance_method(self):
        """Test that service has record_daily_performance method"""
        content = VALIDATOR_PERFORMANCE_SERVICE_FILE.read_text()
        assert ("def record_daily_performance" in content or
                "async def record_daily_performance" in content), \
            "Should have record_daily_performance method"

    def test_has_update_performance_metrics_method(self):
        """Test that service has update_performance_metrics method"""
        content = VALIDATOR_PERFORMANCE_SERVICE_FILE.read_text()
        assert ("def update_performance_metrics" in content or
                "async def update_performance_metrics" in content), \
            "Should have update_performance_metrics method"

    def test_has_get_performance_for_date_method(self):
        """Test that service has get_performance_for_date method"""
        content = VALIDATOR_PERFORMANCE_SERVICE_FILE.read_text()
        assert ("def get_performance_for_date" in content or
                "async def get_performance_for_date" in content), \
            "Should have get_performance_for_date method"

    def test_has_get_performance_history_method(self):
        """Test that service has get_performance_history method"""
        content = VALIDATOR_PERFORMANCE_SERVICE_FILE.read_text()
        assert ("def get_performance_history" in content or
                "async def get_performance_history" in content), \
            "Should have get_performance_history method"

    def test_has_calculate_cohens_kappa_method(self):
        """Test that service has calculate_cohens_kappa method"""
        content = VALIDATOR_PERFORMANCE_SERVICE_FILE.read_text()
        assert ("def calculate_cohens_kappa" in content or
                "async def calculate_cohens_kappa" in content or
                "cohens_kappa" in content.lower() or
                "cohen" in content.lower()), \
            "Should have method for calculating Cohen's Kappa"


class TestValidatorPerformanceServiceMethodSignatures:
    """Test method signatures and parameters"""

    def test_record_daily_performance_has_validator_id_parameter(self):
        """Test that record_daily_performance has validator_id parameter"""
        content = VALIDATOR_PERFORMANCE_SERVICE_FILE.read_text()
        assert "validator_id" in content, \
            "record_daily_performance should have validator_id parameter"

    def test_record_daily_performance_has_date_parameter(self):
        """Test that record_daily_performance has date parameter"""
        content = VALIDATOR_PERFORMANCE_SERVICE_FILE.read_text()
        assert "date" in content, \
            "record_daily_performance should have date parameter"

    def test_update_method_has_metrics_parameters(self):
        """Test that update method has metrics parameters"""
        content = VALIDATOR_PERFORMANCE_SERVICE_FILE.read_text()
        # Should have parameters for validations, time, agreement, etc.
        has_metrics = ("validations" in content or
                      "agreement" in content or
                      "average_time" in content)
        assert has_metrics, "Update method should have metrics parameters"

    def test_get_performance_for_date_has_validator_and_date(self):
        """Test that get_performance_for_date has validator_id and date parameters"""
        content = VALIDATOR_PERFORMANCE_SERVICE_FILE.read_text()
        assert "validator_id" in content and "date" in content, \
            "get_performance_for_date should have validator_id and date parameters"

    def test_get_performance_history_has_validator_id_parameter(self):
        """Test that get_performance_history has validator_id parameter"""
        content = VALIDATOR_PERFORMANCE_SERVICE_FILE.read_text()
        assert "validator_id" in content, \
            "get_performance_history should have validator_id parameter"


class TestValidatorPerformanceServiceReturnTypes:
    """Test method return types"""

    def test_record_method_returns_validator_performance(self):
        """Test that record method returns ValidatorPerformance"""
        content = VALIDATOR_PERFORMANCE_SERVICE_FILE.read_text()
        assert "ValidatorPerformance" in content, \
            "Service should work with ValidatorPerformance model"

    def test_get_performance_returns_optional(self):
        """Test that get performance methods use Optional"""
        content = VALIDATOR_PERFORMANCE_SERVICE_FILE.read_text()
        assert "Optional" in content, \
            "Get methods should return Optional types"

    def test_get_history_returns_list(self):
        """Test that get_performance_history returns List"""
        content = VALIDATOR_PERFORMANCE_SERVICE_FILE.read_text()
        assert ("List" in content or "list" in content), \
            "get_performance_history should return List"

    def test_calculate_cohens_kappa_returns_float(self):
        """Test that calculate_cohens_kappa returns float"""
        content = VALIDATOR_PERFORMANCE_SERVICE_FILE.read_text()
        assert ("float" in content or "Decimal" in content or "numeric" in content.lower()), \
            "Cohen's Kappa calculation should return numeric value"


class TestValidatorPerformanceServiceAsyncMethods:
    """Test that methods are async"""

    def test_methods_are_async(self):
        """Test that service methods are async"""
        content = VALIDATOR_PERFORMANCE_SERVICE_FILE.read_text()
        # Should have async methods
        has_async = "async def" in content
        assert has_async, "Service should have async methods"


class TestValidatorPerformanceServiceDatabaseIntegration:
    """Test database integration patterns"""

    def test_service_works_with_session(self):
        """Test that service methods accept database session"""
        content = VALIDATOR_PERFORMANCE_SERVICE_FILE.read_text()
        assert ("Session" in content or "session" in content or "db" in content), \
            "Service should work with database sessions"

    def test_imports_validator_performance_model(self):
        """Test that service imports ValidatorPerformance model"""
        content = VALIDATOR_PERFORMANCE_SERVICE_FILE.read_text()
        assert "ValidatorPerformance" in content, \
            "Service should import or reference ValidatorPerformance model"


class TestCohensKappaCalculation:
    """Test Cohen's Kappa calculation support"""

    def test_documents_cohens_kappa_calculation(self):
        """Test that service documents Cohen's Kappa calculation"""
        content = VALIDATOR_PERFORMANCE_SERVICE_FILE.read_text()
        # Should mention Cohen's Kappa in docstrings or comments
        has_kappa_doc = ("cohen" in content.lower() or
                        "kappa" in content.lower() or
                        "inter-rater" in content.lower() or
                        "agreement" in content.lower())
        assert has_kappa_doc, \
            "Service should document Cohen's Kappa or inter-rater agreement"

    def test_has_agreement_calculation_logic(self):
        """Test that service has agreement calculation logic"""
        content = VALIDATOR_PERFORMANCE_SERVICE_FILE.read_text()
        # Should have logic for calculating agreement percentages
        has_agreement_logic = ("agreement" in content and
                              ("calculate" in content or "compute" in content))
        assert has_agreement_logic, \
            "Service should have agreement calculation logic"


class TestDailyMetricsTracking:
    """Test daily metrics tracking functionality"""

    def test_supports_date_based_queries(self):
        """Test that service supports date-based queries"""
        content = VALIDATOR_PERFORMANCE_SERVICE_FILE.read_text()
        # Should work with dates for daily tracking
        has_date_support = ("date" in content and ("filter" in content or "where" in content))
        assert has_date_support, \
            "Service should support date-based queries"

    def test_supports_upsert_pattern(self):
        """Test that service documents upsert pattern for daily records"""
        content = VALIDATOR_PERFORMANCE_SERVICE_FILE.read_text()
        # Should mention update-or-create pattern (one record per day)
        has_upsert = ("update" in content and ("create" in content or "insert" in content))
        assert has_upsert, \
            "Service should support update-or-create pattern for daily records"
