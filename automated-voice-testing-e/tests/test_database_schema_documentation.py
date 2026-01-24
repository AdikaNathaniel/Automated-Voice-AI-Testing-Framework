"""
Test Database Schema Documentation

This module tests that the database schema documentation provides comprehensive
information about the database structure, tables, and relationships.

Test Coverage:
    - File existence and structure
    - Required sections present
    - All tables documented
    - Field descriptions
    - Relationships documented
    - ER diagram present
    - Data types and constraints
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest


# =============================================================================
# File Structure Tests
# =============================================================================

class TestDatabaseSchemaFileStructure:
    """Test database schema documentation file structure"""

    def test_database_schema_file_exists(self):
        """Test that database-schema.md file exists"""
        # Arrange
        project_root = Path(__file__).parent.parent
        schema_file = project_root / "docs" / "database-schema.md"

        # Act & Assert
        assert schema_file.exists(), "database-schema.md should exist in docs/"
        assert schema_file.is_file(), "database-schema.md should be a file"

    def test_database_schema_has_content(self):
        """Test that database-schema.md has substantial content"""
        # Arrange
        project_root = Path(__file__).parent.parent
        schema_file = project_root / "docs" / "database-schema.md"

        # Act
        content = schema_file.read_text()

        # Assert
        assert len(content) > 3000, \
            "Database schema should have substantial content (>3000 chars)"

    def test_database_schema_is_markdown(self):
        """Test that database schema uses markdown formatting"""
        # Arrange
        project_root = Path(__file__).parent.parent
        schema_file = project_root / "docs" / "database-schema.md"

        # Act
        content = schema_file.read_text()

        # Assert
        assert "# " in content or "## " in content, \
            "Database schema should have markdown headers"


# =============================================================================
# Required Sections Tests
# =============================================================================

class TestDatabaseSchemaRequiredSections:
    """Test that database schema has all required sections"""

    @pytest.fixture
    def content(self):
        """Load database schema content"""
        project_root = Path(__file__).parent.parent
        schema_file = project_root / "docs" / "database-schema.md"
        return schema_file.read_text()

    def test_has_title(self, content):
        """Test that database schema has a title"""
        # Assert
        assert "# " in content, "Database schema should have a main title"

    def test_has_overview_section(self, content):
        """Test that database schema has overview section"""
        # Assert
        content_lower = content.lower()
        assert "overview" in content_lower or "introduction" in content_lower, \
            "Database schema should have overview section"

    def test_has_er_diagram_section(self, content):
        """Test that database schema has ER diagram section"""
        # Assert
        content_lower = content.lower()
        assert "diagram" in content_lower or "er" in content_lower or "entity" in content_lower, \
            "Database schema should have ER diagram section"

    def test_has_tables_section(self, content):
        """Test that database schema has tables section"""
        # Assert
        content_lower = content.lower()
        assert "table" in content_lower, \
            "Database schema should have tables section"

    def test_has_relationships_section(self, content):
        """Test that database schema has relationships section"""
        # Assert
        content_lower = content.lower()
        assert "relationship" in content_lower or "foreign key" in content_lower, \
            "Database schema should have relationships section"


# =============================================================================
# Table Documentation Tests
# =============================================================================

class TestDatabaseSchemaTables:
    """Test that database schema documents all tables"""

    @pytest.fixture
    def content(self):
        """Load database schema content"""
        project_root = Path(__file__).parent.parent
        schema_file = project_root / "docs" / "database-schema.md"
        return schema_file.read_text()

    def test_documents_users_table(self, content):
        """Test that database schema documents users table"""
        # Assert
        content_lower = content.lower()
        assert "user" in content_lower, \
            "Database schema should document users table"

    def test_documents_test_cases_table(self, content):
        """Test that database schema documents test_cases table"""
        # Assert
        content_lower = content.lower()
        assert "test_case" in content_lower or "test case" in content_lower, \
            "Database schema should document test_cases table"

    def test_documents_test_runs_table(self, content):
        """Test that database schema documents test_runs table"""
        # Assert
        content_lower = content.lower()
        assert "test_run" in content_lower or "test run" in content_lower, \
            "Database schema should document test_runs table"

    def test_documents_test_suites_table(self, content):
        """Test that database schema documents test_suites table"""
        # Assert
        content_lower = content.lower()
        assert "test_suite" in content_lower or "test suite" in content_lower, \
            "Database schema should document test_suites table"

    def test_documents_test_executions_table(self, content):
        """Test that database schema documents test executions table"""
        # Assert
        content_lower = content.lower()
        assert "execution" in content_lower, \
            "Database schema should document test executions table"

    def test_documents_validation_results_table(self, content):
        """Test that database schema documents validation_results table"""
        # Assert
        content_lower = content.lower()
        assert "validation" in content_lower, \
            "Database schema should document validation_results table"

    def test_documents_expected_outcomes_table(self, content):
        """Test that database schema documents expected_outcomes table"""
        # Assert
        content_lower = content.lower()
        assert "expected" in content_lower or "outcome" in content_lower, \
            "Database schema should document expected_outcomes table"

    def test_documents_configuration_table(self, content):
        """Test that database schema documents configuration table"""
        # Assert
        content_lower = content.lower()
        assert "configuration" in content_lower, \
            "Database schema should document configuration table"


# =============================================================================
# Field Documentation Tests
# =============================================================================

class TestDatabaseSchemaFields:
    """Test that database schema documents table fields"""

    @pytest.fixture
    def content(self):
        """Load database schema content"""
        project_root = Path(__file__).parent.parent
        schema_file = project_root / "docs" / "database-schema.md"
        return schema_file.read_text()

    def test_documents_field_names(self, content):
        """Test that database schema documents field names"""
        # Assert
        content_lower = content.lower()
        # Should mention common field names
        assert "id" in content_lower, \
            "Database schema should document field names (e.g., id)"

    def test_documents_data_types(self, content):
        """Test that database schema documents data types"""
        # Assert
        content_lower = content.lower()
        # Should mention common data types
        has_types = any(dtype in content_lower for dtype in [
            "integer", "string", "text", "boolean", "datetime",
            "varchar", "int", "timestamp"
        ])
        assert has_types, \
            "Database schema should document data types"

    def test_documents_primary_keys(self, content):
        """Test that database schema documents primary keys"""
        # Assert
        content_lower = content.lower()
        assert "primary key" in content_lower or "pk" in content_lower, \
            "Database schema should document primary keys"

    def test_documents_foreign_keys(self, content):
        """Test that database schema documents foreign keys"""
        # Assert
        content_lower = content.lower()
        assert "foreign key" in content_lower or "fk" in content_lower or "reference" in content_lower, \
            "Database schema should document foreign keys"


# =============================================================================
# Relationship Documentation Tests
# =============================================================================

class TestDatabaseSchemaRelationships:
    """Test that database schema documents table relationships"""

    @pytest.fixture
    def content(self):
        """Load database schema content"""
        project_root = Path(__file__).parent.parent
        schema_file = project_root / "docs" / "database-schema.md"
        return schema_file.read_text()

    def test_documents_one_to_many_relationships(self, content):
        """Test that database schema documents one-to-many relationships"""
        # Assert
        content_lower = content.lower()
        has_relationship_info = any(term in content_lower for term in [
            "one-to-many", "one to many", "1:n", "has many"
        ])
        assert has_relationship_info, \
            "Database schema should document one-to-many relationships"

    def test_documents_relationship_descriptions(self, content):
        """Test that database schema describes relationships"""
        # Assert
        content_lower = content.lower()
        # Should describe relationships between tables
        has_relationship_desc = "relationship" in content_lower or "belongs to" in content_lower
        assert has_relationship_desc, \
            "Database schema should describe table relationships"


# =============================================================================
# ER Diagram Tests
# =============================================================================

class TestDatabaseSchemaERDiagram:
    """Test that database schema includes ER diagram"""

    @pytest.fixture
    def content(self):
        """Load database schema content"""
        project_root = Path(__file__).parent.parent
        schema_file = project_root / "docs" / "database-schema.md"
        return schema_file.read_text()

    def test_has_visual_representation(self, content):
        """Test that database schema has visual representation"""
        # Assert
        content_lower = content.lower()
        # Should have some form of diagram or visual representation
        has_diagram = any(term in content_lower for term in [
            "diagram", "```mermaid", "```", "visual", "chart"
        ])
        assert has_diagram, \
            "Database schema should have visual representation or diagram"

    def test_has_mermaid_diagram(self, content):
        """Test that database schema uses Mermaid for ER diagram"""
        # Assert
        # Mermaid is a common markdown-friendly diagram tool
        has_mermaid = "```mermaid" in content.lower() or "```erdiagram" in content.lower()
        # Or it could be a text-based diagram
        has_text_diagram = "```" in content and ("table" in content.lower() or "entity" in content.lower())

        assert has_mermaid or has_text_diagram, \
            "Database schema should have Mermaid diagram or text-based diagram"


# =============================================================================
# Constraints and Indexes Tests
# =============================================================================

class TestDatabaseSchemaConstraints:
    """Test that database schema documents constraints and indexes"""

    @pytest.fixture
    def content(self):
        """Load database schema content"""
        project_root = Path(__file__).parent.parent
        schema_file = project_root / "docs" / "database-schema.md"
        return schema_file.read_text()

    def test_documents_constraints(self, content):
        """Test that database schema documents constraints"""
        # Assert
        content_lower = content.lower()
        has_constraints = any(term in content_lower for term in [
            "constraint", "unique", "not null", "nullable", "required"
        ])
        assert has_constraints, \
            "Database schema should document constraints"

    def test_documents_indexes(self, content):
        """Test that database schema mentions indexes"""
        # Assert
        content_lower = content.lower()
        # Indexes are important for performance
        has_index_info = "index" in content_lower or "indexed" in content_lower
        # Or at least mentions performance considerations
        has_performance = has_index_info or "performance" in content_lower

        assert has_performance, \
            "Database schema should mention indexes or performance considerations"


# =============================================================================
# Best Practices Tests
# =============================================================================

class TestDatabaseSchemaBestPractices:
    """Test that database schema follows documentation best practices"""

    @pytest.fixture
    def content(self):
        """Load database schema content"""
        project_root = Path(__file__).parent.parent
        schema_file = project_root / "docs" / "database-schema.md"
        return schema_file.read_text()

    def test_has_table_of_contents(self, content):
        """Test that database schema has table of contents"""
        # Assert
        content_lower = content.lower()
        has_toc = "table of contents" in content_lower or "## " in content
        assert has_toc, \
            "Database schema should have table of contents or clear organization"

    def test_uses_consistent_formatting(self, content):
        """Test that database schema uses consistent formatting"""
        # Assert
        has_headers = "## " in content
        has_code_blocks = "```" in content
        has_lists = "\n- " in content or "\n* " in content

        assert has_headers and (has_code_blocks or has_lists), \
            "Database schema should use consistent markdown formatting"

    def test_has_multiple_sections(self, content):
        """Test that database schema is well-organized with multiple sections"""
        # Assert
        # Count ## headers to ensure good organization
        section_count = content.count("## ")
        assert section_count >= 5, \
            f"Database schema should have multiple sections, got {section_count}"

    def test_documents_timestamps(self, content):
        """Test that database schema mentions timestamp fields"""
        # Assert
        content_lower = content.lower()
        has_timestamps = any(term in content_lower for term in [
            "created_at", "updated_at", "timestamp", "created", "modified"
        ])
        assert has_timestamps, \
            "Database schema should document timestamp fields"
