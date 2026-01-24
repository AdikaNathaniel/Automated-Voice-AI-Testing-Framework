"""
RTP/RTCP Handling Service for voice testing.

This service provides RTP (Real-time Transport Protocol) and
RTCP (RTP Control Protocol) handling for voice AI testing.

Key features:
- RTP packet handling
- RTCP statistics
- Jitter buffer management
- Packet loss detection

Example:
    >>> service = RTPRTCPService()
    >>> session = service.create_rtp_session(local_port=5000)
    >>> service.send_rtp_packet(session['id'], payload=b'audio_data')
    >>> stats = service.get_rtcp_statistics(session['id'])
"""

from typing import List, Dict, Any
from datetime import datetime
import uuid

# Import quality mixin
from services.rtp_rtcp_quality import RTPRTCPQualityMixin


class RTPRTCPService(RTPRTCPQualityMixin):
    """
    Service for RTP/RTCP protocol handling.

    Provides RTP packet handling, RTCP statistics,
    jitter buffer management, and packet loss detection.

    This class inherits from:
    - RTPRTCPQualityMixin: Quality metrics, streams, and injection methods

    Example:
        >>> service = RTPRTCPService()
        >>> session = service.create_rtp_session(local_port=5004)
        >>> jitter = service.calculate_jitter(session['id'])
        >>> print(f"Jitter: {jitter['jitter_ms']:.2f} ms")
    """

    def __init__(self):
        """Initialize the RTP/RTCP service."""
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._packets: Dict[str, List[Dict[str, Any]]] = {}
        self._rtcp_reports: Dict[str, List[Dict[str, Any]]] = {}
        self._streams: Dict[str, Dict[str, Any]] = {}
        self._injections: Dict[str, Dict[str, Any]] = {}

    def create_rtp_session(
        self,
        local_port: int,
        remote_host: str = "",
        remote_port: int = 0,
        payload_type: int = 0
    ) -> Dict[str, Any]:
        """
        Create an RTP session.

        Args:
            local_port: Local port to bind
            remote_host: Remote host address
            remote_port: Remote port
            payload_type: RTP payload type

        Returns:
            Dictionary with session configuration

        Example:
            >>> session = service.create_rtp_session(5004)
        """
        session_id = str(uuid.uuid4())
        session = {
            'id': session_id,
            'local_port': local_port,
            'remote_host': remote_host,
            'remote_port': remote_port,
            'payload_type': payload_type,
            'ssrc': uuid.uuid4().int & 0xFFFFFFFF,
            'sequence_number': 0,
            'timestamp': 0,
            'packets_sent': 0,
            'packets_received': 0,
            'bytes_sent': 0,
            'bytes_received': 0,
            'jitter_buffer_size': 50,
            'status': 'active',
            'created_at': datetime.utcnow().isoformat()
        }
        self._sessions[session_id] = session
        self._packets[session_id] = []
        self._rtcp_reports[session_id] = []
        return session

    def send_rtp_packet(
        self,
        session_id: str,
        payload: bytes,
        marker: bool = False
    ) -> Dict[str, Any]:
        """
        Send an RTP packet.

        Args:
            session_id: Session ID
            payload: Packet payload data
            marker: Marker bit flag

        Returns:
            Dictionary with send result

        Example:
            >>> result = service.send_rtp_packet(session_id, b'audio')
        """
        if session_id not in self._sessions:
            return {'error': 'Session not found'}

        session = self._sessions[session_id]
        session['sequence_number'] += 1
        session['timestamp'] += 160
        session['packets_sent'] += 1
        session['bytes_sent'] += len(payload)

        packet = {
            'sequence_number': session['sequence_number'],
            'timestamp': session['timestamp'],
            'ssrc': session['ssrc'],
            'payload_size': len(payload),
            'marker': marker,
            'sent_at': datetime.utcnow().isoformat()
        }
        self._packets[session_id].append(packet)

        return {
            'session_id': session_id,
            'sequence_number': session['sequence_number'],
            'sent': True
        }

    def receive_rtp_packet(
        self,
        session_id: str,
        packet_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process a received RTP packet.

        Args:
            session_id: Session ID
            packet_data: Received packet data

        Returns:
            Dictionary with receive result

        Example:
            >>> result = service.receive_rtp_packet(session_id, packet)
        """
        if session_id not in self._sessions:
            return {'error': 'Session not found'}

        session = self._sessions[session_id]
        session['packets_received'] += 1
        session['bytes_received'] += packet_data.get('payload_size', 0)

        packet = {
            'sequence_number': packet_data.get('sequence_number', 0),
            'timestamp': packet_data.get('timestamp', 0),
            'ssrc': packet_data.get('ssrc', 0),
            'payload_size': packet_data.get('payload_size', 0),
            'received_at': datetime.utcnow().isoformat()
        }
        self._packets[session_id].append(packet)

        return {
            'session_id': session_id,
            'sequence_number': packet['sequence_number'],
            'received': True
        }

    def close_rtp_session(self, session_id: str) -> Dict[str, Any]:
        """
        Close an RTP session.

        Args:
            session_id: Session ID to close

        Returns:
            Dictionary with close result

        Example:
            >>> result = service.close_rtp_session(session_id)
        """
        if session_id not in self._sessions:
            return {'success': False, 'error': 'Session not found'}

        self._sessions[session_id]['status'] = 'closed'
        return {
            'success': True,
            'session_id': session_id,
            'status': 'closed'
        }

    def send_rtcp_report(
        self,
        session_id: str,
        report_type: str = "SR"
    ) -> Dict[str, Any]:
        """
        Send an RTCP report.

        Args:
            session_id: Session ID
            report_type: Report type (SR, RR)

        Returns:
            Dictionary with report data

        Example:
            >>> report = service.send_rtcp_report(session_id)
        """
        if session_id not in self._sessions:
            return {'error': 'Session not found'}

        session = self._sessions[session_id]
        report = {
            'type': report_type,
            'ssrc': session['ssrc'],
            'packets_sent': session['packets_sent'],
            'bytes_sent': session['bytes_sent'],
            'ntp_timestamp': datetime.utcnow().timestamp(),
            'sent_at': datetime.utcnow().isoformat()
        }
        self._rtcp_reports[session_id].append(report)

        return {
            'session_id': session_id,
            'report': report,
            'sent': True
        }

    def receive_rtcp_report(
        self,
        session_id: str,
        report_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process a received RTCP report.

        Args:
            session_id: Session ID
            report_data: Received report data

        Returns:
            Dictionary with receive result

        Example:
            >>> result = service.receive_rtcp_report(session_id, report)
        """
        if session_id not in self._sessions:
            return {'error': 'Session not found'}

        report = {
            'type': report_data.get('type', 'RR'),
            'ssrc': report_data.get('ssrc', 0),
            'fraction_lost': report_data.get('fraction_lost', 0),
            'cumulative_lost': report_data.get('cumulative_lost', 0),
            'jitter': report_data.get('jitter', 0),
            'received_at': datetime.utcnow().isoformat()
        }
        self._rtcp_reports[session_id].append(report)

        return {
            'session_id': session_id,
            'report': report,
            'received': True
        }

    def get_rtcp_statistics(self, session_id: str) -> Dict[str, Any]:
        """
        Get RTCP statistics for a session.

        Args:
            session_id: Session ID

        Returns:
            Dictionary with RTCP statistics

        Example:
            >>> stats = service.get_rtcp_statistics(session_id)
        """
        if session_id not in self._sessions:
            return {'error': 'Session not found'}

        session = self._sessions[session_id]
        reports = self._rtcp_reports.get(session_id, [])

        return {
            'session_id': session_id,
            'packets_sent': session['packets_sent'],
            'packets_received': session['packets_received'],
            'bytes_sent': session['bytes_sent'],
            'bytes_received': session['bytes_received'],
            'report_count': len(reports),
            'last_report': reports[-1] if reports else None
        }

    def calculate_rtt(self, session_id: str) -> Dict[str, Any]:
        """
        Calculate round-trip time.

        Args:
            session_id: Session ID

        Returns:
            Dictionary with RTT calculation

        Example:
            >>> rtt = service.calculate_rtt(session_id)
        """
        if session_id not in self._sessions:
            return {'error': 'Session not found'}

        return {
            'session_id': session_id,
            'rtt_ms': 0.0,
            'last_sr_timestamp': 0,
            'delay_since_sr': 0,
            'calculated_at': datetime.utcnow().isoformat()
        }

    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """
        Get session information.

        Args:
            session_id: Session ID

        Returns:
            Dictionary with session info

        Example:
            >>> info = service.get_session_info(session_id)
        """
        if session_id not in self._sessions:
            return {'error': 'Session not found'}

        session = self._sessions[session_id]
        return {
            'session_id': session_id,
            'local_port': session.get('local_port'),
            'remote_host': session.get('remote_host'),
            'remote_port': session.get('remote_port'),
            'ssrc': session.get('ssrc'),
            'status': session.get('status'),
            'packets_sent': session.get('packets_sent'),
            'packets_received': session.get('packets_received')
        }

    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """
        Get all RTP sessions.

        Returns:
            List of session information

        Example:
            >>> sessions = service.get_all_sessions()
        """
        return [
            self.get_session_info(session_id)
            for session_id in self._sessions
        ]
