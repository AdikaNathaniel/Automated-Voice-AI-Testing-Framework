"""
Houndify Constants and Mappings

This module defines constants and mappings for Houndify voice AI integration,
including CommandKind to Intent mappings for validation consistency checking.
"""

from typing import Dict, List

# ===========================================================================
# CommandKind Constants
# ===========================================================================

# Houndify CommandKind values (domain-level classification)
COMMAND_KIND_WEATHER = "WeatherCommand"
COMMAND_KIND_MUSIC = "MusicCommand"
COMMAND_KIND_NAVIGATION = "NavigationCommand"
COMMAND_KIND_PHONE = "PhoneCommand"
COMMAND_KIND_LOCAL_SEARCH = "LocalSearchCommand"
COMMAND_KIND_SPORTS = "SportsCommand"
COMMAND_KIND_NEWS = "NewsCommand"
COMMAND_KIND_STOCKS = "StocksCommand"
COMMAND_KIND_CALENDAR = "CalendarCommand"
COMMAND_KIND_ALARM = "AlarmCommand"
COMMAND_KIND_TIMER = "TimerCommand"
COMMAND_KIND_REMINDERS = "RemindersCommand"
COMMAND_KIND_MESSAGES = "MessagesCommand"
COMMAND_KIND_EMAIL = "EmailCommand"
COMMAND_KIND_CONTACTS = "ContactsCommand"
COMMAND_KIND_CONVERSATIONAL = "ConversationalCommand"
COMMAND_KIND_NO_RESULT = "NoResultCommand"
COMMAND_KIND_CUSTOM = "CustomCommand"

# ===========================================================================
# Intent Constants (action-level classification within domains)
# ===========================================================================

# Weather intents
INTENT_WEATHER_QUERY = "weather_query"
INTENT_WEATHER_FORECAST = "weather_forecast"
INTENT_WEATHER_HISTORICAL = "weather_historical"
INTENT_WEATHER_ALERT = "weather_alert"
INTENT_WEATHER_HOURLY = "weather_hourly"
INTENT_WEATHER_WEEKLY = "weather_weekly"

# Music intents
INTENT_MUSIC_PLAY = "music_play"
INTENT_MUSIC_PAUSE = "music_pause"
INTENT_MUSIC_RESUME = "music_resume"
INTENT_MUSIC_SKIP = "music_skip"
INTENT_MUSIC_PREVIOUS = "music_previous"
INTENT_MUSIC_STOP = "music_stop"
INTENT_MUSIC_SEARCH = "music_search"
INTENT_MUSIC_PLAYLIST = "music_playlist"
INTENT_MUSIC_VOLUME = "music_volume"

# Navigation intents
INTENT_NAV_NAVIGATE = "navigate_to_location"
INTENT_NAV_FIND_ROUTE = "find_route"
INTENT_NAV_CHECK_TRAFFIC = "check_traffic"
INTENT_NAV_FIND_PARKING = "find_parking"
INTENT_NAV_ETA = "get_eta"
INTENT_NAV_NEARBY = "find_nearby"

# Phone intents
INTENT_PHONE_CALL = "phone_call"
INTENT_PHONE_VOICEMAIL = "phone_voicemail"
INTENT_PHONE_CONTACT_LOOKUP = "phone_contact_lookup"

# General intents
INTENT_UNRECOGNIZED = "unrecognized"
INTENT_UNCLEAR_QUERY = "unclear_query"
INTENT_CUSTOM = "custom_command"

# ===========================================================================
# CommandKind to Intent Mappings
# ===========================================================================

COMMAND_KIND_TO_INTENTS: Dict[str, List[str]] = {
    COMMAND_KIND_WEATHER: [
        INTENT_WEATHER_QUERY,
        INTENT_WEATHER_FORECAST,
        INTENT_WEATHER_HISTORICAL,
        INTENT_WEATHER_ALERT,
        INTENT_WEATHER_HOURLY,
        INTENT_WEATHER_WEEKLY,
    ],
    COMMAND_KIND_MUSIC: [
        INTENT_MUSIC_PLAY,
        INTENT_MUSIC_PAUSE,
        INTENT_MUSIC_RESUME,
        INTENT_MUSIC_SKIP,
        INTENT_MUSIC_PREVIOUS,
        INTENT_MUSIC_STOP,
        INTENT_MUSIC_SEARCH,
        INTENT_MUSIC_PLAYLIST,
        INTENT_MUSIC_VOLUME,
    ],
    COMMAND_KIND_NAVIGATION: [
        INTENT_NAV_NAVIGATE,
        INTENT_NAV_FIND_ROUTE,
        INTENT_NAV_CHECK_TRAFFIC,
        INTENT_NAV_FIND_PARKING,
        INTENT_NAV_ETA,
        INTENT_NAV_NEARBY,
    ],
    COMMAND_KIND_PHONE: [
        INTENT_PHONE_CALL,
        INTENT_PHONE_VOICEMAIL,
        INTENT_PHONE_CONTACT_LOOKUP,
    ],
    COMMAND_KIND_NO_RESULT: [
        INTENT_UNRECOGNIZED,
        INTENT_UNCLEAR_QUERY,
    ],
    COMMAND_KIND_CUSTOM: [
        INTENT_CUSTOM,
    ],
}


# ===========================================================================
# Helper Functions
# ===========================================================================

def is_intent_valid_for_command_kind(command_kind: str, intent: str) -> bool:
    """
    Check if an intent is valid for a given CommandKind.

    Args:
        command_kind: Houndify CommandKind (e.g., "WeatherCommand")
        intent: Extracted intent (e.g., "weather_query")

    Returns:
        bool: True if intent is valid for the CommandKind, False otherwise

    Example:
        >>> is_intent_valid_for_command_kind("WeatherCommand", "weather_query")
        True
        >>> is_intent_valid_for_command_kind("WeatherCommand", "music_play")
        False
    """
    if command_kind not in COMMAND_KIND_TO_INTENTS:
        # Unknown CommandKind - allow any intent (don't fail validation on unknown)
        return True

    allowed_intents = COMMAND_KIND_TO_INTENTS[command_kind]
    return intent in allowed_intents


def get_allowed_intents_for_command_kind(command_kind: str) -> List[str]:
    """
    Get list of allowed intents for a CommandKind.

    Args:
        command_kind: Houndify CommandKind (e.g., "WeatherCommand")

    Returns:
        List of allowed intent strings

    Example:
        >>> intents = get_allowed_intents_for_command_kind("WeatherCommand")
        >>> "weather_query" in intents
        True
    """
    return COMMAND_KIND_TO_INTENTS.get(command_kind, [])


def get_command_kind_for_intent(intent: str) -> str | None:
    """
    Reverse lookup: get CommandKind for an intent.

    Args:
        intent: Intent string (e.g., "weather_query")

    Returns:
        CommandKind string or None if not found

    Example:
        >>> get_command_kind_for_intent("weather_query")
        'WeatherCommand'
    """
    for command_kind, intents in COMMAND_KIND_TO_INTENTS.items():
        if intent in intents:
            return command_kind
    return None


__all__ = [
    # CommandKind constants
    "COMMAND_KIND_WEATHER",
    "COMMAND_KIND_MUSIC",
    "COMMAND_KIND_NAVIGATION",
    "COMMAND_KIND_PHONE",
    "COMMAND_KIND_LOCAL_SEARCH",
    "COMMAND_KIND_SPORTS",
    "COMMAND_KIND_NEWS",
    "COMMAND_KIND_STOCKS",
    "COMMAND_KIND_CALENDAR",
    "COMMAND_KIND_ALARM",
    "COMMAND_KIND_TIMER",
    "COMMAND_KIND_REMINDERS",
    "COMMAND_KIND_MESSAGES",
    "COMMAND_KIND_EMAIL",
    "COMMAND_KIND_CONTACTS",
    "COMMAND_KIND_CONVERSATIONAL",
    "COMMAND_KIND_NO_RESULT",
    "COMMAND_KIND_CUSTOM",
    # Intent constants
    "INTENT_WEATHER_QUERY",
    "INTENT_WEATHER_FORECAST",
    "INTENT_WEATHER_HISTORICAL",
    "INTENT_WEATHER_ALERT",
    "INTENT_WEATHER_HOURLY",
    "INTENT_WEATHER_WEEKLY",
    "INTENT_MUSIC_PLAY",
    "INTENT_MUSIC_PAUSE",
    "INTENT_MUSIC_RESUME",
    "INTENT_MUSIC_SKIP",
    "INTENT_MUSIC_PREVIOUS",
    "INTENT_MUSIC_STOP",
    "INTENT_MUSIC_SEARCH",
    "INTENT_MUSIC_PLAYLIST",
    "INTENT_MUSIC_VOLUME",
    "INTENT_NAV_NAVIGATE",
    "INTENT_NAV_FIND_ROUTE",
    "INTENT_NAV_CHECK_TRAFFIC",
    "INTENT_NAV_FIND_PARKING",
    "INTENT_NAV_ETA",
    "INTENT_NAV_NEARBY",
    "INTENT_PHONE_CALL",
    "INTENT_PHONE_VOICEMAIL",
    "INTENT_PHONE_CONTACT_LOOKUP",
    "INTENT_UNRECOGNIZED",
    "INTENT_UNCLEAR_QUERY",
    "INTENT_CUSTOM",
    # Mappings
    "COMMAND_KIND_TO_INTENTS",
    # Helper functions
    "is_intent_valid_for_command_kind",
    "get_allowed_intents_for_command_kind",
    "get_command_kind_for_intent",
]
