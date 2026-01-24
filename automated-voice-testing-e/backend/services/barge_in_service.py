"""
Barge-in and Interruption Handling Service for voice testing.

This service provides barge-in detection and interruption
handling for voice AI testing.

Key features:
- Barge-in detection
- Interruption handling
- Speech timing
- Recovery handling

Example:
    >>> service = BargeInService()
    >>> service.start_utterance('session-1')
    >>> if service.detect_barge_in('session-1', audio_frame):
    ...     service.handle_interruption('session-1')
"""

from typing import List, Dict, Any
from datetime import datetime


class BargeInService:
    """
    Service for barge-in and interruption handling.

    Provides barge-in detection, interruption handling,
    speech timing management, and recovery handling.

    Example:
        >>> service = BargeInService()
        >>> service.set_detection_threshold(0.5)
        >>> active = service.is_barge_in_active('session-1')
    """

    def __init__(self):
        """Initialize the barge-in service."""
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._history: List[Dict[str, Any]] = []
        self._detection_threshold = 0.5
        self._energy_threshold = 0.3
        self._endpoint_sensitivity = 0.5
        self._latency_threshold_ms = 200
        self._latency_stats: List[float] = []
        self._enabled = True

    def detect_barge_in(
        self,
        session_id: str,
        audio_frame: bytes = None
    ) -> Dict[str, Any]:
        """
        Detect barge-in from audio.

        Args:
            session_id: Session identifier
            audio_frame: Audio data to analyze

        Returns:
            Dictionary with detection result

        Example:
            >>> result = service.detect_barge_in('session-1', audio)
        """
        if session_id not in self._sessions:
            self._sessions[session_id] = self._create_session(session_id)

        session = self._sessions[session_id]

        # Simulated detection based on energy
        energy = self.calculate_energy(audio_frame).get('energy', 0)
        detected = energy > self._detection_threshold

        if detected and session.get('utterance_active'):
            session['barge_in_active'] = True
            session['barge_in_time'] = datetime.utcnow().isoformat()

            event = {
                'session_id': session_id,
                'type': 'barge_in',
                'energy': energy,
                'timestamp': session['barge_in_time']
            }
            self._history.append(event)

        return {
            'session_id': session_id,
            'detected': detected,
            'energy': energy,
            'threshold': self._detection_threshold
        }

    def set_detection_threshold(
        self,
        threshold: float
    ) -> Dict[str, Any]:
        """
        Set barge-in detection threshold.

        Args:
            threshold: Detection threshold (0-1)

        Returns:
            Dictionary with threshold setting

        Example:
            >>> result = service.set_detection_threshold(0.6)
        """
        self._detection_threshold = threshold
        return {
            'threshold': threshold,
            'configured': True
        }

    def is_barge_in_active(self, session_id: str) -> bool:
        """
        Check if barge-in is currently active.

        Args:
            session_id: Session identifier

        Returns:
            True if barge-in is active

        Example:
            >>> active = service.is_barge_in_active('session-1')
        """
        if session_id not in self._sessions:
            return False

        return self._sessions[session_id].get('barge_in_active', False)

    def handle_interruption(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Handle an interruption.

        Args:
            session_id: Session identifier

        Returns:
            Dictionary with handling result

        Example:
            >>> result = service.handle_interruption('session-1')
        """
        if session_id not in self._sessions:
            return {'error': 'Session not found'}

        session = self._sessions[session_id]
        now = datetime.utcnow()

        # Stop playback and record interruption
        self.stop_playback(session_id)

        session['interruption_handled'] = True
        session['interruption_time'] = now.isoformat()

        return {
            'session_id': session_id,
            'handled': True,
            'interruption_point': self.get_interruption_point(session_id)
        }

    def stop_playback(self, session_id: str) -> Dict[str, Any]:
        """
        Stop audio playback.

        Args:
            session_id: Session identifier

        Returns:
            Dictionary with stop result

        Example:
            >>> result = service.stop_playback('session-1')
        """
        if session_id not in self._sessions:
            return {'error': 'Session not found'}

        session = self._sessions[session_id]
        session['playback_stopped'] = True
        session['stop_time'] = datetime.utcnow().isoformat()

        return {
            'session_id': session_id,
            'stopped': True
        }

    def get_interruption_point(self, session_id: str) -> Dict[str, Any]:
        """
        Get interruption point in utterance.

        Args:
            session_id: Session identifier

        Returns:
            Dictionary with interruption point

        Example:
            >>> point = service.get_interruption_point('session-1')
        """
        if session_id not in self._sessions:
            return {'error': 'Session not found'}

        session = self._sessions[session_id]

        # Calculate position in utterance
        start = session.get('utterance_start')
        interrupt = session.get('barge_in_time')

        position_ms = 0
        if start and interrupt:
            start_dt = datetime.fromisoformat(start)
            interrupt_dt = datetime.fromisoformat(interrupt)
            position_ms = int((interrupt_dt - start_dt).total_seconds() * 1000)

        return {
            'session_id': session_id,
            'position_ms': position_ms
        }

    def start_utterance(self, session_id: str) -> Dict[str, Any]:
        """
        Mark start of system utterance.

        Args:
            session_id: Session identifier

        Returns:
            Dictionary with utterance info

        Example:
            >>> result = service.start_utterance('session-1')
        """
        if session_id not in self._sessions:
            self._sessions[session_id] = self._create_session(session_id)

        session = self._sessions[session_id]
        now = datetime.utcnow()

        session['utterance_active'] = True
        session['utterance_start'] = now.isoformat()
        session['barge_in_active'] = False

        return {
            'session_id': session_id,
            'started': True,
            'start_time': now.isoformat()
        }

    def end_utterance(self, session_id: str) -> Dict[str, Any]:
        """
        Mark end of system utterance.

        Args:
            session_id: Session identifier

        Returns:
            Dictionary with utterance info

        Example:
            >>> result = service.end_utterance('session-1')
        """
        if session_id not in self._sessions:
            return {'error': 'Session not found'}

        session = self._sessions[session_id]
        now = datetime.utcnow()

        session['utterance_active'] = False
        session['utterance_end'] = now.isoformat()

        # Calculate duration
        duration_ms = 0
        if session.get('utterance_start'):
            start = datetime.fromisoformat(session['utterance_start'])
            duration_ms = int((now - start).total_seconds() * 1000)

        return {
            'session_id': session_id,
            'ended': True,
            'duration_ms': duration_ms
        }

    def get_overlap_duration(self, session_id: str) -> Dict[str, Any]:
        """
        Get duration of speech overlap.

        Args:
            session_id: Session identifier

        Returns:
            Dictionary with overlap duration

        Example:
            >>> overlap = service.get_overlap_duration('session-1')
        """
        if session_id not in self._sessions:
            return {'error': 'Session not found'}

        session = self._sessions[session_id]

        # Calculate overlap from barge-in to utterance end
        overlap_ms = 0
        barge_in = session.get('barge_in_time')
        end = session.get('utterance_end') or session.get('stop_time')

        if barge_in and end:
            start_dt = datetime.fromisoformat(barge_in)
            end_dt = datetime.fromisoformat(end)
            overlap_ms = int((end_dt - start_dt).total_seconds() * 1000)

        return {
            'session_id': session_id,
            'overlap_ms': overlap_ms
        }

    def calculate_energy(
        self,
        audio_frame: bytes = None
    ) -> Dict[str, Any]:
        """
        Calculate audio energy level.

        Args:
            audio_frame: Audio data

        Returns:
            Dictionary with energy value

        Example:
            >>> energy = service.calculate_energy(audio)
        """
        # Simulated energy calculation
        energy = 0.0
        if audio_frame:
            # Would calculate RMS energy from audio samples
            energy = 0.5

        return {
            'energy': energy,
            'calculated_at': datetime.utcnow().isoformat()
        }

    def set_energy_threshold(
        self,
        threshold: float
    ) -> Dict[str, Any]:
        """
        Set energy detection threshold.

        Args:
            threshold: Energy threshold (0-1)

        Returns:
            Dictionary with threshold setting

        Example:
            >>> result = service.set_energy_threshold(0.4)
        """
        self._energy_threshold = threshold
        return {
            'threshold': threshold,
            'configured': True
        }

    def resume_after_barge_in(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Resume after barge-in handled.

        Args:
            session_id: Session identifier

        Returns:
            Dictionary with resume info

        Example:
            >>> result = service.resume_after_barge_in('session-1')
        """
        if session_id not in self._sessions:
            return {'error': 'Session not found'}

        session = self._sessions[session_id]

        session['barge_in_active'] = False
        session['resumed'] = True
        session['resume_time'] = datetime.utcnow().isoformat()

        return {
            'session_id': session_id,
            'resumed': True,
            'recovery_point': self.get_recovery_point(session_id)
        }

    def get_recovery_point(self, session_id: str) -> Dict[str, Any]:
        """
        Get recovery point after barge-in.

        Args:
            session_id: Session identifier

        Returns:
            Dictionary with recovery point

        Example:
            >>> point = service.get_recovery_point('session-1')
        """
        if session_id not in self._sessions:
            return {'error': 'Session not found'}

        # Get interruption point as recovery reference
        interruption = self.get_interruption_point(session_id)

        return {
            'session_id': session_id,
            'position_ms': interruption.get('position_ms', 0),
            'can_resume': True
        }

    def get_barge_in_history(
        self,
        session_id: str = None
    ) -> List[Dict[str, Any]]:
        """
        Get barge-in event history.

        Args:
            session_id: Optional session filter

        Returns:
            List of barge-in events

        Example:
            >>> history = service.get_barge_in_history()
        """
        if session_id:
            return [
                h for h in self._history
                if h.get('session_id') == session_id
            ]
        return self._history.copy()

    def detect_interruption(
        self,
        session_id: str,
        audio_frame: bytes = None
    ) -> Dict[str, Any]:
        """
        Detect user interruption during TTS.

        Args:
            session_id: Session identifier
            audio_frame: Audio data to analyze

        Returns:
            Dictionary with interruption detection result

        Example:
            >>> result = service.detect_interruption('session-1', audio)
        """
        if session_id not in self._sessions:
            self._sessions[session_id] = self._create_session(session_id)

        session = self._sessions[session_id]

        # Detect interruption during TTS
        energy = self.calculate_energy(audio_frame).get('energy', 0)
        interrupted = (
            energy > self._detection_threshold and
            session.get('utterance_active', False)
        )

        if interrupted:
            self.handle_interruption(session_id)

        return {
            'session_id': session_id,
            'interrupted': interrupted,
            'energy': energy
        }

    def stop_tts(self, session_id: str) -> Dict[str, Any]:
        """
        Stop TTS playback immediately.

        Args:
            session_id: Session identifier

        Returns:
            Dictionary with stop result

        Example:
            >>> result = service.stop_tts('session-1')
        """
        if session_id not in self._sessions:
            return {'error': 'Session not found'}

        self.stop_playback(session_id)
        self._sessions[session_id]['tts_stopped'] = True

        return {
            'session_id': session_id,
            'tts_stopped': True,
            'stopped_at': datetime.utcnow().isoformat()
        }

    def detect_endpoint(
        self,
        session_id: str,
        audio_frame: bytes = None
    ) -> Dict[str, Any]:
        """
        Detect early endpoint in speech.

        Args:
            session_id: Session identifier
            audio_frame: Audio data to analyze

        Returns:
            Dictionary with endpoint detection result

        Example:
            >>> result = service.detect_endpoint('session-1', audio)
        """
        energy = self.calculate_energy(audio_frame).get('energy', 0)
        endpoint_detected = energy < self._endpoint_sensitivity

        return {
            'session_id': session_id,
            'endpoint_detected': endpoint_detected,
            'energy': energy,
            'sensitivity': self._endpoint_sensitivity
        }

    def set_endpoint_sensitivity(
        self,
        sensitivity: float
    ) -> Dict[str, Any]:
        """
        Set endpoint detection sensitivity.

        Args:
            sensitivity: Sensitivity threshold (0-1)

        Returns:
            Dictionary with sensitivity setting

        Example:
            >>> result = service.set_endpoint_sensitivity(0.3)
        """
        self._endpoint_sensitivity = sensitivity
        return {
            'sensitivity': sensitivity,
            'configured': True
        }

    def get_endpoint_config(self) -> Dict[str, Any]:
        """
        Get endpoint detection configuration.

        Returns:
            Dictionary with endpoint config

        Example:
            >>> config = service.get_endpoint_config()
        """
        return {
            'sensitivity': self._endpoint_sensitivity,
            'energy_threshold': self._energy_threshold
        }

    def measure_barge_in_latency(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Measure barge-in detection latency.

        Args:
            session_id: Session identifier

        Returns:
            Dictionary with latency measurement

        Example:
            >>> latency = service.measure_barge_in_latency('session-1')
        """
        if session_id not in self._sessions:
            return {'error': 'Session not found'}

        session = self._sessions[session_id]
        latency_ms = 0

        barge_in = session.get('barge_in_time')
        stop = session.get('stop_time')

        if barge_in and stop:
            start_dt = datetime.fromisoformat(barge_in)
            stop_dt = datetime.fromisoformat(stop)
            latency_ms = int((stop_dt - start_dt).total_seconds() * 1000)
            self._latency_stats.append(latency_ms)

        return {
            'session_id': session_id,
            'latency_ms': latency_ms,
            'within_threshold': latency_ms <= self._latency_threshold_ms
        }

    def get_latency_stats(self) -> Dict[str, Any]:
        """
        Get barge-in latency statistics.

        Returns:
            Dictionary with latency statistics

        Example:
            >>> stats = service.get_latency_stats()
        """
        if not self._latency_stats:
            return {
                'count': 0,
                'avg_ms': 0,
                'min_ms': 0,
                'max_ms': 0
            }

        return {
            'count': len(self._latency_stats),
            'avg_ms': sum(self._latency_stats) / len(self._latency_stats),
            'min_ms': min(self._latency_stats),
            'max_ms': max(self._latency_stats)
        }

    def set_latency_threshold(
        self,
        threshold_ms: int
    ) -> Dict[str, Any]:
        """
        Set acceptable latency threshold.

        Args:
            threshold_ms: Threshold in milliseconds

        Returns:
            Dictionary with threshold setting

        Example:
            >>> result = service.set_latency_threshold(150)
        """
        self._latency_threshold_ms = threshold_ms
        return {
            'threshold_ms': threshold_ms,
            'configured': True
        }

    def enable_barge_in(self) -> Dict[str, Any]:
        """
        Enable barge-in detection.

        Returns:
            Dictionary with enable result

        Example:
            >>> result = service.enable_barge_in()
        """
        self._enabled = True
        return {
            'enabled': True,
            'timestamp': datetime.utcnow().isoformat()
        }

    def disable_barge_in(self) -> Dict[str, Any]:
        """
        Disable barge-in detection.

        Returns:
            Dictionary with disable result

        Example:
            >>> result = service.disable_barge_in()
        """
        self._enabled = False
        return {
            'enabled': False,
            'timestamp': datetime.utcnow().isoformat()
        }

    def _create_session(self, session_id: str) -> Dict[str, Any]:
        """Create new session tracking."""
        return {
            'id': session_id,
            'utterance_active': False,
            'barge_in_active': False,
            'created_at': datetime.utcnow().isoformat()
        }
