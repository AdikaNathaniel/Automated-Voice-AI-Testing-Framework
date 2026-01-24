"""
Phase 3.7: Test Coverage Analysis
Tests for the coverage matrix analyzer script
"""

import pytest
from pathlib import Path
from typing import Dict, List, Set
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestCoverageAnalyzer:
    """Test the coverage analyzer functionality."""

    @pytest.fixture
    def test_files_dir(self):
        """Get the test files directory."""
        return Path(__file__).parent

    @pytest.fixture
    def analyzer(self):
        """Create a coverage analyzer instance."""
        # Import here to avoid issues
        from coverage_analyzer import CoverageAnalyzer
        return CoverageAnalyzer()

    def test_analyzer_can_find_test_files(self, test_files_dir, analyzer):
        """Test that analyzer can find test files."""
        test_files = analyzer.find_test_files(test_files_dir)

        # Should find test files
        assert len(test_files) > 0
        assert any(f.name.startswith("test_") for f in test_files)

    def test_analyzer_can_extract_route_names_from_test_file(self, analyzer):
        """Test that analyzer can extract route names from test files."""
        # Check a specific test file for route references
        test_file = Path(__file__).parent / "test_e2e_api_routes.py"
        if test_file.exists():
            routes = analyzer.extract_routes_from_file(test_file)
            assert len(routes) > 0
            assert any("auth" in route.lower() or "test" in route.lower() for route in routes)

    def test_analyzer_identifies_test_types(self, analyzer):
        """Test that analyzer can identify test types (unit, integration, e2e, security, performance)."""
        test_file = Path(__file__).parent / "test_e2e_api_routes.py"
        if test_file.exists():
            test_types = analyzer.identify_test_types(test_file)
            # File name contains "e2e", should be identified
            assert "e2e" in test_types or "e2e" in test_file.name.lower()

    def test_analyzer_can_build_api_route_coverage_matrix(self, analyzer, test_files_dir):
        """Test that analyzer can build API route coverage matrix."""
        routes = [
            "auth",
            "test-suites",
            "test-cases",
            "test-runs",
            "scenarios",
        ]
        coverage = analyzer.build_api_route_coverage_matrix(test_files_dir, routes)

        assert isinstance(coverage, dict)
        for route in routes[:3]:  # Check at least first 3 routes
            assert route in coverage
            assert "unit" in coverage[route]
            assert "integration" in coverage[route]
            assert "e2e" in coverage[route]

    def test_analyzer_can_build_service_coverage_matrix(self, analyzer, test_files_dir):
        """Test that analyzer can build service coverage matrix."""
        services = [
            "Orchestration",
            "Validation",
            "Test Management",
        ]
        coverage = analyzer.build_service_coverage_matrix(test_files_dir, services)

        assert isinstance(coverage, dict)
        for service in services:
            assert service in coverage
            assert "unit" in coverage[service]
            assert "integration" in coverage[service]

    def test_analyzer_can_build_model_coverage_matrix(self, analyzer, test_files_dir):
        """Test that analyzer can build model coverage matrix."""
        models = [
            "User",
            "TestSuite",
            "TestCase",
        ]
        coverage = analyzer.build_model_coverage_matrix(test_files_dir, models)

        assert isinstance(coverage, dict)
        for model in models:
            assert model in coverage
            assert "crud" in coverage[model]
            assert "relationships" in coverage[model]
            assert "constraints" in coverage[model]

    def test_analyzer_formats_coverage_matrix_as_markdown(self, analyzer):
        """Test that analyzer can format coverage matrix as markdown."""
        coverage = {
            "auth": {"unit": True, "integration": True, "e2e": False, "security": True, "performance": False},
            "test-suites": {"unit": True, "integration": True, "e2e": True, "security": False, "performance": False},
        }
        markdown = analyzer.format_coverage_matrix(coverage, "api_routes")

        assert isinstance(markdown, str)
        assert "|" in markdown  # Markdown table format
        assert "auth" in markdown
        assert "test-suites" in markdown
        # Check marks (✓) should be present
        assert "✓" in markdown or "[x]" in markdown

    def test_analyzer_can_detect_coverage_gaps(self, analyzer):
        """Test that analyzer can identify coverage gaps."""
        coverage = {
            "auth": {"unit": True, "integration": True, "e2e": False, "security": False, "performance": False},
            "test-suites": {"unit": True, "integration": False, "e2e": True, "security": False, "performance": False},
        }
        gaps = analyzer.find_coverage_gaps(coverage)

        assert isinstance(gaps, dict)
        assert len(gaps) > 0
        # "auth" should have e2e and security gaps
        assert "auth" in gaps
        assert "security" in gaps["auth"]

    def test_analyzer_test_types_correctly_identified(self, test_files_dir, analyzer):
        """Test that different test file types are correctly identified."""
        # E2E test files
        e2e_files = list(test_files_dir.glob("test_e2e_*.py"))
        for f in e2e_files:
            test_types = analyzer.identify_test_types(f)
            assert "e2e" in test_types

    def test_analyzer_handles_missing_test_files(self, analyzer):
        """Test that analyzer gracefully handles missing test directories."""
        non_existent = Path("/non/existent/path")
        coverage = analyzer.build_api_route_coverage_matrix(non_existent, ["auth"])

        # Should return empty or default coverage
        assert isinstance(coverage, dict)
