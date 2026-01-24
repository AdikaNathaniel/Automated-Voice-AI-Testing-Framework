"""
Test suite for Enhanced Noise Profile Library.

This service provides a comprehensive library of noise profiles for testing
ASR systems under various acoustic conditions. Each profile simulates
real-world noise environments.

Noise categories:
- Vehicle: Car cabin, road noise, engine
- Environmental: HVAC, office, home, crowd
- Industrial: Factory, machinery

Components:
- Noise profile definitions and parameters
- Noise generation and simulation
- Profile mixing and layering
- SNR-based noise application
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestNoiseProfileServiceExists:
    """Test that noise profile service exists"""

    @pytest.fixture
    def service_file_content(self):
        """Read the noise profile service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'noise_profile_library_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        """Test that noise_profile_library_service.py exists"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'noise_profile_library_service.py'
        )
        assert os.path.exists(service_file), (
            "noise_profile_library_service.py should exist"
        )

    def test_service_class_exists(self, service_file_content):
        """Test that NoiseProfileLibraryService class exists"""
        assert 'class NoiseProfileLibraryService' in service_file_content


class TestVehicleNoiseProfiles:
    """Test vehicle noise profiles"""

    @pytest.fixture
    def service_file_content(self):
        """Read the noise profile service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'noise_profile_library_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_car_cabin_noise(self, service_file_content):
        """Test car cabin noise profile exists"""
        assert 'car' in service_file_content.lower() or 'cabin' in service_file_content.lower()

    def test_has_road_noise(self, service_file_content):
        """Test road noise profile exists"""
        assert 'road' in service_file_content.lower()

    def test_has_highway_noise(self, service_file_content):
        """Test highway noise profile exists"""
        assert 'highway' in service_file_content.lower()


class TestEnvironmentalNoiseProfiles:
    """Test environmental noise profiles"""

    @pytest.fixture
    def service_file_content(self):
        """Read the noise profile service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'noise_profile_library_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_hvac_noise(self, service_file_content):
        """Test HVAC noise profile exists"""
        assert 'hvac' in service_file_content.lower()

    def test_has_crowd_noise(self, service_file_content):
        """Test crowd/babble noise profile exists"""
        assert 'crowd' in service_file_content.lower() or 'babble' in service_file_content.lower()

    def test_has_office_noise(self, service_file_content):
        """Test office environment noise exists"""
        assert 'office' in service_file_content.lower()

    def test_has_home_noise(self, service_file_content):
        """Test home environment noise exists"""
        assert 'home' in service_file_content.lower()


class TestIndustrialNoiseProfiles:
    """Test industrial noise profiles"""

    @pytest.fixture
    def service_file_content(self):
        """Read the noise profile service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'noise_profile_library_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_industrial_noise(self, service_file_content):
        """Test industrial/factory noise exists"""
        assert 'industrial' in service_file_content.lower() or 'factory' in service_file_content.lower()


class TestNoiseProfileRetrieval:
    """Test noise profile retrieval methods"""

    @pytest.fixture
    def service_file_content(self):
        """Read the noise profile service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'noise_profile_library_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_profile_method(self, service_file_content):
        """Test get_profile method exists"""
        assert 'def get_profile(' in service_file_content

    def test_get_profile_returns_dict(self, service_file_content):
        """Test get_profile returns Dict"""
        if 'def get_profile(' in service_file_content:
            idx = service_file_content.find('def get_profile(')
            method_sig = service_file_content[idx:idx+200]
            assert 'Dict' in method_sig

    def test_has_list_profiles_method(self, service_file_content):
        """Test list_profiles method exists"""
        assert 'def list_profiles(' in service_file_content

    def test_list_profiles_returns_list(self, service_file_content):
        """Test list_profiles returns List"""
        if 'def list_profiles(' in service_file_content:
            idx = service_file_content.find('def list_profiles(')
            method_sig = service_file_content[idx:idx+200]
            assert 'List' in method_sig


class TestNoiseGeneration:
    """Test noise generation functionality"""

    @pytest.fixture
    def service_file_content(self):
        """Read the noise profile service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'noise_profile_library_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_generate_noise_method(self, service_file_content):
        """Test generate_noise method exists"""
        assert 'def generate_noise(' in service_file_content

    def test_has_apply_noise_method(self, service_file_content):
        """Test apply_noise method exists"""
        assert 'def apply_noise(' in service_file_content


class TestNoiseProfileParameters:
    """Test noise profile parameter handling"""

    @pytest.fixture
    def service_file_content(self):
        """Read the noise profile service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'noise_profile_library_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_profile_parameters_method(self, service_file_content):
        """Test get_profile_parameters method exists"""
        assert 'def get_profile_parameters(' in service_file_content

    def test_parameters_returns_dict(self, service_file_content):
        """Test get_profile_parameters returns Dict"""
        if 'def get_profile_parameters(' in service_file_content:
            idx = service_file_content.find('def get_profile_parameters(')
            method_sig = service_file_content[idx:idx+250]
            assert 'Dict' in method_sig


class TestProfileCategories:
    """Test profile category handling"""

    @pytest.fixture
    def service_file_content(self):
        """Read the noise profile service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'noise_profile_library_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_categories_method(self, service_file_content):
        """Test get_categories method exists"""
        assert 'def get_categories(' in service_file_content

    def test_categories_returns_list(self, service_file_content):
        """Test get_categories returns List"""
        if 'def get_categories(' in service_file_content:
            idx = service_file_content.find('def get_categories(')
            method_sig = service_file_content[idx:idx+200]
            assert 'List' in method_sig


class TestNoiseMetrics:
    """Test comprehensive noise profile metrics"""

    @pytest.fixture
    def service_file_content(self):
        """Read the noise profile service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'noise_profile_library_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_profile_metrics_method(self, service_file_content):
        """Test get_profile_metrics method exists"""
        assert 'def get_profile_metrics(' in service_file_content

    def test_metrics_returns_dict(self, service_file_content):
        """Test get_profile_metrics returns Dict"""
        if 'def get_profile_metrics(' in service_file_content:
            idx = service_file_content.find('def get_profile_metrics(')
            method_sig = service_file_content[idx:idx+250]
            assert 'Dict' in method_sig


class TestTypeHints:
    """Test type hints for noise profile service"""

    @pytest.fixture
    def service_file_content(self):
        """Read the noise profile service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'noise_profile_library_service.py'
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
        """Read the noise profile service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'noise_profile_library_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        """Test module has docstring"""
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        """Test class has docstring"""
        if 'class NoiseProfileLibraryService' in service_file_content:
            idx = service_file_content.find('class NoiseProfileLibraryService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section

