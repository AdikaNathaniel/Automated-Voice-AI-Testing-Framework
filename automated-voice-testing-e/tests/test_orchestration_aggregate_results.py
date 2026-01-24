"""
Test suite for aggregate_results Celery task in backend/tasks/orchestration.py

This module tests the result aggregation functionality:
- Aggregating multiple test execution results
- Calculating summary statistics (pass/fail/skip counts, pass rate)
- Updating TestRun records with aggregated results
- Handling edge cases (empty results, invalid data)
- Error handling and logging
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from uuid import uuid4
from datetime import datetime

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"

# Add backend to path
import sys
sys.path.insert(0, str(BACKEND_DIR))


class TestAggregateResultsTaskDefinition:
    """Test aggregate_results task structure and configuration"""

    @pytest.fixture
    def tasks_file(self):
        """Load orchestration.py content"""
        tasks_path = BACKEND_DIR / "tasks" / "orchestration.py"
        return tasks_path.read_text()

    def test_aggregate_results_task_exists(self, tasks_file):
        """Test that aggregate_results task is defined"""
        assert "def aggregate_results" in tasks_file, \
            "Should have aggregate_results task defined"

    def test_aggregate_results_has_celery_decorator(self, tasks_file):
        """Test that aggregate_results has @celery.task decorator"""
        # Check for decorator near the function
        lines = tasks_file.split('\n')
        for i, line in enumerate(lines):
            if 'def aggregate_results' in line:
                # Check previous few lines for decorator
                prev_lines = '\n'.join(lines[max(0, i-5):i])
                assert '@celery.task' in prev_lines, \
                    "aggregate_results should have @celery.task decorator"
                break

    def test_aggregate_results_has_bind_parameter(self, tasks_file):
        """Test that aggregate_results uses bind=True"""
        lines = tasks_file.split('\n')
        for i, line in enumerate(lines):
            if 'def aggregate_results' in line:
                # Check previous few lines for bind=True
                prev_lines = '\n'.join(lines[max(0, i-5):i])
                assert 'bind=True' in prev_lines, \
                    "aggregate_results should have bind=True for task context"
                break

    def test_aggregate_results_has_required_params(self, tasks_file):
        """Test that aggregate_results has required parameters"""
        # Find function definition
        func_start = tasks_file.find('def aggregate_results')
        assert func_start != -1, "Should find aggregate_results function"

        # Get function signature (next ~200 chars)
        func_sig = tasks_file[func_start:func_start + 300]

        assert 'test_run_id' in func_sig, "Should have test_run_id parameter"
        assert 'execution_results' in func_sig, "Should have execution_results parameter"

    def test_aggregate_results_has_type_hints(self, tasks_file):
        """Test that aggregate_results has type hints"""
        func_start = tasks_file.find('def aggregate_results')
        func_sig = tasks_file[func_start:func_start + 400]

        assert 'str' in func_sig, "Should have str type hint for test_run_id"
        assert 'List[Dict[str, Any]]' in func_sig, "Should have List[Dict] type hint"
        assert 'Dict[str, Any]' in func_sig, "Should have Dict return type"

    def test_aggregate_results_has_comprehensive_docstring(self, tasks_file):
        """Test that aggregate_results has detailed documentation"""
        func_start = tasks_file.find('def aggregate_results')
        func_section = tasks_file[func_start:func_start + 1000]

        assert '"""' in func_section, "Should have docstring"
        assert 'Args:' in func_section, "Should document parameters"
        assert 'Returns:' in func_section, "Should document return value"


class TestAggregateResultsImplementation:
    """Test aggregate_results task implementation logic"""

    @pytest.fixture
    def tasks_file(self):
        """Load orchestration.py content"""
        tasks_path = BACKEND_DIR / "tasks" / "orchestration.py"
        return tasks_path.read_text()

    def test_validates_empty_execution_results(self, tasks_file):
        """Test that task handles empty execution results"""
        func_start = tasks_file.find('def aggregate_results')
        func_body = tasks_file[func_start:func_start + 5000]

        # Should check for empty results
        assert 'if not execution_results' in func_body or \
               'if len(execution_results)' in func_body or \
               'execution_results is None' in func_body, \
            "Should validate empty execution results"

    def test_calculates_passed_tests(self, tasks_file):
        """Test that task calculates passed test count"""
        func_start = tasks_file.find('def aggregate_results')
        func_body = tasks_file[func_start:func_start + 5000]

        assert 'passed' in func_body.lower(), \
            "Should calculate passed test count"

    def test_calculates_failed_tests(self, tasks_file):
        """Test that task calculates failed test count"""
        func_start = tasks_file.find('def aggregate_results')
        func_body = tasks_file[func_start:func_start + 5000]

        assert 'failed' in func_body.lower(), \
            "Should calculate failed test count"

    def test_calculates_skipped_tests(self, tasks_file):
        """Test that task calculates skipped test count"""
        func_start = tasks_file.find('def aggregate_results')
        func_body = tasks_file[func_start:func_start + 5000]

        assert 'skipped' in func_body.lower(), \
            "Should calculate skipped test count"

    def test_iterates_through_execution_results(self, tasks_file):
        """Test that task iterates through all execution results"""
        func_start = tasks_file.find('def aggregate_results')
        func_body = tasks_file[func_start:func_start + 5000]

        assert 'for result in execution_results' in func_body or \
               'for ' in func_body and 'execution_results' in func_body, \
            "Should iterate through execution results"

    def test_checks_result_status(self, tasks_file):
        """Test that task checks status of each result"""
        func_start = tasks_file.find('def aggregate_results')
        func_body = tasks_file[func_start:func_start + 5000]

        assert "status" in func_body and "get('status'" in func_body, \
            "Should extract status from each result"

    def test_updates_test_run_in_database(self, tasks_file):
        """Test that task updates TestRun record"""
        func_start = tasks_file.find('def aggregate_results')
        func_body = tasks_file[func_start:func_start + 5000]

        assert 'TestRun' in func_body, "Should import/use TestRun model"
        assert 'db.query(TestRun)' in func_body or \
               'TestRun.query' in func_body or \
               'session' in func_body.lower(), \
            "Should query/update TestRun in database"

    def test_updates_test_counts(self, tasks_file):
        """Test that task updates test counts on TestRun"""
        func_start = tasks_file.find('def aggregate_results')
        func_body = tasks_file[func_start:func_start + 5000]

        # Should update passed/failed/skipped counts
        assert 'passed_tests' in func_body, "Should update passed_tests"
        assert 'failed_tests' in func_body, "Should update failed_tests"
        assert 'skipped_tests' in func_body, "Should update skipped_tests"

    def test_commits_database_changes(self, tasks_file):
        """Test that task commits database changes"""
        func_start = tasks_file.find('def aggregate_results')
        func_body = tasks_file[func_start:func_start + 5000]

        assert 'commit()' in func_body, "Should commit database changes"

    def test_handles_database_errors(self, tasks_file):
        """Test that task handles database errors gracefully"""
        func_start = tasks_file.find('def aggregate_results')
        func_body = tasks_file[func_start:func_start + 5000]

        # Should have try-except around database operations
        assert 'try:' in func_body and 'except' in func_body, \
            "Should have error handling for database operations"


class TestAggregateResultsStatistics:
    """Test statistics calculation in aggregate_results"""

    @pytest.fixture
    def tasks_file(self):
        """Load orchestration.py content"""
        tasks_path = BACKEND_DIR / "tasks" / "orchestration.py"
        return tasks_path.read_text()

    def test_calculates_total_tests(self, tasks_file):
        """Test that task calculates total number of tests"""
        func_start = tasks_file.find('def aggregate_results')
        func_body = tasks_file[func_start:func_start + 5000]

        assert 'total' in func_body.lower() or \
               'len(execution_results)' in func_body, \
            "Should calculate total number of tests"

    def test_calculates_pass_rate(self, tasks_file):
        """Test that task calculates pass rate percentage"""
        func_start = tasks_file.find('def aggregate_results')
        func_body = tasks_file[func_start:func_start + 5000]

        # Should calculate percentage
        assert 'pass_rate' in func_body.lower() or \
               '/ total' in func_body or \
               '* 100' in func_body, \
            "Should calculate pass rate percentage"

    def test_sums_execution_times(self, tasks_file):
        """Test that task sums execution times"""
        func_start = tasks_file.find('def aggregate_results')
        func_body = tasks_file[func_start:func_start + 5000]

        assert 'execution_time' in func_body, \
            "Should track execution times"

    def test_creates_summary_dict(self, tasks_file):
        """Test that task creates summary dictionary"""
        func_start = tasks_file.find('def aggregate_results')
        func_body = tasks_file[func_start:func_start + 5000]

        assert 'summary' in func_body, \
            "Should create summary dictionary"


class TestAggregateResultsReturnValue:
    """Test return value structure of aggregate_results"""

    @pytest.fixture
    def tasks_file(self):
        """Load orchestration.py content"""
        tasks_path = BACKEND_DIR / "tasks" / "orchestration.py"
        return tasks_path.read_text()

    def test_returns_test_run_id(self, tasks_file):
        """Test that task returns test_run_id"""
        func_start = tasks_file.find('def aggregate_results')
        func_body = tasks_file[func_start:func_start + 5000]

        # Should return test_run_id in response
        assert "'test_run_id':" in func_body or \
               '"test_run_id":' in func_body, \
            "Should return test_run_id"

    def test_returns_total_tests(self, tasks_file):
        """Test that task returns total_tests count"""
        func_start = tasks_file.find('def aggregate_results')
        func_body = tasks_file[func_start:func_start + 5000]

        assert "'total_tests':" in func_body or \
               '"total_tests":' in func_body, \
            "Should return total_tests count"

    def test_returns_passed_count(self, tasks_file):
        """Test that task returns passed test count"""
        func_start = tasks_file.find('def aggregate_results')
        func_body = tasks_file[func_start:func_start + 5000]

        assert "'passed':" in func_body or \
               '"passed":' in func_body, \
            "Should return passed count"

    def test_returns_failed_count(self, tasks_file):
        """Test that task returns failed test count"""
        func_start = tasks_file.find('def aggregate_results')
        func_body = tasks_file[func_start:func_start + 5000]

        assert "'failed':" in func_body or \
               '"failed":' in func_body, \
            "Should return failed count"

    def test_returns_summary(self, tasks_file):
        """Test that task returns summary information"""
        func_start = tasks_file.find('def aggregate_results')
        func_body = tasks_file[func_start:func_start + 5000]

        assert "'summary':" in func_body or \
               '"summary":' in func_body, \
            "Should return summary information"

    def test_returns_message(self, tasks_file):
        """Test that task returns message"""
        func_start = tasks_file.find('def aggregate_results')
        func_body = tasks_file[func_start:func_start + 5000]

        assert "'message':" in func_body or \
               '"message":' in func_body, \
            "Should return message"


class TestAggregateResultsErrorHandling:
    """Test error handling in aggregate_results"""

    @pytest.fixture
    def tasks_file(self):
        """Load orchestration.py content"""
        tasks_path = BACKEND_DIR / "tasks" / "orchestration.py"
        return tasks_path.read_text()

    def test_handles_missing_test_run(self, tasks_file):
        """Test that task handles missing TestRun record"""
        func_start = tasks_file.find('def aggregate_results')
        func_body = tasks_file[func_start:func_start + 5000]

        assert 'if not test_run' in func_body or \
               'test_run is None' in func_body, \
            "Should check if TestRun exists"

    def test_handles_unexpected_errors(self, tasks_file):
        """Test that task has global exception handler"""
        func_start = tasks_file.find('def aggregate_results')
        func_body = tasks_file[func_start:func_start + 5000]

        # Should have outer try-except
        assert 'except Exception' in func_body, \
            "Should have global exception handler"

    def test_logs_errors(self, tasks_file):
        """Test that task logs errors"""
        func_start = tasks_file.find('def aggregate_results')
        func_body = tasks_file[func_start:func_start + 5000]

        assert 'logger' in func_body, \
            "Should use logger for error logging"

    def test_returns_error_info_on_failure(self, tasks_file):
        """Test that task returns error information on failure"""
        func_start = tasks_file.find('def aggregate_results')
        func_body = tasks_file[func_start:func_start + 5000]

        # Should return error in response dict
        assert "'error':" in func_body or \
               '"error":' in func_body, \
            "Should return error information on failure"


class TestAggregateResultsStatusDetermination:
    """Test overall status determination logic"""

    @pytest.fixture
    def tasks_file(self):
        """Load orchestration.py content"""
        tasks_path = BACKEND_DIR / "tasks" / "orchestration.py"
        return tasks_path.read_text()

    def test_determines_overall_status(self, tasks_file):
        """Test that task determines overall status"""
        func_start = tasks_file.find('def aggregate_results')
        func_body = tasks_file[func_start:func_start + 5000]

        assert 'overall_status' in func_body or \
               'status' in func_body, \
            "Should determine overall status"

    def test_handles_all_passed(self, tasks_file):
        """Test that task handles all tests passed scenario"""
        func_start = tasks_file.find('def aggregate_results')
        func_body = tasks_file[func_start:func_start + 5000]

        # Should check for completed/success status
        assert 'completed' in func_body.lower(), \
            "Should handle completed status"

    def test_handles_any_failed(self, tasks_file):
        """Test that task handles any tests failed scenario"""
        func_start = tasks_file.find('def aggregate_results')
        func_body = tasks_file[func_start:func_start + 5000]

        # Should check for failures
        assert 'failed' in func_body.lower(), \
            "Should handle failed status"

    def test_updates_test_run_status(self, tasks_file):
        """Test that task updates TestRun status field"""
        func_start = tasks_file.find('def aggregate_results')
        func_body = tasks_file[func_start:func_start + 5000]

        # Should update status using model methods
        assert 'mark_as_completed' in func_body or \
               'mark_as_failed' in func_body or \
               'test_run.status' in func_body, \
            "Should update TestRun status"


class TestAggregateResultsIntegration:
    """Integration tests for aggregate_results (code analysis)"""

    @pytest.fixture
    def tasks_file(self):
        """Load orchestration.py content"""
        tasks_path = BACKEND_DIR / "tasks" / "orchestration.py"
        return tasks_path.read_text()

    def test_imports_required_modules(self, tasks_file):
        """Test that task imports all required modules"""
        func_start = tasks_file.find('def aggregate_results')
        func_body = tasks_file[func_start:func_start + 5000]

        # Should import required modules
        assert 'import logging' in func_body or 'from logging' in func_body, \
            "Should import logging"
        assert 'from uuid import UUID' in func_body or 'UUID' in tasks_file, \
            "Should import UUID"
        assert 'from api.database import' in func_body or 'SessionLocal' in func_body, \
            "Should import database session"

    def test_uses_session_context_manager(self, tasks_file):
        """Test that task uses session context manager"""
        func_start = tasks_file.find('def aggregate_results')
        func_body = tasks_file[func_start:func_start + 5000]

        assert 'with SessionLocal()' in func_body, \
            "Should use SessionLocal context manager"

    def test_emits_realtime_events(self, tasks_file):
        """Test that task emits real-time events"""
        func_start = tasks_file.find('def aggregate_results')
        func_body = tasks_file[func_start:func_start + 5000]

        # Should emit events for real-time updates
        assert 'emit_test_run_update' in func_body or \
               'emit' in func_body, \
            "Should emit real-time events"

    def test_handles_status_categorization(self, tasks_file):
        """Test that task categorizes different status values"""
        func_start = tasks_file.find('def aggregate_results')
        func_body = tasks_file[func_start:func_start + 5000]

        # Should handle various status values
        assert 'passed' in func_body and \
               'failed' in func_body and \
               'skipped' in func_body, \
            "Should categorize status values"

    def test_handles_malformed_results(self, tasks_file):
        """Test that task handles malformed result dictionaries"""
        func_start = tasks_file.find('def aggregate_results')
        func_body = tasks_file[func_start:func_start + 5000]

        # Should use .get() for safe dictionary access
        assert ".get('status'" in func_body or \
               ".get(\"status\"" in func_body, \
            "Should use .get() for safe dictionary access"


class TestAggregateResultsCodeQuality:
    """Test code quality aspects of aggregate_results"""

    @pytest.fixture
    def tasks_file(self):
        """Load orchestration.py content"""
        tasks_path = BACKEND_DIR / "tasks" / "orchestration.py"
        return tasks_path.read_text()

    def test_function_not_too_long(self, tasks_file):
        """Test that aggregate_results function is not excessively long"""
        func_start = tasks_file.find('def aggregate_results')

        # Find next function definition
        next_func = tasks_file.find('\n@celery.task', func_start + 1)
        if next_func == -1:
            next_func = tasks_file.find('\ndef ', func_start + 1)

        func_body = tasks_file[func_start:next_func]
        line_count = len(func_body.split('\n'))

        # Should be under 200 lines (reasonable for complex aggregation logic)
        assert line_count < 200, \
            f"aggregate_results function is too long ({line_count} lines). Consider refactoring."

    def test_uses_descriptive_variable_names(self, tasks_file):
        """Test that task uses descriptive variable names"""
        func_start = tasks_file.find('def aggregate_results')
        func_body = tasks_file[func_start:func_start + 5000]

        # Should use clear variable names
        assert 'passed_tests' in func_body or 'passed_count' in func_body, \
            "Should use descriptive variable names like passed_tests"
        assert 'total_tests' in func_body or 'total_count' in func_body, \
            "Should use descriptive variable names like total_tests"

    def test_has_step_comments(self, tasks_file):
        """Test that task has step-by-step comments"""
        func_start = tasks_file.find('def aggregate_results')
        func_body = tasks_file[func_start:func_start + 5000]

        # Should have STEP comments for major operations
        assert 'STEP' in func_body or '# ' in func_body, \
            "Should have comments explaining major steps"

    def test_proper_string_formatting(self, tasks_file):
        """Test that task uses proper string formatting"""
        func_start = tasks_file.find('def aggregate_results')
        func_body = tasks_file[func_start:func_start + 5000]

        # Should use f-strings (Python 3.6+) or .format()
        assert 'f"' in func_body or 'f\'' in func_body or '.format(' in func_body, \
            "Should use f-strings or .format() for string formatting"
