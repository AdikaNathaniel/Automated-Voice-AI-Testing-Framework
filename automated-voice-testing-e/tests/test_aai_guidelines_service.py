"""
Test suite for Alliance for Automotive Innovation Guidelines Service.

Components:
- Statement of Principles for Driver Interactions
- Menu item limits (4-5 items per AAA Foundation research)
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestAAIGuidelinesServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'aai_guidelines_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'aai_guidelines_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class AAIGuidelinesService' in service_file_content


class TestDriverInteractionPrinciples:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'aai_guidelines_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_check_driver_interaction_compliance_method(self, service_file_content):
        assert 'def check_driver_interaction_compliance(' in service_file_content

    def test_has_validate_interaction_principles_method(self, service_file_content):
        assert 'def validate_interaction_principles(' in service_file_content


class TestMenuItemLimits:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'aai_guidelines_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_check_menu_item_limits_method(self, service_file_content):
        assert 'def check_menu_item_limits(' in service_file_content

    def test_has_validate_menu_structure_method(self, service_file_content):
        assert 'def validate_menu_structure(' in service_file_content


class TestCognitiveDistractionCategories:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'aai_guidelines_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_categorize_cognitive_distraction_method(self, service_file_content):
        assert 'def categorize_cognitive_distraction(' in service_file_content

    def test_has_assess_task_complexity_method(self, service_file_content):
        assert 'def assess_task_complexity(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'aai_guidelines_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_aai_guidelines_config_method(self, service_file_content):
        assert 'def get_aai_guidelines_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'aai_guidelines_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_imports_typing_modules(self, service_file_content):
        assert 'from typing import' in service_file_content

    def test_uses_dict_type_hint(self, service_file_content):
        assert 'Dict[' in service_file_content

    def test_uses_list_type_hint(self, service_file_content):
        assert 'List[' in service_file_content


class TestDocstrings:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'aai_guidelines_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class AAIGuidelinesService' in service_file_content:
            idx = service_file_content.find('class AAIGuidelinesService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
