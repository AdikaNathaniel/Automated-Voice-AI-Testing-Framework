"""
Test suite for Socket.IO packages in backend/requirements.txt

Validates that Socket.IO packages are properly configured:
- python-socketio package presence and version
- asyncio support configuration
- Package placement in requirements.txt
"""

import pytest
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
REQUIREMENTS_FILE = BACKEND_DIR / "requirements.txt"


class TestRequirementsFileExists:
    """Test that requirements.txt exists"""

    def test_requirements_file_exists(self):
        """Test that requirements.txt file exists"""
        assert REQUIREMENTS_FILE.exists(), "requirements.txt should exist"
        assert REQUIREMENTS_FILE.is_file(), "requirements.txt should be a file"


class TestSocketIOPackage:
    """Test Socket.IO package configuration"""

    @pytest.fixture
    def requirements_content(self):
        """Load requirements.txt content"""
        return REQUIREMENTS_FILE.read_text()

    def test_has_python_socketio(self, requirements_content):
        """Test that python-socketio package is present"""
        assert "python-socketio" in requirements_content, \
            "Should have python-socketio package"

    def test_python_socketio_version(self, requirements_content):
        """Test that python-socketio has correct version"""
        # Should specify version 5.10.0
        assert "python-socketio==5.10.0" in requirements_content, \
            "Should have python-socketio==5.10.0"

    def test_has_socketio_asyncio_support(self, requirements_content):
        """Test that Socket.IO has asyncio support configured"""
        # Should have python-socketio with asyncio extras or separate line
        # The requirement asks for python-socketio[asyncio] as well
        # This could be the same line or separate
        has_asyncio = (
            "python-socketio[asyncio]" in requirements_content or
            "[asyncio]" in requirements_content
        )
        assert has_asyncio, \
            "Should have asyncio support for python-socketio"


class TestSocketIOSection:
    """Test Socket.IO section in requirements.txt"""

    @pytest.fixture
    def requirements_content(self):
        """Load requirements.txt content"""
        return REQUIREMENTS_FILE.read_text()

    def test_has_websocket_section(self, requirements_content):
        """Test that there's a WebSocket/Real-time section"""
        # Should have a section for WebSocket or Real-time communication
        has_section = (
            "WebSocket" in requirements_content or
            "Real-time" in requirements_content or
            "Socket.IO" in requirements_content or
            "websocket" in requirements_content.lower()
        )
        assert has_section, \
            "Should have a section comment for WebSocket/Real-time packages"

    def test_socketio_in_organized_section(self, requirements_content):
        """Test that Socket.IO is in an organized section"""
        lines = requirements_content.split('\n')

        # Find the line with python-socketio
        socketio_line_num = None
        for i, line in enumerate(lines):
            if 'python-socketio' in line and not line.strip().startswith('#'):
                socketio_line_num = i
                break

        assert socketio_line_num is not None, \
            "Should have python-socketio package line"

        # Check that there's a section header within previous 10 lines
        has_nearby_header = False
        for i in range(max(0, socketio_line_num - 10), socketio_line_num):
            if lines[i].strip().startswith('#') and '=' in lines[i]:
                has_nearby_header = True
                break

        assert has_nearby_header, \
            "Socket.IO should be in an organized section with header"


class TestPackageCompatibility:
    """Test package compatibility"""

    @pytest.fixture
    def requirements_content(self):
        """Load requirements.txt content"""
        return REQUIREMENTS_FILE.read_text()

    def test_socketio_compatible_with_fastapi(self, requirements_content):
        """Test that Socket.IO and FastAPI are both present (compatible)"""
        assert "fastapi" in requirements_content, \
            "Should have FastAPI"
        assert "python-socketio" in requirements_content, \
            "Should have python-socketio (compatible with FastAPI)"

    def test_has_uvicorn_for_asgi(self, requirements_content):
        """Test that uvicorn is present (needed for ASGI)"""
        # Socket.IO async_mode='asgi' requires an ASGI server
        assert "uvicorn" in requirements_content, \
            "Should have uvicorn for ASGI support"


class TestRequirementsStructure:
    """Test overall requirements.txt structure"""

    @pytest.fixture
    def requirements_content(self):
        """Load requirements.txt content"""
        return REQUIREMENTS_FILE.read_text()

    def test_is_valid_format(self, requirements_content):
        """Test that requirements.txt has valid format"""
        lines = requirements_content.split('\n')

        # Should have package lines with versions
        package_lines = [
            line for line in lines
            if line.strip() and not line.strip().startswith('#')
        ]

        assert len(package_lines) > 0, \
            "Should have package declarations"

        # Check that Socket.IO line follows proper format
        socketio_lines = [
            line for line in package_lines
            if 'python-socketio' in line
        ]

        assert len(socketio_lines) > 0, \
            "Should have python-socketio package line"

        for line in socketio_lines:
            # Should have == for version pinning
            assert '==' in line or '[' in line, \
                "Socket.IO package should have version specification"


class TestDocumentation:
    """Test documentation and comments"""

    @pytest.fixture
    def requirements_content(self):
        """Load requirements.txt content"""
        return REQUIREMENTS_FILE.read_text()

    def test_has_section_comments(self, requirements_content):
        """Test that file has section comments"""
        # Should have comments organizing packages
        assert '#' in requirements_content, \
            "Should have comments for organization"

        # Count section headers (lines with = signs)
        section_headers = [
            line for line in requirements_content.split('\n')
            if line.strip().startswith('#') and '=' in line
        ]

        assert len(section_headers) >= 5, \
            "Should have multiple organized sections"


class TestTaskRequirements:
    """Test TASK-101 specific requirements"""

    @pytest.fixture
    def requirements_content(self):
        """Load requirements.txt content"""
        return REQUIREMENTS_FILE.read_text()

    def test_task_101_python_socketio_version(self, requirements_content):
        """Test TASK-101 requirement: python-socketio==5.10.0"""
        assert "python-socketio==5.10.0" in requirements_content, \
            "TASK-101 requirement: Must have python-socketio==5.10.0"

    def test_task_101_asyncio_support(self, requirements_content):
        """Test TASK-101 requirement: python-socketio[asyncio]"""
        # The task specifies both python-socketio==5.10.0 AND python-socketio[asyncio]
        # This could mean separate lines or combined
        has_asyncio = (
            "python-socketio[asyncio]" in requirements_content or
            "[asyncio]" in requirements_content
        )
        assert has_asyncio, \
            "TASK-101 requirement: Must have python-socketio[asyncio]"

    def test_task_101_requirements_updated(self, requirements_content):
        """Test TASK-101 requirement: requirements.txt updated"""
        # Should have python-socketio in requirements
        assert "python-socketio" in requirements_content, \
            "TASK-101 requirement: requirements.txt should be updated with Socket.IO"
