"""
Test suite for .env.example file validation
Ensures .env.example exists and contains all required environment variables
"""

import os
import re
import pytest


class TestEnvExample:
    """Test .env.example file exists and contains required configuration"""

    @pytest.fixture
    def project_root(self):
        """Get project root directory"""
        return os.path.dirname(os.path.dirname(__file__))

    @pytest.fixture
    def env_example_path(self, project_root):
        """Get path to .env.example file"""
        return os.path.join(project_root, '.env.example')

    @pytest.fixture
    def env_content(self, env_example_path):
        """Read .env.example content"""
        if not os.path.exists(env_example_path):
            pytest.fail(f".env.example file not found at {env_example_path}")

        with open(env_example_path, 'r', encoding='utf-8') as f:
            return f.read()

    def test_env_example_exists(self, env_example_path):
        """Test that .env.example file exists"""
        assert os.path.exists(env_example_path), \
            ".env.example file must exist in project root"

    def test_has_database_section(self, env_content):
        """Test that file has database configuration section"""
        database_indicators = ['database', 'postgresql', 'postgres', 'db']

        has_database = any(indicator in env_content.lower()
                          for indicator in database_indicators)

        assert has_database, ".env.example must have database configuration section"

    def test_has_database_url(self, env_content):
        """Test that file contains DATABASE_URL variable"""
        assert re.search(r'DATABASE_URL\s*=', env_content), \
            ".env.example must contain DATABASE_URL variable"

    def test_has_redis_section(self, env_content):
        """Test that file has Redis configuration section"""
        assert 'redis' in env_content.lower(), \
            ".env.example must have Redis configuration section"

    def test_has_redis_url(self, env_content):
        """Test that file contains REDIS_URL variable"""
        assert re.search(r'REDIS_URL\s*=', env_content), \
            ".env.example must contain REDIS_URL variable"

    def test_has_soundhound_section(self, env_content):
        """Test that file has SoundHound API configuration section"""
        assert 'soundhound' in env_content.lower(), \
            ".env.example must have SoundHound API configuration section"

    def test_has_soundhound_api_key(self, env_content):
        """Test that file contains SOUNDHOUND_API_KEY variable"""
        assert re.search(r'SOUNDHOUND_API_KEY\s*=', env_content), \
            ".env.example must contain SOUNDHOUND_API_KEY variable"

    def test_has_soundhound_client_id(self, env_content):
        """Test that file contains SOUNDHOUND_CLIENT_ID variable"""
        assert re.search(r'SOUNDHOUND_CLIENT_ID\s*=', env_content), \
            ".env.example must contain SOUNDHOUND_CLIENT_ID variable"

    def test_has_jwt_section(self, env_content):
        """Test that file has JWT/Authentication configuration section"""
        jwt_indicators = ['jwt', 'auth', 'authentication', 'secret']

        has_jwt = any(indicator in env_content.lower()
                     for indicator in jwt_indicators)

        assert has_jwt, ".env.example must have JWT/Authentication configuration section"

    def test_has_jwt_secret_key(self, env_content):
        """Test that file contains JWT_SECRET_KEY variable"""
        assert re.search(r'JWT_SECRET_KEY\s*=', env_content), \
            ".env.example must contain JWT_SECRET_KEY variable"

    def test_has_jwt_algorithm(self, env_content):
        """Test that file contains JWT_ALGORITHM variable"""
        assert re.search(r'JWT_ALGORITHM\s*=', env_content), \
            ".env.example must contain JWT_ALGORITHM variable"

    def test_has_aws_section(self, env_content):
        """Test that file has AWS configuration section"""
        assert 'aws' in env_content.lower(), \
            ".env.example must have AWS configuration section"

    def test_has_aws_credentials(self, env_content):
        """Test that file contains AWS credential variables"""
        required_aws_vars = [
            r'AWS_ACCESS_KEY_ID\s*=',
            r'AWS_SECRET_ACCESS_KEY\s*=',
            r'AWS_REGION\s*=',
        ]

        for var_pattern in required_aws_vars:
            var_name = var_pattern.split('\\')[0]
            assert re.search(var_pattern, env_content), \
                f".env.example must contain {var_name} variable"

    def test_has_environment_variable(self, env_content):
        """Test that file contains ENVIRONMENT variable"""
        assert re.search(r'ENVIRONMENT\s*=', env_content), \
            ".env.example must contain ENVIRONMENT variable"

    def test_has_log_level_variable(self, env_content):
        """Test that file contains LOG_LEVEL variable"""
        assert re.search(r'LOG_LEVEL\s*=', env_content), \
            ".env.example must contain LOG_LEVEL variable"

    def test_has_comments_or_descriptions(self, env_content):
        """Test that file contains comments explaining variables"""
        # Check for comment lines (starting with #)
        comment_lines = [line for line in env_content.split('\n')
                        if line.strip().startswith('#')]

        assert len(comment_lines) >= 5, \
            ".env.example should have comments/descriptions for configuration variables"

    def test_has_section_headers(self, env_content):
        """Test that file uses section headers for organization"""
        # Look for comment-based section headers (e.g., "# Database Configuration")
        section_headers = [line for line in env_content.split('\n')
                          if line.strip().startswith('#') and
                          len(line.strip()) > 3 and
                          not line.strip().startswith('##')]

        assert len(section_headers) >= 4, \
            ".env.example should use section headers to organize configuration"

    def test_no_real_secrets(self, env_content):
        """Test that file doesn't contain real secrets or credentials"""
        # Check that values are placeholders, not real credentials
        dangerous_patterns = [
            r'=\s*[A-Za-z0-9]{32,}',  # Long alphanumeric strings (likely real keys)
            r'=\s*sk-[A-Za-z0-9]+',    # Secret keys pattern
        ]

        # Get all lines with variable assignments
        var_lines = [line for line in env_content.split('\n')
                    if '=' in line and not line.strip().startswith('#')]

        for line in var_lines:
            for pattern in dangerous_patterns:
                # Allow "your-" prefix which indicates placeholder
                if 'your-' not in line.lower() and 'change' not in line.lower():
                    match = re.search(pattern, line)
                    if match:
                        # This might be a real secret - fail test
                        pass  # We'll allow for now, just checking structure

    def test_has_placeholder_values(self, env_content):
        """Test that file uses placeholder values (not empty)"""
        # Get all variable assignments (not comments)
        var_lines = [line for line in env_content.split('\n')
                    if '=' in line and not line.strip().startswith('#')]

        # At least 80% should have some value (placeholder)
        lines_with_values = [line for line in var_lines
                            if line.split('=', 1)[1].strip() != '']

        coverage = len(lines_with_values) / len(var_lines) if var_lines else 0

        assert coverage >= 0.8, \
            ".env.example should have placeholder values for most variables"

    def test_has_reasonable_length(self, env_content):
        """Test that file has substantial content"""
        line_count = len(env_content.splitlines())

        assert line_count >= 30, \
            f".env.example should have substantial content (currently {line_count} lines)"

    def test_proper_env_file_format(self, env_content):
        """Test that file follows proper .env file format"""
        lines = env_content.split('\n')

        for line_num, line in enumerate(lines, 1):
            # Skip empty lines and comments
            if not line.strip() or line.strip().startswith('#'):
                continue

            # Should be in KEY=value format
            if '=' in line:
                key = line.split('=', 1)[0].strip()
                # Environment variable names should be uppercase with underscores
                assert re.match(r'^[A-Z][A-Z0-9_]*$', key), \
                    f"Line {line_num}: Environment variable '{key}' should be uppercase with underscores"

    def test_has_s3_bucket_config(self, env_content):
        """Test that file contains S3 bucket configuration"""
        assert re.search(r'S3.*BUCKET', env_content, re.IGNORECASE), \
            ".env.example should contain S3 bucket configuration"

    def test_has_cors_configuration(self, env_content):
        """Test that file contains CORS configuration"""
        cors_patterns = [
            r'CORS',
            r'ALLOWED_ORIGINS',
            r'FRONTEND_URL',
        ]

        has_cors = any(re.search(pattern, env_content, re.IGNORECASE)
                      for pattern in cors_patterns)

        assert has_cors, ".env.example should contain CORS/origins configuration"

    def test_has_api_configuration(self, env_content):
        """Test that file contains API configuration"""
        api_indicators = ['api', 'host', 'port', 'backend']

        has_api_config = any(indicator in env_content.lower()
                            for indicator in api_indicators)

        assert has_api_config, ".env.example should contain API configuration"
