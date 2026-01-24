"""
Test suite for Preference Learning Service.

Components:
- Frequently used commands
- Preferred POI categories
- Music taste learning
- Climate preferences
- Route preferences
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestPreferenceLearningServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'preference_learning_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'preference_learning_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class PreferenceLearningService' in service_file_content


class TestFrequentlyUsedCommands:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'preference_learning_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_track_command_usage_method(self, service_file_content):
        assert 'def track_command_usage(' in service_file_content

    def test_has_get_frequent_commands_method(self, service_file_content):
        assert 'def get_frequent_commands(' in service_file_content

    def test_has_suggest_commands_method(self, service_file_content):
        assert 'def suggest_commands(' in service_file_content


class TestPreferredPOICategories:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'preference_learning_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_track_poi_visit_method(self, service_file_content):
        assert 'def track_poi_visit(' in service_file_content

    def test_has_get_preferred_poi_categories_method(self, service_file_content):
        assert 'def get_preferred_poi_categories(' in service_file_content


class TestMusicTasteLearning:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'preference_learning_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_track_music_preference_method(self, service_file_content):
        assert 'def track_music_preference(' in service_file_content

    def test_has_get_music_preferences_method(self, service_file_content):
        assert 'def get_music_preferences(' in service_file_content


class TestClimatePreferences:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'preference_learning_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_track_climate_setting_method(self, service_file_content):
        assert 'def track_climate_setting(' in service_file_content

    def test_has_get_climate_preferences_method(self, service_file_content):
        assert 'def get_climate_preferences(' in service_file_content


class TestRoutePreferences:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'preference_learning_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_track_route_choice_method(self, service_file_content):
        assert 'def track_route_choice(' in service_file_content

    def test_has_get_route_preferences_method(self, service_file_content):
        assert 'def get_route_preferences(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'preference_learning_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_learning_config_method(self, service_file_content):
        assert 'def get_learning_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'preference_learning_service.py'
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
            '..', 'backend', 'services', 'preference_learning_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class PreferenceLearningService' in service_file_content:
            idx = service_file_content.find('class PreferenceLearningService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
