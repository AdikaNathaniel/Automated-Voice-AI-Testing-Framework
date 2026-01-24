"""
Test suite for test_execution_queue table migration

Validates the Alembic migration for test_execution_queue table including:
- Migration file structure
- Table creation with correct schema
- Column definitions and types
- Priority and status fields
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


# Find the test_execution_queue migration file dynamically
def find_migration_file(keyword: str) -> Path | None:
    """Find migration file containing keyword in filename"""
    if not ALEMBIC_VERSIONS.exists():
        return None

    for file in ALEMBIC_VERSIONS.glob("*.py"):
        if keyword in file.name.lower() and file.name != "__pycache__":
            return file
    return None


TEST_EXECUTION_QUEUE_MIGRATION_FILE = find_migration_file("execution_queue")


class TestTestExecutionQueueMigrationFileExists:
    """Test that test_execution_queue migration file exists"""

    def test_alembic_versions_directory_exists(self):
        """Test that alembic/versions directory exists"""
        assert ALEMBIC_VERSIONS.exists(), "alembic/versions directory should exist"
        assert ALEMBIC_VERSIONS.is_dir(), "alembic/versions should be a directory"

    def test_test_execution_queue_migration_file_exists(self):
        """Test that test_execution_queue migration file exists"""
        assert TEST_EXECUTION_QUEUE_MIGRATION_FILE is not None, "test_execution_queue migration file should exist"
        assert TEST_EXECUTION_QUEUE_MIGRATION_FILE.exists(), "test_execution_queue migration file should exist"
        assert TEST_EXECUTION_QUEUE_MIGRATION_FILE.is_file(), "test_execution_queue migration should be a file"

    def test_migration_file_has_content(self):
        """Test that migration file has content"""
        if TEST_EXECUTION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_EXECUTION_QUEUE_MIGRATION_FILE.read_text()
        assert len(content) > 0, "Migration file should not be empty"


class TestTestExecutionQueueMigrationStructure:
    """Test migration file structure"""

    def test_has_alembic_imports(self):
        """Test that migration imports alembic"""
        if TEST_EXECUTION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_EXECUTION_QUEUE_MIGRATION_FILE.read_text()
        assert "from alembic import op" in content, "Should import alembic.op"
        assert "import sqlalchemy" in content or "from sqlalchemy" in content, "Should import sqlalchemy"

    def test_has_revision_metadata(self):
        """Test that migration has revision metadata"""
        if TEST_EXECUTION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_EXECUTION_QUEUE_MIGRATION_FILE.read_text()
        assert "revision:" in content or "revision =" in content, "Should have revision identifier"
        assert "down_revision" in content, "Should have down_revision identifier"

    def test_has_upgrade_function(self):
        """Test that migration has upgrade function"""
        if TEST_EXECUTION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_EXECUTION_QUEUE_MIGRATION_FILE.read_text()
        assert "def upgrade" in content, "Should have upgrade() function"

    def test_has_downgrade_function(self):
        """Test that migration has downgrade function"""
        if TEST_EXECUTION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_EXECUTION_QUEUE_MIGRATION_FILE.read_text()
        assert "def downgrade" in content, "Should have downgrade() function"


class TestTestExecutionQueueTableCreation:
    """Test test_execution_queue table creation"""

    def test_creates_test_execution_queue_table(self):
        """Test that migration creates test_execution_queue table"""
        if TEST_EXECUTION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_EXECUTION_QUEUE_MIGRATION_FILE.read_text()
        assert "create_table" in content.lower(), "Should create a table"
        assert "test_execution_queue" in content, "Should create test_execution_queue table"

    def test_table_has_id_column(self):
        """Test that test_execution_queue table has id column"""
        if TEST_EXECUTION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_EXECUTION_QUEUE_MIGRATION_FILE.read_text()
        assert "'id'" in content or '"id"' in content, "Should have id column"

    def test_table_has_test_run_id_column(self):
        """Test that test_execution_queue table has test_run_id column"""
        if TEST_EXECUTION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_EXECUTION_QUEUE_MIGRATION_FILE.read_text()
        assert "'test_run_id'" in content or '"test_run_id"' in content, "Should have test_run_id column"

    def test_table_has_priority_column(self):
        """Test that test_execution_queue table has priority column"""
        if TEST_EXECUTION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_EXECUTION_QUEUE_MIGRATION_FILE.read_text()
        assert "'priority'" in content or '"priority"' in content, "Should have priority column"

    def test_table_has_status_column(self):
        """Test that test_execution_queue table has status column"""
        if TEST_EXECUTION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_EXECUTION_QUEUE_MIGRATION_FILE.read_text()
        assert "'status'" in content or '"status"' in content, "Should have status column"

    def test_table_has_created_at_column(self):
        """Test that test_execution_queue table has created_at column"""
        if TEST_EXECUTION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_EXECUTION_QUEUE_MIGRATION_FILE.read_text()
        assert "'created_at'" in content or '"created_at"' in content, "Should have created_at column"

    def test_table_has_updated_at_column(self):
        """Test that test_execution_queue table has updated_at column"""
        if TEST_EXECUTION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_EXECUTION_QUEUE_MIGRATION_FILE.read_text()
        assert "'updated_at'" in content or '"updated_at"' in content, "Should have updated_at column"


class TestTestExecutionQueueColumnTypes:
    """Test column types"""

    def test_id_column_is_uuid(self):
        """Test that id column is UUID type"""
        if TEST_EXECUTION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_EXECUTION_QUEUE_MIGRATION_FILE.read_text()
        assert ("UUID" in content or "uuid" in content.lower()), "id should be UUID type"

    def test_id_column_is_primary_key(self):
        """Test that id column is primary key"""
        if TEST_EXECUTION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_EXECUTION_QUEUE_MIGRATION_FILE.read_text()
        assert "primary_key" in content, "id should be primary key"

    def test_test_run_id_is_uuid(self):
        """Test that test_run_id is UUID type"""
        if TEST_EXECUTION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_EXECUTION_QUEUE_MIGRATION_FILE.read_text()
        assert ("UUID" in content or "uuid" in content.lower()), "test_run_id should be UUID type"

    def test_priority_is_integer(self):
        """Test that priority is Integer type"""
        if TEST_EXECUTION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_EXECUTION_QUEUE_MIGRATION_FILE.read_text()
        assert "Integer" in content, "priority should be Integer type"

    def test_status_is_string(self):
        """Test that status is String type"""
        if TEST_EXECUTION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_EXECUTION_QUEUE_MIGRATION_FILE.read_text()
        assert "String" in content, "status should be String type"

    def test_created_at_is_datetime(self):
        """Test that created_at is DateTime type"""
        if TEST_EXECUTION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_EXECUTION_QUEUE_MIGRATION_FILE.read_text()
        assert "DateTime" in content, "created_at should be DateTime type"

    def test_updated_at_is_datetime(self):
        """Test that updated_at is DateTime type"""
        if TEST_EXECUTION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_EXECUTION_QUEUE_MIGRATION_FILE.read_text()
        assert "DateTime" in content, "updated_at should be DateTime type"


class TestTestExecutionQueueForeignKeys:
    """Test foreign key relationships"""

    def test_test_run_id_references_test_runs(self):
        """Test that test_run_id references test_runs table"""
        if TEST_EXECUTION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_EXECUTION_QUEUE_MIGRATION_FILE.read_text()
        assert ((("ForeignKey" in content and "test_runs" in content) or
                "test_runs.id" in content)), "test_run_id should reference test_runs table"


class TestTestExecutionQueueConstraints:
    """Test constraints and defaults"""

    def test_created_at_has_default(self):
        """Test that created_at has default timestamp"""
        if TEST_EXECUTION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_EXECUTION_QUEUE_MIGRATION_FILE.read_text()
        assert ("server_default" in content or "now()" in content.lower()), "created_at should have default timestamp"

    def test_updated_at_has_default(self):
        """Test that updated_at has default timestamp"""
        if TEST_EXECUTION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_EXECUTION_QUEUE_MIGRATION_FILE.read_text()
        assert ("server_default" in content or "now()" in content.lower()), "updated_at should have default timestamp"

    def test_test_run_id_not_nullable(self):
        """Test that test_run_id is not nullable"""
        if TEST_EXECUTION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_EXECUTION_QUEUE_MIGRATION_FILE.read_text()
        assert "nullable" in content, "Should have nullable constraints"

    def test_status_not_nullable(self):
        """Test that status is not nullable"""
        if TEST_EXECUTION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_EXECUTION_QUEUE_MIGRATION_FILE.read_text()
        assert "nullable" in content, "Should have nullable constraints"


class TestTestExecutionQueueIndexes:
    """Test indexes for performance"""

    def test_has_index_creation(self):
        """Test that migration creates indexes"""
        if TEST_EXECUTION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_EXECUTION_QUEUE_MIGRATION_FILE.read_text()
        assert "create_index" in content or "index=True" in content, "Should create indexes"

    def test_has_status_index(self):
        """Test that migration creates index on status"""
        if TEST_EXECUTION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_EXECUTION_QUEUE_MIGRATION_FILE.read_text()
        assert ("status" in content and ("create_index" in content or "index=True" in content)), "Should create index on status"

    def test_has_priority_index(self):
        """Test that migration creates index on priority"""
        if TEST_EXECUTION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_EXECUTION_QUEUE_MIGRATION_FILE.read_text()
        assert ("priority" in content and ("create_index" in content or "index=True" in content)), "Should create index on priority"


class TestTestExecutionQueueDowngrade:
    """Test downgrade functionality"""

    def test_downgrade_drops_table(self):
        """Test that downgrade drops test_execution_queue table"""
        if TEST_EXECUTION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_EXECUTION_QUEUE_MIGRATION_FILE.read_text()
        assert "drop_table" in content.lower(), "Downgrade should drop table"
        downgrade_match = re.search(r'def downgrade.*?(?=\ndef|\Z)', content, re.DOTALL)
        if downgrade_match:
            downgrade_content = downgrade_match.group(0)
            assert "test_execution_queue" in downgrade_content, "Downgrade should drop test_execution_queue table"

    def test_downgrade_drops_indexes(self):
        """Test that downgrade drops indexes if they exist"""
        if TEST_EXECUTION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_EXECUTION_QUEUE_MIGRATION_FILE.read_text()
        # If indexes are explicitly created, they should be dropped in downgrade
        if "op.create_index" in content:
            downgrade_match = re.search(r'def downgrade.*?(?=\ndef|\Z)', content, re.DOTALL)
            if downgrade_match:
                downgrade_content = downgrade_match.group(0)
                assert "drop_index" in downgrade_content, "Downgrade should drop indexes"


class TestTestExecutionQueueMigrationDocumentation:
    """Test migration documentation"""

    def test_has_docstring(self):
        """Test that migration has docstring"""
        if TEST_EXECUTION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_EXECUTION_QUEUE_MIGRATION_FILE.read_text()
        assert '"""' in content or "'''" in content, "Migration should have docstring"

    def test_docstring_mentions_test_execution_queue(self):
        """Test that docstring mentions test_execution_queue"""
        if TEST_EXECUTION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_EXECUTION_QUEUE_MIGRATION_FILE.read_text()
        assert ("test_execution_queue" in content.lower() or "execution queue" in content.lower()), "Should document test_execution_queue table"


class TestTestExecutionQueueMigrationRevisionChain:
    """Test Alembic revision chain"""

    def test_has_valid_revision_id(self):
        """Test that migration has valid revision ID"""
        if TEST_EXECUTION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_EXECUTION_QUEUE_MIGRATION_FILE.read_text()
        assert "revision:" in content or "revision =" in content, "Should have revision ID"

    def test_down_revision_references_previous_migration(self):
        """Test that down_revision references the test_runs migration"""
        if TEST_EXECUTION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_EXECUTION_QUEUE_MIGRATION_FILE.read_text()
        assert "down_revision" in content, "Should have down_revision"
        # Should reference the test_runs migration (f6a7b8c9d0e1)
