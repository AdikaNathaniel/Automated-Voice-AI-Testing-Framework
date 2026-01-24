"""
Room Impulse Response (RIR) Simulation Service for ASR audio testing.

This service provides tools for simulating room acoustic characteristics
and their impact on ASR performance. RIR captures reflections, reverb,
and decay patterns specific to different room sizes and materials.

Room sizes:
- Small: Car cabin, bathroom (RT60: 0.1-0.3s)
- Medium: Office, living room (RT60: 0.3-0.6s)
- Large: Conference room, auditorium (RT60: 0.6-2.0s)

Key parameters:
- RT60: Time for sound to decay 60 dB
- Early reflections: First 50-80ms of response
- Late reverb: Diffuse sound after early reflections

Example:
    >>> service = RoomImpulseResponseService()
    >>> rir = service.generate_rir('medium_office', 1.0)
    >>> print(f"RIR samples: {len(rir)}")
"""

from typing import List, Dict, Any, Optional
import numpy as np


class RoomImpulseResponseService:
    """
    Service for simulating room impulse responses for ASR testing.

    Provides room acoustic simulation including RT60 calculation,
    RIR generation, and reverb application to audio signals.

    Attributes:
        room_presets: Dictionary of room preset configurations
        sample_rate: Default sample rate for RIR generation

    Example:
        >>> service = RoomImpulseResponseService()
        >>> metrics = service.get_rir_metrics('large_conference')
        >>> print(f"RT60: {metrics['rt60']} seconds")
    """

    # Room size categories
    SIZE_SMALL = 'small'
    SIZE_MEDIUM = 'medium'
    SIZE_LARGE = 'large'

    def __init__(self, sample_rate: int = 16000):
        """Initialize the RIR service."""
        self.sample_rate = sample_rate
        self.room_sizes: List[str] = [
            self.SIZE_SMALL,
            self.SIZE_MEDIUM,
            self.SIZE_LARGE
        ]

        self.room_presets: Dict[str, Dict[str, Any]] = {
            # Small rooms
            'car_cabin': {
                'name': 'Car Cabin',
                'size': self.SIZE_SMALL,
                'dimensions': [2.0, 1.5, 1.2],  # meters
                'rt60': 0.15,
                'absorption': 0.7,
                'asr_difficulty': 'easy',
                'description': 'Compact vehicle interior'
            },
            'bathroom': {
                'name': 'Bathroom',
                'size': self.SIZE_SMALL,
                'dimensions': [3.0, 2.5, 2.5],
                'rt60': 0.8,
                'absorption': 0.3,
                'asr_difficulty': 'medium',
                'description': 'Small reflective bathroom'
            },
            'phone_booth': {
                'name': 'Phone Booth',
                'size': self.SIZE_SMALL,
                'dimensions': [1.0, 1.0, 2.0],
                'rt60': 0.1,
                'absorption': 0.8,
                'asr_difficulty': 'easy',
                'description': 'Small enclosed booth'
            },

            # Medium rooms
            'medium_office': {
                'name': 'Medium Office',
                'size': self.SIZE_MEDIUM,
                'dimensions': [6.0, 5.0, 3.0],
                'rt60': 0.4,
                'absorption': 0.5,
                'asr_difficulty': 'easy',
                'description': 'Standard office space'
            },
            'living_room': {
                'name': 'Living Room',
                'size': self.SIZE_MEDIUM,
                'dimensions': [7.0, 5.0, 2.8],
                'rt60': 0.5,
                'absorption': 0.4,
                'asr_difficulty': 'medium',
                'description': 'Residential living room'
            },
            'classroom': {
                'name': 'Classroom',
                'size': self.SIZE_MEDIUM,
                'dimensions': [10.0, 8.0, 3.5],
                'rt60': 0.6,
                'absorption': 0.4,
                'asr_difficulty': 'medium',
                'description': 'School classroom'
            },

            # Large rooms
            'large_conference': {
                'name': 'Large Conference Room',
                'size': self.SIZE_LARGE,
                'dimensions': [15.0, 12.0, 4.0],
                'rt60': 0.8,
                'absorption': 0.35,
                'asr_difficulty': 'hard',
                'description': 'Corporate conference room'
            },
            'auditorium': {
                'name': 'Auditorium',
                'size': self.SIZE_LARGE,
                'dimensions': [30.0, 20.0, 8.0],
                'rt60': 1.5,
                'absorption': 0.25,
                'asr_difficulty': 'very_hard',
                'description': 'Large auditorium'
            },
            'hall': {
                'name': 'Hall',
                'size': self.SIZE_LARGE,
                'dimensions': [25.0, 15.0, 6.0],
                'rt60': 1.2,
                'absorption': 0.3,
                'asr_difficulty': 'hard',
                'description': 'Large hall or gymnasium'
            }
        }

    def list_room_presets(
        self,
        size: Optional[str] = None
    ) -> List[str]:
        """
        List available room presets.

        Args:
            size: Filter by room size (optional)

        Returns:
            List of preset identifiers

        Example:
            >>> presets = service.list_room_presets('small')
            >>> print(f"Found {len(presets)} small room presets")
        """
        if size:
            return [
                name for name, info in self.room_presets.items()
                if info['size'] == size.lower()
            ]
        return list(self.room_presets.keys())

    def get_room_preset(self, preset_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a room preset.

        Args:
            preset_name: Preset identifier

        Returns:
            Dictionary with room specifications

        Example:
            >>> preset = service.get_room_preset('medium_office')
            >>> print(f"RT60: {preset['rt60']} seconds")
        """
        if preset_name in self.room_presets:
            return self.room_presets[preset_name].copy()

        return {
            'name': 'Unknown',
            'size': 'unknown',
            'dimensions': [0, 0, 0],
            'rt60': 0.0,
            'absorption': 0.0,
            'asr_difficulty': 'unknown',
            'description': 'Unknown room'
        }

    def calculate_rt60(
        self,
        dimensions: List[float],
        absorption: float
    ) -> float:
        """
        Calculate RT60 reverb time from room parameters.

        Uses Sabine's formula: RT60 = 0.161 * V / A
        Where V is volume and A is total absorption.

        Args:
            dimensions: Room dimensions [length, width, height] in meters
            absorption: Average absorption coefficient (0-1)

        Returns:
            RT60 in seconds

        Example:
            >>> rt60 = service.calculate_rt60([6.0, 5.0, 3.0], 0.5)
            >>> print(f"RT60: {rt60:.2f} seconds")
        """
        # Calculate volume
        volume = dimensions[0] * dimensions[1] * dimensions[2]

        # Calculate surface area
        length, w, h = dimensions
        surface_area = 2 * (length * w + length * h + w * h)

        # Total absorption
        total_absorption = surface_area * absorption

        # Sabine's formula
        if total_absorption > 0:
            rt60 = 0.161 * volume / total_absorption
        else:
            rt60 = 0.0

        return float(rt60)

    def generate_rir(
        self,
        preset_name: str,
        duration: float = 1.0,
        sample_rate: Optional[int] = None
    ) -> np.ndarray:
        """
        Generate room impulse response for a preset.

        Args:
            preset_name: Room preset identifier
            duration: RIR duration in seconds
            sample_rate: Sample rate (uses default if not specified)

        Returns:
            RIR signal array

        Example:
            >>> rir = service.generate_rir('medium_office', 0.5)
            >>> print(f"RIR samples: {len(rir)}")
        """
        if sample_rate is None:
            sample_rate = self.sample_rate

        preset = self.get_room_preset(preset_name)
        rt60 = preset.get('rt60', 0.5)

        num_samples = int(duration * sample_rate)

        # Generate exponential decay envelope
        decay_rate = 6.91 / rt60  # -60 dB decay
        t = np.arange(num_samples) / sample_rate
        envelope = np.exp(-decay_rate * t)

        # Generate RIR with early reflections and late reverb
        rir = np.zeros(num_samples)

        # Direct sound (impulse)
        rir[0] = 1.0

        # Early reflections (first 50-80ms)
        early_samples = int(0.08 * sample_rate)
        preset.get('dimensions', [5, 4, 3])

        # Add some early reflections based on room dimensions
        for i in range(5):
            delay_ms = (i + 1) * 10 + np.random.uniform(-2, 2)
            delay_samples = int(delay_ms * sample_rate / 1000)
            if delay_samples < early_samples:
                # Reflection amplitude decreases with each reflection
                amplitude = 0.5 ** (i + 1)
                rir[delay_samples] += amplitude

        # Late reverb (diffuse noise shaped by envelope)
        late_start = early_samples
        if late_start < num_samples:
            noise = np.random.randn(num_samples - late_start) * 0.1
            noise *= envelope[late_start:]
            rir[late_start:] += noise

        # Apply overall envelope
        rir *= envelope

        # Normalize
        rir = rir / (np.max(np.abs(rir)) + 1e-10)

        return rir.astype(np.float32)

    def apply_rir(
        self,
        signal: np.ndarray,
        rir: np.ndarray
    ) -> np.ndarray:
        """
        Apply room impulse response to audio signal.

        Convolves signal with RIR to simulate room acoustics.

        Args:
            signal: Clean audio signal
            rir: Room impulse response

        Returns:
            Reverberant audio signal

        Example:
            >>> reverberant = service.apply_rir(clean_signal, rir)
            >>> print(f"Output length: {len(reverberant)}")
        """
        # Convolve signal with RIR
        reverberant = np.convolve(signal, rir, mode='full')

        # Trim to original length
        reverberant = reverberant[:len(signal)]

        # Normalize to prevent clipping
        max_val = np.max(np.abs(reverberant))
        if max_val > 0:
            reverberant = reverberant / max_val

        return reverberant.astype(np.float32)

    def analyze_room_acoustics(
        self,
        preset_name: str
    ) -> Dict[str, Any]:
        """
        Analyze acoustic characteristics of a room preset.

        Args:
            preset_name: Room preset identifier

        Returns:
            Dictionary with acoustic analysis

        Example:
            >>> analysis = service.analyze_room_acoustics('large_conference')
            >>> print(f"RT60: {analysis['rt60']} seconds")
        """
        preset = self.get_room_preset(preset_name)
        dimensions = preset.get('dimensions', [5, 4, 3])

        # Calculate volume
        volume = dimensions[0] * dimensions[1] * dimensions[2]

        # Calculate surface area
        length, w, h = dimensions
        surface_area = 2 * (length * w + length * h + w * h)

        # Calculate RT60 from parameters
        calculated_rt60 = self.calculate_rt60(dimensions, preset['absorption'])

        # Estimate speech clarity metrics
        rt60 = preset.get('rt60', 0.5)
        if rt60 < 0.3:
            clarity = 'excellent'
            c50 = 10.0
        elif rt60 < 0.6:
            clarity = 'good'
            c50 = 5.0
        elif rt60 < 1.0:
            clarity = 'fair'
            c50 = 0.0
        else:
            clarity = 'poor'
            c50 = -5.0

        return {
            'preset_name': preset_name,
            'preset_info': preset,
            'volume': float(volume),
            'surface_area': float(surface_area),
            'rt60': float(rt60),
            'calculated_rt60': float(calculated_rt60),
            'speech_clarity': clarity,
            'estimated_c50': float(c50),  # Clarity index
            'asr_impact': self._estimate_asr_impact(rt60)
        }

    def _estimate_asr_impact(self, rt60: float) -> Dict[str, Any]:
        """Estimate ASR performance impact from RT60."""
        if rt60 < 0.3:
            wer_increase = 0.0
            impact = 'minimal'
        elif rt60 < 0.6:
            wer_increase = 5.0
            impact = 'low'
        elif rt60 < 1.0:
            wer_increase = 15.0
            impact = 'moderate'
        else:
            wer_increase = 30.0
            impact = 'severe'

        return {
            'impact_level': impact,
            'estimated_wer_increase': wer_increase,
            'recommendation': (
                'acceptable' if wer_increase < 10
                else 'caution' if wer_increase < 20
                else 'dereverberation_recommended'
            )
        }

    def get_rir_metrics(
        self,
        preset_name: str
    ) -> Dict[str, Any]:
        """
        Get comprehensive RIR metrics for a room preset.

        Args:
            preset_name: Room preset identifier

        Returns:
            Dictionary with all RIR metrics

        Example:
            >>> metrics = service.get_rir_metrics('car_cabin')
            >>> print(f"Difficulty: {metrics['asr_difficulty']}")
        """
        preset = self.get_room_preset(preset_name)
        acoustics = self.analyze_room_acoustics(preset_name)

        # Generate a test RIR
        rir = self.generate_rir(preset_name, 0.5)

        # Calculate RIR characteristics
        direct_to_reverb = self._calculate_direct_to_reverb(rir)

        return {
            'preset_name': preset_name,
            'preset_info': preset,
            'room_acoustics': acoustics,
            'rt60': preset.get('rt60', 0.0),
            'asr_difficulty': preset.get('asr_difficulty', 'unknown'),
            'direct_to_reverb_ratio': float(direct_to_reverb),
            'rir_length': len(rir),
            'recommended_for_asr': preset.get('rt60', 0.0) < 0.6,
            'asr_impact': acoustics['asr_impact']
        }

    def _calculate_direct_to_reverb(self, rir: np.ndarray) -> float:
        """Calculate direct-to-reverberant energy ratio."""
        if len(rir) < 100:
            return 0.0

        # Direct sound (first few samples)
        direct_energy = np.sum(rir[:10] ** 2)

        # Reverberant energy (rest)
        reverb_energy = np.sum(rir[10:] ** 2)

        if reverb_energy > 0:
            drr = 10 * np.log10(direct_energy / reverb_energy)
        else:
            drr = float('inf')

        return float(drr)

