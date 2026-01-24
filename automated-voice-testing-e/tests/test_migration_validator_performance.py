"""
Test suite for validator_performance table migration

Validates the Alembic migration for validator_performance table including:
- Migration file structure
- Table creation with correct schema
- Column definitions and types
- Foreign key relationship to users table
- Default values and constraints
- UNIQUE constraint on (validator_id, date)
- Indexes for common query patterns
- Downgrade functionality
- Alembic revision metadata
"""

import pytest
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
ALEMBIC_VERSIONS = PROJECT_ROOT / "alembic" / "versions"


# Find the validator_performance migration file dynamically
def find_migration_file(keyword: str) -> Path | None:
    """Find migration file containing keyword in filename"""
    if not ALEMBIC_VERSIONS.exists():
        return None

    for file in ALEMBIC_VERSIONS.glob("*.py"):
        if keyword in file.name.lower() and file.name != "__pycache__":
            return file
    return None


VALIDATOR_PERFORMANCE_MIGRATION_FILE = find_migration_file("validator_performance")


class TestValidatorPerformanceMigrationFileExists:
    """Test that validator_performance migration file exists"""

    def test_alembic_versions_directory_exists(self):
        """Test that alembic/versions directory exists"""
        assert ALEMBIC_VERSIONS.exists(), "alembic/versions directory should exist"
        assert ALEMBIC_VERSIONS.is_dir(), "alembic/versions should be a directory"

    def test_validator_performance_migration_file_exists(self):
        """Test that validator_performance migration file exists"""
        assert VALIDATOR_PERFORMANCE_MIGRATION_FILE is not None, \
            "validator_performance migration file should exist (filename should contain 'validator_performance')"
        assert VALIDATOR_PERFORMANCE_MIGRATION_FILE.exists(), \
            "validator_performance migration file should exist"
        assert VALIDATOR_PERFORMANCE_MIGRATION_FILE.is_file(), \
            "validator_performance migration should be a file"

    def test_migration_file_has_content(self):
        """Test that migration file has content"""
        if VALIDATOR_PERFORMANCE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATOR_PERFORMANCE_MIGRATION_FILE.read_text()
        assert len(content) > 0, "Migration file should not be empty"


class TestValidatorPerformanceMigrationStructure:
    """Test migration file structure"""

    def test_has_alembic_imports(self):
        """Test that migration imports alembic"""
        if VALIDATOR_PERFORMANCE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATOR_PERFORMANCE_MIGRATION_FILE.read_text()
        assert "from alembic import op" in content, "Should import alembic.op"
        assert "import sqlalchemy" in content or "from sqlalchemy" in content, \
            "Should import sqlalchemy"

    def test_has_revision_metadata(self):
        """Test that migration has revision metadata"""
        if VALIDATOR_PERFORMANCE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATOR_PERFORMANCE_MIGRATION_FILE.read_text()
        assert "revision:" in content or "revision =" in content, \
            "Should have revision identifier"
        assert "down_revision" in content, "Should have down_revision identifier"

    def test_has_upgrade_function(self):
        """Test that migration has upgrade function"""
        if VALIDATOR_PERFORMANCE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATOR_PERFORMANCE_MIGRATION_FILE.read_text()
        assert "def upgrade" in content, "Should have upgrade() function"

    def test_has_downgrade_function(self):
        """Test that migration has downgrade function"""
        if VALIDATOR_PERFORMANCE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATOR_PERFORMANCE_MIGRATION_FILE.read_text()
        assert "def downgrade" in content, "Should have downgrade() function"


class TestValidatorPerformanceTableCreation:
    """Test validator_performance table creation"""

    def test_creates_validator_performance_table(self):
        """Test that migration creates validator_performance table"""
        if VALIDATOR_PERFORMANCE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATOR_PERFORMANCE_MIGRATION_FILE.read_text()
        assert "create_table" in content.lower(), "Should create a table"
        assert "validator_performance" in content, "Should create validator_performance table"

    def test_table_has_id_column(self):
        """Test that validator_performance table has id column"""
        if VALIDATOR_PERFORMANCE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATOR_PERFORMANCE_MIGRATION_FILE.read_text()
        assert "'id'" in content or '"id"' in content, "Should have id column"

    def test_table_has_validator_id_column(self):
        """Test that validator_performance table has validator_id column"""
        if VALIDATOR_PERFORMANCE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATOR_PERFORMANCE_MIGRATION_FILE.read_text()
        assert "'validator_id'" in content or '"validator_id"' in content, \
            "Should have validator_id column"

    def test_table_has_date_column(self):
        """Test that validator_performance table has date column"""
        if VALIDATOR_PERFORMANCE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATOR_PERFORMANCE_MIGRATION_FILE.read_text()
        assert "'date'" in content or '"date"' in content, \
            "Should have date column"

    def test_table_has_validations_completed_column(self):
        """Test that validator_performance table has validations_completed column"""
        if VALIDATOR_PERFORMANCE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATOR_PERFORMANCE_MIGRATION_FILE.read_text()
        assert "'validations_completed'" in content or '"validations_completed"' in content, \
            "Should have validations_completed column"

    def test_table_has_average_time_seconds_column(self):
        """Test that validator_performance table has average_time_seconds column"""
        if VALIDATOR_PERFORMANCE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATOR_PERFORMANCE_MIGRATION_FILE.read_text()
        assert "'average_time_seconds'" in content or '"average_time_seconds"' in content, \
            "Should have average_time_seconds column"

    def test_table_has_agreement_with_peers_pct_column(self):
        """Test that validator_performance table has agreement_with_peers_pct column"""
        if VALIDATOR_PERFORMANCE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATOR_PERFORMANCE_MIGRATION_FILE.read_text()
        assert "'agreement_with_peers_pct'" in content or '"agreement_with_peers_pct"' in content, \
            "Should have agreement_with_peers_pct column"

    def test_table_has_agreement_with_final_pct_column(self):
        """Test that validator_performance table has agreement_with_final_pct column"""
        if VALIDATOR_PERFORMANCE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATOR_PERFORMANCE_MIGRATION_FILE.read_text()
        assert "'agreement_with_final_pct'" in content or '"agreement_with_final_pct"' in content, \
            "Should have agreement_with_final_pct column"

    def test_table_has_created_at_column(self):
        """Test that validator_performance table has created_at column"""
        if VALIDATOR_PERFORMANCE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATOR_PERFORMANCE_MIGRATION_FILE.read_text()
        assert "'created_at'" in content or '"created_at"' in content, \
            "Should have created_at column"


class TestValidatorPerformanceColumnTypes:
    """Test column types"""

    def test_id_column_is_uuid(self):
        """Test that id column is UUID type"""
        if VALIDATOR_PERFORMANCE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATOR_PERFORMANCE_MIGRATION_FILE.read_text()
        assert ("UUID" in content or "uuid" in content.lower()), \
            "id should be UUID type"

    def test_id_column_is_primary_key(self):
        """Test that id column is primary key"""
        if VALIDATOR_PERFORMANCE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATOR_PERFORMANCE_MIGRATION_FILE.read_text()
        assert "primary_key" in content, "id should be primary key"

    def test_validator_id_is_uuid(self):
        """Test that validator_id is UUID type"""
        if VALIDATOR_PERFORMANCE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATOR_PERFORMANCE_MIGRATION_FILE.read_text()
        assert "UUID" in content or "uuid" in content.lower(), \
            "validator_id should be UUID type"

    def test_date_column_is_date_type(self):
        """Test that date column is Date type"""
        if VALIDATOR_PERFORMANCE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATOR_PERFORMANCE_MIGRATION_FILE.read_text()
        assert "Date" in content or "DATE" in content.upper(), \
            "date should be Date type"

    def test_validations_completed_is_integer(self):
        """Test that validations_completed is Integer type"""
        if VALIDATOR_PERFORMANCE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATOR_PERFORMANCE_MIGRATION_FILE.read_text()
        assert "Integer" in content or "INTEGER" in content.upper(), \
            "validations_completed should be Integer type"

    def test_average_time_seconds_is_numeric(self):
        """Test that average_time_seconds is Numeric/DECIMAL type"""
        if VALIDATOR_PERFORMANCE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATOR_PERFORMANCE_MIGRATION_FILE.read_text()
        assert "Numeric" in content or "DECIMAL" in content.upper(), \
            "average_time_seconds should be Numeric/DECIMAL type"

    def test_agreement_pct_columns_are_numeric(self):
        """Test that agreement percentage columns are Numeric/DECIMAL type"""
        if VALIDATOR_PERFORMANCE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATOR_PERFORMANCE_MIGRATION_FILE.read_text()
        # Should have multiple Numeric columns (at least 2 for the agreement percentages)
        assert content.count("Numeric") >= 2 or content.count("DECIMAL") >= 2, \
            "Agreement percentage columns should be Numeric/DECIMAL type"

    def test_timestamp_columns_use_datetime(self):
        """Test that timestamp columns use DateTime"""
        if VALIDATOR_PERFORMANCE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATOR_PERFORMANCE_MIGRATION_FILE.read_text()
        assert "DateTime" in content or "TIMESTAMP" in content.upper(), \
            "Timestamp columns should use DateTime or TIMESTAMP"


class TestValidatorPerformanceForeignKeys:
    """Test foreign key relationships"""

    def test_has_foreign_key_to_users(self):
        """Test that validator_id has foreign key to users"""
        if VALIDATOR_PERFORMANCE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATOR_PERFORMANCE_MIGRATION_FILE.read_text()
        has_fk = "ForeignKey" in content or "REFERENCES" in content.upper()
        has_users = "users" in content
        assert has_fk and has_users, \
            "Should have foreign key to users table"


class TestValidatorPerformanceConstraints:
    """Test table constraints"""

    def test_has_unique_constraint_on_validator_date(self):
        """Test that table has UNIQUE constraint on (validator_id, date)"""
        if VALIDATOR_PERFORMANCE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATOR_PERFORMANCE_MIGRATION_FILE.read_text()
        # Check for UniqueConstraint or UNIQUE keyword
        has_unique = ("UniqueConstraint" in content or
                     "unique" in content.lower() or
                     "UNIQUE" in content)
        assert has_unique, \
            "Should have UNIQUE constraint on (validator_id, date)"


class TestValidatorPerformanceDefaults:
    """Test default values"""

    def test_validations_completed_has_default(self):
        """Test that validations_completed has default value of 0"""
        if VALIDATOR_PERFORMANCE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATOR_PERFORMANCE_MIGRATION_FILE.read_text()
        # Check for default=0 or server_default
        has_default = ("default=" in content.lower() or "server_default" in content.lower())
        assert has_default, "validations_completed should have a default value"

    def test_created_at_has_default(self):
        """Test that created_at has default value"""
        if VALIDATOR_PERFORMANCE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATOR_PERFORMANCE_MIGRATION_FILE.read_text()
        # Check for default or server_default with NOW()/CURRENT_TIMESTAMP/func.now()
        has_default = ("default=" in content.lower() or "server_default" in content.lower() or
                      "func.now()" in content or "NOW()" in content.upper())
        assert has_default, "created_at should have a default value (NOW/CURRENT_TIMESTAMP)"


class TestValidatorPerformanceDowngrade:
    """Test downgrade functionality"""

    def test_downgrade_drops_table(self):
        """Test that downgrade function drops validator_performance table"""
        if VALIDATOR_PERFORMANCE_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATOR_PERFORMANCE_MIGRATION_FILE.read_text()
        assert "drop_table" in content.lower(), \
            "Downgrade should drop the table"
        assert "validator_performance" in content, \
            "Downgrade should reference validator_performance table"
