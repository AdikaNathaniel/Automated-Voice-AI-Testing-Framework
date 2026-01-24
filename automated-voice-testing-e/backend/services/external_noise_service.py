"""
External Noise Intrusion Service for voice AI testing.

This service provides external noise simulation for
automotive voice AI testing with environmental sounds.

Key features:
- Traffic noise
- Construction zones
- Emergency vehicles
- Environmental noise

Example:
    >>> service = ExternalNoiseService()
    >>> result = service.generate_traffic_noise('highway')
"""

from typing import List, Dict, Any
from datetime import datetime
import uuid


class ExternalNoiseService:
    """
    Service for external noise intrusion simulation.

    Provides automotive acoustic simulation for various
    environmental and external noise sources.

    Example:
        >>> service = ExternalNoiseService()
        >>> config = service.get_external_noise_config()
    """

    def __init__(self):
        """Initialize the external noise service."""
        self._active_simulations: List[Dict[str, Any]] = []

    def generate_traffic_noise(
        self,
        traffic_type: str = 'highway',
        density: str = 'moderate'
    ) -> Dict[str, Any]:
        """
        Generate traffic noise from other vehicles.

        Args:
            traffic_type: Type (highway, city, rural)
            density: Traffic density (light, moderate, heavy)

        Returns:
            Dictionary with noise data

        Example:
            >>> result = service.generate_traffic_noise('highway', 'heavy')
        """
        noise_id = str(uuid.uuid4())

        type_config = {
            'highway': {'base_db': 70, 'freq': [125, 250, 500, 1000]},
            'city': {'base_db': 65, 'freq': [100, 250, 500, 1000, 2000]},
            'rural': {'base_db': 50, 'freq': [100, 250, 500]}
        }

        density_modifier = {'light': -5, 'moderate': 0, 'heavy': 8}

        config = type_config.get(traffic_type, type_config['highway'])
        modifier = density_modifier.get(density, 0)

        return {
            'noise_id': noise_id,
            'noise_type': 'traffic',
            'traffic_type': traffic_type,
            'density': density,
            'noise_level_db': config['base_db'] + modifier,
            'dominant_frequencies': config['freq'],
            'passing_vehicles': density == 'heavy',
            'characteristics': ['continuous', 'varying_doppler', 'engine_tire_mix'],
            'generated': True,
            'generated_at': datetime.utcnow().isoformat()
        }

    def generate_construction_noise(
        self,
        equipment: str = 'mixed',
        distance_meters: int = 50
    ) -> Dict[str, Any]:
        """
        Generate construction zone noise.

        Args:
            equipment: Equipment type (jackhammer, excavator, mixed)
            distance_meters: Distance from construction

        Returns:
            Dictionary with noise data

        Example:
            >>> result = service.generate_construction_noise('jackhammer', 30)
        """
        noise_id = str(uuid.uuid4())

        equipment_config = {
            'jackhammer': {'base_db': 95, 'freq': [500, 1000, 2000], 'impulsive': True},
            'excavator': {'base_db': 85, 'freq': [100, 200, 500], 'impulsive': False},
            'mixed': {'base_db': 90, 'freq': [100, 500, 1000, 2000], 'impulsive': True}
        }

        config = equipment_config.get(equipment, equipment_config['mixed'])

        # Distance attenuation (6 dB per doubling of distance from 10m reference)
        attenuation = 20 * (distance_meters / 10) if distance_meters > 10 else 0

        return {
            'noise_id': noise_id,
            'noise_type': 'construction',
            'equipment': equipment,
            'distance_meters': distance_meters,
            'noise_level_db': max(config['base_db'] - attenuation, 40),
            'dominant_frequencies': config['freq'],
            'impulsive_noise': config['impulsive'],
            'characteristics': ['loud_bursts', 'low_frequency', 'irregular'],
            'generated': True,
            'generated_at': datetime.utcnow().isoformat()
        }

    def generate_siren_noise(
        self,
        vehicle_type: str = 'ambulance',
        approach: str = 'passing'
    ) -> Dict[str, Any]:
        """
        Generate emergency vehicle siren noise.

        Args:
            vehicle_type: Vehicle type (ambulance, fire, police)
            approach: Approach state (approaching, passing, receding)

        Returns:
            Dictionary with noise data

        Example:
            >>> result = service.generate_siren_noise('fire', 'approaching')
        """
        noise_id = str(uuid.uuid4())

        vehicle_config = {
            'ambulance': {'db': 110, 'freq': [500, 1000, 1500]},
            'fire': {'db': 115, 'freq': [300, 600, 900]},
            'police': {'db': 105, 'freq': [600, 1200, 1800]}
        }

        approach_modifier = {
            'approaching': 0,
            'passing': -5,
            'receding': -15
        }

        config = vehicle_config.get(vehicle_type, vehicle_config['ambulance'])
        modifier = approach_modifier.get(approach, 0)

        return {
            'noise_id': noise_id,
            'noise_type': 'siren',
            'vehicle_type': vehicle_type,
            'approach': approach,
            'noise_level_db': config['db'] + modifier,
            'dominant_frequencies': config['freq'],
            'doppler_effect': approach != 'passing',
            'wailing_pattern': True,
            'characteristics': ['attention_grabbing', 'modulated', 'high_priority'],
            'generated': True,
            'generated_at': datetime.utcnow().isoformat()
        }

    def generate_train_crossing_noise(
        self,
        train_type: str = 'freight',
        distance_meters: int = 30
    ) -> Dict[str, Any]:
        """
        Generate train crossing noise.

        Args:
            train_type: Train type (freight, passenger, high_speed)
            distance_meters: Distance from crossing

        Returns:
            Dictionary with noise data

        Example:
            >>> result = service.generate_train_crossing_noise('freight', 50)
        """
        noise_id = str(uuid.uuid4())

        train_config = {
            'freight': {'db': 100, 'duration_sec': 60},
            'passenger': {'db': 90, 'duration_sec': 15},
            'high_speed': {'db': 95, 'duration_sec': 8}
        }

        config = train_config.get(train_type, train_config['freight'])
        attenuation = 10 * (distance_meters / 30) if distance_meters > 30 else 0

        return {
            'noise_id': noise_id,
            'noise_type': 'train_crossing',
            'train_type': train_type,
            'distance_meters': distance_meters,
            'noise_level_db': max(config['db'] - attenuation, 50),
            'dominant_frequencies': [50, 100, 200, 500],
            'crossing_bells': True,
            'horn_blasts': True,
            'duration_seconds': config['duration_sec'],
            'characteristics': ['rumbling', 'horn_signals', 'bells'],
            'generated': True,
            'generated_at': datetime.utcnow().isoformat()
        }

    def generate_airport_noise(
        self,
        aircraft_type: str = 'jet',
        phase: str = 'flyover'
    ) -> Dict[str, Any]:
        """
        Generate airport proximity noise.

        Args:
            aircraft_type: Aircraft type (jet, prop, helicopter)
            phase: Flight phase (takeoff, landing, flyover)

        Returns:
            Dictionary with noise data

        Example:
            >>> result = service.generate_airport_noise('jet', 'takeoff')
        """
        noise_id = str(uuid.uuid4())

        aircraft_config = {
            'jet': {'db': 105, 'freq': [250, 500, 1000, 2000]},
            'prop': {'db': 85, 'freq': [100, 200, 500]},
            'helicopter': {'db': 90, 'freq': [50, 100, 200, 500]}
        }

        phase_modifier = {
            'takeoff': 5,
            'landing': 0,
            'flyover': -5
        }

        config = aircraft_config.get(aircraft_type, aircraft_config['jet'])
        modifier = phase_modifier.get(phase, 0)

        return {
            'noise_id': noise_id,
            'noise_type': 'airport',
            'aircraft_type': aircraft_type,
            'phase': phase,
            'noise_level_db': config['db'] + modifier,
            'dominant_frequencies': config['freq'],
            'duration_seconds': 30,
            'characteristics': ['low_frequency_rumble', 'jet_whine', 'fading'],
            'generated': True,
            'generated_at': datetime.utcnow().isoformat()
        }

    def generate_urban_noise(
        self,
        environment: str = 'downtown',
        time_of_day: str = 'day'
    ) -> Dict[str, Any]:
        """
        Generate urban environment noise (horns, etc.).

        Args:
            environment: Environment type (downtown, residential, industrial)
            time_of_day: Time (day, night)

        Returns:
            Dictionary with noise data

        Example:
            >>> result = service.generate_urban_noise('downtown', 'day')
        """
        noise_id = str(uuid.uuid4())

        env_config = {
            'downtown': {'db': 75, 'sources': ['traffic', 'horns', 'pedestrians', 'construction']},
            'residential': {'db': 55, 'sources': ['light_traffic', 'birds', 'lawn_equipment']},
            'industrial': {'db': 80, 'sources': ['machinery', 'trucks', 'loading_docks']}
        }

        time_modifier = {'day': 0, 'night': -10}

        config = env_config.get(environment, env_config['downtown'])
        modifier = time_modifier.get(time_of_day, 0)

        return {
            'noise_id': noise_id,
            'noise_type': 'urban',
            'environment': environment,
            'time_of_day': time_of_day,
            'noise_level_db': config['db'] + modifier,
            'dominant_frequencies': [100, 250, 500, 1000, 2000],
            'noise_sources': config['sources'],
            'characteristics': ['continuous', 'varied', 'unpredictable_events'],
            'generated': True,
            'generated_at': datetime.utcnow().isoformat()
        }

    def get_supported_environments(self) -> List[str]:
        """
        Get list of supported noise environments.

        Returns:
            List of environment names

        Example:
            >>> envs = service.get_supported_environments()
        """
        return [
            'highway_traffic', 'city_traffic', 'construction',
            'emergency_siren', 'train_crossing', 'airport',
            'downtown_urban', 'residential', 'industrial'
        ]

    def get_external_noise_config(self) -> Dict[str, Any]:
        """
        Get external noise configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_external_noise_config()
        """
        return {
            'active_simulations_count': len(self._active_simulations),
            'features': [
                'traffic_noise', 'construction_noise',
                'siren_noise', 'train_crossing',
                'airport_noise', 'urban_noise'
            ]
        }
