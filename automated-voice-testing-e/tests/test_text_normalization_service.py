"""
Test suite for Text Normalization Testing Service.

This service provides locale-aware text normalization testing.

Components:
- Number format by locale (1,000 vs 1.000)
- Date format by locale (MM/DD vs DD/MM)
- Currency format by locale
- Unit conversion by locale
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestTextNormalizationServiceExists:
    """Test that text normalization service exists"""

    @pytest.fixture
    def service_file_content(self):
        """Read the service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'text_normalization_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        """Test that text_normalization_service.py exists"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'text_normalization_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        """Test that TextNormalizationService class exists"""
        assert 'class TextNormalizationService' in service_file_content


class TestNumberFormat:
    """Test number format by locale"""

    def test_normalize_number_returns_dict(self):
        """Test normalize_number returns dictionary"""
        from services.text_normalization_service import TextNormalizationService
        service = TextNormalizationService()
        result = service.normalize_number('1,000', 'en-US')
        assert isinstance(result, dict)

    def test_normalize_number_has_required_keys(self):
        """Test normalize_number result has required keys"""
        from services.text_normalization_service import TextNormalizationService
        service = TextNormalizationService()
        result = service.normalize_number('1,000', 'en-US')
        required_keys = {'original', 'normalized', 'locale', 'format'}
        assert required_keys.issubset(result.keys())

    def test_normalize_number_preserves_original(self):
        """Test normalize_number preserves original text"""
        from services.text_normalization_service import TextNormalizationService
        service = TextNormalizationService()
        result = service.normalize_number('1,000', 'en-US')
        assert result['original'] == '1,000'

    def test_get_number_formats_returns_list(self):
        """Test get_number_formats returns list"""
        from services.text_normalization_service import TextNormalizationService
        service = TextNormalizationService()
        result = service.get_number_formats()
        assert isinstance(result, list)
        assert len(result) > 0

    def test_get_number_formats_has_locales(self):
        """Test get_number_formats entries have locale key"""
        from services.text_normalization_service import TextNormalizationService
        service = TextNormalizationService()
        formats = service.get_number_formats()
        for fmt in formats:
            assert 'locale' in fmt


class TestDateFormat:
    """Test date format by locale"""

    def test_normalize_date_returns_dict(self):
        """Test normalize_date returns dictionary"""
        from services.text_normalization_service import TextNormalizationService
        service = TextNormalizationService()
        result = service.normalize_date('12/31/2024', 'en-US')
        assert isinstance(result, dict)

    def test_normalize_date_has_required_keys(self):
        """Test normalize_date result has required keys"""
        from services.text_normalization_service import TextNormalizationService
        service = TextNormalizationService()
        result = service.normalize_date('12/31/2024', 'en-US')
        required_keys = {'original', 'normalized', 'locale', 'format'}
        assert required_keys.issubset(result.keys())

    def test_get_date_formats_returns_list(self):
        """Test get_date_formats returns list"""
        from services.text_normalization_service import TextNormalizationService
        service = TextNormalizationService()
        result = service.get_date_formats()
        assert isinstance(result, list)
        assert len(result) > 0

    def test_get_date_formats_has_format_key(self):
        """Test get_date_formats entries have format key"""
        from services.text_normalization_service import TextNormalizationService
        service = TextNormalizationService()
        formats = service.get_date_formats()
        for fmt in formats:
            assert 'format' in fmt


class TestCurrencyFormat:
    """Test currency format by locale"""

    def test_normalize_currency_returns_dict(self):
        """Test normalize_currency returns dictionary"""
        from services.text_normalization_service import TextNormalizationService
        service = TextNormalizationService()
        result = service.normalize_currency('$1,000', 'en-US')
        assert isinstance(result, dict)

    def test_normalize_currency_has_required_keys(self):
        """Test normalize_currency result has required keys"""
        from services.text_normalization_service import TextNormalizationService
        service = TextNormalizationService()
        result = service.normalize_currency('$1,000', 'en-US')
        required_keys = {'original', 'normalized', 'locale', 'symbol_position'}
        assert required_keys.issubset(result.keys())

    def test_get_currency_formats_returns_list(self):
        """Test get_currency_formats returns list"""
        from services.text_normalization_service import TextNormalizationService
        service = TextNormalizationService()
        result = service.get_currency_formats()
        assert isinstance(result, list)
        assert len(result) > 0

    def test_get_currency_formats_has_symbol(self):
        """Test get_currency_formats entries have symbol key"""
        from services.text_normalization_service import TextNormalizationService
        service = TextNormalizationService()
        formats = service.get_currency_formats()
        for fmt in formats:
            assert 'symbol' in fmt


class TestUnitConversion:
    """Test unit conversion by locale"""

    def test_normalize_units_returns_dict(self):
        """Test normalize_units returns dictionary"""
        from services.text_normalization_service import TextNormalizationService
        service = TextNormalizationService()
        result = service.normalize_units('5 miles', 'en-US')
        assert isinstance(result, dict)

    def test_normalize_units_has_required_keys(self):
        """Test normalize_units result has required keys"""
        from services.text_normalization_service import TextNormalizationService
        service = TextNormalizationService()
        result = service.normalize_units('5 miles', 'en-US')
        required_keys = {'original', 'normalized', 'locale', 'system'}
        assert required_keys.issubset(result.keys())

    def test_normalize_units_us_locale_is_imperial(self):
        """Test en-US locale uses imperial system"""
        from services.text_normalization_service import TextNormalizationService
        service = TextNormalizationService()
        result = service.normalize_units('5 miles', 'en-US')
        assert result['system'] == 'imperial'

    def test_get_unit_systems_returns_list(self):
        """Test get_unit_systems returns list"""
        from services.text_normalization_service import TextNormalizationService
        service = TextNormalizationService()
        result = service.get_unit_systems()
        assert isinstance(result, list)
        assert len(result) > 0

    def test_get_unit_systems_has_system_key(self):
        """Test get_unit_systems entries have system key"""
        from services.text_normalization_service import TextNormalizationService
        service = TextNormalizationService()
        systems = service.get_unit_systems()
        for sys in systems:
            assert 'system' in sys


class TestNormalizationConfig:
    """Test normalization configuration"""

    def test_get_normalization_config_returns_dict(self):
        """Test get_normalization_config returns dictionary"""
        from services.text_normalization_service import TextNormalizationService
        service = TextNormalizationService()
        result = service.get_normalization_config()
        assert isinstance(result, dict)

    def test_get_normalization_config_has_counts(self):
        """Test get_normalization_config has format counts"""
        from services.text_normalization_service import TextNormalizationService
        service = TextNormalizationService()
        result = service.get_normalization_config()
        expected_keys = {'number_formats', 'date_formats', 'currency_formats', 'unit_systems'}
        assert expected_keys.issubset(result.keys())

    def test_get_supported_locales_returns_list(self):
        """Test get_supported_locales returns list"""
        from services.text_normalization_service import TextNormalizationService
        service = TextNormalizationService()
        result = service.get_supported_locales()
        assert isinstance(result, list)

    def test_get_supported_locales_includes_en_us(self):
        """Test get_supported_locales includes en-US"""
        from services.text_normalization_service import TextNormalizationService
        service = TextNormalizationService()
        locales = service.get_supported_locales()
        assert 'en-US' in locales

    def test_get_supported_locales_returns_strings(self):
        """Test get_supported_locales returns strings"""
        from services.text_normalization_service import TextNormalizationService
        service = TextNormalizationService()
        locales = service.get_supported_locales()
        for locale in locales:
            assert isinstance(locale, str)

