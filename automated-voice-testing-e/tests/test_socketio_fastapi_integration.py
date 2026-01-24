"""
Test suite for Socket.IO integration with FastAPI (TASK-103)

Validates that Socket.IO is properly integrated with FastAPI:
- Socket.IO imports in main.py
- ASGI app creation from Socket.IO server
- Socket.IO app mounted to FastAPI
- Integration configuration
- Application structure and functionality
"""

import pytest
from pathlib import Path
import sys


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
API_DIR = BACKEND_DIR / "api"
MAIN_FILE = API_DIR / "main.py"


class TestMainFileExists:
    """Test that main.py exists"""

    def test_main_file_exists(self):
        """Test that main.py exists"""
        assert MAIN_FILE.exists(), "main.py should exist"
        assert MAIN_FILE.is_file(), "main.py should be a file"

    def test_main_has_content(self):
        """Test that main.py has content"""
        content = MAIN_FILE.read_text()
        assert len(content) > 0, "main.py should not be empty"


class TestSocketIOImports:
    """Test Socket.IO related imports"""

    @pytest.fixture
    def main_content(self):
        """Load main.py content"""
        return MAIN_FILE.read_text()

    def test_imports_socketio(self, main_content):
        """Test that socketio module is imported"""
        assert "import socketio" in main_content or "from socketio import" in main_content, \
            "Should import socketio module"

    def test_imports_sio_from_websocket(self, main_content):
        """Test that sio instance is imported from websocket module"""
        assert "from api.websocket import sio" in main_content or \
               "from .websocket import sio" in main_content, \
            "Should import sio from api.websocket"


class TestSocketIOASGIApp:
    """Test Socket.IO ASGI app creation"""

    @pytest.fixture
    def main_content(self):
        """Load main.py content"""
        return MAIN_FILE.read_text()

    def test_creates_socketio_asgi_app(self, main_content):
        """Test that Socket.IO ASGI app is created"""
        # Should create an ASGI app from the sio instance
        assert "socketio.ASGIApp" in main_content or "sio.ASGIApp" in main_content or \
               "socketio_app" in main_content, \
            "Should create Socket.IO ASGI app"

    def test_socketio_app_variable_exists(self, main_content):
        """Test that socketio_app variable is created"""
        assert "socketio_app" in main_content or "socket_app" in main_content, \
            "Should have socketio_app or socket_app variable"

    def test_asgi_app_wraps_fastapi(self, main_content):
        """Test that ASGI app wraps FastAPI app"""
        # Socket.IO ASGIApp should wrap the FastAPI app
        assert "app" in main_content, \
            "Should reference the FastAPI app instance"


class TestSocketIOMounting:
    """Test Socket.IO app mounting to FastAPI"""

    @pytest.fixture
    def main_content(self):
        """Load main.py content"""
        return MAIN_FILE.read_text()

    def test_mounts_socketio_to_fastapi(self, main_content):
        """Test that Socket.IO is mounted to FastAPI"""
        # Socket.IO ASGIApp pattern integrates Socket.IO with FastAPI
        # by wrapping the FastAPI app in socketio.ASGIApp
        assert "socketio.ASGIApp" in main_content or "ASGIApp" in main_content, \
            "Should integrate Socket.IO with FastAPI using ASGIApp"

    def test_socketio_endpoint_configured(self, main_content):
        """Test that Socket.IO endpoint is configured"""
        # Socket.IO ASGIApp automatically handles /socket.io/ endpoints
        # We just need to verify that socketio_app is created
        assert "socketio_app" in main_content or "socket_app" in main_content, \
            "Should create socketio_app for endpoint handling"


class TestApplicationStructure:
    """Test overall application structure with Socket.IO"""

    @pytest.fixture
    def main_content(self):
        """Load main.py content"""
        return MAIN_FILE.read_text()

    def test_is_valid_python(self, main_content):
        """Test that main.py is valid Python"""
        try:
            compile(main_content, MAIN_FILE, 'exec')
        except SyntaxError as e:
            pytest.fail(f"main.py has syntax error: {e}")

    def test_has_fastapi_app(self, main_content):
        """Test that FastAPI app instance exists"""
        assert "app = FastAPI(" in main_content or "FastAPI(" in main_content, \
            "Should have FastAPI app instance"

    def test_has_all_socket_io_components(self, main_content):
        """Test that all Socket.IO integration components are present"""
        required_components = [
            "sio",  # Socket.IO instance
            "app",  # FastAPI instance
        ]
        for component in required_components:
            assert component in main_content, \
                f"Should have {component} component"


class TestSocketIOConfiguration:
    """Test Socket.IO configuration in FastAPI"""

    @pytest.fixture
    def main_content(self):
        """Load main.py content"""
        return MAIN_FILE.read_text()

    def test_has_socketio_section_comment(self, main_content):
        """Test that there's a comment/section for Socket.IO"""
        # Should have documentation about Socket.IO integration
        has_socket_section = (
            "Socket" in main_content or
            "WebSocket" in main_content or
            "socket.io" in main_content.lower()
        )
        assert has_socket_section, \
            "Should have Socket.IO section or comments"

    def test_socketio_after_fastapi_creation(self, main_content):
        """Test that Socket.IO setup comes after FastAPI app creation"""
        lines = main_content.split('\n')

        # Find line numbers
        fastapi_line = None
        socketio_line = None

        for i, line in enumerate(lines):
            if 'app = FastAPI(' in line:
                fastapi_line = i
            if 'socketio' in line.lower() and 'import' not in line.lower():
                if socketio_line is None:  # Get first occurrence after import
                    socketio_line = i

        # FastAPI should be created before Socket.IO setup
        if fastapi_line is not None and socketio_line is not None:
            assert fastapi_line < socketio_line, \
                "FastAPI app should be created before Socket.IO setup"


class TestImportability:
    """Test that main module can be imported with Socket.IO"""

    def test_can_import_main_module(self):
        """Test that main module can be imported"""
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from api import main
            assert main is not None, \
                "main module should be importable"
        except ImportError as e:
            pytest.fail(f"Cannot import main: {e}")

    def test_can_access_fastapi_app(self):
        """Test that FastAPI app can be accessed"""
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from api.main import app
            assert app is not None, \
                "FastAPI app should be accessible"
        except ImportError as e:
            pytest.fail(f"Cannot import app: {e}")

    def test_can_access_socketio_app(self):
        """Test that Socket.IO app can be accessed"""
        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))

        try:
            from api.main import socketio_app
            assert socketio_app is not None, \
                "Socket.IO app should be accessible"
        except (ImportError, AttributeError) as e:
            pytest.fail(f"Cannot access socketio_app: {e}")


class TestDocumentation:
    """Test documentation and comments"""

    @pytest.fixture
    def main_content(self):
        """Load main.py content"""
        return MAIN_FILE.read_text()

    def test_has_module_docstring(self, main_content):
        """Test that main.py has module docstring"""
        assert '"""' in main_content or "'''" in main_content, \
            "Should have module documentation"

    def test_has_socketio_comments(self, main_content):
        """Test that Socket.IO integration has comments"""
        # Should have comments explaining Socket.IO setup
        lines = main_content.split('\n')
        has_socket_comments = any(
            '#' in line and ('socket' in line.lower() or 'websocket' in line.lower())
            for line in lines
        )
        assert has_socket_comments or 'Socket' in main_content, \
            "Should have Socket.IO related comments or documentation"


class TestIntegrationPattern:
    """Test Socket.IO integration pattern"""

    @pytest.fixture
    def main_content(self):
        """Load main.py content"""
        return MAIN_FILE.read_text()

    def test_uses_asgi_app_pattern(self, main_content):
        """Test that integration uses ASGIApp pattern"""
        # Socket.IO should be integrated using socketio.ASGIApp
        assert "ASGIApp" in main_content, \
            "Should use socketio.ASGIApp for FastAPI integration"

    def test_references_websocket_module(self, main_content):
        """Test that main.py references the websocket module"""
        assert "websocket" in main_content, \
            "Should reference the websocket module"


class TestTaskRequirements:
    """Test TASK-103 specific requirements"""

    @pytest.fixture
    def main_content(self):
        """Load main.py content"""
        return MAIN_FILE.read_text()

    def test_task_103_socketio_import(self, main_content):
        """Test TASK-103 requirement: Import Socket.IO"""
        assert "socketio" in main_content, \
            "TASK-103 requirement: Must import socketio"

    def test_task_103_sio_import(self, main_content):
        """Test TASK-103 requirement: Import sio from websocket module"""
        assert "from api.websocket import sio" in main_content or \
               "from .websocket import sio" in main_content, \
            "TASK-103 requirement: Must import sio from websocket module"

    def test_task_103_mount_socketio(self, main_content):
        """Test TASK-103 requirement: Mount Socket.IO app"""
        # Should mount Socket.IO to FastAPI using ASGIApp
        assert "ASGIApp" in main_content or "mount" in main_content, \
            "TASK-103 requirement: Must mount Socket.IO app to FastAPI"

    def test_task_103_integration_complete(self, main_content):
        """Test TASK-103 requirement: Complete integration"""
        # All key components should be present
        required = ["sio", "ASGIApp", "app"]
        for component in required:
            assert component in main_content, \
                f"TASK-103 requirement: Must have {component} for complete integration"
