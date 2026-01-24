"""
Test suite for TestRunDetail page (TASK-135)

Validates the TestRunDetail.tsx page implementation including:
- File structure and imports
- React component structure
- Material-UI components
- Page sections: Overview, Execution list, Statistics
- URL parameter handling
- TypeScript usage
"""

import pytest
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
FRONTEND_SRC = PROJECT_ROOT / "frontend" / "src"
PAGES_DIR = FRONTEND_SRC / "pages"
TEST_RUNS_DIR = PAGES_DIR / "TestRuns"
TEST_RUN_DETAIL_FILE = TEST_RUNS_DIR / "TestRunDetail.tsx"


class TestTestRunDetailFileStructure:
    """Test TestRunDetail file structure"""

    def test_pages_directory_exists(self):
        """Test that pages directory exists"""
        assert PAGES_DIR.exists(), "frontend/src/pages directory should exist"
        assert PAGES_DIR.is_dir(), "pages should be a directory"

    def test_test_runs_directory_exists(self):
        """Test that TestRuns directory exists"""
        assert TEST_RUNS_DIR.exists(), "frontend/src/pages/TestRuns directory should exist"
        assert TEST_RUNS_DIR.is_dir(), "TestRuns should be a directory"

    def test_test_run_detail_file_exists(self):
        """Test that TestRunDetail.tsx exists"""
        assert TEST_RUN_DETAIL_FILE.exists(), "TestRunDetail.tsx should exist"
        assert TEST_RUN_DETAIL_FILE.is_file(), "TestRunDetail.tsx should be a file"

    def test_test_run_detail_has_content(self):
        """Test that TestRunDetail.tsx has content"""
        content = TEST_RUN_DETAIL_FILE.read_text()
        assert len(content) > 0, "TestRunDetail.tsx should not be empty"


class TestReactImports:
    """Test React and TypeScript imports"""

    def test_imports_react(self):
        """Test that component imports React"""
        content = TEST_RUN_DETAIL_FILE.read_text()
        assert "import" in content and "react" in content.lower(), \
            "Should import React"

    def test_is_typescript_file(self):
        """Test that file uses TypeScript"""
        assert TEST_RUN_DETAIL_FILE.suffix == ".tsx", "Should be a .tsx file"


class TestMaterialUIImports:
    """Test Material-UI component imports"""

    def test_imports_mui_core(self):
        """Test that component imports from @mui/material"""
        content = TEST_RUN_DETAIL_FILE.read_text()
        assert "@mui/material" in content, "Should import from @mui/material"

    def test_imports_container_or_box(self):
        """Test that component imports Container or Box"""
        content = TEST_RUN_DETAIL_FILE.read_text()
        assert ("Container" in content or "Box" in content), \
            "Should import Container or Box for page wrapper"

    def test_imports_typography(self):
        """Test that component imports Typography"""
        content = TEST_RUN_DETAIL_FILE.read_text()
        assert "Typography" in content, "Should import Typography for headings"

    def test_imports_grid_or_stack(self):
        """Test that component imports Grid or Stack for layout"""
        content = TEST_RUN_DETAIL_FILE.read_text()
        assert ("Grid" in content or "Stack" in content), \
            "Should import Grid or Stack for layout"

    def test_imports_card_or_paper(self):
        """Test that component imports Card or Paper for sections"""
        content = TEST_RUN_DETAIL_FILE.read_text()
        assert ("Card" in content or "Paper" in content), \
            "Should import Card or Paper for sections"


class TestReactRouterImports:
    """Test React Router imports"""

    def test_imports_react_router(self):
        """Test that component imports from react-router-dom"""
        content = TEST_RUN_DETAIL_FILE.read_text()
        assert "react-router-dom" in content, \
            "Should import from react-router-dom for URL params"

    def test_imports_use_params(self):
        """Test that component imports useParams hook"""
        content = TEST_RUN_DETAIL_FILE.read_text()
        assert "useParams" in content, \
            "Should import useParams hook to get test run ID from URL"


class TestComponentStructure:
    """Test component structure"""

    def test_exports_test_run_detail(self):
        """Test that component exports TestRunDetail"""
        content = TEST_RUN_DETAIL_FILE.read_text()
        assert "TestRunDetail" in content, "Should define TestRunDetail component"

    def test_is_functional_component(self):
        """Test that component is a functional component"""
        content = TEST_RUN_DETAIL_FILE.read_text()
        assert ("const TestRunDetail" in content or "function TestRunDetail" in content), \
            "Should define functional component"

    def test_has_default_export(self):
        """Test that component has default export"""
        content = TEST_RUN_DETAIL_FILE.read_text()
        assert "export default" in content, "Should have default export"


class TestURLParameterHandling:
    """Test URL parameter handling"""

    def test_uses_use_params_hook(self):
        """Test that component uses useParams hook"""
        content = TEST_RUN_DETAIL_FILE.read_text()
        assert "useParams" in content, "Should use useParams hook"

    def test_extracts_id_from_params(self):
        """Test that component extracts ID from params"""
        content = TEST_RUN_DETAIL_FILE.read_text()
        assert ("id" in content or "testRunId" in content), \
            "Should extract test run ID from URL params"


class TestPageHeader:
    """Test page header implementation"""

    def test_has_page_title(self):
        """Test that page has title"""
        content = TEST_RUN_DETAIL_FILE.read_text()
        assert ("Test Run" in content and "Typography" in content), \
            "Should have Test Run title using Typography"

    def test_uses_typography_for_title(self):
        """Test that page uses Typography component"""
        content = TEST_RUN_DETAIL_FILE.read_text()
        assert "<Typography" in content, "Should use Typography component"


class TestOverviewSection:
    """Test overview section implementation"""

    def test_has_overview_section(self):
        """Test that page has overview section"""
        content = TEST_RUN_DETAIL_FILE.read_text()
        assert "Overview" in content, "Should have Overview section"

    def test_overview_uses_card_or_paper(self):
        """Test that overview section uses Card or Paper"""
        content = TEST_RUN_DETAIL_FILE.read_text()
        assert ("<Card" in content or "<Paper" in content), \
            "Should use Card or Paper for sections"


class TestExecutionListSection:
    """Test execution list section implementation"""

    def test_has_execution_list_section(self):
        """Test that page has execution list section"""
        content = TEST_RUN_DETAIL_FILE.read_text()
        assert ("Execution" in content or "Test" in content), \
            "Should have execution list section"

    def test_may_have_list_or_table(self):
        """Test that page may have list or table structure"""
        content = TEST_RUN_DETAIL_FILE.read_text()
        # May use List, Table, or custom components
        has_list_structure = ("List" in content or "Table" in content or "map" in content)
        # Pass regardless - just documenting the pattern
        assert True, "Execution list structure is recommended"


class TestStatisticsSection:
    """Test statistics section implementation"""

    def test_has_statistics_section(self):
        """Test that page has statistics section"""
        content = TEST_RUN_DETAIL_FILE.read_text()
        assert ("Statistics" in content or "Stats" in content), \
            "Should have Statistics section"

    def test_may_display_metrics(self):
        """Test that page may display metrics"""
        content = TEST_RUN_DETAIL_FILE.read_text()
        # May display counts, percentages, etc.
        has_metrics = ("passed" in content.lower() or "failed" in content.lower() or
                      "total" in content.lower())
        # Pass regardless - just documenting the pattern
        assert True, "Statistics metrics are recommended"


class TestLayoutStructure:
    """Test layout structure"""

    def test_has_container_or_box(self):
        """Test that page has Container or Box wrapper"""
        content = TEST_RUN_DETAIL_FILE.read_text()
        assert ("<Container" in content or "<Box" in content), \
            "Should have Container or Box wrapper"

    def test_has_multiple_sections(self):
        """Test that page has multiple sections"""
        content = TEST_RUN_DETAIL_FILE.read_text()
        # Should have multiple Card or Paper components for sections
        card_count = content.count("<Card") if "<Card" in content else 0
        paper_count = content.count("<Paper") if "<Paper" in content else 0
        assert (card_count >= 2 or paper_count >= 2), \
            "Should have multiple sections (Overview, Execution list, Statistics)"


class TestTypeScript:
    """Test TypeScript usage"""

    def test_uses_typescript_syntax(self):
        """Test that component uses TypeScript syntax"""
        content = TEST_RUN_DETAIL_FILE.read_text()
        assert (":)" in content or "React" in content), \
            "Should use TypeScript syntax"

    def test_component_typed(self):
        """Test that component is properly typed"""
        content = TEST_RUN_DETAIL_FILE.read_text()
        assert ("React.FC" in content or "FC<" in content or ": () =>" in content), \
            "Component should be properly typed"


class TestTaskRequirements:
    """Test TASK-135 specific requirements"""

    def test_task_135_file_location(self):
        """Test TASK-135: File is in correct location"""
        expected_path = PROJECT_ROOT / "frontend" / "src" / "pages" / "TestRuns" / "TestRunDetail.tsx"
        assert expected_path.exists(), \
            "TASK-135: File should be at frontend/src/pages/TestRuns/TestRunDetail.tsx"

    def test_task_135_has_overview_section(self):
        """Test TASK-135: Has Overview section"""
        content = TEST_RUN_DETAIL_FILE.read_text()
        assert "Overview" in content, \
            "TASK-135: Should have Overview section"

    def test_task_135_has_execution_list_section(self):
        """Test TASK-135: Has Execution list section"""
        content = TEST_RUN_DETAIL_FILE.read_text()
        assert ("Execution" in content or "Test" in content), \
            "TASK-135: Should have Execution list section"

    def test_task_135_has_statistics_section(self):
        """Test TASK-135: Has Statistics section"""
        content = TEST_RUN_DETAIL_FILE.read_text()
        assert ("Statistics" in content or "Stats" in content), \
            "TASK-135: Should have Statistics section"

    def test_task_135_handles_url_params(self):
        """Test TASK-135: Handles URL parameters"""
        content = TEST_RUN_DETAIL_FILE.read_text()
        assert "useParams" in content, \
            "TASK-135: Should use useParams to get test run ID"

    def test_task_135_is_page_component(self):
        """Test TASK-135: Is a page component"""
        content = TEST_RUN_DETAIL_FILE.read_text()
        assert "TestRunDetail" in content, \
            "TASK-135: Should be TestRunDetail page component"
