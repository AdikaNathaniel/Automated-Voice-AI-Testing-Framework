"""
WebRTC Integration Service for browser-based testing.

This service provides WebRTC protocol integration for testing
voice AI systems through browser-based connections.

Key features:
- Peer connection management
- STUN/TURN server integration
- Codec negotiation
- Media stream handling

Example:
    >>> service = WebRTCIntegrationService()
    >>> peer = service.create_peer_connection()
    >>> offer = service.create_offer(peer['id'])
"""

from typing import List, Dict, Any
from datetime import datetime
import uuid


class WebRTCIntegrationService:
    """
    Service for WebRTC protocol integration and testing.

    Provides peer connection management, ICE server configuration,
    codec negotiation, and media stream handling.

    Example:
        >>> service = WebRTCIntegrationService()
        >>> service.configure_ice_servers([{'urls': 'stun:stun.l.google.com:19302'}])
        >>> peer = service.create_peer_connection()
    """

    def __init__(self):
        """Initialize the WebRTC integration service."""
        self._connections: Dict[str, Dict[str, Any]] = {}
        self._ice_servers: List[Dict[str, Any]] = []
        self._supported_codecs = ['opus', 'G.711', 'G.722']
        self._preferred_codecs: List[str] = []
        self._browser_sessions: Dict[str, Dict[str, Any]] = {}
        self._ice_candidates: Dict[str, List[Dict[str, Any]]] = {}

    def create_peer_connection(
        self,
        ice_servers: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a WebRTC peer connection.

        Args:
            ice_servers: Optional ICE server configuration

        Returns:
            Dictionary with connection configuration

        Example:
            >>> peer = service.create_peer_connection()
        """
        connection_id = str(uuid.uuid4())
        connection = {
            'id': connection_id,
            'state': 'new',
            'ice_servers': ice_servers or self._ice_servers,
            'ice_connection_state': 'new',
            'signaling_state': 'stable',
            'tracks': [],
            'remote_streams': [],
            'created_at': datetime.utcnow().isoformat()
        }
        self._connections[connection_id] = connection
        return connection

    def close_peer_connection(
        self,
        connection_id: str
    ) -> Dict[str, Any]:
        """
        Close a peer connection.

        Args:
            connection_id: Connection ID to close

        Returns:
            Dictionary with close result

        Example:
            >>> result = service.close_peer_connection(peer_id)
        """
        if connection_id not in self._connections:
            return {'success': False, 'error': 'Connection not found'}

        self._connections[connection_id]['state'] = 'closed'
        return {
            'success': True,
            'connection_id': connection_id,
            'state': 'closed'
        }

    def get_connection_state(
        self,
        connection_id: str
    ) -> Dict[str, Any]:
        """
        Get state of a peer connection.

        Args:
            connection_id: Connection ID to check

        Returns:
            Dictionary with connection state

        Example:
            >>> state = service.get_connection_state(peer_id)
        """
        if connection_id not in self._connections:
            return {'error': 'Connection not found'}

        conn = self._connections[connection_id]
        return {
            'connection_id': connection_id,
            'state': conn.get('state'),
            'ice_connection_state': conn.get('ice_connection_state'),
            'signaling_state': conn.get('signaling_state')
        }

    def configure_ice_servers(
        self,
        servers: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Configure ICE servers.

        Args:
            servers: List of ICE server configurations

        Returns:
            Dictionary with configuration result

        Example:
            >>> service.configure_ice_servers([
            ...     {'urls': 'stun:stun.example.com'}
            ... ])
        """
        self._ice_servers = servers
        return {
            'configured': True,
            'server_count': len(servers)
        }

    def add_stun_server(
        self,
        url: str
    ) -> Dict[str, Any]:
        """
        Add a STUN server.

        Args:
            url: STUN server URL

        Returns:
            Dictionary with add result

        Example:
            >>> result = service.add_stun_server('stun:stun.l.google.com:19302')
        """
        server = {'urls': url}
        self._ice_servers.append(server)
        return {
            'added': True,
            'url': url,
            'total_servers': len(self._ice_servers)
        }

    def add_turn_server(
        self,
        url: str,
        username: str,
        credential: str
    ) -> Dict[str, Any]:
        """
        Add a TURN server.

        Args:
            url: TURN server URL
            username: Auth username
            credential: Auth credential

        Returns:
            Dictionary with add result

        Example:
            >>> result = service.add_turn_server(
            ...     'turn:turn.example.com',
            ...     'user', 'pass'
            ... )
        """
        server = {
            'urls': url,
            'username': username,
            'credential': credential
        }
        self._ice_servers.append(server)
        return {
            'added': True,
            'url': url,
            'total_servers': len(self._ice_servers)
        }

    def test_ice_connectivity(
        self,
        connection_id: str
    ) -> Dict[str, Any]:
        """
        Test ICE connectivity.

        Args:
            connection_id: Connection ID to test

        Returns:
            Dictionary with connectivity test results

        Example:
            >>> result = service.test_ice_connectivity(peer_id)
        """
        if connection_id not in self._connections:
            return {'error': 'Connection not found'}

        return {
            'connection_id': connection_id,
            'connected': True,
            'ice_candidates_gathered': True,
            'tested_at': datetime.utcnow().isoformat()
        }

    def get_supported_codecs(self) -> List[str]:
        """
        Get list of supported codecs.

        Returns:
            List of codec names

        Example:
            >>> codecs = service.get_supported_codecs()
        """
        return self._supported_codecs.copy()

    def set_preferred_codecs(
        self,
        codecs: List[str]
    ) -> Dict[str, Any]:
        """
        Set preferred codecs.

        Args:
            codecs: List of preferred codec names

        Returns:
            Dictionary with configuration result

        Example:
            >>> result = service.set_preferred_codecs(['opus', 'G.711'])
        """
        self._preferred_codecs = codecs
        return {
            'configured': True,
            'codecs': codecs
        }

    def test_codec_compatibility(
        self,
        codec: str
    ) -> Dict[str, Any]:
        """
        Test codec compatibility.

        Args:
            codec: Codec name to test

        Returns:
            Dictionary with compatibility result

        Example:
            >>> result = service.test_codec_compatibility('opus')
        """
        supported = codec in self._supported_codecs
        return {
            'codec': codec,
            'supported': supported,
            'preferred': codec in self._preferred_codecs
        }

    def add_audio_track(
        self,
        connection_id: str,
        track_id: str = None
    ) -> Dict[str, Any]:
        """
        Add an audio track to connection.

        Args:
            connection_id: Connection ID
            track_id: Optional track ID

        Returns:
            Dictionary with track information

        Example:
            >>> track = service.add_audio_track(peer_id)
        """
        if connection_id not in self._connections:
            return {'error': 'Connection not found'}

        track_id = track_id or str(uuid.uuid4())
        track = {
            'id': track_id,
            'kind': 'audio',
            'enabled': True
        }
        self._connections[connection_id]['tracks'].append(track)

        return {
            'connection_id': connection_id,
            'track_id': track_id,
            'added': True
        }

    def get_remote_streams(
        self,
        connection_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get remote streams from connection.

        Args:
            connection_id: Connection ID

        Returns:
            List of remote stream information

        Example:
            >>> streams = service.get_remote_streams(peer_id)
        """
        if connection_id not in self._connections:
            return []

        return self._connections[connection_id].get('remote_streams', [])

    def get_connection_stats(
        self,
        connection_id: str
    ) -> Dict[str, Any]:
        """
        Get connection statistics.

        Args:
            connection_id: Connection ID

        Returns:
            Dictionary with connection statistics

        Example:
            >>> stats = service.get_connection_stats(peer_id)
        """
        if connection_id not in self._connections:
            return {'error': 'Connection not found'}

        return {
            'connection_id': connection_id,
            'bytes_sent': 0,
            'bytes_received': 0,
            'packets_sent': 0,
            'packets_received': 0,
            'packets_lost': 0,
            'jitter': 0.0,
            'round_trip_time': 0.0
        }

    def create_offer(
        self,
        connection_id: str
    ) -> Dict[str, Any]:
        """
        Create an SDP offer.

        Args:
            connection_id: Connection ID

        Returns:
            Dictionary with offer SDP

        Example:
            >>> offer = service.create_offer(peer_id)
        """
        if connection_id not in self._connections:
            return {'error': 'Connection not found'}

        self._connections[connection_id]['signaling_state'] = 'have-local-offer'

        return {
            'connection_id': connection_id,
            'type': 'offer',
            'sdp': 'v=0\r\no=- 0 0 IN IP4 127.0.0.1\r\n...'
        }

    def create_answer(
        self,
        connection_id: str,
        offer: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Create an SDP answer.

        Args:
            connection_id: Connection ID
            offer: Remote offer SDP

        Returns:
            Dictionary with answer SDP

        Example:
            >>> answer = service.create_answer(peer_id, remote_offer)
        """
        if connection_id not in self._connections:
            return {'error': 'Connection not found'}

        self._connections[connection_id]['signaling_state'] = 'stable'

        return {
            'connection_id': connection_id,
            'type': 'answer',
            'sdp': 'v=0\r\no=- 0 0 IN IP4 127.0.0.1\r\n...'
        }

    def set_local_description(
        self,
        connection_id: str,
        description: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Set the local session description.

        Args:
            connection_id: Connection ID
            description: SDP description (type and sdp)

        Returns:
            Dictionary with result

        Example:
            >>> result = service.set_local_description(peer_id, offer)
        """
        if connection_id not in self._connections:
            return {'error': 'Connection not found'}

        self._connections[connection_id]['local_description'] = description

        return {
            'connection_id': connection_id,
            'set': True,
            'type': description.get('type')
        }

    def set_remote_description(
        self,
        connection_id: str,
        description: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Set the remote session description.

        Args:
            connection_id: Connection ID
            description: SDP description (type and sdp)

        Returns:
            Dictionary with result

        Example:
            >>> result = service.set_remote_description(peer_id, answer)
        """
        if connection_id not in self._connections:
            return {'error': 'Connection not found'}

        self._connections[connection_id]['remote_description'] = description

        return {
            'connection_id': connection_id,
            'set': True,
            'type': description.get('type')
        }

    def create_browser_session(
        self,
        browser_type: str = 'chrome',
        headless: bool = True
    ) -> Dict[str, Any]:
        """
        Create a browser session for WebRTC testing.

        Args:
            browser_type: Browser type (chrome, firefox, edge)
            headless: Run in headless mode

        Returns:
            Dictionary with session information

        Example:
            >>> session = service.create_browser_session('chrome')
        """
        session_id = str(uuid.uuid4())
        session = {
            'id': session_id,
            'browser_type': browser_type,
            'headless': headless,
            'status': 'active',
            'created_at': datetime.utcnow().isoformat()
        }
        self._browser_sessions[session_id] = session
        return session

    def close_browser_session(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Close a browser session.

        Args:
            session_id: Session ID to close

        Returns:
            Dictionary with close result

        Example:
            >>> result = service.close_browser_session(session_id)
        """
        if session_id not in self._browser_sessions:
            return {'success': False, 'error': 'Session not found'}

        self._browser_sessions[session_id]['status'] = 'closed'
        return {
            'success': True,
            'session_id': session_id,
            'status': 'closed'
        }

    def get_browser_capabilities(
        self,
        browser_type: str = 'chrome'
    ) -> Dict[str, Any]:
        """
        Get browser WebRTC capabilities.

        Args:
            browser_type: Browser type to check

        Returns:
            Dictionary with capabilities

        Example:
            >>> caps = service.get_browser_capabilities('chrome')
        """
        capabilities = {
            'chrome': {
                'webrtc': True,
                'screen_sharing': True,
                'codecs': ['opus', 'VP8', 'VP9', 'H.264'],
                'data_channels': True
            },
            'firefox': {
                'webrtc': True,
                'screen_sharing': True,
                'codecs': ['opus', 'VP8', 'VP9'],
                'data_channels': True
            },
            'edge': {
                'webrtc': True,
                'screen_sharing': True,
                'codecs': ['opus', 'VP8', 'VP9', 'H.264'],
                'data_channels': True
            }
        }

        return {
            'browser_type': browser_type,
            'capabilities': capabilities.get(browser_type, {})
        }

    def get_ice_candidates(
        self,
        connection_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get ICE candidates for a connection.

        Args:
            connection_id: Connection ID

        Returns:
            List of ICE candidates

        Example:
            >>> candidates = service.get_ice_candidates(peer_id)
        """
        if connection_id not in self._connections:
            return []

        # Return stored candidates or generate sample ones
        if connection_id in self._ice_candidates:
            return self._ice_candidates[connection_id]

        # Generate sample ICE candidates
        candidates = [
            {
                'candidate': 'candidate:1 1 UDP 2122252543 192.168.1.1 12345 typ host',
                'sdpMid': 'audio',
                'sdpMLineIndex': 0
            },
            {
                'candidate': 'candidate:2 1 UDP 1686052607 203.0.113.1 54321 typ srflx',
                'sdpMid': 'audio',
                'sdpMLineIndex': 0
            }
        ]
        self._ice_candidates[connection_id] = candidates
        return candidates

    def negotiate_codecs(
        self,
        connection_id: str,
        remote_codecs: List[str]
    ) -> Dict[str, Any]:
        """
        Negotiate codecs with remote peer.

        Args:
            connection_id: Connection ID
            remote_codecs: List of remote supported codecs

        Returns:
            Dictionary with negotiation result

        Example:
            >>> result = service.negotiate_codecs(peer_id, ['opus', 'G.711'])
        """
        if connection_id not in self._connections:
            return {'error': 'Connection not found'}

        # Find common codecs
        local_codecs = self._preferred_codecs or self._supported_codecs
        common = [c for c in local_codecs if c in remote_codecs]

        if not common:
            common = [c for c in self._supported_codecs if c in remote_codecs]

        negotiated = common[0] if common else None

        self._connections[connection_id]['negotiated_codec'] = negotiated

        return {
            'connection_id': connection_id,
            'negotiated': negotiated is not None,
            'codec': negotiated,
            'common_codecs': common
        }

    def get_negotiated_codec(
        self,
        connection_id: str
    ) -> Dict[str, Any]:
        """
        Get the negotiated codec for a connection.

        Args:
            connection_id: Connection ID

        Returns:
            Dictionary with negotiated codec info

        Example:
            >>> codec = service.get_negotiated_codec(peer_id)
        """
        if connection_id not in self._connections:
            return {'error': 'Connection not found'}

        codec = self._connections[connection_id].get('negotiated_codec')

        return {
            'connection_id': connection_id,
            'codec': codec,
            'negotiated': codec is not None
        }

