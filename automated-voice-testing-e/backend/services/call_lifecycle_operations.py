"""
Call Lifecycle Operations Mixin for metrics and call operations.

This mixin provides metrics, timing, and operation methods for CallLifecycleService:
- Duration and timing calculations
- Hold and transfer operations
- Call history and metrics aggregation

Extracted from call_lifecycle_service.py to maintain 500-line limit per file.

Example:
    >>> class CallLifecycleService(CallLifecycleOperationsMixin):
    ...     pass
"""

from typing import List, Dict, Any
from datetime import datetime


class CallLifecycleOperationsMixin:
    """
    Mixin providing operations and metrics methods for CallLifecycleService.

    This mixin contains:
    - Duration calculation methods
    - Hold/resume methods
    - Transfer methods
    - Metrics aggregation methods
    """

    def get_call_duration(self, call_id: str) -> Dict[str, Any]:
        """
        Get call duration.

        Args:
            call_id: Call ID

        Returns:
            Dictionary with duration info

        Example:
            >>> duration = service.get_call_duration(call_id)
        """
        if call_id not in self._calls:
            return {'error': 'Call not found'}

        call = self._calls[call_id]
        duration_ms = 0

        if call.get('connected_at'):
            start = datetime.fromisoformat(call['connected_at'])
            end_time = call.get('ended_at')
            if end_time:
                end = datetime.fromisoformat(end_time)
            else:
                end = datetime.utcnow()
            duration_ms = int((end - start).total_seconds() * 1000)

        return {
            'call_id': call_id,
            'duration_ms': duration_ms,
            'duration_seconds': duration_ms / 1000
        }

    def get_termination_reason(self, call_id: str) -> Dict[str, Any]:
        """
        Get call termination reason.

        Args:
            call_id: Call ID

        Returns:
            Dictionary with termination reason

        Example:
            >>> reason = service.get_termination_reason(call_id)
        """
        if call_id not in self._calls:
            return {'error': 'Call not found'}

        call = self._calls[call_id]
        return {
            'call_id': call_id,
            'reason': call.get('termination_reason'),
            'state': call.get('state')
        }

    def hold_call(self, call_id: str) -> Dict[str, Any]:
        """
        Place call on hold.

        Args:
            call_id: Call ID

        Returns:
            Dictionary with hold result

        Example:
            >>> result = service.hold_call(call_id)
        """
        return self.transition_state(call_id, 'on_hold')

    def resume_call(self, call_id: str) -> Dict[str, Any]:
        """
        Resume call from hold.

        Args:
            call_id: Call ID

        Returns:
            Dictionary with resume result

        Example:
            >>> result = service.resume_call(call_id)
        """
        return self.transition_state(call_id, 'connected')

    def transfer_call(
        self,
        call_id: str,
        target: str
    ) -> Dict[str, Any]:
        """
        Transfer call to another target.

        Args:
            call_id: Call ID
            target: Transfer target

        Returns:
            Dictionary with transfer result

        Example:
            >>> result = service.transfer_call(call_id, 'sip:new@domain')
        """
        if call_id not in self._calls:
            return {'error': 'Call not found'}

        result = self.transition_state(call_id, 'transferring')
        if 'error' not in result:
            self._calls[call_id]['transfer_target'] = target

        return {
            'call_id': call_id,
            'transfer_target': target,
            'state': 'transferring'
        }

    def get_ring_duration(self, call_id: str) -> Dict[str, Any]:
        """
        Get ring duration.

        Args:
            call_id: Call ID

        Returns:
            Dictionary with ring duration

        Example:
            >>> ring = service.get_ring_duration(call_id)
        """
        if call_id not in self._calls:
            return {'error': 'Call not found'}

        call = self._calls[call_id]
        duration_ms = 0

        if call.get('ring_start') and call.get('connected_at'):
            start = datetime.fromisoformat(call['ring_start'])
            end = datetime.fromisoformat(call['connected_at'])
            duration_ms = int((end - start).total_seconds() * 1000)

        return {
            'call_id': call_id,
            'ring_duration_ms': duration_ms
        }

    def get_setup_time(self, call_id: str) -> Dict[str, Any]:
        """
        Get call setup time.

        Args:
            call_id: Call ID

        Returns:
            Dictionary with setup time

        Example:
            >>> setup = service.get_setup_time(call_id)
        """
        if call_id not in self._calls:
            return {'error': 'Call not found'}

        call = self._calls[call_id]
        setup_ms = 0

        if call.get('created_at') and call.get('connected_at'):
            start = datetime.fromisoformat(call['created_at'])
            end = datetime.fromisoformat(call['connected_at'])
            setup_ms = int((end - start).total_seconds() * 1000)

        return {
            'call_id': call_id,
            'setup_time_ms': setup_ms
        }

    def get_call_metrics(self, call_id: str) -> Dict[str, Any]:
        """
        Get comprehensive call metrics.

        Args:
            call_id: Call ID

        Returns:
            Dictionary with all call metrics

        Example:
            >>> metrics = service.get_call_metrics(call_id)
        """
        if call_id not in self._calls:
            return {'error': 'Call not found'}

        call = self._calls[call_id]
        duration = self.get_call_duration(call_id)
        ring = self.get_ring_duration(call_id)
        setup = self.get_setup_time(call_id)

        return {
            'call_id': call_id,
            'state': call.get('state'),
            'target': call.get('target'),
            'duration_ms': duration.get('duration_ms', 0),
            'ring_duration_ms': ring.get('ring_duration_ms', 0),
            'setup_time_ms': setup.get('setup_time_ms', 0),
            'state_transitions': len(self._state_history.get(call_id, []))
        }

    def measure_setup_latency(self, call_id: str) -> Dict[str, Any]:
        """
        Measure call setup latency.

        Args:
            call_id: Call ID

        Returns:
            Dictionary with setup latency metrics

        Example:
            >>> latency = service.measure_setup_latency(call_id)
        """
        if call_id not in self._calls:
            return {'error': 'Call not found'}

        call = self._calls[call_id]
        setup_latency_ms = 0
        ring_latency_ms = 0
        connect_latency_ms = 0

        if call.get('created_at'):
            created = datetime.fromisoformat(call['created_at'])

            if call.get('ring_start'):
                ring_start = datetime.fromisoformat(call['ring_start'])
                ring_latency_ms = int((ring_start - created).total_seconds() * 1000)

            if call.get('connected_at'):
                connected = datetime.fromisoformat(call['connected_at'])
                setup_latency_ms = int((connected - created).total_seconds() * 1000)

                if call.get('ring_start'):
                    ring_start = datetime.fromisoformat(call['ring_start'])
                    connect_latency_ms = int((connected - ring_start).total_seconds() * 1000)

        return {
            'call_id': call_id,
            'setup_latency_ms': setup_latency_ms,
            'ring_latency_ms': ring_latency_ms,
            'connect_latency_ms': connect_latency_ms
        }

    def get_hold_duration(self, call_id: str) -> Dict[str, Any]:
        """
        Get duration call was on hold.

        Args:
            call_id: Call ID

        Returns:
            Dictionary with hold duration

        Example:
            >>> hold = service.get_hold_duration(call_id)
        """
        if call_id not in self._calls:
            return {'error': 'Call not found'}

        hold_duration_ms = 0
        hold_count = 0
        history = self._state_history.get(call_id, [])

        hold_start = None
        for entry in history:
            if entry['state'] == 'on_hold':
                hold_start = datetime.fromisoformat(entry['timestamp'])
                hold_count += 1
            elif entry['state'] == 'connected' and hold_start:
                end = datetime.fromisoformat(entry['timestamp'])
                hold_duration_ms += int((end - hold_start).total_seconds() * 1000)
                hold_start = None

        # If still on hold
        if hold_start and self._calls[call_id]['state'] == 'on_hold':
            hold_duration_ms += int((datetime.utcnow() - hold_start).total_seconds() * 1000)

        return {
            'call_id': call_id,
            'hold_duration_ms': hold_duration_ms,
            'hold_count': hold_count
        }

    def blind_transfer(
        self,
        call_id: str,
        target: str
    ) -> Dict[str, Any]:
        """
        Blind transfer call without consultation.

        Args:
            call_id: Call ID
            target: Transfer target

        Returns:
            Dictionary with transfer result

        Example:
            >>> result = service.blind_transfer(call_id, 'sip:target@domain')
        """
        if call_id not in self._calls:
            return {'error': 'Call not found'}

        result = self.transition_state(call_id, 'transferring')
        if 'error' in result:
            return result

        self._calls[call_id]['transfer_target'] = target
        self._calls[call_id]['transfer_type'] = 'blind'

        return {
            'call_id': call_id,
            'transfer_target': target,
            'transfer_type': 'blind',
            'state': 'transferring'
        }

    def attended_transfer(
        self,
        call_id: str,
        target: str,
        consult_call_id: str = None
    ) -> Dict[str, Any]:
        """
        Attended transfer with consultation.

        Args:
            call_id: Call ID
            target: Transfer target
            consult_call_id: Consultation call ID

        Returns:
            Dictionary with transfer result

        Example:
            >>> result = service.attended_transfer(call_id, 'sip:target@domain')
        """
        if call_id not in self._calls:
            return {'error': 'Call not found'}

        result = self.transition_state(call_id, 'transferring')
        if 'error' in result:
            return result

        self._calls[call_id]['transfer_target'] = target
        self._calls[call_id]['transfer_type'] = 'attended'
        if consult_call_id:
            self._calls[call_id]['consult_call_id'] = consult_call_id

        return {
            'call_id': call_id,
            'transfer_target': target,
            'transfer_type': 'attended',
            'consult_call_id': consult_call_id,
            'state': 'transferring'
        }

    def terminate_call(
        self,
        call_id: str,
        reason: str = "terminated"
    ) -> Dict[str, Any]:
        """
        Terminate call.

        Args:
            call_id: Call ID
            reason: Termination reason

        Returns:
            Dictionary with termination result

        Example:
            >>> result = service.terminate_call(call_id, 'user_hangup')
        """
        return self.end_call(call_id, reason)

    def get_call_history(
        self,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get call history.

        Args:
            limit: Maximum number of calls to return

        Returns:
            List of call records

        Example:
            >>> history = service.get_call_history(50)
        """
        calls = []
        for call_id, call in self._calls.items():
            call_record = {
                'call_id': call_id,
                'target': call.get('target'),
                'state': call.get('state'),
                'created_at': call.get('created_at'),
                'ended_at': call.get('ended_at'),
                'termination_reason': call.get('termination_reason')
            }
            calls.append(call_record)

        # Sort by creation time
        calls.sort(
            key=lambda x: x.get('created_at', ''),
            reverse=True
        )

        return calls[:limit]
