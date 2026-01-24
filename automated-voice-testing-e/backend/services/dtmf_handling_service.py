"""
DTMF Handling Service for voice testing.

This service provides DTMF (Dual-Tone Multi-Frequency)
generation and detection for voice AI testing.

Key features:
- DTMF tone generation
- DTMF detection
- Tone duration control
- RFC 2833 support

Example:
    >>> service = DTMFHandlingService()
    >>> tone = service.generate_tone('5')
    >>> service.generate_sequence('1234#')
"""

from typing import List, Dict, Any
from datetime import datetime


class DTMFHandlingService:
    """
    Service for DTMF tone handling.

    Provides tone generation, detection, duration control,
    and RFC 2833 RTP event support.

    Example:
        >>> service = DTMFHandlingService()
        >>> frequencies = service.get_tone_frequencies('9')
        >>> print(f"Low: {frequencies['low_freq']} Hz")
    """

    def __init__(self):
        """Initialize the DTMF handling service."""
        self._tone_duration_ms = 100
        self._inter_digit_gap_ms = 50
        self._payload_type = 101
        self._detecting = False
        self._detected_digits: List[Dict[str, Any]] = []
        self._mode = 'inband'  # 'inband' or 'outofband'

        # DTMF frequency matrix
        self._freq_matrix = {
            '1': (697, 1209), '2': (697, 1336), '3': (697, 1477), 'A': (697, 1633),
            '4': (770, 1209), '5': (770, 1336), '6': (770, 1477), 'B': (770, 1633),
            '7': (852, 1209), '8': (852, 1336), '9': (852, 1477), 'C': (852, 1633),
            '*': (941, 1209), '0': (941, 1336), '#': (941, 1477), 'D': (941, 1633)
        }

        # RFC 2833 event codes
        self._event_codes = {
            '0': 0, '1': 1, '2': 2, '3': 3, '4': 4,
            '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
            '*': 10, '#': 11, 'A': 12, 'B': 13, 'C': 14, 'D': 15
        }

    def generate_tone(
        self,
        digit: str,
        duration_ms: int = None
    ) -> Dict[str, Any]:
        """
        Generate DTMF tone for a digit.

        Args:
            digit: DTMF digit (0-9, *, #, A-D)
            duration_ms: Optional tone duration

        Returns:
            Dictionary with tone information

        Example:
            >>> tone = service.generate_tone('5')
        """
        if not self.is_valid_digit(digit):
            return {'error': 'Invalid DTMF digit'}

        duration = duration_ms or self._tone_duration_ms
        frequencies = self._freq_matrix.get(digit, (0, 0))

        return {
            'digit': digit,
            'low_freq': frequencies[0],
            'high_freq': frequencies[1],
            'duration_ms': duration,
            'generated_at': datetime.utcnow().isoformat()
        }

    def generate_sequence(
        self,
        digits: str,
        duration_ms: int = None,
        gap_ms: int = None
    ) -> Dict[str, Any]:
        """
        Generate DTMF tone sequence.

        Args:
            digits: String of DTMF digits
            duration_ms: Optional tone duration
            gap_ms: Optional inter-digit gap

        Returns:
            Dictionary with sequence information

        Example:
            >>> sequence = service.generate_sequence('1234#')
        """
        duration = duration_ms or self._tone_duration_ms
        gap = gap_ms or self._inter_digit_gap_ms

        tones = []
        for digit in digits:
            if self.is_valid_digit(digit):
                tones.append(self.generate_tone(digit, duration))

        total_duration = len(tones) * duration + (len(tones) - 1) * gap

        return {
            'digits': digits,
            'tone_count': len(tones),
            'tones': tones,
            'total_duration_ms': total_duration,
            'generated_at': datetime.utcnow().isoformat()
        }

    def get_tone_frequencies(self, digit: str) -> Dict[str, Any]:
        """
        Get frequencies for a DTMF digit.

        Args:
            digit: DTMF digit

        Returns:
            Dictionary with frequency information

        Example:
            >>> freq = service.get_tone_frequencies('9')
        """
        if not self.is_valid_digit(digit):
            return {'error': 'Invalid DTMF digit'}

        frequencies = self._freq_matrix.get(digit, (0, 0))

        return {
            'digit': digit,
            'low_freq': frequencies[0],
            'high_freq': frequencies[1]
        }

    def detect_tone(
        self,
        low_freq: int,
        high_freq: int
    ) -> Dict[str, Any]:
        """
        Detect DTMF digit from frequencies.

        Args:
            low_freq: Low frequency in Hz
            high_freq: High frequency in Hz

        Returns:
            Dictionary with detected digit

        Example:
            >>> result = service.detect_tone(770, 1336)
        """
        detected = None
        for digit, freqs in self._freq_matrix.items():
            if abs(freqs[0] - low_freq) < 20 and abs(freqs[1] - high_freq) < 20:
                detected = digit
                break

        if detected:
            record = {
                'digit': detected,
                'low_freq': low_freq,
                'high_freq': high_freq,
                'detected_at': datetime.utcnow().isoformat()
            }
            self._detected_digits.append(record)
            return record

        return {
            'digit': None,
            'error': 'No DTMF digit detected'
        }

    def decode_sequence(
        self,
        audio_data: bytes = None
    ) -> Dict[str, Any]:
        """
        Decode DTMF sequence from audio.

        Args:
            audio_data: Audio data to decode

        Returns:
            Dictionary with decoded sequence

        Example:
            >>> result = service.decode_sequence(audio_bytes)
        """
        # Simulated decoding - returns detected digits
        digits = ''.join(d.get('digit', '') for d in self._detected_digits)

        return {
            'sequence': digits,
            'digit_count': len(digits),
            'decoded_at': datetime.utcnow().isoformat()
        }

    def start_detection(self) -> Dict[str, Any]:
        """
        Start DTMF detection.

        Returns:
            Dictionary with detection status

        Example:
            >>> result = service.start_detection()
        """
        self._detecting = True
        self._detected_digits = []

        return {
            'detecting': True,
            'started_at': datetime.utcnow().isoformat()
        }

    def stop_detection(self) -> Dict[str, Any]:
        """
        Stop DTMF detection.

        Returns:
            Dictionary with detection results

        Example:
            >>> result = service.stop_detection()
        """
        self._detecting = False

        return {
            'detecting': False,
            'digits_detected': len(self._detected_digits),
            'stopped_at': datetime.utcnow().isoformat()
        }

    def set_tone_duration(self, duration_ms: int) -> Dict[str, Any]:
        """
        Set tone duration.

        Args:
            duration_ms: Duration in milliseconds

        Returns:
            Dictionary with duration setting

        Example:
            >>> result = service.set_tone_duration(150)
        """
        self._tone_duration_ms = duration_ms
        return {
            'duration_ms': duration_ms,
            'configured': True
        }

    def set_inter_digit_gap(self, gap_ms: int) -> Dict[str, Any]:
        """
        Set inter-digit gap.

        Args:
            gap_ms: Gap in milliseconds

        Returns:
            Dictionary with gap setting

        Example:
            >>> result = service.set_inter_digit_gap(75)
        """
        self._inter_digit_gap_ms = gap_ms
        return {
            'gap_ms': gap_ms,
            'configured': True
        }

    def get_timing_config(self) -> Dict[str, Any]:
        """
        Get timing configuration.

        Returns:
            Dictionary with timing settings

        Example:
            >>> config = service.get_timing_config()
        """
        return {
            'tone_duration_ms': self._tone_duration_ms,
            'inter_digit_gap_ms': self._inter_digit_gap_ms
        }

    def create_rtp_event(
        self,
        digit: str,
        end: bool = False,
        duration: int = 0
    ) -> Dict[str, Any]:
        """
        Create RFC 2833 RTP event.

        Args:
            digit: DTMF digit
            end: End of event flag
            duration: Event duration

        Returns:
            Dictionary with RTP event data

        Example:
            >>> event = service.create_rtp_event('5')
        """
        if not self.is_valid_digit(digit):
            return {'error': 'Invalid DTMF digit'}

        event_code = self._event_codes.get(digit, 0)

        return {
            'digit': digit,
            'event_code': event_code,
            'end': end,
            'duration': duration,
            'payload_type': self._payload_type,
            'created_at': datetime.utcnow().isoformat()
        }

    def parse_rtp_event(
        self,
        event_data: bytes
    ) -> Dict[str, Any]:
        """
        Parse RFC 2833 RTP event.

        Args:
            event_data: RTP event payload

        Returns:
            Dictionary with parsed event

        Example:
            >>> event = service.parse_rtp_event(payload)
        """
        # Simulated parsing
        return {
            'event_code': 0,
            'end': False,
            'duration': 0,
            'parsed_at': datetime.utcnow().isoformat()
        }

    def set_payload_type(self, payload_type: int) -> Dict[str, Any]:
        """
        Set RTP payload type for DTMF events.

        Args:
            payload_type: Payload type number

        Returns:
            Dictionary with payload type setting

        Example:
            >>> result = service.set_payload_type(101)
        """
        self._payload_type = payload_type
        return {
            'payload_type': payload_type,
            'configured': True
        }

    def is_valid_digit(self, digit: str) -> bool:
        """
        Check if digit is valid DTMF.

        Args:
            digit: Character to check

        Returns:
            True if valid DTMF digit

        Example:
            >>> valid = service.is_valid_digit('5')
        """
        return digit in self._freq_matrix

    def validate_sequence(self, sequence: str) -> Dict[str, Any]:
        """
        Validate DTMF sequence.

        Args:
            sequence: String of digits to validate

        Returns:
            Dictionary with validation result

        Example:
            >>> result = service.validate_sequence('1234#')
        """
        valid_digits = []
        invalid_digits = []

        for digit in sequence:
            if self.is_valid_digit(digit):
                valid_digits.append(digit)
            else:
                invalid_digits.append(digit)

        return {
            'sequence': sequence,
            'valid': len(invalid_digits) == 0,
            'valid_digits': valid_digits,
            'invalid_digits': invalid_digits,
            'total_digits': len(sequence)
        }

    def get_detected_digits(self) -> List[Dict[str, Any]]:
        """
        Get list of detected digits.

        Returns:
            List of detected digit records

        Example:
            >>> digits = service.get_detected_digits()
        """
        return self._detected_digits.copy()

    def detect_sequence(
        self,
        audio_data: bytes
    ) -> Dict[str, Any]:
        """
        Detect DTMF sequence from audio data.

        Args:
            audio_data: Audio data to analyze

        Returns:
            Dictionary with detected sequence

        Example:
            >>> result = service.detect_sequence(audio_bytes)
        """
        # Simulated detection - would use FFT in real implementation
        digits = ''.join(d.get('digit', '') for d in self._detected_digits)
        return {
            'sequence': digits,
            'digit_count': len(digits),
            'audio_size': len(audio_data) if audio_data else 0,
            'detected_at': datetime.utcnow().isoformat()
        }

    def validate_detection(
        self,
        expected: str,
        detected: str
    ) -> Dict[str, Any]:
        """
        Validate detected DTMF against expected sequence.

        Args:
            expected: Expected DTMF sequence
            detected: Detected DTMF sequence

        Returns:
            Dictionary with validation result

        Example:
            >>> result = service.validate_detection('1234', '1234')
        """
        matches = expected == detected
        return {
            'expected': expected,
            'detected': detected,
            'matches': matches,
            'expected_length': len(expected),
            'detected_length': len(detected),
            'validated_at': datetime.utcnow().isoformat()
        }

    def set_mode(
        self,
        mode: str
    ) -> Dict[str, Any]:
        """
        Set DTMF transmission mode.

        Args:
            mode: 'inband' or 'outofband'

        Returns:
            Dictionary with mode setting

        Example:
            >>> result = service.set_mode('outofband')
        """
        if mode not in ['inband', 'outofband']:
            return {'error': 'Invalid mode. Use inband or outofband'}

        self._mode = mode
        return {
            'mode': mode,
            'configured': True
        }

    def get_mode(self) -> Dict[str, Any]:
        """
        Get current DTMF transmission mode.

        Returns:
            Dictionary with current mode

        Example:
            >>> mode = service.get_mode()
        """
        return {
            'mode': self._mode
        }

    def send_inband(
        self,
        digits: str
    ) -> Dict[str, Any]:
        """
        Send DTMF tones in-band (audio).

        Args:
            digits: DTMF digits to send

        Returns:
            Dictionary with send result

        Example:
            >>> result = service.send_inband('123')
        """
        sequence = self.generate_sequence(digits)
        return {
            'method': 'inband',
            'digits': digits,
            'tone_count': sequence['tone_count'],
            'total_duration_ms': sequence['total_duration_ms'],
            'sent_at': datetime.utcnow().isoformat()
        }

    def send_outofband(
        self,
        digits: str
    ) -> Dict[str, Any]:
        """
        Send DTMF tones out-of-band (RFC 2833).

        Args:
            digits: DTMF digits to send

        Returns:
            Dictionary with send result

        Example:
            >>> result = service.send_outofband('456')
        """
        events = []
        for digit in digits:
            if self.is_valid_digit(digit):
                events.append(self.create_rtp_event(digit))

        return {
            'method': 'outofband',
            'digits': digits,
            'event_count': len(events),
            'payload_type': self._payload_type,
            'sent_at': datetime.utcnow().isoformat()
        }

    def set_gap_duration(
        self,
        gap_ms: int
    ) -> Dict[str, Any]:
        """
        Set inter-digit gap duration.

        Args:
            gap_ms: Gap duration in milliseconds

        Returns:
            Dictionary with gap setting

        Example:
            >>> result = service.set_gap_duration(100)
        """
        self._inter_digit_gap_ms = gap_ms
        return {
            'gap_ms': gap_ms,
            'configured': True
        }

    def get_supported_tones(self) -> List[str]:
        """
        Get list of supported DTMF tones.

        Returns:
            List of supported digit characters

        Example:
            >>> tones = service.get_supported_tones()
        """
        return list(self._freq_matrix.keys())

    def reset_configuration(self) -> Dict[str, Any]:
        """
        Reset DTMF configuration to defaults.

        Returns:
            Dictionary with reset result

        Example:
            >>> result = service.reset_configuration()
        """
        self._tone_duration_ms = 100
        self._inter_digit_gap_ms = 50
        self._payload_type = 101
        self._detecting = False
        self._detected_digits = []
        self._mode = 'inband'

        return {
            'reset': True,
            'timestamp': datetime.utcnow().isoformat()
        }
