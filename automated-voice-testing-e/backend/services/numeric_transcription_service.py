"""
Numeric Transcription Service for ASR analysis.

This service provides methods for analyzing numeric and alphanumeric content
in ASR transcriptions. Numeric data (phone numbers, addresses, serial numbers)
is particularly challenging for ASR systems because numbers can be spoken in
various formats and may include letter-number combinations.

Supported numeric types:
- Phone numbers: Various formats (555-1234, (555) 555-1234, etc.)
- Addresses: Street addresses with numbers and abbreviations
- Alphanumeric sequences: License plates, serial numbers, confirmation codes
- General numeric patterns: Dates, times, currency, percentages

Example:
    >>> service = NumericTranscriptionService()
    >>> phones = service.extract_phone_numbers("Call me at 555-123-4567")
    >>> print(phones)
    ['555-123-4567']
"""

from typing import List, Dict, Any
import re


class NumericTranscriptionService:
    """
    Service for numeric and alphanumeric transcription analysis.

    Provides methods for extracting numeric patterns, calculating accuracy
    metrics, and normalizing numeric representations between spoken and
    written forms.

    Attributes:
        phone_patterns: Regex patterns for phone number detection
        address_patterns: Patterns for address recognition

    Example:
        >>> service = NumericTranscriptionService()
        >>> metrics = service.get_numeric_metrics(
        ...     "Call 555-1234 at 123 Main St",
        ...     "Call 555-1235 at 123 Main Street"
        ... )
        >>> print(f"Phone accuracy: {metrics['phone_accuracy']:.2f}")
    """

    # Common word-to-digit mappings
    WORD_TO_DIGIT = {
        'zero': '0', 'one': '1', 'two': '2', 'three': '3', 'four': '4',
        'five': '5', 'six': '6', 'seven': '7', 'eight': '8', 'nine': '9',
        'ten': '10', 'eleven': '11', 'twelve': '12', 'thirteen': '13',
        'fourteen': '14', 'fifteen': '15', 'sixteen': '16', 'seventeen': '17',
        'eighteen': '18', 'nineteen': '19', 'twenty': '20', 'thirty': '30',
        'forty': '40', 'fifty': '50', 'sixty': '60', 'seventy': '70',
        'eighty': '80', 'ninety': '90', 'hundred': '100', 'thousand': '1000'
    }

    # Digit to word mappings
    DIGIT_TO_WORD = {v: k for k, v in WORD_TO_DIGIT.items() if len(v) == 1}

    def __init__(self):
        """Initialize the numeric transcription service."""
        # Phone number patterns
        self.phone_patterns = [
            r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',  # 555-123-4567
            r'\b\(\d{3}\)\s*\d{3}[-.\s]?\d{4}\b',   # (555) 123-4567
            r'\b\d{3}[-.\s]?\d{4}\b',               # 555-1234
            r'\b1[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',  # 1-555-123-4567
        ]

        # Address patterns
        self.address_patterns = [
            r'\b\d+\s+[A-Za-z]+\s+(Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Court|Ct|Way|Place|Pl)\b',
            r'\b\d+\s+[A-Za-z]+\s+[A-Za-z]+\s+(Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Court|Ct|Way|Place|Pl)\b',
        ]

        # Alphanumeric patterns (license plates, serial numbers, etc.)
        self.alphanumeric_patterns = [
            r'\b[A-Z]{2,3}[-\s]?\d{3,4}\b',        # ABC-1234 (license plate)
            r'\b\d{3,4}[-\s]?[A-Z]{2,3}\b',        # 1234-ABC
            r'\b[A-Z0-9]{6,12}\b',                  # Serial numbers
        ]

    def extract_phone_numbers(self, text: str) -> List[str]:
        """
        Extract phone numbers from text.

        Args:
            text: Input text to analyze

        Returns:
            List of phone number strings found

        Example:
            >>> phones = service.extract_phone_numbers("Call 555-123-4567")
            >>> print(phones)
            ['555-123-4567']
        """
        if not text:
            return []

        phone_numbers = []
        for pattern in self.phone_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            phone_numbers.extend(matches)

        # Remove duplicates while preserving order
        seen = set()
        unique_phones = []
        for phone in phone_numbers:
            normalized = re.sub(r'[\s\-\.\(\)]', '', phone)
            if normalized not in seen:
                seen.add(normalized)
                unique_phones.append(phone)

        return unique_phones

    def calculate_phone_accuracy(
        self,
        reference: str,
        hypothesis: str
    ) -> Dict[str, Any]:
        """
        Calculate phone number transcription accuracy.

        Args:
            reference: Reference transcription
            hypothesis: Hypothesis transcription

        Returns:
            Dictionary with accuracy metrics

        Example:
            >>> metrics = service.calculate_phone_accuracy(
            ...     "Call 555-123-4567",
            ...     "Call 555-123-4568"
            ... )
            >>> print(f"Accuracy: {metrics['accuracy']:.2f}")
        """
        ref_phones = self.extract_phone_numbers(reference)
        hyp_phones = self.extract_phone_numbers(hypothesis)

        if not ref_phones and not hyp_phones:
            return {
                'accuracy': 1.0,
                'total': 0,
                'correct': 0,
                'digit_accuracy': 1.0
            }

        # Normalize phone numbers for comparison
        ref_normalized = [re.sub(r'[\s\-\.\(\)]', '', p) for p in ref_phones]
        hyp_normalized = [re.sub(r'[\s\-\.\(\)]', '', p) for p in hyp_phones]

        correct = 0
        total_digits = 0
        correct_digits = 0

        for i, ref_phone in enumerate(ref_normalized):
            total_digits += len(ref_phone)

            if i < len(hyp_normalized):
                hyp_phone = hyp_normalized[i]
                if ref_phone == hyp_phone:
                    correct += 1
                    correct_digits += len(ref_phone)
                else:
                    # Count matching digits
                    for j, digit in enumerate(ref_phone):
                        if j < len(hyp_phone) and hyp_phone[j] == digit:
                            correct_digits += 1

        accuracy = correct / len(ref_normalized) if ref_normalized else 0.0
        digit_accuracy = correct_digits / total_digits if total_digits > 0 else 0.0

        return {
            'accuracy': accuracy,
            'total': len(ref_normalized),
            'correct': correct,
            'digit_accuracy': digit_accuracy
        }

    def extract_addresses(self, text: str) -> List[str]:
        """
        Extract street addresses from text.

        Args:
            text: Input text to analyze

        Returns:
            List of address strings found

        Example:
            >>> addresses = service.extract_addresses("Meet at 123 Main Street")
            >>> print(addresses)
            ['123 Main Street']
        """
        if not text:
            return []

        addresses = []
        for pattern in self.address_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            # findall returns tuples when there are groups, get full match
            if matches:
                full_matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in full_matches:
                    addresses.append(match.group())

        # Remove duplicates
        seen = set()
        unique_addresses = []
        for addr in addresses:
            normalized = addr.lower().strip()
            if normalized not in seen:
                seen.add(normalized)
                unique_addresses.append(addr)

        return unique_addresses

    def calculate_address_accuracy(
        self,
        reference: str,
        hypothesis: str
    ) -> Dict[str, Any]:
        """
        Calculate address transcription accuracy.

        Args:
            reference: Reference transcription
            hypothesis: Hypothesis transcription

        Returns:
            Dictionary with accuracy metrics

        Example:
            >>> metrics = service.calculate_address_accuracy(
            ...     "Meet at 123 Main Street",
            ...     "Meet at 123 Main St"
            ... )
        """
        ref_addresses = self.extract_addresses(reference)
        hyp_addresses = self.extract_addresses(hypothesis)

        if not ref_addresses and not hyp_addresses:
            return {
                'accuracy': 1.0,
                'total': 0,
                'correct': 0
            }

        correct = 0
        for i, ref_addr in enumerate(ref_addresses):
            if i < len(hyp_addresses):
                # Normalize for comparison
                ref_norm = self._normalize_address(ref_addr)
                hyp_norm = self._normalize_address(hyp_addresses[i])
                if ref_norm == hyp_norm:
                    correct += 1

        accuracy = correct / len(ref_addresses) if ref_addresses else 0.0

        return {
            'accuracy': accuracy,
            'total': len(ref_addresses),
            'correct': correct
        }

    def _normalize_address(self, address: str) -> str:
        """Normalize address for comparison."""
        # Common abbreviations
        replacements = {
            'street': 'st', 'avenue': 'ave', 'road': 'rd',
            'boulevard': 'blvd', 'drive': 'dr', 'lane': 'ln',
            'court': 'ct', 'place': 'pl'
        }

        normalized = address.lower().strip()
        for full, abbrev in replacements.items():
            normalized = normalized.replace(full, abbrev)

        return normalized

    def extract_alphanumeric(self, text: str) -> List[str]:
        """
        Extract alphanumeric sequences from text.

        Finds license plates, serial numbers, confirmation codes, etc.

        Args:
            text: Input text to analyze

        Returns:
            List of alphanumeric sequences found

        Example:
            >>> sequences = service.extract_alphanumeric("License plate ABC-1234")
            >>> print(sequences)
            ['ABC-1234']
        """
        if not text:
            return []

        sequences = []
        for pattern in self.alphanumeric_patterns:
            matches = re.findall(pattern, text.upper())
            sequences.extend(matches)

        # Remove duplicates
        seen = set()
        unique_sequences = []
        for seq in sequences:
            normalized = re.sub(r'[\s\-]', '', seq)
            if normalized not in seen:
                seen.add(normalized)
                unique_sequences.append(seq)

        return unique_sequences

    def calculate_alphanumeric_accuracy(
        self,
        reference: str,
        hypothesis: str
    ) -> Dict[str, Any]:
        """
        Calculate alphanumeric sequence accuracy.

        Args:
            reference: Reference transcription
            hypothesis: Hypothesis transcription

        Returns:
            Dictionary with accuracy metrics

        Example:
            >>> metrics = service.calculate_alphanumeric_accuracy(
            ...     "Code is ABC123",
            ...     "Code is ABC124"
            ... )
        """
        ref_sequences = self.extract_alphanumeric(reference)
        hyp_sequences = self.extract_alphanumeric(hypothesis)

        if not ref_sequences and not hyp_sequences:
            return {
                'accuracy': 1.0,
                'total': 0,
                'correct': 0
            }

        # Normalize for comparison
        ref_normalized = [re.sub(r'[\s\-]', '', s) for s in ref_sequences]
        hyp_normalized = [re.sub(r'[\s\-]', '', s) for s in hyp_sequences]

        correct = 0
        for i, ref_seq in enumerate(ref_normalized):
            if i < len(hyp_normalized) and ref_seq == hyp_normalized[i]:
                correct += 1

        accuracy = correct / len(ref_normalized) if ref_normalized else 0.0

        return {
            'accuracy': accuracy,
            'total': len(ref_normalized),
            'correct': correct
        }

    def detect_numeric_patterns(self, text: str) -> List[Dict[str, Any]]:
        """
        Detect all numeric patterns in text.

        Args:
            text: Input text to analyze

        Returns:
            List of pattern dictionaries with 'type', 'value', and 'position'

        Example:
            >>> patterns = service.detect_numeric_patterns("Call 555-1234")
            >>> print(patterns[0]['type'])
            'phone'
        """
        if not text:
            return []

        patterns = []

        # Detect phone numbers
        for phone in self.extract_phone_numbers(text):
            match = re.search(re.escape(phone), text)
            if match:
                patterns.append({
                    'type': 'phone',
                    'value': phone,
                    'position': match.start()
                })

        # Detect addresses
        for address in self.extract_addresses(text):
            match = re.search(re.escape(address), text)
            if match:
                patterns.append({
                    'type': 'address',
                    'value': address,
                    'position': match.start()
                })

        # Detect alphanumeric sequences
        for seq in self.extract_alphanumeric(text):
            match = re.search(re.escape(seq), text, re.IGNORECASE)
            if match:
                patterns.append({
                    'type': 'alphanumeric',
                    'value': seq,
                    'position': match.start()
                })

        # Detect standalone numbers
        number_pattern = r'\b\d+(?:\.\d+)?\b'
        for match in re.finditer(number_pattern, text):
            # Skip if already captured as part of another pattern
            already_captured = any(
                p['position'] <= match.start() < p['position'] + len(p['value'])
                for p in patterns
            )
            if not already_captured:
                patterns.append({
                    'type': 'number',
                    'value': match.group(),
                    'position': match.start()
                })

        # Sort by position
        patterns.sort(key=lambda x: x['position'])

        return patterns

    def normalize_numeric(self, text: str) -> str:
        """
        Normalize numeric text between word and digit forms.

        Converts word numbers to digits for consistent comparison.

        Args:
            text: Input text to normalize

        Returns:
            Normalized text with consistent numeric representation

        Example:
            >>> normalized = service.normalize_numeric("five five five")
            >>> print(normalized)
            '5 5 5'
        """
        if not text:
            return ''

        words = text.lower().split()
        result = []

        for word in words:
            # Clean punctuation
            clean_word = re.sub(r'[^\w]', '', word)

            if clean_word in self.WORD_TO_DIGIT:
                result.append(self.WORD_TO_DIGIT[clean_word])
            else:
                result.append(word)

        return ' '.join(result)

    def calculate_digit_accuracy(
        self,
        reference: str,
        hypothesis: str
    ) -> Dict[str, Any]:
        """
        Calculate digit-by-digit accuracy.

        Args:
            reference: Reference transcription
            hypothesis: Hypothesis transcription

        Returns:
            Dictionary with digit accuracy metrics

        Example:
            >>> metrics = service.calculate_digit_accuracy("1234", "1235")
            >>> print(f"Accuracy: {metrics['accuracy']:.2f}")
        """
        # Extract only digits
        ref_digits = re.findall(r'\d', reference)
        hyp_digits = re.findall(r'\d', hypothesis)

        if not ref_digits and not hyp_digits:
            return {
                'accuracy': 1.0,
                'total': 0,
                'correct': 0,
                'insertions': 0,
                'deletions': 0,
                'substitutions': 0
            }

        # Count correct digits at same positions
        correct = 0
        substitutions = 0
        min_len = min(len(ref_digits), len(hyp_digits))

        for i in range(min_len):
            if ref_digits[i] == hyp_digits[i]:
                correct += 1
            else:
                substitutions += 1

        insertions = max(0, len(hyp_digits) - len(ref_digits))
        deletions = max(0, len(ref_digits) - len(hyp_digits))

        accuracy = correct / len(ref_digits) if ref_digits else 0.0

        return {
            'accuracy': accuracy,
            'total': len(ref_digits),
            'correct': correct,
            'insertions': insertions,
            'deletions': deletions,
            'substitutions': substitutions
        }

    def get_numeric_metrics(
        self,
        reference: str,
        hypothesis: str
    ) -> Dict[str, Any]:
        """
        Get comprehensive numeric transcription metrics.

        Args:
            reference: Reference transcription
            hypothesis: Hypothesis transcription

        Returns:
            Dictionary with all numeric accuracy metrics

        Example:
            >>> metrics = service.get_numeric_metrics(
            ...     "Call 555-1234 at 123 Main St",
            ...     "Call 555-1235 at 123 Main Street"
            ... )
            >>> print(f"Overall accuracy: {metrics['accuracy']:.2f}")
        """
        phone_metrics = self.calculate_phone_accuracy(reference, hypothesis)
        address_metrics = self.calculate_address_accuracy(reference, hypothesis)
        alphanumeric_metrics = self.calculate_alphanumeric_accuracy(
            reference, hypothesis
        )
        digit_metrics = self.calculate_digit_accuracy(reference, hypothesis)

        # Calculate overall accuracy
        total_items = (
            phone_metrics['total'] +
            address_metrics['total'] +
            alphanumeric_metrics['total']
        )
        correct_items = (
            phone_metrics['correct'] +
            address_metrics['correct'] +
            alphanumeric_metrics['correct']
        )

        overall_accuracy = correct_items / total_items if total_items > 0 else 1.0

        # Detect patterns in both texts
        ref_patterns = self.detect_numeric_patterns(reference)
        hyp_patterns = self.detect_numeric_patterns(hypothesis)

        return {
            'accuracy': overall_accuracy,
            'phone_accuracy': phone_metrics['accuracy'],
            'address_accuracy': address_metrics['accuracy'],
            'alphanumeric_accuracy': alphanumeric_metrics['accuracy'],
            'digit_accuracy': digit_metrics['accuracy'],
            'phone_metrics': phone_metrics,
            'address_metrics': address_metrics,
            'alphanumeric_metrics': alphanumeric_metrics,
            'digit_metrics': digit_metrics,
            'reference_patterns': ref_patterns,
            'hypothesis_patterns': hyp_patterns
        }
