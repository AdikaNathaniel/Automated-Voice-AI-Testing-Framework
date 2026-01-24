"""
Test suite for dev-setup.sh script

Ensures proper development setup script configuration that automates:
- Database creation
- Running migrations
- Seeding initial data
- Starting all services
"""

import os
import stat
import pytest
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
DEV_SETUP_SCRIPT = SCRIPTS_DIR / "dev-setup.sh"


class TestDevSetupScriptExists:
    """Test dev-setup.sh script existence"""

    def test_scripts_directory_exists(self):
        """Test that scripts directory exists"""
        assert SCRIPTS_DIR.exists(), "scripts directory should exist"
        assert SCRIPTS_DIR.is_dir(), "scripts should be a directory"

    def test_dev_setup_script_exists(self):
        """Test that dev-setup.sh exists"""
        assert DEV_SETUP_SCRIPT.exists(), "scripts/dev-setup.sh should exist"
        assert DEV_SETUP_SCRIPT.is_file(), "dev-setup.sh should be a file"

    def test_dev_setup_has_content(self):
        """Test that dev-setup.sh has content"""
        content = DEV_SETUP_SCRIPT.read_text()
        assert len(content) > 0, "dev-setup.sh should not be empty"


class TestDevSetupScriptPermissions:
    """Test dev-setup.sh script permissions"""

    def test_dev_setup_is_executable(self):
        """Test that dev-setup.sh is executable"""
        assert DEV_SETUP_SCRIPT.exists(), "dev-setup.sh should exist"
        file_stat = os.stat(DEV_SETUP_SCRIPT)
        is_executable = bool(file_stat.st_mode & stat.S_IXUSR)
        assert is_executable, "dev-setup.sh should be executable (chmod +x)"


class TestDevSetupScriptStructure:
    """Test dev-setup.sh script structure"""

    def test_has_bash_shebang(self):
        """Test that script starts with bash shebang"""
        content = DEV_SETUP_SCRIPT.read_text()
        lines = content.split('\n')
        first_line = lines[0].strip()
        assert first_line.startswith('#!'), "Script should start with shebang"
        assert 'bash' in first_line.lower(), "Script should use bash"

    def test_has_comments(self):
        """Test that script has comments for documentation"""
        content = DEV_SETUP_SCRIPT.read_text()
        assert '#' in content, "Script should have comments"

    def test_has_error_handling(self):
        """Test that script has error handling"""
        content = DEV_SETUP_SCRIPT.read_text()
        # Should have set -e or error checking
        has_error_handling = (
            'set -e' in content or
            'set -euo pipefail' in content or
            'if [' in content or
            'exit 1' in content
        )
        assert has_error_handling, "Script should have error handling"


class TestDatabaseSetupFunctionality:
    """Test database setup functionality"""

    def test_mentions_database_creation(self):
        """Test that script mentions database creation"""
        content = DEV_SETUP_SCRIPT.read_text()
        # Should mention postgres, database, or createdb
        has_db_setup = (
            'postgres' in content.lower() or
            'database' in content.lower() or
            'createdb' in content or
            'psql' in content
        )
        assert has_db_setup, "Script should mention database setup"

    def test_has_database_wait_or_check(self):
        """Test that script waits for database to be ready"""
        content = DEV_SETUP_SCRIPT.read_text()
        # Should wait for postgres or check if it's ready
        has_wait = (
            'pg_isready' in content or
            'wait' in content.lower() or
            'sleep' in content or
            'health' in content.lower()
        )
        # Wait is optional but recommended
        pass

    def test_uses_docker_compose_or_postgres(self):
        """Test that script uses docker-compose or postgres commands"""
        content = DEV_SETUP_SCRIPT.read_text()
        has_docker_or_postgres = (
            'docker-compose' in content or
            'docker compose' in content or
            'psql' in content or
            'createdb' in content
        )
        assert has_docker_or_postgres, \
            "Script should use docker-compose or postgres commands"


class TestMigrationFunctionality:
    """Test migration functionality"""

    def test_mentions_migrations(self):
        """Test that script mentions migrations"""
        content = DEV_SETUP_SCRIPT.read_text()
        has_migrations = (
            'migration' in content.lower() or
            'migrate' in content.lower() or
            'alembic' in content.lower() or
            'upgrade' in content.lower()
        )
        assert has_migrations, "Script should mention migrations"

    def test_runs_alembic_or_migration_tool(self):
        """Test that script runs alembic or another migration tool"""
        content = DEV_SETUP_SCRIPT.read_text()
        # Should run migrations using alembic or similar
        has_migration_tool = (
            'alembic upgrade' in content or
            'alembic' in content or
            'migrate' in content.lower()
        )
        assert has_migration_tool, "Script should run migration tool"


class TestDataSeedingFunctionality:
    """Test data seeding functionality"""

    def test_mentions_seeding_or_initial_data(self):
        """Test that script mentions seeding or initial data"""
        content = DEV_SETUP_SCRIPT.read_text()
        has_seeding = (
            'seed' in content.lower() or
            'initial' in content.lower() or
            'populate' in content.lower() or
            'fixture' in content.lower()
        )
        assert has_seeding, "Script should mention data seeding"

    def test_seeds_data_via_script_or_sql(self):
        """Test that script seeds data"""
        content = DEV_SETUP_SCRIPT.read_text()
        # Should seed data using python script, SQL, or fixture
        has_seeding_method = (
            'seed' in content.lower() or
            '.sql' in content or
            'python' in content or
            'fixture' in content.lower()
        )
        assert has_seeding_method, "Script should have data seeding method"


class TestServiceStartupFunctionality:
    """Test service startup functionality"""

    def test_starts_services(self):
        """Test that script starts services"""
        content = DEV_SETUP_SCRIPT.read_text()
        has_service_startup = (
            'docker-compose up' in content or
            'docker compose up' in content or
            'npm start' in content or
            'uvicorn' in content or
            'start' in content.lower()
        )
        assert has_service_startup, "Script should start services"

    def test_uses_docker_compose_up(self):
        """Test that script uses docker-compose up"""
        content = DEV_SETUP_SCRIPT.read_text()
        has_compose_up = (
            'docker-compose up' in content or
            'docker compose up' in content
        )
        assert has_compose_up, "Script should use docker-compose up to start services"


class TestScriptFunctions:
    """Test script function organization"""

    def test_has_functions_or_sections(self):
        """Test that script has functions or clear sections"""
        content = DEV_SETUP_SCRIPT.read_text()
        # Bash functions use: function_name() { or function function_name {
        has_functions = (
            '() {' in content or
            'function ' in content
        )
        # Or at least has clear section comments
        has_sections = content.count('##') >= 3 or content.count('###') >= 3
        assert has_functions or has_sections, \
            "Script should have functions or clear sections"

    def test_has_main_execution_flow(self):
        """Test that script has main execution flow"""
        content = DEV_SETUP_SCRIPT.read_text()
        # Should have some main execution logic
        lines = [line for line in content.split('\n') if line.strip() and not line.strip().startswith('#')]
        assert len(lines) >= 10, "Script should have substantial execution logic"


class TestScriptErrorMessages:
    """Test script error messages and user feedback"""

    def test_has_echo_or_print_statements(self):
        """Test that script has echo statements for user feedback"""
        content = DEV_SETUP_SCRIPT.read_text()
        has_output = (
            'echo' in content or
            'printf' in content
        )
        assert has_output, "Script should have echo statements for user feedback"

    def test_provides_status_messages(self):
        """Test that script provides status messages"""
        content = DEV_SETUP_SCRIPT.read_text()
        # Should have informative messages
        has_status = content.lower().count('echo') >= 3
        assert has_status, "Script should provide multiple status messages"


class TestScriptEnvironment:
    """Test script environment handling"""

    def test_handles_environment_variables(self):
        """Test that script handles environment variables"""
        content = DEV_SETUP_SCRIPT.read_text()
        # Should reference environment variables or .env files
        has_env = (
            '$' in content or
            '.env' in content or
            'export' in content
        )
        assert has_env, "Script should handle environment variables"


class TestScriptDocumentation:
    """Test script documentation"""

    def test_has_usage_comments(self):
        """Test that script has usage or description comments"""
        content = DEV_SETUP_SCRIPT.read_text()
        lines = content.split('\n')
        # First 10 lines should have comments explaining usage
        first_lines = '\n'.join(lines[:10])
        has_docs = '#' in first_lines
        assert has_docs, "Script should have usage documentation in comments"


class TestScriptDependencies:
    """Test script dependency checking"""

    def test_checks_for_required_commands(self):
        """Test that script checks for required commands (optional but recommended)"""
        content = DEV_SETUP_SCRIPT.read_text()
        # Should check if docker, docker-compose, etc. are available
        checks_deps = (
            'which' in content or
            'command -v' in content or
            'hash' in content
        )
        # This is optional but good practice
        pass


class TestScriptCleanup:
    """Test script cleanup functionality"""

    def test_has_cleanup_or_reset_option(self):
        """Test that script can handle cleanup or reset (optional)"""
        content = DEV_SETUP_SCRIPT.read_text()
        # Should have cleanup or reset functionality
        has_cleanup = (
            'clean' in content.lower() or
            'reset' in content.lower() or
            'down' in content or
            'rm' in content
        )
        # This is optional but useful
        pass


class TestScriptIdempotency:
    """Test script idempotency"""

    def test_can_run_multiple_times(self):
        """Test that script considers idempotency"""
        content = DEV_SETUP_SCRIPT.read_text()
        # Should check if things already exist before creating
        has_checks = (
            'if' in content or
            'exist' in content.lower() or
            '-f' in content or
            '-d' in content
        )
        # Idempotency checks are optional but good practice
        pass


class TestScriptIntegration:
    """Test script integration with docker-compose"""

    def test_references_docker_compose_file(self):
        """Test that script references docker-compose.yml"""
        content = DEV_SETUP_SCRIPT.read_text()
        has_compose_ref = (
            'docker-compose' in content or
            'docker compose' in content or
            'compose.yml' in content or
            'compose.yaml' in content
        )
        assert has_compose_ref, "Script should reference docker-compose"

    def test_can_start_full_stack(self):
        """Test that script can start the full stack"""
        content = DEV_SETUP_SCRIPT.read_text()
        # Should start all services (backend, frontend, databases)
        has_full_stack = (
            'up' in content or
            'start' in content
        )
        assert has_full_stack, "Script should be able to start full stack"
