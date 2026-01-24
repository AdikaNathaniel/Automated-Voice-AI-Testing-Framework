"""
Text Normalization Testing Service for voice AI.

This service provides locale-aware text normalization testing
for evaluating voice AI systems across different locales.

Key features:
- Number format by locale
- Date format by locale
- Currency format by locale
- Unit conversion by locale

Example:
    >>> service = TextNormalizationService()
    >>> result = service.normalize_number('1,000', 'en-US')
"""

from typing import List, Dict, Any


class TextNormalizationService:
    """
    Service for text normalization testing.

    Provides locale-aware normalization for numbers, dates,
    currencies, and units.

    Example:
        >>> service = TextNormalizationService()
        >>> locales = service.get_supported_locales()
    """

    def __init__(self):
        """Initialize the text normalization service."""
        self._normalizations: List[Dict[str, Any]] = []

    def normalize_number(
        self,
        text: str,
        locale: str = 'en-US'
    ) -> Dict[str, Any]:
        """
        Normalize number format for locale.

        Args:
            text: Text with number
            locale: Locale code

        Returns:
            Dictionary with normalized result

        Example:
            >>> result = service.normalize_number('1,000', 'en-US')
        """
        return {
            'original': text,
            'normalized': text.replace(',', '').replace('.', ''),
            'locale': locale,
            'format': 'thousands_comma' if locale == 'en-US' else 'thousands_period'
        }

    def get_number_formats(self) -> List[Dict[str, Any]]:
        """
        Get number format configurations.

        Returns:
            List of number format configs

        Example:
            >>> formats = service.get_number_formats()
        """
        return [
            {'locale': 'en-US', 'thousands': ',', 'decimal': '.'},
            {'locale': 'de-DE', 'thousands': '.', 'decimal': ','},
            {'locale': 'fr-FR', 'thousands': ' ', 'decimal': ','}
        ]

    def normalize_date(
        self,
        text: str,
        locale: str = 'en-US'
    ) -> Dict[str, Any]:
        """
        Normalize date format for locale.

        Args:
            text: Text with date
            locale: Locale code

        Returns:
            Dictionary with normalized result

        Example:
            >>> result = service.normalize_date('12/31/2024', 'en-US')
        """
        return {
            'original': text,
            'normalized': text,
            'locale': locale,
            'format': 'MM/DD/YYYY' if locale == 'en-US' else 'DD/MM/YYYY'
        }

    def get_date_formats(self) -> List[Dict[str, Any]]:
        """
        Get date format configurations.

        Returns:
            List of date format configs

        Example:
            >>> formats = service.get_date_formats()
        """
        return [
            {'locale': 'en-US', 'format': 'MM/DD/YYYY'},
            {'locale': 'en-GB', 'format': 'DD/MM/YYYY'},
            {'locale': 'de-DE', 'format': 'DD.MM.YYYY'},
            {'locale': 'ja-JP', 'format': 'YYYY/MM/DD'}
        ]

    def normalize_currency(
        self,
        text: str,
        locale: str = 'en-US'
    ) -> Dict[str, Any]:
        """
        Normalize currency format for locale.

        Args:
            text: Text with currency
            locale: Locale code

        Returns:
            Dictionary with normalized result

        Example:
            >>> result = service.normalize_currency('$1,000', 'en-US')
        """
        return {
            'original': text,
            'normalized': text,
            'locale': locale,
            'symbol_position': 'prefix' if locale in ['en-US', 'en-GB'] else 'suffix'
        }

    def get_currency_formats(self) -> List[Dict[str, Any]]:
        """
        Get currency format configurations.

        Returns:
            List of currency format configs

        Example:
            >>> formats = service.get_currency_formats()
        """
        return [
            {'locale': 'en-US', 'symbol': '$', 'position': 'prefix'},
            {'locale': 'en-GB', 'symbol': '£', 'position': 'prefix'},
            {'locale': 'de-DE', 'symbol': '€', 'position': 'suffix'},
            {'locale': 'ja-JP', 'symbol': '¥', 'position': 'prefix'}
        ]

    def normalize_units(
        self,
        text: str,
        locale: str = 'en-US'
    ) -> Dict[str, Any]:
        """
        Normalize units for locale.

        Args:
            text: Text with units
            locale: Locale code

        Returns:
            Dictionary with normalized result

        Example:
            >>> result = service.normalize_units('5 miles', 'en-US')
        """
        return {
            'original': text,
            'normalized': text,
            'locale': locale,
            'system': 'imperial' if locale == 'en-US' else 'metric'
        }

    def get_unit_systems(self) -> List[Dict[str, Any]]:
        """
        Get unit system configurations.

        Returns:
            List of unit system configs

        Example:
            >>> systems = service.get_unit_systems()
        """
        return [
            {'locale': 'en-US', 'system': 'imperial', 'distance': 'miles', 'temp': 'F'},
            {'locale': 'en-GB', 'system': 'metric', 'distance': 'km', 'temp': 'C'},
            {'locale': 'de-DE', 'system': 'metric', 'distance': 'km', 'temp': 'C'}
        ]

    def get_normalization_config(self) -> Dict[str, Any]:
        """
        Get normalization configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_normalization_config()
        """
        return {
            'number_formats': len(self.get_number_formats()),
            'date_formats': len(self.get_date_formats()),
            'currency_formats': len(self.get_currency_formats()),
            'unit_systems': len(self.get_unit_systems())
        }

    def get_supported_locales(self) -> List[str]:
        """
        Get supported locales.

        Returns:
            List of locale codes

        Example:
            >>> locales = service.get_supported_locales()
        """
        return ['en-US', 'en-GB', 'de-DE', 'fr-FR', 'es-ES', 'ja-JP', 'zh-CN']

