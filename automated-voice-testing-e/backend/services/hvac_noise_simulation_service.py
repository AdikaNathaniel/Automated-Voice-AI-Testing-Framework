"""
HVAC Noise Simulation Service for voice AI testing.

This service provides HVAC and climate control noise simulation
for automotive voice AI testing.

Key features:
- Fan speed noise levels
- AC compressor cycling
- Defrost and ventilation
- Air quality systems

Example:
    >>> service = HVACNoiseSimulationService()
    >>> result = service.generate_fan_noise('high')
"""

from typing import List, Dict, Any
from datetime import datetime
import uuid


class HVACNoiseSimulationService:
    """
    Service for HVAC noise simulation testing.

    Provides automotive acoustic simulation for climate
    control systems and ventilation noise.

    Example:
        >>> service = HVACNoiseSimulationService()
        >>> config = service.get_hvac_noise_config()
    """

    def __init__(self):
        """Initialize the HVAC noise simulation service."""
        self._active_simulations: List[Dict[str, Any]] = []

    def generate_fan_noise(
        self,
        speed: str = 'medium'
    ) -> Dict[str, Any]:
        """
        Generate fan speed noise.

        Args:
            speed: Fan speed (off, low, medium, high, max)

        Returns:
            Dictionary with noise data

        Example:
            >>> result = service.generate_fan_noise('high')
        """
        noise_id = str(uuid.uuid4())

        speed_profiles = {
            'off': {'db': 0, 'freq': [], 'airflow': 0},
            'low': {'db': 35, 'freq': [100, 200, 400], 'airflow': 50},
            'medium': {'db': 45, 'freq': [100, 200, 400, 800], 'airflow': 150},
            'high': {'db': 55, 'freq': [100, 200, 400, 800, 1600], 'airflow': 250},
            'max': {'db': 65, 'freq': [100, 200, 400, 800, 1600, 3200], 'airflow': 400}
        }

        profile = speed_profiles.get(speed, speed_profiles['medium'])

        return {
            'noise_id': noise_id,
            'noise_type': 'fan',
            'speed': speed,
            'noise_level_db': profile['db'],
            'dominant_frequencies': profile['freq'],
            'airflow_cfm': profile['airflow'],
            'characteristics': ['broadband', 'steady_state'],
            'generated': True,
            'generated_at': datetime.utcnow().isoformat()
        }

    def get_fan_speed_profiles(self) -> Dict[str, Any]:
        """
        Get all fan speed noise profiles.

        Returns:
            Dictionary with all profiles

        Example:
            >>> profiles = service.get_fan_speed_profiles()
        """
        return {
            'profiles': {
                'off': {'noise_db': 0, 'description': 'Fan off'},
                'low': {'noise_db': 35, 'description': 'Low fan speed'},
                'medium': {'noise_db': 45, 'description': 'Medium fan speed'},
                'high': {'noise_db': 55, 'description': 'High fan speed'},
                'max': {'noise_db': 65, 'description': 'Maximum fan speed'}
            },
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def generate_ac_compressor_noise(
        self,
        state: str = 'on',
        compressor_type: str = 'variable'
    ) -> Dict[str, Any]:
        """
        Generate AC compressor noise.

        Args:
            state: Compressor state (on, off, cycling)
            compressor_type: Type (fixed, variable)

        Returns:
            Dictionary with noise data

        Example:
            >>> result = service.generate_ac_compressor_noise('on')
        """
        noise_id = str(uuid.uuid4())

        return {
            'noise_id': noise_id,
            'noise_type': 'ac_compressor',
            'state': state,
            'compressor_type': compressor_type,
            'noise_level_db': 40 if state == 'on' else 0,
            'dominant_frequencies': [50, 100, 150] if state == 'on' else [],
            'clutch_engagement_click': compressor_type == 'fixed',
            'characteristics': ['low_frequency_hum', 'vibration'],
            'generated': True,
            'generated_at': datetime.utcnow().isoformat()
        }

    def simulate_compressor_cycling(
        self,
        cycle_time_seconds: int = 30,
        duty_cycle_percent: int = 60
    ) -> Dict[str, Any]:
        """
        Simulate AC compressor cycling pattern.

        Args:
            cycle_time_seconds: Total cycle time
            duty_cycle_percent: Percentage on time

        Returns:
            Dictionary with cycling data

        Example:
            >>> result = service.simulate_compressor_cycling(30, 70)
        """
        simulation_id = str(uuid.uuid4())

        on_time = cycle_time_seconds * duty_cycle_percent / 100
        off_time = cycle_time_seconds - on_time

        return {
            'simulation_id': simulation_id,
            'cycle_time_seconds': cycle_time_seconds,
            'duty_cycle_percent': duty_cycle_percent,
            'on_time_seconds': on_time,
            'off_time_seconds': off_time,
            'click_on_transition': True,
            'click_off_transition': True,
            'noise_modulation': True,
            'simulated': True,
            'simulated_at': datetime.utcnow().isoformat()
        }

    def generate_defrost_noise(
        self,
        mode: str = 'front',
        fan_speed: str = 'high'
    ) -> Dict[str, Any]:
        """
        Generate defrost mode noise (high airflow).

        Args:
            mode: Defrost mode (front, rear)
            fan_speed: Associated fan speed

        Returns:
            Dictionary with noise data

        Example:
            >>> result = service.generate_defrost_noise('front', 'max')
        """
        noise_id = str(uuid.uuid4())

        return {
            'noise_id': noise_id,
            'noise_type': 'defrost',
            'mode': mode,
            'fan_speed': fan_speed,
            'noise_level_db': 60 if fan_speed in ['high', 'max'] else 50,
            'dominant_frequencies': [100, 200, 400, 800, 1600],
            'ac_engaged': mode == 'front',
            'characteristics': ['high_airflow', 'concentrated_direction'],
            'generated': True,
            'generated_at': datetime.utcnow().isoformat()
        }

    def generate_seat_ventilation_noise(
        self,
        seat: str = 'driver',
        level: int = 3
    ) -> Dict[str, Any]:
        """
        Generate seat ventilation fan noise.

        Args:
            seat: Seat position (driver, passenger)
            level: Ventilation level (1-5)

        Returns:
            Dictionary with noise data

        Example:
            >>> result = service.generate_seat_ventilation_noise('driver', 3)
        """
        noise_id = str(uuid.uuid4())

        noise_db = 25 + (level * 5)

        return {
            'noise_id': noise_id,
            'noise_type': 'seat_ventilation',
            'seat': seat,
            'level': level,
            'noise_level_db': noise_db,
            'dominant_frequencies': [200, 400, 800],
            'localized_noise': True,
            'characteristics': ['localized', 'small_fan'],
            'generated': True,
            'generated_at': datetime.utcnow().isoformat()
        }

    def generate_air_filter_noise(
        self,
        filter_type: str = 'hepa',
        clogging_percent: int = 0
    ) -> Dict[str, Any]:
        """
        Generate air quality filter noise.

        Args:
            filter_type: Filter type (standard, hepa, activated_carbon)
            clogging_percent: Filter clogging level

        Returns:
            Dictionary with noise data

        Example:
            >>> result = service.generate_air_filter_noise('hepa', 30)
        """
        noise_id = str(uuid.uuid4())

        base_noise = {'standard': 5, 'hepa': 8, 'activated_carbon': 10}
        noise_db = base_noise.get(filter_type, 5) + (clogging_percent * 0.1)

        return {
            'noise_id': noise_id,
            'noise_type': 'air_filter',
            'filter_type': filter_type,
            'clogging_percent': clogging_percent,
            'noise_level_db': noise_db,
            'dominant_frequencies': [100, 200],
            'airflow_restriction': clogging_percent > 50,
            'characteristics': ['air_resistance', 'turbulence'],
            'generated': True,
            'generated_at': datetime.utcnow().isoformat()
        }

    def get_supported_hvac_modes(self) -> List[str]:
        """
        Get list of supported HVAC modes.

        Returns:
            List of mode names

        Example:
            >>> modes = service.get_supported_hvac_modes()
        """
        return [
            'off', 'face', 'feet', 'face_feet', 'defrost_front',
            'defrost_rear', 'recirculation', 'auto'
        ]

    def get_hvac_noise_config(self) -> Dict[str, Any]:
        """
        Get HVAC noise simulation configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_hvac_noise_config()
        """
        return {
            'active_simulations_count': len(self._active_simulations),
            'features': [
                'fan_speed_noise', 'ac_compressor',
                'compressor_cycling', 'defrost_mode',
                'seat_ventilation', 'air_filter'
            ]
        }
