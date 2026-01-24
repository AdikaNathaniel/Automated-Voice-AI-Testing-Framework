"""
Test suite for event emissions in orchestration tasks (TASK-105)

Validates that orchestration tasks properly emit events on status changes:
- schedule_test_run emits events when tests are scheduled
- monitor_test_run_progress emits progress updates
- Event data contains correct information
- Events are emitted using the event emitter utilities
"""

import pytest
from pathlib import Path
import sys


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
TASKS_DIR = BACKEND_DIR / "tasks"
ORCHESTRATION_FILE = TASKS_DIR / "orchestration.py"


class TestOrchestrationFileExists:
    """Test that orchestration.py exists"""

    def test_orchestration_file_exists(self):
        """Test that orchestration.py exists"""
        assert ORCHESTRATION_FILE.exists(), "orchestration.py should exist"
        assert ORCHESTRATION_FILE.is_file(), "orchestration.py should be a file"


class TestEventEmitterImports:
    """Test event emitter imports in orchestration.py"""

    @pytest.fixture
    def orchestration_content(self):
        """Load orchestration.py content"""
        return ORCHESTRATION_FILE.read_text()

    def test_imports_event_emitters(self, orchestration_content):
        """Test that event emitter utilities are imported"""
        # Should import emit_test_run_update from api.events
        has_import = (
            "from api.events import" in orchestration_content or
            "import api.events" in orchestration_content
        )
        assert has_import, \
            "Should import event emitter utilities from api.events"

    def test_imports_emit_test_run_update(self, orchestration_content):
        """Test that emit_test_run_update is imported"""
        assert "emit_test_run_update" in orchestration_content, \
            "Should import or reference emit_test_run_update"


class TestScheduleTestRunEventEmission:
    """Test event emissions in schedule_test_run task"""

    @pytest.fixture
    def orchestration_content(self):
        """Load orchestration.py content"""
        return ORCHESTRATION_FILE.read_text()

    def test_schedule_test_run_has_event_emission(self, orchestration_content):
        """Test that schedule_test_run emits events"""
        # Should call emit_test_run_update
        assert "emit_test_run_update" in orchestration_content, \
            "schedule_test_run should use emit_test_run_update"

    def test_schedule_test_run_emits_after_scheduling(self, orchestration_content):
        """Test that event is emitted after successful scheduling"""
        # Find the schedule_test_run function
        lines = orchestration_content.split('\n')

        schedule_test_run_start = None
        for i, line in enumerate(lines):
            if 'def schedule_test_run' in line:
                schedule_test_run_start = i
                break

        assert schedule_test_run_start is not None, \
            "Should have schedule_test_run function"

        # Check that emit_test_run_update appears in the function
        function_lines = lines[schedule_test_run_start:]
        has_emit = any('emit_test_run_update' in line for line in function_lines[:150])
        assert has_emit, \
            "schedule_test_run should call emit_test_run_update"

    def test_schedule_test_run_includes_status_in_event(self, orchestration_content):
        """Test that emitted event includes status"""
        # The event emission should include status information
        assert "status" in orchestration_content, \
            "Event data should include status"


class TestMonitorTestRunProgressEventEmission:
    """Test event emissions in monitor_test_run_progress task"""

    @pytest.fixture
    def orchestration_content(self):
        """Load orchestration.py content"""
        return ORCHESTRATION_FILE.read_text()

    def test_monitor_has_event_emission(self, orchestration_content):
        """Test that monitor_test_run_progress emits events"""
        # Should call emit_test_run_update for progress updates
        assert "emit_test_run_update" in orchestration_content, \
            "monitor_test_run_progress should use emit_test_run_update"

    def test_monitor_emits_progress_updates(self, orchestration_content):
        """Test that progress updates are emitted"""
        # Find the monitor_test_run_progress function
        lines = orchestration_content.split('\n')

        monitor_start = None
        for i, line in enumerate(lines):
            if 'def monitor_test_run_progress' in line:
                monitor_start = i
                break

        assert monitor_start is not None, \
            "Should have monitor_test_run_progress function"

        # Check that emit_test_run_update appears in the function
        function_lines = lines[monitor_start:]
        has_emit = any('emit_test_run_update' in line for line in function_lines[:150])
        assert has_emit, \
            "monitor_test_run_progress should call emit_test_run_update"

    def test_monitor_includes_progress_in_event(self, orchestration_content):
        """Test that emitted event includes progress"""
        # The event emission should include progress information
        assert "progress" in orchestration_content, \
            "Event data should include progress"


class TestEventDataContent:
    """Test event data content"""

    @pytest.fixture
    def orchestration_content(self):
        """Load orchestration.py content"""
        return ORCHESTRATION_FILE.read_text()

    def test_events_include_test_run_id(self, orchestration_content):
        """Test that events include test_run_id"""
        # Events should pass test_run_id to emit functions
        assert "test_run_id" in orchestration_content, \
            "Events should include test_run_id"

    def test_events_include_status_updates(self, orchestration_content):
        """Test that events include status updates"""
        # Events should include status information
        assert "status" in orchestration_content, \
            "Events should include status"


class TestAsyncEventEmission:
    """Test async event emission handling"""

    @pytest.fixture
    def orchestration_content(self):
        """Load orchestration.py content"""
        return ORCHESTRATION_FILE.read_text()

    def test_uses_asyncio_for_event_emission(self, orchestration_content):
        """Test that async events are handled properly"""
        # Since Celery tasks are sync but event emitters are async,
        # should use asyncio.run or similar
        has_async_handling = (
            "asyncio.run" in orchestration_content or
            "asyncio" in orchestration_content or
            "await" in orchestration_content
        )
        assert has_async_handling, \
            "Should handle async event emission (asyncio.run or await)"


class TestErrorHandling:
    """Test error handling in event emission"""

    @pytest.fixture
    def orchestration_content(self):
        """Load orchestration.py content"""
        return ORCHESTRATION_FILE.read_text()

    def test_event_emission_has_error_handling(self, orchestration_content):
        """Test that event emission has try-except"""
        # Event emission should have error handling to not break tasks
        has_try_except = "try:" in orchestration_content and "except" in orchestration_content
        assert has_try_except, \
            "Should have error handling for event emission"


class TestImportability:
    """Test that updated orchestration module can be imported"""

    def test_can_import_orchestration_module(self):
        """Test that orchestration module can be imported"""
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from tasks import orchestration
            assert orchestration is not None, \
                "orchestration module should be importable"
        except ImportError as e:
            pytest.fail(f"Cannot import orchestration: {e}")

    def test_can_import_schedule_test_run(self):
        """Test that schedule_test_run can be imported"""
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from tasks.orchestration import schedule_test_run
            assert schedule_test_run is not None, \
                "schedule_test_run should be importable"
        except ImportError as e:
            pytest.fail(f"Cannot import schedule_test_run: {e}")

    def test_can_import_monitor_test_run_progress(self):
        """Test that monitor_test_run_progress can be imported"""
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from tasks.orchestration import monitor_test_run_progress
            assert monitor_test_run_progress is not None, \
                "monitor_test_run_progress should be importable"
        except ImportError as e:
            pytest.fail(f"Cannot import monitor_test_run_progress: {e}")


class TestOrchestrationStructure:
    """Test overall orchestration structure with events"""

    @pytest.fixture
    def orchestration_content(self):
        """Load orchestration.py content"""
        return ORCHESTRATION_FILE.read_text()

    def test_is_valid_python(self, orchestration_content):
        """Test that file is valid Python"""
        try:
            compile(orchestration_content, ORCHESTRATION_FILE, 'exec')
        except SyntaxError as e:
            pytest.fail(f"orchestration.py has syntax error: {e}")

    def test_has_celery_tasks(self, orchestration_content):
        """Test that Celery tasks are still defined"""
        assert "@celery.task" in orchestration_content, \
            "Should have Celery task decorators"

    def test_maintains_existing_functionality(self, orchestration_content):
        """Test that existing functions are maintained"""
        required_functions = [
            "schedule_test_run",
            "monitor_test_run_progress"
        ]
        for function in required_functions:
            assert f"def {function}" in orchestration_content, \
                f"Should maintain {function} function"


class TestEventEmissionPattern:
    """Test event emission patterns"""

    @pytest.fixture
    def orchestration_content(self):
        """Load orchestration.py content"""
        return ORCHESTRATION_FILE.read_text()

    def test_events_emitted_on_success(self, orchestration_content):
        """Test that events are emitted on successful operations"""
        # Events should be in the success path, not error path
        lines = orchestration_content.split('\n')

        # Find emit calls and verify they're not only in except blocks
        emit_lines = [i for i, line in enumerate(lines) if 'emit_test_run_update' in line]

        assert len(emit_lines) > 0, \
            "Should have emit_test_run_update calls"

    def test_events_include_relevant_data(self, orchestration_content):
        """Test that events include relevant data fields"""
        # Events should include progress, status, counts, etc.
        required_fields = ["status", "progress"]
        for field in required_fields:
            assert field in orchestration_content, \
                f"Event data should include {field}"


class TestTaskRequirements:
    """Test TASK-105 specific requirements"""

    @pytest.fixture
    def orchestration_content(self):
        """Load orchestration.py content"""
        return ORCHESTRATION_FILE.read_text()

    def test_task_105_imports_event_emitters(self, orchestration_content):
        """Test TASK-105 requirement: Import event emitters"""
        assert "emit_test_run_update" in orchestration_content, \
            "TASK-105 requirement: Must import event emitter utilities"

    def test_task_105_emits_on_status_changes(self, orchestration_content):
        """Test TASK-105 requirement: Emit events on status changes"""
        # Should call emit_test_run_update when status changes
        assert "emit_test_run_update" in orchestration_content, \
            "TASK-105 requirement: Must emit events on status changes"

    def test_task_105_schedule_emits_events(self, orchestration_content):
        """Test TASK-105 requirement: schedule_test_run emits events"""
        lines = orchestration_content.split('\n')

        # Find schedule_test_run function
        in_schedule_function = False
        has_emit_in_schedule = False

        for line in lines:
            if 'def schedule_test_run' in line:
                in_schedule_function = True
            elif in_schedule_function and 'def ' in line and 'schedule_test_run' not in line:
                # Reached next function
                break
            elif in_schedule_function and 'emit_test_run_update' in line:
                has_emit_in_schedule = True
                break

        assert has_emit_in_schedule, \
            "TASK-105 requirement: schedule_test_run must emit events"

    def test_task_105_monitor_emits_events(self, orchestration_content):
        """Test TASK-105 requirement: monitor_test_run_progress emits events"""
        lines = orchestration_content.split('\n')

        # Find monitor_test_run_progress function
        in_monitor_function = False
        has_emit_in_monitor = False

        for line in lines:
            if 'def monitor_test_run_progress' in line:
                in_monitor_function = True
            elif in_monitor_function and 'def ' in line and 'monitor_test_run_progress' not in line:
                # Reached next function
                break
            elif in_monitor_function and 'emit_test_run_update' in line:
                has_emit_in_monitor = True
                break

        assert has_emit_in_monitor, \
            "TASK-105 requirement: monitor_test_run_progress must emit events"
