"""
Test suite for backend/requirements.txt validation
Ensures requirements.txt exists and contains required Python dependencies
"""

import os
import re
import pytest


class TestRequirements:
    """Test backend/requirements.txt file exists and contains required dependencies"""

    @pytest.fixture
    def project_root(self):
        """Get project root directory"""
        return os.path.dirname(os.path.dirname(__file__))

    @pytest.fixture
    def requirements_path(self, project_root):
        """Get path to backend/requirements.txt file"""
        return os.path.join(project_root, 'backend', 'requirements.txt')

    @pytest.fixture
    def requirements_content(self, requirements_path):
        """Read requirements.txt content"""
        if not os.path.exists(requirements_path):
            pytest.fail(f"requirements.txt file not found at {requirements_path}")

        with open(requirements_path, 'r', encoding='utf-8') as f:
            return f.read()

    def test_requirements_file_exists(self, requirements_path):
        """Test that backend/requirements.txt file exists"""
        assert os.path.exists(requirements_path), \
            "backend/requirements.txt file must exist"

    def test_has_fastapi(self, requirements_content):
        """Test that requirements include FastAPI"""
        assert re.search(r'^fastapi[=<>]', requirements_content, re.MULTILINE), \
            "requirements.txt must include fastapi"

    def test_has_uvicorn(self, requirements_content):
        """Test that requirements include Uvicorn"""
        assert re.search(r'^uvicorn', requirements_content, re.MULTILINE), \
            "requirements.txt must include uvicorn"

    def test_has_sqlalchemy(self, requirements_content):
        """Test that requirements include SQLAlchemy"""
        assert re.search(r'^sqlalchemy[=<>]', requirements_content, re.MULTILINE | re.IGNORECASE), \
            "requirements.txt must include sqlalchemy"

    def test_has_alembic(self, requirements_content):
        """Test that requirements include Alembic for migrations"""
        assert re.search(r'^alembic[=<>]', requirements_content, re.MULTILINE), \
            "requirements.txt must include alembic"

    def test_has_pydantic(self, requirements_content):
        """Test that requirements include Pydantic"""
        assert re.search(r'^pydantic[=<>]', requirements_content, re.MULTILINE), \
            "requirements.txt must include pydantic"

    def test_has_python_jose(self, requirements_content):
        """Test that requirements include python-jose for JWT"""
        assert re.search(r'^python-jose', requirements_content, re.MULTILINE), \
            "requirements.txt must include python-jose"

    def test_has_passlib(self, requirements_content):
        """Test that requirements include passlib for password hashing"""
        assert re.search(r'^passlib', requirements_content, re.MULTILINE), \
            "requirements.txt must include passlib"

    def test_has_psycopg2(self, requirements_content):
        """Test that requirements include psycopg2 for PostgreSQL"""
        assert re.search(r'^psycopg2', requirements_content, re.MULTILINE), \
            "requirements.txt must include psycopg2"

    def test_has_redis(self, requirements_content):
        """Test that requirements include redis client"""
        assert re.search(r'^redis[=<>]', requirements_content, re.MULTILINE), \
            "requirements.txt must include redis"

    def test_has_celery(self, requirements_content):
        """Test that requirements include Celery for task queue"""
        assert re.search(r'^celery(\[.*\])?[=<>]', requirements_content, re.MULTILINE), \
            "requirements.txt must include celery"

    def test_has_pytest(self, requirements_content):
        """Test that requirements include pytest"""
        assert re.search(r'^pytest[=<>]', requirements_content, re.MULTILINE), \
            "requirements.txt must include pytest"

    def test_has_pytest_cov(self, requirements_content):
        """Test that requirements include pytest-cov for coverage"""
        assert re.search(r'^pytest-cov[=<>]', requirements_content, re.MULTILINE), \
            "requirements.txt must include pytest-cov"

    def test_has_pytest_asyncio(self, requirements_content):
        """Test that requirements include pytest-asyncio"""
        assert re.search(r'^pytest-asyncio[=<>]', requirements_content, re.MULTILINE), \
            "requirements.txt must include pytest-asyncio"

    def test_has_httpx(self, requirements_content):
        """Test that requirements include httpx for async HTTP client"""
        assert re.search(r'^httpx[=<>]', requirements_content, re.MULTILINE), \
            "requirements.txt must include httpx"

    def test_has_python_multipart(self, requirements_content):
        """Test that requirements include python-multipart for file uploads"""
        assert re.search(r'^python-multipart[=<>]', requirements_content, re.MULTILINE), \
            "requirements.txt must include python-multipart"

    def test_has_python_dotenv(self, requirements_content):
        """Test that requirements include python-dotenv for environment variables"""
        assert re.search(r'^python-dotenv[=<>]', requirements_content, re.MULTILINE), \
            "requirements.txt must include python-dotenv"

    def test_has_boto3(self, requirements_content):
        """Test that requirements include boto3 for AWS"""
        assert re.search(r'^boto3[=<>]', requirements_content, re.MULTILINE), \
            "requirements.txt must include boto3"

    def test_has_requests(self, requirements_content):
        """Test that requirements include requests HTTP library"""
        assert re.search(r'^requests[=<>]', requirements_content, re.MULTILINE), \
            "requirements.txt must include requests"

    def test_has_linting_tools(self, requirements_content):
        """Test that requirements include linting tools"""
        has_ruff = re.search(r'^ruff[=<>]', requirements_content, re.MULTILINE)
        has_black = re.search(r'^black[=<>]', requirements_content, re.MULTILINE)

        assert has_ruff or has_black, \
            "requirements.txt must include linting tools (ruff or black)"

    def test_has_version_pins(self, requirements_content):
        """Test that dependencies have version specifications"""
        # Get all non-comment, non-empty lines
        dependency_lines = [line.strip() for line in requirements_content.split('\n')
                           if line.strip() and not line.strip().startswith('#')]

        # Count lines with version specifications (==, >=, <=, ~=, etc.)
        versioned_lines = [line for line in dependency_lines
                          if re.search(r'[=<>~]', line)]

        # At least 80% should have version specifications
        if dependency_lines:
            version_ratio = len(versioned_lines) / len(dependency_lines)
            assert version_ratio >= 0.8, \
                "At least 80% of dependencies should have version specifications"

    def test_no_duplicate_packages(self, requirements_content):
        """Test that there are no duplicate package declarations"""
        # Get package names (before ==, >=, etc.)
        package_lines = [line.strip() for line in requirements_content.split('\n')
                        if line.strip() and not line.strip().startswith('#')]

        package_names = []
        for line in package_lines:
            # Extract package name (before version specifier)
            match = re.match(r'^([a-zA-Z0-9_\-\[\]]+)', line)
            if match:
                package_names.append(match.group(1).lower())

        # Check for duplicates
        duplicates = [pkg for pkg in set(package_names)
                     if package_names.count(pkg) > 1]

        assert not duplicates, \
            f"requirements.txt contains duplicate packages: {', '.join(duplicates)}"

    def test_has_reasonable_number_of_dependencies(self, requirements_content):
        """Test that requirements has reasonable number of dependencies"""
        # Get non-comment, non-empty lines
        dependency_lines = [line.strip() for line in requirements_content.split('\n')
                           if line.strip() and not line.strip().startswith('#')]

        assert len(dependency_lines) >= 15, \
            f"requirements.txt should have at least 15 dependencies (currently {len(dependency_lines)})"

    def test_proper_requirements_format(self, requirements_content):
        """Test that requirements file follows proper format"""
        lines = requirements_content.split('\n')

        for line_num, line in enumerate(lines, 1):
            # Skip empty lines and comments
            if not line.strip() or line.strip().startswith('#'):
                continue

            # Should match package specification format
            # e.g., "package==1.0.0" or "package[extra]>=1.0.0"
            assert re.match(r'^[a-zA-Z0-9_\-\[\]]+[=<>~]', line.strip()), \
                f"Line {line_num}: Invalid format '{line.strip()}'. Should be 'package==version' or similar"
