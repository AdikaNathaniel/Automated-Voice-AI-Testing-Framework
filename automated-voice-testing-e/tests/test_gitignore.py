"""
Test suite for .gitignore file validation
Ensures all necessary patterns are present for Python, Node.js, IDE, and OS-specific exclusions
"""

import os
import pytest


class TestGitignore:
    """Test .gitignore file exists and contains required patterns"""

    @pytest.fixture
    def gitignore_path(self):
        """Get path to .gitignore file"""
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), '.gitignore')

    @pytest.fixture
    def gitignore_content(self, gitignore_path):
        """Read .gitignore content"""
        if not os.path.exists(gitignore_path):
            pytest.fail(f".gitignore file not found at {gitignore_path}")

        with open(gitignore_path, 'r') as f:
            return f.read()

    def test_gitignore_exists(self, gitignore_path):
        """Test that .gitignore file exists"""
        assert os.path.exists(gitignore_path), ".gitignore file must exist in project root"

    def test_python_exclusions(self, gitignore_content):
        """Test that Python-specific exclusions are present"""
        required_patterns = [
            '__pycache__',
            '*.py[cod]',
            '*$py.class',
            '*.so',
            '.Python',
            'build/',
            'develop-eggs/',
            'dist/',
            'downloads/',
            'eggs/',
            '.eggs/',
            'lib/',
            'lib64/',
            'parts/',
            'sdist/',
            'var/',
            'wheels/',
            '*.egg-info/',
            '.installed.cfg',
            '*.egg',
            'pip-log.txt',
            'pip-delete-this-directory.txt',
        ]

        for pattern in required_patterns:
            assert pattern in gitignore_content, f"Python pattern '{pattern}' must be in .gitignore"

    def test_virtual_environment_exclusions(self, gitignore_content):
        """Test that virtual environment directories are excluded"""
        venv_patterns = [
            'venv/',
            'ENV/',
            'env/',
            '.venv',
        ]

        for pattern in venv_patterns:
            assert pattern in gitignore_content, f"Virtual env pattern '{pattern}' must be in .gitignore"

    def test_nodejs_exclusions(self, gitignore_content):
        """Test that Node.js-specific exclusions are present"""
        required_patterns = [
            'node_modules/',
            'npm-debug.log*',
            'yarn-debug.log*',
            'yarn-error.log*',
            '.npm',
            '.yarn',
            'package-lock.json',
            'yarn.lock',
        ]

        for pattern in required_patterns:
            assert pattern in gitignore_content, f"Node.js pattern '{pattern}' must be in .gitignore"

    def test_environment_files_exclusion(self, gitignore_content):
        """Test that environment files are excluded"""
        env_patterns = [
            '.env',
            '.env.local',
            '.env.development',
            '.env.staging',
            '.env.production',
            '*.env',
        ]

        for pattern in env_patterns:
            assert pattern in gitignore_content, f"Environment file pattern '{pattern}' must be in .gitignore"

    def test_log_files_exclusion(self, gitignore_content):
        """Test that log files and directories are excluded"""
        log_patterns = [
            '*.log',
            'logs/',
            'log/',
        ]

        for pattern in log_patterns:
            assert pattern in gitignore_content, f"Log pattern '{pattern}' must be in .gitignore"

    def test_cache_directories_exclusion(self, gitignore_content):
        """Test that cache directories are excluded"""
        cache_patterns = [
            '.cache/',
            '*.cache',
            '__pycache__/',
            '.pytest_cache/',
            '.mypy_cache/',
            '.ruff_cache/',
        ]

        for pattern in cache_patterns:
            assert pattern in gitignore_content, f"Cache pattern '{pattern}' must be in .gitignore"

    def test_ide_exclusions(self, gitignore_content):
        """Test that IDE-specific files are excluded"""
        ide_patterns = [
            '.vscode/',
            '.idea/',
            '*.swp',
            '*.swo',
            '*~',
            '.DS_Store',
            'Thumbs.db',
        ]

        for pattern in ide_patterns:
            assert pattern in gitignore_content, f"IDE pattern '{pattern}' must be in .gitignore"

    def test_os_specific_exclusions(self, gitignore_content):
        """Test that OS-specific files are excluded"""
        os_patterns = [
            '.DS_Store',  # macOS
            'Thumbs.db',  # Windows
            'Desktop.ini',  # Windows
            '*.swp',  # Vim temp files
            '*.swo',
            '*~',  # Backup files
        ]

        for pattern in os_patterns:
            assert pattern in gitignore_content, f"OS-specific pattern '{pattern}' must be in .gitignore"

    def test_database_exclusions(self, gitignore_content):
        """Test that database files are excluded"""
        db_patterns = [
            '*.db',
            '*.sqlite',
            '*.sqlite3',
        ]

        for pattern in db_patterns:
            assert pattern in gitignore_content, f"Database pattern '{pattern}' must be in .gitignore"

    def test_docker_exclusions(self, gitignore_content):
        """Test that Docker-related files are excluded where appropriate"""
        # Note: We want to keep docker-compose.yml and Dockerfile
        # but exclude docker volumes and temp files
        docker_patterns = [
            '.docker/',
        ]

        for pattern in docker_patterns:
            assert pattern in gitignore_content, f"Docker pattern '{pattern}' must be in .gitignore"

    def test_coverage_exclusions(self, gitignore_content):
        """Test that test coverage files are excluded"""
        coverage_patterns = [
            'htmlcov/',
            '.coverage',
            'coverage.xml',
            '*.cover',
        ]

        for pattern in coverage_patterns:
            assert pattern in gitignore_content, f"Coverage pattern '{pattern}' must be in .gitignore"
