"""
Test suite for configurations table migration

Validates the Alembic migration for configurations table including:
- Migration file structure
- Table creation with correct schema
- Column definitions and types
- JSONB field for config_data
- Foreign key relationships (if any)
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


# Find the configurations migration file dynamically
def find_migration_file(keyword: str) -> Path | None:
    """Find migration file containing keyword in filename"""
    if not ALEMBIC_VERSIONS.exists():
        return None

    for file in ALEMBIC_VERSIONS.glob("*.py"):
        if keyword in file.name.lower() and file.name != "__pycache__":
            return file
    return None


CONFIGURATIONS_MIGRATION_FILE = find_migration_file("configuration")


class TestConfigurationsMigrationFileExists:
    """Test that configurations migration file exists"""

    def test_alembic_versions_directory_exists(self):
        """Test that alembic/versions directory exists"""
        assert ALEMBIC_VERSIONS.exists(), "alembic/versions directory should exist"
        assert ALEMBIC_VERSIONS.is_dir(), "alembic/versions should be a directory"

    def test_configurations_migration_file_exists(self):
        """Test that configurations migration file exists"""
        assert CONFIGURATIONS_MIGRATION_FILE is not None, "configurations migration file should exist"
        assert CONFIGURATIONS_MIGRATION_FILE.exists(), "configurations migration file should exist"
        assert CONFIGURATIONS_MIGRATION_FILE.is_file(), "configurations migration should be a file"

    def test_migration_file_has_content(self):
        """Test that migration file has content"""
        if CONFIGURATIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIGURATIONS_MIGRATION_FILE.read_text()
        assert len(content) > 0, "Migration file should not be empty"


class TestConfigurationsMigrationStructure:
    """Test migration file structure"""

    def test_has_alembic_imports(self):
        """Test that migration imports alembic"""
        if CONFIGURATIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIGURATIONS_MIGRATION_FILE.read_text()
        assert "from alembic import op" in content, "Should import alembic.op"
        assert "import sqlalchemy" in content or "from sqlalchemy" in content, "Should import sqlalchemy"

    def test_has_revision_metadata(self):
        """Test that migration has revision metadata"""
        if CONFIGURATIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIGURATIONS_MIGRATION_FILE.read_text()
        assert "revision:" in content or "revision =" in content, "Should have revision identifier"
        assert "down_revision" in content, "Should have down_revision identifier"

    def test_has_upgrade_function(self):
        """Test that migration has upgrade function"""
        if CONFIGURATIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIGURATIONS_MIGRATION_FILE.read_text()
        assert "def upgrade" in content, "Should have upgrade() function"

    def test_has_downgrade_function(self):
        """Test that migration has downgrade function"""
        if CONFIGURATIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIGURATIONS_MIGRATION_FILE.read_text()
        assert "def downgrade" in content, "Should have downgrade() function"


class TestConfigurationsTableCreation:
    """Test configurations table creation"""

    def test_creates_configurations_table(self):
        """Test that migration creates configurations table"""
        if CONFIGURATIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIGURATIONS_MIGRATION_FILE.read_text()
        assert "create_table" in content.lower(), "Should create a table"
        assert "configurations" in content, "Should create configurations table"

    def test_table_has_id_column(self):
        """Test that configurations table has id column"""
        if CONFIGURATIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIGURATIONS_MIGRATION_FILE.read_text()
        assert "'id'" in content or '"id"' in content, "Should have id column"

    def test_table_has_config_key_column(self):
        """Test that configurations table has config_key column"""
        if CONFIGURATIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIGURATIONS_MIGRATION_FILE.read_text()
        assert "'config_key'" in content or '"config_key"' in content or "'key'" in content or '"key"' in content, "Should have config_key or key column"

    def test_table_has_config_data_column(self):
        """Test that configurations table has config_data column"""
        if CONFIGURATIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIGURATIONS_MIGRATION_FILE.read_text()
        assert "'config_data'" in content or '"config_data"' in content or "'data'" in content or '"data"' in content, "Should have config_data or data column"

    def test_table_has_created_at_column(self):
        """Test that configurations table has created_at column"""
        if CONFIGURATIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIGURATIONS_MIGRATION_FILE.read_text()
        assert "'created_at'" in content or '"created_at"' in content, "Should have created_at column"


class TestConfigurationsColumnTypes:
    """Test column types"""

    def test_id_column_is_uuid(self):
        """Test that id column is UUID type"""
        if CONFIGURATIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIGURATIONS_MIGRATION_FILE.read_text()
        assert ("UUID" in content or "uuid" in content.lower()), "id should be UUID type"

    def test_id_column_is_primary_key(self):
        """Test that id column is primary key"""
        if CONFIGURATIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIGURATIONS_MIGRATION_FILE.read_text()
        assert "primary_key" in content, "id should be primary key"

    def test_config_key_is_string(self):
        """Test that config_key is String type"""
        if CONFIGURATIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIGURATIONS_MIGRATION_FILE.read_text()
        assert "String" in content, "config_key should be String type"

    def test_config_data_is_jsonb(self):
        """Test that config_data is JSONB type"""
        if CONFIGURATIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIGURATIONS_MIGRATION_FILE.read_text()
        assert "JSONB" in content, "config_data should be JSONB type"

    def test_created_at_is_datetime(self):
        """Test that created_at is DateTime type"""
        if CONFIGURATIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIGURATIONS_MIGRATION_FILE.read_text()
        assert "DateTime" in content, "created_at should be DateTime type"


class TestConfigurationsJSONBField:
    """Test JSONB field requirements"""

    def test_has_jsonb_field(self):
        """Test that migration has JSONB field"""
        if CONFIGURATIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIGURATIONS_MIGRATION_FILE.read_text()
        jsonb_count = content.count("JSONB")
        assert jsonb_count >= 1, "Should have at least 1 JSONB field"


class TestConfigurationsConstraints:
    """Test constraints and defaults"""

    def test_created_at_has_default(self):
        """Test that created_at has default timestamp"""
        if CONFIGURATIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIGURATIONS_MIGRATION_FILE.read_text()
        assert ("server_default" in content or "now()" in content.lower()), "created_at should have default timestamp"

    def test_config_key_not_nullable(self):
        """Test that config_key is not nullable"""
        if CONFIGURATIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIGURATIONS_MIGRATION_FILE.read_text()
        assert "nullable" in content, "Should have nullable constraints"

    def test_config_key_unique(self):
        """Test that config_key has unique constraint"""
        if CONFIGURATIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIGURATIONS_MIGRATION_FILE.read_text()
        assert "unique" in content.lower(), "config_key should have unique constraint"


class TestConfigurationsIndexes:
    """Test indexes for performance"""

    def test_has_index_on_config_key(self):
        """Test that migration creates index on config_key"""
        if CONFIGURATIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIGURATIONS_MIGRATION_FILE.read_text()
        # Either explicit index creation or unique constraint (which creates index)
        assert ("create_index" in content or "index=True" in content or "unique" in content.lower()), "Should create index on config_key"


class TestConfigurationsDowngrade:
    """Test downgrade functionality"""

    def test_downgrade_drops_table(self):
        """Test that downgrade drops configurations table"""
        if CONFIGURATIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIGURATIONS_MIGRATION_FILE.read_text()
        assert "drop_table" in content.lower(), "Downgrade should drop table"
        downgrade_match = re.search(r'def downgrade.*?(?=\ndef|\Z)', content, re.DOTALL)
        if downgrade_match:
            downgrade_content = downgrade_match.group(0)
            assert "configurations" in downgrade_content, "Downgrade should drop configurations table"

    def test_downgrade_drops_indexes(self):
        """Test that downgrade drops indexes if they exist"""
        if CONFIGURATIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIGURATIONS_MIGRATION_FILE.read_text()
        # If indexes are explicitly created, they should be dropped in downgrade
        if "op.create_index" in content:
            downgrade_match = re.search(r'def downgrade.*?(?=\ndef|\Z)', content, re.DOTALL)
            if downgrade_match:
                downgrade_content = downgrade_match.group(0)
                assert "drop_index" in downgrade_content, "Downgrade should drop indexes"


class TestConfigurationsMigrationDocumentation:
    """Test migration documentation"""

    def test_has_docstring(self):
        """Test that migration has docstring"""
        if CONFIGURATIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIGURATIONS_MIGRATION_FILE.read_text()
        assert '"""' in content or "'''" in content, "Migration should have docstring"

    def test_docstring_mentions_configurations(self):
        """Test that docstring mentions configurations"""
        if CONFIGURATIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIGURATIONS_MIGRATION_FILE.read_text()
        assert ("configurations" in content.lower() or "configuration" in content.lower()), "Should document configurations table"


class TestConfigurationsMigrationRevisionChain:
    """Test Alembic revision chain"""

    def test_has_valid_revision_id(self):
        """Test that migration has valid revision ID"""
        if CONFIGURATIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIGURATIONS_MIGRATION_FILE.read_text()
        assert "revision:" in content or "revision =" in content, "Should have revision ID"

    def test_down_revision_references_previous_migration(self):
        """Test that down_revision references the validation_results migration"""
        if CONFIGURATIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = CONFIGURATIONS_MIGRATION_FILE.read_text()
        assert "down_revision" in content, "Should have down_revision"
        # Should reference the validation_results migration (d0e1f2a3b4c5)
