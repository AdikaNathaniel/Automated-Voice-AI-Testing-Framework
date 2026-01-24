"""
Test suite for Audio Augmentation Service.

Components:
- Speed perturbation (0.9x - 1.1x)
- Pitch shifting
- Tempo modification
- SpecAugment implementation
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestAudioAugmentationServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'audio_augmentation_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'audio_augmentation_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class AudioAugmentationService' in service_file_content


class TestSpeedPerturbation:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'audio_augmentation_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_apply_speed_perturbation_method(self, service_file_content):
        assert 'def apply_speed_perturbation(' in service_file_content

    def test_has_get_speed_range_method(self, service_file_content):
        assert 'def get_speed_range(' in service_file_content


class TestPitchShifting:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'audio_augmentation_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_apply_pitch_shift_method(self, service_file_content):
        assert 'def apply_pitch_shift(' in service_file_content

    def test_has_get_pitch_range_method(self, service_file_content):
        assert 'def get_pitch_range(' in service_file_content


class TestTempoModification:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'audio_augmentation_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_apply_tempo_change_method(self, service_file_content):
        assert 'def apply_tempo_change(' in service_file_content

    def test_has_get_tempo_range_method(self, service_file_content):
        assert 'def get_tempo_range(' in service_file_content


class TestSpecAugment:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'audio_augmentation_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_apply_spec_augment_method(self, service_file_content):
        assert 'def apply_spec_augment(' in service_file_content

    def test_has_apply_time_masking_method(self, service_file_content):
        assert 'def apply_time_masking(' in service_file_content

    def test_has_apply_frequency_masking_method(self, service_file_content):
        assert 'def apply_frequency_masking(' in service_file_content


class TestAugmentationPipeline:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'audio_augmentation_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_create_augmentation_pipeline_method(self, service_file_content):
        assert 'def create_augmentation_pipeline(' in service_file_content

    def test_has_apply_pipeline_method(self, service_file_content):
        assert 'def apply_pipeline(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'audio_augmentation_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_augmentation_config_method(self, service_file_content):
        assert 'def get_augmentation_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'audio_augmentation_service.py'
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
            '..', 'backend', 'services', 'audio_augmentation_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class AudioAugmentationService' in service_file_content:
            idx = service_file_content.find('class AudioAugmentationService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
