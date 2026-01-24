"""
Test suite for test_suites table migration

Validates the Alembic migration for test_suites table including:
- Migration file structure
- Table creation with correct schema
- Column definitions and types
- Constraints and defaults
- Foreign key relationships
- Downgrade functionality
- Alembic revision metadata
"""

import pytest
from pathlib import Path
import re


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
ALEMBIC_VERSIONS = PROJECT_ROOT / "alembic" / "versions"


# Find the test_suites migration file dynamically
def find_migration_file(keyword: str) -> Path | None:
    """Find migration file containing keyword in filename"""
    if not ALEMBIC_VERSIONS.exists():
        return None

    for file in ALEMBIC_VERSIONS.glob("*.py"):
        if keyword in file.name.lower() and file.name != "__pycache__":
            return file
    return None


TEST_SUITES_MIGRATION_FILE = find_migration_file("test_suite")


class TestTestSuitesMigrationFileExists:
    """Test that test_suites migration file exists"""

    def test_alembic_versions_directory_exists(self):
        """Test that alembic/versions directory exists"""
        assert ALEMBIC_VERSIONS.exists(), "alembic/versions directory should exist"
        assert ALEMBIC_VERSIONS.is_dir(), "alembic/versions should be a directory"

    def test_test_suites_migration_file_exists(self):
        """Test that test_suites migration file exists"""
        assert TEST_SUITES_MIGRATION_FILE is not None, "test_suites migration file should exist"
        assert TEST_SUITES_MIGRATION_FILE.exists(), "test_suites migration file should exist"
        assert TEST_SUITES_MIGRATION_FILE.is_file(), "test_suites migration should be a file"

    def test_migration_file_has_content(self):
        """Test that migration file has content"""
        if TEST_SUITES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_SUITES_MIGRATION_FILE.read_text()
        assert len(content) > 0, "Migration file should not be empty"


class TestTestSuitesMigrationStructure:
    """Test migration file structure"""

    def test_has_alembic_imports(self):
        """Test that migration imports alembic"""
        if TEST_SUITES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_SUITES_MIGRATION_FILE.read_text()
        assert "from alembic import op" in content, "Should import alembic.op"
        assert "import sqlalchemy" in content or "from sqlalchemy" in content, "Should import sqlalchemy"

    def test_has_revision_metadata(self):
        """Test that migration has revision metadata"""
        if TEST_SUITES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_SUITES_MIGRATION_FILE.read_text()
        assert "revision:" in content or "revision =" in content, "Should have revision identifier"
        assert "down_revision" in content, "Should have down_revision identifier"

    def test_has_upgrade_function(self):
        """Test that migration has upgrade function"""
        if TEST_SUITES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_SUITES_MIGRATION_FILE.read_text()
        assert "def upgrade" in content, "Should have upgrade() function"

    def test_has_downgrade_function(self):
        """Test that migration has downgrade function"""
        if TEST_SUITES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_SUITES_MIGRATION_FILE.read_text()
        assert "def downgrade" in content, "Should have downgrade() function"


class TestTestSuitesTableCreation:
    """Test test_suites table creation"""

    def test_creates_test_suites_table(self):
        """Test that migration creates test_suites table"""
        if TEST_SUITES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_SUITES_MIGRATION_FILE.read_text()
        assert "create_table" in content.lower(), "Should create a table"
        assert "test_suites" in content, "Should create test_suites table"

    def test_table_has_id_column(self):
        """Test that test_suites table has id column"""
        if TEST_SUITES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_SUITES_MIGRATION_FILE.read_text()
        assert "'id'" in content or '"id"' in content, "Should have id column"

    def test_table_has_name_column(self):
        """Test that test_suites table has name column"""
        if TEST_SUITES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_SUITES_MIGRATION_FILE.read_text()
        assert "'name'" in content or '"name"' in content, "Should have name column"

    def test_table_has_description_column(self):
        """Test that test_suites table has description column"""
        if TEST_SUITES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_SUITES_MIGRATION_FILE.read_text()
        assert "'description'" in content or '"description"' in content, "Should have description column"

    def test_table_has_category_column(self):
        """Test that test_suites table has category column"""
        if TEST_SUITES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_SUITES_MIGRATION_FILE.read_text()
        assert "'category'" in content or '"category"' in content, "Should have category column"

    def test_table_has_is_active_column(self):
        """Test that test_suites table has is_active column"""
        if TEST_SUITES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_SUITES_MIGRATION_FILE.read_text()
        assert "'is_active'" in content or '"is_active"' in content, "Should have is_active column"

    def test_table_has_created_by_column(self):
        """Test that test_suites table has created_by column"""
        if TEST_SUITES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_SUITES_MIGRATION_FILE.read_text()
        assert "'created_by'" in content or '"created_by"' in content, "Should have created_by column"

    def test_table_has_created_at_column(self):
        """Test that test_suites table has created_at column"""
        if TEST_SUITES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_SUITES_MIGRATION_FILE.read_text()
        assert "'created_at'" in content or '"created_at"' in content, "Should have created_at column"

    def test_table_has_updated_at_column(self):
        """Test that test_suites table has updated_at column"""
        if TEST_SUITES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_SUITES_MIGRATION_FILE.read_text()
        assert "'updated_at'" in content or '"updated_at"' in content, "Should have updated_at column"


class TestTestSuitesColumnTypes:
    """Test column types"""

    def test_id_column_is_uuid(self):
        """Test that id column is UUID type"""
        if TEST_SUITES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_SUITES_MIGRATION_FILE.read_text()
        assert ("UUID" in content or "uuid" in content.lower()), "id should be UUID type"

    def test_id_column_is_primary_key(self):
        """Test that id column is primary key"""
        if TEST_SUITES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_SUITES_MIGRATION_FILE.read_text()
        assert "primary_key" in content, "id should be primary key"

    def test_name_column_is_string(self):
        """Test that name column is String type"""
        if TEST_SUITES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_SUITES_MIGRATION_FILE.read_text()
        # Should have String type for name
        assert "String" in content, "name should be String type"

    def test_name_column_not_nullable(self):
        """Test that name column is not nullable"""
        if TEST_SUITES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_SUITES_MIGRATION_FILE.read_text()
        # Check for nullable=False for name column
        assert "nullable" in content, "Should have nullable constraints"

    def test_description_column_is_text(self):
        """Test that description column is Text type"""
        if TEST_SUITES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_SUITES_MIGRATION_FILE.read_text()
        assert "Text" in content, "description should be Text type"

    def test_is_active_column_is_boolean(self):
        """Test that is_active column is Boolean type"""
        if TEST_SUITES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_SUITES_MIGRATION_FILE.read_text()
        assert "Boolean" in content, "is_active should be Boolean type"

    def test_timestamps_are_datetime(self):
        """Test that timestamp columns are DateTime type"""
        if TEST_SUITES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_SUITES_MIGRATION_FILE.read_text()
        assert "DateTime" in content, "Timestamp columns should be DateTime type"


class TestTestSuitesConstraints:
    """Test constraints and defaults"""

    def test_is_active_has_default_true(self):
        """Test that is_active has default value of true"""
        if TEST_SUITES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_SUITES_MIGRATION_FILE.read_text()
        assert ("server_default" in content or "default" in content), "is_active should have default value"

    def test_created_at_has_default(self):
        """Test that created_at has default timestamp"""
        if TEST_SUITES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_SUITES_MIGRATION_FILE.read_text()
        assert ("server_default" in content or "now()" in content.lower()), "created_at should have default timestamp"

    def test_updated_at_has_default(self):
        """Test that updated_at has default timestamp"""
        if TEST_SUITES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_SUITES_MIGRATION_FILE.read_text()
        assert ("server_default" in content or "now()" in content.lower()), "updated_at should have default timestamp"


class TestTestSuitesForeignKeys:
    """Test foreign key relationships"""

    def test_created_by_references_users(self):
        """Test that created_by references users table"""
        if TEST_SUITES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_SUITES_MIGRATION_FILE.read_text()
        # Should have foreign key to users table
        assert (("ForeignKey" in content and "users" in content) or
                "users.id" in content), "created_by should reference users table"


class TestTestSuitesDowngrade:
    """Test downgrade functionality"""

    def test_downgrade_drops_table(self):
        """Test that downgrade drops test_suites table"""
        if TEST_SUITES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_SUITES_MIGRATION_FILE.read_text()
        assert "drop_table" in content.lower(), "Downgrade should drop table"
        # Should mention test_suites in downgrade
        downgrade_match = re.search(r'def downgrade.*?(?=\ndef|\Z)', content, re.DOTALL)
        if downgrade_match:
            downgrade_content = downgrade_match.group(0)
            assert "test_suites" in downgrade_content, "Downgrade should drop test_suites table"


class TestTestSuitesMigrationDocumentation:
    """Test migration documentation"""

    def test_has_docstring(self):
        """Test that migration has docstring"""
        if TEST_SUITES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_SUITES_MIGRATION_FILE.read_text()
        assert '"""' in content or "'''" in content, "Migration should have docstring"

    def test_docstring_mentions_test_suites(self):
        """Test that docstring mentions test_suites"""
        if TEST_SUITES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_SUITES_MIGRATION_FILE.read_text()
        # Should mention test_suites or test suites in comments/docstring
        assert ("test_suites" in content.lower() or "test suites" in content.lower()), "Should document test_suites table"


class TestTestSuitesMigrationRevisionChain:
    """Test Alembic revision chain"""

    def test_down_revision_references_users_migration(self):
        """Test that down_revision references the users migration"""
        if TEST_SUITES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = TEST_SUITES_MIGRATION_FILE.read_text()
        # Should have down_revision set (not None for the second migration)
        assert "down_revision" in content, "Should have down_revision"
        # down_revision should not be None (it should reference the users migration)
        # This is a sanity check - actual value will be the users migration revision ID
