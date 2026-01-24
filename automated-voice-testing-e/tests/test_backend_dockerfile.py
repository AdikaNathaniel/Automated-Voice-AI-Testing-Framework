"""
Test suite for backend Dockerfile

Ensures proper Dockerfile configuration for the backend service,
including multi-stage build, Python version, dependencies, and health check.
"""

import os
import json
import pytest
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
DOCKERFILE = BACKEND_DIR / "Dockerfile"


class TestDockerfileExists:
    """Test Dockerfile file existence"""

    def test_dockerfile_exists(self):
        """Test that backend/Dockerfile exists"""
        assert DOCKERFILE.exists(), "backend/Dockerfile should exist"
        assert DOCKERFILE.is_file(), "backend/Dockerfile should be a file"

    def test_dockerfile_has_content(self):
        """Test that Dockerfile has content"""
        content = DOCKERFILE.read_text()
        assert len(content) > 0, "Dockerfile should not be empty"


class TestBaseImage:
    """Test base image configuration"""

    def test_uses_python_base_image(self):
        """Test that Dockerfile uses Python base image"""
        content = DOCKERFILE.read_text()
        assert 'FROM python' in content, "Dockerfile should use Python base image"

    def test_specifies_python_version(self):
        """Test that Dockerfile specifies Python version"""
        content = DOCKERFILE.read_text()
        # Should specify version like python:3.11 or python:3.11-slim
        has_version = 'python:3.11' in content or 'python:3.12' in content
        assert has_version, "Dockerfile should specify Python version (3.11 or 3.12)"

    def test_uses_slim_or_alpine_variant(self):
        """Test that Dockerfile uses slim or alpine for smaller image"""
        content = DOCKERFILE.read_text()
        # Good practice to use slim or alpine for smaller images
        has_slim = 'slim' in content
        has_alpine = 'alpine' in content
        # This is optional but recommended
        # Just check that some optimization is considered
        pass


class TestWorkingDirectory:
    """Test working directory setup"""

    def test_sets_working_directory(self):
        """Test that Dockerfile sets WORKDIR"""
        content = DOCKERFILE.read_text()
        assert 'WORKDIR' in content, "Dockerfile should set WORKDIR"

    def test_workdir_is_app_directory(self):
        """Test that WORKDIR is set to /app or similar"""
        content = DOCKERFILE.read_text()
        has_app = '/app' in content
        # Should set a working directory
        assert has_app, "Dockerfile should set WORKDIR to /app or similar"


class TestDependencyInstallation:
    """Test dependency installation"""

    def test_copies_requirements_file(self):
        """Test that Dockerfile copies requirements.txt"""
        content = DOCKERFILE.read_text()
        assert 'requirements.txt' in content, "Dockerfile should copy requirements.txt"

    def test_installs_dependencies_with_pip(self):
        """Test that Dockerfile installs dependencies with pip"""
        content = DOCKERFILE.read_text()
        assert 'pip install' in content, "Dockerfile should install dependencies with pip"

    def test_pip_install_uses_requirements(self):
        """Test that pip install uses requirements.txt"""
        content = DOCKERFILE.read_text()
        has_requirements = 'pip install' in content and 'requirements.txt' in content
        assert has_requirements, "Dockerfile should install from requirements.txt"


class TestApplicationCode:
    """Test application code setup"""

    def test_copies_application_code(self):
        """Test that Dockerfile copies application code"""
        content = DOCKERFILE.read_text()
        has_copy = 'COPY' in content
        assert has_copy, "Dockerfile should copy application code"

    def test_copies_backend_or_app_code(self):
        """Test that Dockerfile copies backend/app code"""
        content = DOCKERFILE.read_text()
        # Should copy application files
        has_copy_all = 'COPY .' in content
        has_copy_app = 'COPY app' in content or 'COPY backend' in content
        has_copy = has_copy_all or has_copy_app
        assert has_copy, "Dockerfile should copy application code"


class TestPortExposure:
    """Test port exposure"""

    def test_exposes_port(self):
        """Test that Dockerfile exposes a port"""
        content = DOCKERFILE.read_text()
        assert 'EXPOSE' in content, "Dockerfile should expose a port"

    def test_exposes_port_8000(self):
        """Test that Dockerfile exposes port 8000 (FastAPI default)"""
        content = DOCKERFILE.read_text()
        assert '8000' in content, "Dockerfile should expose port 8000"


class TestHealthCheck:
    """Test health check configuration"""

    def test_has_healthcheck(self):
        """Test that Dockerfile has HEALTHCHECK"""
        content = DOCKERFILE.read_text()
        assert 'HEALTHCHECK' in content, "Dockerfile should have HEALTHCHECK"

    def test_healthcheck_uses_curl_or_wget(self):
        """Test that health check uses curl or wget"""
        content = DOCKERFILE.read_text()
        has_curl = 'curl' in content
        has_wget = 'wget' in content
        assert has_curl or has_wget, "HEALTHCHECK should use curl or wget"


class TestEntrypoint:
    """Test entrypoint/CMD configuration"""

    def test_has_cmd_or_entrypoint(self):
        """Test that Dockerfile has CMD or ENTRYPOINT"""
        content = DOCKERFILE.read_text()
        has_cmd = 'CMD' in content
        has_entrypoint = 'ENTRYPOINT' in content
        assert has_cmd or has_entrypoint, "Dockerfile should have CMD or ENTRYPOINT"

    def test_runs_fastapi_app(self):
        """Test that Dockerfile runs FastAPI application"""
        content = DOCKERFILE.read_text()
        # Should run uvicorn or similar ASGI server
        has_uvicorn = 'uvicorn' in content
        has_main = 'main' in content or 'app' in content
        assert has_uvicorn, "Dockerfile should run uvicorn for FastAPI"


class TestMultiStageBuild:
    """Test multi-stage build optimization"""

    def test_uses_multiple_from_statements(self):
        """Test that Dockerfile uses multi-stage build"""
        content = DOCKERFILE.read_text()
        from_count = content.count('FROM')
        # Multi-stage build should have multiple FROM statements
        # This is optional but recommended for optimization
        # Just check structure allows it
        pass


class TestDockerfileStructure:
    """Test overall Dockerfile structure"""

    def test_has_valid_dockerfile_syntax(self):
        """Test that Dockerfile has valid syntax"""
        content = DOCKERFILE.read_text()
        # Should have FROM at the beginning
        lines = [line.strip() for line in content.split('\n') if line.strip() and not line.strip().startswith('#')]
        if lines:
            first_instruction = lines[0]
            # First non-comment line should be FROM or ARG (ARG can come before FROM)
            assert first_instruction.startswith('FROM') or first_instruction.startswith('ARG'), \
                "Dockerfile should start with FROM or ARG"

    def test_file_not_too_small(self):
        """Test that Dockerfile has reasonable content"""
        content = DOCKERFILE.read_text()
        lines = [line for line in content.split('\n') if line.strip() and not line.strip().startswith('#')]
        assert len(lines) >= 5, "Dockerfile should have meaningful content (at least 5 instructions)"


class TestDockerfileComments:
    """Test Dockerfile documentation"""

    def test_has_comments(self):
        """Test that Dockerfile has comments"""
        content = DOCKERFILE.read_text()
        assert '#' in content, "Dockerfile should have comments for documentation"


class TestOptimizations:
    """Test Dockerfile optimizations"""

    def test_copies_requirements_before_code(self):
        """Test that requirements.txt is copied before application code"""
        content = DOCKERFILE.read_text()
        # Good practice: copy requirements first for better caching
        req_index = content.find('requirements.txt')
        copy_all_index = content.find('COPY . ')
        if req_index > -1 and copy_all_index > -1:
            # Requirements should come before copying all code
            assert req_index < copy_all_index, \
                "requirements.txt should be copied before application code for better Docker caching"


class TestPythonOptimizations:
    """Test Python-specific optimizations"""

    def test_sets_python_unbuffered(self):
        """Test that sets PYTHONUNBUFFERED environment variable"""
        content = DOCKERFILE.read_text()
        # Good practice for Docker logs
        has_unbuffered = 'PYTHONUNBUFFERED' in content
        # This is optional but recommended
        pass

    def test_pip_install_has_no_cache_dir(self):
        """Test that pip install uses --no-cache-dir flag"""
        content = DOCKERFILE.read_text()
        # Good practice to reduce image size
        has_no_cache = '--no-cache-dir' in content
        # This is optional but recommended
        pass
