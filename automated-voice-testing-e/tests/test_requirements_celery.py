"""
Test suite for backend/requirements.txt Celery dependencies

Validates the requirements.txt file includes proper Celery configuration:
- Celery package with redis extras
- Celery version 5.3.4
- Kombu package (Celery dependency)
- Kombu version 5.3.4
- Proper formatting
"""

import pytest
from pathlib import Path
import re


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
REQUIREMENTS_FILE = BACKEND_DIR / "requirements.txt"


class TestRequirementsFileExists:
    """Test that requirements.txt exists"""

    def test_backend_directory_exists(self):
        """Test that backend directory exists"""
        assert BACKEND_DIR.exists(), "backend directory should exist"
        assert BACKEND_DIR.is_dir(), "backend should be a directory"

    def test_requirements_file_exists(self):
        """Test that requirements.txt exists"""
        assert REQUIREMENTS_FILE.exists(), "backend/requirements.txt should exist"
        assert REQUIREMENTS_FILE.is_file(), "requirements.txt should be a file"

    def test_requirements_has_content(self):
        """Test that requirements.txt has content"""
        content = REQUIREMENTS_FILE.read_text()
        assert len(content) > 0, "requirements.txt should not be empty"


class TestCeleryPackage:
    """Test Celery package configuration"""

    @pytest.fixture
    def requirements_content(self):
        """Load requirements.txt content"""
        return REQUIREMENTS_FILE.read_text()

    def test_celery_is_present(self, requirements_content):
        """Test that Celery package is present"""
        # Check for celery (case-insensitive, with or without extras)
        assert re.search(r'^celery(\[.*?\])?==', requirements_content, re.MULTILINE | re.IGNORECASE), \
            "Celery package should be in requirements.txt"

    def test_celery_has_redis_extras(self, requirements_content):
        """Test that Celery includes redis extras"""
        # Look for celery[redis] or celery[...,redis,...]
        assert re.search(r'^celery\[.*?redis.*?\]==', requirements_content, re.MULTILINE | re.IGNORECASE), \
            "Celery should include [redis] extras"

    def test_celery_version_is_5_3_4(self, requirements_content):
        """Test that Celery version is 5.3.4"""
        # Find celery line and extract version
        match = re.search(r'^celery\[.*?\]==([\d.]+)', requirements_content, re.MULTILINE | re.IGNORECASE)
        assert match, "Celery version should be specified"
        version = match.group(1)
        assert version == "5.3.4", f"Celery version should be 5.3.4, got {version}"

    def test_celery_line_format(self, requirements_content):
        """Test that Celery line is properly formatted"""
        # Should match pattern: celery[redis]==5.3.4
        assert re.search(r'^celery\[redis\]==5\.3\.4', requirements_content, re.MULTILINE | re.IGNORECASE), \
            "Celery line should be formatted as 'celery[redis]==5.3.4'"


class TestKombuPackage:
    """Test Kombu package configuration"""

    @pytest.fixture
    def requirements_content(self):
        """Load requirements.txt content"""
        return REQUIREMENTS_FILE.read_text()

    def test_kombu_is_present(self, requirements_content):
        """Test that Kombu package is present"""
        assert re.search(r'^kombu==', requirements_content, re.MULTILINE | re.IGNORECASE), \
            "Kombu package should be in requirements.txt"

    def test_kombu_version_is_5_3_4(self, requirements_content):
        """Test that Kombu version is 5.3.4"""
        match = re.search(r'^kombu==([\d.]+)', requirements_content, re.MULTILINE | re.IGNORECASE)
        assert match, "Kombu version should be specified"
        version = match.group(1)
        assert version == "5.3.4", f"Kombu version should be 5.3.4, got {version}"

    def test_kombu_line_format(self, requirements_content):
        """Test that Kombu line is properly formatted"""
        assert re.search(r'^kombu==5\.3\.4', requirements_content, re.MULTILINE | re.IGNORECASE), \
            "Kombu line should be formatted as 'kombu==5.3.4'"


class TestTaskQueueSection:
    """Test Task Queue & Caching section"""

    @pytest.fixture
    def requirements_content(self):
        """Load requirements.txt content"""
        return REQUIREMENTS_FILE.read_text()

    def test_has_task_queue_section(self, requirements_content):
        """Test that Task Queue section exists"""
        assert 'Task Queue' in requirements_content or 'task queue' in requirements_content.lower(), \
            "Should have Task Queue section in requirements.txt"

    def test_packages_near_task_queue_section(self, requirements_content):
        """Test that Celery and Kombu appear near Task Queue section"""
        # Find positions of Task Queue section and the packages
        lines = requirements_content.split('\n')

        task_queue_line = -1
        celery_line = -1
        kombu_line = -1

        for i, line in enumerate(lines):
            if 'task queue' in line.lower() and '#' in line:
                task_queue_line = i
            if re.search(r'^celery\[', line, re.IGNORECASE):
                celery_line = i
            if re.search(r'^kombu==', line, re.IGNORECASE):
                kombu_line = i

        # All should be found
        assert task_queue_line >= 0, "Task Queue section should exist"
        assert celery_line >= 0, "Celery package should exist"
        assert kombu_line >= 0, "Kombu package should exist"

        # Celery and Kombu should appear after Task Queue section (within ~10 lines)
        assert celery_line > task_queue_line, "Celery should appear after Task Queue section"
        assert kombu_line > task_queue_line, "Kombu should appear after Task Queue section"
        assert celery_line - task_queue_line < 10, "Celery should be within 10 lines of Task Queue section"
        assert kombu_line - task_queue_line < 10, "Kombu should be within 10 lines of Task Queue section"


class TestRedisPackage:
    """Test Redis package (supporting Celery)"""

    @pytest.fixture
    def requirements_content(self):
        """Load requirements.txt content"""
        return REQUIREMENTS_FILE.read_text()

    def test_redis_is_present(self, requirements_content):
        """Test that Redis package is present"""
        assert re.search(r'^redis==', requirements_content, re.MULTILINE | re.IGNORECASE), \
            "Redis package should be in requirements.txt (needed for Celery broker)"

    def test_redis_version_specified(self, requirements_content):
        """Test that Redis has a version specified"""
        match = re.search(r'^redis==([\d.]+)', requirements_content, re.MULTILINE | re.IGNORECASE)
        assert match, "Redis version should be specified"
        version = match.group(1)
        # Just check that it's a valid version format
        assert re.match(r'^\d+\.\d+\.\d+', version), "Redis version should be in x.y.z format"


class TestPackageCompatibility:
    """Test package version compatibility"""

    @pytest.fixture
    def requirements_content(self):
        """Load requirements.txt content"""
        return REQUIREMENTS_FILE.read_text()

    def test_celery_and_kombu_same_version(self, requirements_content):
        """Test that Celery and Kombu have the same version (5.3.4)"""
        celery_match = re.search(r'^celery\[.*?\]==([\d.]+)', requirements_content, re.MULTILINE | re.IGNORECASE)
        kombu_match = re.search(r'^kombu==([\d.]+)', requirements_content, re.MULTILINE | re.IGNORECASE)

        assert celery_match and kombu_match, "Both Celery and Kombu should be present"

        celery_version = celery_match.group(1)
        kombu_version = kombu_match.group(1)

        assert celery_version == kombu_version, \
            f"Celery ({celery_version}) and Kombu ({kombu_version}) should have the same version"
        assert celery_version == "5.3.4", "Both should be version 5.3.4"


class TestFileStructure:
    """Test overall file structure and organization"""

    @pytest.fixture
    def requirements_content(self):
        """Load requirements.txt content"""
        return REQUIREMENTS_FILE.read_text()

    def test_no_duplicate_celery(self, requirements_content):
        """Test that Celery is not duplicated"""
        celery_lines = [line for line in requirements_content.split('\n')
                       if re.match(r'^celery', line, re.IGNORECASE)]
        assert len(celery_lines) == 1, f"Celery should appear exactly once, found {len(celery_lines)} times"

    def test_no_duplicate_kombu(self, requirements_content):
        """Test that Kombu is not duplicated"""
        kombu_lines = [line for line in requirements_content.split('\n')
                      if re.match(r'^kombu==', line, re.IGNORECASE)]
        assert len(kombu_lines) == 1, f"Kombu should appear exactly once, found {len(kombu_lines)} times"

    def test_packages_are_pinned(self, requirements_content):
        """Test that packages have pinned versions (==)"""
        assert re.search(r'^celery\[redis\]==5\.3\.4', requirements_content, re.MULTILINE | re.IGNORECASE), \
            "Celery should be pinned with =="
        assert re.search(r'^kombu==5\.3\.4', requirements_content, re.MULTILINE | re.IGNORECASE), \
            "Kombu should be pinned with =="
