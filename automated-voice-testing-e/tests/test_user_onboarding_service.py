"""
Test suite for User Onboarding Service.

Components:
- Interactive tutorial
- Sample data population
- Quick start guides
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestUserOnboardingServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'user_onboarding_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'user_onboarding_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class UserOnboardingService' in service_file_content


class TestInteractiveTutorial:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'user_onboarding_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_start_tutorial_method(self, service_file_content):
        assert 'def start_tutorial(' in service_file_content

    def test_has_get_tutorial_step_method(self, service_file_content):
        assert 'def get_tutorial_step(' in service_file_content

    def test_has_complete_tutorial_step_method(self, service_file_content):
        assert 'def complete_tutorial_step(' in service_file_content

    def test_has_skip_tutorial_method(self, service_file_content):
        assert 'def skip_tutorial(' in service_file_content


class TestSampleDataPopulation:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'user_onboarding_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_populate_sample_data_method(self, service_file_content):
        assert 'def populate_sample_data(' in service_file_content

    def test_has_get_sample_datasets_method(self, service_file_content):
        assert 'def get_sample_datasets(' in service_file_content

    def test_has_clear_sample_data_method(self, service_file_content):
        assert 'def clear_sample_data(' in service_file_content


class TestQuickStartGuides:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'user_onboarding_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_list_guides_method(self, service_file_content):
        assert 'def list_guides(' in service_file_content

    def test_has_get_guide_method(self, service_file_content):
        assert 'def get_guide(' in service_file_content

    def test_has_track_guide_progress_method(self, service_file_content):
        assert 'def track_guide_progress(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'user_onboarding_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_onboarding_config_method(self, service_file_content):
        assert 'def get_onboarding_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'user_onboarding_service.py'
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
            '..', 'backend', 'services', 'user_onboarding_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class UserOnboardingService' in service_file_content:
            idx = service_file_content.find('class UserOnboardingService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
