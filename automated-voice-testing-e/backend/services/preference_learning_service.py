"""
Preference Learning Service for voice AI testing.

This service provides preference learning and personalization
for voice AI systems based on user behavior patterns.

Key features:
- Frequently used commands tracking
- Preferred POI categories
- Music taste learning
- Climate preferences
- Route preferences

Example:
    >>> service = PreferenceLearningService()
    >>> service.track_command_usage(profile_id='prof_123', command='navigate home')
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import Counter
import uuid


class PreferenceLearningService:
    """
    Service for preference learning and personalization.

    Provides tools for tracking user behavior and learning
    preferences over time for better personalization.

    Example:
        >>> service = PreferenceLearningService()
        >>> config = service.get_learning_config()
    """

    def __init__(self):
        """Initialize the preference learning service."""
        self._command_history: Dict[str, List[Dict[str, Any]]] = {}
        self._poi_visits: Dict[str, List[Dict[str, Any]]] = {}
        self._music_history: Dict[str, List[Dict[str, Any]]] = {}
        self._climate_settings: Dict[str, List[Dict[str, Any]]] = {}
        self._route_choices: Dict[str, List[Dict[str, Any]]] = {}

    def track_command_usage(
        self,
        profile_id: str,
        command: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Track a command usage for learning.

        Args:
            profile_id: Profile identifier
            command: Command used
            context: Optional context data

        Returns:
            Dictionary with tracking result

        Example:
            >>> result = service.track_command_usage('prof_123', 'play music')
        """
        tracking_id = str(uuid.uuid4())

        if profile_id not in self._command_history:
            self._command_history[profile_id] = []

        usage = {
            'tracking_id': tracking_id,
            'command': command,
            'context': context or {},
            'tracked_at': datetime.utcnow().isoformat()
        }

        self._command_history[profile_id].append(usage)

        return {
            'tracking_id': tracking_id,
            'profile_id': profile_id,
            'command': command,
            'total_tracked': len(self._command_history[profile_id]),
            'success': True,
            'tracked_at': usage['tracked_at']
        }

    def get_frequent_commands(
        self,
        profile_id: str,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Get frequently used commands for a profile.

        Args:
            profile_id: Profile identifier
            limit: Maximum commands to return

        Returns:
            Dictionary with frequent commands

        Example:
            >>> commands = service.get_frequent_commands('prof_123')
        """
        query_id = str(uuid.uuid4())

        if profile_id not in self._command_history:
            return {
                'query_id': query_id,
                'profile_id': profile_id,
                'commands': [],
                'total_commands': 0,
                'queried_at': datetime.utcnow().isoformat()
            }

        history = self._command_history[profile_id]
        command_counts = Counter(item['command'] for item in history)
        frequent = command_counts.most_common(limit)

        commands = [
            {'command': cmd, 'count': count, 'rank': i + 1}
            for i, (cmd, count) in enumerate(frequent)
        ]

        return {
            'query_id': query_id,
            'profile_id': profile_id,
            'commands': commands,
            'total_commands': len(history),
            'queried_at': datetime.utcnow().isoformat()
        }

    def suggest_commands(
        self,
        profile_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Suggest commands based on learned preferences.

        Args:
            profile_id: Profile identifier
            context: Current context

        Returns:
            Dictionary with suggestions

        Example:
            >>> suggestions = service.suggest_commands('prof_123')
        """
        suggestion_id = str(uuid.uuid4())

        frequent = self.get_frequent_commands(profile_id, limit=5)
        suggestions = [
            {
                'command': cmd['command'],
                'confidence': min(0.9, cmd['count'] / 10),
                'reason': 'frequently_used'
            }
            for cmd in frequent.get('commands', [])
        ]

        return {
            'suggestion_id': suggestion_id,
            'profile_id': profile_id,
            'suggestions': suggestions,
            'context_used': context is not None,
            'suggested_at': datetime.utcnow().isoformat()
        }

    def track_poi_visit(
        self,
        profile_id: str,
        category: str,
        poi_name: str,
        location: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Track a POI visit for learning preferences.

        Args:
            profile_id: Profile identifier
            category: POI category
            poi_name: POI name
            location: Optional location

        Returns:
            Dictionary with tracking result

        Example:
            >>> result = service.track_poi_visit('prof_123', 'restaurant', 'Olive Garden')
        """
        tracking_id = str(uuid.uuid4())

        if profile_id not in self._poi_visits:
            self._poi_visits[profile_id] = []

        visit = {
            'tracking_id': tracking_id,
            'category': category,
            'poi_name': poi_name,
            'location': location,
            'visited_at': datetime.utcnow().isoformat()
        }

        self._poi_visits[profile_id].append(visit)

        return {
            'tracking_id': tracking_id,
            'profile_id': profile_id,
            'category': category,
            'poi_name': poi_name,
            'success': True,
            'tracked_at': visit['visited_at']
        }

    def get_preferred_poi_categories(
        self,
        profile_id: str,
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        Get preferred POI categories for a profile.

        Args:
            profile_id: Profile identifier
            limit: Maximum categories to return

        Returns:
            Dictionary with preferred categories

        Example:
            >>> categories = service.get_preferred_poi_categories('prof_123')
        """
        query_id = str(uuid.uuid4())

        if profile_id not in self._poi_visits:
            return {
                'query_id': query_id,
                'profile_id': profile_id,
                'categories': [],
                'total_visits': 0,
                'queried_at': datetime.utcnow().isoformat()
            }

        visits = self._poi_visits[profile_id]
        category_counts = Counter(visit['category'] for visit in visits)
        preferred = category_counts.most_common(limit)

        categories = [
            {'category': cat, 'visits': count, 'rank': i + 1}
            for i, (cat, count) in enumerate(preferred)
        ]

        return {
            'query_id': query_id,
            'profile_id': profile_id,
            'categories': categories,
            'total_visits': len(visits),
            'queried_at': datetime.utcnow().isoformat()
        }

    def track_music_preference(
        self,
        profile_id: str,
        genre: str,
        artist: Optional[str] = None,
        action: str = 'play'
    ) -> Dict[str, Any]:
        """
        Track music preference for learning.

        Args:
            profile_id: Profile identifier
            genre: Music genre
            artist: Optional artist name
            action: User action (play, skip, like)

        Returns:
            Dictionary with tracking result

        Example:
            >>> result = service.track_music_preference('prof_123', 'rock', 'AC/DC')
        """
        tracking_id = str(uuid.uuid4())

        if profile_id not in self._music_history:
            self._music_history[profile_id] = []

        preference = {
            'tracking_id': tracking_id,
            'genre': genre,
            'artist': artist,
            'action': action,
            'tracked_at': datetime.utcnow().isoformat()
        }

        self._music_history[profile_id].append(preference)

        return {
            'tracking_id': tracking_id,
            'profile_id': profile_id,
            'genre': genre,
            'artist': artist,
            'action': action,
            'success': True,
            'tracked_at': preference['tracked_at']
        }

    def get_music_preferences(
        self,
        profile_id: str
    ) -> Dict[str, Any]:
        """
        Get learned music preferences.

        Args:
            profile_id: Profile identifier

        Returns:
            Dictionary with music preferences

        Example:
            >>> prefs = service.get_music_preferences('prof_123')
        """
        query_id = str(uuid.uuid4())

        if profile_id not in self._music_history:
            return {
                'query_id': query_id,
                'profile_id': profile_id,
                'genres': [],
                'artists': [],
                'total_tracks': 0,
                'queried_at': datetime.utcnow().isoformat()
            }

        history = self._music_history[profile_id]

        # Get genre preferences
        genre_counts = Counter(item['genre'] for item in history)
        genres = [
            {'genre': g, 'count': c}
            for g, c in genre_counts.most_common(5)
        ]

        # Get artist preferences
        artist_counts = Counter(
            item['artist'] for item in history if item['artist']
        )
        artists = [
            {'artist': a, 'count': c}
            for a, c in artist_counts.most_common(5)
        ]

        return {
            'query_id': query_id,
            'profile_id': profile_id,
            'genres': genres,
            'artists': artists,
            'total_tracks': len(history),
            'queried_at': datetime.utcnow().isoformat()
        }

    def track_climate_setting(
        self,
        profile_id: str,
        temperature: float,
        fan_speed: str = 'auto',
        conditions: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Track climate control setting for learning.

        Args:
            profile_id: Profile identifier
            temperature: Temperature setting
            fan_speed: Fan speed setting
            conditions: External conditions

        Returns:
            Dictionary with tracking result

        Example:
            >>> result = service.track_climate_setting('prof_123', 72.0, 'medium')
        """
        tracking_id = str(uuid.uuid4())

        if profile_id not in self._climate_settings:
            self._climate_settings[profile_id] = []

        setting = {
            'tracking_id': tracking_id,
            'temperature': temperature,
            'fan_speed': fan_speed,
            'conditions': conditions or {},
            'tracked_at': datetime.utcnow().isoformat()
        }

        self._climate_settings[profile_id].append(setting)

        return {
            'tracking_id': tracking_id,
            'profile_id': profile_id,
            'temperature': temperature,
            'fan_speed': fan_speed,
            'success': True,
            'tracked_at': setting['tracked_at']
        }

    def get_climate_preferences(
        self,
        profile_id: str
    ) -> Dict[str, Any]:
        """
        Get learned climate preferences.

        Args:
            profile_id: Profile identifier

        Returns:
            Dictionary with climate preferences

        Example:
            >>> prefs = service.get_climate_preferences('prof_123')
        """
        query_id = str(uuid.uuid4())

        if profile_id not in self._climate_settings:
            return {
                'query_id': query_id,
                'profile_id': profile_id,
                'avg_temperature': None,
                'preferred_fan_speed': None,
                'total_settings': 0,
                'queried_at': datetime.utcnow().isoformat()
            }

        settings = self._climate_settings[profile_id]

        # Calculate averages
        temps = [s['temperature'] for s in settings]
        avg_temp = sum(temps) / len(temps)

        fan_counts = Counter(s['fan_speed'] for s in settings)
        preferred_fan = fan_counts.most_common(1)[0][0] if fan_counts else 'auto'

        return {
            'query_id': query_id,
            'profile_id': profile_id,
            'avg_temperature': round(avg_temp, 1),
            'preferred_fan_speed': preferred_fan,
            'total_settings': len(settings),
            'queried_at': datetime.utcnow().isoformat()
        }

    def track_route_choice(
        self,
        profile_id: str,
        route_type: str,
        factors: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Track route choice for learning preferences.

        Args:
            profile_id: Profile identifier
            route_type: Type of route chosen
            factors: Factors that influenced choice

        Returns:
            Dictionary with tracking result

        Example:
            >>> result = service.track_route_choice('prof_123', 'fastest')
        """
        tracking_id = str(uuid.uuid4())

        if profile_id not in self._route_choices:
            self._route_choices[profile_id] = []

        choice = {
            'tracking_id': tracking_id,
            'route_type': route_type,
            'factors': factors or [],
            'tracked_at': datetime.utcnow().isoformat()
        }

        self._route_choices[profile_id].append(choice)

        return {
            'tracking_id': tracking_id,
            'profile_id': profile_id,
            'route_type': route_type,
            'success': True,
            'tracked_at': choice['tracked_at']
        }

    def get_route_preferences(
        self,
        profile_id: str
    ) -> Dict[str, Any]:
        """
        Get learned route preferences.

        Args:
            profile_id: Profile identifier

        Returns:
            Dictionary with route preferences

        Example:
            >>> prefs = service.get_route_preferences('prof_123')
        """
        query_id = str(uuid.uuid4())

        if profile_id not in self._route_choices:
            return {
                'query_id': query_id,
                'profile_id': profile_id,
                'preferred_route_type': None,
                'common_factors': [],
                'total_choices': 0,
                'queried_at': datetime.utcnow().isoformat()
            }

        choices = self._route_choices[profile_id]

        # Get preferred route type
        type_counts = Counter(c['route_type'] for c in choices)
        preferred = type_counts.most_common(1)[0][0] if type_counts else None

        # Get common factors
        all_factors = []
        for c in choices:
            all_factors.extend(c.get('factors', []))
        factor_counts = Counter(all_factors)
        common_factors = [f for f, _ in factor_counts.most_common(3)]

        return {
            'query_id': query_id,
            'profile_id': profile_id,
            'preferred_route_type': preferred,
            'common_factors': common_factors,
            'total_choices': len(choices),
            'queried_at': datetime.utcnow().isoformat()
        }

    def get_learning_config(self) -> Dict[str, Any]:
        """
        Get preference learning configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_learning_config()
        """
        return {
            'profiles_tracked': len(set(
                list(self._command_history.keys()) +
                list(self._poi_visits.keys()) +
                list(self._music_history.keys()) +
                list(self._climate_settings.keys()) +
                list(self._route_choices.keys())
            )),
            'total_command_events': sum(len(v) for v in self._command_history.values()),
            'total_poi_events': sum(len(v) for v in self._poi_visits.values()),
            'total_music_events': sum(len(v) for v in self._music_history.values()),
            'total_climate_events': sum(len(v) for v in self._climate_settings.values()),
            'total_route_events': sum(len(v) for v in self._route_choices.values()),
            'features': [
                'command_tracking', 'poi_preferences',
                'music_learning', 'climate_preferences',
                'route_preferences', 'suggestions'
            ]
        }
