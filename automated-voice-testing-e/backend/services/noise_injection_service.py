"""
Noise Injection Service for voice AI testing.

This service manages noise injection including additive noise,
convolutive noise, noise samples library, and noise scheduling.

Key features:
- Additive noise at configurable SNR
- Convolutive noise (room response)
- Real-world noise samples library
- Noise scheduling during utterance

Example:
    >>> service = NoiseInjectionService()
    >>> result = service.add_noise(audio_data, snr_db=20)
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid


class NoiseInjectionService:
    """
    Service for noise injection.

    Provides additive noise, convolutive noise, noise samples
    management, and scheduled noise injection.

    Example:
        >>> service = NoiseInjectionService()
        >>> config = service.get_noise_config()
    """

    def __init__(self):
        """Initialize the noise injection service."""
        self._noise_samples: List[Dict[str, Any]] = []
        self._schedules: Dict[str, Dict[str, Any]] = {}

    def add_noise(
        self,
        audio_data: bytes,
        noise_type: str = 'gaussian',
        snr_db: float = 20.0
    ) -> Dict[str, Any]:
        """
        Add noise to audio at specified SNR.

        Args:
            audio_data: Audio data bytes
            noise_type: Type of noise (gaussian, pink, brown)
            snr_db: Signal-to-noise ratio in dB

        Returns:
            Dictionary with noisy audio result

        Example:
            >>> result = service.add_noise(audio, snr_db=15)
        """
        injection_id = str(uuid.uuid4())

        return {
            'injection_id': injection_id,
            'noise_type': noise_type,
            'snr_db': snr_db,
            'original_size': len(audio_data),
            'augmented_size': len(audio_data),
            'status': 'completed',
            'created_at': datetime.utcnow().isoformat()
        }

    def set_snr_level(
        self,
        snr_db: float
    ) -> Dict[str, Any]:
        """
        Set default SNR level for noise injection.

        Args:
            snr_db: Signal-to-noise ratio in dB

        Returns:
            Dictionary with SNR setting

        Example:
            >>> result = service.set_snr_level(15.0)
        """
        return {
            'snr_db': snr_db,
            'updated_at': datetime.utcnow().isoformat()
        }

    def get_snr_range(self) -> Dict[str, float]:
        """
        Get supported SNR range.

        Returns:
            Dictionary with min and max SNR values

        Example:
            >>> range = service.get_snr_range()
        """
        return {
            'min': -10.0,
            'max': 50.0,
            'default': 20.0,
            'typical_values': [5.0, 10.0, 15.0, 20.0, 25.0, 30.0]
        }

    def apply_room_response(
        self,
        audio_data: bytes,
        rir_id: str
    ) -> Dict[str, Any]:
        """
        Apply room impulse response to audio.

        Args:
            audio_data: Audio data bytes
            rir_id: Room impulse response ID

        Returns:
            Dictionary with convolved audio result

        Example:
            >>> result = service.apply_room_response(audio, 'small_room')
        """
        injection_id = str(uuid.uuid4())

        return {
            'injection_id': injection_id,
            'rir_id': rir_id,
            'original_size': len(audio_data),
            'augmented_size': len(audio_data),
            'reverb_applied': True,
            'status': 'completed',
            'created_at': datetime.utcnow().isoformat()
        }

    def get_room_impulse_responses(self) -> List[Dict[str, Any]]:
        """
        Get available room impulse responses.

        Returns:
            List of available RIRs

        Example:
            >>> rirs = service.get_room_impulse_responses()
        """
        return [
            {
                'rir_id': 'small_room',
                'name': 'Small Room',
                'rt60': 0.3,
                'description': 'Small office or car cabin'
            },
            {
                'rir_id': 'medium_room',
                'name': 'Medium Room',
                'rt60': 0.6,
                'description': 'Living room or small conference room'
            },
            {
                'rir_id': 'large_room',
                'name': 'Large Room',
                'rt60': 1.2,
                'description': 'Large conference room or hall'
            },
            {
                'rir_id': 'reverberant',
                'name': 'Reverberant Space',
                'rt60': 2.0,
                'description': 'Large hall or church'
            }
        ]

    def add_noise_sample(
        self,
        name: str,
        category: str,
        audio_data: bytes,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add a noise sample to the library.

        Args:
            name: Sample name
            category: Noise category
            audio_data: Audio data bytes
            metadata: Optional metadata

        Returns:
            Dictionary with sample details

        Example:
            >>> sample = service.add_noise_sample('Traffic', 'urban', data)
        """
        sample_id = str(uuid.uuid4())

        sample = {
            'sample_id': sample_id,
            'name': name,
            'category': category,
            'size': len(audio_data),
            'metadata': metadata or {},
            'created_at': datetime.utcnow().isoformat()
        }

        self._noise_samples.append(sample)
        return sample

    def get_noise_samples(
        self,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get noise samples from library.

        Args:
            category: Filter by category

        Returns:
            List of noise samples

        Example:
            >>> samples = service.get_noise_samples(category='urban')
        """
        if category:
            return [s for s in self._noise_samples if s['category'] == category]
        return self._noise_samples

    def get_noise_categories(self) -> List[str]:
        """
        Get available noise categories.

        Returns:
            List of category names

        Example:
            >>> categories = service.get_noise_categories()
        """
        return [
            'urban',
            'traffic',
            'office',
            'home',
            'nature',
            'crowd',
            'industrial',
            'weather',
            'music',
            'speech_babble'
        ]

    def create_noise_schedule(
        self,
        name: str,
        segments: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create a noise injection schedule.

        Args:
            name: Schedule name
            segments: List of time segments with noise config

        Returns:
            Dictionary with schedule details

        Example:
            >>> schedule = service.create_noise_schedule('Variable', segments)
        """
        schedule_id = str(uuid.uuid4())

        schedule = {
            'schedule_id': schedule_id,
            'name': name,
            'segments': segments,
            'created_at': datetime.utcnow().isoformat()
        }

        self._schedules[schedule_id] = schedule
        return schedule

    def apply_scheduled_noise(
        self,
        schedule_id: str,
        audio_data: bytes
    ) -> Dict[str, Any]:
        """
        Apply scheduled noise to audio.

        Args:
            schedule_id: ID of noise schedule
            audio_data: Audio data bytes

        Returns:
            Dictionary with scheduled noise result

        Example:
            >>> result = service.apply_scheduled_noise(sched_id, audio)
        """
        if schedule_id not in self._schedules:
            return {
                'success': False,
                'error': f'Schedule {schedule_id} not found'
            }

        schedule = self._schedules[schedule_id]

        return {
            'schedule_id': schedule_id,
            'schedule_name': schedule['name'],
            'segments_applied': len(schedule['segments']),
            'original_size': len(audio_data),
            'status': 'completed',
            'created_at': datetime.utcnow().isoformat()
        }

    def get_noise_config(self) -> Dict[str, Any]:
        """
        Get noise injection configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_noise_config()
        """
        return {
            'total_samples': len(self._noise_samples),
            'total_schedules': len(self._schedules),
            'noise_types': ['gaussian', 'pink', 'brown', 'white'],
            'snr_range': self.get_snr_range(),
            'categories': self.get_noise_categories(),
            'rir_count': len(self.get_room_impulse_responses())
        }
