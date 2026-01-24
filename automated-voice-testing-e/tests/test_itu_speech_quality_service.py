"""
Test suite for ITU Standards Speech Quality Service.

Components:
- ITU-T P.862 (PESQ) - Perceptual Evaluation of Speech Quality
- ITU-T P.863 (POLQA) - Perceptual Objective Listening Quality
- ITU-T G.168 - Digital network echo cancellers
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestITUSpeechQualityServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'itu_speech_quality_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'itu_speech_quality_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class ITUSpeechQualityService' in service_file_content


class TestPESQEvaluation:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'itu_speech_quality_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_evaluate_pesq_method(self, service_file_content):
        assert 'def evaluate_pesq(' in service_file_content

    def test_has_check_p862_compliance_method(self, service_file_content):
        assert 'def check_p862_compliance(' in service_file_content


class TestPOLQAEvaluation:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'itu_speech_quality_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_evaluate_polqa_method(self, service_file_content):
        assert 'def evaluate_polqa(' in service_file_content

    def test_has_check_p863_compliance_method(self, service_file_content):
        assert 'def check_p863_compliance(' in service_file_content


class TestEchoCancellation:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'itu_speech_quality_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_check_g168_compliance_method(self, service_file_content):
        assert 'def check_g168_compliance(' in service_file_content

    def test_has_measure_erle_method(self, service_file_content):
        assert 'def measure_erle(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'itu_speech_quality_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_itu_speech_quality_config_method(self, service_file_content):
        assert 'def get_itu_speech_quality_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'itu_speech_quality_service.py'
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
            '..', 'backend', 'services', 'itu_speech_quality_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class ITUSpeechQualityService' in service_file_content:
            idx = service_file_content.find('class ITUSpeechQualityService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
