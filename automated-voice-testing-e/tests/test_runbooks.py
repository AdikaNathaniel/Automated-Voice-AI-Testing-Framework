"""
Test suite for operations runbook documentation.

This module tests that runbooks exist and contain required operational procedures:
- Restarting services
- Rotating SoundHound credentials
- Investigating failed test runs and high queue depth
"""

from pathlib import Path

import pytest


class TestRunbookFileExists:
    """Test that runbook documentation file exists"""

    @pytest.fixture
    def project_root(self):
        """Get project root directory"""
        return Path(__file__).parent.parent

    @pytest.fixture
    def docs_dir(self, project_root):
        """Get docs directory"""
        return project_root / "docs"

    def test_docs_directory_exists(self, docs_dir):
        """Test that docs directory exists"""
        assert docs_dir.exists(), "docs directory should exist"

    def test_runbook_file_exists(self, docs_dir):
        """Test that runbook file exists"""
        runbook_path = docs_dir / "RUNBOOK.md"
        assert runbook_path.exists(), \
            "RUNBOOK.md should exist in docs/"


class TestRunbookRestartingServices:
    """Test runbook contains restarting services procedures"""

    @pytest.fixture
    def project_root(self):
        """Get project root directory"""
        return Path(__file__).parent.parent

    @pytest.fixture
    def runbook_content(self, project_root):
        """Load runbook content"""
        runbook_path = project_root / "docs" / "RUNBOOK.md"
        with open(runbook_path) as f:
            return f.read()

    def test_has_restart_section(self, runbook_content):
        """Test that runbook has restart services section"""
        runbook_lower = runbook_content.lower()
        has_restart = 'restart' in runbook_lower
        assert has_restart, \
            "Runbook should have section for restarting services"

    def test_documents_docker_compose_restart(self, runbook_content):
        """Test that runbook documents docker-compose restart"""
        has_docker_restart = 'docker-compose restart' in runbook_content or \
                            'docker compose restart' in runbook_content
        assert has_docker_restart, \
            "Runbook should document docker-compose restart command"

    def test_documents_individual_service_restart(self, runbook_content):
        """Test that runbook documents individual service restart"""
        runbook_lower = runbook_content.lower()
        services = ['backend', 'frontend', 'postgres', 'redis']

        service_mentioned = any(
            service in runbook_lower for service in services
        )
        assert service_mentioned, \
            "Runbook should mention individual services for restart"

    def test_has_health_check_verification(self, runbook_content):
        """Test that runbook includes health check after restart"""
        runbook_lower = runbook_content.lower()
        has_health = 'health' in runbook_lower
        assert has_health, \
            "Runbook should include health check verification after restart"


class TestRunbookCredentialRotation:
    """Test runbook contains credential rotation procedures"""

    @pytest.fixture
    def project_root(self):
        """Get project root directory"""
        return Path(__file__).parent.parent

    @pytest.fixture
    def runbook_content(self, project_root):
        """Load runbook content"""
        runbook_path = project_root / "docs" / "RUNBOOK.md"
        with open(runbook_path) as f:
            return f.read()

    def test_has_credential_rotation_section(self, runbook_content):
        """Test that runbook has credential rotation section"""
        runbook_lower = runbook_content.lower()
        has_rotation = 'credential' in runbook_lower or 'rotation' in runbook_lower
        assert has_rotation, \
            "Runbook should have section for credential rotation"

    def test_documents_soundhound_credentials(self, runbook_content):
        """Test that runbook documents SoundHound credential rotation"""
        runbook_lower = runbook_content.lower()
        has_soundhound = 'soundhound' in runbook_lower or 'houndify' in runbook_lower
        assert has_soundhound, \
            "Runbook should document SoundHound/Houndify credential rotation"

    def test_documents_env_variable_update(self, runbook_content):
        """Test that runbook documents environment variable updates"""
        runbook_lower = runbook_content.lower()
        has_env = 'env' in runbook_lower or 'environment' in runbook_lower
        assert has_env, \
            "Runbook should document environment variable updates"

    def test_documents_service_restart_after_rotation(self, runbook_content):
        """Test that runbook documents service restart after credential rotation"""
        runbook_lower = runbook_content.lower()
        # After rotating credentials, services must be restarted
        has_restart = 'restart' in runbook_lower
        assert has_restart, \
            "Runbook should document service restart after credential rotation"


class TestRunbookInvestigatingFailures:
    """Test runbook contains failure investigation procedures"""

    @pytest.fixture
    def project_root(self):
        """Get project root directory"""
        return Path(__file__).parent.parent

    @pytest.fixture
    def runbook_content(self, project_root):
        """Load runbook content"""
        runbook_path = project_root / "docs" / "RUNBOOK.md"
        with open(runbook_path) as f:
            return f.read()

    def test_has_investigation_section(self, runbook_content):
        """Test that runbook has failure investigation section"""
        runbook_lower = runbook_content.lower()
        has_investigation = 'investigat' in runbook_lower or 'troubleshoot' in runbook_lower
        assert has_investigation, \
            "Runbook should have section for investigating failures"

    def test_documents_queue_depth_investigation(self, runbook_content):
        """Test that runbook documents queue depth investigation"""
        runbook_lower = runbook_content.lower()
        has_queue = 'queue' in runbook_lower
        assert has_queue, \
            "Runbook should document queue depth investigation"

    def test_documents_log_checking(self, runbook_content):
        """Test that runbook documents log checking procedures"""
        runbook_lower = runbook_content.lower()
        has_logs = 'log' in runbook_lower
        assert has_logs, \
            "Runbook should document log checking procedures"

    def test_documents_metrics_checking(self, runbook_content):
        """Test that runbook documents metrics checking"""
        runbook_lower = runbook_content.lower()
        has_metrics = 'metric' in runbook_lower or 'prometheus' in runbook_lower or 'grafana' in runbook_lower
        assert has_metrics, \
            "Runbook should document metrics checking procedures"

    def test_documents_database_connection_check(self, runbook_content):
        """Test that runbook documents database connection checks"""
        runbook_lower = runbook_content.lower()
        has_db_check = 'database' in runbook_lower or 'postgres' in runbook_lower
        assert has_db_check, \
            "Runbook should document database connection checks"


class TestRunbookCompleteness:
    """Test overall runbook completeness"""

    @pytest.fixture
    def project_root(self):
        """Get project root directory"""
        return Path(__file__).parent.parent

    @pytest.fixture
    def runbook_content(self, project_root):
        """Load runbook content"""
        runbook_path = project_root / "docs" / "RUNBOOK.md"
        with open(runbook_path) as f:
            return f.read()

    def test_has_table_of_contents(self, runbook_content):
        """Test that runbook has table of contents or clear sections"""
        # Should have multiple sections with headers
        header_count = runbook_content.count('## ')
        assert header_count >= 3, \
            "Runbook should have at least 3 major sections"

    def test_has_contact_information(self, runbook_content):
        """Test that runbook has escalation/contact information"""
        runbook_lower = runbook_content.lower()
        has_contact = 'contact' in runbook_lower or 'escalat' in runbook_lower or 'support' in runbook_lower
        assert has_contact, \
            "Runbook should have contact/escalation information"

    def test_runbook_is_markdown_formatted(self, runbook_content):
        """Test that runbook is properly formatted markdown"""
        # Should have at least title and code blocks
        has_title = runbook_content.startswith('#')
        has_code_blocks = '```' in runbook_content

        assert has_title, "Runbook should start with markdown title"
        assert has_code_blocks, "Runbook should have code blocks for commands"
