"""
Test suite for Weather-adaptive Responses Service.

Components:
- Driving condition warnings
- Destination weather prep
- Automatic climate suggestions
- Route adjustments for weather
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestWeatherAdaptiveServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'weather_adaptive_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'weather_adaptive_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class WeatherAdaptiveService' in service_file_content


class TestDrivingConditions:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'weather_adaptive_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_driving_condition_warnings_method(self, service_file_content):
        assert 'def get_driving_condition_warnings(' in service_file_content

    def test_has_assess_road_conditions_method(self, service_file_content):
        assert 'def assess_road_conditions(' in service_file_content


class TestDestinationWeather:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'weather_adaptive_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_destination_weather_method(self, service_file_content):
        assert 'def get_destination_weather(' in service_file_content

    def test_has_get_weather_prep_suggestions_method(self, service_file_content):
        assert 'def get_weather_prep_suggestions(' in service_file_content


class TestClimateSuggestions:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'weather_adaptive_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_climate_suggestions_method(self, service_file_content):
        assert 'def get_climate_suggestions(' in service_file_content

    def test_has_auto_adjust_climate_method(self, service_file_content):
        assert 'def auto_adjust_climate(' in service_file_content


class TestRouteAdjustments:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'weather_adaptive_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_suggest_route_adjustment_method(self, service_file_content):
        assert 'def suggest_route_adjustment(' in service_file_content

    def test_has_get_weather_safe_route_method(self, service_file_content):
        assert 'def get_weather_safe_route(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'weather_adaptive_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_weather_adaptive_config_method(self, service_file_content):
        assert 'def get_weather_adaptive_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'weather_adaptive_service.py'
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
            '..', 'backend', 'services', 'weather_adaptive_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class WeatherAdaptiveService' in service_file_content:
            idx = service_file_content.find('class WeatherAdaptiveService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
