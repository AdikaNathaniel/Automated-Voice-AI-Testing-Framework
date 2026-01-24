"""
Test suite for Speaker Demographic Testing Service.

This service provides speaker demographic testing for voice AI systems.

Components:
- Age group variation (child, adult, elderly)
- Gender variation
- Non-native speaker testing
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestSpeakerDemographicServiceExists:
    """Test that speaker demographic service exists"""

    @pytest.fixture
    def service_file_content(self):
        """Read the speaker demographic service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'speaker_demographic_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        """Test that speaker_demographic_service.py exists"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'speaker_demographic_service.py'
        )
        assert os.path.exists(service_file), (
            "speaker_demographic_service.py should exist"
        )

    def test_service_class_exists(self, service_file_content):
        """Test that SpeakerDemographicService class exists"""
        assert 'class SpeakerDemographicService' in service_file_content


class TestAgeGroupVariation:
    """Test age group variation testing"""

    @pytest.fixture
    def service_file_content(self):
        """Read the speaker demographic service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'speaker_demographic_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_age_groups_method(self, service_file_content):
        """Test get_age_groups method exists"""
        assert 'def get_age_groups(' in service_file_content

    def test_has_create_age_test_suite_method(self, service_file_content):
        """Test create_age_test_suite method exists"""
        assert 'def create_age_test_suite(' in service_file_content

    def test_has_evaluate_age_group_method(self, service_file_content):
        """Test evaluate_age_group method exists"""
        assert 'def evaluate_age_group(' in service_file_content


class TestGenderVariation:
    """Test gender variation testing"""

    @pytest.fixture
    def service_file_content(self):
        """Read the speaker demographic service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'speaker_demographic_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_gender_categories_method(self, service_file_content):
        """Test get_gender_categories method exists"""
        assert 'def get_gender_categories(' in service_file_content

    def test_has_create_gender_test_suite_method(self, service_file_content):
        """Test create_gender_test_suite method exists"""
        assert 'def create_gender_test_suite(' in service_file_content

    def test_has_evaluate_gender_variation_method(self, service_file_content):
        """Test evaluate_gender_variation method exists"""
        assert 'def evaluate_gender_variation(' in service_file_content


class TestNonNativeSpeaker:
    """Test non-native speaker testing"""

    @pytest.fixture
    def service_file_content(self):
        """Read the speaker demographic service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'speaker_demographic_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_proficiency_levels_method(self, service_file_content):
        """Test get_proficiency_levels method exists"""
        assert 'def get_proficiency_levels(' in service_file_content

    def test_has_create_non_native_test_suite_method(self, service_file_content):
        """Test create_non_native_test_suite method exists"""
        assert 'def create_non_native_test_suite(' in service_file_content

    def test_has_evaluate_non_native_method(self, service_file_content):
        """Test evaluate_non_native method exists"""
        assert 'def evaluate_non_native(' in service_file_content


class TestDemographicConfiguration:
    """Test demographic configuration"""

    @pytest.fixture
    def service_file_content(self):
        """Read the speaker demographic service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'speaker_demographic_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_demographic_config_method(self, service_file_content):
        """Test get_demographic_config method exists"""
        assert 'def get_demographic_config(' in service_file_content

    def test_has_get_demographic_summary_method(self, service_file_content):
        """Test get_demographic_summary method exists"""
        assert 'def get_demographic_summary(' in service_file_content

    def test_has_compare_demographics_method(self, service_file_content):
        """Test compare_demographics method exists"""
        assert 'def compare_demographics(' in service_file_content


class TestTypeHints:
    """Test type hints for speaker demographic service"""

    @pytest.fixture
    def service_file_content(self):
        """Read the speaker demographic service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'speaker_demographic_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_imports_typing_modules(self, service_file_content):
        """Test typing modules are imported"""
        assert 'from typing import' in service_file_content

    def test_uses_dict_type_hint(self, service_file_content):
        """Test Dict type hint is used"""
        assert 'Dict[' in service_file_content

    def test_uses_list_type_hint(self, service_file_content):
        """Test List type hint is used"""
        assert 'List[' in service_file_content


class TestDocstrings:
    """Test comprehensive documentation"""

    @pytest.fixture
    def service_file_content(self):
        """Read the speaker demographic service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'speaker_demographic_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        """Test module has docstring"""
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        """Test class has docstring"""
        if 'class SpeakerDemographicService' in service_file_content:
            idx = service_file_content.find('class SpeakerDemographicService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section

