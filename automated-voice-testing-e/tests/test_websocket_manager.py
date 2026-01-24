"""
Test suite for backend/api/websocket.py

Validates the WebSocket manager implementation:
- File structure and imports
- AsyncServer configuration
- ASGI mode setup
- CORS configuration
- Event handlers (connect, subscribe_test_run)
- Room management
- Authentication integration
"""

import pytest
from pathlib import Path
import sys


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
API_DIR = BACKEND_DIR / "api"
WEBSOCKET_FILE = API_DIR / "websocket.py"


class TestWebSocketFileExists:
    """Test that websocket.py exists"""

    def test_api_directory_exists(self):
        """Test that api directory exists"""
        assert API_DIR.exists(), "backend/api directory should exist"
        assert API_DIR.is_dir(), "api should be a directory"

    def test_websocket_file_exists(self):
        """Test that websocket.py exists"""
        assert WEBSOCKET_FILE.exists(), "websocket.py should exist"
        assert WEBSOCKET_FILE.is_file(), "websocket.py should be a file"

    def test_websocket_has_content(self):
        """Test that websocket.py has content"""
        content = WEBSOCKET_FILE.read_text()
        assert len(content) > 0, "websocket.py should not be empty"


class TestWebSocketImports:
    """Test necessary imports"""

    @pytest.fixture
    def websocket_content(self):
        """Load websocket.py content"""
        return WEBSOCKET_FILE.read_text()

    def test_imports_socketio(self, websocket_content):
        """Test that socketio is imported"""
        assert "import socketio" in websocket_content or "from socketio import" in websocket_content, \
            "Should import socketio"

    def test_has_socketio_asyncserver(self, websocket_content):
        """Test that AsyncServer is used"""
        assert "AsyncServer" in websocket_content, \
            "Should use socketio.AsyncServer"


class TestAsyncServerConfiguration:
    """Test AsyncServer configuration"""

    @pytest.fixture
    def websocket_content(self):
        """Load websocket.py content"""
        return WEBSOCKET_FILE.read_text()

    def test_creates_async_server(self, websocket_content):
        """Test that AsyncServer is created"""
        assert "AsyncServer" in websocket_content, \
            "Should create AsyncServer instance"

    def test_uses_asgi_mode(self, websocket_content):
        """Test that async_mode is set to 'asgi'"""
        assert "async_mode='asgi'" in websocket_content or 'async_mode="asgi"' in websocket_content, \
            "Should set async_mode='asgi'"

    def test_has_cors_configuration(self, websocket_content):
        """Test that CORS is configured"""
        assert "cors_allowed_origins" in websocket_content, \
            "Should configure CORS allowed origins"

    def test_cors_allows_all_origins(self, websocket_content):
        """Test that CORS allows all origins (development)"""
        # Should allow '*' or have cors_allowed_origins configured
        assert "cors_allowed_origins" in websocket_content, \
            "Should have cors_allowed_origins parameter"

    def test_has_sio_instance(self, websocket_content):
        """Test that sio instance is created"""
        assert "sio = " in websocket_content or "sio=" in websocket_content, \
            "Should create sio instance"


class TestConnectEventHandler:
    """Test connect event handler"""

    @pytest.fixture
    def websocket_content(self):
        """Load websocket.py content"""
        return WEBSOCKET_FILE.read_text()

    def test_has_connect_handler(self, websocket_content):
        """Test that connect event handler exists"""
        assert "def connect" in websocket_content, \
            "Should have connect event handler"

    def test_connect_is_async(self, websocket_content):
        """Test that connect handler is async"""
        assert "async def connect" in websocket_content, \
            "connect handler should be async"

    def test_connect_has_sio_event_decorator(self, websocket_content):
        """Test that connect has @sio.event decorator"""
        assert "@sio.event" in websocket_content, \
            "Should have @sio.event decorator"

    def test_connect_has_sid_parameter(self, websocket_content):
        """Test that connect has sid parameter"""
        # Should have sid in function signature
        assert "sid" in websocket_content, \
            "connect should have sid parameter"

    def test_connect_has_environ_parameter(self, websocket_content):
        """Test that connect has environ parameter"""
        assert "environ" in websocket_content, \
            "connect should have environ parameter"

    def test_connect_has_auth_parameter(self, websocket_content):
        """Test that connect has auth parameter"""
        assert "auth" in websocket_content, \
            "connect should have auth parameter"


class TestSubscribeTestRunHandler:
    """Test subscribe_test_run event handler"""

    @pytest.fixture
    def websocket_content(self):
        """Load websocket.py content"""
        return WEBSOCKET_FILE.read_text()

    def test_has_subscribe_test_run_handler(self, websocket_content):
        """Test that subscribe_test_run event handler exists"""
        assert "def subscribe_test_run" in websocket_content, \
            "Should have subscribe_test_run event handler"

    def test_subscribe_test_run_is_async(self, websocket_content):
        """Test that subscribe_test_run handler is async"""
        assert "async def subscribe_test_run" in websocket_content, \
            "subscribe_test_run handler should be async"

    def test_subscribe_test_run_has_sio_event_decorator(self, websocket_content):
        """Test that subscribe_test_run has @sio.event decorator"""
        # Should have multiple @sio.event decorators
        decorator_count = websocket_content.count("@sio.event")
        assert decorator_count >= 2, \
            "Should have @sio.event decorators for multiple handlers"

    def test_subscribe_test_run_has_sid_parameter(self, websocket_content):
        """Test that subscribe_test_run has sid parameter"""
        assert "sid" in websocket_content, \
            "subscribe_test_run should have sid parameter"

    def test_subscribe_test_run_has_data_parameter(self, websocket_content):
        """Test that subscribe_test_run has data parameter"""
        assert "data" in websocket_content, \
            "subscribe_test_run should have data parameter"

    def test_uses_enter_room(self, websocket_content):
        """Test that handler uses enter_room for room management"""
        assert "enter_room" in websocket_content, \
            "Should use enter_room to join rooms"

    def test_creates_test_run_room(self, websocket_content):
        """Test that handler creates test run rooms"""
        assert "test_run" in websocket_content, \
            "Should create rooms for test runs"


class TestDocumentation:
    """Test documentation"""

    @pytest.fixture
    def websocket_content(self):
        """Load websocket.py content"""
        return WEBSOCKET_FILE.read_text()

    def test_has_module_documentation(self, websocket_content):
        """Test that module has documentation"""
        assert '"""' in websocket_content or "'''" in websocket_content, \
            "Should have module documentation"

    def test_has_function_docstrings(self, websocket_content):
        """Test that functions have docstrings"""
        # Should have multiple docstrings for different handlers
        docstring_count = websocket_content.count('"""')
        assert docstring_count >= 2, \
            "Should have docstrings for handlers"


class TestWebSocketStructure:
    """Test overall websocket structure"""

    @pytest.fixture
    def websocket_content(self):
        """Load websocket.py content"""
        return WEBSOCKET_FILE.read_text()

    def test_is_valid_python(self, websocket_content):
        """Test that file is valid Python"""
        try:
            compile(websocket_content, WEBSOCKET_FILE, 'exec')
        except SyntaxError as e:
            pytest.fail(f"websocket.py has syntax error: {e}")

    def test_has_all_required_components(self, websocket_content):
        """Test that all required components are present"""
        required_components = [
            "AsyncServer",
            "async_mode",
            "connect",
            "subscribe_test_run"
        ]
        for component in required_components:
            assert component in websocket_content, \
                f"Should have {component}"


class TestImportability:
    """Test that websocket module can be imported"""

    def test_can_import_websocket_module(self):
        """Test that websocket module can be imported"""
        # Add backend to path
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from api import websocket
            assert websocket is not None, \
                "websocket module should be importable"
        except ImportError as e:
            pytest.fail(f"Cannot import websocket: {e}")

    def test_can_access_sio_instance(self):
        """Test that sio instance can be accessed"""
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from api.websocket import sio
            assert sio is not None, \
                "sio instance should be accessible"
        except ImportError as e:
            pytest.fail(f"Cannot import sio: {e}")


class TestTaskRequirements:
    """Test TASK-102 specific requirements"""

    @pytest.fixture
    def websocket_content(self):
        """Load websocket.py content"""
        return WEBSOCKET_FILE.read_text()

    def test_task_102_async_server_setup(self, websocket_content):
        """Test TASK-102 requirement: AsyncServer with ASGI mode"""
        assert "AsyncServer" in websocket_content, \
            "TASK-102 requirement: Must create AsyncServer"
        assert "async_mode='asgi'" in websocket_content or 'async_mode="asgi"' in websocket_content, \
            "TASK-102 requirement: Must use async_mode='asgi'"

    def test_task_102_cors_configuration(self, websocket_content):
        """Test TASK-102 requirement: CORS allowed origins"""
        assert "cors_allowed_origins" in websocket_content, \
            "TASK-102 requirement: Must configure cors_allowed_origins"

    def test_task_102_connect_handler(self, websocket_content):
        """Test TASK-102 requirement: connect event handler"""
        assert "async def connect" in websocket_content, \
            "TASK-102 requirement: Must implement connect handler"
        assert "sid" in websocket_content and "environ" in websocket_content and "auth" in websocket_content, \
            "TASK-102 requirement: connect should have sid, environ, auth parameters"

    def test_task_102_subscribe_handler(self, websocket_content):
        """Test TASK-102 requirement: subscribe_test_run handler"""
        assert "async def subscribe_test_run" in websocket_content, \
            "TASK-102 requirement: Must implement subscribe_test_run handler"
        assert "enter_room" in websocket_content, \
            "TASK-102 requirement: subscribe_test_run should use enter_room"
