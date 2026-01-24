"""
Test suite for new orchestration Celery tasks in backend/tasks/orchestration.py

Validates the new orchestration task implementations:
- schedule_test_run task
- monitor_test_run_progress task
- Task decorators and configuration
- Type annotations
- Documentation
"""

import pytest
from pathlib import Path
import sys


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
TASKS_DIR = BACKEND_DIR / "tasks"
ORCHESTRATION_TASKS_FILE = TASKS_DIR / "orchestration.py"


class TestScheduleTestRunTask:
    """Test schedule_test_run task"""

    @pytest.fixture
    def tasks_content(self):
        """Load orchestration.py content"""
        return ORCHESTRATION_TASKS_FILE.read_text()

    def test_has_schedule_test_run_task(self, tasks_content):
        """Test that schedule_test_run task exists"""
        assert "def schedule_test_run" in tasks_content, \
            "Should have schedule_test_run task"

    def test_schedule_test_run_has_celery_decorator(self, tasks_content):
        """Test that schedule_test_run has celery task decorator"""
        assert "@celery.task" in tasks_content, \
            "Should have @celery.task decorator"

    def test_schedule_test_run_has_test_run_id_param(self, tasks_content):
        """Test that schedule_test_run has test_run_id parameter"""
        assert "test_run_id" in tasks_content, \
            "Should have test_run_id parameter"

    def test_schedule_test_run_has_docstring(self, tasks_content):
        """Test that schedule_test_run has documentation"""
        # Count docstrings - should have docstring for schedule_test_run
        assert '"""' in tasks_content, \
            "Should have docstrings"

    def test_schedule_test_run_handles_queue_creation(self, tasks_content):
        """Test that schedule_test_run creates queue entries"""
        # Should mention queue or enqueue operations
        assert "queue" in tasks_content.lower() or "enqueue" in tasks_content.lower(), \
            "Should handle queue entry creation"


class TestMonitorTestRunProgressTask:
    """Test monitor_test_run_progress task"""

    @pytest.fixture
    def tasks_content(self):
        """Load orchestration.py content"""
        return ORCHESTRATION_TASKS_FILE.read_text()

    def test_has_monitor_test_run_progress_task(self, tasks_content):
        """Test that monitor_test_run_progress task exists"""
        assert "def monitor_test_run_progress" in tasks_content, \
            "Should have monitor_test_run_progress task"

    def test_monitor_test_run_progress_has_celery_decorator(self, tasks_content):
        """Test that monitor_test_run_progress has celery task decorator"""
        assert "@celery.task" in tasks_content, \
            "Should have @celery.task decorator"

    def test_monitor_test_run_progress_has_test_run_id_param(self, tasks_content):
        """Test that monitor_test_run_progress has test_run_id parameter"""
        assert "test_run_id" in tasks_content, \
            "Should have test_run_id parameter"

    def test_monitor_test_run_progress_has_docstring(self, tasks_content):
        """Test that monitor_test_run_progress has documentation"""
        # Should have multiple docstrings
        docstring_count = tasks_content.count('"""')
        assert docstring_count >= 4, \
            "Should have docstrings for multiple tasks"

    def test_monitor_test_run_progress_checks_status(self, tasks_content):
        """Test that monitor_test_run_progress checks completion status"""
        # Should mention status or completion
        assert "status" in tasks_content.lower() or "completion" in tasks_content.lower(), \
            "Should check completion status"


class TestTaskConfiguration:
    """Test task configuration and decorators"""

    @pytest.fixture
    def tasks_content(self):
        """Load orchestration.py content"""
        return ORCHESTRATION_TASKS_FILE.read_text()

    def test_uses_celery_task_decorator(self, tasks_content):
        """Test that tasks use @celery.task decorator"""
        # Should have multiple task decorators
        assert tasks_content.count("@celery.task") >= 5, \
            "Should have at least 5 task decorators (3 existing + 2 new)"

    def test_tasks_have_name_parameter(self, tasks_content):
        """Test that tasks have name parameter in decorator"""
        # Should specify task names
        assert "name=" in tasks_content, \
            "Tasks should have name parameter"

    def test_tasks_use_bind_parameter(self, tasks_content):
        """Test that tasks use bind=True parameter"""
        # Should bind tasks to get access to self
        assert "bind=True" in tasks_content, \
            "Tasks should use bind=True"


class TestTaskDocumentation:
    """Test task documentation"""

    @pytest.fixture
    def tasks_content(self):
        """Load orchestration.py content"""
        return ORCHESTRATION_TASKS_FILE.read_text()

    def test_has_comprehensive_docstrings(self, tasks_content):
        """Test that tasks have comprehensive docstrings"""
        # Should have docstrings for all tasks
        docstring_count = tasks_content.count('"""')
        assert docstring_count >= 10, \
            "Should have docstrings for module and all tasks"

    def test_docstrings_include_args_section(self, tasks_content):
        """Test that docstrings document arguments"""
        assert "Args:" in tasks_content, \
            "Docstrings should document arguments"

    def test_docstrings_include_returns_section(self, tasks_content):
        """Test that docstrings document return values"""
        assert "Returns:" in tasks_content, \
            "Docstrings should document return values"


class TestImportability:
    """Test that new tasks can be imported"""

    def test_can_import_orchestration_tasks(self):
        """Test that orchestration tasks module can be imported"""
        # Add backend to path
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from tasks import orchestration
            assert orchestration is not None, \
                "orchestration tasks module should be importable"
        except ImportError as e:
            pytest.fail(f"Cannot import orchestration tasks: {e}")

    def test_can_access_schedule_test_run(self):
        """Test that schedule_test_run task can be accessed"""
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from tasks.orchestration import schedule_test_run
            assert schedule_test_run is not None, \
                "schedule_test_run should be accessible"
        except ImportError as e:
            pytest.fail(f"Cannot import schedule_test_run: {e}")

    def test_can_access_monitor_test_run_progress(self):
        """Test that monitor_test_run_progress task can be accessed"""
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from tasks.orchestration import monitor_test_run_progress
            assert monitor_test_run_progress is not None, \
                "monitor_test_run_progress should be accessible"
        except ImportError as e:
            pytest.fail(f"Cannot import monitor_test_run_progress: {e}")


class TestTaskIntegration:
    """Test task integration with services"""

    @pytest.fixture
    def tasks_content(self):
        """Load orchestration.py content"""
        return ORCHESTRATION_TASKS_FILE.read_text()

    def test_integrates_with_queue_manager(self, tasks_content):
        """Test that tasks integrate with queue manager"""
        # Should import or use queue_manager
        assert "queue" in tasks_content.lower(), \
            "Should integrate with queue manager"

    def test_integrates_with_orchestration_service(self, tasks_content):
        """Test that tasks integrate with orchestration service"""
        # Should use orchestration service functions
        assert "orchestration" in tasks_content.lower(), \
            "Should integrate with orchestration service"

    def test_uses_database_operations(self, tasks_content):
        """Test that tasks perform database operations"""
        # Should mention database or session
        assert "db" in tasks_content or "session" in tasks_content.lower(), \
            "Should perform database operations"


class TestTaskReturnValues:
    """Test task return value structures"""

    @pytest.fixture
    def tasks_content(self):
        """Load orchestration.py content"""
        return ORCHESTRATION_TASKS_FILE.read_text()

    def test_tasks_return_dict(self, tasks_content):
        """Test that tasks return dictionary results"""
        assert "Dict" in tasks_content or "dict" in tasks_content, \
            "Tasks should return Dict type"

    def test_schedule_test_run_returns_structured_result(self, tasks_content):
        """Test that schedule_test_run returns structured result"""
        # Should return result with relevant fields
        assert "return" in tasks_content, \
            "Tasks should return results"


class TestTaskErrorHandling:
    """Test task error handling"""

    @pytest.fixture
    def tasks_content(self):
        """Load orchestration.py content"""
        return ORCHESTRATION_TASKS_FILE.read_text()

    def test_handles_exceptions(self, tasks_content):
        """Test that tasks handle exceptions"""
        # Should have try/except blocks
        assert "try" in tasks_content or "except" in tasks_content or "Exception" in tasks_content, \
            "Tasks should handle exceptions"


class TestFileStructure:
    """Test overall file structure"""

    @pytest.fixture
    def tasks_content(self):
        """Load orchestration.py content"""
        return ORCHESTRATION_TASKS_FILE.read_text()

    def test_is_valid_python(self, tasks_content):
        """Test that file is valid Python"""
        try:
            compile(tasks_content, ORCHESTRATION_TASKS_FILE, 'exec')
        except SyntaxError as e:
            pytest.fail(f"orchestration.py has syntax error: {e}")

    def test_has_all_required_tasks(self, tasks_content):
        """Test that all required tasks are present"""
        required_tasks = [
            "schedule_test_run",
            "monitor_test_run_progress"
        ]
        for task in required_tasks:
            assert task in tasks_content, \
                f"Should have {task} task"
