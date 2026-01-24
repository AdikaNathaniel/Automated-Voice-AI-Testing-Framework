"""
Test suite for Homophone Disambiguation Testing.

Homophones are words that sound the same but have different meanings and
spellings (e.g., their/there/they're, to/too/two). ASR systems must use
context to choose the correct spelling.

Components:
- Homophone detection: Identify homophones in text
- Context analysis: Evaluate if context is sufficient for disambiguation
- Accuracy metrics: Calculate homophone-specific accuracy
- Common homophone sets: Built-in database of common homophones
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestHomophoneServiceExists:
    """Test that homophone disambiguation service exists"""

    @pytest.fixture
    def service_file_content(self):
        """Read the homophone disambiguation service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'homophone_disambiguation_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        """Test that homophone_disambiguation_service.py exists"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'homophone_disambiguation_service.py'
        )
        assert os.path.exists(service_file), (
            "homophone_disambiguation_service.py should exist"
        )

    def test_service_class_exists(self, service_file_content):
        """Test that HomophoneDisambiguationService class exists"""
        assert 'class HomophoneDisambiguationService' in service_file_content


class TestHomophoneSets:
    """Test homophone set management"""

    @pytest.fixture
    def service_file_content(self):
        """Read the homophone disambiguation service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'homophone_disambiguation_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_their_there_theyre(self, service_file_content):
        """Test includes their/there/they're homophone set"""
        assert 'their' in service_file_content.lower()
        assert 'there' in service_file_content.lower()

    def test_has_to_too_two(self, service_file_content):
        """Test includes to/too/two homophone set"""
        assert 'too' in service_file_content.lower()
        assert 'two' in service_file_content.lower()

    def test_has_your_youre(self, service_file_content):
        """Test includes your/you're homophone set"""
        assert 'your' in service_file_content.lower()

    def test_has_its_its(self, service_file_content):
        """Test includes its/it's homophone set"""
        assert "it's" in service_file_content.lower() or 'its' in service_file_content.lower()


class TestHomophoneDetection:
    """Test homophone detection functionality"""

    @pytest.fixture
    def service_file_content(self):
        """Read the homophone disambiguation service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'homophone_disambiguation_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_detect_homophones_method(self, service_file_content):
        """Test detect_homophones method exists"""
        assert 'def detect_homophones(' in service_file_content

    def test_detect_homophones_has_docstring(self, service_file_content):
        """Test detect_homophones has docstring"""
        if 'def detect_homophones(' in service_file_content:
            idx = service_file_content.find('def detect_homophones(')
            method_section = service_file_content[idx:idx+600]
            assert '"""' in method_section

    def test_detect_homophones_returns_list(self, service_file_content):
        """Test detect_homophones returns List"""
        if 'def detect_homophones(' in service_file_content:
            idx = service_file_content.find('def detect_homophones(')
            method_sig = service_file_content[idx:idx+200]
            assert 'List' in method_sig


class TestHomophoneAccuracy:
    """Test homophone accuracy calculation"""

    @pytest.fixture
    def service_file_content(self):
        """Read the homophone disambiguation service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'homophone_disambiguation_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_calculate_homophone_accuracy_method(self, service_file_content):
        """Test calculate_homophone_accuracy method exists"""
        assert 'def calculate_homophone_accuracy(' in service_file_content

    def test_accuracy_has_docstring(self, service_file_content):
        """Test calculate_homophone_accuracy has docstring"""
        if 'def calculate_homophone_accuracy(' in service_file_content:
            idx = service_file_content.find('def calculate_homophone_accuracy(')
            method_section = service_file_content[idx:idx+600]
            assert '"""' in method_section

    def test_accuracy_returns_dict(self, service_file_content):
        """Test calculate_homophone_accuracy returns Dict"""
        if 'def calculate_homophone_accuracy(' in service_file_content:
            idx = service_file_content.find('def calculate_homophone_accuracy(')
            method_sig = service_file_content[idx:idx+250]
            assert 'Dict' in method_sig


class TestHomophoneSetManagement:
    """Test custom homophone set management"""

    @pytest.fixture
    def service_file_content(self):
        """Read the homophone disambiguation service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'homophone_disambiguation_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_add_homophone_set_method(self, service_file_content):
        """Test add_homophone_set method exists"""
        assert 'def add_homophone_set(' in service_file_content

    def test_has_get_homophone_sets_method(self, service_file_content):
        """Test get_homophone_sets method exists"""
        assert 'def get_homophone_sets(' in service_file_content

    def test_has_get_homophone_group_method(self, service_file_content):
        """Test get_homophone_group method exists"""
        assert 'def get_homophone_group(' in service_file_content


class TestContextAnalysis:
    """Test context-dependent analysis"""

    @pytest.fixture
    def service_file_content(self):
        """Read the homophone disambiguation service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'homophone_disambiguation_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_analyze_context_method(self, service_file_content):
        """Test analyze_context method exists"""
        assert 'def analyze_context(' in service_file_content

    def test_context_analysis_returns_dict(self, service_file_content):
        """Test analyze_context returns Dict"""
        if 'def analyze_context(' in service_file_content:
            idx = service_file_content.find('def analyze_context(')
            method_sig = service_file_content[idx:idx+200]
            assert 'Dict' in method_sig


class TestHomophoneMetrics:
    """Test comprehensive homophone metrics"""

    @pytest.fixture
    def service_file_content(self):
        """Read the homophone disambiguation service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'homophone_disambiguation_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_homophone_metrics_method(self, service_file_content):
        """Test get_homophone_metrics method exists"""
        assert 'def get_homophone_metrics(' in service_file_content

    def test_metrics_returns_dict(self, service_file_content):
        """Test get_homophone_metrics returns Dict"""
        if 'def get_homophone_metrics(' in service_file_content:
            idx = service_file_content.find('def get_homophone_metrics(')
            method_sig = service_file_content[idx:idx+250]
            assert 'Dict' in method_sig

    def test_metrics_include_accuracy(self, service_file_content):
        """Test metrics include accuracy"""
        assert 'accuracy' in service_file_content.lower()

    def test_metrics_include_total_homophones(self, service_file_content):
        """Test metrics include total count"""
        assert 'total' in service_file_content.lower()


class TestTypeHints:
    """Test type hints for homophone service"""

    @pytest.fixture
    def service_file_content(self):
        """Read the homophone disambiguation service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'homophone_disambiguation_service.py'
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

    def test_uses_set_type_hint(self, service_file_content):
        """Test Set type hint is used"""
        assert 'Set[' in service_file_content


class TestDocstrings:
    """Test comprehensive documentation"""

    @pytest.fixture
    def service_file_content(self):
        """Read the homophone disambiguation service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'homophone_disambiguation_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        """Test module has docstring"""
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        """Test class has docstring"""
        if 'class HomophoneDisambiguationService' in service_file_content:
            idx = service_file_content.find('class HomophoneDisambiguationService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section


class TestErrorHandling:
    """Test error handling in homophone service"""

    @pytest.fixture
    def service_file_content(self):
        """Read the homophone disambiguation service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'homophone_disambiguation_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_handles_empty_text(self, service_file_content):
        """Test service handles empty text"""
        # Should check for empty strings
        assert 'not text' in service_file_content or '""' in service_file_content or 'if text' in service_file_content


class TestAccuracyBySet:
    """Test accuracy calculation by homophone set"""

    @pytest.fixture
    def service_file_content(self):
        """Read the homophone disambiguation service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'homophone_disambiguation_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_accuracy_by_set_method(self, service_file_content):
        """Test get_accuracy_by_set method exists"""
        assert 'def get_accuracy_by_set(' in service_file_content


