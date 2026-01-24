#!/usr/bin/env python3
"""
Seed Comprehensive Test Scenarios for LLM Ensemble Validation.

This script creates realistic test scenarios covering:
1. Weather queries (single-turn, multi-language)
2. Navigation commands (single-turn)
3. Music commands (single-turn)
4. Restaurant reservation (multi-turn conversation)
5. Smart home commands (single-turn)
6. Edge cases (ambiguous queries, failures)

Each scenario includes:
- ScenarioScript with appropriate validation_mode
- ScenarioStep(s) with user utterances
- ExpectedOutcome with CommandKind and response patterns

Usage:
    python scripts/seed_comprehensive_scenarios.py

Environment:
    Requires DATABASE_URL to be set or uses default development database.
"""

import asyncio
import logging
import os
import sys
from uuid import uuid4

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def get_database_url():
    """Get database URL from environment or use default."""
    url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5433/voiceai_testing')
    # Ensure we use psycopg2 for sync operations
    if url.startswith('postgresql+asyncpg://'):
        url = url.replace('postgresql+asyncpg://', 'postgresql://')
    return url


def create_scenario_scripts():
    """Define comprehensive test scenarios."""
    return [
        # =====================================================================
        # WEATHER SCENARIOS (Single-turn, Multi-language)
        # =====================================================================
        {
            "name": "Weather Query - Basic English",
            "description": "Test basic weather query in English",
            "version": "1.0.0",
            "validation_mode": "hybrid",
            "is_active": True,
            "approval_status": "approved",
            "steps": [
                {
                    "step_order": 1,
                    "user_utterance": "What's the weather like today?",
                    "expected_outcomes": [
                        {
                            "expected_command_kind": "WeatherCommand",
                            "expected_asr_confidence_min": 0.80,
                            "validation_rules": {
                                "expected_transcript": "What's the weather like today?",
                                "response_should_contain": ["weather", "temperature", "degrees"],
                            },
                            "entities": {
                                "query_type": "current_weather",
                            },
                        }
                    ],
                }
            ],
        },
        {
            "name": "Weather Query - Location Specific",
            "description": "Test weather query for specific location",
            "version": "1.0.0",
            "validation_mode": "hybrid",
            "is_active": True,
            "approval_status": "approved",
            "steps": [
                {
                    "step_order": 1,
                    "user_utterance": "What's the weather in Seattle tomorrow?",
                    "expected_outcomes": [
                        {
                            "expected_command_kind": "WeatherCommand",
                            "expected_asr_confidence_min": 0.80,
                            "validation_rules": {
                                "expected_transcript": "What's the weather in Seattle tomorrow?",
                                "response_should_contain": ["Seattle", "tomorrow"],
                            },
                            "entities": {
                                "location": "Seattle",
                                "time_reference": "tomorrow",
                            },
                        }
                    ],
                }
            ],
        },
        {
            "name": "Weather Query - Spanish",
            "description": "Test weather query in Spanish",
            "version": "1.0.0",
            "validation_mode": "hybrid",
            "is_active": True,
            "approval_status": "approved",
            "script_metadata": {"language": "es-ES"},
            "steps": [
                {
                    "step_order": 1,
                    "user_utterance": "¿Cómo está el tiempo hoy?",
                    "expected_outcomes": [
                        {
                            "expected_command_kind": "WeatherCommand",
                            "expected_asr_confidence_min": 0.75,
                            "validation_rules": {
                                "expected_transcript": "¿Cómo está el tiempo hoy?",
                                "language": "es-ES",
                            },
                            "entities": {
                                "language": "es-ES",
                            },
                        }
                    ],
                }
            ],
        },
        {
            "name": "Weather Query - French",
            "description": "Test weather query in French",
            "version": "1.0.0",
            "validation_mode": "hybrid",
            "is_active": True,
            "approval_status": "approved",
            "script_metadata": {"language": "fr-FR"},
            "steps": [
                {
                    "step_order": 1,
                    "user_utterance": "Quel temps fait-il aujourd'hui?",
                    "expected_outcomes": [
                        {
                            "expected_command_kind": "WeatherCommand",
                            "expected_asr_confidence_min": 0.75,
                            "validation_rules": {
                                "expected_transcript": "Quel temps fait-il aujourd'hui?",
                                "language": "fr-FR",
                            },
                            "entities": {
                                "language": "fr-FR",
                            },
                        }
                    ],
                }
            ],
        },
        # =====================================================================
        # NAVIGATION SCENARIOS (Single-turn)
        # =====================================================================
        {
            "name": "Navigation - Basic Directions",
            "description": "Test basic navigation request",
            "version": "1.0.0",
            "validation_mode": "hybrid",
            "is_active": True,
            "approval_status": "approved",
            "steps": [
                {
                    "step_order": 1,
                    "user_utterance": "Navigate to the nearest coffee shop",
                    "expected_outcomes": [
                        {
                            "expected_command_kind": "NavigationCommand",
                            "expected_asr_confidence_min": 0.80,
                            "validation_rules": {
                                "expected_transcript": "Navigate to the nearest coffee shop",
                                "response_should_contain": ["navigating", "coffee"],
                            },
                            "entities": {
                                "destination_type": "coffee_shop",
                                "distance_preference": "nearest",
                            },
                        }
                    ],
                }
            ],
        },
        {
            "name": "Navigation - Address",
            "description": "Test navigation to specific address",
            "version": "1.0.0",
            "validation_mode": "hybrid",
            "is_active": True,
            "approval_status": "approved",
            "steps": [
                {
                    "step_order": 1,
                    "user_utterance": "Give me directions to 123 Main Street",
                    "expected_outcomes": [
                        {
                            "expected_command_kind": "NavigationCommand",
                            "expected_asr_confidence_min": 0.80,
                            "validation_rules": {
                                "expected_transcript": "Give me directions to 123 Main Street",
                                "response_should_contain": ["directions", "Main Street"],
                            },
                            "entities": {
                                "address": "123 Main Street",
                            },
                        }
                    ],
                }
            ],
        },
        # =====================================================================
        # MUSIC SCENARIOS (Single-turn)
        # =====================================================================
        {
            "name": "Music - Play Artist",
            "description": "Test playing music by artist",
            "version": "1.0.0",
            "validation_mode": "hybrid",
            "is_active": True,
            "approval_status": "approved",
            "steps": [
                {
                    "step_order": 1,
                    "user_utterance": "Play some music by The Beatles",
                    "expected_outcomes": [
                        {
                            "expected_command_kind": "MusicCommand",
                            "expected_asr_confidence_min": 0.80,
                            "validation_rules": {
                                "expected_transcript": "Play some music by The Beatles",
                                "response_should_contain": ["playing", "Beatles"],
                            },
                            "entities": {
                                "artist": "The Beatles",
                                "action": "play",
                            },
                        }
                    ],
                }
            ],
        },
        {
            "name": "Music - Play Genre",
            "description": "Test playing music by genre",
            "version": "1.0.0",
            "validation_mode": "hybrid",
            "is_active": True,
            "approval_status": "approved",
            "steps": [
                {
                    "step_order": 1,
                    "user_utterance": "Play jazz music",
                    "expected_outcomes": [
                        {
                            "expected_command_kind": "MusicCommand",
                            "expected_asr_confidence_min": 0.80,
                            "validation_rules": {
                                "expected_transcript": "Play jazz music",
                                "response_should_contain": ["playing", "jazz"],
                            },
                            "entities": {
                                "genre": "jazz",
                                "action": "play",
                            },
                        }
                    ],
                }
            ],
        },
        {
            "name": "Music - Control Playback",
            "description": "Test music playback control",
            "version": "1.0.0",
            "validation_mode": "hybrid",
            "is_active": True,
            "approval_status": "approved",
            "steps": [
                {
                    "step_order": 1,
                    "user_utterance": "Pause the music",
                    "expected_outcomes": [
                        {
                            "expected_command_kind": "MusicCommand",
                            "expected_asr_confidence_min": 0.85,
                            "validation_rules": {
                                "expected_transcript": "Pause the music",
                                "response_should_contain": ["pausing", "paused"],
                            },
                            "entities": {
                                "action": "pause",
                            },
                        }
                    ],
                }
            ],
        },
        # =====================================================================
        # RESTAURANT RESERVATION (Multi-turn)
        # =====================================================================
        {
            "name": "Restaurant Reservation - Full Flow",
            "description": "Complete multi-turn restaurant reservation",
            "version": "1.0.0",
            "validation_mode": "hybrid",
            "is_active": True,
            "approval_status": "approved",
            "script_metadata": {
                "domain": "dining_reservation",
                "multi_turn": True,
            },
            "steps": [
                {
                    "step_order": 1,
                    "user_utterance": "I'd like to make a dinner reservation",
                    "expected_outcomes": [
                        {
                            "expected_command_kind": "ClientMatchCommand",
                            "expected_asr_confidence_min": 0.80,
                            "validation_rules": {
                                "expected_transcript": "I'd like to make a dinner reservation",
                                "response_should_contain": ["restaurant", "which"],
                            },
                            "entities": {
                                "intent": "reservation_start",
                            },
                        }
                    ],
                },
                {
                    "step_order": 2,
                    "user_utterance": "Italian restaurant downtown",
                    "expected_outcomes": [
                        {
                            "expected_command_kind": "ClientMatchCommand",
                            "expected_asr_confidence_min": 0.80,
                            "validation_rules": {
                                "expected_transcript": "Italian restaurant downtown",
                                "response_should_contain": ["date", "time"],
                            },
                            "entities": {
                                "cuisine": "italian",
                                "location": "downtown",
                            },
                        }
                    ],
                },
                {
                    "step_order": 3,
                    "user_utterance": "Tomorrow at 7 PM",
                    "expected_outcomes": [
                        {
                            "expected_command_kind": "ClientMatchCommand",
                            "expected_asr_confidence_min": 0.80,
                            "validation_rules": {
                                "expected_transcript": "Tomorrow at 7 PM",
                                "response_should_contain": ["people", "party"],
                            },
                            "entities": {
                                "date": "tomorrow",
                                "time": "19:00",
                            },
                        }
                    ],
                },
                {
                    "step_order": 4,
                    "user_utterance": "Four people",
                    "expected_outcomes": [
                        {
                            "expected_command_kind": "ClientMatchCommand",
                            "expected_asr_confidence_min": 0.85,
                            "validation_rules": {
                                "expected_transcript": "Four people",
                                "response_should_contain": ["confirm", "reservation"],
                            },
                            "entities": {
                                "party_size": 4,
                            },
                        }
                    ],
                },
                {
                    "step_order": 5,
                    "user_utterance": "Yes, confirm the reservation",
                    "expected_outcomes": [
                        {
                            "expected_command_kind": "ClientMatchCommand",
                            "expected_asr_confidence_min": 0.85,
                            "validation_rules": {
                                "expected_transcript": "Yes, confirm the reservation",
                                "response_should_contain": ["confirmed", "confirmation"],
                            },
                            "entities": {
                                "confirmation": True,
                            },
                        }
                    ],
                },
            ],
        },
        # =====================================================================
        # SMART HOME SCENARIOS (Single-turn)
        # =====================================================================
        {
            "name": "Smart Home - Turn On Lights",
            "description": "Test turning on lights",
            "version": "1.0.0",
            "validation_mode": "hybrid",
            "is_active": True,
            "approval_status": "approved",
            "steps": [
                {
                    "step_order": 1,
                    "user_utterance": "Turn on the living room lights",
                    "expected_outcomes": [
                        {
                            "expected_command_kind": "ClientMatchCommand",
                            "expected_asr_confidence_min": 0.85,
                            "validation_rules": {
                                "expected_transcript": "Turn on the living room lights",
                                "response_should_contain": ["turning on", "living room", "lights"],
                            },
                            "entities": {
                                "device": "lights",
                                "location": "living room",
                                "action": "on",
                            },
                        }
                    ],
                }
            ],
        },
        {
            "name": "Smart Home - Turn Off Lights",
            "description": "Test turning off lights",
            "version": "1.0.0",
            "validation_mode": "hybrid",
            "is_active": True,
            "approval_status": "approved",
            "steps": [
                {
                    "step_order": 1,
                    "user_utterance": "Turn off all the lights",
                    "expected_outcomes": [
                        {
                            "expected_command_kind": "ClientMatchCommand",
                            "expected_asr_confidence_min": 0.85,
                            "validation_rules": {
                                "expected_transcript": "Turn off all the lights",
                                "response_should_contain": ["turning off", "lights"],
                            },
                            "entities": {
                                "device": "lights",
                                "scope": "all",
                                "action": "off",
                            },
                        }
                    ],
                }
            ],
        },
        # =====================================================================
        # EDGE CASES AND FAILURE SCENARIOS
        # =====================================================================
        {
            "name": "Edge Case - Ambiguous Query",
            "description": "Test handling of ambiguous query",
            "version": "1.0.0",
            "validation_mode": "llm_ensemble",  # LLM-only for behavioral testing
            "is_active": True,
            "approval_status": "approved",
            "steps": [
                {
                    "step_order": 1,
                    "user_utterance": "Play that thing",
                    "expected_outcomes": [
                        {
                            "expected_command_kind": "MusicCommand",
                            "expected_asr_confidence_min": 0.70,
                            "validation_rules": {
                                "expected_transcript": "Play that thing",
                                "response_should_contain": ["which", "what", "clarify"],
                            },
                            "entities": {
                                "ambiguous": True,
                            },
                        }
                    ],
                }
            ],
        },
        {
            "name": "Edge Case - No Result",
            "description": "Test handling of unrecognized query",
            "version": "1.0.0",
            "validation_mode": "llm_ensemble",
            "is_active": True,
            "approval_status": "approved",
            "steps": [
                {
                    "step_order": 1,
                    "user_utterance": "Blah blah random words xyz",
                    "expected_outcomes": [
                        {
                            "expected_command_kind": "NoResultCommand",
                            "expected_asr_confidence_min": 0.50,
                            "validation_rules": {
                                "expected_transcript": "Blah blah random words xyz",
                                "response_should_contain": ["understand", "sorry", "didn't"],
                            },
                            "entities": {},
                        }
                    ],
                }
            ],
        },
        {
            "name": "Edge Case - Low Confidence",
            "description": "Test with expected low ASR confidence",
            "version": "1.0.0",
            "validation_mode": "hybrid",
            "is_active": True,
            "approval_status": "approved",
            "steps": [
                {
                    "step_order": 1,
                    "user_utterance": "Whzzt weddur tomrrow",  # Intentionally garbled
                    "expected_outcomes": [
                        {
                            "expected_command_kind": "WeatherCommand",
                            "expected_asr_confidence_min": 0.50,  # Lower threshold
                            "validation_rules": {
                                "expected_transcript": "What's the weather tomorrow",
                                "fuzzy_match": True,
                            },
                            "entities": {},
                        }
                    ],
                }
            ],
        },
        # =====================================================================
        # RESPONSE CONTENT VALIDATION - PASS SCENARIOS
        # =====================================================================
        {
            "name": "Response Content - Contains Pattern (Pass)",
            "description": "Test that response contains required phrases",
            "version": "1.0.0",
            "validation_mode": "houndify",
            "is_active": True,
            "approval_status": "approved",
            "steps": [
                {
                    "step_order": 1,
                    "user_utterance": "What's the weather in Seattle?",
                    "expected_outcomes": [
                        {
                            "expected_command_kind": "WeatherCommand",
                            "expected_asr_confidence_min": 0.80,
                            "expected_response_content": {
                                "contains": ["seattle", "weather"],
                            },
                            "entities": {},
                        }
                    ],
                }
            ],
        },
        {
            "name": "Response Content - Not Contains Pattern (Pass)",
            "description": "Test that response does NOT contain forbidden phrases",
            "version": "1.0.0",
            "validation_mode": "houndify",
            "is_active": True,
            "approval_status": "approved",
            "steps": [
                {
                    "step_order": 1,
                    "user_utterance": "Play some jazz music",
                    "expected_outcomes": [
                        {
                            "expected_command_kind": "MusicCommand",
                            "expected_asr_confidence_min": 0.80,
                            "expected_response_content": {
                                "contains": ["jazz", "playing"],
                                "not_contains": ["error", "sorry", "can't"],
                            },
                            "entities": {},
                        }
                    ],
                }
            ],
        },
        {
            "name": "Response Content - Regex Pattern (Pass)",
            "description": "Test regex pattern matching in response",
            "version": "1.0.0",
            "validation_mode": "houndify",
            "is_active": True,
            "approval_status": "approved",
            "steps": [
                {
                    "step_order": 1,
                    "user_utterance": "What's the temperature outside?",
                    "expected_outcomes": [
                        {
                            "expected_command_kind": "WeatherCommand",
                            "expected_asr_confidence_min": 0.80,
                            "expected_response_content": {
                                "regex": ["\\d+\\s*(degrees|°)"],
                            },
                            "entities": {},
                        }
                    ],
                }
            ],
        },
        {
            "name": "Response Content - Combined Patterns (Pass)",
            "description": "Test all pattern types together with hybrid (Houndify + LLM) validation",
            "version": "1.0.0",
            "validation_mode": "hybrid",
            "is_active": True,
            "approval_status": "approved",
            "steps": [
                {
                    "step_order": 1,
                    "user_utterance": "Navigate to downtown Seattle",
                    "expected_outcomes": [
                        {
                            "expected_command_kind": "NavigationCommand",
                            "expected_asr_confidence_min": 0.80,
                            "expected_response_content": {
                                "contains": ["seattle", "navigation"],
                                "not_contains": ["error", "unknown location"],
                                "regex": ["(route|directions?|navigating)"],
                                "regex_not_match": ["no\\s+results?", "cannot\\s+find"],
                            },
                            "entities": {},
                        }
                    ],
                }
            ],
        },
        # =====================================================================
        # RESPONSE CONTENT VALIDATION - FAIL SCENARIOS (for testing)
        # =====================================================================
        {
            "name": "Response Content - Missing Required Phrase (Fail)",
            "description": "TEST: Should FAIL - response missing required 'humidity' phrase",
            "version": "1.0.0",
            "validation_mode": "houndify",
            "is_active": True,
            "approval_status": "approved",
            "steps": [
                {
                    "step_order": 1,
                    "user_utterance": "What's the weather?",
                    "expected_outcomes": [
                        {
                            "expected_command_kind": "WeatherCommand",
                            "expected_asr_confidence_min": 0.80,
                            # Mock client doesn't include humidity, so this should fail
                            "expected_response_content": {
                                "contains": ["weather", "humidity"],
                            },
                            "entities": {},
                        }
                    ],
                }
            ],
        },
        {
            "name": "Response Content - Contains Forbidden Phrase (Fail)",
            "description": "TEST: Should FAIL - response contains 'currently' which is forbidden",
            "version": "1.0.0",
            "validation_mode": "houndify",
            "is_active": True,
            "approval_status": "approved",
            "steps": [
                {
                    "step_order": 1,
                    "user_utterance": "What's the weather?",
                    "expected_outcomes": [
                        {
                            "expected_command_kind": "WeatherCommand",
                            "expected_asr_confidence_min": 0.80,
                            # Mock client includes 'currently', so this should fail
                            "expected_response_content": {
                                "not_contains": ["currently"],
                            },
                            "entities": {},
                        }
                    ],
                }
            ],
        },
        {
            "name": "Response Content - Regex Not Matched (Fail)",
            "description": "TEST: Should FAIL - response doesn't match strict numeric pattern",
            "version": "1.0.0",
            "validation_mode": "houndify",
            "is_active": True,
            "approval_status": "approved",
            "steps": [
                {
                    "step_order": 1,
                    "user_utterance": "Play some music",
                    "expected_outcomes": [
                        {
                            "expected_command_kind": "MusicCommand",
                            "expected_asr_confidence_min": 0.80,
                            # Music response won't have temperature pattern
                            "expected_response_content": {
                                "regex": ["\\d{2,3}\\s*degrees\\s*fahrenheit"],
                            },
                            "entities": {},
                        }
                    ],
                }
            ],
        },
        {
            "name": "Response Content - No Patterns Defined (Auto-Pass)",
            "description": "TEST: Should PASS - empty expected_response_content auto-passes",
            "version": "1.0.0",
            "validation_mode": "houndify",
            "is_active": True,
            "approval_status": "approved",
            "steps": [
                {
                    "step_order": 1,
                    "user_utterance": "What time is it?",
                    "expected_outcomes": [
                        {
                            "expected_command_kind": "TimerCommand",
                            "expected_asr_confidence_min": 0.80,
                            # Empty object should auto-pass
                            "expected_response_content": {},
                            "entities": {},
                        }
                    ],
                }
            ],
        },
        # =====================================================================
        # HOUNDIFY-ONLY VALIDATION MODE
        # =====================================================================
        {
            "name": "Houndify Only - Weather",
            "description": "Test with Houndify-only validation (no LLM)",
            "version": "1.0.0",
            "validation_mode": "houndify",  # Skip LLM validation
            "is_active": True,
            "approval_status": "approved",
            "steps": [
                {
                    "step_order": 1,
                    "user_utterance": "What's the temperature?",
                    "expected_outcomes": [
                        {
                            "expected_command_kind": "WeatherCommand",
                            "expected_asr_confidence_min": 0.85,
                            "expected_response_content": {
                                "contains": ["temperature", "degrees"],
                            },
                            "entities": {},
                        }
                    ],
                }
            ],
        },
        # =====================================================================
        # LLM-ENSEMBLE ONLY VALIDATION MODE
        # =====================================================================
        {
            "name": "LLM Only - Complex Query",
            "description": "Test with LLM-only validation for behavioral testing",
            "version": "1.0.0",
            "validation_mode": "llm_ensemble",  # Skip Houndify validation
            "is_active": True,
            "approval_status": "approved",
            "steps": [
                {
                    "step_order": 1,
                    "user_utterance": "I need to find a place for dinner tonight that's not too expensive",
                    "expected_outcomes": [
                        {
                            "expected_command_kind": "ClientMatchCommand",
                            "expected_asr_confidence_min": 0.70,
                            "validation_rules": {
                                "expected_transcript": "I need to find a place for dinner tonight that's not too expensive",
                                "behavioral_expectation": "AI should understand dining intent and offer restaurant options",
                            },
                            "entities": {
                                "intent": "restaurant_search",
                                "time": "tonight",
                                "budget": "moderate",
                            },
                        }
                    ],
                }
            ],
        },
    ]


def seed_scenarios(db_url: str):
    """Seed scenarios into the database."""
    from models.scenario_script import ScenarioScript, ScenarioStep
    from models.expected_outcome import ExpectedOutcome
    from models.base import Base

    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    scenarios = create_scenario_scripts()
    created_count = 0

    try:
        for scenario_data in scenarios:
            # Check if scenario already exists
            existing = session.query(ScenarioScript).filter(
                ScenarioScript.name == scenario_data["name"]
            ).first()

            if existing:
                logger.info(f"Scenario already exists: {scenario_data['name']}")
                continue

            # Create ScenarioScript
            script = ScenarioScript(
                id=uuid4(),
                name=scenario_data["name"],
                description=scenario_data.get("description"),
                version=scenario_data.get("version", "1.0.0"),
                validation_mode=scenario_data.get("validation_mode", "hybrid"),
                is_active=scenario_data.get("is_active", True),
                approval_status=scenario_data.get("approval_status", "approved"),
                script_metadata=scenario_data.get("script_metadata"),
            )
            session.add(script)
            session.flush()  # Get script.id

            # Create steps and expected outcomes
            for step_data in scenario_data.get("steps", []):
                step = ScenarioStep(
                    id=uuid4(),
                    script_id=script.id,
                    step_order=step_data["step_order"],
                    user_utterance=step_data["user_utterance"],
                    step_metadata=step_data.get("step_metadata"),
                )
                session.add(step)
                session.flush()  # Get step.id

                # Create expected outcomes for this step
                for idx, outcome_data in enumerate(step_data.get("expected_outcomes", [])):
                    # Generate outcome_code from scenario name and step
                    cmd_kind = outcome_data.get("expected_command_kind", "Unknown")
                    outcome_code = f"{script.name.upper().replace(' ', '_').replace('-', '_')}_S{step_data['step_order']}_O{idx+1}"
                    outcome_name = f"{cmd_kind} - Step {step_data['step_order']}"

                    outcome = ExpectedOutcome(
                        id=uuid4(),
                        scenario_step_id=step.id,
                        outcome_code=outcome_code,
                        name=outcome_name,
                        description=f"Expected outcome for {script.name} step {step_data['step_order']}",
                        expected_command_kind=outcome_data.get("expected_command_kind"),
                        expected_asr_confidence_min=outcome_data.get("expected_asr_confidence_min"),
                        expected_response_content=outcome_data.get("expected_response_content"),
                        validation_rules=outcome_data.get("validation_rules"),
                        entities=outcome_data.get("entities"),
                    )
                    session.add(outcome)

            created_count += 1
            logger.info(f"Created scenario: {scenario_data['name']}")

        session.commit()
        logger.info(f"Successfully created {created_count} new scenarios")

    except Exception as e:
        session.rollback()
        logger.error(f"Error seeding scenarios: {e}")
        raise
    finally:
        session.close()


def main():
    """Main entry point."""
    db_url = get_database_url()
    logger.info(f"Connecting to database...")

    try:
        seed_scenarios(db_url)
        logger.info("Scenario seeding complete!")
    except Exception as e:
        logger.error(f"Failed to seed scenarios: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
