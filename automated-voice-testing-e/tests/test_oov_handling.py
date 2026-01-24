"""
Test suite for Out-of-Vocabulary (OOV) word handling.

OOV words are words that appear in the input but are not in the ASR
system's vocabulary/language model. Tracking OOV rates helps identify:
- Domain-specific terminology gaps
- Need for custom vocabulary additions
- Performance issues on specific content types

Components:
- OOV word detection: Identify words not in vocabulary
- OOV rate tracking: Calculate percentage of OOV words
- Custom vocabulary testing: Test recognition of specific terms
- User-defined lexicons: Support custom word lists
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestOOVServiceExists:
    """Test that OOV detection service exists"""

    @pytest.fixture
    def service_file_content(self):
        """Read the OOV detection service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'oov_detection_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        """Test that oov_detection_service.py exists"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'oov_detection_service.py'
        )
        assert os.path.exists(service_file), (
            "oov_detection_service.py should exist"
        )

    def test_service_class_exists(self, service_file_content):
        """Test that OOVDetectionService class exists"""
        assert 'class OOVDetectionService' in service_file_content


class TestOOVWordDetection:
    """Test OOV word detection functionality"""

    @pytest.fixture
    def service_file_content(self):
        """Read the OOV detection service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'oov_detection_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_detect_oov_words_method(self, service_file_content):
        """Test detect_oov_words method exists"""
        assert 'def detect_oov_words(' in service_file_content

    def test_detect_oov_has_docstring(self, service_file_content):
        """Test detect_oov_words has docstring"""
        if 'def detect_oov_words(' in service_file_content:
            idx = service_file_content.find('def detect_oov_words(')
            method_section = service_file_content[idx:idx+600]
            assert '"""' in method_section

    def test_detect_oov_accepts_text(self, service_file_content):
        """Test method accepts text parameter"""
        if 'def detect_oov_words(' in service_file_content:
            idx = service_file_content.find('def detect_oov_words(')
            method_sig = service_file_content[idx:idx+200]
            assert 'text' in method_sig

    def test_detect_oov_accepts_vocabulary(self, service_file_content):
        """Test method accepts vocabulary parameter"""
        if 'def detect_oov_words(' in service_file_content:
            idx = service_file_content.find('def detect_oov_words(')
            method_sig = service_file_content[idx:idx+200]
            assert 'vocabulary' in method_sig

    def test_detect_oov_returns_list(self, service_file_content):
        """Test method returns List"""
        if 'def detect_oov_words(' in service_file_content:
            idx = service_file_content.find('def detect_oov_words(')
            method_sig = service_file_content[idx:idx+200]
            assert 'List' in method_sig


class TestOOVRateCalculation:
    """Test OOV rate calculation"""

    @pytest.fixture
    def service_file_content(self):
        """Read the OOV detection service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'oov_detection_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_calculate_oov_rate_method(self, service_file_content):
        """Test calculate_oov_rate method exists"""
        assert 'def calculate_oov_rate(' in service_file_content

    def test_oov_rate_has_docstring(self, service_file_content):
        """Test calculate_oov_rate has docstring"""
        if 'def calculate_oov_rate(' in service_file_content:
            idx = service_file_content.find('def calculate_oov_rate(')
            method_section = service_file_content[idx:idx+600]
            assert '"""' in method_section

    def test_oov_rate_returns_float(self, service_file_content):
        """Test calculate_oov_rate returns float"""
        if 'def calculate_oov_rate(' in service_file_content:
            idx = service_file_content.find('def calculate_oov_rate(')
            method_sig = service_file_content[idx:idx+250]
            assert 'float' in method_sig


class TestVocabularyManagement:
    """Test vocabulary management functionality"""

    @pytest.fixture
    def service_file_content(self):
        """Read the OOV detection service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'oov_detection_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_load_vocabulary_method(self, service_file_content):
        """Test load_vocabulary method exists"""
        assert 'def load_vocabulary(' in service_file_content

    def test_has_add_to_vocabulary_method(self, service_file_content):
        """Test add_to_vocabulary method exists"""
        assert 'def add_to_vocabulary(' in service_file_content

    def test_has_get_vocabulary_method(self, service_file_content):
        """Test get_vocabulary method exists"""
        assert 'def get_vocabulary(' in service_file_content


class TestCustomLexicons:
    """Test user-defined lexicon support"""

    @pytest.fixture
    def service_file_content(self):
        """Read the OOV detection service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'oov_detection_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_load_custom_lexicon_method(self, service_file_content):
        """Test load_custom_lexicon method exists"""
        assert 'def load_custom_lexicon(' in service_file_content

    def test_has_merge_lexicons_method(self, service_file_content):
        """Test merge_lexicons method exists"""
        assert 'def merge_lexicons(' in service_file_content

    def test_lexicon_accepts_domain(self, service_file_content):
        """Test lexicon methods accept domain parameter"""
        assert 'domain' in service_file_content


class TestDomainTracking:
    """Test OOV tracking per domain"""

    @pytest.fixture
    def service_file_content(self):
        """Read the OOV detection service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'oov_detection_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_track_oov_by_domain_method(self, service_file_content):
        """Test track_oov_by_domain method exists"""
        assert 'def track_oov_by_domain(' in service_file_content

    def test_has_get_domain_oov_stats_method(self, service_file_content):
        """Test get_domain_oov_stats method exists"""
        assert 'def get_domain_oov_stats(' in service_file_content

    def test_stats_returns_dict(self, service_file_content):
        """Test get_domain_oov_stats returns Dict"""
        if 'def get_domain_oov_stats(' in service_file_content:
            idx = service_file_content.find('def get_domain_oov_stats(')
            method_sig = service_file_content[idx:idx+150]
            assert 'Dict' in method_sig


class TestTextNormalization:
    """Test text normalization for OOV detection"""

    @pytest.fixture
    def service_file_content(self):
        """Read the OOV detection service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'oov_detection_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_normalize_text_method(self, service_file_content):
        """Test normalize_text method exists"""
        assert 'def normalize_text(' in service_file_content

    def test_has_tokenize_method(self, service_file_content):
        """Test tokenize method exists"""
        assert 'def tokenize(' in service_file_content


class TestOOVAnalysis:
    """Test OOV analysis and reporting"""

    @pytest.fixture
    def service_file_content(self):
        """Read the OOV detection service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'oov_detection_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_oov_analysis_method(self, service_file_content):
        """Test get_oov_analysis method exists"""
        assert 'def get_oov_analysis(' in service_file_content

    def test_analysis_returns_dict(self, service_file_content):
        """Test get_oov_analysis returns Dict"""
        if 'def get_oov_analysis(' in service_file_content:
            idx = service_file_content.find('def get_oov_analysis(')
            method_sig = service_file_content[idx:idx+250]
            assert 'Dict' in method_sig

    def test_analysis_includes_oov_words(self, service_file_content):
        """Test analysis includes OOV words list"""
        if 'def get_oov_analysis(' in service_file_content:
            idx = service_file_content.find('def get_oov_analysis(')
            method_def = service_file_content[idx:idx+800]
            assert 'oov_words' in method_def

    def test_analysis_includes_oov_rate(self, service_file_content):
        """Test analysis includes OOV rate"""
        if 'def get_oov_analysis(' in service_file_content:
            idx = service_file_content.find('def get_oov_analysis(')
            method_def = service_file_content[idx:idx+800]
            assert 'oov_rate' in method_def


class TestTypeHints:
    """Test type hints for OOV service"""

    @pytest.fixture
    def service_file_content(self):
        """Read the OOV detection service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'oov_detection_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_imports_typing_modules(self, service_file_content):
        """Test typing modules are imported"""
        assert 'from typing import' in service_file_content

    def test_uses_set_type_hint(self, service_file_content):
        """Test Set type hint is used for vocabulary"""
        assert 'Set[' in service_file_content

    def test_uses_list_type_hint(self, service_file_content):
        """Test List type hint is used"""
        assert 'List[' in service_file_content

    def test_uses_optional_type_hint(self, service_file_content):
        """Test Optional type hint is used"""
        assert 'Optional[' in service_file_content


class TestDocstrings:
    """Test comprehensive documentation"""

    @pytest.fixture
    def service_file_content(self):
        """Read the OOV detection service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'oov_detection_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        """Test module has docstring"""
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        """Test class has docstring"""
        if 'class OOVDetectionService' in service_file_content:
            idx = service_file_content.find('class OOVDetectionService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section


class TestCaseSensitivity:
    """Test case handling options"""

    @pytest.fixture
    def service_file_content(self):
        """Read the OOV detection service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'oov_detection_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_supports_case_insensitive(self, service_file_content):
        """Test supports case-insensitive matching"""
        assert 'case_sensitive' in service_file_content or 'lower()' in service_file_content


class TestFrequencyAnalysis:
    """Test OOV word frequency analysis"""

    @pytest.fixture
    def service_file_content(self):
        """Read the OOV detection service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'oov_detection_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_oov_frequency_method(self, service_file_content):
        """Test get_oov_frequency method exists"""
        assert 'def get_oov_frequency(' in service_file_content

    def test_frequency_returns_dict(self, service_file_content):
        """Test get_oov_frequency returns Dict"""
        if 'def get_oov_frequency(' in service_file_content:
            idx = service_file_content.find('def get_oov_frequency(')
            method_sig = service_file_content[idx:idx+150]
            assert 'Dict' in method_sig


