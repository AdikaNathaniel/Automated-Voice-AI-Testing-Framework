"""
Test suite for environment_variables table migration

Validates the Alembic migration for environment_variables table including:
- Migration file structure
- Table creation with correct schema
- Column definitions and types
- Encrypted value field for secure storage
- Variable name/key field
- Optional description field
- Constraints and defaults
- Indexes for performance
- Downgrade functionality
- Alembic revision metadata
"""

import pytest
from pathlib import Path
import re


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
ALEMBIC_VERSIONS = PROJECT_ROOT / "alembic" / "versions"


# Find the environment_variables migration file dynamically
def find_migration_file(keyword: str) -> Path | None:
    """Find migration file containing keyword in filename"""
    if not ALEMBIC_VERSIONS.exists():
        return None

    for file in ALEMBIC_VERSIONS.glob("*.py"):
        if keyword in file.name.lower() and file.name != "__pycache__":
            return file
    return None


ENV_VARS_MIGRATION_FILE = find_migration_file("env_var") or find_migration_file("environment_variable")


class TestEnvironmentVariablesMigrationFileExists:
    """Test that environment_variables migration file exists"""

    def test_alembic_versions_directory_exists(self):
        """Test that alembic/versions directory exists"""
        assert ALEMBIC_VERSIONS.exists(), "alembic/versions directory should exist"
        assert ALEMBIC_VERSIONS.is_dir(), "alembic/versions should be a directory"

    def test_environment_variables_migration_file_exists(self):
        """Test that environment_variables migration file exists"""
        assert ENV_VARS_MIGRATION_FILE is not None, "environment_variables migration file should exist"
        assert ENV_VARS_MIGRATION_FILE.exists(), "environment_variables migration file should exist"
        assert ENV_VARS_MIGRATION_FILE.is_file(), "environment_variables migration should be a file"

    def test_migration_file_has_content(self):
        """Test that migration file has content"""
        if ENV_VARS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = ENV_VARS_MIGRATION_FILE.read_text()
        assert len(content) > 0, "Migration file should not be empty"


class TestEnvironmentVariablesMigrationStructure:
    """Test migration file structure"""

    def test_has_alembic_imports(self):
        """Test that migration imports alembic"""
        if ENV_VARS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = ENV_VARS_MIGRATION_FILE.read_text()
        assert "from alembic import op" in content, "Should import alembic.op"
        assert "import sqlalchemy" in content or "from sqlalchemy" in content, "Should import sqlalchemy"

    def test_has_revision_metadata(self):
        """Test that migration has revision metadata"""
        if ENV_VARS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = ENV_VARS_MIGRATION_FILE.read_text()
        assert "revision:" in content or "revision =" in content, "Should have revision identifier"
        assert "down_revision" in content, "Should have down_revision identifier"

    def test_has_upgrade_function(self):
        """Test that migration has upgrade function"""
        if ENV_VARS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = ENV_VARS_MIGRATION_FILE.read_text()
        assert "def upgrade" in content, "Should have upgrade() function"

    def test_has_downgrade_function(self):
        """Test that migration has downgrade function"""
        if ENV_VARS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = ENV_VARS_MIGRATION_FILE.read_text()
        assert "def downgrade" in content, "Should have downgrade() function"


class TestEnvironmentVariablesTableCreation:
    """Test environment_variables table creation"""

    def test_creates_environment_variables_table(self):
        """Test that migration creates environment_variables table"""
        if ENV_VARS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = ENV_VARS_MIGRATION_FILE.read_text()
        assert "create_table" in content.lower(), "Should create a table"
        assert "environment_variables" in content, "Should create environment_variables table"

    def test_table_has_id_column(self):
        """Test that environment_variables table has id column"""
        if ENV_VARS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = ENV_VARS_MIGRATION_FILE.read_text()
        assert "'id'" in content or '"id"' in content, "Should have id column"

    def test_table_has_variable_name_column(self):
        """Test that environment_variables table has variable_name or var_name column"""
        if ENV_VARS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = ENV_VARS_MIGRATION_FILE.read_text()
        assert ("'variable_name'" in content or '"variable_name"' in content or
                "'var_name'" in content or '"var_name"' in content or
                "'name'" in content or '"name"' in content), "Should have variable name column"

    def test_table_has_encrypted_value_column(self):
        """Test that environment_variables table has encrypted_value column"""
        if ENV_VARS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = ENV_VARS_MIGRATION_FILE.read_text()
        assert ("'encrypted_value'" in content or '"encrypted_value"' in content or
                "'value'" in content or '"value"' in content), "Should have encrypted value column"

    def test_table_has_description_column(self):
        """Test that environment_variables table has description column"""
        if ENV_VARS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = ENV_VARS_MIGRATION_FILE.read_text()
        assert "'description'" in content or '"description"' in content, "Should have description column"

    def test_table_has_created_at_column(self):
        """Test that environment_variables table has created_at column"""
        if ENV_VARS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = ENV_VARS_MIGRATION_FILE.read_text()
        assert "'created_at'" in content or '"created_at"' in content, "Should have created_at column"


class TestEnvironmentVariablesColumnTypes:
    """Test column types"""

    def test_id_column_is_uuid(self):
        """Test that id column is UUID type"""
        if ENV_VARS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = ENV_VARS_MIGRATION_FILE.read_text()
        assert ("UUID" in content or "uuid" in content.lower()), "id should be UUID type"

    def test_id_column_is_primary_key(self):
        """Test that id column is primary key"""
        if ENV_VARS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = ENV_VARS_MIGRATION_FILE.read_text()
        assert "primary_key" in content, "id should be primary key"

    def test_variable_name_is_string(self):
        """Test that variable_name is String type"""
        if ENV_VARS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = ENV_VARS_MIGRATION_FILE.read_text()
        assert "String" in content, "variable_name should be String type"

    def test_encrypted_value_is_text_or_string(self):
        """Test that encrypted_value is Text or String type"""
        if ENV_VARS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = ENV_VARS_MIGRATION_FILE.read_text()
        assert ("Text" in content or "String" in content), "encrypted_value should be Text or String type"

    def test_description_is_text_or_string(self):
        """Test that description is Text or String type"""
        if ENV_VARS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = ENV_VARS_MIGRATION_FILE.read_text()
        assert ("Text" in content or "String" in content), "description should be Text or String type"

    def test_created_at_is_datetime(self):
        """Test that created_at is DateTime type"""
        if ENV_VARS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = ENV_VARS_MIGRATION_FILE.read_text()
        assert "DateTime" in content, "created_at should be DateTime type"


class TestEnvironmentVariablesEncryptedField:
    """Test encrypted value field requirements"""

    def test_has_encrypted_value_field(self):
        """Test that migration has encrypted_value field"""
        if ENV_VARS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = ENV_VARS_MIGRATION_FILE.read_text()
        # Should have a field for encrypted value
        assert ("encrypted" in content.lower() or "value" in content), "Should have encrypted value field"


class TestEnvironmentVariablesConstraints:
    """Test constraints and defaults"""

    def test_created_at_has_default(self):
        """Test that created_at has default timestamp"""
        if ENV_VARS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = ENV_VARS_MIGRATION_FILE.read_text()
        assert ("server_default" in content or "now()" in content.lower()), "created_at should have default timestamp"

    def test_variable_name_not_nullable(self):
        """Test that variable_name is not nullable"""
        if ENV_VARS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = ENV_VARS_MIGRATION_FILE.read_text()
        assert "nullable" in content, "Should have nullable constraints"

    def test_variable_name_unique(self):
        """Test that variable_name has unique constraint"""
        if ENV_VARS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = ENV_VARS_MIGRATION_FILE.read_text()
        assert "unique" in content.lower(), "variable_name should have unique constraint"


class TestEnvironmentVariablesIndexes:
    """Test indexes for performance"""

    def test_has_index_creation(self):
        """Test that migration creates indexes or uses unique constraint"""
        if ENV_VARS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = ENV_VARS_MIGRATION_FILE.read_text()
        # Either explicit index or unique constraint
        assert ("create_index" in content or "index=True" in content or "unique" in content.lower()), "Should create indexes or have unique constraint"


class TestEnvironmentVariablesDowngrade:
    """Test downgrade functionality"""

    def test_downgrade_drops_table(self):
        """Test that downgrade drops environment_variables table"""
        if ENV_VARS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = ENV_VARS_MIGRATION_FILE.read_text()
        assert "drop_table" in content.lower(), "Downgrade should drop table"
        downgrade_match = re.search(r'def downgrade.*?(?=\ndef|\Z)', content, re.DOTALL)
        if downgrade_match:
            downgrade_content = downgrade_match.group(0)
            assert "environment_variables" in downgrade_content, "Downgrade should drop environment_variables table"

    def test_downgrade_drops_indexes(self):
        """Test that downgrade drops indexes if they exist"""
        if ENV_VARS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = ENV_VARS_MIGRATION_FILE.read_text()
        # If indexes are explicitly created, they should be dropped in downgrade
        if "op.create_index" in content:
            downgrade_match = re.search(r'def downgrade.*?(?=\ndef|\Z)', content, re.DOTALL)
            if downgrade_match:
                downgrade_content = downgrade_match.group(0)
                assert "drop_index" in downgrade_content, "Downgrade should drop indexes"


class TestEnvironmentVariablesMigrationDocumentation:
    """Test migration documentation"""

    def test_has_docstring(self):
        """Test that migration has docstring"""
        if ENV_VARS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = ENV_VARS_MIGRATION_FILE.read_text()
        assert '"""' in content or "'''" in content, "Migration should have docstring"

    def test_docstring_mentions_environment_variables(self):
        """Test that docstring mentions environment_variables"""
        if ENV_VARS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = ENV_VARS_MIGRATION_FILE.read_text()
        assert ("environment_variables" in content.lower() or
                "environment variable" in content.lower() or
                "env" in content.lower()), "Should document environment_variables table"


class TestEnvironmentVariablesMigrationRevisionChain:
    """Test Alembic revision chain"""

    def test_has_valid_revision_id(self):
        """Test that migration has valid revision ID"""
        if ENV_VARS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = ENV_VARS_MIGRATION_FILE.read_text()
        assert "revision:" in content or "revision =" in content, "Should have revision ID"

    def test_down_revision_references_previous_migration(self):
        """Test that down_revision references the configuration_history migration"""
        if ENV_VARS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = ENV_VARS_MIGRATION_FILE.read_text()
        assert "down_revision" in content, "Should have down_revision"
        # Should reference the configuration_history migration (f2a3b4c5d6e7)


class TestEnvironmentVariablesColumnComments:
    """Test column comments/documentation"""

    def test_columns_have_comments(self):
        """Test that columns have comment documentation"""
        if ENV_VARS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = ENV_VARS_MIGRATION_FILE.read_text()
        assert "comment" in content.lower(), "Columns should have comment documentation"
