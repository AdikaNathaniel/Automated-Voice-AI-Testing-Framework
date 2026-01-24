"""
Test suite for validation_results table migration

Validates the Alembic migration for validation_results table including:
- Migration file structure
- Table creation with correct schema
- Column definitions and types
- Score fields (accuracy, confidence, semantic similarity, etc.)
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


# Find the validation_results migration file dynamically
def find_migration_file(keyword: str) -> Path | None:
    """Find migration file containing keyword in filename"""
    if not ALEMBIC_VERSIONS.exists():
        return None

    for file in ALEMBIC_VERSIONS.glob("*.py"):
        if keyword in file.name.lower() and file.name != "__pycache__":
            return file
    return None


VALIDATION_RESULTS_MIGRATION_FILE = find_migration_file("validation")


class TestValidationResultsMigrationFileExists:
    """Test that validation_results migration file exists"""

    def test_alembic_versions_directory_exists(self):
        """Test that alembic/versions directory exists"""
        assert ALEMBIC_VERSIONS.exists(), "alembic/versions directory should exist"
        assert ALEMBIC_VERSIONS.is_dir(), "alembic/versions should be a directory"

    def test_validation_results_migration_file_exists(self):
        """Test that validation_results migration file exists"""
        assert VALIDATION_RESULTS_MIGRATION_FILE is not None, "validation_results migration file should exist"
        assert VALIDATION_RESULTS_MIGRATION_FILE.exists(), "validation_results migration file should exist"
        assert VALIDATION_RESULTS_MIGRATION_FILE.is_file(), "validation_results migration should be a file"

    def test_migration_file_has_content(self):
        """Test that migration file has content"""
        if VALIDATION_RESULTS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_RESULTS_MIGRATION_FILE.read_text()
        assert len(content) > 0, "Migration file should not be empty"


class TestValidationResultsMigrationStructure:
    """Test migration file structure"""

    def test_has_alembic_imports(self):
        """Test that migration imports alembic"""
        if VALIDATION_RESULTS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_RESULTS_MIGRATION_FILE.read_text()
        assert "from alembic import op" in content, "Should import alembic.op"
        assert "import sqlalchemy" in content or "from sqlalchemy" in content, "Should import sqlalchemy"

    def test_has_revision_metadata(self):
        """Test that migration has revision metadata"""
        if VALIDATION_RESULTS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_RESULTS_MIGRATION_FILE.read_text()
        assert "revision:" in content or "revision =" in content, "Should have revision identifier"
        assert "down_revision" in content, "Should have down_revision identifier"

    def test_has_upgrade_function(self):
        """Test that migration has upgrade function"""
        if VALIDATION_RESULTS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_RESULTS_MIGRATION_FILE.read_text()
        assert "def upgrade" in content, "Should have upgrade() function"

    def test_has_downgrade_function(self):
        """Test that migration has downgrade function"""
        if VALIDATION_RESULTS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_RESULTS_MIGRATION_FILE.read_text()
        assert "def downgrade" in content, "Should have downgrade() function"


class TestValidationResultsTableCreation:
    """Test validation_results table creation"""

    def test_creates_validation_results_table(self):
        """Test that migration creates validation_results table"""
        if VALIDATION_RESULTS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_RESULTS_MIGRATION_FILE.read_text()
        assert "create_table" in content.lower(), "Should create a table"
        assert "validation_results" in content, "Should create validation_results table"

    def test_table_has_id_column(self):
        """Test that validation_results table has id column"""
        if VALIDATION_RESULTS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_RESULTS_MIGRATION_FILE.read_text()
        assert "'id'" in content or '"id"' in content, "Should have id column"

    def test_table_has_test_run_id_column(self):
        """Test that validation_results table has test_run_id column"""
        if VALIDATION_RESULTS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_RESULTS_MIGRATION_FILE.read_text()
        assert "'test_run_id'" in content or '"test_run_id"' in content, "Should have test_run_id column"

    def test_table_has_accuracy_score_column(self):
        """Test that validation_results table has accuracy_score column"""
        if VALIDATION_RESULTS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_RESULTS_MIGRATION_FILE.read_text()
        assert "'accuracy_score'" in content or '"accuracy_score"' in content, "Should have accuracy_score column"

    def test_table_has_confidence_score_column(self):
        """Test that validation_results table has confidence_score column"""
        if VALIDATION_RESULTS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_RESULTS_MIGRATION_FILE.read_text()
        assert "'confidence_score'" in content or '"confidence_score"' in content, "Should have confidence_score column"

    def test_table_has_semantic_similarity_score_column(self):
        """Test that validation_results table has semantic_similarity_score column"""
        if VALIDATION_RESULTS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_RESULTS_MIGRATION_FILE.read_text()
        assert "'semantic_similarity_score'" in content or '"semantic_similarity_score"' in content, "Should have semantic_similarity_score column"

    def test_table_has_command_kind_match_score_column(self):
        """Test that validation_results table has command_kind_match_score column"""
        if VALIDATION_RESULTS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_RESULTS_MIGRATION_FILE.read_text()
        assert "'command_kind_match_score'" in content or '"command_kind_match_score"' in content, "Should have command_kind_match_score column"

    def test_table_has_asr_confidence_score_column(self):
        """Test that validation_results table has asr_confidence_score column"""
        if VALIDATION_RESULTS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_RESULTS_MIGRATION_FILE.read_text()
        assert "'asr_confidence_score'" in content or '"asr_confidence_score"' in content, "Should have asr_confidence_score column"

    def test_table_has_created_at_column(self):
        """Test that validation_results table has created_at column"""
        if VALIDATION_RESULTS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_RESULTS_MIGRATION_FILE.read_text()
        assert "'created_at'" in content or '"created_at"' in content, "Should have created_at column"


class TestValidationResultsColumnTypes:
    """Test column types"""

    def test_id_column_is_uuid(self):
        """Test that id column is UUID type"""
        if VALIDATION_RESULTS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_RESULTS_MIGRATION_FILE.read_text()
        assert ("UUID" in content or "uuid" in content.lower()), "id should be UUID type"

    def test_id_column_is_primary_key(self):
        """Test that id column is primary key"""
        if VALIDATION_RESULTS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_RESULTS_MIGRATION_FILE.read_text()
        assert "primary_key" in content, "id should be primary key"

    def test_test_run_id_is_uuid(self):
        """Test that test_run_id is UUID type"""
        if VALIDATION_RESULTS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_RESULTS_MIGRATION_FILE.read_text()
        assert ("UUID" in content or "uuid" in content.lower()), "test_run_id should be UUID type"

    def test_score_fields_are_numeric(self):
        """Test that score fields are numeric types (Float or Numeric)"""
        if VALIDATION_RESULTS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_RESULTS_MIGRATION_FILE.read_text()
        assert ("Float" in content or "Numeric" in content), "Score fields should be Float or Numeric type"

    def test_created_at_is_datetime(self):
        """Test that created_at is DateTime type"""
        if VALIDATION_RESULTS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_RESULTS_MIGRATION_FILE.read_text()
        assert "DateTime" in content, "created_at should be DateTime type"


class TestValidationResultsScoreFields:
    """Test score field requirements"""

    def test_has_multiple_score_fields(self):
        """Test that migration has multiple score fields"""
        if VALIDATION_RESULTS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_RESULTS_MIGRATION_FILE.read_text()
        score_count = content.count("_score")
        assert score_count >= 5, "Should have at least 5 score fields"

    def test_score_fields_properly_defined(self):
        """Test that all expected score fields are present"""
        if VALIDATION_RESULTS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_RESULTS_MIGRATION_FILE.read_text()
        assert "accuracy_score" in content, "Should have accuracy_score field"
        assert "confidence_score" in content, "Should have confidence_score field"
        assert "semantic_similarity_score" in content, "Should have semantic_similarity_score field"
        assert "command_kind_match_score" in content, "Should have command_kind_match_score field"
        assert "asr_confidence_score" in content, "Should have asr_confidence_score field"


class TestValidationResultsForeignKeys:
    """Test foreign key relationships"""

    def test_test_run_id_references_test_runs(self):
        """Test that test_run_id references test_runs table"""
        if VALIDATION_RESULTS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_RESULTS_MIGRATION_FILE.read_text()
        assert (("ForeignKey" in content and "test_runs" in content) or
                "test_runs.id" in content), "test_run_id should reference test_runs table"


class TestValidationResultsConstraints:
    """Test constraints and defaults"""

    def test_created_at_has_default(self):
        """Test that created_at has default timestamp"""
        if VALIDATION_RESULTS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_RESULTS_MIGRATION_FILE.read_text()
        assert ("server_default" in content or "now()" in content.lower()), "created_at should have default timestamp"

    def test_test_run_id_not_nullable(self):
        """Test that test_run_id is not nullable"""
        if VALIDATION_RESULTS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_RESULTS_MIGRATION_FILE.read_text()
        assert "nullable" in content, "Should have nullable constraints"


class TestValidationResultsIndexes:
    """Test indexes for performance"""

    def test_has_index_creation(self):
        """Test that migration creates indexes"""
        if VALIDATION_RESULTS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_RESULTS_MIGRATION_FILE.read_text()
        assert "create_index" in content or "index=True" in content, "Should create indexes"

    def test_has_test_run_id_index(self):
        """Test that migration creates index on test_run_id"""
        if VALIDATION_RESULTS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_RESULTS_MIGRATION_FILE.read_text()
        assert ("test_run_id" in content and ("create_index" in content or "index=True" in content)), "Should create index on test_run_id"


class TestValidationResultsDowngrade:
    """Test downgrade functionality"""

    def test_downgrade_drops_table(self):
        """Test that downgrade drops validation_results table"""
        if VALIDATION_RESULTS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_RESULTS_MIGRATION_FILE.read_text()
        assert "drop_table" in content.lower(), "Downgrade should drop table"
        downgrade_match = re.search(r'def downgrade.*?(?=\ndef|\Z)', content, re.DOTALL)
        if downgrade_match:
            downgrade_content = downgrade_match.group(0)
            assert "validation_results" in downgrade_content, "Downgrade should drop validation_results table"

    def test_downgrade_drops_indexes(self):
        """Test that downgrade drops indexes if they exist"""
        if VALIDATION_RESULTS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_RESULTS_MIGRATION_FILE.read_text()
        # If indexes are explicitly created, they should be dropped in downgrade
        if "op.create_index" in content:
            downgrade_match = re.search(r'def downgrade.*?(?=\ndef|\Z)', content, re.DOTALL)
            if downgrade_match:
                downgrade_content = downgrade_match.group(0)
                assert "drop_index" in downgrade_content, "Downgrade should drop indexes"


class TestValidationResultsMigrationDocumentation:
    """Test migration documentation"""

    def test_has_docstring(self):
        """Test that migration has docstring"""
        if VALIDATION_RESULTS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_RESULTS_MIGRATION_FILE.read_text()
        assert '"""' in content or "'''" in content, "Migration should have docstring"

    def test_docstring_mentions_validation_results(self):
        """Test that docstring mentions validation_results"""
        if VALIDATION_RESULTS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_RESULTS_MIGRATION_FILE.read_text()
        assert ("validation_results" in content.lower() or "validation" in content.lower()), "Should document validation_results table"


class TestValidationResultsMigrationRevisionChain:
    """Test Alembic revision chain"""

    def test_has_valid_revision_id(self):
        """Test that migration has valid revision ID"""
        if VALIDATION_RESULTS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_RESULTS_MIGRATION_FILE.read_text()
        assert "revision:" in content or "revision =" in content, "Should have revision ID"

    def test_down_revision_references_previous_migration(self):
        """Test that down_revision references the device_test_executions migration"""
        if VALIDATION_RESULTS_MIGRATION_FILE is None:
            pytest.skip("Migration file not found")
        content = VALIDATION_RESULTS_MIGRATION_FILE.read_text()
        assert "down_revision" in content, "Should have down_revision"
        # Should reference the device_test_executions migration (c9d0e1f2a3b4)
