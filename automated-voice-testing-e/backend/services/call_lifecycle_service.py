"""
Call Lifecycle Testing Service for voice testing.

This service provides call lifecycle management and
state testing for voice AI systems.

Key features:
- Call initiation
- Call state management
- Call termination
- Call transfer/hold

Example:
    >>> service = CallLifecycleService()
    >>> call = service.initiate_call('sip:target@domain')
    >>> service.answer_call(call['id'])
    >>> service.end_call(call['id'])
"""

from typing import List, Dict, Any
from datetime import datetime
import uuid

# Import operations mixin
from services.call_lifecycle_operations import CallLifecycleOperationsMixin


class CallLifecycleService(CallLifecycleOperationsMixin):
    """
    Service for call lifecycle management.

    Provides call initiation, state management,
    termination, transfer/hold, and timing metrics.

    Example:
        >>> service = CallLifecycleService()
        >>> call = service.initiate_call('sip:target@domain')
        >>> duration = service.get_call_duration(call['id'])
    """

    def __init__(self):
        """Initialize the call lifecycle service."""
        self._calls: Dict[str, Dict[str, Any]] = {}
        self._state_history: Dict[str, List[Dict[str, Any]]] = {}

        # Define state machine
        self._valid_transitions = {
            'idle': ['initiating', 'ringing'],
            'initiating': ['ringing', 'failed'],
            'ringing': ['connected', 'failed', 'rejected'],
            'connected': ['on_hold', 'transferring', 'ended'],
            'on_hold': ['connected', 'ended'],
            'transferring': ['connected', 'ended', 'failed'],
            'failed': [],
            'rejected': [],
            'ended': []
        }

    def initiate_call(
        self,
        target: str,
        caller_id: str = ""
    ) -> Dict[str, Any]:
        """
        Initiate a call.

        Args:
            target: Target URI or number
            caller_id: Optional caller ID

        Returns:
            Dictionary with call information

        Example:
            >>> call = service.initiate_call('sip:target@domain')
        """
        call_id = str(uuid.uuid4())
        now = datetime.utcnow()

        call = {
            'id': call_id,
            'target': target,
            'caller_id': caller_id,
            'state': 'initiating',
            'created_at': now.isoformat(),
            'ring_start': None,
            'connected_at': None,
            'ended_at': None,
            'termination_reason': None
        }
        self._calls[call_id] = call
        self._state_history[call_id] = [{
            'state': 'initiating',
            'timestamp': now.isoformat()
        }]

        return call

    def answer_call(self, call_id: str) -> Dict[str, Any]:
        """
        Answer a call.

        Args:
            call_id: Call ID to answer

        Returns:
            Dictionary with answer result

        Example:
            >>> result = service.answer_call(call_id)
        """
        if call_id not in self._calls:
            return {'error': 'Call not found'}

        call = self._calls[call_id]
        if call['state'] not in ['ringing', 'initiating']:
            return {'error': 'Cannot answer call in current state'}

        now = datetime.utcnow()
        call['state'] = 'connected'
        call['connected_at'] = now.isoformat()

        self._record_state(call_id, 'connected')

        return {
            'call_id': call_id,
            'state': 'connected',
            'answered_at': now.isoformat()
        }

    def reject_call(
        self,
        call_id: str,
        reason: str = "rejected"
    ) -> Dict[str, Any]:
        """
        Reject a call.

        Args:
            call_id: Call ID to reject
            reason: Rejection reason

        Returns:
            Dictionary with rejection result

        Example:
            >>> result = service.reject_call(call_id)
        """
        if call_id not in self._calls:
            return {'error': 'Call not found'}

        call = self._calls[call_id]
        now = datetime.utcnow()

        call['state'] = 'rejected'
        call['ended_at'] = now.isoformat()
        call['termination_reason'] = reason

        self._record_state(call_id, 'rejected')

        return {
            'call_id': call_id,
            'state': 'rejected',
            'reason': reason
        }

    def get_call_state(self, call_id: str) -> Dict[str, Any]:
        """
        Get call state.

        Args:
            call_id: Call ID to check

        Returns:
            Dictionary with call state

        Example:
            >>> state = service.get_call_state(call_id)
        """
        if call_id not in self._calls:
            return {'error': 'Call not found'}

        call = self._calls[call_id]
        return {
            'call_id': call_id,
            'state': call.get('state'),
            'target': call.get('target')
        }

    def transition_state(
        self,
        call_id: str,
        new_state: str
    ) -> Dict[str, Any]:
        """
        Transition call to new state.

        Args:
            call_id: Call ID
            new_state: Target state

        Returns:
            Dictionary with transition result

        Example:
            >>> result = service.transition_state(call_id, 'ringing')
        """
        if call_id not in self._calls:
            return {'error': 'Call not found'}

        call = self._calls[call_id]
        current = call['state']

        if new_state not in self._valid_transitions.get(current, []):
            return {
                'error': f'Invalid transition from {current} to {new_state}'
            }

        call['state'] = new_state
        if new_state == 'ringing':
            call['ring_start'] = datetime.utcnow().isoformat()

        self._record_state(call_id, new_state)

        return {
            'call_id': call_id,
            'previous_state': current,
            'state': new_state,
            'transitioned': True
        }

    def get_valid_transitions(self, call_id: str) -> Dict[str, Any]:
        """
        Get valid transitions from current state.

        Args:
            call_id: Call ID

        Returns:
            Dictionary with valid transitions

        Example:
            >>> transitions = service.get_valid_transitions(call_id)
        """
        if call_id not in self._calls:
            return {'error': 'Call not found'}

        state = self._calls[call_id]['state']
        valid = self._valid_transitions.get(state, [])

        return {
            'call_id': call_id,
            'current_state': state,
            'valid_transitions': valid
        }

    def get_state_history(self, call_id: str) -> List[Dict[str, Any]]:
        """
        Get state transition history.

        Args:
            call_id: Call ID

        Returns:
            List of state transitions

        Example:
            >>> history = service.get_state_history(call_id)
        """
        return self._state_history.get(call_id, [])

    def end_call(
        self,
        call_id: str,
        reason: str = "normal"
    ) -> Dict[str, Any]:
        """
        End a call.

        Args:
            call_id: Call ID to end
            reason: Termination reason

        Returns:
            Dictionary with termination result

        Example:
            >>> result = service.end_call(call_id)
        """
        if call_id not in self._calls:
            return {'error': 'Call not found'}

        call = self._calls[call_id]
        now = datetime.utcnow()

        call['state'] = 'ended'
        call['ended_at'] = now.isoformat()
        call['termination_reason'] = reason

        self._record_state(call_id, 'ended')

        return {
            'call_id': call_id,
            'state': 'ended',
            'reason': reason,
            'ended_at': now.isoformat()
        }

    def _record_state(self, call_id: str, state: str) -> None:
        """Record state transition."""
        if call_id not in self._state_history:
            self._state_history[call_id] = []

        self._state_history[call_id].append({
            'state': state,
            'timestamp': datetime.utcnow().isoformat()
        })
