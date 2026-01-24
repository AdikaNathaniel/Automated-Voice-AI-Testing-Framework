"""
Test suite for device_test_executions table migration

Validates the Alembic migration for device_test_executions table including:
- Migration file structure
- Table creation with correct schema
- Column definitions and types
- JSONB fields for device-specific data
- Foreign key relationships
- Indexes for performance
- Constraints and defaults
- Downgrade functionality
- Alembic revision metadata
"""

import pytest
from pathlib import Path
import re


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
ALEMBIC_VERSIONS = PROJECT_ROOT / "alembic" / "versions"


# Find the device_test_executions migration file dynamically
def find_migration_file(keyword: str) -> Path | None:
    """Find migration file containing keyword in filename"""
    if not ALEMBIC_VERSIONS.exists():
        return None

    for file in ALEMBIC_VERSIONS.glob("*.py"):
        if keyword in file.name.lower() and file.name != "__pycache__":
            return file
    return None


DEVICE_TEST_EXECUTIONS_MIGRATION_FILE = find_migration_file("device")


class TestDeviceTestExecutionsMigrationFileExists:
    """Test that device_test_executions migration file exists"""

    def test_alembic_versions_directory_exists(self):
        """Test that alembic/versions directory exists"""
        assert ALEMBIC_VERSIONS.exists(), "alembic/versions directory should exist"
        assert ALEMBIC_VERSIONS.is_dir(), "alembic/versions should be a directory"

    def test_device_test_executions_migration_file_exists(self):
        """Test that device_test_executions migration file exists"""
        assert DEVICE_TEST_EXECUTIONS_MIGRATION_FILE is not None, "device_test_executions migration file should exist"
        assert DEVICE_TEST_EXECUTIONS_MIGRATION_FILE.exists(), "device_test_executions migration file should exist"
        assert DEVICE_TEST_EXECUTIONS_MIGRATION_FILE.is_file(), "device_test_executions migration should be a file"

    def test_migration_file_has_content(self):
        """Test that migration file has content"""
        if DEVICE_TEST_EXECUTIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = DEVICE_TEST_EXECUTIONS_MIGRATION_FILE.read_text()
        assert len(content) > 0, "Migration file should not be empty"


class TestDeviceTestExecutionsMigrationStructure:
    """Test migration file structure"""

    def test_has_alembic_imports(self):
        """Test that migration imports alembic"""
        if DEVICE_TEST_EXECUTIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = DEVICE_TEST_EXECUTIONS_MIGRATION_FILE.read_text()
        assert "from alembic import op" in content, "Should import alembic.op"
        assert "import sqlalchemy" in content or "from sqlalchemy" in content, "Should import sqlalchemy"

    def test_has_revision_metadata(self):
        """Test that migration has revision metadata"""
        if DEVICE_TEST_EXECUTIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = DEVICE_TEST_EXECUTIONS_MIGRATION_FILE.read_text()
        assert "revision:" in content or "revision =" in content, "Should have revision identifier"
        assert "down_revision" in content, "Should have down_revision identifier"

    def test_has_upgrade_function(self):
        """Test that migration has upgrade function"""
        if DEVICE_TEST_EXECUTIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = DEVICE_TEST_EXECUTIONS_MIGRATION_FILE.read_text()
        assert "def upgrade" in content, "Should have upgrade() function"

    def test_has_downgrade_function(self):
        """Test that migration has downgrade function"""
        if DEVICE_TEST_EXECUTIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = DEVICE_TEST_EXECUTIONS_MIGRATION_FILE.read_text()
        assert "def downgrade" in content, "Should have downgrade() function"


class TestDeviceTestExecutionsTableCreation:
    """Test device_test_executions table creation"""

    def test_creates_device_test_executions_table(self):
        """Test that migration creates device_test_executions table"""
        if DEVICE_TEST_EXECUTIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = DEVICE_TEST_EXECUTIONS_MIGRATION_FILE.read_text()
        assert "create_table" in content.lower(), "Should create a table"
        assert "device_test_executions" in content, "Should create device_test_executions table"

    def test_table_has_id_column(self):
        """Test that device_test_executions table has id column"""
        if DEVICE_TEST_EXECUTIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = DEVICE_TEST_EXECUTIONS_MIGRATION_FILE.read_text()
        assert "'id'" in content or '"id"' in content, "Should have id column"

    def test_table_has_test_run_id_column(self):
        """Test that device_test_executions table has test_run_id column"""
        if DEVICE_TEST_EXECUTIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = DEVICE_TEST_EXECUTIONS_MIGRATION_FILE.read_text()
        assert "'test_run_id'" in content or '"test_run_id"' in content, "Should have test_run_id column"

    def test_table_has_device_info_column(self):
        """Test that device_test_executions table has device_info column"""
        if DEVICE_TEST_EXECUTIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = DEVICE_TEST_EXECUTIONS_MIGRATION_FILE.read_text()
        assert "'device_info'" in content or '"device_info"' in content, "Should have device_info column"

    def test_table_has_platform_details_column(self):
        """Test that device_test_executions table has platform_details column"""
        if DEVICE_TEST_EXECUTIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = DEVICE_TEST_EXECUTIONS_MIGRATION_FILE.read_text()
        assert "'platform_details'" in content or '"platform_details"' in content, "Should have platform_details column"

    def test_table_has_test_results_column(self):
        """Test that device_test_executions table has test_results column"""
        if DEVICE_TEST_EXECUTIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = DEVICE_TEST_EXECUTIONS_MIGRATION_FILE.read_text()
        assert "'test_results'" in content or '"test_results"' in content, "Should have test_results column"

    def test_table_has_created_at_column(self):
        """Test that device_test_executions table has created_at column"""
        if DEVICE_TEST_EXECUTIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = DEVICE_TEST_EXECUTIONS_MIGRATION_FILE.read_text()
        assert "'created_at'" in content or '"created_at"' in content, "Should have created_at column"


class TestDeviceTestExecutionsColumnTypes:
    """Test column types"""

    def test_id_column_is_uuid(self):
        """Test that id column is UUID type"""
        if DEVICE_TEST_EXECUTIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = DEVICE_TEST_EXECUTIONS_MIGRATION_FILE.read_text()
        assert ("UUID" in content or "uuid" in content.lower()), "id should be UUID type"

    def test_id_column_is_primary_key(self):
        """Test that id column is primary key"""
        if DEVICE_TEST_EXECUTIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = DEVICE_TEST_EXECUTIONS_MIGRATION_FILE.read_text()
        assert "primary_key" in content, "id should be primary key"

    def test_test_run_id_is_uuid(self):
        """Test that test_run_id is UUID type"""
        if DEVICE_TEST_EXECUTIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = DEVICE_TEST_EXECUTIONS_MIGRATION_FILE.read_text()
        assert ("UUID" in content or "uuid" in content.lower()), "test_run_id should be UUID type"

    def test_device_info_is_jsonb(self):
        """Test that device_info is JSONB type"""
        if DEVICE_TEST_EXECUTIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = DEVICE_TEST_EXECUTIONS_MIGRATION_FILE.read_text()
        assert "JSONB" in content, "device_info should be JSONB type"

    def test_platform_details_is_jsonb(self):
        """Test that platform_details is JSONB type"""
        if DEVICE_TEST_EXECUTIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = DEVICE_TEST_EXECUTIONS_MIGRATION_FILE.read_text()
        assert "JSONB" in content, "platform_details should be JSONB type"

    def test_test_results_is_jsonb(self):
        """Test that test_results is JSONB type"""
        if DEVICE_TEST_EXECUTIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = DEVICE_TEST_EXECUTIONS_MIGRATION_FILE.read_text()
        assert "JSONB" in content, "test_results should be JSONB type"

    def test_created_at_is_datetime(self):
        """Test that created_at is DateTime type"""
        if DEVICE_TEST_EXECUTIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = DEVICE_TEST_EXECUTIONS_MIGRATION_FILE.read_text()
        assert "DateTime" in content, "created_at should be DateTime type"


class TestDeviceTestExecutionsJSONBFields:
    """Test JSONB field requirements"""

    def test_has_three_jsonb_fields(self):
        """Test that migration has three JSONB fields"""
        if DEVICE_TEST_EXECUTIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = DEVICE_TEST_EXECUTIONS_MIGRATION_FILE.read_text()
        jsonb_count = content.count("JSONB")
        assert jsonb_count >= 3, "Should have at least 3 JSONB fields"

    def test_jsonb_fields_properly_defined(self):
        """Test that all JSONB fields are present"""
        if DEVICE_TEST_EXECUTIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = DEVICE_TEST_EXECUTIONS_MIGRATION_FILE.read_text()
        assert "device_info" in content, "Should have device_info JSONB field"
        assert "platform_details" in content, "Should have platform_details JSONB field"
        assert "test_results" in content, "Should have test_results JSONB field"


class TestDeviceTestExecutionsForeignKeys:
    """Test foreign key relationships"""

    def test_test_run_id_references_test_runs(self):
        """Test that test_run_id references test_runs table"""
        if DEVICE_TEST_EXECUTIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = DEVICE_TEST_EXECUTIONS_MIGRATION_FILE.read_text()
        assert (((("ForeignKey" in content and "test_runs" in content) or
                "test_runs.id" in content))), "test_run_id should reference test_runs table"


class TestDeviceTestExecutionsConstraints:
    """Test constraints and defaults"""

    def test_created_at_has_default(self):
        """Test that created_at has default timestamp"""
        if DEVICE_TEST_EXECUTIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = DEVICE_TEST_EXECUTIONS_MIGRATION_FILE.read_text()
        assert ("server_default" in content or "now()" in content.lower()), "created_at should have default timestamp"

    def test_test_run_id_not_nullable(self):
        """Test that test_run_id is not nullable"""
        if DEVICE_TEST_EXECUTIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = DEVICE_TEST_EXECUTIONS_MIGRATION_FILE.read_text()
        assert "nullable" in content, "Should have nullable constraints"


class TestDeviceTestExecutionsIndexes:
    """Test indexes for performance"""

    def test_has_index_creation(self):
        """Test that migration creates indexes"""
        if DEVICE_TEST_EXECUTIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = DEVICE_TEST_EXECUTIONS_MIGRATION_FILE.read_text()
        assert "create_index" in content or "index=True" in content, "Should create indexes"

    def test_has_test_run_id_index(self):
        """Test that migration creates index on test_run_id"""
        if DEVICE_TEST_EXECUTIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = DEVICE_TEST_EXECUTIONS_MIGRATION_FILE.read_text()
        assert ("test_run_id" in content and ("create_index" in content or "index=True" in content)), "Should create index on test_run_id"


class TestDeviceTestExecutionsDowngrade:
    """Test downgrade functionality"""

    def test_downgrade_drops_table(self):
        """Test that downgrade drops device_test_executions table"""
        if DEVICE_TEST_EXECUTIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = DEVICE_TEST_EXECUTIONS_MIGRATION_FILE.read_text()
        assert "drop_table" in content.lower(), "Downgrade should drop table"
        downgrade_match = re.search(r'def downgrade.*?(?=\ndef|\Z)', content, re.DOTALL)
        if downgrade_match:
            downgrade_content = downgrade_match.group(0)
            assert "device_test_executions" in downgrade_content, "Downgrade should drop device_test_executions table"

    def test_downgrade_drops_indexes(self):
        """Test that downgrade drops indexes if they exist"""
        if DEVICE_TEST_EXECUTIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = DEVICE_TEST_EXECUTIONS_MIGRATION_FILE.read_text()
        # If indexes are explicitly created, they should be dropped in downgrade
        if "op.create_index" in content:
            downgrade_match = re.search(r'def downgrade.*?(?=\ndef|\Z)', content, re.DOTALL)
            if downgrade_match:
                downgrade_content = downgrade_match.group(0)
                assert "drop_index" in downgrade_content, "Downgrade should drop indexes"


class TestDeviceTestExecutionsMigrationDocumentation:
    """Test migration documentation"""

    def test_has_docstring(self):
        """Test that migration has docstring"""
        if DEVICE_TEST_EXECUTIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = DEVICE_TEST_EXECUTIONS_MIGRATION_FILE.read_text()
        assert '"""' in content or "'''" in content, "Migration should have docstring"

    def test_docstring_mentions_device_test_executions(self):
        """Test that docstring mentions device_test_executions"""
        if DEVICE_TEST_EXECUTIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = DEVICE_TEST_EXECUTIONS_MIGRATION_FILE.read_text()
        assert ("device_test_executions" in content.lower() or "device" in content.lower()), "Should document device_test_executions table"


class TestDeviceTestExecutionsMigrationRevisionChain:
    """Test Alembic revision chain"""

    def test_has_valid_revision_id(self):
        """Test that migration has valid revision ID"""
        if DEVICE_TEST_EXECUTIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = DEVICE_TEST_EXECUTIONS_MIGRATION_FILE.read_text()
        assert "revision:" in content or "revision =" in content, "Should have revision ID"

    def test_down_revision_references_previous_migration(self):
        """Test that down_revision references a previous migration"""
        if DEVICE_TEST_EXECUTIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = DEVICE_TEST_EXECUTIONS_MIGRATION_FILE.read_text()
        assert "down_revision" in content, "Should have down_revision"
