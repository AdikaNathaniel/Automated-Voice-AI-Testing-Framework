"""
Network Impairment Simulation Service for testing.

This service provides network condition simulation
for testing voice AI systems under various conditions.

Key features:
- Latency injection
- Packet loss simulation
- Jitter simulation
- Network profiles

Example:
    >>> service = NetworkImpairmentService()
    >>> service.set_latency(100)
    >>> service.set_packet_loss(1.0)
    >>> service.apply_profile('3G')
"""

from typing import List, Dict, Any
from datetime import datetime
import random


class NetworkImpairmentService:
    """
    Service for network impairment simulation.

    Provides latency injection, packet loss simulation,
    jitter, bandwidth throttling, and network profiles.

    Example:
        >>> service = NetworkImpairmentService()
        >>> service.apply_profile('4G')
        >>> delay = service.get_current_latency()
        >>> print(f"Latency: {delay['latency_ms']} ms")
    """

    def __init__(self):
        """Initialize the network impairment service."""
        self._enabled = False
        self._latency_ms = 0
        self._latency_variation = 0
        self._packet_loss_rate = 0.0
        self._burst_loss_length = 0
        self._jitter_ms = 0
        self._bandwidth_kbps = 0
        self._profiles: Dict[str, Dict[str, Any]] = self._init_profiles()
        self._custom_profiles: List[Dict[str, Any]] = []

    def _init_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Initialize default network profiles."""
        return {
            '3G': {
                'latency_ms': 200,
                'latency_variation': 50,
                'packet_loss': 2.0,
                'jitter_ms': 30,
                'bandwidth_kbps': 1500
            },
            '4G': {
                'latency_ms': 50,
                'latency_variation': 20,
                'packet_loss': 0.5,
                'jitter_ms': 10,
                'bandwidth_kbps': 10000
            },
            'WiFi': {
                'latency_ms': 30,
                'latency_variation': 10,
                'packet_loss': 0.1,
                'jitter_ms': 5,
                'bandwidth_kbps': 50000
            },
            'Satellite': {
                'latency_ms': 600,
                'latency_variation': 100,
                'packet_loss': 1.0,
                'jitter_ms': 50,
                'bandwidth_kbps': 2000
            },
            'LAN': {
                'latency_ms': 1,
                'latency_variation': 0,
                'packet_loss': 0.0,
                'jitter_ms': 0,
                'bandwidth_kbps': 1000000
            }
        }

    def set_latency(
        self,
        latency_ms: int
    ) -> Dict[str, Any]:
        """
        Set base latency.

        Args:
            latency_ms: Latency in milliseconds

        Returns:
            Dictionary with latency setting

        Example:
            >>> result = service.set_latency(100)
        """
        self._latency_ms = latency_ms
        return {
            'latency_ms': latency_ms,
            'configured': True
        }

    def add_latency_variation(
        self,
        variation_ms: int
    ) -> Dict[str, Any]:
        """
        Add latency variation.

        Args:
            variation_ms: Variation in milliseconds

        Returns:
            Dictionary with variation setting

        Example:
            >>> result = service.add_latency_variation(20)
        """
        self._latency_variation = variation_ms
        return {
            'variation_ms': variation_ms,
            'configured': True
        }

    def get_current_latency(self) -> Dict[str, Any]:
        """
        Get current effective latency.

        Returns:
            Dictionary with latency values

        Example:
            >>> latency = service.get_current_latency()
        """
        # Calculate effective latency with variation
        variation = 0
        if self._latency_variation > 0:
            variation = random.randint(
                -self._latency_variation,
                self._latency_variation
            )

        effective = max(0, self._latency_ms + variation)

        return {
            'base_latency_ms': self._latency_ms,
            'variation_ms': self._latency_variation,
            'effective_latency_ms': effective
        }

    def set_packet_loss(
        self,
        loss_rate: float
    ) -> Dict[str, Any]:
        """
        Set packet loss rate.

        Args:
            loss_rate: Loss rate percentage (0-100)

        Returns:
            Dictionary with loss setting

        Example:
            >>> result = service.set_packet_loss(1.5)
        """
        self._packet_loss_rate = loss_rate
        return {
            'loss_rate': loss_rate,
            'configured': True
        }

    def set_burst_loss(
        self,
        burst_length: int
    ) -> Dict[str, Any]:
        """
        Set burst loss length.

        Args:
            burst_length: Number of consecutive packets to lose

        Returns:
            Dictionary with burst setting

        Example:
            >>> result = service.set_burst_loss(3)
        """
        self._burst_loss_length = burst_length
        return {
            'burst_length': burst_length,
            'configured': True
        }

    def should_drop_packet(self) -> bool:
        """
        Determine if packet should be dropped.

        Returns:
            True if packet should be dropped

        Example:
            >>> if service.should_drop_packet():
            ...     # Drop the packet
        """
        if not self._enabled:
            return False

        if self._packet_loss_rate <= 0:
            return False

        return random.random() * 100 < self._packet_loss_rate

    def set_jitter(
        self,
        jitter_ms: int
    ) -> Dict[str, Any]:
        """
        Set jitter.

        Args:
            jitter_ms: Jitter in milliseconds

        Returns:
            Dictionary with jitter setting

        Example:
            >>> result = service.set_jitter(15)
        """
        self._jitter_ms = jitter_ms
        return {
            'jitter_ms': jitter_ms,
            'configured': True
        }

    def get_jitter_delay(self) -> Dict[str, Any]:
        """
        Get jitter-induced delay.

        Returns:
            Dictionary with jitter delay

        Example:
            >>> jitter = service.get_jitter_delay()
        """
        delay = 0
        if self._jitter_ms > 0:
            delay = random.randint(0, self._jitter_ms)

        return {
            'max_jitter_ms': self._jitter_ms,
            'delay_ms': delay
        }

    def set_bandwidth(
        self,
        bandwidth_kbps: int
    ) -> Dict[str, Any]:
        """
        Set bandwidth limit.

        Args:
            bandwidth_kbps: Bandwidth in kbps

        Returns:
            Dictionary with bandwidth setting

        Example:
            >>> result = service.set_bandwidth(1000)
        """
        self._bandwidth_kbps = bandwidth_kbps
        return {
            'bandwidth_kbps': bandwidth_kbps,
            'configured': True
        }

    def get_throttle_delay(
        self,
        packet_size_bytes: int
    ) -> Dict[str, Any]:
        """
        Get throttle delay for packet.

        Args:
            packet_size_bytes: Size of packet in bytes

        Returns:
            Dictionary with throttle delay

        Example:
            >>> delay = service.get_throttle_delay(1500)
        """
        delay_ms = 0
        if self._bandwidth_kbps > 0:
            # Calculate delay based on bandwidth
            bits = packet_size_bytes * 8
            delay_ms = (bits / self._bandwidth_kbps) * 1000

        return {
            'packet_size_bytes': packet_size_bytes,
            'delay_ms': delay_ms,
            'bandwidth_kbps': self._bandwidth_kbps
        }

    def apply_profile(
        self,
        profile_name: str
    ) -> Dict[str, Any]:
        """
        Apply a network profile.

        Args:
            profile_name: Name of profile to apply

        Returns:
            Dictionary with applied profile settings

        Example:
            >>> result = service.apply_profile('4G')
        """
        profile = self._profiles.get(profile_name)
        if not profile:
            return {'error': 'Profile not found'}

        self._latency_ms = profile['latency_ms']
        self._latency_variation = profile['latency_variation']
        self._packet_loss_rate = profile['packet_loss']
        self._jitter_ms = profile['jitter_ms']
        self._bandwidth_kbps = profile['bandwidth_kbps']
        self._enabled = True

        return {
            'profile': profile_name,
            'applied': True,
            'settings': profile
        }

    def get_available_profiles(self) -> List[str]:
        """
        Get list of available profiles.

        Returns:
            List of profile names

        Example:
            >>> profiles = service.get_available_profiles()
        """
        return list(self._profiles.keys())

    def create_custom_profile(
        self,
        name: str,
        latency_ms: int = 0,
        latency_variation: int = 0,
        packet_loss: float = 0.0,
        jitter_ms: int = 0,
        bandwidth_kbps: int = 0
    ) -> Dict[str, Any]:
        """
        Create a custom network profile.

        Args:
            name: Profile name
            latency_ms: Base latency
            latency_variation: Latency variation
            packet_loss: Packet loss rate
            jitter_ms: Jitter
            bandwidth_kbps: Bandwidth limit

        Returns:
            Dictionary with profile configuration

        Example:
            >>> profile = service.create_custom_profile('custom', 150, 25)
        """
        profile = {
            'latency_ms': latency_ms,
            'latency_variation': latency_variation,
            'packet_loss': packet_loss,
            'jitter_ms': jitter_ms,
            'bandwidth_kbps': bandwidth_kbps
        }
        self._profiles[name] = profile
        self._custom_profiles.append({'name': name, **profile})

        return {
            'name': name,
            'created': True,
            'settings': profile
        }

    def enable_impairment(self) -> Dict[str, Any]:
        """
        Enable network impairment.

        Returns:
            Dictionary with enable result

        Example:
            >>> result = service.enable_impairment()
        """
        self._enabled = True
        return {
            'enabled': True,
            'timestamp': datetime.utcnow().isoformat()
        }

    def disable_impairment(self) -> Dict[str, Any]:
        """
        Disable network impairment.

        Returns:
            Dictionary with disable result

        Example:
            >>> result = service.disable_impairment()
        """
        self._enabled = False
        return {
            'enabled': False,
            'timestamp': datetime.utcnow().isoformat()
        }

    def reset_all(self) -> Dict[str, Any]:
        """
        Reset all impairment settings.

        Returns:
            Dictionary with reset result

        Example:
            >>> result = service.reset_all()
        """
        self._enabled = False
        self._latency_ms = 0
        self._latency_variation = 0
        self._packet_loss_rate = 0.0
        self._burst_loss_length = 0
        self._jitter_ms = 0
        self._bandwidth_kbps = 0

        return {
            'reset': True,
            'timestamp': datetime.utcnow().isoformat()
        }

    def get_current_settings(self) -> Dict[str, Any]:
        """
        Get current impairment settings.

        Returns:
            Dictionary with all current settings

        Example:
            >>> settings = service.get_current_settings()
        """
        return {
            'enabled': self._enabled,
            'latency_ms': self._latency_ms,
            'latency_variation': self._latency_variation,
            'packet_loss_rate': self._packet_loss_rate,
            'burst_loss_length': self._burst_loss_length,
            'jitter_ms': self._jitter_ms,
            'bandwidth_kbps': self._bandwidth_kbps
        }

    def get_packet_loss(self) -> Dict[str, Any]:
        """
        Get current packet loss settings.

        Returns:
            Dictionary with packet loss configuration

        Example:
            >>> loss = service.get_packet_loss()
        """
        return {
            'loss_rate': self._packet_loss_rate,
            'burst_length': self._burst_loss_length,
            'enabled': self._enabled
        }

    def apply_packet_loss(
        self,
        packet_data: bytes
    ) -> Dict[str, Any]:
        """
        Apply packet loss to data.

        Args:
            packet_data: The packet data to process

        Returns:
            Dictionary with packet loss result

        Example:
            >>> result = service.apply_packet_loss(b'data')
        """
        dropped = self.should_drop_packet()
        return {
            'dropped': dropped,
            'packet_size': len(packet_data),
            'loss_rate': self._packet_loss_rate
        }

    def get_jitter(self) -> Dict[str, Any]:
        """
        Get current jitter settings.

        Returns:
            Dictionary with jitter configuration

        Example:
            >>> jitter = service.get_jitter()
        """
        return {
            'jitter_ms': self._jitter_ms,
            'enabled': self._enabled
        }

    def apply_jitter(
        self,
        packet_data: bytes
    ) -> Dict[str, Any]:
        """
        Apply jitter to packet timing.

        Args:
            packet_data: The packet data to process

        Returns:
            Dictionary with jitter delay result

        Example:
            >>> result = service.apply_jitter(b'data')
        """
        jitter_delay = self.get_jitter_delay()
        return {
            'delay_ms': jitter_delay['delay_ms'],
            'packet_size': len(packet_data),
            'jitter_ms': self._jitter_ms
        }

    def get_latency(self) -> Dict[str, Any]:
        """
        Get current latency settings.

        Returns:
            Dictionary with latency configuration

        Example:
            >>> latency = service.get_latency()
        """
        return {
            'latency_ms': self._latency_ms,
            'variation_ms': self._latency_variation,
            'enabled': self._enabled
        }

    def apply_latency(
        self,
        packet_data: bytes
    ) -> Dict[str, Any]:
        """
        Apply latency to packet.

        Args:
            packet_data: The packet data to process

        Returns:
            Dictionary with latency delay result

        Example:
            >>> result = service.apply_latency(b'data')
        """
        latency = self.get_current_latency()
        return {
            'delay_ms': latency['effective_latency_ms'],
            'packet_size': len(packet_data),
            'base_latency_ms': self._latency_ms
        }

    def get_bandwidth(self) -> Dict[str, Any]:
        """
        Get current bandwidth settings.

        Returns:
            Dictionary with bandwidth configuration

        Example:
            >>> bandwidth = service.get_bandwidth()
        """
        return {
            'bandwidth_kbps': self._bandwidth_kbps,
            'enabled': self._enabled
        }

    def apply_bandwidth_limit(
        self,
        packet_data: bytes
    ) -> Dict[str, Any]:
        """
        Apply bandwidth limitation to packet.

        Args:
            packet_data: The packet data to process

        Returns:
            Dictionary with bandwidth throttle result

        Example:
            >>> result = service.apply_bandwidth_limit(b'data')
        """
        throttle = self.get_throttle_delay(len(packet_data))
        return {
            'delay_ms': throttle['delay_ms'],
            'packet_size': len(packet_data),
            'bandwidth_kbps': self._bandwidth_kbps
        }

    def create_profile(
        self,
        name: str,
        settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a new network profile.

        Args:
            name: Profile name
            settings: Profile settings dictionary

        Returns:
            Dictionary with created profile

        Example:
            >>> profile = service.create_profile('custom', {'latency_ms': 100})
        """
        profile = {
            'latency_ms': settings.get('latency_ms', 0),
            'latency_variation': settings.get('latency_variation', 0),
            'packet_loss': settings.get('packet_loss', 0.0),
            'jitter_ms': settings.get('jitter_ms', 0),
            'bandwidth_kbps': settings.get('bandwidth_kbps', 0)
        }
        self._profiles[name] = profile
        return {
            'name': name,
            'created': True,
            'settings': profile
        }

    def get_profile(
        self,
        name: str
    ) -> Dict[str, Any]:
        """
        Get a network profile by name.

        Args:
            name: Profile name

        Returns:
            Dictionary with profile settings

        Example:
            >>> profile = service.get_profile('4G')
        """
        profile = self._profiles.get(name)
        if not profile:
            return {'error': 'Profile not found', 'name': name}
        return {
            'name': name,
            'settings': profile
        }

    def reset_impairments(self) -> Dict[str, Any]:
        """
        Reset all network impairments to defaults.

        Returns:
            Dictionary with reset result

        Example:
            >>> result = service.reset_impairments()
        """
        return self.reset_all()
