"""
Test suite for Intent Classification Accuracy Service.

This service provides comprehensive metrics for evaluating intent
classification performance in NLU systems.

Components:
- Precision, Recall, F1 per intent class
- Confusion matrix generation
- Top-N intent accuracy (top-1, top-3, top-5)
- Confidence threshold optimization
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestIntentClassificationServiceExists:
    """Test that intent classification service exists"""

    @pytest.fixture
    def service_file_content(self):
        """Read the intent classification service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'intent_classification_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        """Test that intent_classification_service.py exists"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'intent_classification_service.py'
        )
        assert os.path.exists(service_file), (
            "intent_classification_service.py should exist"
        )

    def test_service_class_exists(self, service_file_content):
        """Test that IntentClassificationService class exists"""
        assert 'class IntentClassificationService' in service_file_content


class TestClassificationMetrics:
    """Test classification metrics calculation"""

    @pytest.fixture
    def service_file_content(self):
        """Read the intent classification service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'intent_classification_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_calculate_precision_method(self, service_file_content):
        """Test calculate_precision method exists"""
        assert 'def calculate_precision(' in service_file_content

    def test_has_calculate_recall_method(self, service_file_content):
        """Test calculate_recall method exists"""
        assert 'def calculate_recall(' in service_file_content

    def test_has_calculate_f1_method(self, service_file_content):
        """Test calculate_f1 method exists"""
        assert 'def calculate_f1(' in service_file_content


class TestConfusionMatrix:
    """Test confusion matrix generation"""

    @pytest.fixture
    def service_file_content(self):
        """Read the intent classification service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'intent_classification_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_generate_confusion_matrix_method(self, service_file_content):
        """Test generate_confusion_matrix method exists"""
        assert 'def generate_confusion_matrix(' in service_file_content

    def test_confusion_matrix_returns_dict(self, service_file_content):
        """Test generate_confusion_matrix returns Dict"""
        if 'def generate_confusion_matrix(' in service_file_content:
            idx = service_file_content.find('def generate_confusion_matrix(')
            method_sig = service_file_content[idx:idx+250]
            assert 'Dict' in method_sig


class TestTopNAccuracy:
    """Test top-N intent accuracy"""

    @pytest.fixture
    def service_file_content(self):
        """Read the intent classification service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'intent_classification_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_calculate_top_n_accuracy_method(self, service_file_content):
        """Test calculate_top_n_accuracy method exists"""
        assert 'def calculate_top_n_accuracy(' in service_file_content

    def test_top_n_returns_dict(self, service_file_content):
        """Test calculate_top_n_accuracy returns Dict"""
        if 'def calculate_top_n_accuracy(' in service_file_content:
            idx = service_file_content.find('def calculate_top_n_accuracy(')
            method_sig = service_file_content[idx:idx+250]
            assert 'Dict' in method_sig


class TestThresholdOptimization:
    """Test confidence threshold optimization"""

    @pytest.fixture
    def service_file_content(self):
        """Read the intent classification service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'intent_classification_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_optimize_threshold_method(self, service_file_content):
        """Test optimize_threshold method exists"""
        assert 'def optimize_threshold(' in service_file_content

    def test_threshold_returns_dict(self, service_file_content):
        """Test optimize_threshold returns Dict"""
        if 'def optimize_threshold(' in service_file_content:
            idx = service_file_content.find('def optimize_threshold(')
            method_sig = service_file_content[idx:idx+250]
            assert 'Dict' in method_sig


class TestPerClassMetrics:
    """Test per-class metrics calculation"""

    @pytest.fixture
    def service_file_content(self):
        """Read the intent classification service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'intent_classification_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_calculate_per_class_metrics_method(self, service_file_content):
        """Test calculate_per_class_metrics method exists"""
        assert 'def calculate_per_class_metrics(' in service_file_content

    def test_per_class_returns_dict(self, service_file_content):
        """Test calculate_per_class_metrics returns Dict"""
        if 'def calculate_per_class_metrics(' in service_file_content:
            idx = service_file_content.find('def calculate_per_class_metrics(')
            method_sig = service_file_content[idx:idx+250]
            assert 'Dict' in method_sig


class TestOverallMetrics:
    """Test overall classification metrics"""

    @pytest.fixture
    def service_file_content(self):
        """Read the intent classification service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'intent_classification_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_classification_metrics_method(self, service_file_content):
        """Test get_classification_metrics method exists"""
        assert 'def get_classification_metrics(' in service_file_content

    def test_metrics_returns_dict(self, service_file_content):
        """Test get_classification_metrics returns Dict"""
        if 'def get_classification_metrics(' in service_file_content:
            idx = service_file_content.find('def get_classification_metrics(')
            method_sig = service_file_content[idx:idx+250]
            assert 'Dict' in method_sig


class TestTypeHints:
    """Test type hints for intent classification service"""

    @pytest.fixture
    def service_file_content(self):
        """Read the intent classification service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'intent_classification_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_imports_typing_modules(self, service_file_content):
        """Test typing modules are imported"""
        assert 'from typing import' in service_file_content

    def test_uses_dict_type_hint(self, service_file_content):
        """Test Dict type hint is used"""
        assert 'Dict[' in service_file_content

    def test_uses_list_type_hint(self, service_file_content):
        """Test List type hint is used"""
        assert 'List[' in service_file_content


class TestDocstrings:
    """Test comprehensive documentation"""

    @pytest.fixture
    def service_file_content(self):
        """Read the intent classification service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'intent_classification_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        """Test module has docstring"""
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        """Test class has docstring"""
        if 'class IntentClassificationService' in service_file_content:
            idx = service_file_content.find('class IntentClassificationService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section

