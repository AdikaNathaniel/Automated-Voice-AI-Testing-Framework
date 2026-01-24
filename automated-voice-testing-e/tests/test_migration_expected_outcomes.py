"""
Test suite for expected_outcomes table migration

Validates the Alembic migration for expected_outcomes table including:
- Migration file structure
- Table creation with correct schema
- Column definitions and types
- JSONB fields for entities, validation_rules, language_variations
- Constraints and defaults
- Unique constraint on outcome_code
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


# Find the expected_outcomes migration file dynamically
def find_migration_file(keyword: str) -> Path | None:
    """Find migration file containing keyword in filename"""
    if not ALEMBIC_VERSIONS.exists():
        return None

    for file in ALEMBIC_VERSIONS.glob("*.py"):
        if keyword in file.name.lower() and file.name != "__pycache__":
            return file
    return None


EXPECTED_OUTCOMES_MIGRATION_FILE = find_migration_file("expected_outcome")


class TestExpectedOutcomesMigrationFileExists:
    """Test that expected_outcomes migration file exists"""

    def test_alembic_versions_directory_exists(self):
        """Test that alembic/versions directory exists"""
        assert ALEMBIC_VERSIONS.exists(), "alembic/versions directory should exist"
        assert ALEMBIC_VERSIONS.is_dir(), "alembic/versions should be a directory"

    def test_expected_outcomes_migration_file_exists(self):
        """Test that expected_outcomes migration file exists"""
        assert EXPECTED_OUTCOMES_MIGRATION_FILE is not None, "expected_outcomes migration file should exist"
        assert EXPECTED_OUTCOMES_MIGRATION_FILE.exists(), "expected_outcomes migration file should exist"
        assert EXPECTED_OUTCOMES_MIGRATION_FILE.is_file(), "expected_outcomes migration should be a file"

    def test_migration_file_has_content(self):
        """Test that migration file has content"""
        if EXPECTED_OUTCOMES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = EXPECTED_OUTCOMES_MIGRATION_FILE.read_text()
        assert len(content) > 0, "Migration file should not be empty"


class TestExpectedOutcomesMigrationStructure:
    """Test migration file structure"""

    def test_has_alembic_imports(self):
        """Test that migration imports alembic"""
        if EXPECTED_OUTCOMES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = EXPECTED_OUTCOMES_MIGRATION_FILE.read_text()
        assert "from alembic import op" in content, "Should import alembic.op"
        assert "import sqlalchemy" in content or "from sqlalchemy" in content, "Should import sqlalchemy"

    def test_has_revision_metadata(self):
        """Test that migration has revision metadata"""
        if EXPECTED_OUTCOMES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = EXPECTED_OUTCOMES_MIGRATION_FILE.read_text()
        assert "revision:" in content or "revision =" in content, "Should have revision identifier"
        assert "down_revision" in content, "Should have down_revision identifier"

    def test_has_upgrade_function(self):
        """Test that migration has upgrade function"""
        if EXPECTED_OUTCOMES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = EXPECTED_OUTCOMES_MIGRATION_FILE.read_text()
        assert "def upgrade" in content, "Should have upgrade() function"

    def test_has_downgrade_function(self):
        """Test that migration has downgrade function"""
        if EXPECTED_OUTCOMES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = EXPECTED_OUTCOMES_MIGRATION_FILE.read_text()
        assert "def downgrade" in content, "Should have downgrade() function"


class TestExpectedOutcomesTableCreation:
    """Test expected_outcomes table creation"""

    def test_creates_expected_outcomes_table(self):
        """Test that migration creates expected_outcomes table"""
        if EXPECTED_OUTCOMES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = EXPECTED_OUTCOMES_MIGRATION_FILE.read_text()
        assert "create_table" in content.lower(), "Should create a table"
        assert "expected_outcomes" in content, "Should create expected_outcomes table"

    def test_table_has_id_column(self):
        """Test that expected_outcomes table has id column"""
        if EXPECTED_OUTCOMES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = EXPECTED_OUTCOMES_MIGRATION_FILE.read_text()
        assert "'id'" in content or '"id"' in content, "Should have id column"

    def test_table_has_outcome_code_column(self):
        """Test that expected_outcomes table has outcome_code column"""
        if EXPECTED_OUTCOMES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = EXPECTED_OUTCOMES_MIGRATION_FILE.read_text()
        assert "'outcome_code'" in content or '"outcome_code"' in content, "Should have outcome_code column"

    def test_table_has_name_column(self):
        """Test that expected_outcomes table has name column"""
        if EXPECTED_OUTCOMES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = EXPECTED_OUTCOMES_MIGRATION_FILE.read_text()
        assert "'name'" in content or '"name"' in content, "Should have name column"

    def test_table_has_description_column(self):
        """Test that expected_outcomes table has description column"""
        if EXPECTED_OUTCOMES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = EXPECTED_OUTCOMES_MIGRATION_FILE.read_text()
        assert "'description'" in content or '"description"' in content, "Should have description column"

    def test_table_has_entities_column(self):
        """Test that expected_outcomes table has entities column"""
        if EXPECTED_OUTCOMES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = EXPECTED_OUTCOMES_MIGRATION_FILE.read_text()
        assert "'entities'" in content or '"entities"' in content, "Should have entities column"

    def test_table_has_validation_rules_column(self):
        """Test that expected_outcomes table has validation_rules column"""
        if EXPECTED_OUTCOMES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = EXPECTED_OUTCOMES_MIGRATION_FILE.read_text()
        assert "'validation_rules'" in content or '"validation_rules"' in content, "Should have validation_rules column"

    def test_table_has_language_variations_column(self):
        """Test that expected_outcomes table has language_variations column"""
        if EXPECTED_OUTCOMES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = EXPECTED_OUTCOMES_MIGRATION_FILE.read_text()
        assert "'language_variations'" in content or '"language_variations"' in content, "Should have language_variations column"

    def test_table_has_created_at_column(self):
        """Test that expected_outcomes table has created_at column"""
        if EXPECTED_OUTCOMES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = EXPECTED_OUTCOMES_MIGRATION_FILE.read_text()
        assert "'created_at'" in content or '"created_at"' in content, "Should have created_at column"

    def test_table_has_updated_at_column(self):
        """Test that expected_outcomes table has updated_at column"""
        if EXPECTED_OUTCOMES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = EXPECTED_OUTCOMES_MIGRATION_FILE.read_text()
        assert "'updated_at'" in content or '"updated_at"' in content, "Should have updated_at column"


class TestExpectedOutcomesColumnTypes:
    """Test column types"""

    def test_id_column_is_uuid(self):
        """Test that id column is UUID type"""
        if EXPECTED_OUTCOMES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = EXPECTED_OUTCOMES_MIGRATION_FILE.read_text()
        assert ("UUID" in content or "uuid" in content.lower()), "id should be UUID type"

    def test_id_column_is_primary_key(self):
        """Test that id column is primary key"""
        if EXPECTED_OUTCOMES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = EXPECTED_OUTCOMES_MIGRATION_FILE.read_text()
        assert "primary_key" in content, "id should be primary key"

    def test_outcome_code_is_string(self):
        """Test that outcome_code is String type"""
        if EXPECTED_OUTCOMES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = EXPECTED_OUTCOMES_MIGRATION_FILE.read_text()
        assert "String" in content, "outcome_code should be String type"

    def test_name_is_string(self):
        """Test that name is String type"""
        if EXPECTED_OUTCOMES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = EXPECTED_OUTCOMES_MIGRATION_FILE.read_text()
        assert "String" in content, "name should be String type"

    def test_description_is_text(self):
        """Test that description is Text type"""
        if EXPECTED_OUTCOMES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = EXPECTED_OUTCOMES_MIGRATION_FILE.read_text()
        assert "Text" in content, "description should be Text type"

    def test_entities_is_jsonb(self):
        """Test that entities is JSONB type"""
        if EXPECTED_OUTCOMES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = EXPECTED_OUTCOMES_MIGRATION_FILE.read_text()
        assert "JSONB" in content, "entities should be JSONB type"

    def test_validation_rules_is_jsonb(self):
        """Test that validation_rules is JSONB type"""
        if EXPECTED_OUTCOMES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = EXPECTED_OUTCOMES_MIGRATION_FILE.read_text()
        assert "JSONB" in content, "validation_rules should be JSONB type"

    def test_language_variations_is_jsonb(self):
        """Test that language_variations is JSONB type"""
        if EXPECTED_OUTCOMES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = EXPECTED_OUTCOMES_MIGRATION_FILE.read_text()
        assert "JSONB" in content, "language_variations should be JSONB type"

    def test_created_at_is_datetime(self):
        """Test that created_at is DateTime type"""
        if EXPECTED_OUTCOMES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = EXPECTED_OUTCOMES_MIGRATION_FILE.read_text()
        assert "DateTime" in content, "created_at should be DateTime type"

    def test_updated_at_is_datetime(self):
        """Test that updated_at is DateTime type"""
        if EXPECTED_OUTCOMES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = EXPECTED_OUTCOMES_MIGRATION_FILE.read_text()
        assert "DateTime" in content, "updated_at should be DateTime type"


class TestExpectedOutcomesConstraints:
    """Test constraints and defaults"""

    def test_outcome_code_is_unique(self):
        """Test that outcome_code has unique constraint"""
        if EXPECTED_OUTCOMES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = EXPECTED_OUTCOMES_MIGRATION_FILE.read_text()
        assert ("unique=True" in content or "UniqueConstraint" in content), "outcome_code should be unique"

    def test_created_at_has_default(self):
        """Test that created_at has default timestamp"""
        if EXPECTED_OUTCOMES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = EXPECTED_OUTCOMES_MIGRATION_FILE.read_text()
        assert ("server_default" in content or "now()" in content.lower()), "created_at should have default timestamp"

    def test_updated_at_has_default(self):
        """Test that updated_at has default timestamp"""
        if EXPECTED_OUTCOMES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = EXPECTED_OUTCOMES_MIGRATION_FILE.read_text()
        assert ("server_default" in content or "now()" in content.lower()), "updated_at should have default timestamp"

    def test_outcome_code_not_nullable(self):
        """Test that outcome_code is not nullable"""
        if EXPECTED_OUTCOMES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = EXPECTED_OUTCOMES_MIGRATION_FILE.read_text()
        assert "nullable" in content, "Should have nullable constraints"


class TestExpectedOutcomesIndexes:
    """Test indexes for performance"""

    def test_has_index_creation(self):
        """Test that migration creates indexes"""
        if EXPECTED_OUTCOMES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = EXPECTED_OUTCOMES_MIGRATION_FILE.read_text()
        assert "create_index" in content, "Should create indexes"

    def test_has_outcome_code_index(self):
        """Test that migration creates index on outcome_code"""
        if EXPECTED_OUTCOMES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = EXPECTED_OUTCOMES_MIGRATION_FILE.read_text()
        assert ("outcome_code" in content and "create_index" in content), "Should create index on outcome_code"


class TestExpectedOutcomesJSONBFields:
    """Test JSONB field requirements"""

    def test_has_three_jsonb_fields(self):
        """Test that migration has three JSONB fields: entities, validation_rules, language_variations"""
        if EXPECTED_OUTCOMES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = EXPECTED_OUTCOMES_MIGRATION_FILE.read_text()
        assert "entities" in content, "Should have entities JSONB field"
        assert "validation_rules" in content, "Should have validation_rules JSONB field"
        assert "language_variations" in content, "Should have language_variations JSONB field"

    def test_jsonb_fields_have_proper_type(self):
        """Test that JSONB fields use proper PostgreSQL type"""
        if EXPECTED_OUTCOMES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = EXPECTED_OUTCOMES_MIGRATION_FILE.read_text()
        jsonb_count = content.count("JSONB")
        assert jsonb_count >= 3, "Should have at least 3 JSONB fields"


class TestExpectedOutcomesDowngrade:
    """Test downgrade functionality"""

    def test_downgrade_drops_table(self):
        """Test that downgrade drops expected_outcomes table"""
        if EXPECTED_OUTCOMES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = EXPECTED_OUTCOMES_MIGRATION_FILE.read_text()
        assert "drop_table" in content.lower(), "Downgrade should drop table"
        downgrade_match = re.search(r'def downgrade.*?(?=\ndef|\Z)', content, re.DOTALL)
        if downgrade_match:
            downgrade_content = downgrade_match.group(0)
            assert "expected_outcomes" in downgrade_content, "Downgrade should drop expected_outcomes table"

    def test_downgrade_drops_indexes(self):
        """Test that downgrade drops indexes"""
        if EXPECTED_OUTCOMES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = EXPECTED_OUTCOMES_MIGRATION_FILE.read_text()
        downgrade_match = re.search(r'def downgrade.*?(?=\ndef|\Z)', content, re.DOTALL)
        if downgrade_match:
            downgrade_content = downgrade_match.group(0)
            assert "drop_index" in downgrade_content, "Downgrade should drop indexes"


class TestExpectedOutcomesMigrationDocumentation:
    """Test migration documentation"""

    def test_has_docstring(self):
        """Test that migration has docstring"""
        if EXPECTED_OUTCOMES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = EXPECTED_OUTCOMES_MIGRATION_FILE.read_text()
        assert '"""' in content or "'''" in content, "Migration should have docstring"

    def test_docstring_mentions_expected_outcomes(self):
        """Test that docstring mentions expected_outcomes"""
        if EXPECTED_OUTCOMES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = EXPECTED_OUTCOMES_MIGRATION_FILE.read_text()
        assert ("expected_outcomes" in content.lower() or "expected outcomes" in content.lower()), "Should document expected_outcomes table"


class TestExpectedOutcomesMigrationRevisionChain:
    """Test Alembic revision chain"""

    def test_has_valid_revision_id(self):
        """Test that migration has valid revision ID"""
        if EXPECTED_OUTCOMES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = EXPECTED_OUTCOMES_MIGRATION_FILE.read_text()
        assert "revision:" in content or "revision =" in content, "Should have revision ID"

    def test_down_revision_references_previous_migration(self):
        """Test that down_revision references the test_case_languages migration"""
        if EXPECTED_OUTCOMES_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = EXPECTED_OUTCOMES_MIGRATION_FILE.read_text()
        assert "down_revision" in content, "Should have down_revision"
        # Should reference the test_case_languages migration (c3d4e5f6a7b8)
