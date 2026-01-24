"""
VAD Analysis Mixin for segment analysis and accuracy metrics.

This mixin provides analysis and accuracy tracking methods for VADService:
- Speech/silence segment extraction
- Duration calculations
- Speech ratio analysis
- VAD accuracy tracking
- Endpoint detection

Extracted from vad_service.py to maintain 500-line limit per file.

Example:
    >>> class VADService(VADAnalysisMixin):
    ...     pass
"""

from typing import List, Dict, Any


class VADAnalysisMixin:
    """
    Mixin providing analysis and accuracy methods for VADService.

    This mixin contains:
    - Segment extraction methods
    - Duration calculation methods
    - Accuracy tracking methods
    - Endpoint detection methods
    """

    def get_speech_segments(
        self,
        session_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get detected speech segments.

        Args:
            session_id: Session identifier

        Returns:
            List of speech segments

        Example:
            >>> segments = service.get_speech_segments('session-1')
        """
        if session_id not in self._sessions:
            return []

        return [
            s for s in self._sessions[session_id].get('segments', [])
            if s.get('type') == 'speech'
        ]

    def get_silence_segments(
        self,
        session_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get detected silence segments.

        Args:
            session_id: Session identifier

        Returns:
            List of silence segments

        Example:
            >>> segments = service.get_silence_segments('session-1')
        """
        if session_id not in self._sessions:
            return []

        return [
            s for s in self._sessions[session_id].get('segments', [])
            if s.get('type') == 'silence'
        ]

    def get_segment_count(self, session_id: str) -> Dict[str, Any]:
        """
        Get count of segments.

        Args:
            session_id: Session identifier

        Returns:
            Dictionary with segment counts

        Example:
            >>> counts = service.get_segment_count('session-1')
        """
        speech = len(self.get_speech_segments(session_id))
        silence = len(self.get_silence_segments(session_id))

        return {
            'session_id': session_id,
            'speech_segments': speech,
            'silence_segments': silence,
            'total_segments': speech + silence
        }

    def get_speech_duration(self, session_id: str) -> Dict[str, Any]:
        """
        Get total speech duration.

        Args:
            session_id: Session identifier

        Returns:
            Dictionary with speech duration

        Example:
            >>> duration = service.get_speech_duration('session-1')
        """
        if session_id not in self._sessions:
            return {'error': 'Session not found'}

        session = self._sessions[session_id]
        speech_frames = sum(
            1 for f in session.get('frames', [])
            if f.get('is_speech')
        )
        duration_ms = speech_frames * self._frame_duration_ms

        return {
            'session_id': session_id,
            'duration_ms': duration_ms,
            'frame_count': speech_frames
        }

    def get_silence_duration(self, session_id: str) -> Dict[str, Any]:
        """
        Get total silence duration.

        Args:
            session_id: Session identifier

        Returns:
            Dictionary with silence duration

        Example:
            >>> duration = service.get_silence_duration('session-1')
        """
        if session_id not in self._sessions:
            return {'error': 'Session not found'}

        session = self._sessions[session_id]
        silence_frames = sum(
            1 for f in session.get('frames', [])
            if not f.get('is_speech')
        )
        duration_ms = silence_frames * self._frame_duration_ms

        return {
            'session_id': session_id,
            'duration_ms': duration_ms,
            'frame_count': silence_frames
        }

    def get_speech_ratio(self, session_id: str) -> Dict[str, Any]:
        """
        Get speech to total ratio.

        Args:
            session_id: Session identifier

        Returns:
            Dictionary with ratio

        Example:
            >>> ratio = service.get_speech_ratio('session-1')
        """
        if session_id not in self._sessions:
            return {'error': 'Session not found'}

        session = self._sessions[session_id]
        total = len(session.get('frames', []))
        if total == 0:
            return {
                'session_id': session_id,
                'ratio': 0.0
            }

        speech = sum(
            1 for f in session.get('frames', [])
            if f.get('is_speech')
        )
        ratio = speech / total

        return {
            'session_id': session_id,
            'ratio': ratio,
            'speech_frames': speech,
            'total_frames': total
        }

    def detect_voice_activity(
        self,
        session_id: str,
        audio_frame: bytes = None
    ) -> Dict[str, Any]:
        """
        Detect voice activity in audio frame.

        Args:
            session_id: Session identifier
            audio_frame: Audio frame data

        Returns:
            Dictionary with VAD detection result

        Example:
            >>> result = service.detect_voice_activity('session-1', frame)
        """
        return self.process_frame(session_id, audio_frame)

    def get_vad_accuracy(self) -> Dict[str, Any]:
        """
        Get VAD accuracy statistics.

        Returns:
            Dictionary with accuracy metrics

        Example:
            >>> accuracy = service.get_vad_accuracy()
        """
        if not self._accuracy_samples:
            return {
                'accuracy': 0.0,
                'samples': 0
            }

        correct = sum(1 for s in self._accuracy_samples if s.get('correct'))
        total = len(self._accuracy_samples)

        return {
            'accuracy': correct / total if total > 0 else 0.0,
            'correct': correct,
            'total': total
        }

    def detect_speech_start(
        self,
        session_id: str,
        audio_frame: bytes = None
    ) -> Dict[str, Any]:
        """
        Detect start of speech.

        Args:
            session_id: Session identifier
            audio_frame: Audio frame data

        Returns:
            Dictionary with speech start detection

        Example:
            >>> result = service.detect_speech_start('session-1', frame)
        """
        if session_id not in self._sessions:
            self.start_session(session_id)

        session = self._sessions[session_id]
        result = self.process_frame(session_id, audio_frame)

        # Check if this is transition to speech
        frames = session.get('frames', [])
        speech_started = (
            result.get('is_speech') and
            len(frames) >= 2 and
            not frames[-2].get('is_speech')
        )

        return {
            'session_id': session_id,
            'speech_started': speech_started,
            'is_speech': result.get('is_speech'),
            'frame_index': len(frames) - 1
        }

    def detect_speech_end(
        self,
        session_id: str,
        audio_frame: bytes = None
    ) -> Dict[str, Any]:
        """
        Detect end of speech.

        Args:
            session_id: Session identifier
            audio_frame: Audio frame data

        Returns:
            Dictionary with speech end detection

        Example:
            >>> result = service.detect_speech_end('session-1', frame)
        """
        if session_id not in self._sessions:
            self.start_session(session_id)

        session = self._sessions[session_id]
        result = self.process_frame(session_id, audio_frame)

        # Check if this is transition from speech
        frames = session.get('frames', [])
        speech_ended = (
            not result.get('is_speech') and
            len(frames) >= 2 and
            frames[-2].get('is_speech')
        )

        return {
            'session_id': session_id,
            'speech_ended': speech_ended,
            'is_speech': result.get('is_speech'),
            'frame_index': len(frames) - 1
        }

    def get_endpoint_accuracy(self) -> Dict[str, Any]:
        """
        Get endpoint detection accuracy.

        Returns:
            Dictionary with endpoint accuracy metrics

        Example:
            >>> accuracy = service.get_endpoint_accuracy()
        """
        if not self._endpoint_samples:
            return {
                'accuracy': 0.0,
                'samples': 0
            }

        correct = sum(1 for s in self._endpoint_samples if s.get('correct'))
        total = len(self._endpoint_samples)

        return {
            'accuracy': correct / total if total > 0 else 0.0,
            'correct': correct,
            'total': total
        }

    def detect_silence(
        self,
        session_id: str,
        audio_frame: bytes = None
    ) -> Dict[str, Any]:
        """
        Detect silence in audio frame.

        Args:
            session_id: Session identifier
            audio_frame: Audio frame data

        Returns:
            Dictionary with silence detection result

        Example:
            >>> result = service.detect_silence('session-1', frame)
        """
        result = self.process_frame(session_id, audio_frame)
        is_silence = not result.get('is_speech', True)

        return {
            'session_id': session_id,
            'is_silence': is_silence,
            'probability': result.get('probability', 0)
        }

    def get_vad_stats(
        self,
        session_id: str = None
    ) -> Dict[str, Any]:
        """
        Get VAD statistics.

        Args:
            session_id: Optional session to get stats for

        Returns:
            Dictionary with VAD statistics

        Example:
            >>> stats = service.get_vad_stats()
        """
        if session_id:
            if session_id not in self._sessions:
                return {'error': 'Session not found'}

            session = self._sessions[session_id]
            frames = session.get('frames', [])
            speech_frames = sum(1 for f in frames if f.get('is_speech'))

            return {
                'session_id': session_id,
                'total_frames': len(frames),
                'speech_frames': speech_frames,
                'silence_frames': len(frames) - speech_frames,
                'segments': len(session.get('segments', []))
            }

        # Global stats
        total_sessions = len(self._sessions)
        total_frames = sum(
            len(s.get('frames', []))
            for s in self._sessions.values()
        )

        return {
            'total_sessions': total_sessions,
            'total_frames': total_frames,
            'accuracy_samples': len(self._accuracy_samples),
            'endpoint_samples': len(self._endpoint_samples)
        }
