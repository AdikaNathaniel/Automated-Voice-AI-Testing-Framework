"""
Enhanced Noise Profile Library Service for ASR audio testing.

This service provides a comprehensive library of noise profiles for testing
ASR systems under various real-world acoustic conditions. Each profile
models specific noise characteristics and frequency responses.

Noise categories:
- Vehicle: Car cabin noise, road noise, highway, city streets
- Environmental: HVAC, office, home, crowd/babble
- Industrial: Factory, machinery, construction

Example:
    >>> service = NoiseProfileLibraryService()
    >>> profile = service.get_profile('car_cabin_highway')
    >>> print(f"Category: {profile['category']}")
"""

from typing import List, Dict, Any, Optional
import numpy as np


class NoiseProfileLibraryService:
    """
    Service for managing and generating noise profiles for ASR testing.

    Provides a library of realistic noise environments and tools
    for applying noise to audio signals at specified SNR levels.

    Attributes:
        profiles: Dictionary of noise profile definitions
        categories: List of noise categories

    Example:
        >>> service = NoiseProfileLibraryService()
        >>> profiles = service.list_profiles('vehicle')
        >>> print(f"Found {len(profiles)} vehicle noise profiles")
    """

    # Noise categories
    CATEGORY_VEHICLE = 'vehicle'
    CATEGORY_ENVIRONMENTAL = 'environmental'
    CATEGORY_INDUSTRIAL = 'industrial'

    def __init__(self):
        """Initialize the noise profile library service."""
        self.categories: List[str] = [
            self.CATEGORY_VEHICLE,
            self.CATEGORY_ENVIRONMENTAL,
            self.CATEGORY_INDUSTRIAL
        ]

        self.profiles: Dict[str, Dict[str, Any]] = {
            # Vehicle noise profiles
            'car_cabin_idle': {
                'name': 'Car Cabin - Idle',
                'category': self.CATEGORY_VEHICLE,
                'description': 'Car cabin noise at idle with engine running',
                'frequency_range': [20, 500],
                'dominant_frequency': 100,
                'typical_snr': 25,
                'asr_difficulty': 'easy'
            },
            'car_cabin_city': {
                'name': 'Car Cabin - City',
                'category': self.CATEGORY_VEHICLE,
                'description': 'Car cabin noise driving in city at 30 mph',
                'frequency_range': [20, 2000],
                'dominant_frequency': 200,
                'typical_snr': 15,
                'asr_difficulty': 'medium'
            },
            'car_cabin_highway': {
                'name': 'Car Cabin - Highway',
                'category': self.CATEGORY_VEHICLE,
                'description': 'Car cabin noise driving on highway at 65 mph',
                'frequency_range': [20, 4000],
                'dominant_frequency': 500,
                'typical_snr': 5,
                'asr_difficulty': 'hard'
            },
            'road_highway': {
                'name': 'Road Noise - Highway',
                'category': self.CATEGORY_VEHICLE,
                'description': 'Highway road noise from tire and wind',
                'frequency_range': [100, 4000],
                'dominant_frequency': 1000,
                'typical_snr': 0,
                'asr_difficulty': 'very_hard'
            },
            'road_city': {
                'name': 'Road Noise - City',
                'category': self.CATEGORY_VEHICLE,
                'description': 'City road noise with traffic',
                'frequency_range': [50, 3000],
                'dominant_frequency': 500,
                'typical_snr': 10,
                'asr_difficulty': 'hard'
            },
            'road_gravel': {
                'name': 'Road Noise - Gravel',
                'category': self.CATEGORY_VEHICLE,
                'description': 'Gravel road noise with loose stones',
                'frequency_range': [100, 6000],
                'dominant_frequency': 2000,
                'typical_snr': 5,
                'asr_difficulty': 'hard'
            },

            # Environmental noise profiles
            'hvac_office': {
                'name': 'HVAC - Office',
                'category': self.CATEGORY_ENVIRONMENTAL,
                'description': 'Office HVAC system humming',
                'frequency_range': [50, 500],
                'dominant_frequency': 100,
                'typical_snr': 30,
                'asr_difficulty': 'easy'
            },
            'hvac_residential': {
                'name': 'HVAC - Residential',
                'category': self.CATEGORY_ENVIRONMENTAL,
                'description': 'Residential air conditioning',
                'frequency_range': [50, 800],
                'dominant_frequency': 150,
                'typical_snr': 25,
                'asr_difficulty': 'easy'
            },
            'crowd_sparse': {
                'name': 'Crowd - Sparse',
                'category': self.CATEGORY_ENVIRONMENTAL,
                'description': 'Light crowd babble noise (cafe)',
                'frequency_range': [100, 8000],
                'dominant_frequency': 500,
                'typical_snr': 15,
                'asr_difficulty': 'medium'
            },
            'crowd_dense': {
                'name': 'Crowd - Dense',
                'category': self.CATEGORY_ENVIRONMENTAL,
                'description': 'Dense crowd babble noise (party)',
                'frequency_range': [100, 8000],
                'dominant_frequency': 1000,
                'typical_snr': 0,
                'asr_difficulty': 'very_hard'
            },
            'office_quiet': {
                'name': 'Office - Quiet',
                'category': self.CATEGORY_ENVIRONMENTAL,
                'description': 'Quiet office environment',
                'frequency_range': [50, 2000],
                'dominant_frequency': 200,
                'typical_snr': 35,
                'asr_difficulty': 'easy'
            },
            'office_busy': {
                'name': 'Office - Busy',
                'category': self.CATEGORY_ENVIRONMENTAL,
                'description': 'Busy office with keyboards and conversation',
                'frequency_range': [50, 6000],
                'dominant_frequency': 1000,
                'typical_snr': 10,
                'asr_difficulty': 'hard'
            },
            'home_quiet': {
                'name': 'Home - Quiet',
                'category': self.CATEGORY_ENVIRONMENTAL,
                'description': 'Quiet home environment',
                'frequency_range': [30, 1000],
                'dominant_frequency': 100,
                'typical_snr': 40,
                'asr_difficulty': 'easy'
            },
            'home_tv': {
                'name': 'Home - TV Background',
                'category': self.CATEGORY_ENVIRONMENTAL,
                'description': 'Home with TV playing in background',
                'frequency_range': [50, 8000],
                'dominant_frequency': 500,
                'typical_snr': 10,
                'asr_difficulty': 'hard'
            },
            'home_appliances': {
                'name': 'Home - Appliances',
                'category': self.CATEGORY_ENVIRONMENTAL,
                'description': 'Home with appliances (dishwasher, etc.)',
                'frequency_range': [50, 4000],
                'dominant_frequency': 300,
                'typical_snr': 15,
                'asr_difficulty': 'medium'
            },

            # Industrial noise profiles
            'factory_light': {
                'name': 'Factory - Light Industrial',
                'category': self.CATEGORY_INDUSTRIAL,
                'description': 'Light factory machinery noise',
                'frequency_range': [50, 6000],
                'dominant_frequency': 500,
                'typical_snr': 10,
                'asr_difficulty': 'hard'
            },
            'factory_heavy': {
                'name': 'Factory - Heavy Industrial',
                'category': self.CATEGORY_INDUSTRIAL,
                'description': 'Heavy factory machinery and equipment',
                'frequency_range': [20, 8000],
                'dominant_frequency': 1000,
                'typical_snr': 0,
                'asr_difficulty': 'very_hard'
            },
            'construction': {
                'name': 'Construction Site',
                'category': self.CATEGORY_INDUSTRIAL,
                'description': 'Construction site with tools and machinery',
                'frequency_range': [50, 10000],
                'dominant_frequency': 2000,
                'typical_snr': -5,
                'asr_difficulty': 'extreme'
            }
        }

    def get_categories(self) -> List[str]:
        """
        Get list of noise profile categories.

        Returns:
            List of category names

        Example:
            >>> categories = service.get_categories()
            >>> print(categories)
            ['vehicle', 'environmental', 'industrial']
        """
        return self.categories.copy()

    def list_profiles(
        self,
        category: Optional[str] = None
    ) -> List[str]:
        """
        List available noise profiles.

        Args:
            category: Filter by category (optional)

        Returns:
            List of profile identifiers

        Example:
            >>> profiles = service.list_profiles('vehicle')
            >>> print(f"Found {len(profiles)} vehicle profiles")
        """
        if category:
            return [
                name for name, info in self.profiles.items()
                if info['category'] == category.lower()
            ]
        return list(self.profiles.keys())

    def get_profile(self, profile_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a noise profile.

        Args:
            profile_name: Profile identifier

        Returns:
            Dictionary with profile specifications

        Example:
            >>> profile = service.get_profile('car_cabin_highway')
            >>> print(f"Difficulty: {profile['asr_difficulty']}")
        """
        if profile_name in self.profiles:
            return self.profiles[profile_name].copy()

        return {
            'name': 'Unknown',
            'category': 'unknown',
            'description': 'Unknown profile',
            'frequency_range': [0, 0],
            'dominant_frequency': 0,
            'typical_snr': 0,
            'asr_difficulty': 'unknown'
        }

    def get_profile_parameters(
        self,
        profile_name: str
    ) -> Dict[str, Any]:
        """
        Get generation parameters for a noise profile.

        Args:
            profile_name: Profile identifier

        Returns:
            Dictionary with noise generation parameters

        Example:
            >>> params = service.get_profile_parameters('hvac_office')
            >>> print(f"Frequency range: {params['frequency_range']}")
        """
        profile = self.get_profile(profile_name)

        # Calculate noise generation parameters
        freq_range = profile.get('frequency_range', [20, 8000])
        dominant = profile.get('dominant_frequency', 500)

        return {
            'profile_name': profile_name,
            'frequency_range': freq_range,
            'dominant_frequency': dominant,
            'bandwidth': freq_range[1] - freq_range[0],
            'spectral_shape': self._determine_spectral_shape(profile_name),
            'temporal_variation': self._determine_temporal_variation(profile_name),
            'typical_snr': profile.get('typical_snr', 10)
        }

    def _determine_spectral_shape(self, profile_name: str) -> str:
        """Determine spectral shape for noise generation."""
        if 'hvac' in profile_name or 'cabin' in profile_name:
            return 'pink'  # More low frequency
        elif 'road' in profile_name or 'highway' in profile_name:
            return 'brown'  # Heavy low frequency
        elif 'crowd' in profile_name or 'babble' in profile_name:
            return 'speech_shaped'
        elif 'factory' in profile_name or 'industrial' in profile_name:
            return 'white'  # Broadband
        else:
            return 'pink'

    def _determine_temporal_variation(self, profile_name: str) -> str:
        """Determine temporal variation pattern."""
        if 'crowd' in profile_name:
            return 'modulated'
        elif 'construction' in profile_name:
            return 'impulsive'
        elif 'highway' in profile_name or 'road' in profile_name:
            return 'slow_variation'
        else:
            return 'stationary'

    def generate_noise(
        self,
        profile_name: str,
        duration: float,
        sample_rate: int = 16000
    ) -> np.ndarray:
        """
        Generate noise signal for a profile.

        Args:
            profile_name: Profile identifier
            duration: Duration in seconds
            sample_rate: Sample rate in Hz

        Returns:
            Noise signal array

        Example:
            >>> noise = service.generate_noise('hvac_office', 5.0)
            >>> print(f"Samples: {len(noise)}")
        """
        params = self.get_profile_parameters(profile_name)
        num_samples = int(duration * sample_rate)

        # Generate base noise based on spectral shape
        spectral_shape = params.get('spectral_shape', 'pink')

        if spectral_shape == 'white':
            noise = np.random.randn(num_samples)
        elif spectral_shape == 'pink':
            noise = self._generate_pink_noise(num_samples)
        elif spectral_shape == 'brown':
            noise = self._generate_brown_noise(num_samples)
        elif spectral_shape == 'speech_shaped':
            noise = self._generate_speech_shaped_noise(num_samples, sample_rate)
        else:
            noise = np.random.randn(num_samples)

        # Apply frequency filtering
        freq_range = params.get('frequency_range', [20, 8000])
        noise = self._apply_frequency_filter(noise, freq_range, sample_rate)

        # Normalize
        noise = noise / (np.max(np.abs(noise)) + 1e-10)

        return noise.astype(np.float32)

    def _generate_pink_noise(self, num_samples: int) -> np.ndarray:
        """Generate pink (1/f) noise."""
        white = np.random.randn(num_samples)
        fft = np.fft.rfft(white)
        freqs = np.fft.rfftfreq(num_samples)
        freqs[0] = 1  # Avoid division by zero
        pink_fft = fft / np.sqrt(freqs)
        return np.fft.irfft(pink_fft, num_samples)

    def _generate_brown_noise(self, num_samples: int) -> np.ndarray:
        """Generate brown (1/f^2) noise."""
        white = np.random.randn(num_samples)
        fft = np.fft.rfft(white)
        freqs = np.fft.rfftfreq(num_samples)
        freqs[0] = 1
        brown_fft = fft / freqs
        return np.fft.irfft(brown_fft, num_samples)

    def _generate_speech_shaped_noise(
        self,
        num_samples: int,
        sample_rate: int
    ) -> np.ndarray:
        """Generate speech-shaped noise."""
        # Approximate speech spectrum
        white = np.random.randn(num_samples)
        fft = np.fft.rfft(white)
        freqs = np.fft.rfftfreq(num_samples, 1 / sample_rate)

        # Apply speech-like spectral envelope
        envelope = np.exp(-((freqs - 500) ** 2) / (2 * 200 ** 2))
        envelope += 0.5 * np.exp(-((freqs - 1500) ** 2) / (2 * 300 ** 2))
        envelope += 0.3 * np.exp(-((freqs - 2500) ** 2) / (2 * 400 ** 2))

        shaped_fft = fft * envelope
        return np.fft.irfft(shaped_fft, num_samples)

    def _apply_frequency_filter(
        self,
        signal: np.ndarray,
        freq_range: List[int],
        sample_rate: int
    ) -> np.ndarray:
        """Apply bandpass frequency filter."""
        fft = np.fft.rfft(signal)
        freqs = np.fft.rfftfreq(len(signal), 1 / sample_rate)

        # Simple bandpass
        mask = (freqs >= freq_range[0]) & (freqs <= freq_range[1])
        fft[~mask] = 0

        return np.fft.irfft(fft, len(signal))

    def apply_noise(
        self,
        signal: np.ndarray,
        profile_name: str,
        snr_db: float,
        sample_rate: int = 16000
    ) -> np.ndarray:
        """
        Apply noise profile to audio signal at specified SNR.

        Args:
            signal: Clean audio signal
            profile_name: Noise profile identifier
            snr_db: Target SNR in dB
            sample_rate: Sample rate in Hz

        Returns:
            Noisy audio signal

        Example:
            >>> noisy = service.apply_noise(clean_signal, 'hvac_office', 15)
            >>> print(f"Applied noise at 15 dB SNR")
        """
        duration = len(signal) / sample_rate
        noise = self.generate_noise(profile_name, duration, sample_rate)

        # Adjust noise length to match signal
        if len(noise) > len(signal):
            noise = noise[:len(signal)]
        elif len(noise) < len(signal):
            noise = np.pad(noise, (0, len(signal) - len(noise)))

        # Calculate signal power
        signal_power = np.mean(signal ** 2)

        # Calculate noise power for desired SNR
        snr_linear = 10 ** (snr_db / 10)
        noise_power = signal_power / snr_linear

        # Scale noise
        current_noise_power = np.mean(noise ** 2)
        if current_noise_power > 0:
            noise = noise * np.sqrt(noise_power / current_noise_power)

        return (signal + noise).astype(np.float32)

    def get_profile_metrics(
        self,
        profile_name: str
    ) -> Dict[str, Any]:
        """
        Get comprehensive metrics for a noise profile.

        Args:
            profile_name: Profile identifier

        Returns:
            Dictionary with all profile metrics

        Example:
            >>> metrics = service.get_profile_metrics('car_cabin_highway')
            >>> print(f"Difficulty: {metrics['asr_difficulty']}")
        """
        profile = self.get_profile(profile_name)
        params = self.get_profile_parameters(profile_name)

        # Estimate WER increase based on difficulty
        difficulty_wer = {
            'easy': 2.0,
            'medium': 5.0,
            'hard': 15.0,
            'very_hard': 30.0,
            'extreme': 50.0
        }

        wer_increase = difficulty_wer.get(profile['asr_difficulty'], 10.0)

        return {
            'profile_name': profile_name,
            'profile_info': profile,
            'parameters': params,
            'asr_difficulty': profile['asr_difficulty'],
            'typical_snr': profile['typical_snr'],
            'estimated_wer_increase': wer_increase,
            'spectral_characteristics': {
                'bandwidth': params['bandwidth'],
                'dominant_frequency': params['dominant_frequency'],
                'spectral_shape': params['spectral_shape']
            },
            'recommended_snr_range': self._get_recommended_snr_range(profile_name)
        }

    def _get_recommended_snr_range(self, profile_name: str) -> List[float]:
        """Get recommended SNR range for testing."""
        profile = self.get_profile(profile_name)
        typical_snr = profile.get('typical_snr', 10)

        return [typical_snr - 10, typical_snr + 10]

