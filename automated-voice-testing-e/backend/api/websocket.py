"""
WebSocket Manager for Real-time Test Execution Updates

This module provides Socket.IO based WebSocket functionality for real-time
communication between the backend and frontend clients. It enables:
- Client connection management with authentication
- Room-based subscriptions to specific suite runs
- Real-time updates for test execution progress

The WebSocket manager uses Socket.IO with ASGI mode for integration with FastAPI.
"""

import socketio
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Create Socket.IO AsyncServer with ASGI mode for FastAPI integration
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',  # Allow all origins in development
    logger=True,
    engineio_logger=True
)


async def _validate_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Validate JWT token and return user info.

    Args:
        token: JWT token string

    Returns:
        User info dict if valid, None if invalid
    """
    from api.config import get_settings

    try:
        import jwt
    except ImportError:
        logger.error("PyJWT library not installed")
        return None

    try:
        settings = get_settings()

        # Decode and validate token
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        # Check expiration (jwt.decode handles this automatically with default options)
        return {
            "user_id": payload.get("sub"),
            "email": payload.get("email"),
            "role": payload.get("role"),
        }
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token has expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT token: {e}")
        return None
    except Exception as e:
        logger.error(f"Error validating JWT token: {e}")
        return None


# Store authenticated sessions
_authenticated_sessions: Dict[str, Dict[str, Any]] = {}


@sio.event
async def connect(sid: str, environ: Dict[str, Any], auth: Optional[Dict[str, Any]] = None):
    """
    Handle client connection events with JWT authentication.

    This event is triggered when a client establishes a WebSocket connection.
    If auth data is provided, it validates the JWT token and stores user info.

    Args:
        sid: Session ID assigned to the connected client
        environ: ASGI environment dictionary containing connection details
        auth: Optional authentication data sent by the client
            Expected format: {'token': 'jwt_token_string'}

    Returns:
        True to accept the connection, False to reject it

    Example:
        Client can send auth data when connecting:
        socket = socketio.Client()
        socket.connect('http://localhost:8000', auth={'token': 'jwt_token'})
    """
    logger.info(f"Client attempting to connect: {sid}")

    # Authentication validation
    user_info = None

    if auth:
        token = auth.get("token")
        if token:
            user_info = await _validate_jwt_token(token)

            if user_info:
                logger.info(f"Client {sid} authenticated as user {user_info.get('user_id')}")
                _authenticated_sessions[sid] = user_info
            else:
                logger.warning(f"Client {sid} provided invalid token, allowing anonymous connection")
        else:
            logger.debug(f"Client {sid} connected without token (anonymous)")
    else:
        logger.debug(f"Client {sid} connected without auth (anonymous)")

    # Accept connection (both authenticated and anonymous)
    # Some endpoints may require authentication and will check _authenticated_sessions
    return True


def get_session_user(sid: str) -> Optional[Dict[str, Any]]:
    """
    Get authenticated user info for a session.

    Args:
        sid: Session ID to look up

    Returns:
        User info dict if session is authenticated, None otherwise
    """
    return _authenticated_sessions.get(sid)


def is_session_authenticated(sid: str) -> bool:
    """
    Check if a session is authenticated.

    Args:
        sid: Session ID to check

    Returns:
        True if session has valid authentication, False otherwise
    """
    return sid in _authenticated_sessions


@sio.event
async def disconnect(sid: str):
    """
    Handle client disconnection events.

    Args:
        sid: Session ID of the disconnected client
    """
    # Clean up authenticated session
    if sid in _authenticated_sessions:
        user_info = _authenticated_sessions.pop(sid)
        logger.info(f"Authenticated client {sid} (user {user_info.get('user_id')}) disconnected")
    else:
        logger.info(f"Anonymous client {sid} disconnected")


@sio.event
async def subscribe_test_run(sid: str, data: Dict[str, Any]):
    """
    Subscribe a client to real-time updates for a specific suite run.

    When a client subscribes to a suite run, they are added to a Socket.IO room
    named after the suite run ID. All subsequent updates for that suite run will
    be emitted to clients in that room.

    Args:
        sid: Session ID of the subscribing client
        data: Dictionary containing subscription details, must include 'suite_run_id'

    Expected data format:
        {
            'suite_run_id': 'uuid-string'
        }

    Example:
        socket.emit('subscribe_test_run', {'suite_run_id': '123e4567-e89b-12d3-a456-426614174000'})
    """
    suite_run_id = data.get('suite_run_id')

    if not suite_run_id:
        logger.warning(f"Client {sid} attempted to subscribe without suite_run_id")
        await sio.emit('error', {
            'message': 'suite_run_id is required'
        }, room=sid)
        return

    # Create room name for the suite run
    room_name = f"suite_run_{suite_run_id}"

    # Add client to the room
    sio.enter_room(sid, room_name)

    logger.info(f"Client {sid} subscribed to {room_name}")

    # Confirm subscription to the client
    await sio.emit('subscribed', {
        'suite_run_id': suite_run_id,
        'room': room_name
    }, room=sid)


@sio.event
async def unsubscribe_test_run(sid: str, data: Dict[str, Any]):
    """
    Unsubscribe a client from suite run updates.

    Args:
        sid: Session ID of the client
        data: Dictionary containing 'suite_run_id'
    """
    suite_run_id = data.get('suite_run_id')

    if not suite_run_id:
        return

    room_name = f"suite_run_{suite_run_id}"
    sio.leave_room(sid, room_name)

    logger.info(f"Client {sid} unsubscribed from {room_name}")


# Helper function to emit test execution updates
async def emit_test_execution_update(suite_run_id: str, update_data: Dict[str, Any]):
    """
    Emit test execution updates to all clients subscribed to a suite run.

    This function should be called by the test execution service when there are
    updates to broadcast to subscribed clients.

    Args:
        suite_run_id: UUID of the suite run
        update_data: Dictionary containing update information

    Example:
        await emit_test_execution_update(
            suite_run_id='123e4567-e89b-12d3-a456-426614174000',
            update_data={
                'status': 'running',
                'progress': 50,
                'completed_tests': 5,
                'total_tests': 10
            }
        )
    """
    room_name = f"suite_run_{suite_run_id}"
    await sio.emit('test_run_update', update_data, room=room_name)
    logger.debug(f"Emitted update to {room_name}: {update_data}")


# Helper function to emit test case updates
async def emit_test_case_update(suite_run_id: str, test_case_data: Dict[str, Any]):
    """
    Emit individual test case execution updates.

    Args:
        suite_run_id: UUID of the suite run
        test_case_data: Dictionary containing test case execution details

    Example:
        await emit_test_case_update(
            suite_run_id='123e4567-e89b-12d3-a456-426614174000',
            test_case_data={
                'test_case_id': '456e4567-e89b-12d3-a456-426614174000',
                'name': 'Test customer login',
                'status': 'passed',
                'duration': 2.5
            }
        )
    """
    room_name = f"suite_run_{suite_run_id}"
    await sio.emit('test_case_update', test_case_data, room=room_name)
    logger.debug(f"Emitted test case update to {room_name}")


# Helper function to emit dashboard metrics updates
async def emit_dashboard_metrics_update(metrics_data: Dict[str, Any]):
    """
    Broadcast dashboard metrics updates to all connected clients.

    This should be called periodically or when significant metrics change
    to keep all dashboards in sync with real-time data.

    Args:
        metrics_data: Dictionary containing dashboard metrics

    Example:
        await emit_dashboard_metrics_update({
            'tests_executed': 1234,
            'system_health_pct': 98.5,
            'issues_detected': 12,
            'avg_response_time_ms': 245.3,
            'active_test_runs': 3
        })
    """
    await sio.emit('dashboard:metrics_update', metrics_data)
    logger.debug("Broadcast dashboard metrics update to all clients")


# Validation queue room for real-time updates
VALIDATION_QUEUE_ROOM = "validation_queue"


@sio.event
async def subscribe_validation_queue(sid: str, data: Dict[str, Any]):
    """
    Subscribe a client to validation queue updates.

    When a client subscribes, they join the validation_queue room and will
    receive real-time updates when items are claimed or completed.

    Args:
        sid: Session ID of the subscribing client
        data: Optional data (not used, but required for Socket.IO event signature)

    Example:
        socket.emit('subscribe_validation_queue', {})
    """
    await sio.enter_room(sid, VALIDATION_QUEUE_ROOM)
    logger.info(f"Client {sid} subscribed to validation queue updates")

    await sio.emit('subscribed', {
        'room': VALIDATION_QUEUE_ROOM
    }, room=sid)


@sio.event
async def validation_claimed(sid: str, data: Dict[str, Any]):
    """
    Handle validation claimed events from clients.

    When a client claims a validation item, this broadcasts to all other
    subscribers so their UIs can update in real-time.

    Args:
        sid: Session ID of the client that claimed the item
        data: Dictionary containing {'queueId': 'uuid-string'}
    """
    queue_id = data.get('queueId')
    if queue_id:
        # Broadcast to all subscribers except the sender
        await sio.emit('validation_claimed', {
            'queue_id': queue_id,
            'claimed_by_sid': sid
        }, room=VALIDATION_QUEUE_ROOM, skip_sid=sid)
        logger.info(f"Broadcast validation_claimed for {queue_id} from {sid}")


@sio.event
async def validation_completed(sid: str, data: Dict[str, Any]):
    """
    Handle validation completed events from clients.

    When a client completes a validation, this broadcasts to all other
    subscribers so their UIs can update in real-time.

    Args:
        sid: Session ID of the client that completed the validation
        data: Dictionary containing {'queueId': 'uuid-string'}
    """
    queue_id = data.get('queueId')
    if queue_id:
        await sio.emit('validation_completed', {
            'queue_id': queue_id,
            'completed_by_sid': sid
        }, room=VALIDATION_QUEUE_ROOM, skip_sid=sid)
        logger.info(f"Broadcast validation_completed for {queue_id} from {sid}")


# Helper function to emit validation queue updates
async def emit_validation_queue_update(queue_data: Dict[str, Any]):
    """
    Broadcast validation queue updates to all connected clients.

    Args:
        queue_data: Dictionary containing validation queue information

    Example:
        await emit_validation_queue_update({
            'pending_count': 15,
            'in_progress_count': 5,
            'completed_today': 42
        })
    """
    await sio.emit('validation:queue_update', queue_data)
    logger.debug("Broadcast validation queue update to all clients")


# Helper function to emit validation claimed event (can be called from API routes)
async def emit_validation_claimed(queue_id: str):
    """
    Emit validation claimed event to all subscribed clients.

    This can be called from the claim validation API endpoint to notify
    all connected clients that an item has been claimed.

    Args:
        queue_id: UUID of the claimed validation queue item
    """
    await sio.emit('validation_claimed', {
        'queue_id': queue_id
    }, room=VALIDATION_QUEUE_ROOM)
    logger.info(f"Emitted validation_claimed for {queue_id} to {VALIDATION_QUEUE_ROOM}")
