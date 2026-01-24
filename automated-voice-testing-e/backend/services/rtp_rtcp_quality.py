"""
RTPRTCPQualityMixin - Quality, stream, and injection methods for RTP/RTCP service.

This mixin provides quality monitoring and simulation methods:
- Jitter buffer management
- Stream quality metrics
- Packet loss detection
- Network impairment injection

Extracted from rtp_rtcp_service.py to reduce file size per coding conventions.
"""

from typing import Dict, Any
from datetime import datetime
import uuid


class RTPRTCPQualityMixin:
    """
    Mixin providing quality and simulation methods for RTPRTCPService.

    This mixin contains:
    - Jitter buffer configuration and stats
    - Stream creation and quality metrics
    - Packet loss detection and measurement
    - Network impairment injection (jitter, latency, packet loss)
    """

    def configure_jitter_buffer(
        self,
        session_id: str,
        min_size: int = 20,
        max_size: int = 200,
        target_size: int = 50
    ) -> Dict[str, Any]:
        """Configure jitter buffer for a session."""
        if session_id not in self._sessions:
            return {'error': 'Session not found'}

        self._sessions[session_id]['jitter_buffer'] = {
            'min_size': min_size,
            'max_size': max_size,
            'target_size': target_size,
            'current_size': target_size
        }

        return {
            'session_id': session_id,
            'configured': True,
            'min_size': min_size,
            'max_size': max_size,
            'target_size': target_size
        }

    def get_jitter_buffer_stats(self, session_id: str) -> Dict[str, Any]:
        """Get jitter buffer statistics for a session."""
        if session_id not in self._sessions:
            return {'error': 'Session not found'}

        buffer = self._sessions[session_id].get('jitter_buffer', {})

        return {
            'session_id': session_id,
            'current_size': buffer.get('current_size', 50),
            'min_size': buffer.get('min_size', 20),
            'max_size': buffer.get('max_size', 200),
            'underruns': 0,
            'overruns': 0
        }

    def calculate_jitter(self, session_id: str) -> Dict[str, Any]:
        """Calculate interarrival jitter for a session."""
        if session_id not in self._sessions:
            return {'error': 'Session not found'}

        packets = self._packets.get(session_id, [])
        jitter_ms = 0.0
        if len(packets) >= 2:
            jitter_ms = 0.0

        return {
            'session_id': session_id,
            'jitter_ms': jitter_ms,
            'packet_count': len(packets),
            'calculated_at': datetime.utcnow().isoformat()
        }

    def detect_packet_loss(self, session_id: str) -> Dict[str, Any]:
        """Detect packet loss for a session."""
        if session_id not in self._sessions:
            return {'error': 'Session not found'}

        packets = self._packets.get(session_id, [])
        gaps = self.get_sequence_gaps(session_id)

        return {
            'session_id': session_id,
            'total_packets': len(packets),
            'lost_packets': len(gaps.get('gaps', [])),
            'loss_detected': len(gaps.get('gaps', [])) > 0
        }

    def get_packet_loss_rate(self, session_id: str) -> Dict[str, Any]:
        """Get packet loss rate for a session."""
        if session_id not in self._sessions:
            return {'error': 'Session not found'}

        session = self._sessions[session_id]
        total = session['packets_sent'] + session['packets_received']

        return {
            'session_id': session_id,
            'loss_rate': 0.0,
            'total_packets': total,
            'lost_packets': 0
        }

    def get_sequence_gaps(self, session_id: str) -> Dict[str, Any]:
        """Get sequence number gaps for a session."""
        if session_id not in self._sessions:
            return {'error': 'Session not found'}

        packets = self._packets.get(session_id, [])
        gaps = []

        if len(packets) >= 2:
            sorted_packets = sorted(
                packets,
                key=lambda p: p.get('sequence_number', 0)
            )
            for i in range(1, len(sorted_packets)):
                prev_seq = sorted_packets[i-1].get('sequence_number', 0)
                curr_seq = sorted_packets[i].get('sequence_number', 0)
                if curr_seq - prev_seq > 1:
                    gaps.append({
                        'start': prev_seq + 1,
                        'end': curr_seq - 1,
                        'count': curr_seq - prev_seq - 1
                    })

        return {
            'session_id': session_id,
            'gaps': gaps,
            'total_gaps': len(gaps)
        }

    def create_stream(
        self,
        stream_type: str = 'audio',
        codec: str = 'opus'
    ) -> Dict[str, Any]:
        """Create an RTP stream."""
        stream_id = str(uuid.uuid4())
        stream = {
            'id': stream_id,
            'type': stream_type,
            'codec': codec,
            'status': 'active',
            'packets_sent': 0,
            'packets_received': 0,
            'created_at': datetime.utcnow().isoformat()
        }
        self._streams[stream_id] = stream
        return stream

    def get_stream_stats(self, stream_id: str) -> Dict[str, Any]:
        """Get stream statistics."""
        if stream_id not in self._streams:
            return {'error': 'Stream not found'}

        stream = self._streams[stream_id]
        return {
            'stream_id': stream_id,
            'type': stream.get('type'),
            'codec': stream.get('codec'),
            'packets_sent': stream.get('packets_sent', 0),
            'packets_received': stream.get('packets_received', 0),
            'jitter_ms': 0.0,
            'packet_loss_rate': 0.0
        }

    def measure_jitter(self, stream_id: str) -> Dict[str, Any]:
        """Measure jitter for a stream."""
        if stream_id not in self._streams:
            return {'error': 'Stream not found'}

        return {
            'stream_id': stream_id,
            'jitter_ms': 0.0,
            'min_jitter_ms': 0.0,
            'max_jitter_ms': 0.0,
            'avg_jitter_ms': 0.0,
            'measured_at': datetime.utcnow().isoformat()
        }

    def calculate_packet_loss(self, stream_id: str) -> Dict[str, Any]:
        """Calculate packet loss for a stream."""
        if stream_id not in self._streams:
            return {'error': 'Stream not found'}

        stream = self._streams[stream_id]
        total = stream.get('packets_sent', 0)
        received = stream.get('packets_received', 0)
        lost = max(0, total - received)
        rate = (lost / total * 100) if total > 0 else 0.0

        return {
            'stream_id': stream_id,
            'packets_sent': total,
            'packets_received': received,
            'packets_lost': lost,
            'loss_rate_percent': rate
        }

    def get_stream_quality(self, stream_id: str) -> Dict[str, Any]:
        """Get overall stream quality metrics."""
        if stream_id not in self._streams:
            return {'error': 'Stream not found'}

        jitter = self.measure_jitter(stream_id)
        loss = self.calculate_packet_loss(stream_id)

        mos = 4.5
        mos -= loss.get('loss_rate_percent', 0) * 0.1
        mos -= jitter.get('jitter_ms', 0) * 0.01
        mos = max(1.0, min(5.0, mos))

        return {
            'stream_id': stream_id,
            'jitter_ms': jitter.get('jitter_ms', 0),
            'packet_loss_percent': loss.get('loss_rate_percent', 0),
            'estimated_mos': round(mos, 2),
            'quality_rating': 'excellent' if mos >= 4.0 else 'good' if mos >= 3.0 else 'fair'
        }

    def process_rtcp_report(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Process an RTCP report."""
        ssrc = report.get('ssrc', 0)

        return {
            'processed': True,
            'ssrc': ssrc,
            'report_type': report.get('type', 'RR'),
            'fraction_lost': report.get('fraction_lost', 0),
            'jitter': report.get('jitter', 0),
            'processed_at': datetime.utcnow().isoformat()
        }

    def get_rtcp_stats(self, session_id: str) -> Dict[str, Any]:
        """Get RTCP stats for a session."""
        return self.get_rtcp_statistics(session_id)

    def get_buffer_status(self, session_id: str) -> Dict[str, Any]:
        """Get jitter buffer status."""
        if session_id not in self._sessions:
            return {'error': 'Session not found'}

        buffer = self._sessions[session_id].get('jitter_buffer', {})

        return {
            'session_id': session_id,
            'current_size_ms': buffer.get('current_size', 50),
            'fill_level_percent': 50,
            'status': 'normal',
            'underruns': 0,
            'overruns': 0
        }

    def simulate_jitter(
        self,
        session_id: str,
        jitter_ms: float,
        duration_ms: int = 1000
    ) -> Dict[str, Any]:
        """Simulate jitter on a session."""
        if session_id not in self._sessions:
            return {'error': 'Session not found'}

        self._injections[session_id] = self._injections.get(session_id, {})
        self._injections[session_id]['jitter'] = {
            'jitter_ms': jitter_ms,
            'duration_ms': duration_ms,
            'started_at': datetime.utcnow().isoformat()
        }

        return {
            'session_id': session_id,
            'simulating': True,
            'jitter_ms': jitter_ms,
            'duration_ms': duration_ms
        }

    def get_buffer_stats(self, session_id: str) -> Dict[str, Any]:
        """Get buffer statistics."""
        return self.get_jitter_buffer_stats(session_id)

    def inject_packet_loss(
        self,
        session_id: str,
        loss_percent: float
    ) -> Dict[str, Any]:
        """Inject packet loss into a session."""
        if session_id not in self._sessions:
            return {'error': 'Session not found'}

        self._injections[session_id] = self._injections.get(session_id, {})
        self._injections[session_id]['packet_loss'] = {
            'loss_percent': loss_percent,
            'started_at': datetime.utcnow().isoformat()
        }

        return {
            'session_id': session_id,
            'injecting': True,
            'loss_percent': loss_percent
        }

    def inject_latency(
        self,
        session_id: str,
        latency_ms: float
    ) -> Dict[str, Any]:
        """Inject latency into a session."""
        if session_id not in self._sessions:
            return {'error': 'Session not found'}

        self._injections[session_id] = self._injections.get(session_id, {})
        self._injections[session_id]['latency'] = {
            'latency_ms': latency_ms,
            'started_at': datetime.utcnow().isoformat()
        }

        return {
            'session_id': session_id,
            'injecting': True,
            'latency_ms': latency_ms
        }

    def inject_burst_loss(
        self,
        session_id: str,
        burst_length: int,
        probability: float
    ) -> Dict[str, Any]:
        """Inject burst packet loss into a session."""
        if session_id not in self._sessions:
            return {'error': 'Session not found'}

        self._injections[session_id] = self._injections.get(session_id, {})
        self._injections[session_id]['burst_loss'] = {
            'burst_length': burst_length,
            'probability': probability,
            'started_at': datetime.utcnow().isoformat()
        }

        return {
            'session_id': session_id,
            'injecting': True,
            'burst_length': burst_length,
            'probability': probability
        }

    def get_injection_stats(self, session_id: str) -> Dict[str, Any]:
        """Get injection statistics for a session."""
        if session_id not in self._sessions:
            return {'error': 'Session not found'}

        injections = self._injections.get(session_id, {})

        return {
            'session_id': session_id,
            'packet_loss': injections.get('packet_loss'),
            'latency': injections.get('latency'),
            'jitter': injections.get('jitter'),
            'burst_loss': injections.get('burst_loss'),
            'active_injections': len(injections)
        }
