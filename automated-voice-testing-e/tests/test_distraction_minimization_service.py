"""
Test suite for Distraction Minimization Testing Service.

Components:
- Task completion time measurement
- Number of turns required
- Cognitive load assessment
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestDistractionMinimizationServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'distraction_minimization_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'distraction_minimization_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class DistractionMinimizationService' in service_file_content


class TestTaskCompletionTime:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'distraction_minimization_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_measure_task_completion_time_method(self, service_file_content):
        assert 'def measure_task_completion_time(' in service_file_content

    def test_has_get_task_time_thresholds_method(self, service_file_content):
        assert 'def get_task_time_thresholds(' in service_file_content

    def test_has_validate_completion_time_method(self, service_file_content):
        assert 'def validate_completion_time(' in service_file_content

    def test_has_track_task_duration_method(self, service_file_content):
        assert 'def track_task_duration(' in service_file_content


class TestInteractionTurns:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'distraction_minimization_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_count_interaction_turns_method(self, service_file_content):
        assert 'def count_interaction_turns(' in service_file_content

    def test_has_validate_turn_count_method(self, service_file_content):
        assert 'def validate_turn_count(' in service_file_content

    def test_has_get_optimal_turns_method(self, service_file_content):
        assert 'def get_optimal_turns(' in service_file_content

    def test_has_analyze_turn_efficiency_method(self, service_file_content):
        assert 'def analyze_turn_efficiency(' in service_file_content


class TestCognitiveLoad:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'distraction_minimization_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_assess_cognitive_load_method(self, service_file_content):
        assert 'def assess_cognitive_load(' in service_file_content

    def test_has_calculate_load_score_method(self, service_file_content):
        assert 'def calculate_load_score(' in service_file_content

    def test_has_get_load_thresholds_method(self, service_file_content):
        assert 'def get_load_thresholds(' in service_file_content

    def test_has_validate_cognitive_load_method(self, service_file_content):
        assert 'def validate_cognitive_load(' in service_file_content


class TestDistractionMetrics:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'distraction_minimization_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_calculate_distraction_score_method(self, service_file_content):
        assert 'def calculate_distraction_score(' in service_file_content

    def test_has_get_distraction_factors_method(self, service_file_content):
        assert 'def get_distraction_factors(' in service_file_content

    def test_has_generate_minimization_report_method(self, service_file_content):
        assert 'def generate_minimization_report(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'distraction_minimization_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_distraction_minimization_config_method(self, service_file_content):
        assert 'def get_distraction_minimization_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'distraction_minimization_service.py'
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
            '..', 'backend', 'services', 'distraction_minimization_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class DistractionMinimizationService' in service_file_content:
            idx = service_file_content.find('class DistractionMinimizationService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
