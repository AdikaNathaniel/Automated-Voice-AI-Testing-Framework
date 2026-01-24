"""
Test Demo Data Loader

This module tests that the demo data loader creates comprehensive
demo test cases for showcasing the framework functionality.

Test Coverage:
    - Demo data loader module exists
    - Creates demo test suite
    - Creates 10 diverse test cases
    - Includes multiple language variations
    - Covers different test categories
    - Covers different test types
    - Test cases have valid structure
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import pytest
from uuid import UUID


# =============================================================================
# Module Existence Tests
# =============================================================================

class TestDemoDataLoaderModule:
    """Test that demo data loader module exists"""

    def test_demo_data_loader_module_exists(self):
        """Test that demo data loader module exists"""
        # Arrange
        project_root = Path(__file__).parent.parent
        loader_file = project_root / "backend" / "scripts" / "load_demo_data.py"

        # Act & Assert
        assert loader_file.exists(), "load_demo_data.py should exist in backend/scripts/"
        assert loader_file.is_file(), "load_demo_data.py should be a file"


# =============================================================================
# Demo Suite Tests
# =============================================================================

class TestDemoSuiteCreation:
    """Test that demo data loader creates demo suite"""

    def test_demo_suite_data_defined(self):
        """Test that demo suite data is defined"""
        # Arrange
        from scripts import load_demo_data

        # Act & Assert
        assert hasattr(load_demo_data, 'DEMO_SUITE_DATA'), \
            "load_demo_data should define DEMO_SUITE_DATA"

    def test_demo_suite_has_required_fields(self):
        """Test that demo suite has required fields"""
        # Arrange
        from scripts.load_demo_data import DEMO_SUITE_DATA

        # Act & Assert
        assert 'name' in DEMO_SUITE_DATA, "Demo suite should have name"
        assert 'description' in DEMO_SUITE_DATA, "Demo suite should have description"

    def test_demo_suite_name_is_descriptive(self):
        """Test that demo suite name is descriptive"""
        # Arrange
        from scripts.load_demo_data import DEMO_SUITE_DATA

        # Act
        name = DEMO_SUITE_DATA['name']

        # Assert
        assert len(name) > 5, "Demo suite name should be descriptive (>5 characters)"
        assert "Demo" in name or "demo" in name, \
            "Demo suite name should indicate it's a demo"


# =============================================================================
# Demo Test Cases Tests
# =============================================================================

class TestDemoTestCasesData:
    """Test that demo test cases data is properly defined"""

    def test_demo_test_cases_defined(self):
        """Test that demo test cases are defined"""
        # Arrange
        from scripts import load_demo_data

        # Act & Assert
        assert hasattr(load_demo_data, 'DEMO_TEST_CASES'), \
            "load_demo_data should define DEMO_TEST_CASES"

    def test_has_10_test_cases(self):
        """Test that there are 10 demo test cases"""
        # Arrange
        from scripts.load_demo_data import DEMO_TEST_CASES

        # Act
        count = len(DEMO_TEST_CASES)

        # Assert
        assert count == 10, f"Should have 10 demo test cases, got {count}"

    def test_test_cases_have_required_fields(self):
        """Test that all test cases have required fields"""
        # Arrange
        from scripts.load_demo_data import DEMO_TEST_CASES
        required_fields = {'name', 'test_type', 'category', 'scenario_definition'}

        # Act & Assert
        for i, test_case in enumerate(DEMO_TEST_CASES):
            for field in required_fields:
                assert field in test_case, \
                    f"Test case {i} should have '{field}' field"

    def test_test_cases_have_diverse_categories(self):
        """Test that test cases cover diverse categories"""
        # Arrange
        from scripts.load_demo_data import DEMO_TEST_CASES

        # Act
        categories = {tc.get('category') for tc in DEMO_TEST_CASES}

        # Assert
        assert len(categories) >= 5, \
            f"Test cases should cover at least 5 categories, got {len(categories)}"

    def test_test_cases_have_diverse_types(self):
        """Test that test cases cover diverse types"""
        # Arrange
        from scripts.load_demo_data import DEMO_TEST_CASES

        # Act
        types = {tc.get('test_type') for tc in DEMO_TEST_CASES}

        # Assert
        assert len(types) >= 2, \
            f"Test cases should cover at least 2 test types, got {len(types)}"

    def test_test_cases_have_language_variations(self):
        """Test that test cases include language variations"""
        # Arrange
        from scripts.load_demo_data import DEMO_TEST_CASES

        # Act
        cases_with_languages = [
            tc for tc in DEMO_TEST_CASES
            if 'languages' in tc and len(tc['languages']) > 0
        ]

        # Assert
        assert len(cases_with_languages) >= 5, \
            f"At least 5 test cases should have language variations, got {len(cases_with_languages)}"

    def test_language_variations_have_multiple_languages(self):
        """Test that language variations include multiple languages"""
        # Arrange
        from scripts.load_demo_data import DEMO_TEST_CASES

        # Act
        all_language_codes = set()
        for tc in DEMO_TEST_CASES:
            if 'languages' in tc:
                for lang in tc['languages']:
                    all_language_codes.add(lang.get('language_code'))

        # Assert
        assert len(all_language_codes) >= 3, \
            f"Demo cases should include at least 3 languages, got {len(all_language_codes)}"


# =============================================================================
# Demo Data Loader Function Tests
# =============================================================================

class TestLoadDemoDataFunction:
    """Test that load_demo_data function works correctly"""

    def test_load_demo_data_function_exists(self):
        """Test that load_demo_data function exists"""
        # Arrange
        from scripts import load_demo_data

        # Act & Assert
        assert hasattr(load_demo_data, 'load_demo_data'), \
            "load_demo_data module should have load_demo_data function"
        assert callable(load_demo_data.load_demo_data), \
            "load_demo_data should be a function"


# =============================================================================
# Data Quality Tests
# =============================================================================

class TestDemoDataQuality:
    """Test quality and completeness of demo data"""

    def test_test_case_names_are_unique(self):
        """Test that test case names are unique"""
        # Arrange
        from scripts.load_demo_data import DEMO_TEST_CASES

        # Act
        names = [tc['name'] for tc in DEMO_TEST_CASES]

        # Assert
        assert len(names) == len(set(names)), \
            "All test case names should be unique"

    def test_test_cases_have_descriptions(self):
        """Test that test cases have descriptions"""
        # Arrange
        from scripts.load_demo_data import DEMO_TEST_CASES

        # Act
        cases_with_descriptions = [
            tc for tc in DEMO_TEST_CASES
            if 'description' in tc and tc['description']
        ]

        # Assert
        assert len(cases_with_descriptions) >= 8, \
            f"At least 8 test cases should have descriptions, got {len(cases_with_descriptions)}"

    def test_test_cases_have_tags(self):
        """Test that test cases have tags"""
        # Arrange
        from scripts.load_demo_data import DEMO_TEST_CASES

        # Act
        cases_with_tags = [
            tc for tc in DEMO_TEST_CASES
            if 'tags' in tc and len(tc['tags']) > 0
        ]

        # Assert
        assert len(cases_with_tags) >= 8, \
            f"At least 8 test cases should have tags, got {len(cases_with_tags)}"

    def test_scenario_definitions_are_not_empty(self):
        """Test that scenario definitions are not empty"""
        # Arrange
        from scripts.load_demo_data import DEMO_TEST_CASES

        # Act & Assert
        for i, tc in enumerate(DEMO_TEST_CASES):
            scenario = tc.get('scenario_definition', {})
            assert len(scenario) > 0, \
                f"Test case {i} ({tc.get('name')}) should have non-empty scenario_definition"

    def test_language_variations_have_required_fields(self):
        """Test that language variations have required fields"""
        # Arrange
        from scripts.load_demo_data import DEMO_TEST_CASES

        # Act & Assert
        for tc in DEMO_TEST_CASES:
            if 'languages' in tc:
                for lang in tc['languages']:
                    assert 'language_code' in lang, \
                        f"Language variation in '{tc['name']}' should have language_code"
                    assert 'input_text' in lang, \
                        f"Language variation in '{tc['name']}' should have input_text"
