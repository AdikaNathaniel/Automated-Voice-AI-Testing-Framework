#!/usr/bin/env python3
"""
Seed Morning Routine Multi-Language Scenario

Creates a realistic 3-step morning routine scenario that demonstrates:
- Natural conversation flow (weather → calendar → directions)
- Multi-language support (English & French)
- Context preservation across language switches
- Realistic use case for bilingual voice assistant users

Usage:
    python backend/scripts/seed_morning_routine.py
"""

import asyncio
import logging
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from api.config import get_settings
from models.user import User
from models.scenario_script import ScenarioScript, ScenarioStep
from models.expected_outcome import ExpectedOutcome

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


async def seed_morning_routine_scenario():
    """Seed the morning routine scenario into the database."""
    settings = get_settings()

    # Convert DATABASE_URL to async version
    database_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

    # Create async engine
    engine = create_async_engine(database_url, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        try:
            # Get admin user
            result = await db.execute(
                select(User).where(User.email == "admin@voiceai.com")
            )
            user = result.scalar_one_or_none()

            if not user:
                logger.error("❌ Admin user not found. Please run seed_data.py first.")
                return False

            # Check if scenario already exists
            result = await db.execute(
                select(ScenarioScript).where(
                    ScenarioScript.name == "Morning Routine - Bilingual Assistant"
                )
            )
            existing = result.scalar_one_or_none()

            if existing:
                logger.info(f"✓ Morning Routine scenario already exists (ID: {existing.id})")
                logger.info(f"  To re-seed, delete it first or use a different name")
                return True

            logger.info("Creating Morning Routine scenario...")

            # Create the scenario script
            scenario = ScenarioScript(
                name="Morning Routine - Bilingual Assistant",
                description="Realistic 3-step morning routine: check weather, review calendar (French), get coffee directions. Tests natural conversation flow with language switching.",
                version="1.0.0",
                is_active=True,
                approval_status="approved",
                created_by=user.id,
                tenant_id=user.tenant_id,
                script_metadata={
                    "languages": ["en-US", "fr-FR"],
                    "provider": "houndify",
                    "test_type": "multilanguage_conversation_flow",
                    "context": "Bilingual professional's morning routine",
                    "narrative": {
                        "story": [
                            "User wakes up and checks weather to decide what to wear",
                            "User reviews calendar in French (preferred language for scheduling)",
                            "User gets directions to coffee shop before work"
                        ],
                        "why_realistic": [
                            "Natural morning sequence: weather → schedule → directions",
                            "Language switching is realistic for bilingual professionals",
                            "Each step logically leads to the next",
                            "Common real-world use case"
                        ]
                    }
                }
            )

            db.add(scenario)
            await db.flush()  # Get scenario ID

            logger.info(f"✓ Created scenario: {scenario.name} (ID: {scenario.id})")

            # Step 1: Check Weather (English)
            step1 = ScenarioStep(
                script_id=scenario.id,
                step_order=1,
                user_utterance="What's the weather in San Francisco today?",
                step_metadata={
                    "language_code": "en-US",
                    "context": "User just woke up and wants to know how to dress for the day",
                    "follow_up": "Based on weather, user decides what to wear and checks schedule"
                }
            )
            db.add(step1)
            await db.flush()

            # Expected outcome for step 1
            outcome1 = ExpectedOutcome(
                outcome_code="morning_routine_weather_check",
                name="Weather Check - San Francisco",
                description="Expected outcome for weather query in San Francisco",
                scenario_step_id=step1.id,
                expected_command_kind="InformationCommand",
                expected_asr_confidence_min=0.85,
                validation_rules={
                    "expected_transcript": "what's the weather in san francisco today?",
                    "response_should_contain": ["weather", "San Francisco", "degrees"],
                    "language": "en-US"
                },
                entities={
                    "query_type": "weather",
                    "location": "San Francisco",
                    "time_reference": "today"
                }
            )
            db.add(outcome1)

            # Step 2: Check Calendar (French)
            step2 = ScenarioStep(
                script_id=scenario.id,
                step_order=2,
                user_utterance="Qu'est-ce que j'ai au calendrier aujourd'hui?",
                step_metadata={
                    "language_code": "fr-FR",
                    "translation": {
                        "en": "What's on my calendar today?",
                        "fr": "Qu'est-ce que j'ai au calendrier aujourd'hui?"
                    },
                    "context": "User switches to French for calendar (preferred language for scheduling)",
                    "follow_up": "After seeing schedule, user realizes they have meetings and needs coffee"
                }
            )
            db.add(step2)
            await db.flush()

            # Expected outcome for step 2
            outcome2 = ExpectedOutcome(
                outcome_code="morning_routine_calendar_check",
                name="Calendar Check - Today's Schedule",
                description="Expected outcome for calendar query in French",
                scenario_step_id=step2.id,
                expected_command_kind="CalendarCommand",
                expected_asr_confidence_min=0.75,
                validation_rules={
                    "expected_transcript": "qu'est-ce que j'ai au calendrier aujourd'hui?",
                    "response_should_contain": ["calendar", "calendrier", "today", "aujourd'hui"],
                    "language": "fr-FR"
                },
                entities={
                    "query_type": "calendar_lookup",
                    "language": "fr-FR",
                    "time_reference": "today"
                }
            )
            db.add(outcome2)

            # Step 3: Get Directions (English)
            step3 = ScenarioStep(
                script_id=scenario.id,
                step_order=3,
                user_utterance="Get directions to the nearest coffee shop",
                step_metadata={
                    "language_code": "en-US",
                    "context": "User returns to English for navigation, needs coffee before work",
                    "follow_up": "User is now prepared for the day with coffee directions"
                }
            )
            db.add(step3)
            await db.flush()

            # Expected outcome for step 3
            outcome3 = ExpectedOutcome(
                outcome_code="morning_routine_coffee_directions",
                name="Coffee Shop Directions",
                description="Expected outcome for navigation to nearest coffee shop",
                scenario_step_id=step3.id,
                expected_command_kind="MapCommand",
                expected_asr_confidence_min=0.85,
                validation_rules={
                    "expected_transcript": "get directions to the nearest coffee shop",
                    "response_should_contain": ["directions", "coffee"],
                    "language": "en-US"
                },
                entities={
                    "query_type": "directions",
                    "destination_type": "coffee_shop",
                    "distance_preference": "nearest"
                }
            )
            db.add(outcome3)

            # Commit all changes
            await db.commit()

            logger.info(f"✓ Created 3 steps with expected outcomes")
            logger.info(f"\n{'='*70}")
            logger.info("✅ Morning Routine scenario successfully seeded!")
            logger.info(f"{'='*70}")
            logger.info(f"\nScenario Details:")
            logger.info(f"  Name: {scenario.name}")
            logger.info(f"  ID: {scenario.id}")
            logger.info(f"  Steps: 3")
            logger.info(f"  Languages: en-US, fr-FR")
            logger.info(f"\nSteps:")
            logger.info(f"  1. Check weather (English)")
            logger.info(f"  2. Check calendar (French)")
            logger.info(f"  3. Get directions (English)")
            logger.info(f"\nYou can now:")
            logger.info(f"  • View it in the UI at /scenarios/{scenario.id}")
            logger.info(f"  • Execute it via API: POST /api/v1/scenarios/{scenario.id}/execute")
            logger.info(f"  • Add it to a test suite")

            return True

        except Exception as e:
            logger.error(f"❌ Error seeding scenario: {str(e)}")
            import traceback
            traceback.print_exc()
            await db.rollback()
            return False
        finally:
            await engine.dispose()


async def main():
    """Main entry point."""
    success = await seed_morning_routine_scenario()
    if success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
