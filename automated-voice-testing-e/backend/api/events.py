"""
Event Emitter Utilities for Real-time WebSocket Communication

This module provides utility functions for emitting real-time events to clients
via Socket.IO. These functions are used throughout the application to broadcast
updates about suite runs, test executions, and validations.

All events are emitted to specific rooms based on resource IDs, allowing clients
to subscribe only to updates for resources they're interested in.
"""

from uuid import UUID
from typing import Dict, Any
import logging
from api.websocket import sio

logger = logging.getLogger(__name__)


async def emit_suite_run_update(suite_run_id: UUID, data: Dict[str, Any]) -> None:
    """
    Emit a suite run update event to all subscribed clients.

    This function broadcasts updates about a suite run to all clients that have
    subscribed to the specific suite run room. It's used to send progress updates,
    status changes, and completion notifications.

    Args:
        suite_run_id: UUID of the suite run to emit updates for
        data: Dictionary containing update information. Common fields include:
            - status: Current status (queued, running, completed, failed)
            - progress: Percentage completion (0-100)
            - completed_tests: Number of tests completed
            - total_tests: Total number of tests
            - passed_tests: Number of passed tests
            - failed_tests: Number of failed tests
            - started_at: Suite run start timestamp
            - completed_at: Suite run completion timestamp

    Example:
        await emit_suite_run_update(
            suite_run_id=UUID('123e4567-e89b-12d3-a456-426614174000'),
            data={
                'status': 'running',
                'progress': 45,
                'completed_tests': 9,
                'total_tests': 20,
                'passed_tests': 7,
                'failed_tests': 2
            }
        )
    """
    room_name = f"suite_run_{suite_run_id}"

    # Add suite_run_id to data for client reference
    event_data = {
        'suite_run_id': str(suite_run_id),
        **data
    }

    try:
        await sio.emit('suite_run_update', event_data, room=room_name)
        logger.debug(f"Emitted suite_run_update to {room_name}: {event_data}")
    except Exception as e:
        logger.error(f"Failed to emit suite_run_update to {room_name}: {e}")


# Backward compatibility alias
async def emit_test_run_update(test_run_id: UUID, data: Dict[str, Any]) -> None:
    """Deprecated: Use emit_suite_run_update instead."""
    await emit_suite_run_update(test_run_id, data)


async def emit_test_completed(test_execution_id: UUID, data: Dict[str, Any]) -> None:
    """
    Emit a test execution completion event to subscribed clients.

    This function broadcasts when an individual test execution completes. It's used
    to provide real-time feedback about each test case as it finishes, including
    pass/fail status, duration, and any errors.

    Args:
        test_execution_id: UUID of the test execution that completed
        data: Dictionary containing test execution results. Common fields include:
            - test_case_id: UUID of the test case
            - suite_run_id: UUID of the parent suite run
            - status: Execution status (passed, failed, skipped, error)
            - duration: Execution time in seconds
            - error_message: Error message if failed
            - expected_result: Expected outcome
            - actual_result: Actual outcome
            - similarity_score: Validation similarity score
            - completed_at: Completion timestamp

    Example:
        await emit_test_completed(
            test_execution_id=UUID('456e4567-e89b-12d3-a456-426614174000'),
            data={
                'test_case_id': '789e4567-e89b-12d3-a456-426614174000',
                'suite_run_id': '123e4567-e89b-12d3-a456-426614174000',
                'status': 'passed',
                'duration': 2.5,
                'similarity_score': 0.95
            }
        )
    """
    # Determine which room to emit to (typically the suite run room)
    suite_run_id = data.get('suite_run_id')
    if suite_run_id:
        room_name = f"suite_run_{suite_run_id}"
    else:
        logger.warning(f"No suite_run_id provided for test_execution {test_execution_id}")
        return

    # Add test_execution_id to data for client reference
    event_data = {
        'test_execution_id': str(test_execution_id),
        **data
    }

    try:
        await sio.emit('test_completed', event_data, room=room_name)
        logger.debug(f"Emitted test_completed to {room_name}: {event_data}")
    except Exception as e:
        logger.error(f"Failed to emit test_completed to {room_name}: {e}")


async def emit_validation_update(validation_id: UUID, data: Dict[str, Any]) -> None:
    """
    Emit a validation update event to subscribed clients.

    This function broadcasts updates about validation tasks (human-in-the-loop reviews)
    to subscribed clients. It's used to notify about validation assignments, status
    changes, and completion.

    Args:
        validation_id: UUID of the validation task
        data: Dictionary containing validation information. Common fields include:
            - test_execution_id: UUID of the related test execution
            - suite_run_id: UUID of the related suite run
            - status: Validation status (pending, in_review, approved, rejected)
            - validator_id: UUID of the assigned validator
            - validation_result: Human review decision
            - notes: Validator notes/comments
            - created_at: Validation creation timestamp
            - completed_at: Validation completion timestamp

    Example:
        await emit_validation_update(
            validation_id=UUID('321e4567-e89b-12d3-a456-426614174000'),
            data={
                'test_execution_id': '456e4567-e89b-12d3-a456-426614174000',
                'suite_run_id': '123e4567-e89b-12d3-a456-426614174000',
                'status': 'approved',
                'validator_id': '999e4567-e89b-12d3-a456-426614174000',
                'validation_result': 'pass',
                'notes': 'Response is semantically correct'
            }
        )
    """
    # Emit to suite run room if available
    suite_run_id = data.get('suite_run_id')
    if suite_run_id:
        room_name = f"suite_run_{suite_run_id}"
    else:
        # Fall back to validation-specific room
        room_name = f"validation_{validation_id}"
        logger.debug(f"No suite_run_id provided, using validation room: {room_name}")

    # Add validation_id to data for client reference
    event_data = {
        'validation_id': str(validation_id),
        **data
    }

    try:
        await sio.emit('validation_update', event_data, room=room_name)
        logger.debug(f"Emitted validation_update to {room_name}: {event_data}")
    except Exception as e:
        logger.error(f"Failed to emit validation_update to {room_name}: {e}")


# Additional utility functions for broadcasting to multiple rooms

async def emit_to_room(room: str, event: str, data: Dict[str, Any]) -> None:
    """
    Generic utility to emit an event to a specific room.

    Args:
        room: Room name to emit to
        event: Event name
        data: Event data payload
    """
    try:
        await sio.emit(event, data, room=room)
        logger.debug(f"Emitted {event} to {room}")
    except Exception as e:
        logger.error(f"Failed to emit {event} to {room}: {e}")


async def emit_to_all(event: str, data: Dict[str, Any]) -> None:
    """
    Broadcast an event to all connected clients.

    Use sparingly as this sends to every connected client.

    Args:
        event: Event name
        data: Event data payload
    """
    try:
        await sio.emit(event, data)
        logger.debug(f"Broadcasted {event} to all clients")
    except Exception as e:
        logger.error(f"Failed to broadcast {event}: {e}")
