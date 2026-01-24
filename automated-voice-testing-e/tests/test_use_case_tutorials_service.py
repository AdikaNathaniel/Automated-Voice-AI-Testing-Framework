"""
Test suite for Use Case Tutorials Service.

Components:
- End-to-end workflow tutorials
- Integration guides
- Best practices guides
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestUseCaseTutorialsServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'use_case_tutorials_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'use_case_tutorials_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class UseCaseTutorialsService' in service_file_content


class TestEndToEndWorkflows:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'use_case_tutorials_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_list_workflows_method(self, service_file_content):
        assert 'def list_workflows(' in service_file_content

    def test_has_get_workflow_method(self, service_file_content):
        assert 'def get_workflow(' in service_file_content

    def test_has_track_workflow_progress_method(self, service_file_content):
        assert 'def track_workflow_progress(' in service_file_content


class TestIntegrationGuides:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'use_case_tutorials_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_list_integrations_method(self, service_file_content):
        assert 'def list_integrations(' in service_file_content

    def test_has_get_integration_guide_method(self, service_file_content):
        assert 'def get_integration_guide(' in service_file_content


class TestBestPracticesGuides:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'use_case_tutorials_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_list_best_practices_method(self, service_file_content):
        assert 'def list_best_practices(' in service_file_content

    def test_has_get_best_practice_method(self, service_file_content):
        assert 'def get_best_practice(' in service_file_content

    def test_has_search_tutorials_method(self, service_file_content):
        assert 'def search_tutorials(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'use_case_tutorials_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_tutorials_config_method(self, service_file_content):
        assert 'def get_tutorials_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'use_case_tutorials_service.py'
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
            '..', 'backend', 'services', 'use_case_tutorials_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class UseCaseTutorialsService' in service_file_content:
            idx = service_file_content.find('class UseCaseTutorialsService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
