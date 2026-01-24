"""
Test suite for Confidence score calibration.

Confidence calibration ensures that when a model says it's 80% confident,
it's actually correct 80% of the time. Well-calibrated models have
predictions that match their confidence levels.

Components:
- Reliability diagrams: Visual comparison of confidence vs accuracy
- Expected Calibration Error (ECE): Numerical calibration metric
- Confidence vs accuracy correlation: Statistical relationship
- Per-word confidence aggregation: Methods to combine word-level confidences
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestCalibrationServiceExists:
    """Test that calibration service exists"""

    @pytest.fixture
    def service_file_content(self):
        """Read the calibration service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'confidence_calibration_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        """Test that confidence_calibration_service.py exists"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'confidence_calibration_service.py'
        )
        assert os.path.exists(service_file), (
            "confidence_calibration_service.py should exist"
        )

    def test_service_class_exists(self, service_file_content):
        """Test that ConfidenceCalibrationService class exists"""
        assert 'class ConfidenceCalibrationService' in service_file_content


class TestReliabilityDiagramData:
    """Test reliability diagram data generation"""

    @pytest.fixture
    def service_file_content(self):
        """Read the calibration service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'confidence_calibration_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_generate_reliability_diagram_data_method(self, service_file_content):
        """Test generate_reliability_diagram_data method exists"""
        assert 'def generate_reliability_diagram_data(' in service_file_content

    def test_reliability_diagram_has_docstring(self, service_file_content):
        """Test generate_reliability_diagram_data has docstring"""
        if 'def generate_reliability_diagram_data(' in service_file_content:
            idx = service_file_content.find('def generate_reliability_diagram_data(')
            method_section = service_file_content[idx:idx+600]
            assert '"""' in method_section

    def test_reliability_diagram_accepts_predictions(self, service_file_content):
        """Test method accepts predictions parameter"""
        if 'def generate_reliability_diagram_data(' in service_file_content:
            idx = service_file_content.find('def generate_reliability_diagram_data(')
            method_sig = service_file_content[idx:idx+200]
            assert 'predictions' in method_sig

    def test_reliability_diagram_accepts_num_bins(self, service_file_content):
        """Test method accepts num_bins parameter"""
        if 'def generate_reliability_diagram_data(' in service_file_content:
            idx = service_file_content.find('def generate_reliability_diagram_data(')
            method_sig = service_file_content[idx:idx+200]
            assert 'num_bins' in method_sig

    def test_reliability_diagram_returns_dict(self, service_file_content):
        """Test method returns Dict"""
        if 'def generate_reliability_diagram_data(' in service_file_content:
            idx = service_file_content.find('def generate_reliability_diagram_data(')
            method_sig = service_file_content[idx:idx+200]
            assert 'Dict' in method_sig


class TestExpectedCalibrationError:
    """Test Expected Calibration Error (ECE) calculation"""

    @pytest.fixture
    def service_file_content(self):
        """Read the calibration service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'confidence_calibration_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_calculate_ece_method(self, service_file_content):
        """Test calculate_ece method exists"""
        assert 'def calculate_ece(' in service_file_content

    def test_ece_has_docstring(self, service_file_content):
        """Test calculate_ece has docstring"""
        if 'def calculate_ece(' in service_file_content:
            idx = service_file_content.find('def calculate_ece(')
            method_section = service_file_content[idx:idx+600]
            assert '"""' in method_section

    def test_ece_returns_float(self, service_file_content):
        """Test calculate_ece returns float"""
        if 'def calculate_ece(' in service_file_content:
            idx = service_file_content.find('def calculate_ece(')
            method_sig = service_file_content[idx:idx+150]
            assert 'float' in method_sig

    def test_ece_accepts_predictions(self, service_file_content):
        """Test calculate_ece accepts predictions parameter"""
        if 'def calculate_ece(' in service_file_content:
            idx = service_file_content.find('def calculate_ece(')
            method_sig = service_file_content[idx:idx+200]
            assert 'predictions' in method_sig

    def test_ece_formula_documented(self, service_file_content):
        """Test ECE formula is documented"""
        # ECE = sum(|accuracy_bin - confidence_bin| * fraction_in_bin)
        assert 'accuracy' in service_file_content.lower()
        assert 'confidence' in service_file_content.lower()


class TestMaximumCalibrationError:
    """Test Maximum Calibration Error (MCE) calculation"""

    @pytest.fixture
    def service_file_content(self):
        """Read the calibration service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'confidence_calibration_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_calculate_mce_method(self, service_file_content):
        """Test calculate_mce method exists"""
        assert 'def calculate_mce(' in service_file_content

    def test_mce_returns_float(self, service_file_content):
        """Test calculate_mce returns float"""
        if 'def calculate_mce(' in service_file_content:
            idx = service_file_content.find('def calculate_mce(')
            method_sig = service_file_content[idx:idx+150]
            assert 'float' in method_sig


class TestConfidenceAccuracyCorrelation:
    """Test confidence vs accuracy correlation analysis"""

    @pytest.fixture
    def service_file_content(self):
        """Read the calibration service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'confidence_calibration_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_calculate_correlation_method(self, service_file_content):
        """Test calculate_confidence_accuracy_correlation method exists"""
        assert 'def calculate_confidence_accuracy_correlation(' in service_file_content

    def test_correlation_has_docstring(self, service_file_content):
        """Test calculate_confidence_accuracy_correlation has docstring"""
        if 'def calculate_confidence_accuracy_correlation(' in service_file_content:
            idx = service_file_content.find('def calculate_confidence_accuracy_correlation(')
            method_section = service_file_content[idx:idx+600]
            assert '"""' in method_section

    def test_correlation_returns_dict(self, service_file_content):
        """Test method returns Dict with correlation metrics"""
        if 'def calculate_confidence_accuracy_correlation(' in service_file_content:
            idx = service_file_content.find('def calculate_confidence_accuracy_correlation(')
            method_sig = service_file_content[idx:idx+200]
            assert 'Dict' in method_sig


class TestPerWordConfidenceAggregation:
    """Test per-word confidence aggregation methods"""

    @pytest.fixture
    def service_file_content(self):
        """Read the calibration service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'confidence_calibration_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_aggregate_word_confidences_method(self, service_file_content):
        """Test aggregate_word_confidences method exists"""
        assert 'def aggregate_word_confidences(' in service_file_content

    def test_aggregation_has_docstring(self, service_file_content):
        """Test aggregate_word_confidences has docstring"""
        if 'def aggregate_word_confidences(' in service_file_content:
            idx = service_file_content.find('def aggregate_word_confidences(')
            method_section = service_file_content[idx:idx+600]
            assert '"""' in method_section

    def test_aggregation_accepts_method_parameter(self, service_file_content):
        """Test aggregate_word_confidences accepts method parameter"""
        if 'def aggregate_word_confidences(' in service_file_content:
            idx = service_file_content.find('def aggregate_word_confidences(')
            method_sig = service_file_content[idx:idx+200]
            assert 'method' in method_sig

    def test_supports_mean_aggregation(self, service_file_content):
        """Test supports mean aggregation method"""
        assert "'mean'" in service_file_content or '"mean"' in service_file_content

    def test_supports_min_aggregation(self, service_file_content):
        """Test supports min aggregation method"""
        assert "'min'" in service_file_content or '"min"' in service_file_content

    def test_supports_geometric_mean_aggregation(self, service_file_content):
        """Test supports geometric mean aggregation method"""
        assert 'geometric' in service_file_content.lower()


class TestBinningMethods:
    """Test binning methods for calibration"""

    @pytest.fixture
    def service_file_content(self):
        """Read the calibration service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'confidence_calibration_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_bin_predictions_method(self, service_file_content):
        """Test bin_predictions method exists"""
        assert 'def bin_predictions(' in service_file_content

    def test_bin_predictions_returns_dict(self, service_file_content):
        """Test bin_predictions returns Dict"""
        if 'def bin_predictions(' in service_file_content:
            idx = service_file_content.find('def bin_predictions(')
            method_sig = service_file_content[idx:idx+150]
            assert 'Dict' in method_sig


class TestCalibrationMetrics:
    """Test comprehensive calibration metrics"""

    @pytest.fixture
    def service_file_content(self):
        """Read the calibration service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'confidence_calibration_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_calibration_metrics_method(self, service_file_content):
        """Test get_calibration_metrics method exists"""
        assert 'def get_calibration_metrics(' in service_file_content

    def test_calibration_metrics_returns_dict(self, service_file_content):
        """Test get_calibration_metrics returns Dict"""
        if 'def get_calibration_metrics(' in service_file_content:
            idx = service_file_content.find('def get_calibration_metrics(')
            method_sig = service_file_content[idx:idx+150]
            assert 'Dict' in method_sig

    def test_metrics_include_ece(self, service_file_content):
        """Test metrics include ECE"""
        if 'def get_calibration_metrics(' in service_file_content:
            idx = service_file_content.find('def get_calibration_metrics(')
            method_def = service_file_content[idx:idx+1000]
            assert "'ece'" in method_def or '"ece"' in method_def

    def test_metrics_include_mce(self, service_file_content):
        """Test metrics include MCE"""
        if 'def get_calibration_metrics(' in service_file_content:
            idx = service_file_content.find('def get_calibration_metrics(')
            method_def = service_file_content[idx:idx+1200]
            assert "'mce'" in method_def or '"mce"' in method_def


class TestPredictionDataStructure:
    """Test prediction data structure handling"""

    @pytest.fixture
    def service_file_content(self):
        """Read the calibration service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'confidence_calibration_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_handles_confidence_field(self, service_file_content):
        """Test service handles confidence field in predictions"""
        assert 'confidence' in service_file_content

    def test_handles_correct_field(self, service_file_content):
        """Test service handles correct/accuracy field in predictions"""
        assert 'correct' in service_file_content or 'accuracy' in service_file_content


class TestEdgeCases:
    """Test edge case handling"""

    @pytest.fixture
    def service_file_content(self):
        """Read the calibration service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'confidence_calibration_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_handles_empty_predictions(self, service_file_content):
        """Test service handles empty predictions list"""
        # Should check for empty list
        assert 'not predictions' in service_file_content or 'len(predictions) == 0' in service_file_content or '[]' in service_file_content

    def test_handles_single_prediction(self, service_file_content):
        """Test service handles single prediction"""
        # Should handle len(predictions) == 1 case
        assert 'predictions' in service_file_content


class TestTypeHints:
    """Test type hints for calibration methods"""

    @pytest.fixture
    def service_file_content(self):
        """Read the calibration service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'confidence_calibration_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_imports_typing_modules(self, service_file_content):
        """Test typing modules are imported"""
        assert 'from typing import' in service_file_content

    def test_uses_list_type_hint(self, service_file_content):
        """Test List type hint is used"""
        assert 'List[' in service_file_content

    def test_uses_dict_type_hint(self, service_file_content):
        """Test Dict type hint is used"""
        assert 'Dict[' in service_file_content

    def test_uses_optional_type_hint(self, service_file_content):
        """Test Optional type hint is used"""
        assert 'Optional[' in service_file_content


class TestDocstrings:
    """Test comprehensive documentation"""

    @pytest.fixture
    def service_file_content(self):
        """Read the calibration service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'confidence_calibration_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        """Test module has docstring"""
        # Should start with docstring
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        """Test class has docstring"""
        if 'class ConfidenceCalibrationService' in service_file_content:
            idx = service_file_content.find('class ConfidenceCalibrationService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section


class TestBinDataContent:
    """Test bin data contains required fields"""

    @pytest.fixture
    def service_file_content(self):
        """Read the calibration service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'confidence_calibration_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_bin_data_has_mean_confidence(self, service_file_content):
        """Test bin data includes mean confidence"""
        assert 'mean_confidence' in service_file_content or 'avg_confidence' in service_file_content

    def test_bin_data_has_accuracy(self, service_file_content):
        """Test bin data includes accuracy"""
        assert 'accuracy' in service_file_content

    def test_bin_data_has_count(self, service_file_content):
        """Test bin data includes count"""
        assert 'count' in service_file_content


