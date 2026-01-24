"""
Test suite for System Design Documentation Service.

Components:
- Component diagrams
- Data flow diagrams
- Sequence diagrams
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestSystemDesignDocsServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'system_design_docs_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'system_design_docs_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class SystemDesignDocsService' in service_file_content


class TestComponentDiagrams:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'system_design_docs_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_create_component_diagram_method(self, service_file_content):
        assert 'def create_component_diagram(' in service_file_content

    def test_has_get_component_diagram_method(self, service_file_content):
        assert 'def get_component_diagram(' in service_file_content

    def test_has_list_components_method(self, service_file_content):
        assert 'def list_components(' in service_file_content

    def test_has_add_component_method(self, service_file_content):
        assert 'def add_component(' in service_file_content


class TestDataFlowDiagrams:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'system_design_docs_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_create_data_flow_method(self, service_file_content):
        assert 'def create_data_flow(' in service_file_content

    def test_has_get_data_flow_method(self, service_file_content):
        assert 'def get_data_flow(' in service_file_content

    def test_has_add_data_node_method(self, service_file_content):
        assert 'def add_data_node(' in service_file_content

    def test_has_connect_nodes_method(self, service_file_content):
        assert 'def connect_nodes(' in service_file_content


class TestSequenceDiagrams:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'system_design_docs_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_create_sequence_diagram_method(self, service_file_content):
        assert 'def create_sequence_diagram(' in service_file_content

    def test_has_get_sequence_diagram_method(self, service_file_content):
        assert 'def get_sequence_diagram(' in service_file_content

    def test_has_add_actor_method(self, service_file_content):
        assert 'def add_actor(' in service_file_content

    def test_has_add_message_method(self, service_file_content):
        assert 'def add_message(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'system_design_docs_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_design_docs_config_method(self, service_file_content):
        assert 'def get_design_docs_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'system_design_docs_service.py'
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
            '..', 'backend', 'services', 'system_design_docs_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class SystemDesignDocsService' in service_file_content:
            idx = service_file_content.find('class SystemDesignDocsService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
