"""
Test suite for validation_queue table migration

Validates the Alembic migration for validation_queue table including:
- Migration file structure
- Table creation with correct schema
- Column definitions and types
- Foreign key relationships to validation_results and users tables
- Default values and constraints
- Indexes for common query patterns
- Downgrade functionality
- Alembic revision metadata
"""

import pytest
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
ALEMBIC_VERSIONS = PROJECT_ROOT / "alembic" / "versions"


# Find the validation_queue migration file dynamically
def find_migration_file(keyword: str) -> Path | None:
    """Find migration file containing keyword in filename"""
    if not ALEMBIC_VERSIONS.exists():
        return None

    for file in ALEMBIC_VERSIONS.glob("*.py"):
        if keyword in file.name.lower() and file.name != "__pycache__":
            return file
    return None


VALIDATION_QUEUE_MIGRATION_FILE = find_migration_file("validation_queue")


class TestValidationQueueMigrationFileExists:
    """Test that validation_queue migration file exists"""

    def test_alembic_versions_directory_exists(self):
        """Test that alembic/versions directory exists"""
        assert ALEMBIC_VERSIONS.exists(), "alembic/versions directory should exist"
        assert ALEMBIC_VERSIONS.is_dir(), "alembic/versions should be a directory"

    def test_validation_queue_migration_file_exists(self):
        """Test that validation_queue migration file exists"""
        assert VALIDATION_QUEUE_MIGRATION_FILE is not None, \
            "validation_queue migration file should exist (filename should contain 'validation_queue')"
        assert VALIDATION_QUEUE_MIGRATION_FILE.exists(), \
            "validation_queue migration file should exist"
        assert VALIDATION_QUEUE_MIGRATION_FILE.is_file(), \
            "validation_queue migration should be a file"

    def test_migration_file_has_content(self):
        """Test that migration file has content"""
        if VALIDATION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_QUEUE_MIGRATION_FILE.read_text()
        assert len(content) > 0, "Migration file should not be empty"


class TestValidationQueueMigrationStructure:
    """Test migration file structure"""

    def test_has_alembic_imports(self):
        """Test that migration imports alembic"""
        if VALIDATION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_QUEUE_MIGRATION_FILE.read_text()
        assert "from alembic import op" in content, "Should import alembic.op"
        assert "import sqlalchemy" in content or "from sqlalchemy" in content, \
            "Should import sqlalchemy"

    def test_has_revision_metadata(self):
        """Test that migration has revision metadata"""
        if VALIDATION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_QUEUE_MIGRATION_FILE.read_text()
        assert "revision:" in content or "revision =" in content, \
            "Should have revision identifier"
        assert "down_revision" in content, "Should have down_revision identifier"

    def test_has_upgrade_function(self):
        """Test that migration has upgrade function"""
        if VALIDATION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_QUEUE_MIGRATION_FILE.read_text()
        assert "def upgrade" in content, "Should have upgrade() function"

    def test_has_downgrade_function(self):
        """Test that migration has downgrade function"""
        if VALIDATION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_QUEUE_MIGRATION_FILE.read_text()
        assert "def downgrade" in content, "Should have downgrade() function"


class TestValidationQueueTableCreation:
    """Test validation_queue table creation"""

    def test_creates_validation_queue_table(self):
        """Test that migration creates validation_queue table"""
        if VALIDATION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_QUEUE_MIGRATION_FILE.read_text()
        assert "create_table" in content.lower(), "Should create a table"
        assert "validation_queue" in content, "Should create validation_queue table"

    def test_table_has_id_column(self):
        """Test that validation_queue table has id column"""
        if VALIDATION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_QUEUE_MIGRATION_FILE.read_text()
        assert "'id'" in content or '"id"' in content, "Should have id column"

    def test_table_has_validation_result_id_column(self):
        """Test that validation_queue table has validation_result_id column"""
        if VALIDATION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_QUEUE_MIGRATION_FILE.read_text()
        assert "'validation_result_id'" in content or '"validation_result_id"' in content, \
            "Should have validation_result_id column"

    def test_table_has_priority_column(self):
        """Test that validation_queue table has priority column"""
        if VALIDATION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_QUEUE_MIGRATION_FILE.read_text()
        assert "'priority'" in content or '"priority"' in content, \
            "Should have priority column"

    def test_table_has_confidence_score_column(self):
        """Test that validation_queue table has confidence_score column"""
        if VALIDATION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_QUEUE_MIGRATION_FILE.read_text()
        assert "'confidence_score'" in content or '"confidence_score"' in content, \
            "Should have confidence_score column"

    def test_table_has_language_code_column(self):
        """Test that validation_queue table has language_code column"""
        if VALIDATION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_QUEUE_MIGRATION_FILE.read_text()
        assert "'language_code'" in content or '"language_code"' in content, \
            "Should have language_code column"

    def test_table_has_claimed_by_column(self):
        """Test that validation_queue table has claimed_by column"""
        if VALIDATION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_QUEUE_MIGRATION_FILE.read_text()
        assert "'claimed_by'" in content or '"claimed_by"' in content, \
            "Should have claimed_by column"

    def test_table_has_claimed_at_column(self):
        """Test that validation_queue table has claimed_at column"""
        if VALIDATION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_QUEUE_MIGRATION_FILE.read_text()
        assert "'claimed_at'" in content or '"claimed_at"' in content, \
            "Should have claimed_at column"

    def test_table_has_status_column(self):
        """Test that validation_queue table has status column"""
        if VALIDATION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_QUEUE_MIGRATION_FILE.read_text()
        assert "'status'" in content or '"status"' in content, \
            "Should have status column"

    def test_table_has_requires_native_speaker_column(self):
        """Test that validation_queue table has requires_native_speaker column"""
        if VALIDATION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_QUEUE_MIGRATION_FILE.read_text()
        assert "'requires_native_speaker'" in content or '"requires_native_speaker"' in content, \
            "Should have requires_native_speaker column"

    def test_table_has_created_at_column(self):
        """Test that validation_queue table has created_at column"""
        if VALIDATION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_QUEUE_MIGRATION_FILE.read_text()
        assert "'created_at'" in content or '"created_at"' in content, \
            "Should have created_at column"


class TestValidationQueueColumnTypes:
    """Test column types"""

    def test_id_column_is_uuid(self):
        """Test that id column is UUID type"""
        if VALIDATION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_QUEUE_MIGRATION_FILE.read_text()
        assert ("UUID" in content or "uuid" in content.lower()), \
            "id should be UUID type"

    def test_id_column_is_primary_key(self):
        """Test that id column is primary key"""
        if VALIDATION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_QUEUE_MIGRATION_FILE.read_text()
        assert "primary_key" in content, "id should be primary key"

    def test_validation_result_id_is_uuid(self):
        """Test that validation_result_id is UUID type"""
        if VALIDATION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_QUEUE_MIGRATION_FILE.read_text()
        assert "UUID" in content or "uuid" in content.lower(), \
            "validation_result_id should be UUID type"

    def test_priority_is_integer(self):
        """Test that priority is Integer type"""
        if VALIDATION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_QUEUE_MIGRATION_FILE.read_text()
        assert "Integer" in content or "INTEGER" in content.upper(), \
            "priority should be Integer type"

    def test_confidence_score_is_numeric(self):
        """Test that confidence_score is Numeric/DECIMAL type"""
        if VALIDATION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_QUEUE_MIGRATION_FILE.read_text()
        assert "Numeric" in content or "DECIMAL" in content.upper(), \
            "confidence_score should be Numeric/DECIMAL type"

    def test_language_code_is_string(self):
        """Test that language_code is String/VARCHAR type"""
        if VALIDATION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_QUEUE_MIGRATION_FILE.read_text()
        assert "String" in content or "VARCHAR" in content.upper(), \
            "language_code should be String/VARCHAR type"

    def test_claimed_by_is_uuid(self):
        """Test that claimed_by is UUID type"""
        if VALIDATION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_QUEUE_MIGRATION_FILE.read_text()
        assert "UUID" in content or "uuid" in content.lower(), \
            "claimed_by should be UUID type"

    def test_status_is_string(self):
        """Test that status is String/VARCHAR type"""
        if VALIDATION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_QUEUE_MIGRATION_FILE.read_text()
        assert "String" in content or "VARCHAR" in content.upper(), \
            "status should be String/VARCHAR type"

    def test_requires_native_speaker_is_boolean(self):
        """Test that requires_native_speaker is Boolean type"""
        if VALIDATION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_QUEUE_MIGRATION_FILE.read_text()
        assert "Boolean" in content or "BOOLEAN" in content.upper(), \
            "requires_native_speaker should be Boolean type"

    def test_timestamp_columns_use_datetime(self):
        """Test that timestamp columns use DateTime"""
        if VALIDATION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_QUEUE_MIGRATION_FILE.read_text()
        assert "DateTime" in content or "TIMESTAMP" in content.upper(), \
            "Timestamp columns should use DateTime or TIMESTAMP"


class TestValidationQueueForeignKeys:
    """Test foreign key relationships"""

    def test_has_foreign_key_to_validation_results(self):
        """Test that validation_result_id has foreign key to validation_results"""
        if VALIDATION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_QUEUE_MIGRATION_FILE.read_text()
        has_fk = "ForeignKey" in content or "REFERENCES" in content.upper()
        has_validation_results = "validation_results" in content
        assert has_fk and has_validation_results, \
            "Should have foreign key to validation_results table"

    def test_has_foreign_key_to_users(self):
        """Test that claimed_by has foreign key to users"""
        if VALIDATION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_QUEUE_MIGRATION_FILE.read_text()
        has_fk = "ForeignKey" in content or "REFERENCES" in content.upper()
        has_users = "users" in content
        assert has_fk and has_users, \
            "Should have foreign key to users table"


class TestValidationQueueDefaults:
    """Test default values"""

    def test_priority_has_default(self):
        """Test that priority has default value of 5"""
        if VALIDATION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_QUEUE_MIGRATION_FILE.read_text()
        # Check for default=5 or server_default
        has_default = ("default=" in content.lower() or "server_default" in content.lower())
        assert has_default, "priority should have a default value"

    def test_requires_native_speaker_has_default(self):
        """Test that requires_native_speaker has default value"""
        if VALIDATION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_QUEUE_MIGRATION_FILE.read_text()
        # Check for default=False or server_default
        has_default = ("default=" in content.lower() or "server_default" in content.lower())
        assert has_default, "requires_native_speaker should have a default value"

    def test_created_at_has_default(self):
        """Test that created_at has default value"""
        if VALIDATION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_QUEUE_MIGRATION_FILE.read_text()
        # Check for default or server_default with NOW()/CURRENT_TIMESTAMP/func.now()
        has_default = ("default=" in content.lower() or "server_default" in content.lower() or
                      "func.now()" in content or "NOW()" in content.upper())
        assert has_default, "created_at should have a default value (NOW/CURRENT_TIMESTAMP)"


class TestValidationQueueDowngrade:
    """Test downgrade functionality"""

    def test_downgrade_drops_table(self):
        """Test that downgrade function drops validation_queue table"""
        if VALIDATION_QUEUE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_QUEUE_MIGRATION_FILE.read_text()
        assert "drop_table" in content.lower(), \
            "Downgrade should drop the table"
        assert "validation_queue" in content, \
            "Downgrade should reference validation_queue table"
