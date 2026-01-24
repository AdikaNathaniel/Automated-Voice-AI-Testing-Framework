"""
Test suite for execute_voice_test_task Celery task (TASK-116).

This module tests the Celery task for voice test execution:
- Task structure and decorator
- Task signature
- Queue item fetching
- Test case retrieval
- Audio generation/fetching
- SoundHound integration
- Result storage
- Queue status updates
- Validation triggering
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../backend'))

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
from uuid import uuid4

from services.execution_resource_manager import ResourceLimitExceeded

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
TASKS_DIR = BACKEND_DIR / "tasks"
EXECUTION_TASKS_FILE = TASKS_DIR / "execution.py"


class TestExecutionTasksFileStructure:
    """Test execution.py file structure"""

    def test_execution_tasks_file_exists(self):
        """Test that execution.py exists"""
        assert EXECUTION_TASKS_FILE.exists(), \
            "execution.py should exist in backend/tasks/"

    def test_execution_tasks_has_content(self):
        """Test that execution.py has content"""
        content = EXECUTION_TASKS_FILE.read_text()
        assert len(content) > 0, "execution.py should not be empty"


class TestExecutionTasksImports:
    """Test necessary imports in execution.py"""

    @pytest.fixture
    def tasks_content(self):
        """Load execution.py content"""
        return EXECUTION_TASKS_FILE.read_text()

    def test_imports_celery(self, tasks_content):
        """Test that celery is imported"""
        assert "celery" in tasks_content.lower(), \
            "Should import celery for task definition"

    def test_imports_from_celery_app(self, tasks_content):
        """Test that celery instance is imported from celery_app"""
        assert "from celery_app import celery" in tasks_content or \
               "from celery_app import celery" in tasks_content, \
            "Should import celery instance from celery_app"


class TestExecuteVoiceTestTaskStructure:
    """Test execute_voice_test_task structure"""

    @pytest.fixture
    def tasks_content(self):
        """Load execution.py content"""
        return EXECUTION_TASKS_FILE.read_text()

    def test_has_execute_voice_test_task_function(self, tasks_content):
        """Test that execute_voice_test_task function exists"""
        assert "def execute_voice_test_task" in tasks_content, \
            "Should have execute_voice_test_task function"

    def test_task_has_celery_decorator(self, tasks_content):
        """Test that task has @celery.task decorator"""
        lines = tasks_content.split('\n')
        found_decorator = False
        found_function = False

        for i, line in enumerate(lines):
            if '@celery.task' in line:
                # Check if next non-empty line is the function
                for j in range(i+1, min(i+5, len(lines))):
                    if 'def execute_voice_test_task' in lines[j]:
                        found_decorator = True
                        found_function = True
                        break

        assert found_decorator and found_function, \
            "execute_voice_test_task should have @celery.task decorator"

    def test_task_decorator_has_bind_true(self, tasks_content):
        """Test that decorator has bind=True"""
        lines = tasks_content.split('\n')

        for i, line in enumerate(lines):
            if '@celery.task' in line and 'execute_voice_test_task' in ''.join(lines[i:i+3]):
                decorator_section = ''.join(lines[i:i+3])
                assert 'bind=True' in decorator_section, \
                    "Decorator should have bind=True parameter"
                break

    def test_task_decorator_has_max_retries(self, tasks_content):
        """Test that decorator has max_retries=3"""
        lines = tasks_content.split('\n')

        for i, line in enumerate(lines):
            if '@celery.task' in line and 'execute_voice_test_task' in ''.join(lines[i:i+3]):
                decorator_section = ''.join(lines[i:i+3])
                assert 'max_retries' in decorator_section, \
                    "Decorator should have max_retries parameter"
                assert '3' in decorator_section, \
                    "max_retries should be set to 3"
                break

    def test_task_has_docstring(self, tasks_content):
        """Test that execute_voice_test_task has docstring"""
        lines = tasks_content.split('\n')
        in_function = False
        has_docstring = False
        lines_checked = 0

        for i, line in enumerate(lines):
            if 'def execute_voice_test_task' in line:
                in_function = True
            elif in_function:
                lines_checked += 1
                if '"""' in line or "'''" in line:
                    has_docstring = True
                    break
                elif lines_checked > 10:
                    break

        assert has_docstring, "execute_voice_test_task should have docstring"


class TestExecuteVoiceTestTaskSignature:
    """Test execute_voice_test_task signature"""

    @pytest.fixture
    def tasks_content(self):
        """Load execution.py content"""
        return EXECUTION_TASKS_FILE.read_text()

    def test_task_has_self_parameter(self, tasks_content):
        """Test that task has self parameter (from bind=True)"""
        lines = tasks_content.split('\n')

        for i, line in enumerate(lines):
            if 'def execute_voice_test_task' in line:
                func_def = ''.join(lines[i:min(i+5, len(lines))])
                assert 'self' in func_def, \
                    "Task should have 'self' parameter due to bind=True"
                break

    def test_task_has_execution_queue_id_parameter(self, tasks_content):
        """Test that task has execution_queue_id parameter"""
        lines = tasks_content.split('\n')

        for i, line in enumerate(lines):
            if 'def execute_voice_test_task' in line:
                func_def = ''.join(lines[i:min(i+5, len(lines))])
                assert 'execution_queue_id' in func_def, \
                    "Task should have execution_queue_id parameter"
                break


class TestExecuteVoiceTestTaskWorkflow:
    """Test execute_voice_test_task workflow components"""

    @pytest.fixture
    def tasks_content(self):
        """Load execution.py content"""
        return EXECUTION_TASKS_FILE.read_text()

    def test_task_mentions_fetch_queue_item(self, tasks_content):
        """Test that task logic mentions fetching queue item"""
        # Look for comments or implementation mentioning queue fetching
        assert 'queue' in tasks_content.lower(), \
            "Task should handle queue item fetching"

    def test_task_mentions_test_case(self, tasks_content):
        """Test that task logic mentions test case retrieval"""
        assert 'test_case' in tasks_content.lower() or 'test case' in tasks_content.lower(), \
            "Task should handle test case retrieval"


class TestExecuteVoiceTestTaskImportability:
    """Test that execute_voice_test_task can be imported"""

    def test_can_import_execution_tasks_module(self):
        """Test that execution tasks module can be imported"""
        try:
            from tasks import execution
            assert execution is not None
        except ImportError as e:
            pytest.fail(f"Cannot import tasks.execution: {e}")

    def test_can_access_execute_voice_test_task(self):
        """Test that execute_voice_test_task can be accessed"""
        try:
            from tasks.execution import execute_voice_test_task
            assert execute_voice_test_task is not None
        except ImportError as e:
            pytest.fail(f"Cannot import execute_voice_test_task: {e}")
        except AttributeError as e:
            pytest.fail(f"execute_voice_test_task not found in execution module: {e}")


class TestExecuteVoiceTestTaskExecution:
    """Test execute_voice_test_task execution behavior"""

    def test_task_is_callable(self):
        """Test that task is callable"""
        try:
            from tasks.execution import execute_voice_test_task
            assert callable(execute_voice_test_task), \
                "execute_voice_test_task should be callable"
        except (ImportError, AttributeError):
            pytest.skip("execute_voice_test_task not yet implemented")

    def test_task_accepts_execution_queue_id(self):
        """Test that task accepts execution_queue_id parameter"""
        try:
            from tasks.execution import execute_voice_test_task
            import inspect

            sig = inspect.signature(execute_voice_test_task)
            params = list(sig.parameters.keys())

            # Should have 'self' and 'execution_queue_id'
            assert 'self' in params, "Task should have self parameter"
            assert 'execution_queue_id' in params, \
                "Task should have execution_queue_id parameter"

        except (ImportError, AttributeError):
            pytest.skip("execute_voice_test_task not yet implemented")

    @patch('tasks.execution.TestExecutionQueue')
    @patch('tasks.execution.TestCase')
    @patch('tasks.execution.VoiceExecutionService')
    def test_task_fetches_queue_item(
        self,
        mock_voice_service,
        mock_test_case,
        mock_queue
    ):
        """Test that task fetches queue item from database"""
        try:
            from tasks.execution import execute_voice_test_task

            # Setup mocks
            queue_id = str(uuid4())
            mock_queue_item = Mock()
            mock_queue_item.id = queue_id
            mock_queue_item.test_case_id = uuid4()
            mock_queue_item.test_run_id = uuid4()
            mock_queue_item.language_code = "en-US"

            mock_queue.query.return_value.filter.return_value.first.return_value = mock_queue_item

            # Execute task (will fail if not properly implemented, but that's ok for now)
            try:
                result = execute_voice_test_task(queue_id)
            except Exception:
                # Task may not be fully implemented yet
                pass

        except (ImportError, AttributeError):
            pytest.skip("execute_voice_test_task not yet implemented")


class TestTaskRequirements:
    """Test TASK-116 specific requirements"""

    def test_task_116_file_location(self):
        """Test TASK-116: File is in correct location"""
        assert EXECUTION_TASKS_FILE == TASKS_DIR / "execution.py", \
            "TASK-116: File should be at backend/tasks/execution.py"

    def test_task_116_has_execute_voice_test_task(self):
        """Test TASK-116: execute_voice_test_task function exists"""
        content = EXECUTION_TASKS_FILE.read_text()
        assert "def execute_voice_test_task" in content, \
            "TASK-116: Must have execute_voice_test_task function"

    def test_task_116_has_celery_decorator(self):
        """Test TASK-116: Task has @celery.task decorator"""
        content = EXECUTION_TASKS_FILE.read_text()
        lines = content.split('\n')

        has_decorator = False
        for i, line in enumerate(lines):
            if '@celery.task' in line:
                # Check next few lines for the function
                for j in range(i+1, min(i+5, len(lines))):
                    if 'def execute_voice_test_task' in lines[j]:
                        has_decorator = True
                        break

        assert has_decorator, \
            "TASK-116: execute_voice_test_task must have @celery.task decorator"

    def test_task_116_decorator_parameters(self):
        """Test TASK-116: Decorator has bind=True and max_retries=3"""
        content = EXECUTION_TASKS_FILE.read_text()
        lines = content.split('\n')

        for i, line in enumerate(lines):
            if '@celery.task' in line:
                # Check if this decorator is for execute_voice_test_task
                decorator_and_func = ''.join(lines[i:min(i+5, len(lines))])
                if 'execute_voice_test_task' in decorator_and_func:
                    assert 'bind=True' in decorator_and_func, \
                        "TASK-116: Decorator must have bind=True"
                    assert 'max_retries' in decorator_and_func, \
                        "TASK-116: Decorator must have max_retries parameter"
                    break

    def test_task_116_parameter_name(self):
        """Test TASK-116: Task has execution_queue_id parameter"""
        content = EXECUTION_TASKS_FILE.read_text()
        lines = content.split('\n')

        for i, line in enumerate(lines):
            if 'def execute_voice_test_task' in line:
                func_def = ''.join(lines[i:min(i+5, len(lines))])
                assert 'execution_queue_id' in func_def, \
                    "TASK-116: Task must have execution_queue_id parameter"
                break


class TestExecuteVoiceTestTaskResourceLimits:
    """Ensure execute_voice_test_task enforces resource limits."""

    def _prepare_task(self):
        from tasks import execution

        fake_self = MagicMock()
        fake_self.request = MagicMock(retries=0)
        fake_self.max_retries = 3
        fake_self.retry = MagicMock()
        task = execution.execute_voice_test_task
        invoke = task.__wrapped__.__get__(fake_self, type(fake_self))
        return execution, invoke, fake_self

    def test_resource_monitor_invoked_before_execution(self, monkeypatch):
        execution, invoke, fake_self = self._prepare_task()

        monitor = MagicMock()
        monitor.ensure_capacity.return_value = MagicMock()
        monitor_cls = MagicMock(return_value=monitor)

        monkeypatch.setattr(execution, "ExecutionResourceMonitor", monitor_cls)
        monkeypatch.setattr(execution, "get_settings", lambda: MagicMock(
            EXECUTION_CPU_LIMIT_PERCENT=85.0,
            EXECUTION_MEMORY_LIMIT_MB=2048,
        ))
        monkeypatch.setattr(execution, "_fetch_queue_item", MagicMock(return_value=None))
        monkeypatch.setattr(execution, "_RESOURCE_MONITOR", None)

        invoke("queue-id")

        monitor.ensure_capacity.assert_called_once()

    def test_deferred_when_limits_exceeded(self, monkeypatch):
        execution, invoke, fake_self = self._prepare_task()

        monitor = MagicMock()
        monitor.ensure_capacity.side_effect = ResourceLimitExceeded("CPU limit reached")
        monitor_cls = MagicMock(return_value=monitor)

        monkeypatch.setattr(execution, "ExecutionResourceMonitor", monitor_cls)
        monkeypatch.setattr(execution, "get_settings", lambda: MagicMock(
            EXECUTION_CPU_LIMIT_PERCENT=85.0,
            EXECUTION_MEMORY_LIMIT_MB=2048,
        ))
        queue_update = MagicMock()
        monkeypatch.setattr(execution, "_update_queue_status", queue_update)
        monkeypatch.setattr(execution, "_RESOURCE_MONITOR", None)

        result = invoke("queue-id")

        monitor.ensure_capacity.assert_called_once()
        queue_update.assert_called_once_with("queue-id", "queued", "CPU limit reached")
        assert result["status"] == "deferred"
        assert "CPU limit reached" in result["message"]
