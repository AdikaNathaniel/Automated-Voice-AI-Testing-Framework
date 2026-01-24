"""
Test suite for Media Commands Service.

Components:
- Music playback
- Playlist management
- Radio tuning
- Volume control
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestMediaCommandsServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'media_commands_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'media_commands_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class MediaCommandsService' in service_file_content


class TestMusicPlayback:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'media_commands_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_play_music_method(self, service_file_content):
        assert 'def play_music(' in service_file_content

    def test_has_control_playback_method(self, service_file_content):
        assert 'def control_playback(' in service_file_content

    def test_has_search_media_method(self, service_file_content):
        assert 'def search_media(' in service_file_content


class TestPlaylistManagement:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'media_commands_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_manage_playlist_method(self, service_file_content):
        assert 'def manage_playlist(' in service_file_content

    def test_has_get_now_playing_method(self, service_file_content):
        assert 'def get_now_playing(' in service_file_content

    def test_has_manage_favorites_method(self, service_file_content):
        assert 'def manage_favorites(' in service_file_content


class TestRadioAndVolume:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'media_commands_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_tune_radio_method(self, service_file_content):
        assert 'def tune_radio(' in service_file_content

    def test_has_control_volume_method(self, service_file_content):
        assert 'def control_volume(' in service_file_content

    def test_has_switch_audio_source_method(self, service_file_content):
        assert 'def switch_audio_source(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'media_commands_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_media_commands_config_method(self, service_file_content):
        assert 'def get_media_commands_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'media_commands_service.py'
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
            '..', 'backend', 'services', 'media_commands_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class MediaCommandsService' in service_file_content:
            idx = service_file_content.find('class MediaCommandsService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
