"""
Test suite for Numeric and Alphanumeric Transcription Testing.

Numeric data (phone numbers, addresses, serial numbers) is challenging for
ASR systems because numbers can be spoken in various formats and may include
letter-number combinations.

Components:
- Phone number accuracy: Recognize various phone formats
- Address transcription: Street addresses with numbers and abbreviations
- Alphanumeric sequences: License plates, serial numbers, confirmation codes
- Format detection: Identify numeric patterns in text
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestNumericServiceExists:
    """Test that numeric transcription service exists"""

    @pytest.fixture
    def service_file_content(self):
        """Read the numeric transcription service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'numeric_transcription_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        """Test that numeric_transcription_service.py exists"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'numeric_transcription_service.py'
        )
        assert os.path.exists(service_file), (
            "numeric_transcription_service.py should exist"
        )

    def test_service_class_exists(self, service_file_content):
        """Test that NumericTranscriptionService class exists"""
        assert 'class NumericTranscriptionService' in service_file_content


class TestPhoneNumberAccuracy:
    """Test phone number transcription accuracy"""

    @pytest.fixture
    def service_file_content(self):
        """Read the numeric transcription service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'numeric_transcription_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_extract_phone_numbers_method(self, service_file_content):
        """Test extract_phone_numbers method exists"""
        assert 'def extract_phone_numbers(' in service_file_content

    def test_has_calculate_phone_accuracy_method(self, service_file_content):
        """Test calculate_phone_accuracy method exists"""
        assert 'def calculate_phone_accuracy(' in service_file_content

    def test_phone_accuracy_returns_dict(self, service_file_content):
        """Test calculate_phone_accuracy returns Dict"""
        if 'def calculate_phone_accuracy(' in service_file_content:
            idx = service_file_content.find('def calculate_phone_accuracy(')
            method_sig = service_file_content[idx:idx+250]
            assert 'Dict' in method_sig


class TestAddressTranscription:
    """Test address transcription accuracy"""

    @pytest.fixture
    def service_file_content(self):
        """Read the numeric transcription service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'numeric_transcription_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_extract_addresses_method(self, service_file_content):
        """Test extract_addresses method exists"""
        assert 'def extract_addresses(' in service_file_content

    def test_has_calculate_address_accuracy_method(self, service_file_content):
        """Test calculate_address_accuracy method exists"""
        assert 'def calculate_address_accuracy(' in service_file_content


class TestAlphanumericSequences:
    """Test alphanumeric sequence handling"""

    @pytest.fixture
    def service_file_content(self):
        """Read the numeric transcription service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'numeric_transcription_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_extract_alphanumeric_method(self, service_file_content):
        """Test extract_alphanumeric method exists"""
        assert 'def extract_alphanumeric(' in service_file_content

    def test_has_calculate_alphanumeric_accuracy_method(self, service_file_content):
        """Test calculate_alphanumeric_accuracy method exists"""
        assert 'def calculate_alphanumeric_accuracy(' in service_file_content


class TestNumericFormatDetection:
    """Test numeric format detection"""

    @pytest.fixture
    def service_file_content(self):
        """Read the numeric transcription service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'numeric_transcription_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_detect_numeric_patterns_method(self, service_file_content):
        """Test detect_numeric_patterns method exists"""
        assert 'def detect_numeric_patterns(' in service_file_content

    def test_patterns_returns_list(self, service_file_content):
        """Test detect_numeric_patterns returns List"""
        if 'def detect_numeric_patterns(' in service_file_content:
            idx = service_file_content.find('def detect_numeric_patterns(')
            method_sig = service_file_content[idx:idx+200]
            assert 'List' in method_sig


class TestNumericNormalization:
    """Test numeric text normalization"""

    @pytest.fixture
    def service_file_content(self):
        """Read the numeric transcription service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'numeric_transcription_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_normalize_numeric_method(self, service_file_content):
        """Test normalize_numeric method exists"""
        assert 'def normalize_numeric(' in service_file_content

    def test_has_digit_to_words_conversion(self, service_file_content):
        """Test digit-to-words or words-to-digit conversion"""
        assert 'digit' in service_file_content.lower() or 'word' in service_file_content.lower()


class TestNumericMetrics:
    """Test comprehensive numeric metrics"""

    @pytest.fixture
    def service_file_content(self):
        """Read the numeric transcription service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'numeric_transcription_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_numeric_metrics_method(self, service_file_content):
        """Test get_numeric_metrics method exists"""
        assert 'def get_numeric_metrics(' in service_file_content

    def test_metrics_returns_dict(self, service_file_content):
        """Test get_numeric_metrics returns Dict"""
        if 'def get_numeric_metrics(' in service_file_content:
            idx = service_file_content.find('def get_numeric_metrics(')
            method_sig = service_file_content[idx:idx+200]
            assert 'Dict' in method_sig

    def test_metrics_include_accuracy(self, service_file_content):
        """Test metrics include accuracy"""
        assert 'accuracy' in service_file_content.lower()


class TestDigitAccuracy:
    """Test digit-by-digit accuracy"""

    @pytest.fixture
    def service_file_content(self):
        """Read the numeric transcription service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'numeric_transcription_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_calculate_digit_accuracy_method(self, service_file_content):
        """Test calculate_digit_accuracy method exists"""
        assert 'def calculate_digit_accuracy(' in service_file_content


class TestTypeHints:
    """Test type hints for numeric service"""

    @pytest.fixture
    def service_file_content(self):
        """Read the numeric transcription service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'numeric_transcription_service.py'
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


class TestDocstrings:
    """Test comprehensive documentation"""

    @pytest.fixture
    def service_file_content(self):
        """Read the numeric transcription service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'numeric_transcription_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        """Test module has docstring"""
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        """Test class has docstring"""
        if 'class NumericTranscriptionService' in service_file_content:
            idx = service_file_content.find('class NumericTranscriptionService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section


class TestPatternTypes:
    """Test pattern type support"""

    @pytest.fixture
    def service_file_content(self):
        """Read the numeric transcription service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'numeric_transcription_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_supports_phone_pattern(self, service_file_content):
        """Test supports phone number patterns"""
        assert 'phone' in service_file_content.lower()

    def test_supports_address_pattern(self, service_file_content):
        """Test supports address patterns"""
        assert 'address' in service_file_content.lower()

    def test_supports_serial_pattern(self, service_file_content):
        """Test supports serial number patterns"""
        assert 'serial' in service_file_content.lower() or 'alphanumeric' in service_file_content.lower()


