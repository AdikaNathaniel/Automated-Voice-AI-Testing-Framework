"""
Test suite for Visualization Service.

Components:
- Confusion matrix heatmaps
- ROC curves
- Precision-recall curves
- Calibration plots
- Error distribution charts
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestVisualizationServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'visualization_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'visualization_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class VisualizationService' in service_file_content


class TestConfusionMatrix:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'visualization_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_generate_confusion_matrix_method(self, service_file_content):
        assert 'def generate_confusion_matrix(' in service_file_content

    def test_has_get_heatmap_data_method(self, service_file_content):
        assert 'def get_heatmap_data(' in service_file_content


class TestROCCurves:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'visualization_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_generate_roc_curve_method(self, service_file_content):
        assert 'def generate_roc_curve(' in service_file_content

    def test_has_calculate_auc_method(self, service_file_content):
        assert 'def calculate_auc(' in service_file_content


class TestPrecisionRecallCurves:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'visualization_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_generate_precision_recall_curve_method(self, service_file_content):
        assert 'def generate_precision_recall_curve(' in service_file_content


class TestCalibrationPlots:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'visualization_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_generate_calibration_plot_method(self, service_file_content):
        assert 'def generate_calibration_plot(' in service_file_content


class TestErrorDistribution:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'visualization_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_generate_error_distribution_method(self, service_file_content):
        assert 'def generate_error_distribution(' in service_file_content

    def test_has_get_distribution_stats_method(self, service_file_content):
        assert 'def get_distribution_stats(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'visualization_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_visualization_config_method(self, service_file_content):
        assert 'def get_visualization_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'visualization_service.py'
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
            '..', 'backend', 'services', 'visualization_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class VisualizationService' in service_file_content:
            idx = service_file_content.find('class VisualizationService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
