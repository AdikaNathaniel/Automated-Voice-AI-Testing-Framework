"""
Test suite for human_validations table migration

Validates the Alembic migration for human_validations table including:
- Migration file structure
- Table creation with correct schema
- Column definitions and types
- Foreign key relationships to validation_results and users tables
- Timestamp columns
- Boolean defaults
- Constraints and defaults
- Downgrade functionality
- Alembic revision metadata
"""

import pytest
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
ALEMBIC_VERSIONS = PROJECT_ROOT / "alembic" / "versions"


# Find the human_validations migration file dynamically
def find_migration_file(keyword: str) -> Path | None:
    """Find migration file containing keyword in filename"""
    if not ALEMBIC_VERSIONS.exists():
        return None

    for file in ALEMBIC_VERSIONS.glob("*.py"):
        if keyword in file.name.lower() and file.name != "__pycache__":
            return file
    return None


HUMAN_VALIDATIONS_MIGRATION_FILE = find_migration_file("human_validation")


class TestHumanValidationsMigrationFileExists:
    """Test that human_validations migration file exists"""

    def test_alembic_versions_directory_exists(self):
        """Test that alembic/versions directory exists"""
        assert ALEMBIC_VERSIONS.exists(), "alembic/versions directory should exist"
        assert ALEMBIC_VERSIONS.is_dir(), "alembic/versions should be a directory"

    def test_human_validations_migration_file_exists(self):
        """Test that human_validations migration file exists"""
        assert HUMAN_VALIDATIONS_MIGRATION_FILE is not None, \
            "human_validations migration file should exist (filename should contain 'human_validation')"
        assert HUMAN_VALIDATIONS_MIGRATION_FILE.exists(), \
            "human_validations migration file should exist"
        assert HUMAN_VALIDATIONS_MIGRATION_FILE.is_file(), \
            "human_validations migration should be a file"

    def test_migration_file_has_content(self):
        """Test that migration file has content"""
        if HUMAN_VALIDATIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = HUMAN_VALIDATIONS_MIGRATION_FILE.read_text()
        assert len(content) > 0, "Migration file should not be empty"


class TestHumanValidationsMigrationStructure:
    """Test migration file structure"""

    def test_has_alembic_imports(self):
        """Test that migration imports alembic"""
        if HUMAN_VALIDATIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = HUMAN_VALIDATIONS_MIGRATION_FILE.read_text()
        assert "from alembic import op" in content, "Should import alembic.op"
        assert "import sqlalchemy" in content or "from sqlalchemy" in content, \
            "Should import sqlalchemy"

    def test_has_revision_metadata(self):
        """Test that migration has revision metadata"""
        if HUMAN_VALIDATIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = HUMAN_VALIDATIONS_MIGRATION_FILE.read_text()
        assert "revision:" in content or "revision =" in content, \
            "Should have revision identifier"
        assert "down_revision" in content, "Should have down_revision identifier"

    def test_has_upgrade_function(self):
        """Test that migration has upgrade function"""
        if HUMAN_VALIDATIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = HUMAN_VALIDATIONS_MIGRATION_FILE.read_text()
        assert "def upgrade" in content, "Should have upgrade() function"

    def test_has_downgrade_function(self):
        """Test that migration has downgrade function"""
        if HUMAN_VALIDATIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = HUMAN_VALIDATIONS_MIGRATION_FILE.read_text()
        assert "def downgrade" in content, "Should have downgrade() function"


class TestHumanValidationsTableCreation:
    """Test human_validations table creation"""

    def test_creates_human_validations_table(self):
        """Test that migration creates human_validations table"""
        if HUMAN_VALIDATIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = HUMAN_VALIDATIONS_MIGRATION_FILE.read_text()
        assert "create_table" in content.lower(), "Should create a table"
        assert "human_validations" in content, "Should create human_validations table"

    def test_table_has_id_column(self):
        """Test that human_validations table has id column"""
        if HUMAN_VALIDATIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = HUMAN_VALIDATIONS_MIGRATION_FILE.read_text()
        assert "'id'" in content or '"id"' in content, "Should have id column"

    def test_table_has_validation_result_id_column(self):
        """Test that human_validations table has validation_result_id column"""
        if HUMAN_VALIDATIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = HUMAN_VALIDATIONS_MIGRATION_FILE.read_text()
        assert "'validation_result_id'" in content or '"validation_result_id"' in content, \
            "Should have validation_result_id column"

    def test_table_has_validator_id_column(self):
        """Test that human_validations table has validator_id column"""
        if HUMAN_VALIDATIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = HUMAN_VALIDATIONS_MIGRATION_FILE.read_text()
        assert "'validator_id'" in content or '"validator_id"' in content, \
            "Should have validator_id column"

    def test_table_has_claimed_at_column(self):
        """Test that human_validations table has claimed_at column"""
        if HUMAN_VALIDATIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = HUMAN_VALIDATIONS_MIGRATION_FILE.read_text()
        assert "'claimed_at'" in content or '"claimed_at"' in content, \
            "Should have claimed_at column"

    def test_table_has_submitted_at_column(self):
        """Test that human_validations table has submitted_at column"""
        if HUMAN_VALIDATIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = HUMAN_VALIDATIONS_MIGRATION_FILE.read_text()
        assert "'submitted_at'" in content or '"submitted_at"' in content, \
            "Should have submitted_at column"

    def test_table_has_validation_decision_column(self):
        """Test that human_validations table has validation_decision column"""
        if HUMAN_VALIDATIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = HUMAN_VALIDATIONS_MIGRATION_FILE.read_text()
        assert "'validation_decision'" in content or '"validation_decision"' in content, \
            "Should have validation_decision column"

    def test_table_has_feedback_column(self):
        """Test that human_validations table has feedback column"""
        if HUMAN_VALIDATIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = HUMAN_VALIDATIONS_MIGRATION_FILE.read_text()
        assert "'feedback'" in content or '"feedback"' in content, \
            "Should have feedback column"

    def test_table_has_time_spent_seconds_column(self):
        """Test that human_validations table has time_spent_seconds column"""
        if HUMAN_VALIDATIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = HUMAN_VALIDATIONS_MIGRATION_FILE.read_text()
        assert "'time_spent_seconds'" in content or '"time_spent_seconds"' in content, \
            "Should have time_spent_seconds column"

    def test_table_has_is_second_opinion_column(self):
        """Test that human_validations table has is_second_opinion column"""
        if HUMAN_VALIDATIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = HUMAN_VALIDATIONS_MIGRATION_FILE.read_text()
        assert "'is_second_opinion'" in content or '"is_second_opinion"' in content, \
            "Should have is_second_opinion column"

    def test_table_has_created_at_column(self):
        """Test that human_validations table has created_at column"""
        if HUMAN_VALIDATIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = HUMAN_VALIDATIONS_MIGRATION_FILE.read_text()
        assert "'created_at'" in content or '"created_at"' in content, \
            "Should have created_at column"


class TestHumanValidationsColumnTypes:
    """Test column types"""

    def test_id_column_is_uuid(self):
        """Test that id column is UUID type"""
        if HUMAN_VALIDATIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = HUMAN_VALIDATIONS_MIGRATION_FILE.read_text()
        assert ("UUID" in content or "uuid" in content.lower()), \
            "id should be UUID type"

    def test_id_column_is_primary_key(self):
        """Test that id column is primary key"""
        if HUMAN_VALIDATIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = HUMAN_VALIDATIONS_MIGRATION_FILE.read_text()
        assert "primary_key" in content, "id should be primary key"

    def test_validation_result_id_is_uuid(self):
        """Test that validation_result_id is UUID type"""
        if HUMAN_VALIDATIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = HUMAN_VALIDATIONS_MIGRATION_FILE.read_text()
        assert "UUID" in content or "uuid" in content.lower(), \
            "validation_result_id should be UUID type"

    def test_validator_id_is_uuid(self):
        """Test that validator_id is UUID type"""
        if HUMAN_VALIDATIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = HUMAN_VALIDATIONS_MIGRATION_FILE.read_text()
        assert "UUID" in content or "uuid" in content.lower(), \
            "validator_id should be UUID type"

    def test_validation_decision_is_string(self):
        """Test that validation_decision is String/VARCHAR type"""
        if HUMAN_VALIDATIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = HUMAN_VALIDATIONS_MIGRATION_FILE.read_text()
        assert "String" in content or "VARCHAR" in content.upper(), \
            "validation_decision should be String/VARCHAR type"

    def test_feedback_is_text(self):
        """Test that feedback is Text type"""
        if HUMAN_VALIDATIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = HUMAN_VALIDATIONS_MIGRATION_FILE.read_text()
        assert "Text" in content or "TEXT" in content.upper(), \
            "feedback should be Text type"

    def test_time_spent_seconds_is_integer(self):
        """Test that time_spent_seconds is Integer type"""
        if HUMAN_VALIDATIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = HUMAN_VALIDATIONS_MIGRATION_FILE.read_text()
        assert "Integer" in content or "INTEGER" in content.upper(), \
            "time_spent_seconds should be Integer type"

    def test_is_second_opinion_is_boolean(self):
        """Test that is_second_opinion is Boolean type"""
        if HUMAN_VALIDATIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = HUMAN_VALIDATIONS_MIGRATION_FILE.read_text()
        assert "Boolean" in content or "BOOLEAN" in content.upper(), \
            "is_second_opinion should be Boolean type"

    def test_timestamp_columns_use_datetime(self):
        """Test that timestamp columns use DateTime"""
        if HUMAN_VALIDATIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = HUMAN_VALIDATIONS_MIGRATION_FILE.read_text()
        assert "DateTime" in content or "TIMESTAMP" in content.upper(), \
            "Timestamp columns should use DateTime or TIMESTAMP"


class TestHumanValidationsForeignKeys:
    """Test foreign key relationships"""

    def test_has_foreign_key_to_validation_results(self):
        """Test that validation_result_id has foreign key to validation_results"""
        if HUMAN_VALIDATIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = HUMAN_VALIDATIONS_MIGRATION_FILE.read_text()
        has_fk = "ForeignKey" in content or "REFERENCES" in content.upper()
        has_validation_results = "validation_results" in content
        assert has_fk and has_validation_results, \
            "Should have foreign key to validation_results table"

    def test_has_foreign_key_to_users(self):
        """Test that validator_id has foreign key to users"""
        if HUMAN_VALIDATIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = HUMAN_VALIDATIONS_MIGRATION_FILE.read_text()
        has_fk = "ForeignKey" in content or "REFERENCES" in content.upper()
        has_users = "users" in content
        assert has_fk and has_users, \
            "Should have foreign key to users table"


class TestHumanValidationsDefaults:
    """Test default values"""

    def test_is_second_opinion_has_default(self):
        """Test that is_second_opinion has default value"""
        if HUMAN_VALIDATIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = HUMAN_VALIDATIONS_MIGRATION_FILE.read_text()
        # Check for default=False or server_default
        has_default = ("default=" in content.lower() or "server_default" in content.lower())
        assert has_default, "is_second_opinion should have a default value"

    def test_created_at_has_default(self):
        """Test that created_at has default value"""
        if HUMAN_VALIDATIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = HUMAN_VALIDATIONS_MIGRATION_FILE.read_text()
        # Check for default or server_default with NOW()/CURRENT_TIMESTAMP/func.now()
        has_default = ("default=" in content.lower() or "server_default" in content.lower() or
                      "func.now()" in content or "NOW()" in content.upper())
        assert has_default, "created_at should have a default value (NOW/CURRENT_TIMESTAMP)"


class TestHumanValidationsDowngrade:
    """Test downgrade functionality"""

    def test_downgrade_drops_table(self):
        """Test that downgrade function drops human_validations table"""
        if HUMAN_VALIDATIONS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = HUMAN_VALIDATIONS_MIGRATION_FILE.read_text()
        assert "drop_table" in content.lower(), \
            "Downgrade should drop the table"
        assert "human_validations" in content, \
            "Downgrade should reference human_validations table"
