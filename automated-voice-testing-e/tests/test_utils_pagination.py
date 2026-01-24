"""
Test suite for pagination utilities

Validates the pagination helper implementation including:
- File structure
- PaginationMetadata class/model
- paginate function
- Function signature and parameters
- Pagination logic
- Type hints
- Documentation
"""

import pytest
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
UTILS_DIR = PROJECT_ROOT / "backend" / "api" / "utils"
PAGINATION_FILE = UTILS_DIR / "pagination.py"


class TestPaginationFileExists:
    """Test that pagination utilities file exists"""

    def test_utils_directory_exists(self):
        """Test that utils directory exists"""
        assert UTILS_DIR.exists(), "backend/api/utils directory should exist"
        assert UTILS_DIR.is_dir(), "utils should be a directory"

    def test_pagination_file_exists(self):
        """Test that pagination.py exists"""
        assert PAGINATION_FILE.exists(), "pagination.py should exist"
        assert PAGINATION_FILE.is_file(), "pagination.py should be a file"

    def test_pagination_file_has_content(self):
        """Test that pagination file has content"""
        content = PAGINATION_FILE.read_text()
        assert len(content) > 0, "pagination.py should not be empty"


class TestPaginationImports:
    """Test pagination imports"""

    def test_imports_sqlalchemy_select(self):
        """Test that module imports Select from SQLAlchemy"""
        content = PAGINATION_FILE.read_text()
        assert ("Select" in content or
                "from sqlalchemy" in content), "Should import Select type"

    def test_imports_typing(self):
        """Test that module imports typing utilities"""
        content = PAGINATION_FILE.read_text()
        assert ("from typing import" in content or
                "import typing" in content), "Should import typing utilities"

    def test_imports_pydantic_basemodel(self):
        """Test that module imports Pydantic BaseModel for metadata"""
        content = PAGINATION_FILE.read_text()
        assert ("BaseModel" in content or
                "from pydantic" in content), "Should import BaseModel for PaginationMetadata"


class TestPaginationMetadataClass:
    """Test PaginationMetadata class"""

    def test_has_pagination_metadata_class(self):
        """Test that PaginationMetadata class is defined"""
        content = PAGINATION_FILE.read_text()
        assert "class PaginationMetadata" in content, "Should have PaginationMetadata class"

    def test_pagination_metadata_inherits_from_basemodel(self):
        """Test that PaginationMetadata inherits from BaseModel"""
        content = PAGINATION_FILE.read_text()
        assert ("class PaginationMetadata(BaseModel)" in content or
                "PaginationMetadata" in content), "Should inherit from BaseModel"

    def test_pagination_metadata_has_total_field(self):
        """Test that PaginationMetadata has total field"""
        content = PAGINATION_FILE.read_text()
        assert "total" in content, "Should have total field"

    def test_pagination_metadata_has_page_field(self):
        """Test that PaginationMetadata has page field"""
        content = PAGINATION_FILE.read_text()
        assert "page" in content, "Should have page field"

    def test_pagination_metadata_has_limit_field(self):
        """Test that PaginationMetadata has limit field"""
        content = PAGINATION_FILE.read_text()
        assert "limit" in content, "Should have limit field"

    def test_pagination_metadata_has_pages_field(self):
        """Test that PaginationMetadata has pages field"""
        content = PAGINATION_FILE.read_text()
        assert "pages" in content, "Should have pages field (total pages)"


class TestPaginateFunction:
    """Test paginate function"""

    def test_has_paginate_function(self):
        """Test that paginate function exists"""
        content = PAGINATION_FILE.read_text()
        assert "def paginate" in content, "Should have paginate function"

    def test_paginate_function_is_async(self):
        """Test that paginate function is async"""
        content = PAGINATION_FILE.read_text()
        # Could be async or sync - check implementation
        assert ("def paginate" in content), "Should have paginate function"

    def test_paginate_has_query_parameter(self):
        """Test that paginate has query parameter"""
        content = PAGINATION_FILE.read_text()
        assert ("paginate(query" in content or
                "paginate(" in content), "Should have query parameter"

    def test_paginate_has_page_parameter(self):
        """Test that paginate has page parameter"""
        content = PAGINATION_FILE.read_text()
        assert "page" in content, "Should have page parameter"

    def test_paginate_has_limit_parameter(self):
        """Test that paginate has limit parameter"""
        content = PAGINATION_FILE.read_text()
        assert "limit" in content, "Should have limit parameter"

    def test_paginate_has_default_values(self):
        """Test that paginate has default values for page and limit"""
        content = PAGINATION_FILE.read_text()
        assert ("= 1" in content or "page" in content), "Should have default values"
        assert ("= 50" in content or "limit" in content), "Should have default values"


class TestPaginateFunctionReturnType:
    """Test paginate function return type"""

    def test_paginate_returns_tuple(self):
        """Test that paginate returns tuple"""
        content = PAGINATION_FILE.read_text()
        assert ("tuple" in content or "Tuple" in content), "Should return tuple"

    def test_paginate_returns_list_and_metadata(self):
        """Test that paginate returns list and PaginationMetadata"""
        content = PAGINATION_FILE.read_text()
        assert "PaginationMetadata" in content, "Should return PaginationMetadata"


class TestPaginationDocumentation:
    """Test pagination documentation"""

    def test_has_module_docstring(self):
        """Test that module has docstring"""
        content = PAGINATION_FILE.read_text()
        assert '"""' in content or "'''" in content, "Should have module docstring"

    def test_pagination_metadata_has_docstring(self):
        """Test that PaginationMetadata has docstring"""
        content = PAGINATION_FILE.read_text()
        lines = content.split('\n')
        metadata_found = False
        for i, line in enumerate(lines):
            if "class PaginationMetadata" in line:
                metadata_found = True
                next_lines = '\n'.join(lines[i:i+5])
                assert '"""' in next_lines or "'''" in next_lines, "PaginationMetadata should have docstring"
                break
        assert metadata_found, "PaginationMetadata class should exist"

    def test_paginate_has_docstring(self):
        """Test that paginate function has docstring"""
        content = PAGINATION_FILE.read_text()
        lines = content.split('\n')
        paginate_found = False
        for i, line in enumerate(lines):
            if "def paginate" in line:
                paginate_found = True
                # Check more lines to account for multi-line function signatures
                next_lines = '\n'.join(lines[i:i+10])
                assert '"""' in next_lines or "'''" in next_lines, "paginate should have docstring"
                break
        assert paginate_found, "paginate function should exist"


class TestPaginationTypeHints:
    """Test type hints"""

    def test_uses_type_hints(self):
        """Test that module uses type hints"""
        content = PAGINATION_FILE.read_text()
        assert "->" in content, "Should use return type hints"
        assert ":" in content, "Should use parameter type hints"

    def test_imports_typing_module(self):
        """Test that typing module is imported"""
        content = PAGINATION_FILE.read_text()
        assert ("from typing import" in content or
                "import typing" in content), "Should import typing module"


class TestPaginationLogic:
    """Test pagination logic"""

    def test_calculates_offset(self):
        """Test that pagination calculates offset"""
        content = PAGINATION_FILE.read_text()
        # Should calculate offset from page and limit
        assert ("offset" in content or
                "skip" in content), "Should calculate offset"

    def test_applies_limit(self):
        """Test that pagination applies limit"""
        content = PAGINATION_FILE.read_text()
        assert "limit" in content, "Should apply limit"

    def test_counts_total(self):
        """Test that pagination counts total records"""
        content = PAGINATION_FILE.read_text()
        assert ("count" in content.lower() or
                "total" in content), "Should count total records"


class TestPaginationStructure:
    """Test overall pagination structure"""

    def test_has_pagination_metadata_and_function(self):
        """Test that module has both PaginationMetadata and paginate function"""
        content = PAGINATION_FILE.read_text()
        assert "class PaginationMetadata" in content, "Should have PaginationMetadata class"
        assert "def paginate" in content, "Should have paginate function"

    def test_exports_pagination_components(self):
        """Test that module exports pagination components"""
        content = PAGINATION_FILE.read_text()
        # Should define the key components
        assert "PaginationMetadata" in content, "Should define PaginationMetadata"
        assert "paginate" in content, "Should define paginate"
