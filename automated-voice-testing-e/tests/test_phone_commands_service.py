"""
Test suite for Phone Commands Service.

Components:
- Call management
- Text messaging
- Contact lookup
- Do Not Disturb
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestPhoneCommandsServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'phone_commands_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'phone_commands_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class PhoneCommandsService' in service_file_content


class TestCallManagement:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'phone_commands_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_make_call_method(self, service_file_content):
        assert 'def make_call(' in service_file_content

    def test_has_control_call_method(self, service_file_content):
        assert 'def control_call(' in service_file_content

    def test_has_get_call_history_method(self, service_file_content):
        assert 'def get_call_history(' in service_file_content


class TestTextMessaging:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'phone_commands_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_send_message_method(self, service_file_content):
        assert 'def send_message(' in service_file_content

    def test_has_read_message_method(self, service_file_content):
        assert 'def read_message(' in service_file_content

    def test_has_reply_message_method(self, service_file_content):
        assert 'def reply_message(' in service_file_content


class TestContactAndDND:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'phone_commands_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_lookup_contact_method(self, service_file_content):
        assert 'def lookup_contact(' in service_file_content

    def test_has_toggle_dnd_method(self, service_file_content):
        assert 'def toggle_dnd(' in service_file_content

    def test_has_play_voicemail_method(self, service_file_content):
        assert 'def play_voicemail(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'phone_commands_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_phone_commands_config_method(self, service_file_content):
        assert 'def get_phone_commands_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'phone_commands_service.py'
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
            '..', 'backend', 'services', 'phone_commands_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class PhoneCommandsService' in service_file_content:
            idx = service_file_content.find('class PhoneCommandsService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
