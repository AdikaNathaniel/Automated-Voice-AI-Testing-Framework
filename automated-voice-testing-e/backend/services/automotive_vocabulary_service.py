"""
Automotive Vocabulary Service for voice AI testing.

This service provides automotive-specific vocabulary handling
including regional terminology, units, and format variations.

Key features:
- Car terminology variations (UK vs US English)
- Measurement units (miles vs kilometers)
- Temperature units (Fahrenheit vs Celsius)
- Address format variations
- Phone number formats

Example:
    >>> service = AutomotiveVocabularyService()
    >>> translated = service.translate_terminology('trunk', 'en-GB')
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import re


class AutomotiveVocabularyService:
    """
    Service for automotive vocabulary and localization.

    Provides tools for handling regional terminology differences,
    unit conversions, and format variations across markets.

    Example:
        >>> service = AutomotiveVocabularyService()
        >>> config = service.get_vocabulary_config()
    """

    def __init__(self):
        """Initialize the automotive vocabulary service."""
        # US to UK terminology mappings
        self._us_to_uk = {
            'trunk': 'boot',
            'hood': 'bonnet',
            'gas': 'petrol',
            'gasoline': 'petrol',
            'fender': 'wing',
            'windshield': 'windscreen',
            'turn signal': 'indicator',
            'parking lot': 'car park',
            'freeway': 'motorway',
            'highway': 'motorway',
            'sidewalk': 'pavement',
            'sedan': 'saloon',
            'station wagon': 'estate',
            'stick shift': 'manual',
            'transmission': 'gearbox'
        }

        # UK to US (reverse mapping)
        self._uk_to_us = {v: k for k, v in self._us_to_uk.items()}

        # Phone format patterns by region
        self._phone_patterns = {
            'US': r'^\+?1?\s*\(?(\d{3})\)?[-.\s]*(\d{3})[-.\s]*(\d{4})$',
            'UK': r'^\+?44?\s*\(?0?(\d{2,5})\)?[-.\s]*(\d{3,4})[-.\s]*(\d{3,4})$',
            'DE': r'^\+?49?\s*\(?0?(\d{2,5})\)?[-.\s]*(\d+)$'
        }

    def translate_terminology(
        self,
        term: str,
        target_dialect: str
    ) -> Dict[str, Any]:
        """
        Translate automotive terminology between dialects.

        Args:
            term: Term to translate
            target_dialect: Target dialect (en-US, en-GB)

        Returns:
            Dictionary with translation result

        Example:
            >>> result = service.translate_terminology('trunk', 'en-GB')
        """
        translation_id = str(uuid.uuid4())

        term_lower = term.lower()
        translated = term
        found = False

        if target_dialect == 'en-GB':
            if term_lower in self._us_to_uk:
                translated = self._us_to_uk[term_lower]
                found = True
        elif target_dialect == 'en-US':
            if term_lower in self._uk_to_us:
                translated = self._uk_to_us[term_lower]
                found = True

        return {
            'translation_id': translation_id,
            'original_term': term,
            'translated_term': translated,
            'target_dialect': target_dialect,
            'found': found,
            'translated_at': datetime.utcnow().isoformat()
        }

    def get_regional_terms(
        self,
        region: str,
        category: Optional[str] = None,
        filters: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get automotive terms for a specific region.

        Args:
            region: Region code (US, UK, DE, etc.)
            category: Optional category filter

        Returns:
            Dictionary with regional terms

        Example:
            >>> terms = service.get_regional_terms('UK')
        """
        query_id = str(uuid.uuid4())

        if region in ['UK', 'GB', 'en-GB']:
            terms = list(self._us_to_uk.values())
            dialect = 'en-GB'
        else:
            terms = list(self._us_to_uk.keys())
            dialect = 'en-US'

        return {
            'query_id': query_id,
            'region': region,
            'dialect': dialect,
            'terms': terms,
            'term_count': len(terms),
            'category': category,
            'queried_at': datetime.utcnow().isoformat()
        }

    def detect_dialect(
        self,
        text: str
    ) -> Dict[str, Any]:
        """
        Detect dialect from automotive terminology in text.

        Args:
            text: Text to analyze

        Returns:
            Dictionary with detection result

        Example:
            >>> result = service.detect_dialect('Open the boot')
        """
        detection_id = str(uuid.uuid4())

        text_lower = text.lower()
        us_matches = []
        uk_matches = []

        for us_term, uk_term in self._us_to_uk.items():
            if us_term in text_lower:
                us_matches.append(us_term)
            if uk_term in text_lower:
                uk_matches.append(uk_term)

        if uk_matches and not us_matches:
            detected = 'en-GB'
            confidence = min(0.9, 0.5 + len(uk_matches) * 0.1)
        elif us_matches and not uk_matches:
            detected = 'en-US'
            confidence = min(0.9, 0.5 + len(us_matches) * 0.1)
        elif uk_matches and us_matches:
            detected = 'mixed'
            confidence = 0.5
        else:
            detected = 'unknown'
            confidence = 0.0

        return {
            'detection_id': detection_id,
            'text': text,
            'detected_dialect': detected,
            'confidence': confidence,
            'us_terms_found': us_matches,
            'uk_terms_found': uk_matches,
            'detected_at': datetime.utcnow().isoformat()
        }

    def convert_distance(
        self,
        value: float,
        from_unit: str,
        to_unit: str
    ) -> Dict[str, Any]:
        """
        Convert distance between units.

        Args:
            value: Distance value
            from_unit: Source unit (miles, km, m, ft)
            to_unit: Target unit

        Returns:
            Dictionary with conversion result

        Example:
            >>> result = service.convert_distance(10, 'miles', 'km')
        """
        conversion_id = str(uuid.uuid4())

        # Convert to meters first
        to_meters = {
            'miles': 1609.344,
            'km': 1000,
            'kilometers': 1000,
            'm': 1,
            'meters': 1,
            'ft': 0.3048,
            'feet': 0.3048,
            'yards': 0.9144
        }

        from_meters = {
            'miles': 1 / 1609.344,
            'km': 1 / 1000,
            'kilometers': 1 / 1000,
            'm': 1,
            'meters': 1,
            'ft': 1 / 0.3048,
            'feet': 1 / 0.3048,
            'yards': 1 / 0.9144
        }

        if from_unit.lower() not in to_meters or to_unit.lower() not in from_meters:
            return {
                'conversion_id': conversion_id,
                'success': False,
                'error': 'Invalid unit',
                'converted_at': datetime.utcnow().isoformat()
            }

        meters = value * to_meters[from_unit.lower()]
        converted = meters * from_meters[to_unit.lower()]

        return {
            'conversion_id': conversion_id,
            'original_value': value,
            'original_unit': from_unit,
            'converted_value': round(converted, 2),
            'converted_unit': to_unit,
            'success': True,
            'converted_at': datetime.utcnow().isoformat()
        }

    def format_distance(
        self,
        value: float,
        unit: str,
        region: str
    ) -> Dict[str, Any]:
        """
        Format distance for display in a specific region.

        Args:
            value: Distance value
            unit: Unit of the value
            region: Target region

        Returns:
            Dictionary with formatted distance

        Example:
            >>> result = service.format_distance(10, 'km', 'US')
        """
        format_id = str(uuid.uuid4())

        # Determine target unit based on region
        imperial_regions = ['US']

        if region in imperial_regions:
            target_unit = 'miles'
            if unit.lower() in ['km', 'kilometers', 'm', 'meters']:
                converted = self.convert_distance(value, unit, 'miles')
                display_value = converted['converted_value']
            else:
                display_value = value
            formatted = f"{display_value} mi"
        else:
            target_unit = 'km'
            if unit.lower() in ['miles', 'ft', 'feet']:
                converted = self.convert_distance(value, unit, 'km')
                display_value = converted['converted_value']
            else:
                display_value = value
            formatted = f"{display_value} km"

        return {
            'format_id': format_id,
            'original_value': value,
            'original_unit': unit,
            'region': region,
            'formatted': formatted,
            'target_unit': target_unit,
            'formatted_at': datetime.utcnow().isoformat()
        }

    def convert_temperature(
        self,
        value: float,
        from_unit: str,
        to_unit: str
    ) -> Dict[str, Any]:
        """
        Convert temperature between units.

        Args:
            value: Temperature value
            from_unit: Source unit (F, C, K)
            to_unit: Target unit

        Returns:
            Dictionary with conversion result

        Example:
            >>> result = service.convert_temperature(72, 'F', 'C')
        """
        conversion_id = str(uuid.uuid4())

        from_unit = from_unit.upper()
        to_unit = to_unit.upper()

        # Convert to Celsius first
        if from_unit == 'F':
            celsius = (value - 32) * 5 / 9
        elif from_unit == 'K':
            celsius = value - 273.15
        elif from_unit == 'C':
            celsius = value
        else:
            return {
                'conversion_id': conversion_id,
                'success': False,
                'error': 'Invalid from_unit',
                'converted_at': datetime.utcnow().isoformat()
            }

        # Convert from Celsius to target
        if to_unit == 'F':
            converted = celsius * 9 / 5 + 32
        elif to_unit == 'K':
            converted = celsius + 273.15
        elif to_unit == 'C':
            converted = celsius
        else:
            return {
                'conversion_id': conversion_id,
                'success': False,
                'error': 'Invalid to_unit',
                'converted_at': datetime.utcnow().isoformat()
            }

        return {
            'conversion_id': conversion_id,
            'original_value': value,
            'original_unit': from_unit,
            'converted_value': round(converted, 1),
            'converted_unit': to_unit,
            'success': True,
            'converted_at': datetime.utcnow().isoformat()
        }

    def format_temperature(
        self,
        value: float,
        unit: str,
        region: str
    ) -> Dict[str, Any]:
        """
        Format temperature for display in a specific region.

        Args:
            value: Temperature value
            unit: Unit of the value
            region: Target region

        Returns:
            Dictionary with formatted temperature

        Example:
            >>> result = service.format_temperature(22, 'C', 'US')
        """
        format_id = str(uuid.uuid4())

        # US uses Fahrenheit, most others use Celsius
        fahrenheit_regions = ['US']

        if region in fahrenheit_regions:
            target_unit = 'F'
            if unit.upper() != 'F':
                converted = self.convert_temperature(value, unit, 'F')
                display_value = converted['converted_value']
            else:
                display_value = value
            formatted = f"{display_value}°F"
        else:
            target_unit = 'C'
            if unit.upper() != 'C':
                converted = self.convert_temperature(value, unit, 'C')
                display_value = converted['converted_value']
            else:
                display_value = value
            formatted = f"{display_value}°C"

        return {
            'format_id': format_id,
            'original_value': value,
            'original_unit': unit,
            'region': region,
            'formatted': formatted,
            'target_unit': target_unit,
            'formatted_at': datetime.utcnow().isoformat()
        }

    def format_address(
        self,
        address_parts: Dict[str, str],
        region: str
    ) -> Dict[str, Any]:
        """
        Format address according to regional conventions.

        Args:
            address_parts: Address components
            region: Target region

        Returns:
            Dictionary with formatted address

        Example:
            >>> result = service.format_address({'street': '123 Main St', 'city': 'Boston'}, 'US')
        """
        format_id = str(uuid.uuid4())

        street = address_parts.get('street', '')
        city = address_parts.get('city', '')
        state = address_parts.get('state', '')
        postal_code = address_parts.get('postal_code', '')
        country = address_parts.get('country', '')

        if region == 'US':
            # US format: Street, City, State ZIP
            parts = [street, f"{city}, {state} {postal_code}".strip()]
        elif region in ['UK', 'GB']:
            # UK format: Street, City, Postal Code
            parts = [street, city, postal_code]
        elif region == 'DE':
            # German format: Street, Postal Code City
            parts = [street, f"{postal_code} {city}".strip()]
        elif region == 'JP':
            # Japanese format: Postal Code, Prefecture, City, Street
            parts = [postal_code, state, city, street]
        else:
            parts = [street, city, state, postal_code, country]

        formatted = ', '.join(p for p in parts if p)

        return {
            'format_id': format_id,
            'original_parts': address_parts,
            'region': region,
            'formatted': formatted,
            'formatted_at': datetime.utcnow().isoformat()
        }

    def parse_address(
        self,
        address: str,
        region: str
    ) -> Dict[str, Any]:
        """
        Parse address string into components.

        Args:
            address: Address string
            region: Region hint for parsing

        Returns:
            Dictionary with parsed components

        Example:
            >>> result = service.parse_address('123 Main St, Boston, MA 02101', 'US')
        """
        parse_id = str(uuid.uuid4())

        parts = [p.strip() for p in address.split(',')]

        parsed = {
            'street': parts[0] if len(parts) > 0 else '',
            'city': '',
            'state': '',
            'postal_code': '',
            'country': ''
        }

        if region == 'US' and len(parts) >= 2:
            # Parse "City, State ZIP"
            city_state_zip = parts[1] if len(parts) > 1 else ''
            match = re.match(r'([^,]+),?\s*([A-Z]{2})?\s*(\d{5})?', city_state_zip.strip())
            if match:
                parsed['city'] = match.group(1).strip() if match.group(1) else ''
                parsed['state'] = match.group(2) or ''
                parsed['postal_code'] = match.group(3) or ''
        elif len(parts) >= 2:
            parsed['city'] = parts[1]
            if len(parts) >= 3:
                parsed['postal_code'] = parts[2]

        return {
            'parse_id': parse_id,
            'original_address': address,
            'region': region,
            'parsed': parsed,
            'parsed_at': datetime.utcnow().isoformat()
        }

    def format_phone_number(
        self,
        phone: str,
        region: str
    ) -> Dict[str, Any]:
        """
        Format phone number according to regional conventions.

        Args:
            phone: Phone number to format
            region: Target region

        Returns:
            Dictionary with formatted phone number

        Example:
            >>> result = service.format_phone_number('6175551234', 'US')
        """
        format_id = str(uuid.uuid4())

        # Remove non-digits
        digits = re.sub(r'\D', '', phone)

        if region == 'US':
            if len(digits) == 10:
                formatted = f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
            elif len(digits) == 11 and digits[0] == '1':
                formatted = f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
            else:
                formatted = phone
        elif region in ['UK', 'GB']:
            if len(digits) >= 10:
                formatted = f"+44 {digits[-10:-7]} {digits[-7:-4]} {digits[-4:]}"
            else:
                formatted = phone
        elif region == 'DE':
            formatted = f"+49 {digits}"
        else:
            formatted = phone

        return {
            'format_id': format_id,
            'original': phone,
            'formatted': formatted,
            'region': region,
            'formatted_at': datetime.utcnow().isoformat()
        }

    def validate_phone_number(
        self,
        phone: str,
        region: str
    ) -> Dict[str, Any]:
        """
        Validate phone number for a region.

        Args:
            phone: Phone number to validate
            region: Region to validate against

        Returns:
            Dictionary with validation result

        Example:
            >>> result = service.validate_phone_number('617-555-1234', 'US')
        """
        validation_id = str(uuid.uuid4())

        pattern = self._phone_patterns.get(region)

        if not pattern:
            return {
                'validation_id': validation_id,
                'phone': phone,
                'region': region,
                'valid': False,
                'error': 'Region not supported',
                'validated_at': datetime.utcnow().isoformat()
            }

        match = re.match(pattern, phone)

        return {
            'validation_id': validation_id,
            'phone': phone,
            'region': region,
            'valid': bool(match),
            'pattern_used': pattern,
            'validated_at': datetime.utcnow().isoformat()
        }

    def get_vocabulary_config(self) -> Dict[str, Any]:
        """
        Get vocabulary service configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_vocabulary_config()
        """
        return {
            'supported_dialects': ['en-US', 'en-GB'],
            'terminology_count': len(self._us_to_uk),
            'supported_distance_units': ['miles', 'km', 'm', 'ft', 'yards'],
            'supported_temperature_units': ['F', 'C', 'K'],
            'supported_phone_regions': list(self._phone_patterns.keys()),
            'features': [
                'terminology_translation', 'dialect_detection',
                'distance_conversion', 'temperature_conversion',
                'address_formatting', 'phone_formatting'
            ]
        }
