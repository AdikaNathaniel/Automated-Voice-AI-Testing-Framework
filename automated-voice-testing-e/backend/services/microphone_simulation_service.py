"""
Microphone Simulation Service for ASR audio testing.

This service simulates various microphone characteristics and their
impact on ASR performance. Different microphone types, placements,
and configurations affect frequency response and noise characteristics.

Microphone types:
- Close-talk: Headset, handheld (distance < 10cm)
- Near-field: Desktop, laptop (distance 30-60cm)
- Far-field: Smart speaker, room mic (distance > 1m)
- Array: Beamforming microphone arrays

Key characteristics:
- Frequency response curve
- Distance attenuation (inverse square law)
- Directivity pattern
- Self-noise level

Example:
    >>> service = MicrophoneSimulationService()
    >>> signal = service.simulate_distance(clean_audio, 2.0)
    >>> print(f"Simulated 2m distance")
"""

from typing import List, Dict, Any, Optional
import numpy as np


class MicrophoneSimulationService:
    """
    Service for simulating microphone characteristics for ASR testing.

    Provides microphone models, distance attenuation, frequency response
    simulation, and array microphone beamforming effects.

    Attributes:
        microphone_presets: Dictionary of microphone preset configurations
        sample_rate: Default sample rate

    Example:
        >>> service = MicrophoneSimulationService()
        >>> metrics = service.get_microphone_metrics('close_talk_headset')
        >>> print(f"Self noise: {metrics['self_noise']} dB")
    """

    # Microphone types
    TYPE_CLOSE_TALK = 'close_talk'
    TYPE_NEAR_FIELD = 'near_field'
    TYPE_FAR_FIELD = 'far_field'
    TYPE_ARRAY = 'array'

    def __init__(self, sample_rate: int = 16000):
        """Initialize the microphone simulation service."""
        self.sample_rate = sample_rate
        self.microphone_types: List[str] = [
            self.TYPE_CLOSE_TALK,
            self.TYPE_NEAR_FIELD,
            self.TYPE_FAR_FIELD,
            self.TYPE_ARRAY
        ]

        self.microphone_presets: Dict[str, Dict[str, Any]] = {
            # Close-talk microphones
            'close_talk_headset': {
                'name': 'Close-talk Headset',
                'type': self.TYPE_CLOSE_TALK,
                'distance': 0.05,  # meters
                'frequency_range': [100, 8000],
                'self_noise': 20,  # dB SPL
                'sensitivity': -40,  # dBV/Pa
                'directivity': 'cardioid',
                'asr_quality': 'excellent',
                'description': 'Headset microphone near mouth'
            },
            'close_talk_handheld': {
                'name': 'Close-talk Handheld',
                'type': self.TYPE_CLOSE_TALK,
                'distance': 0.1,
                'frequency_range': [80, 10000],
                'self_noise': 22,
                'sensitivity': -38,
                'directivity': 'cardioid',
                'asr_quality': 'excellent',
                'description': 'Handheld phone or radio'
            },

            # Near-field microphones
            'near_field_desktop': {
                'name': 'Near-field Desktop',
                'type': self.TYPE_NEAR_FIELD,
                'distance': 0.5,
                'frequency_range': [100, 12000],
                'self_noise': 18,
                'sensitivity': -42,
                'directivity': 'cardioid',
                'asr_quality': 'good',
                'description': 'Desktop USB microphone'
            },
            'near_field_laptop': {
                'name': 'Near-field Laptop',
                'type': self.TYPE_NEAR_FIELD,
                'distance': 0.6,
                'frequency_range': [150, 8000],
                'self_noise': 30,
                'sensitivity': -45,
                'directivity': 'omnidirectional',
                'asr_quality': 'fair',
                'description': 'Built-in laptop microphone'
            },

            # Far-field microphones
            'far_field_smart_speaker': {
                'name': 'Far-field Smart Speaker',
                'type': self.TYPE_FAR_FIELD,
                'distance': 3.0,
                'frequency_range': [100, 8000],
                'self_noise': 25,
                'sensitivity': -38,
                'directivity': 'omnidirectional',
                'asr_quality': 'fair',
                'description': 'Smart speaker across room'
            },
            'far_field_room': {
                'name': 'Far-field Room Mic',
                'type': self.TYPE_FAR_FIELD,
                'distance': 5.0,
                'frequency_range': [50, 15000],
                'self_noise': 15,
                'sensitivity': -35,
                'directivity': 'omnidirectional',
                'asr_quality': 'poor',
                'description': 'Room microphone for recording'
            },

            # Array microphones
            'array_2_mic': {
                'name': '2-Microphone Array',
                'type': self.TYPE_ARRAY,
                'distance': 1.0,
                'frequency_range': [100, 8000],
                'self_noise': 22,
                'sensitivity': -40,
                'directivity': 'beamforming',
                'num_elements': 2,
                'element_spacing': 0.04,
                'asr_quality': 'good',
                'description': 'Laptop dual-mic array'
            },
            'array_4_mic': {
                'name': '4-Microphone Array',
                'type': self.TYPE_ARRAY,
                'distance': 2.0,
                'frequency_range': [100, 8000],
                'self_noise': 20,
                'sensitivity': -38,
                'directivity': 'beamforming',
                'num_elements': 4,
                'element_spacing': 0.04,
                'asr_quality': 'good',
                'description': 'Smart speaker mic array'
            },
            'array_7_mic': {
                'name': '7-Microphone Array',
                'type': self.TYPE_ARRAY,
                'distance': 3.0,
                'frequency_range': [100, 8000],
                'self_noise': 18,
                'sensitivity': -36,
                'directivity': 'beamforming',
                'num_elements': 7,
                'element_spacing': 0.035,
                'asr_quality': 'excellent',
                'description': 'Professional circular array'
            }
        }

    def list_microphone_presets(
        self,
        mic_type: Optional[str] = None
    ) -> List[str]:
        """
        List available microphone presets.

        Args:
            mic_type: Filter by microphone type (optional)

        Returns:
            List of preset identifiers

        Example:
            >>> presets = service.list_microphone_presets('close_talk')
            >>> print(f"Found {len(presets)} close-talk presets")
        """
        if mic_type:
            return [
                name for name, info in self.microphone_presets.items()
                if info['type'] == mic_type.lower()
            ]
        return list(self.microphone_presets.keys())

    def get_microphone_preset(self, preset_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a microphone preset.

        Args:
            preset_name: Preset identifier

        Returns:
            Dictionary with microphone specifications

        Example:
            >>> preset = service.get_microphone_preset('close_talk_headset')
            >>> print(f"Self noise: {preset['self_noise']} dB")
        """
        if preset_name in self.microphone_presets:
            return self.microphone_presets[preset_name].copy()

        return {
            'name': 'Unknown',
            'type': 'unknown',
            'distance': 0.0,
            'frequency_range': [0, 0],
            'self_noise': 0,
            'sensitivity': 0,
            'directivity': 'unknown',
            'asr_quality': 'unknown',
            'description': 'Unknown microphone'
        }

    def calculate_attenuation(
        self,
        distance: float,
        reference_distance: float = 1.0
    ) -> float:
        """
        Calculate distance attenuation using inverse square law.

        Attenuation = 20 * log10(d / d_ref)

        Args:
            distance: Target distance in meters
            reference_distance: Reference distance (default 1m)

        Returns:
            Attenuation in dB (negative for loss)

        Example:
            >>> atten = service.calculate_attenuation(3.0)
            >>> print(f"Attenuation at 3m: {atten:.1f} dB")
        """
        if distance <= 0 or reference_distance <= 0:
            return 0.0

        attenuation = 20 * np.log10(reference_distance / distance)
        return float(attenuation)

    def simulate_distance(
        self,
        signal: np.ndarray,
        distance: float,
        reference_distance: float = 0.1
    ) -> np.ndarray:
        """
        Simulate distance effect on audio signal.

        Applies attenuation and high-frequency roll-off.

        Args:
            signal: Audio signal
            distance: Target distance in meters
            reference_distance: Reference distance

        Returns:
            Attenuated signal

        Example:
            >>> far_signal = service.simulate_distance(close_signal, 2.0)
            >>> print(f"Simulated 2m distance")
        """
        # Calculate attenuation
        attenuation_db = self.calculate_attenuation(distance, reference_distance)
        attenuation_linear = 10 ** (attenuation_db / 20)

        # Apply attenuation
        output = signal * attenuation_linear

        # Apply high-frequency roll-off for distance
        if distance > 1.0:
            rolloff_factor = 1.0 / distance
            output = self._apply_low_pass(output, rolloff_factor)

        return output.astype(np.float32)

    def _apply_low_pass(
        self,
        signal: np.ndarray,
        factor: float
    ) -> np.ndarray:
        """Apply simple low-pass filter for distance simulation."""
        # Simple moving average as low-pass
        kernel_size = max(1, int(5 / factor))
        if kernel_size > 1:
            kernel = np.ones(kernel_size) / kernel_size
            return np.convolve(signal, kernel, mode='same')
        return signal

    def get_frequency_response(
        self,
        preset_name: str
    ) -> Dict[str, Any]:
        """
        Get frequency response for a microphone preset.

        Args:
            preset_name: Preset identifier

        Returns:
            Dictionary with frequency response data

        Example:
            >>> response = service.get_frequency_response('near_field_laptop')
            >>> print(f"Range: {response['frequency_range']}")
        """
        preset = self.get_microphone_preset(preset_name)
        freq_range = preset.get('frequency_range', [100, 8000])

        # Generate approximate frequency response curve
        frequencies = [31, 63, 125, 250, 500, 1000, 2000, 4000, 8000, 16000]
        response = []

        for f in frequencies:
            if f < freq_range[0]:
                # Below range - roll off
                db = -12 * np.log2(freq_range[0] / f)
            elif f > freq_range[1]:
                # Above range - roll off
                db = -12 * np.log2(f / freq_range[1])
            else:
                # In range - relatively flat with some variation
                db = np.random.uniform(-2, 2)

            response.append({
                'frequency': f,
                'response_db': float(db)
            })

        return {
            'preset_name': preset_name,
            'frequency_range': freq_range,
            'response_curve': response,
            'flatness': 'good' if freq_range[1] - freq_range[0] > 7000 else 'fair'
        }

    def apply_frequency_response(
        self,
        signal: np.ndarray,
        preset_name: str,
        sample_rate: Optional[int] = None
    ) -> np.ndarray:
        """
        Apply microphone frequency response to signal.

        Args:
            signal: Audio signal
            preset_name: Microphone preset
            sample_rate: Sample rate (uses default if not specified)

        Returns:
            Filtered signal

        Example:
            >>> filtered = service.apply_frequency_response(signal, 'near_field_laptop')
            >>> print(f"Applied laptop mic response")
        """
        if sample_rate is None:
            sample_rate = self.sample_rate

        preset = self.get_microphone_preset(preset_name)
        freq_range = preset.get('frequency_range', [100, 8000])

        # Apply bandpass filter based on frequency response
        fft = np.fft.rfft(signal)
        freqs = np.fft.rfftfreq(len(signal), 1 / sample_rate)

        # Create frequency response mask
        mask = np.ones(len(freqs))

        for i, f in enumerate(freqs):
            if f < freq_range[0]:
                # Low frequency roll-off
                if freq_range[0] > 0:
                    mask[i] = (f / freq_range[0]) ** 2
            elif f > freq_range[1]:
                # High frequency roll-off
                mask[i] = (freq_range[1] / f) ** 2

        fft_filtered = fft * mask
        return np.fft.irfft(fft_filtered, len(signal)).astype(np.float32)

    def simulate_array(
        self,
        signal: np.ndarray,
        preset_name: str,
        direction: float = 0.0
    ) -> np.ndarray:
        """
        Simulate array microphone beamforming effect.

        Args:
            signal: Audio signal
            preset_name: Array microphone preset
            direction: Source direction in degrees (0 = frontal)

        Returns:
            Processed signal with beamforming effect

        Example:
            >>> output = service.simulate_array(signal, 'array_4_mic', 30)
            >>> print(f"Beamformed at 30 degrees")
        """
        preset = self.get_microphone_preset(preset_name)

        if preset.get('type') != self.TYPE_ARRAY:
            return signal

        num_elements = preset.get('num_elements', 2)

        # Simulate beamforming gain based on direction
        # On-axis has maximum gain, off-axis has reduced gain
        direction_rad = np.radians(direction)
        beam_pattern = np.cos(direction_rad) ** (num_elements / 2)

        # Array processing improves SNR
        snr_improvement = 10 * np.log10(num_elements)

        # Apply gain
        gain = beam_pattern * (10 ** (snr_improvement / 20))
        output = signal * gain

        # Normalize
        max_val = np.max(np.abs(output))
        if max_val > 0:
            output = output / max_val

        return output.astype(np.float32)

    def get_microphone_metrics(
        self,
        preset_name: str
    ) -> Dict[str, Any]:
        """
        Get comprehensive microphone metrics.

        Args:
            preset_name: Microphone preset identifier

        Returns:
            Dictionary with all microphone metrics

        Example:
            >>> metrics = service.get_microphone_metrics('far_field_smart_speaker')
            >>> print(f"ASR quality: {metrics['asr_quality']}")
        """
        preset = self.get_microphone_preset(preset_name)
        freq_response = self.get_frequency_response(preset_name)

        # Calculate ASR impact
        distance = preset.get('distance', 1.0)
        self_noise = preset.get('self_noise', 20)

        if distance < 0.2:
            distance_impact = 'minimal'
            wer_increase = 0.0
        elif distance < 1.0:
            distance_impact = 'low'
            wer_increase = 5.0
        elif distance < 3.0:
            distance_impact = 'moderate'
            wer_increase = 15.0
        else:
            distance_impact = 'high'
            wer_increase = 30.0

        # Self-noise impact
        if self_noise > 25:
            wer_increase += 5.0

        return {
            'preset_name': preset_name,
            'preset_info': preset,
            'frequency_response': freq_response,
            'distance': distance,
            'self_noise': self_noise,
            'asr_quality': preset.get('asr_quality', 'unknown'),
            'distance_impact': distance_impact,
            'estimated_wer_increase': wer_increase,
            'recommended_for_asr': distance < 1.0 and self_noise < 25,
            'attenuation_at_distance': self.calculate_attenuation(distance)
        }

