"""
In-Vehicle Noise Simulation Service for voice AI testing.

This service provides in-vehicle noise simulation for
automotive voice AI testing with various sound sources.

Key features:
- Vehicle sounds (signals, wipers)
- Weather sounds
- Occupant sounds
- Electronic devices

Example:
    >>> service = InVehicleNoiseService()
    >>> result = service.generate_turn_signal_noise()
"""

from typing import List, Dict, Any
from datetime import datetime
import uuid


class InVehicleNoiseService:
    """
    Service for in-vehicle noise simulation.

    Provides automotive acoustic simulation for various
    interior sound sources.

    Example:
        >>> service = InVehicleNoiseService()
        >>> config = service.get_invehicle_noise_config()
    """

    def __init__(self):
        """Initialize the in-vehicle noise service."""
        self._active_simulations: List[Dict[str, Any]] = []

    def generate_turn_signal_noise(
        self,
        signal_type: str = 'standard',
        rate_bpm: int = 90
    ) -> Dict[str, Any]:
        """
        Generate turn signal clicking noise.

        Args:
            signal_type: Type (standard, led, hazard)
            rate_bpm: Click rate in beats per minute

        Returns:
            Dictionary with noise data

        Example:
            >>> result = service.generate_turn_signal_noise()
        """
        noise_id = str(uuid.uuid4())

        return {
            'noise_id': noise_id,
            'noise_type': 'turn_signal',
            'signal_type': signal_type,
            'rate_bpm': rate_bpm,
            'noise_level_db': 45,
            'dominant_frequencies': [1000, 2000, 4000],
            'click_duration_ms': 50,
            'characteristics': ['periodic', 'sharp_attack', 'localized'],
            'generated': True,
            'generated_at': datetime.utcnow().isoformat()
        }

    def generate_wiper_noise(
        self,
        speed: str = 'intermittent',
        rain_present: bool = False
    ) -> Dict[str, Any]:
        """
        Generate windshield wiper operation noise.

        Args:
            speed: Wiper speed (off, intermittent, low, high)
            rain_present: Whether rain is present

        Returns:
            Dictionary with noise data

        Example:
            >>> result = service.generate_wiper_noise('low', True)
        """
        noise_id = str(uuid.uuid4())

        speed_config = {
            'off': {'db': 0, 'rpm': 0},
            'intermittent': {'db': 40, 'rpm': 15},
            'low': {'db': 45, 'rpm': 30},
            'high': {'db': 50, 'rpm': 45}
        }

        config = speed_config.get(speed, speed_config['intermittent'])

        return {
            'noise_id': noise_id,
            'noise_type': 'wiper',
            'speed': speed,
            'wipe_rpm': config['rpm'],
            'noise_level_db': config['db'] + (5 if rain_present else 0),
            'dominant_frequencies': [100, 200, 500],
            'squeaking': not rain_present and speed != 'off',
            'characteristics': ['periodic_sweep', 'rubber_on_glass'],
            'generated': True,
            'generated_at': datetime.utcnow().isoformat()
        }

    def generate_rain_noise(
        self,
        intensity: str = 'moderate',
        surface: str = 'roof'
    ) -> Dict[str, Any]:
        """
        Generate rain on roof/windshield noise.

        Args:
            intensity: Rain intensity (light, moderate, heavy, torrential)
            surface: Impact surface (roof, windshield)

        Returns:
            Dictionary with noise data

        Example:
            >>> result = service.generate_rain_noise('heavy', 'roof')
        """
        noise_id = str(uuid.uuid4())

        intensity_config = {
            'light': {'db': 35, 'drops_per_sec': 10},
            'moderate': {'db': 50, 'drops_per_sec': 50},
            'heavy': {'db': 65, 'drops_per_sec': 200},
            'torrential': {'db': 75, 'drops_per_sec': 500}
        }

        config = intensity_config.get(intensity, intensity_config['moderate'])

        return {
            'noise_id': noise_id,
            'noise_type': 'rain',
            'intensity': intensity,
            'surface': surface,
            'noise_level_db': config['db'],
            'drops_per_second': config['drops_per_sec'],
            'dominant_frequencies': [500, 1000, 2000, 4000, 8000],
            'characteristics': ['broadband', 'random_impacts', 'masking'],
            'generated': True,
            'generated_at': datetime.utcnow().isoformat()
        }

    def generate_audio_system_noise(
        self,
        volume_percent: int = 50,
        content_type: str = 'music'
    ) -> Dict[str, Any]:
        """
        Generate audio system noise at various volumes.

        Args:
            volume_percent: Volume level (0-100)
            content_type: Content type (music, talk, podcast)

        Returns:
            Dictionary with noise data

        Example:
            >>> result = service.generate_audio_system_noise(70, 'music')
        """
        noise_id = str(uuid.uuid4())

        max_db = 95
        noise_db = (volume_percent / 100) * max_db

        return {
            'noise_id': noise_id,
            'noise_type': 'audio_system',
            'volume_percent': volume_percent,
            'content_type': content_type,
            'noise_level_db': noise_db,
            'dominant_frequencies': [100, 500, 1000, 4000, 8000] if content_type == 'music' else [200, 500, 2000],
            'bass_heavy': content_type == 'music' and volume_percent > 60,
            'characteristics': ['fullband' if content_type == 'music' else 'speech_spectrum'],
            'generated': True,
            'generated_at': datetime.utcnow().isoformat()
        }

    def generate_passenger_conversation(
        self,
        num_speakers: int = 2,
        loudness: str = 'normal'
    ) -> Dict[str, Any]:
        """
        Generate passenger conversation noise.

        Args:
            num_speakers: Number of speakers
            loudness: Conversation loudness (quiet, normal, loud)

        Returns:
            Dictionary with noise data

        Example:
            >>> result = service.generate_passenger_conversation(3, 'loud')
        """
        noise_id = str(uuid.uuid4())

        loudness_db = {'quiet': 50, 'normal': 60, 'loud': 70}
        db = loudness_db.get(loudness, 60)

        return {
            'noise_id': noise_id,
            'noise_type': 'passenger_conversation',
            'num_speakers': num_speakers,
            'loudness': loudness,
            'noise_level_db': db + (num_speakers * 2),
            'dominant_frequencies': [200, 500, 1000, 2000],
            'overlapping_speech': num_speakers > 2,
            'characteristics': ['speech', 'varying_levels', 'semantic_interference'],
            'generated': True,
            'generated_at': datetime.utcnow().isoformat()
        }

    def generate_children_noise(
        self,
        num_children: int = 2,
        activity: str = 'playing'
    ) -> Dict[str, Any]:
        """
        Generate children in back seat noise.

        Args:
            num_children: Number of children
            activity: Activity (quiet, playing, crying)

        Returns:
            Dictionary with noise data

        Example:
            >>> result = service.generate_children_noise(2, 'playing')
        """
        noise_id = str(uuid.uuid4())

        activity_db = {'quiet': 45, 'playing': 65, 'crying': 80}
        db = activity_db.get(activity, 65)

        return {
            'noise_id': noise_id,
            'noise_type': 'children',
            'num_children': num_children,
            'activity': activity,
            'noise_level_db': db + (num_children * 3),
            'dominant_frequencies': [500, 1000, 2000, 4000],
            'high_pitch': True,
            'characteristics': ['unpredictable', 'high_frequency', 'distracting'],
            'generated': True,
            'generated_at': datetime.utcnow().isoformat()
        }

    def generate_pet_noise(
        self,
        pet_type: str = 'dog',
        activity: str = 'quiet'
    ) -> Dict[str, Any]:
        """
        Generate pet sound noise.

        Args:
            pet_type: Type of pet (dog, cat)
            activity: Activity (quiet, panting, barking, meowing)

        Returns:
            Dictionary with noise data

        Example:
            >>> result = service.generate_pet_noise('dog', 'barking')
        """
        noise_id = str(uuid.uuid4())

        activity_config = {
            'quiet': {'db': 30, 'char': 'minimal'},
            'panting': {'db': 45, 'char': 'rhythmic_breathing'},
            'barking': {'db': 85, 'char': 'loud_bursts'},
            'meowing': {'db': 65, 'char': 'tonal'}
        }

        config = activity_config.get(activity, activity_config['quiet'])

        return {
            'noise_id': noise_id,
            'noise_type': 'pet',
            'pet_type': pet_type,
            'activity': activity,
            'noise_level_db': config['db'],
            'dominant_frequencies': [250, 500, 1000, 2000],
            'characteristics': [config['char'], 'unpredictable'],
            'generated': True,
            'generated_at': datetime.utcnow().isoformat()
        }

    def generate_eating_noise(
        self,
        activity: str = 'eating',
        intensity: str = 'normal'
    ) -> Dict[str, Any]:
        """
        Generate eating/drinking sound noise.

        Args:
            activity: Activity (eating, drinking, unwrapping)
            intensity: Sound intensity (quiet, normal, loud)

        Returns:
            Dictionary with noise data

        Example:
            >>> result = service.generate_eating_noise('eating', 'normal')
        """
        noise_id = str(uuid.uuid4())

        intensity_db = {'quiet': 35, 'normal': 45, 'loud': 55}
        db = intensity_db.get(intensity, 45)

        return {
            'noise_id': noise_id,
            'noise_type': 'eating',
            'activity': activity,
            'intensity': intensity,
            'noise_level_db': db,
            'dominant_frequencies': [500, 1000, 2000, 4000],
            'localized': True,
            'characteristics': ['crunching', 'rustling', 'slurping'],
            'generated': True,
            'generated_at': datetime.utcnow().isoformat()
        }

    def generate_phone_notification_noise(
        self,
        notification_type: str = 'ringtone',
        volume: str = 'normal'
    ) -> Dict[str, Any]:
        """
        Generate phone ringing/notification noise.

        Args:
            notification_type: Type (ringtone, message, alert)
            volume: Volume level (silent, vibrate, normal, loud)

        Returns:
            Dictionary with noise data

        Example:
            >>> result = service.generate_phone_notification_noise('ringtone', 'loud')
        """
        noise_id = str(uuid.uuid4())

        volume_db = {'silent': 0, 'vibrate': 35, 'normal': 65, 'loud': 80}
        db = volume_db.get(volume, 65)

        return {
            'noise_id': noise_id,
            'noise_type': 'phone_notification',
            'notification_type': notification_type,
            'volume': volume,
            'noise_level_db': db,
            'dominant_frequencies': [1000, 2000, 4000],
            'duration_seconds': 3 if notification_type == 'ringtone' else 1,
            'characteristics': ['tonal', 'attention_grabbing', 'periodic'],
            'generated': True,
            'generated_at': datetime.utcnow().isoformat()
        }

    def get_supported_noise_types(self) -> List[str]:
        """
        Get list of supported noise types.

        Returns:
            List of noise type names

        Example:
            >>> types = service.get_supported_noise_types()
        """
        return [
            'turn_signal', 'wiper', 'rain', 'audio_system',
            'passenger_conversation', 'children', 'pet',
            'eating', 'phone_notification'
        ]

    def get_invehicle_noise_config(self) -> Dict[str, Any]:
        """
        Get in-vehicle noise configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_invehicle_noise_config()
        """
        return {
            'active_simulations_count': len(self._active_simulations),
            'features': [
                'turn_signal', 'wiper', 'rain',
                'audio_system', 'passenger_conversation',
                'children', 'pet', 'eating', 'phone_notification'
            ]
        }
