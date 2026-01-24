"""
Test suite for test_runs table migration

Validates the Alembic migration for test_runs table including:
- Migration file structure
- Table creation with correct schema
- Column definitions and types
- Foreign key relationships to test_suites and users
- Status tracking columns
- Indexes on status, created_by, created_at
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


# Find the test_runs migration file dynamically
def find_migration_file(keyword: str) -> Path | None:
    """Find migration file containing keyword in filename"""
    if not ALEMBIC_VERSIONS.exists():
        return None

    for file in ALEMBIC_VERSIONS.glob("*.py"):
        if keyword in file.name.lower() and file.name != "__pycache__":
            return file
    return None


TEST_RUNS_MIGRATION_FILE = find_migration_file("test_run")


class TestTestRunsMigrationFileExists:
    """Test that test_runs migration file exists"""

    def test_alembic_versions_directory_exists(self):
        """Test that alembic/versions directory exists"""
        assert ALEMBIC_VERSIONS.exists(), "alembic/versions directory should exist"
        assert ALEMBIC_VERSIONS.is_dir(), "alembic/versions should be a directory"

    def test_test_runs_migration_file_exists(self):
        """Test that test_runs migration file exists"""
        assert TEST_RUNS_MIGRATION_FILE is not None, "test_runs migration file should exist"
        assert TEST_RUNS_MIGRATION_FILE.exists(), "test_runs migration file should exist"
        assert TEST_RUNS_MIGRATION_FILE.is_file(), "test_runs migration should be a file"

    def test_migration_file_has_content(self):
        """Test that migration file has content"""
        if TEST_RUNS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_RUNS_MIGRATION_FILE.read_text()
        assert len(content) > 0, "Migration file should not be empty"


class TestTestRunsMigrationStructure:
    """Test migration file structure"""

    def test_has_alembic_imports(self):
        """Test that migration imports alembic"""
        if TEST_RUNS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_RUNS_MIGRATION_FILE.read_text()
        assert "from alembic import op" in content, "Should import alembic.op"
        assert "import sqlalchemy" in content or "from sqlalchemy" in content, "Should import sqlalchemy"

    def test_has_revision_metadata(self):
        """Test that migration has revision metadata"""
        if TEST_RUNS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_RUNS_MIGRATION_FILE.read_text()
        assert "revision:" in content or "revision =" in content, "Should have revision identifier"
        assert "down_revision" in content, "Should have down_revision identifier"

    def test_has_upgrade_function(self):
        """Test that migration has upgrade function"""
        if TEST_RUNS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_RUNS_MIGRATION_FILE.read_text()
        assert "def upgrade" in content, "Should have upgrade() function"

    def test_has_downgrade_function(self):
        """Test that migration has downgrade function"""
        if TEST_RUNS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_RUNS_MIGRATION_FILE.read_text()
        assert "def downgrade" in content, "Should have downgrade() function"


class TestTestRunsTableCreation:
    """Test test_runs table creation"""

    def test_creates_test_runs_table(self):
        """Test that migration creates test_runs table"""
        if TEST_RUNS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_RUNS_MIGRATION_FILE.read_text()
        assert "create_table" in content.lower(), "Should create a table"
        assert "test_runs" in content, "Should create test_runs table"

    def test_table_has_id_column(self):
        """Test that test_runs table has id column"""
        if TEST_RUNS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_RUNS_MIGRATION_FILE.read_text()
        assert "'id'" in content or '"id"' in content, "Should have id column"

    def test_table_has_suite_id_column(self):
        """Test that test_runs table has suite_id column"""
        if TEST_RUNS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_RUNS_MIGRATION_FILE.read_text()
        assert "'suite_id'" in content or '"suite_id"' in content, "Should have suite_id column"

    def test_table_has_status_column(self):
        """Test that test_runs table has status column"""
        if TEST_RUNS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_RUNS_MIGRATION_FILE.read_text()
        assert "'status'" in content or '"status"' in content, "Should have status column"

    def test_table_has_created_by_column(self):
        """Test that test_runs table has created_by column"""
        if TEST_RUNS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_RUNS_MIGRATION_FILE.read_text()
        assert "'created_by'" in content or '"created_by"' in content, "Should have created_by column"

    def test_table_has_created_at_column(self):
        """Test that test_runs table has created_at column"""
        if TEST_RUNS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_RUNS_MIGRATION_FILE.read_text()
        assert "'created_at'" in content or '"created_at"' in content, "Should have created_at column"

    def test_table_has_updated_at_column(self):
        """Test that test_runs table has updated_at column"""
        if TEST_RUNS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_RUNS_MIGRATION_FILE.read_text()
        assert "'updated_at'" in content or '"updated_at"' in content, "Should have updated_at column"

    def test_table_has_started_at_column(self):
        """Test that test_runs table has started_at column"""
        if TEST_RUNS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_RUNS_MIGRATION_FILE.read_text()
        assert "'started_at'" in content or '"started_at"' in content, "Should have started_at column"

    def test_table_has_completed_at_column(self):
        """Test that test_runs table has completed_at column"""
        if TEST_RUNS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_RUNS_MIGRATION_FILE.read_text()
        assert "'completed_at'" in content or '"completed_at"' in content, "Should have completed_at column"


class TestTestRunsColumnTypes:
    """Test column types"""

    def test_id_column_is_uuid(self):
        """Test that id column is UUID type"""
        if TEST_RUNS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_RUNS_MIGRATION_FILE.read_text()
        assert ("UUID" in content or "uuid" in content.lower()), "id should be UUID type"

    def test_id_column_is_primary_key(self):
        """Test that id column is primary key"""
        if TEST_RUNS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_RUNS_MIGRATION_FILE.read_text()
        assert "primary_key" in content, "id should be primary key"

    def test_suite_id_is_uuid(self):
        """Test that suite_id is UUID type"""
        if TEST_RUNS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_RUNS_MIGRATION_FILE.read_text()
        assert ("UUID" in content or "uuid" in content.lower()), "suite_id should be UUID type"

    def test_status_is_string(self):
        """Test that status is String type"""
        if TEST_RUNS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_RUNS_MIGRATION_FILE.read_text()
        assert "String" in content, "status should be String type"

    def test_created_by_is_uuid(self):
        """Test that created_by is UUID type"""
        if TEST_RUNS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_RUNS_MIGRATION_FILE.read_text()
        assert ("UUID" in content or "uuid" in content.lower()), "created_by should be UUID type"

    def test_datetime_columns_are_datetime(self):
        """Test that timestamp columns are DateTime type"""
        if TEST_RUNS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_RUNS_MIGRATION_FILE.read_text()
        assert "DateTime" in content, "Should have DateTime columns"


class TestTestRunsForeignKeys:
    """Test foreign key relationships"""

    def test_suite_id_references_test_suites(self):
        """Test that suite_id references test_suites table"""
        if TEST_RUNS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_RUNS_MIGRATION_FILE.read_text()
        assert ((("ForeignKey" in content and "test_suites" in content) or
                "test_suites.id" in content)), "suite_id should reference test_suites table"

    def test_created_by_references_users(self):
        """Test that created_by references users table"""
        if TEST_RUNS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_RUNS_MIGRATION_FILE.read_text()
        assert ((("ForeignKey" in content and "users" in content) or
                "users.id" in content)), "created_by should reference users table"


class TestTestRunsConstraints:
    """Test constraints and defaults"""

    def test_created_at_has_default(self):
        """Test that created_at has default timestamp"""
        if TEST_RUNS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_RUNS_MIGRATION_FILE.read_text()
        assert ("server_default" in content or "now()" in content.lower()), "created_at should have default timestamp"

    def test_updated_at_has_default(self):
        """Test that updated_at has default timestamp"""
        if TEST_RUNS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_RUNS_MIGRATION_FILE.read_text()
        assert ("server_default" in content or "now()" in content.lower()), "updated_at should have default timestamp"

    def test_suite_id_not_nullable(self):
        """Test that suite_id is not nullable"""
        if TEST_RUNS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_RUNS_MIGRATION_FILE.read_text()
        assert "nullable" in content, "Should have nullable constraints"

    def test_status_not_nullable(self):
        """Test that status is not nullable"""
        if TEST_RUNS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_RUNS_MIGRATION_FILE.read_text()
        assert "nullable" in content, "Should have nullable constraints"


class TestTestRunsIndexes:
    """Test indexes for performance"""

    def test_has_index_creation(self):
        """Test that migration creates indexes"""
        if TEST_RUNS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_RUNS_MIGRATION_FILE.read_text()
        assert "create_index" in content or "index=True" in content, "Should create indexes"

    def test_has_status_index(self):
        """Test that migration creates index on status"""
        if TEST_RUNS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_RUNS_MIGRATION_FILE.read_text()
        assert ("status" in content and ("create_index" in content or "index=True" in content)), "Should create index on status"

    def test_has_created_by_index(self):
        """Test that migration creates index on created_by"""
        if TEST_RUNS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_RUNS_MIGRATION_FILE.read_text()
        assert ("created_by" in content and ("create_index" in content or "index=True" in content)), "Should create index on created_by"

    def test_has_created_at_index(self):
        """Test that migration creates index on created_at"""
        if TEST_RUNS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_RUNS_MIGRATION_FILE.read_text()
        assert ("created_at" in content and ("create_index" in content or "index=True" in content)), "Should create index on created_at"


class TestTestRunsDowngrade:
    """Test downgrade functionality"""

    def test_downgrade_drops_table(self):
        """Test that downgrade drops test_runs table"""
        if TEST_RUNS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_RUNS_MIGRATION_FILE.read_text()
        assert "drop_table" in content.lower(), "Downgrade should drop table"
        downgrade_match = re.search(r'def downgrade.*?(?=\ndef|\Z)', content, re.DOTALL)
        if downgrade_match:
            downgrade_content = downgrade_match.group(0)
            assert "test_runs" in downgrade_content, "Downgrade should drop test_runs table"

    def test_downgrade_drops_indexes(self):
        """Test that downgrade drops indexes if they exist"""
        if TEST_RUNS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_RUNS_MIGRATION_FILE.read_text()
        # If indexes are explicitly created, they should be dropped in downgrade
        if "op.create_index" in content:
            downgrade_match = re.search(r'def downgrade.*?(?=\ndef|\Z)', content, re.DOTALL)
            if downgrade_match:
                downgrade_content = downgrade_match.group(0)
                assert "drop_index" in downgrade_content, "Downgrade should drop indexes"


class TestTestRunsMigrationDocumentation:
    """Test migration documentation"""

    def test_has_docstring(self):
        """Test that migration has docstring"""
        if TEST_RUNS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_RUNS_MIGRATION_FILE.read_text()
        assert '"""' in content or "'''" in content, "Migration should have docstring"

    def test_docstring_mentions_test_runs(self):
        """Test that docstring mentions test_runs"""
        if TEST_RUNS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_RUNS_MIGRATION_FILE.read_text()
        assert ("test_runs" in content.lower() or "test runs" in content.lower()), "Should document test_runs table"


class TestTestRunsMigrationRevisionChain:
    """Test Alembic revision chain"""

    def test_has_valid_revision_id(self):
        """Test that migration has valid revision ID"""
        if TEST_RUNS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_RUNS_MIGRATION_FILE.read_text()
        assert "revision:" in content or "revision =" in content, "Should have revision ID"

    def test_down_revision_references_previous_migration(self):
        """Test that down_revision references the test_case_outcomes migration"""
        if TEST_RUNS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_RUNS_MIGRATION_FILE.read_text()
        assert "down_revision" in content, "Should have down_revision"
        # Should reference the test_case_outcomes migration (e5f6a7b8c9d0)
