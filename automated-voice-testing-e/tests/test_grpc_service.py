"""
Test suite for gRPC Service.

Components:
- Protobuf schema definition
- gRPC service implementation
- Bidirectional streaming for audio
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestGRPCServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'grpc_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'grpc_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class GRPCService' in service_file_content


class TestProtobufSchemas:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'grpc_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_define_service_method(self, service_file_content):
        assert 'def define_service(' in service_file_content

    def test_has_register_message_type_method(self, service_file_content):
        assert 'def register_message_type(' in service_file_content


class TestGRPCServices:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'grpc_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_register_handler_method(self, service_file_content):
        assert 'def register_handler(' in service_file_content

    def test_has_call_method(self, service_file_content):
        assert 'def call(' in service_file_content


class TestBidirectionalStreaming:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'grpc_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_create_stream_method(self, service_file_content):
        assert 'def create_stream(' in service_file_content

    def test_has_stream_audio_method(self, service_file_content):
        assert 'def stream_audio(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'grpc_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_grpc_config_method(self, service_file_content):
        assert 'def get_grpc_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'grpc_service.py'
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
            '..', 'backend', 'services', 'grpc_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class GRPCService' in service_file_content:
            idx = service_file_content.find('class GRPCService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
