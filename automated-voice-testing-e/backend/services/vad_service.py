"""
Voice Activity Detection Service for voice testing.

This service provides VAD (Voice Activity Detection)
for detecting speech and silence in audio.

Key features:
- Speech detection
- Silence detection
- Frame processing
- Speech segments

Example:
    >>> service = VADService()
    >>> service.start_session('session-1')
    >>> result = service.process_frame('session-1', audio_frame)
    >>> if result['is_speech']:
    ...     print("Speech detected")
"""

from typing import List, Dict, Any
from datetime import datetime

# Import analysis mixin
from services.vad_analysis import VADAnalysisMixin


class VADService(VADAnalysisMixin):
    """
    Service for Voice Activity Detection.

    Provides speech detection, silence detection,
    frame processing, and segment analysis.

    Example:
        >>> service = VADService()
        >>> service.set_aggressiveness(2)
        >>> segments = service.get_speech_segments('session-1')
    """

    def __init__(self):
        """Initialize the VAD service."""
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._aggressiveness = 1
        self._frame_duration_ms = 30
        self._speech_threshold = 0.5
        self._silence_threshold = 0.3
        self._accuracy_samples: List[Dict[str, Any]] = []
        self._endpoint_samples: List[Dict[str, Any]] = []

    def process_frame(
        self,
        session_id: str,
        audio_frame: bytes = None
    ) -> Dict[str, Any]:
        """
        Process an audio frame for VAD.

        Args:
            session_id: Session identifier
            audio_frame: Audio frame data

        Returns:
            Dictionary with VAD result

        Example:
            >>> result = service.process_frame('session-1', frame)
        """
        if session_id not in self._sessions:
            self.start_session(session_id)

        session = self._sessions[session_id]

        # Simulated VAD processing
        probability = self.get_speech_probability(audio_frame).get('probability', 0)
        is_speech = probability >= self._speech_threshold

        # Track frame
        frame_info = {
            'is_speech': is_speech,
            'probability': probability,
            'timestamp': datetime.utcnow().isoformat()
        }
        session['frames'].append(frame_info)

        # Update segments
        self._update_segments(session, is_speech)

        return {
            'session_id': session_id,
            'is_speech': is_speech,
            'probability': probability,
            'frame_count': len(session['frames'])
        }

    def is_speech(
        self,
        session_id: str,
        audio_frame: bytes = None
    ) -> bool:
        """
        Check if frame contains speech.

        Args:
            session_id: Session identifier
            audio_frame: Audio frame data

        Returns:
            True if speech detected

        Example:
            >>> speech = service.is_speech('session-1', frame)
        """
        result = self.process_frame(session_id, audio_frame)
        return result.get('is_speech', False)

    def get_speech_probability(
        self,
        audio_frame: bytes = None
    ) -> Dict[str, Any]:
        """
        Get speech probability for frame.

        Args:
            audio_frame: Audio frame data

        Returns:
            Dictionary with probability

        Example:
            >>> prob = service.get_speech_probability(frame)
        """
        # Simulated probability calculation
        probability = 0.0
        if audio_frame:
            # Would calculate based on energy, spectral features
            probability = 0.6

        return {
            'probability': probability,
            'calculated_at': datetime.utcnow().isoformat()
        }

    def set_aggressiveness(self, level: int) -> Dict[str, Any]:
        """
        Set VAD aggressiveness level.

        Args:
            level: Aggressiveness (0-3)

        Returns:
            Dictionary with setting

        Example:
            >>> result = service.set_aggressiveness(2)
        """
        self._aggressiveness = max(0, min(3, level))
        # Adjust threshold based on aggressiveness
        thresholds = [0.3, 0.5, 0.7, 0.9]
        self._speech_threshold = thresholds[self._aggressiveness]

        return {
            'aggressiveness': self._aggressiveness,
            'threshold': self._speech_threshold,
            'configured': True
        }

    def set_frame_duration(self, duration_ms: int) -> Dict[str, Any]:
        """
        Set frame duration.

        Args:
            duration_ms: Frame duration in ms

        Returns:
            Dictionary with setting

        Example:
            >>> result = service.set_frame_duration(20)
        """
        self._frame_duration_ms = duration_ms
        return {
            'frame_duration_ms': duration_ms,
            'configured': True
        }

    def get_config(self) -> Dict[str, Any]:
        """
        Get VAD configuration.

        Returns:
            Dictionary with current config

        Example:
            >>> config = service.get_config()
        """
        return {
            'aggressiveness': self._aggressiveness,
            'frame_duration_ms': self._frame_duration_ms,
            'speech_threshold': self._speech_threshold
        }

    def start_session(self, session_id: str) -> Dict[str, Any]:
        """
        Start a VAD session.

        Args:
            session_id: Session identifier

        Returns:
            Dictionary with session info

        Example:
            >>> result = service.start_session('session-1')
        """
        self._sessions[session_id] = {
            'id': session_id,
            'frames': [],
            'segments': [],
            'current_segment': None,
            'started_at': datetime.utcnow().isoformat()
        }

        return {
            'session_id': session_id,
            'started': True
        }

    def end_session(self, session_id: str) -> Dict[str, Any]:
        """
        End a VAD session.

        Args:
            session_id: Session identifier

        Returns:
            Dictionary with session summary

        Example:
            >>> result = service.end_session('session-1')
        """
        if session_id not in self._sessions:
            return {'error': 'Session not found'}

        session = self._sessions[session_id]

        # Close any open segment
        if session.get('current_segment'):
            session['current_segment']['end_frame'] = len(session['frames'])
            session['segments'].append(session['current_segment'])
            session['current_segment'] = None

        session['ended_at'] = datetime.utcnow().isoformat()

        return {
            'session_id': session_id,
            'ended': True,
            'frame_count': len(session['frames']),
            'segment_count': len(session['segments'])
        }

    def reset(self, session_id: str) -> Dict[str, Any]:
        """
        Reset a VAD session.

        Args:
            session_id: Session identifier

        Returns:
            Dictionary with reset result

        Example:
            >>> result = service.reset('session-1')
        """
        if session_id in self._sessions:
            del self._sessions[session_id]

        return self.start_session(session_id)

    def set_vad_threshold(
        self,
        threshold: float
    ) -> Dict[str, Any]:
        """
        Set VAD speech detection threshold.

        Args:
            threshold: Detection threshold (0-1)

        Returns:
            Dictionary with threshold setting

        Example:
            >>> result = service.set_vad_threshold(0.6)
        """
        self._speech_threshold = threshold
        return {
            'threshold': threshold,
            'configured': True
        }

    def set_silence_threshold(
        self,
        threshold: float
    ) -> Dict[str, Any]:
        """
        Set silence detection threshold.

        Args:
            threshold: Silence threshold (0-1)

        Returns:
            Dictionary with threshold setting

        Example:
            >>> result = service.set_silence_threshold(0.2)
        """
        self._silence_threshold = threshold
        return {
            'threshold': threshold,
            'configured': True
        }

    def get_vad_config(self) -> Dict[str, Any]:
        """
        Get complete VAD configuration.

        Returns:
            Dictionary with all VAD config

        Example:
            >>> config = service.get_vad_config()
        """
        return {
            'aggressiveness': self._aggressiveness,
            'frame_duration_ms': self._frame_duration_ms,
            'speech_threshold': self._speech_threshold,
            'silence_threshold': self._silence_threshold
        }

    def reset_vad(self) -> Dict[str, Any]:
        """
        Reset VAD to default configuration.

        Returns:
            Dictionary with reset result

        Example:
            >>> result = service.reset_vad()
        """
        self._sessions = {}
        self._aggressiveness = 1
        self._frame_duration_ms = 30
        self._speech_threshold = 0.5
        self._silence_threshold = 0.3
        self._accuracy_samples = []
        self._endpoint_samples = []

        return {
            'reset': True,
            'timestamp': datetime.utcnow().isoformat()
        }

    def _update_segments(
        self,
        session: Dict[str, Any],
        is_speech: bool
    ) -> None:
        """Update segment tracking."""
        segment_type = 'speech' if is_speech else 'silence'
        current = session.get('current_segment')

        if current is None:
            # Start new segment
            session['current_segment'] = {
                'type': segment_type,
                'start_frame': len(session['frames']) - 1
            }
        elif current['type'] != segment_type:
            # End current segment and start new
            current['end_frame'] = len(session['frames']) - 1
            session['segments'].append(current)

            session['current_segment'] = {
                'type': segment_type,
                'start_frame': len(session['frames']) - 1
            }
