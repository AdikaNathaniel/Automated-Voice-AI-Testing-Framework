"""
Test suite for event emitter utilities (TASK-104)

Validates the event emitter utilities in backend/api/events.py:
- File structure and imports
- emit_test_run_update function
- emit_test_completed function
- emit_validation_update function
- Proper integration with Socket.IO
- Type hints and documentation
"""

import pytest
from pathlib import Path
import sys
from uuid import UUID, uuid4


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
API_DIR = BACKEND_DIR / "api"
EVENTS_FILE = API_DIR / "events.py"


class TestEventsFileExists:
    """Test that events.py exists"""

    def test_api_directory_exists(self):
        """Test that api directory exists"""
        assert API_DIR.exists(), "backend/api directory should exist"
        assert API_DIR.is_dir(), "api should be a directory"

    def test_events_file_exists(self):
        """Test that events.py exists"""
        assert EVENTS_FILE.exists(), "events.py should exist"
        assert EVENTS_FILE.is_file(), "events.py should be a file"

    def test_events_has_content(self):
        """Test that events.py has content"""
        content = EVENTS_FILE.read_text()
        assert len(content) > 0, "events.py should not be empty"


class TestEventsImports:
    """Test necessary imports"""

    @pytest.fixture
    def events_content(self):
        """Load events.py content"""
        return EVENTS_FILE.read_text()

    def test_imports_uuid(self, events_content):
        """Test that UUID is imported"""
        assert "from uuid import UUID" in events_content or "import uuid" in events_content, \
            "Should import UUID"

    def test_imports_dict_typing(self, events_content):
        """Test that Dict typing is imported"""
        assert "Dict" in events_content or "dict" in events_content, \
            "Should have dict type hints"

    def test_imports_sio_from_websocket(self, events_content):
        """Test that sio is imported from websocket module"""
        assert "from api.websocket import sio" in events_content or \
               "from .websocket import sio" in events_content, \
            "Should import sio from websocket module"


class TestEmitTestRunUpdateFunction:
    """Test emit_test_run_update function"""

    @pytest.fixture
    def events_content(self):
        """Load events.py content"""
        return EVENTS_FILE.read_text()

    def test_has_emit_test_run_update_function(self, events_content):
        """Test that emit_test_run_update function exists"""
        assert "def emit_test_run_update" in events_content, \
            "Should have emit_test_run_update function"

    def test_emit_test_run_update_is_async(self, events_content):
        """Test that emit_test_run_update is async"""
        assert "async def emit_test_run_update" in events_content, \
            "emit_test_run_update should be async"

    def test_emit_test_run_update_has_test_run_id_param(self, events_content):
        """Test that emit_test_run_update has test_run_id parameter"""
        assert "test_run_id" in events_content, \
            "Should have test_run_id parameter"

    def test_emit_test_run_update_has_data_param(self, events_content):
        """Test that emit_test_run_update has data parameter"""
        # Should accept data parameter
        lines = events_content.split('\n')
        function_found = False
        for line in lines:
            if 'def emit_test_run_update' in line:
                assert 'data' in line, \
                    "emit_test_run_update should have data parameter"
                function_found = True
                break
        assert function_found, "Should find emit_test_run_update function definition"

    def test_emit_test_run_update_has_docstring(self, events_content):
        """Test that emit_test_run_update has docstring"""
        lines = events_content.split('\n')
        function_line = None
        for i, line in enumerate(lines):
            if 'async def emit_test_run_update' in line:
                function_line = i
                break

        if function_line is not None:
            # Check next few lines for docstring
            has_docstring = False
            for i in range(function_line + 1, min(function_line + 5, len(lines))):
                if '"""' in lines[i] or "'''" in lines[i]:
                    has_docstring = True
                    break
            assert has_docstring, \
                "emit_test_run_update should have docstring"

    def test_emit_test_run_update_uses_sio_emit(self, events_content):
        """Test that emit_test_run_update uses sio.emit"""
        # Function should use sio.emit to send events
        assert "sio.emit" in events_content or "await sio.emit" in events_content, \
            "Should use sio.emit to emit events"


class TestEmitTestCompletedFunction:
    """Test emit_test_completed function"""

    @pytest.fixture
    def events_content(self):
        """Load events.py content"""
        return EVENTS_FILE.read_text()

    def test_has_emit_test_completed_function(self, events_content):
        """Test that emit_test_completed function exists"""
        assert "def emit_test_completed" in events_content, \
            "Should have emit_test_completed function"

    def test_emit_test_completed_is_async(self, events_content):
        """Test that emit_test_completed is async"""
        assert "async def emit_test_completed" in events_content, \
            "emit_test_completed should be async"

    def test_emit_test_completed_has_test_execution_id_param(self, events_content):
        """Test that emit_test_completed has test_execution_id parameter"""
        assert "test_execution_id" in events_content, \
            "Should have test_execution_id parameter"

    def test_emit_test_completed_has_data_param(self, events_content):
        """Test that emit_test_completed has data parameter"""
        lines = events_content.split('\n')
        function_found = False
        for line in lines:
            if 'def emit_test_completed' in line:
                assert 'data' in line, \
                    "emit_test_completed should have data parameter"
                function_found = True
                break
        assert function_found, "Should find emit_test_completed function definition"

    def test_emit_test_completed_has_docstring(self, events_content):
        """Test that emit_test_completed has docstring"""
        lines = events_content.split('\n')
        function_line = None
        for i, line in enumerate(lines):
            if 'async def emit_test_completed' in line:
                function_line = i
                break

        if function_line is not None:
            has_docstring = False
            for i in range(function_line + 1, min(function_line + 5, len(lines))):
                if '"""' in lines[i] or "'''" in lines[i]:
                    has_docstring = True
                    break
            assert has_docstring, \
                "emit_test_completed should have docstring"


class TestEmitValidationUpdateFunction:
    """Test emit_validation_update function"""

    @pytest.fixture
    def events_content(self):
        """Load events.py content"""
        return EVENTS_FILE.read_text()

    def test_has_emit_validation_update_function(self, events_content):
        """Test that emit_validation_update function exists"""
        assert "def emit_validation_update" in events_content, \
            "Should have emit_validation_update function"

    def test_emit_validation_update_is_async(self, events_content):
        """Test that emit_validation_update is async"""
        assert "async def emit_validation_update" in events_content, \
            "emit_validation_update should be async"

    def test_emit_validation_update_has_validation_id_param(self, events_content):
        """Test that emit_validation_update has validation_id parameter"""
        assert "validation_id" in events_content, \
            "Should have validation_id parameter"

    def test_emit_validation_update_has_data_param(self, events_content):
        """Test that emit_validation_update has data parameter"""
        lines = events_content.split('\n')
        function_found = False
        for line in lines:
            if 'def emit_validation_update' in line:
                assert 'data' in line, \
                    "emit_validation_update should have data parameter"
                function_found = True
                break
        assert function_found, "Should find emit_validation_update function definition"

    def test_emit_validation_update_has_docstring(self, events_content):
        """Test that emit_validation_update has docstring"""
        lines = events_content.split('\n')
        function_line = None
        for i, line in enumerate(lines):
            if 'async def emit_validation_update' in line:
                function_line = i
                break

        if function_line is not None:
            has_docstring = False
            for i in range(function_line + 1, min(function_line + 5, len(lines))):
                if '"""' in lines[i] or "'''" in lines[i]:
                    has_docstring = True
                    break
            assert has_docstring, \
                "emit_validation_update should have docstring"


class TestDocumentation:
    """Test documentation"""

    @pytest.fixture
    def events_content(self):
        """Load events.py content"""
        return EVENTS_FILE.read_text()

    def test_has_module_documentation(self, events_content):
        """Test that module has documentation"""
        assert '"""' in events_content or "'''" in events_content, \
            "Should have module documentation"

    def test_has_multiple_docstrings(self, events_content):
        """Test that functions have docstrings"""
        # Should have multiple docstrings for different functions
        docstring_count = events_content.count('"""')
        assert docstring_count >= 6, \
            "Should have docstrings for module and functions (at least 3 functions + module)"


class TestEventsStructure:
    """Test overall events structure"""

    @pytest.fixture
    def events_content(self):
        """Load events.py content"""
        return EVENTS_FILE.read_text()

    def test_is_valid_python(self, events_content):
        """Test that file is valid Python"""
        try:
            compile(events_content, EVENTS_FILE, 'exec')
        except SyntaxError as e:
            pytest.fail(f"events.py has syntax error: {e}")

    def test_has_all_required_functions(self, events_content):
        """Test that all required functions are present"""
        required_functions = [
            "emit_test_run_update",
            "emit_test_completed",
            "emit_validation_update"
        ]
        for function in required_functions:
            assert function in events_content, \
                f"Should have {function} function"


class TestImportability:
    """Test that events module can be imported"""

    def test_can_import_events_module(self):
        """Test that events module can be imported"""
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from api import events
            assert events is not None, \
                "events module should be importable"
        except ImportError as e:
            pytest.fail(f"Cannot import events: {e}")

    def test_can_import_emit_test_run_update(self):
        """Test that emit_test_run_update can be imported"""
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from api.events import emit_test_run_update
            assert emit_test_run_update is not None, \
                "emit_test_run_update should be importable"
        except ImportError as e:
            pytest.fail(f"Cannot import emit_test_run_update: {e}")

    def test_can_import_emit_test_completed(self):
        """Test that emit_test_completed can be imported"""
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from api.events import emit_test_completed
            assert emit_test_completed is not None, \
                "emit_test_completed should be importable"
        except ImportError as e:
            pytest.fail(f"Cannot import emit_test_completed: {e}")

    def test_can_import_emit_validation_update(self):
        """Test that emit_validation_update can be imported"""
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from api.events import emit_validation_update
            assert emit_validation_update is not None, \
                "emit_validation_update should be importable"
        except ImportError as e:
            pytest.fail(f"Cannot import emit_validation_update: {e}")


class TestFunctionSignatures:
    """Test function signatures with inspection"""

    def test_emit_test_run_update_signature(self):
        """Test emit_test_run_update signature"""
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from api.events import emit_test_run_update
            import inspect

            sig = inspect.signature(emit_test_run_update)
            params = sig.parameters

            assert 'test_run_id' in params, \
                "Should have test_run_id parameter"
            assert 'data' in params, \
                "Should have data parameter"

            # Check it's async
            assert inspect.iscoroutinefunction(emit_test_run_update), \
                "Should be async function"
        except ImportError as e:
            pytest.fail(f"Cannot import emit_test_run_update: {e}")

    def test_emit_test_completed_signature(self):
        """Test emit_test_completed signature"""
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from api.events import emit_test_completed
            import inspect

            sig = inspect.signature(emit_test_completed)
            params = sig.parameters

            assert 'test_execution_id' in params, \
                "Should have test_execution_id parameter"
            assert 'data' in params, \
                "Should have data parameter"

            # Check it's async
            assert inspect.iscoroutinefunction(emit_test_completed), \
                "Should be async function"
        except ImportError as e:
            pytest.fail(f"Cannot import emit_test_completed: {e}")

    def test_emit_validation_update_signature(self):
        """Test emit_validation_update signature"""
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from api.events import emit_validation_update
            import inspect

            sig = inspect.signature(emit_validation_update)
            params = sig.parameters

            assert 'validation_id' in params, \
                "Should have validation_id parameter"
            assert 'data' in params, \
                "Should have data parameter"

            # Check it's async
            assert inspect.iscoroutinefunction(emit_validation_update), \
                "Should be async function"
        except ImportError as e:
            pytest.fail(f"Cannot import emit_validation_update: {e}")


class TestTaskRequirements:
    """Test TASK-104 specific requirements"""

    @pytest.fixture
    def events_content(self):
        """Load events.py content"""
        return EVENTS_FILE.read_text()

    def test_task_104_emit_test_run_update(self, events_content):
        """Test TASK-104 requirement: emit_test_run_update function"""
        assert "async def emit_test_run_update" in events_content, \
            "TASK-104 requirement: Must implement emit_test_run_update"
        assert "test_run_id" in events_content and "UUID" in events_content, \
            "TASK-104 requirement: Must use UUID for test_run_id"

    def test_task_104_emit_test_completed(self, events_content):
        """Test TASK-104 requirement: emit_test_completed function"""
        assert "async def emit_test_completed" in events_content, \
            "TASK-104 requirement: Must implement emit_test_completed"
        assert "test_execution_id" in events_content, \
            "TASK-104 requirement: Must use test_execution_id parameter"

    def test_task_104_emit_validation_update(self, events_content):
        """Test TASK-104 requirement: emit_validation_update function"""
        assert "async def emit_validation_update" in events_content, \
            "TASK-104 requirement: Must implement emit_validation_update"
        assert "validation_id" in events_content, \
            "TASK-104 requirement: Must use validation_id parameter"

    def test_task_104_all_functions_complete(self, events_content):
        """Test TASK-104 requirement: All three functions implemented"""
        required_functions = [
            "emit_test_run_update",
            "emit_test_completed",
            "emit_validation_update"
        ]
        for function in required_functions:
            assert f"async def {function}" in events_content, \
                f"TASK-104 requirement: Must implement async {function}"
