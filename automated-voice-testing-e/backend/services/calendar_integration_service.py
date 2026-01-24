"""
Calendar and Schedule Integration Service for voice AI testing.

This service provides calendar integration testing for
automotive voice AI systems with schedule awareness.

Key features:
- Next appointment navigation
- Meeting reminders
- Schedule conflicts
- Participant contact info

Example:
    >>> service = CalendarIntegrationService()
    >>> appointment = service.get_next_appointment()
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import uuid


class CalendarIntegrationService:
    """
    Service for calendar and schedule integration testing.

    Provides automotive voice AI testing for calendar-based
    responses and schedule awareness.

    Example:
        >>> service = CalendarIntegrationService()
        >>> config = service.get_calendar_integration_config()
    """

    def __init__(self):
        """Initialize the calendar integration service."""
        self._appointments: List[Dict[str, Any]] = []
        self._reminders: List[Dict[str, Any]] = []

    def get_next_appointment(
        self,
        from_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get next scheduled appointment.

        Args:
            from_time: Time to search from (defaults to now)

        Returns:
            Dictionary with appointment information

        Example:
            >>> appointment = service.get_next_appointment()
        """
        query_id = str(uuid.uuid4())

        if from_time is None:
            from_time = datetime.utcnow()

        # Find next appointment
        next_appointment = None
        for apt in self._appointments:
            apt_time = apt.get('start_time')
            if apt_time and apt_time > from_time:
                if next_appointment is None or apt_time < next_appointment.get('start_time'):
                    next_appointment = apt

        if next_appointment:
            time_until = (next_appointment['start_time'] - from_time).total_seconds() / 60
            return {
                'query_id': query_id,
                'appointment': next_appointment,
                'found': True,
                'minutes_until': round(time_until, 1),
                'retrieved_at': datetime.utcnow().isoformat()
            }

        return {
            'query_id': query_id,
            'appointment': None,
            'found': False,
            'minutes_until': None,
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def navigate_to_appointment(
        self,
        appointment_id: str
    ) -> Dict[str, Any]:
        """
        Start navigation to appointment location.

        Args:
            appointment_id: ID of appointment to navigate to

        Returns:
            Dictionary with navigation information

        Example:
            >>> nav = service.navigate_to_appointment('apt-123')
        """
        nav_id = str(uuid.uuid4())

        # Find appointment
        appointment = None
        for apt in self._appointments:
            if apt.get('appointment_id') == appointment_id:
                appointment = apt
                break

        if not appointment:
            return {
                'nav_id': nav_id,
                'success': False,
                'error': 'Appointment not found',
                'started_at': datetime.utcnow().isoformat()
            }

        location = appointment.get('location', {})

        return {
            'nav_id': nav_id,
            'success': True,
            'appointment_id': appointment_id,
            'destination': location.get('name', 'Unknown'),
            'address': location.get('address', ''),
            'coordinates': location.get('coordinates'),
            'started_at': datetime.utcnow().isoformat()
        }

    def get_meeting_reminders(
        self,
        hours_ahead: int = 24
    ) -> Dict[str, Any]:
        """
        Get upcoming meeting reminders.

        Args:
            hours_ahead: Hours to look ahead

        Returns:
            Dictionary with reminder information

        Example:
            >>> reminders = service.get_meeting_reminders(2)
        """
        reminder_id = str(uuid.uuid4())

        now = datetime.utcnow()
        end_time = now + timedelta(hours=hours_ahead)

        upcoming: List[Dict[str, Any]] = []
        for apt in self._appointments:
            apt_time = apt.get('start_time')
            if apt_time and now <= apt_time <= end_time:
                upcoming.append({
                    'appointment_id': apt.get('appointment_id'),
                    'title': apt.get('title'),
                    'start_time': apt_time.isoformat(),
                    'minutes_until': round((apt_time - now).total_seconds() / 60, 1)
                })

        return {
            'reminder_id': reminder_id,
            'reminders': upcoming,
            'reminder_count': len(upcoming),
            'hours_ahead': hours_ahead,
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def set_reminder(
        self,
        appointment_id: str,
        minutes_before: int = 15
    ) -> Dict[str, Any]:
        """
        Set reminder for appointment.

        Args:
            appointment_id: Appointment to set reminder for
            minutes_before: Minutes before to remind

        Returns:
            Dictionary with reminder creation result

        Example:
            >>> result = service.set_reminder('apt-123', 30)
        """
        set_id = str(uuid.uuid4())

        reminder = {
            'reminder_id': set_id,
            'appointment_id': appointment_id,
            'minutes_before': minutes_before,
            'created_at': datetime.utcnow().isoformat()
        }
        self._reminders.append(reminder)

        return {
            'set_id': set_id,
            'success': True,
            'appointment_id': appointment_id,
            'minutes_before': minutes_before,
            'created_at': datetime.utcnow().isoformat()
        }

    def check_schedule_conflicts(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """
        Check for schedule conflicts in time range.

        Args:
            start_time: Start of time range
            end_time: End of time range

        Returns:
            Dictionary with conflict information

        Example:
            >>> conflicts = service.check_schedule_conflicts(start, end)
        """
        check_id = str(uuid.uuid4())

        conflicts: List[Dict[str, Any]] = []
        for apt in self._appointments:
            apt_start = apt.get('start_time')
            apt_end = apt.get('end_time')

            if apt_start and apt_end:
                # Check for overlap
                if apt_start < end_time and apt_end > start_time:
                    conflicts.append({
                        'appointment_id': apt.get('appointment_id'),
                        'title': apt.get('title'),
                        'start_time': apt_start.isoformat(),
                        'end_time': apt_end.isoformat()
                    })

        return {
            'check_id': check_id,
            'has_conflicts': len(conflicts) > 0,
            'conflicts': conflicts,
            'conflict_count': len(conflicts),
            'checked_at': datetime.utcnow().isoformat()
        }

    def get_available_slots(
        self,
        date: datetime,
        duration_minutes: int = 60
    ) -> Dict[str, Any]:
        """
        Get available time slots on date.

        Args:
            date: Date to check
            duration_minutes: Required slot duration

        Returns:
            Dictionary with available slots

        Example:
            >>> slots = service.get_available_slots(date, 30)
        """
        slots_id = str(uuid.uuid4())

        # Simple slot calculation (9 AM to 5 PM)
        business_start = 9
        business_end = 17
        slots: List[Dict[str, str]] = []

        # Generate hourly slots as example
        for hour in range(business_start, business_end):
            slot_start = date.replace(hour=hour, minute=0, second=0)
            slot_end = slot_start + timedelta(minutes=duration_minutes)

            # Check if slot conflicts
            is_free = True
            for apt in self._appointments:
                apt_start = apt.get('start_time')
                apt_end = apt.get('end_time')
                if apt_start and apt_end:
                    if apt_start < slot_end and apt_end > slot_start:
                        is_free = False
                        break

            if is_free:
                slots.append({
                    'start': slot_start.isoformat(),
                    'end': slot_end.isoformat()
                })

        return {
            'slots_id': slots_id,
            'date': date.date().isoformat(),
            'duration_minutes': duration_minutes,
            'available_slots': slots,
            'slot_count': len(slots),
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def get_participant_info(
        self,
        appointment_id: str
    ) -> Dict[str, Any]:
        """
        Get participant information for appointment.

        Args:
            appointment_id: Appointment ID

        Returns:
            Dictionary with participant information

        Example:
            >>> participants = service.get_participant_info('apt-123')
        """
        info_id = str(uuid.uuid4())

        # Find appointment
        appointment = None
        for apt in self._appointments:
            if apt.get('appointment_id') == appointment_id:
                appointment = apt
                break

        if not appointment:
            return {
                'info_id': info_id,
                'found': False,
                'participants': [],
                'retrieved_at': datetime.utcnow().isoformat()
            }

        participants = appointment.get('participants', [])

        return {
            'info_id': info_id,
            'found': True,
            'appointment_id': appointment_id,
            'participants': participants,
            'participant_count': len(participants),
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def call_participant(
        self,
        appointment_id: str,
        participant_index: int = 0
    ) -> Dict[str, Any]:
        """
        Initiate call to meeting participant.

        Args:
            appointment_id: Appointment ID
            participant_index: Index of participant to call

        Returns:
            Dictionary with call initiation result

        Example:
            >>> call = service.call_participant('apt-123', 0)
        """
        call_id = str(uuid.uuid4())

        # Find appointment
        appointment = None
        for apt in self._appointments:
            if apt.get('appointment_id') == appointment_id:
                appointment = apt
                break

        if not appointment:
            return {
                'call_id': call_id,
                'success': False,
                'error': 'Appointment not found',
                'initiated_at': datetime.utcnow().isoformat()
            }

        participants = appointment.get('participants', [])
        if participant_index >= len(participants):
            return {
                'call_id': call_id,
                'success': False,
                'error': 'Participant not found',
                'initiated_at': datetime.utcnow().isoformat()
            }

        participant = participants[participant_index]

        return {
            'call_id': call_id,
            'success': True,
            'participant': participant.get('name'),
            'phone': participant.get('phone'),
            'initiated_at': datetime.utcnow().isoformat()
        }

    def add_appointment(
        self,
        title: str,
        start_time: datetime,
        end_time: datetime,
        location: Optional[Dict[str, Any]] = None,
        participants: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Add appointment to calendar.

        Args:
            title: Appointment title
            start_time: Start time
            end_time: End time
            location: Location information
            participants: List of participants

        Returns:
            Dictionary with creation result

        Example:
            >>> apt = service.add_appointment('Meeting', start, end)
        """
        appointment_id = str(uuid.uuid4())

        appointment = {
            'appointment_id': appointment_id,
            'title': title,
            'start_time': start_time,
            'end_time': end_time,
            'location': location or {},
            'participants': participants or []
        }
        self._appointments.append(appointment)

        return {
            'appointment_id': appointment_id,
            'success': True,
            'title': title,
            'created_at': datetime.utcnow().isoformat()
        }

    def get_calendar_integration_config(self) -> Dict[str, Any]:
        """
        Get calendar integration service configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_calendar_integration_config()
        """
        return {
            'appointment_count': len(self._appointments),
            'reminder_count': len(self._reminders),
            'features': [
                'appointment_navigation', 'meeting_reminders',
                'schedule_conflicts', 'participant_info',
                'available_slots'
            ]
        }
