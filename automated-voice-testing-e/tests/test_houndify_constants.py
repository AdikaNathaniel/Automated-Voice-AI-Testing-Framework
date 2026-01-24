"""
Tests for Houndify constants and validation functions

This module tests the Houndify CommandKind and Intent mappings,
along with the validation helper functions.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import pytest
from constants.houndify import (
    COMMAND_KIND_WEATHER,
    COMMAND_KIND_MUSIC,
    COMMAND_KIND_NAVIGATION,
    COMMAND_KIND_PHONE,
    COMMAND_KIND_NO_RESULT,
    INTENT_WEATHER_QUERY,
    INTENT_WEATHER_FORECAST,
    INTENT_MUSIC_PLAY,
    INTENT_MUSIC_PAUSE,
    INTENT_NAV_NAVIGATE,
    INTENT_PHONE_CALL,
    INTENT_UNRECOGNIZED,
    is_intent_valid_for_command_kind,
    get_allowed_intents_for_command_kind,
    get_command_kind_for_intent,
)


class TestCommandKindConstants:
    """Test CommandKind constant definitions"""

    def test_weather_command_kind(self):
        """Test WeatherCommand constant"""
        assert COMMAND_KIND_WEATHER == "WeatherCommand"

    def test_music_command_kind(self):
        """Test MusicCommand constant"""
        assert COMMAND_KIND_MUSIC == "MusicCommand"

    def test_navigation_command_kind(self):
        """Test NavigationCommand constant"""
        assert COMMAND_KIND_NAVIGATION == "NavigationCommand"

    def test_phone_command_kind(self):
        """Test PhoneCommand constant"""
        assert COMMAND_KIND_PHONE == "PhoneCommand"

    def test_no_result_command_kind(self):
        """Test NoResultCommand constant"""
        assert COMMAND_KIND_NO_RESULT == "NoResultCommand"


class TestIntentConstants:
    """Test Intent constant definitions"""

    def test_weather_intents(self):
        """Test weather intent constants"""
        assert INTENT_WEATHER_QUERY == "weather_query"
        assert INTENT_WEATHER_FORECAST == "weather_forecast"

    def test_music_intents(self):
        """Test music intent constants"""
        assert INTENT_MUSIC_PLAY == "music_play"
        assert INTENT_MUSIC_PAUSE == "music_pause"

    def test_navigation_intents(self):
        """Test navigation intent constants"""
        assert INTENT_NAV_NAVIGATE == "navigate_to_location"

    def test_phone_intents(self):
        """Test phone intent constants"""
        assert INTENT_PHONE_CALL == "phone_call"

    def test_generic_intents(self):
        """Test generic intent constants"""
        assert INTENT_UNRECOGNIZED == "unrecognized"


class TestIsIntentValidForCommandKind:
    """Test is_intent_valid_for_command_kind function"""

    def test_valid_weather_intent(self):
        """Test valid weather intent returns True"""
        result = is_intent_valid_for_command_kind(
            COMMAND_KIND_WEATHER,
            INTENT_WEATHER_QUERY
        )
        assert result is True

    def test_invalid_weather_intent(self):
        """Test invalid weather intent returns False"""
        result = is_intent_valid_for_command_kind(
            COMMAND_KIND_WEATHER,
            INTENT_MUSIC_PLAY
        )
        assert result is False

    def test_valid_music_intent(self):
        """Test valid music intent returns True"""
        result = is_intent_valid_for_command_kind(
            COMMAND_KIND_MUSIC,
            INTENT_MUSIC_PLAY
        )
        assert result is True

    def test_invalid_music_intent(self):
        """Test invalid music intent returns False"""
        result = is_intent_valid_for_command_kind(
            COMMAND_KIND_MUSIC,
            INTENT_NAV_NAVIGATE
        )
        assert result is False

    def test_unknown_command_kind_returns_true(self):
        """Test unknown CommandKind returns True (allows any intent)"""
        result = is_intent_valid_for_command_kind(
            "UnknownCommand",
            "some_intent"
        )
        assert result is True

    def test_valid_navigation_intent(self):
        """Test valid navigation intent returns True"""
        result = is_intent_valid_for_command_kind(
            COMMAND_KIND_NAVIGATION,
            INTENT_NAV_NAVIGATE
        )
        assert result is True

    def test_valid_phone_intent(self):
        """Test valid phone intent returns True"""
        result = is_intent_valid_for_command_kind(
            COMMAND_KIND_PHONE,
            INTENT_PHONE_CALL
        )
        assert result is True

    def test_no_result_with_unrecognized_intent(self):
        """Test NoResultCommand with unrecognized intent"""
        result = is_intent_valid_for_command_kind(
            COMMAND_KIND_NO_RESULT,
            INTENT_UNRECOGNIZED
        )
        assert result is True


class TestGetAllowedIntentsForCommandKind:
    """Test get_allowed_intents_for_command_kind function"""

    def test_weather_command_intents(self):
        """Test getting allowed intents for WeatherCommand"""
        intents = get_allowed_intents_for_command_kind(COMMAND_KIND_WEATHER)
        assert isinstance(intents, list)
        assert len(intents) > 0
        assert INTENT_WEATHER_QUERY in intents
        assert INTENT_WEATHER_FORECAST in intents

    def test_music_command_intents(self):
        """Test getting allowed intents for MusicCommand"""
        intents = get_allowed_intents_for_command_kind(COMMAND_KIND_MUSIC)
        assert isinstance(intents, list)
        assert len(intents) > 0
        assert INTENT_MUSIC_PLAY in intents
        assert INTENT_MUSIC_PAUSE in intents

    def test_navigation_command_intents(self):
        """Test getting allowed intents for NavigationCommand"""
        intents = get_allowed_intents_for_command_kind(COMMAND_KIND_NAVIGATION)
        assert isinstance(intents, list)
        assert len(intents) > 0
        assert INTENT_NAV_NAVIGATE in intents

    def test_unknown_command_kind_returns_empty_list(self):
        """Test unknown CommandKind returns empty list"""
        intents = get_allowed_intents_for_command_kind("UnknownCommand")
        assert isinstance(intents, list)
        assert len(intents) == 0


class TestGetCommandKindForIntent:
    """Test get_command_kind_for_intent function"""

    def test_weather_query_intent(self):
        """Test getting CommandKind for weather_query intent"""
        command_kind = get_command_kind_for_intent(INTENT_WEATHER_QUERY)
        assert command_kind == COMMAND_KIND_WEATHER

    def test_music_play_intent(self):
        """Test getting CommandKind for music_play intent"""
        command_kind = get_command_kind_for_intent(INTENT_MUSIC_PLAY)
        assert command_kind == COMMAND_KIND_MUSIC

    def test_navigate_intent(self):
        """Test getting CommandKind for navigate_to_location intent"""
        command_kind = get_command_kind_for_intent(INTENT_NAV_NAVIGATE)
        assert command_kind == COMMAND_KIND_NAVIGATION

    def test_phone_call_intent(self):
        """Test getting CommandKind for phone_call intent"""
        command_kind = get_command_kind_for_intent(INTENT_PHONE_CALL)
        assert command_kind == COMMAND_KIND_PHONE

    def test_unknown_intent_returns_none(self):
        """Test unknown intent returns None"""
        command_kind = get_command_kind_for_intent("unknown_intent")
        assert command_kind is None

    def test_unrecognized_intent(self):
        """Test getting CommandKind for unrecognized intent"""
        command_kind = get_command_kind_for_intent(INTENT_UNRECOGNIZED)
        assert command_kind == COMMAND_KIND_NO_RESULT
