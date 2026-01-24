"""
Vehicle State Awareness Service for voice AI testing.

This service provides vehicle state awareness testing for
automotive voice AI systems with contextual state awareness.

Key features:
- Parked vs driving responses
- Engine on/off context
- EV charging state
- Towing mode
- Valet mode restrictions

Example:
    >>> service = VehicleStateAwarenessService()
    >>> state = service.get_driving_state()
"""

from typing import List, Dict, Any
from datetime import datetime
import uuid


class VehicleStateAwarenessService:
    """
    Service for vehicle state awareness testing.

    Provides automotive voice AI testing for state-based
    responses and contextual awareness.

    Example:
        >>> service = VehicleStateAwarenessService()
        >>> config = service.get_vehicle_state_config()
    """

    def __init__(self):
        """Initialize the vehicle state awareness service."""
        self._driving_state: str = 'parked'
        self._engine_state: str = 'off'
        self._charging_state: str = 'not_charging'
        self._towing_mode: bool = False
        self._valet_mode: bool = False

    def get_driving_state(self) -> Dict[str, Any]:
        """
        Get current driving state.

        Returns:
            Dictionary with driving state information

        Example:
            >>> state = service.get_driving_state()
        """
        state_id = str(uuid.uuid4())

        return {
            'state_id': state_id,
            'driving_state': self._driving_state,
            'is_moving': self._driving_state == 'driving',
            'is_parked': self._driving_state == 'parked',
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def is_parked(self) -> Dict[str, Any]:
        """
        Check if vehicle is parked.

        Returns:
            Dictionary with parked status

        Example:
            >>> status = service.is_parked()
        """
        check_id = str(uuid.uuid4())

        return {
            'check_id': check_id,
            'is_parked': self._driving_state == 'parked',
            'driving_state': self._driving_state,
            'checked_at': datetime.utcnow().isoformat()
        }

    def get_driving_mode_response(
        self,
        command: str
    ) -> Dict[str, Any]:
        """
        Get response based on driving mode.

        Args:
            command: Voice command to process

        Returns:
            Dictionary with mode-specific response

        Example:
            >>> response = service.get_driving_mode_response('play video')
        """
        response_id = str(uuid.uuid4())

        # Define restricted commands while driving
        restricted_while_driving: List[str] = [
            'video', 'browse', 'read', 'compose', 'write'
        ]

        is_restricted = False
        if self._driving_state == 'driving':
            is_restricted = any(
                word in command.lower()
                for word in restricted_while_driving
            )

        return {
            'response_id': response_id,
            'command': command,
            'driving_state': self._driving_state,
            'is_restricted': is_restricted,
            'allowed': not is_restricted,
            'reason': 'Command restricted while driving' if is_restricted else None,
            'processed_at': datetime.utcnow().isoformat()
        }

    def get_engine_state(self) -> Dict[str, Any]:
        """
        Get current engine state.

        Returns:
            Dictionary with engine state information

        Example:
            >>> state = service.get_engine_state()
        """
        state_id = str(uuid.uuid4())

        return {
            'state_id': state_id,
            'engine_state': self._engine_state,
            'is_running': self._engine_state == 'running',
            'is_off': self._engine_state == 'off',
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def is_engine_running(self) -> Dict[str, Any]:
        """
        Check if engine is running.

        Returns:
            Dictionary with engine running status

        Example:
            >>> status = service.is_engine_running()
        """
        check_id = str(uuid.uuid4())

        return {
            'check_id': check_id,
            'is_running': self._engine_state == 'running',
            'engine_state': self._engine_state,
            'checked_at': datetime.utcnow().isoformat()
        }

    def get_charging_state(self) -> Dict[str, Any]:
        """
        Get EV charging state.

        Returns:
            Dictionary with charging state information

        Example:
            >>> state = service.get_charging_state()
        """
        state_id = str(uuid.uuid4())

        charging_states = {
            'not_charging': {'active': False, 'level': 0},
            'charging': {'active': True, 'level': 50},
            'fully_charged': {'active': False, 'level': 100}
        }

        state_info = charging_states.get(
            self._charging_state,
            {'active': False, 'level': 0}
        )

        return {
            'state_id': state_id,
            'charging_state': self._charging_state,
            'is_charging': state_info['active'],
            'battery_level': state_info['level'],
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def is_charging(self) -> Dict[str, Any]:
        """
        Check if vehicle is charging.

        Returns:
            Dictionary with charging status

        Example:
            >>> status = service.is_charging()
        """
        check_id = str(uuid.uuid4())

        return {
            'check_id': check_id,
            'is_charging': self._charging_state == 'charging',
            'charging_state': self._charging_state,
            'checked_at': datetime.utcnow().isoformat()
        }

    def get_towing_mode(self) -> Dict[str, Any]:
        """
        Get towing mode status.

        Returns:
            Dictionary with towing mode information

        Example:
            >>> mode = service.get_towing_mode()
        """
        mode_id = str(uuid.uuid4())

        restrictions: List[str] = []
        if self._towing_mode:
            restrictions = [
                'max_speed_limited',
                'transmission_locked',
                'stability_control_active'
            ]

        return {
            'mode_id': mode_id,
            'towing_mode': self._towing_mode,
            'is_active': self._towing_mode,
            'restrictions': restrictions,
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def get_valet_mode(self) -> Dict[str, Any]:
        """
        Get valet mode status.

        Returns:
            Dictionary with valet mode information

        Example:
            >>> mode = service.get_valet_mode()
        """
        mode_id = str(uuid.uuid4())

        restrictions: List[str] = []
        if self._valet_mode:
            restrictions = [
                'speed_limited',
                'storage_locked',
                'personal_data_hidden',
                'location_tracking_active'
            ]

        return {
            'mode_id': mode_id,
            'valet_mode': self._valet_mode,
            'is_active': self._valet_mode,
            'restrictions': restrictions,
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def get_mode_restrictions(
        self,
        mode: str
    ) -> Dict[str, Any]:
        """
        Get restrictions for specific mode.

        Args:
            mode: Mode to get restrictions for

        Returns:
            Dictionary with mode restrictions

        Example:
            >>> restrictions = service.get_mode_restrictions('valet')
        """
        restriction_id = str(uuid.uuid4())

        mode_restrictions: Dict[str, List[str]] = {
            'valet': [
                'speed_limited',
                'storage_locked',
                'personal_data_hidden'
            ],
            'towing': [
                'max_speed_limited',
                'transmission_locked'
            ],
            'transport': [
                'all_systems_disabled',
                'battery_save_mode'
            ],
            'service': [
                'diagnostic_mode',
                'limited_features'
            ]
        }

        restrictions = mode_restrictions.get(mode, [])

        return {
            'restriction_id': restriction_id,
            'mode': mode,
            'restrictions': restrictions,
            'restriction_count': len(restrictions),
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def set_driving_state(self, state: str) -> Dict[str, Any]:
        """
        Set driving state.

        Args:
            state: Driving state to set

        Returns:
            Dictionary with update result

        Example:
            >>> result = service.set_driving_state('driving')
        """
        update_id = str(uuid.uuid4())

        valid_states = ['parked', 'driving', 'idling']
        if state not in valid_states:
            return {
                'update_id': update_id,
                'success': False,
                'error': f'Invalid state: {state}',
                'valid_states': valid_states
            }

        self._driving_state = state

        return {
            'update_id': update_id,
            'success': True,
            'driving_state': state,
            'updated_at': datetime.utcnow().isoformat()
        }

    def set_engine_state(self, state: str) -> Dict[str, Any]:
        """
        Set engine state.

        Args:
            state: Engine state to set

        Returns:
            Dictionary with update result

        Example:
            >>> result = service.set_engine_state('running')
        """
        update_id = str(uuid.uuid4())

        valid_states = ['off', 'running', 'starting']
        if state not in valid_states:
            return {
                'update_id': update_id,
                'success': False,
                'error': f'Invalid state: {state}'
            }

        self._engine_state = state

        return {
            'update_id': update_id,
            'success': True,
            'engine_state': state,
            'updated_at': datetime.utcnow().isoformat()
        }

    def get_vehicle_state_config(self) -> Dict[str, Any]:
        """
        Get vehicle state awareness service configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_vehicle_state_config()
        """
        return {
            'driving_state': self._driving_state,
            'engine_state': self._engine_state,
            'charging_state': self._charging_state,
            'towing_mode': self._towing_mode,
            'valet_mode': self._valet_mode,
            'features': [
                'driving_state', 'engine_state',
                'ev_charging', 'towing_mode',
                'valet_mode', 'mode_restrictions'
            ]
        }
