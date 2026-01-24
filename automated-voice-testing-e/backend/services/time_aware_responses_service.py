"""
Time-aware Responses Service for voice AI testing.

This service provides time-aware response testing for
automotive voice AI systems with contextual time awareness.

Key features:
- Morning/evening greetings
- Business hours awareness
- Time-based suggestions
- Contextual reminders

Example:
    >>> service = TimeAwareResponsesService()
    >>> greeting = service.get_time_greeting()
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, time
import uuid


class TimeAwareResponsesService:
    """
    Service for time-aware response testing.

    Provides automotive voice AI testing for time-based
    responses and contextual awareness.

    Example:
        >>> service = TimeAwareResponsesService()
        >>> config = service.get_time_aware_config()
    """

    def __init__(self):
        """Initialize the time-aware responses service."""
        self._business_hours = {
            'open': time(9, 0),
            'close': time(17, 0)
        }
        self._time_periods = {
            'morning': (5, 12),
            'afternoon': (12, 17),
            'evening': (17, 21),
            'night': (21, 5)
        }

    def get_time_greeting(
        self,
        current_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get appropriate greeting for current time.

        Args:
            current_time: Time to get greeting for (defaults to now)

        Returns:
            Dictionary with greeting information

        Example:
            >>> greeting = service.get_time_greeting()
        """
        greeting_id = str(uuid.uuid4())

        if current_time is None:
            current_time = datetime.utcnow()

        hour = current_time.hour
        time_of_day = self._get_time_period(hour)

        greetings = {
            'morning': 'Good morning',
            'afternoon': 'Good afternoon',
            'evening': 'Good evening',
            'night': 'Hello'
        }

        return {
            'greeting_id': greeting_id,
            'greeting': greetings.get(time_of_day, 'Hello'),
            'time_of_day': time_of_day,
            'hour': hour,
            'generated_at': datetime.utcnow().isoformat()
        }

    def get_time_of_day(
        self,
        current_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get current time of day period.

        Args:
            current_time: Time to evaluate (defaults to now)

        Returns:
            Dictionary with time period information

        Example:
            >>> period = service.get_time_of_day()
        """
        period_id = str(uuid.uuid4())

        if current_time is None:
            current_time = datetime.utcnow()

        hour = current_time.hour
        time_period = self._get_time_period(hour)

        return {
            'period_id': period_id,
            'time_period': time_period,
            'hour': hour,
            'is_daytime': 6 <= hour < 20,
            'evaluated_at': datetime.utcnow().isoformat()
        }

    def _get_time_period(self, hour: int) -> str:
        """Get time period name for hour."""
        if 5 <= hour < 12:
            return 'morning'
        elif 12 <= hour < 17:
            return 'afternoon'
        elif 17 <= hour < 21:
            return 'evening'
        else:
            return 'night'

    def check_business_hours(
        self,
        check_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Check if within business hours.

        Args:
            check_time: Time to check (defaults to now)

        Returns:
            Dictionary with business hours status

        Example:
            >>> status = service.check_business_hours()
        """
        check_id = str(uuid.uuid4())

        if check_time is None:
            check_time = datetime.utcnow()

        current_time_obj = check_time.time()
        is_open = (
            self._business_hours['open'] <= current_time_obj
            <= self._business_hours['close']
        )

        # Check if weekday (Monday = 0, Sunday = 6)
        is_weekday = check_time.weekday() < 5
        is_business_hours = is_open and is_weekday

        return {
            'check_id': check_id,
            'is_open': is_business_hours,
            'is_weekday': is_weekday,
            'current_time': current_time_obj.isoformat(),
            'business_open': self._business_hours['open'].isoformat(),
            'business_close': self._business_hours['close'].isoformat(),
            'checked_at': datetime.utcnow().isoformat()
        }

    def get_next_open_time(
        self,
        from_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get next business opening time.

        Args:
            from_time: Time to calculate from (defaults to now)

        Returns:
            Dictionary with next open time information

        Example:
            >>> next_open = service.get_next_open_time()
        """
        next_id = str(uuid.uuid4())

        if from_time is None:
            from_time = datetime.utcnow()

        # Calculate next open time
        next_open = datetime.combine(
            from_time.date(),
            self._business_hours['open']
        )

        # If already past today's opening, move to next day
        if from_time.time() >= self._business_hours['open']:
            from datetime import timedelta
            next_open = next_open + timedelta(days=1)

        # Skip weekends
        while next_open.weekday() >= 5:
            from datetime import timedelta
            next_open = next_open + timedelta(days=1)

        return {
            'next_id': next_id,
            'next_open_time': next_open.isoformat(),
            'from_time': from_time.isoformat(),
            'hours_until': round(
                (next_open - from_time).total_seconds() / 3600, 1
            ),
            'calculated_at': datetime.utcnow().isoformat()
        }

    def get_time_based_suggestions(
        self,
        current_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get suggestions based on current time.

        Args:
            current_time: Time to base suggestions on (defaults to now)

        Returns:
            Dictionary with time-based suggestions

        Example:
            >>> suggestions = service.get_time_based_suggestions()
        """
        suggestion_id = str(uuid.uuid4())

        if current_time is None:
            current_time = datetime.utcnow()

        hour = current_time.hour
        time_period = self._get_time_period(hour)

        suggestions_map: Dict[str, List[str]] = {
            'morning': [
                'Check traffic for commute',
                'Review calendar for today',
                'Listen to morning news'
            ],
            'afternoon': [
                'Find nearby lunch options',
                'Check afternoon appointments',
                'Review pending tasks'
            ],
            'evening': [
                'Navigate home',
                'Call family',
                'Review tomorrow\'s schedule'
            ],
            'night': [
                'Set morning alarm',
                'Enable do not disturb',
                'Check weather for tomorrow'
            ]
        }

        return {
            'suggestion_id': suggestion_id,
            'time_period': time_period,
            'suggestions': suggestions_map.get(time_period, []),
            'suggestion_count': len(suggestions_map.get(time_period, [])),
            'generated_at': datetime.utcnow().isoformat()
        }

    def get_contextual_reminders(
        self,
        current_time: Optional[datetime] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get contextual reminders based on time and context.

        Args:
            current_time: Current time (defaults to now)
            context: Additional context information

        Returns:
            Dictionary with contextual reminders

        Example:
            >>> reminders = service.get_contextual_reminders()
        """
        reminder_id = str(uuid.uuid4())

        if current_time is None:
            current_time = datetime.utcnow()

        if context is None:
            context = {}

        hour = current_time.hour
        reminders: List[Dict[str, Any]] = []

        # Morning commute reminder
        if 7 <= hour <= 9:
            reminders.append({
                'type': 'commute',
                'message': 'Time for morning commute',
                'priority': 'high'
            })

        # Lunch reminder
        if 11 <= hour <= 13:
            reminders.append({
                'type': 'meal',
                'message': 'Consider lunch break',
                'priority': 'medium'
            })

        # Evening commute reminder
        if 16 <= hour <= 18:
            reminders.append({
                'type': 'commute',
                'message': 'Evening commute time',
                'priority': 'high'
            })

        # End of business day
        if hour == 17:
            reminders.append({
                'type': 'business',
                'message': 'Business hours ending soon',
                'priority': 'medium'
            })

        return {
            'reminder_id': reminder_id,
            'reminders': reminders,
            'reminder_count': len(reminders),
            'hour': hour,
            'context_used': bool(context),
            'generated_at': datetime.utcnow().isoformat()
        }

    def get_time_aware_config(self) -> Dict[str, Any]:
        """
        Get time-aware responses service configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_time_aware_config()
        """
        return {
            'business_hours': {
                'open': self._business_hours['open'].isoformat(),
                'close': self._business_hours['close'].isoformat()
            },
            'time_periods': self._time_periods,
            'features': [
                'time_greetings', 'business_hours',
                'time_suggestions', 'contextual_reminders'
            ]
        }
