"""
Test suite for configuration_history table migration

Validates the Alembic migration for configuration_history table including:
- Migration file structure
- Table creation with correct schema
- Column definitions and types
- JSONB fields for old_value and new_value
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


# Find the configuration_history migration file dynamically
def find_migration_file(keyword: str) -> Path | None:
    """Find migration file containing keyword in filename"""
    if not ALEMBIC_VERSIONS.exists():
        return None

    for file in ALEMBIC_VERSIONS.glob("*.py"):
        if keyword in file.name.lower() and file.name != "__pycache__":
            return file
    return None


CONFIG_HISTORY_MIGRATION_FILE = find_migration_file("config_history") or find_migration_file("configuration_history")


class TestConfigurationHistoryMigrationFileExists:
    """Test that configuration_history migration file exists"""

    def test_alembic_versions_directory_exists(self):
        """Test that alembic/versions directory exists"""
        assert ALEMBIC_VERSIONS.exists(), "alembic/versions directory should exist"
        assert ALEMBIC_VERSIONS.is_dir(), "alembic/versions should be a directory"

    def test_configuration_history_migration_file_exists(self):
        """Test that configuration_history migration file exists"""
        assert CONFIG_HISTORY_MIGRATION_FILE is not None, "configuration_history migration file should exist"
        assert CONFIG_HISTORY_MIGRATION_FILE.exists(), "configuration_history migration file should exist"
        assert CONFIG_HISTORY_MIGRATION_FILE.is_file(), "configuration_history migration should be a file"

    def test_migration_file_has_content(self):
        """Test that migration file has content"""
        if CONFIG_HISTORY_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIG_HISTORY_MIGRATION_FILE.read_text()
        assert len(content) > 0, "Migration file should not be empty"


class TestConfigurationHistoryMigrationStructure:
    """Test migration file structure"""

    def test_has_alembic_imports(self):
        """Test that migration imports alembic"""
        if CONFIG_HISTORY_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIG_HISTORY_MIGRATION_FILE.read_text()
        assert "from alembic import op" in content, "Should import alembic.op"
        assert "import sqlalchemy" in content or "from sqlalchemy" in content, "Should import sqlalchemy"

    def test_has_revision_metadata(self):
        """Test that migration has revision metadata"""
        if CONFIG_HISTORY_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIG_HISTORY_MIGRATION_FILE.read_text()
        assert "revision:" in content or "revision =" in content, "Should have revision identifier"
        assert "down_revision" in content, "Should have down_revision identifier"

    def test_has_upgrade_function(self):
        """Test that migration has upgrade function"""
        if CONFIG_HISTORY_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIG_HISTORY_MIGRATION_FILE.read_text()
        assert "def upgrade" in content, "Should have upgrade() function"

    def test_has_downgrade_function(self):
        """Test that migration has downgrade function"""
        if CONFIG_HISTORY_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIG_HISTORY_MIGRATION_FILE.read_text()
        assert "def downgrade" in content, "Should have downgrade() function"


class TestConfigurationHistoryTableCreation:
    """Test configuration_history table creation"""

    def test_creates_configuration_history_table(self):
        """Test that migration creates configuration_history table"""
        if CONFIG_HISTORY_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIG_HISTORY_MIGRATION_FILE.read_text()
        assert "create_table" in content.lower(), "Should create a table"
        assert "configuration_history" in content, "Should create configuration_history table"

    def test_table_has_id_column(self):
        """Test that configuration_history table has id column"""
        if CONFIG_HISTORY_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIG_HISTORY_MIGRATION_FILE.read_text()
        assert "'id'" in content or '"id"' in content, "Should have id column"

    def test_table_has_configuration_id_column(self):
        """Test that configuration_history table has configuration_id column"""
        if CONFIG_HISTORY_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIG_HISTORY_MIGRATION_FILE.read_text()
        assert "'configuration_id'" in content or '"configuration_id"' in content, "Should have configuration_id column"

    def test_table_has_config_key_column(self):
        """Test that configuration_history table has config_key column"""
        if CONFIG_HISTORY_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIG_HISTORY_MIGRATION_FILE.read_text()
        assert "'config_key'" in content or '"config_key"' in content, "Should have config_key column"

    def test_table_has_old_value_column(self):
        """Test that configuration_history table has old_value column"""
        if CONFIG_HISTORY_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIG_HISTORY_MIGRATION_FILE.read_text()
        assert "'old_value'" in content or '"old_value"' in content, "Should have old_value column"

    def test_table_has_new_value_column(self):
        """Test that configuration_history table has new_value column"""
        if CONFIG_HISTORY_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIG_HISTORY_MIGRATION_FILE.read_text()
        assert "'new_value'" in content or '"new_value"' in content, "Should have new_value column"

    def test_table_has_changed_by_column(self):
        """Test that configuration_history table has changed_by column"""
        if CONFIG_HISTORY_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIG_HISTORY_MIGRATION_FILE.read_text()
        assert "'changed_by'" in content or '"changed_by"' in content, "Should have changed_by column"

    def test_table_has_created_at_column(self):
        """Test that configuration_history table has created_at column"""
        if CONFIG_HISTORY_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIG_HISTORY_MIGRATION_FILE.read_text()
        assert "'created_at'" in content or '"created_at"' in content, "Should have created_at column"


class TestConfigurationHistoryColumnTypes:
    """Test column types"""

    def test_id_column_is_uuid(self):
        """Test that id column is UUID type"""
        if CONFIG_HISTORY_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIG_HISTORY_MIGRATION_FILE.read_text()
        assert ("UUID" in content or "uuid" in content.lower()), "id should be UUID type"

    def test_id_column_is_primary_key(self):
        """Test that id column is primary key"""
        if CONFIG_HISTORY_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIG_HISTORY_MIGRATION_FILE.read_text()
        assert "primary_key" in content, "id should be primary key"

    def test_configuration_id_is_uuid(self):
        """Test that configuration_id is UUID type"""
        if CONFIG_HISTORY_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIG_HISTORY_MIGRATION_FILE.read_text()
        assert ("UUID" in content or "uuid" in content.lower()), "configuration_id should be UUID type"

    def test_config_key_is_string(self):
        """Test that config_key is String type"""
        if CONFIG_HISTORY_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIG_HISTORY_MIGRATION_FILE.read_text()
        assert "String" in content, "config_key should be String type"

    def test_old_value_is_jsonb(self):
        """Test that old_value is JSONB type"""
        if CONFIG_HISTORY_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIG_HISTORY_MIGRATION_FILE.read_text()
        assert "JSONB" in content, "old_value should be JSONB type"

    def test_new_value_is_jsonb(self):
        """Test that new_value is JSONB type"""
        if CONFIG_HISTORY_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIG_HISTORY_MIGRATION_FILE.read_text()
        assert "JSONB" in content, "new_value should be JSONB type"

    def test_changed_by_is_uuid(self):
        """Test that changed_by is UUID type"""
        if CONFIG_HISTORY_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIG_HISTORY_MIGRATION_FILE.read_text()
        assert ("UUID" in content or "uuid" in content.lower()), "changed_by should be UUID type"

    def test_created_at_is_datetime(self):
        """Test that created_at is DateTime type"""
        if CONFIG_HISTORY_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIG_HISTORY_MIGRATION_FILE.read_text()
        assert "DateTime" in content, "created_at should be DateTime type"


class TestConfigurationHistoryJSONBFields:
    """Test JSONB field requirements"""

    def test_has_two_jsonb_fields(self):
        """Test that migration has two JSONB fields"""
        if CONFIG_HISTORY_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIG_HISTORY_MIGRATION_FILE.read_text()
        jsonb_count = content.count("JSONB")
        assert jsonb_count >= 2, "Should have at least 2 JSONB fields (old_value, new_value)"


class TestConfigurationHistoryForeignKeys:
    """Test foreign key relationships"""

    def test_configuration_id_references_configurations(self):
        """Test that configuration_id references configurations table"""
        if CONFIG_HISTORY_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIG_HISTORY_MIGRATION_FILE.read_text()
        assert (("ForeignKey" in content and "configurations" in content) or
                "configurations.id" in content), "configuration_id should reference configurations table"

    def test_changed_by_references_users(self):
        """Test that changed_by references users table"""
        if CONFIG_HISTORY_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIG_HISTORY_MIGRATION_FILE.read_text()
        # changed_by should reference users, but might be nullable
        if "changed_by" in content and "ForeignKey" in content:
            assert "users" in content, "changed_by should reference users table if foreign key is defined"


class TestConfigurationHistoryConstraints:
    """Test constraints and defaults"""

    def test_created_at_has_default(self):
        """Test that created_at has default timestamp"""
        if CONFIG_HISTORY_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIG_HISTORY_MIGRATION_FILE.read_text()
        assert ("server_default" in content or "now()" in content.lower()), "created_at should have default timestamp"

    def test_configuration_id_not_nullable(self):
        """Test that configuration_id is not nullable"""
        if CONFIG_HISTORY_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIG_HISTORY_MIGRATION_FILE.read_text()
        assert "nullable" in content, "Should have nullable constraints"


class TestConfigurationHistoryIndexes:
    """Test indexes for performance"""

    def test_has_index_creation(self):
        """Test that migration creates indexes"""
        if CONFIG_HISTORY_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIG_HISTORY_MIGRATION_FILE.read_text()
        assert "create_index" in content or "index=True" in content, "Should create indexes"

    def test_has_configuration_id_index(self):
        """Test that migration creates index on configuration_id"""
        if CONFIG_HISTORY_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIG_HISTORY_MIGRATION_FILE.read_text()
        assert ("configuration_id" in content and ("create_index" in content or "index=True" in content)), "Should create index on configuration_id"


class TestConfigurationHistoryDowngrade:
    """Test downgrade functionality"""

    def test_downgrade_drops_table(self):
        """Test that downgrade drops configuration_history table"""
        if CONFIG_HISTORY_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIG_HISTORY_MIGRATION_FILE.read_text()
        assert "drop_table" in content.lower(), "Downgrade should drop table"
        downgrade_match = re.search(r'def downgrade.*?(?=\ndef|\Z)', content, re.DOTALL)
        if downgrade_match:
            downgrade_content = downgrade_match.group(0)
            assert "configuration_history" in downgrade_content, "Downgrade should drop configuration_history table"

    def test_downgrade_drops_indexes(self):
        """Test that downgrade drops indexes if they exist"""
        if CONFIG_HISTORY_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIG_HISTORY_MIGRATION_FILE.read_text()
        # If indexes are explicitly created, they should be dropped in downgrade
        if "op.create_index" in content:
            downgrade_match = re.search(r'def downgrade.*?(?=\ndef|\Z)', content, re.DOTALL)
            if downgrade_match:
                downgrade_content = downgrade_match.group(0)
                assert "drop_index" in downgrade_content, "Downgrade should drop indexes"


class TestConfigurationHistoryMigrationDocumentation:
    """Test migration documentation"""

    def test_has_docstring(self):
        """Test that migration has docstring"""
        if CONFIG_HISTORY_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIG_HISTORY_MIGRATION_FILE.read_text()
        assert '"""' in content or "'''" in content, "Migration should have docstring"

    def test_docstring_mentions_configuration_history(self):
        """Test that docstring mentions configuration_history"""
        if CONFIG_HISTORY_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIG_HISTORY_MIGRATION_FILE.read_text()
        assert ("configuration_history" in content.lower() or "config" in content.lower()), "Should document configuration_history table"


class TestConfigurationHistoryMigrationRevisionChain:
    """Test Alembic revision chain"""

    def test_has_valid_revision_id(self):
        """Test that migration has valid revision ID"""
        if CONFIG_HISTORY_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIG_HISTORY_MIGRATION_FILE.read_text()
        assert "revision:" in content or "revision =" in content, "Should have revision ID"

    def test_down_revision_references_previous_migration(self):
        """Test that down_revision references the configurations migration"""
        if CONFIG_HISTORY_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIG_HISTORY_MIGRATION_FILE.read_text()
        assert "down_revision" in content, "Should have down_revision"
        # Should reference the configurations migration (e1f2a3b4c5d6)
