#!/usr/bin/env python3
"""
Seed Morning Routine Multi-Language Scenario (CORRECTED VERSION)

Creates a 3-step morning routine where each step has language variants stored
in step_metadata['language_variants'], NOT as separate ScenarioStep records.

CORRECT DATA MODEL:
- 1 ScenarioStep per step_order (3 total steps)
- Language variants stored in step_metadata['language_variants'] array
- Each variant has: language_code, user_utterance

3-step flow:
- Step 1: Check weather (English & French variants)
- Step 2: Check calendar (English & French variants)
- Step 3: Get directions (English & French variants)

Usage:
    python backend/scripts/seed_morning_routine_fixed.py
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


async def seed_morning_routine_fixed():
    """Seed the corrected morning routine scenario with language variants."""
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
                logger.error("Admin user not found. Please run seed_data.py first.")
                return False

            # Check if scenario already exists
            result = await db.execute(
                select(ScenarioScript).where(
                    ScenarioScript.name == "Morning Routine - Full Bilingual"
                )
            )
            existing = result.scalar_one_or_none()

            if existing:
                logger.info(f"Full Bilingual Morning Routine scenario already exists (ID: {existing.id})")
                logger.info(f"  To re-seed, delete it first")
                return True

            logger.info("Creating corrected Morning Routine scenario...")

            # Create the scenario script
            scenario = ScenarioScript(
                name="Morning Routine - Full Bilingual",
                description="3-step morning routine with bilingual support. Each step has English/French variants stored in step_metadata.",
                version="3.0.0",
                is_active=True,
                approval_status="approved",
                created_by=user.id,
                tenant_id=user.tenant_id,
                script_metadata={
                    "languages": ["en-US", "fr-FR"],
                    "provider": "houndify",
                    "test_type": "multilanguage_conversation_flow",
                    "conversation_flow": "3 steps, each step has language_variants in metadata"
                }
            )

            db.add(scenario)
            await db.flush()

            logger.info(f"Created scenario: {scenario.name} (ID: {scenario.id})")

            # =====================================================================
            # STEP 1: Check Weather (ONE step with language_variants)
            # =====================================================================
            step1 = ScenarioStep(
                script_id=scenario.id,
                step_order=1,
                user_utterance="What's the weather in San Francisco today?",  # Primary utterance
                step_metadata={
                    "primary_language": "en-US",
                    "variant_group": "weather_check",
                    "context": "User checks weather to decide what to wear",
                    "language_variants": [
                        {
                            "language_code": "en-US",
                            "user_utterance": "What's the weather in San Francisco today?"
                        },
                        {
                            "language_code": "fr-FR",
                            "user_utterance": "Quel temps fait-il a San Francisco aujourd'hui?"
                        }
                    ]
                }
            )
            db.add(step1)
            await db.flush()

            # ExpectedOutcome for Step 1 (applies to all language variants)
            outcome1 = ExpectedOutcome(
                outcome_code="morning_routine_weather",
                name="Weather Check",
                description="Check weather in San Francisco (any language)",
                scenario_step_id=step1.id,
                expected_command_kind="InformationCommand",
                expected_asr_confidence_min=0.75,
                validation_rules={
                    "response_should_contain": ["weather", "San Francisco", "temps"],
                    "languages": ["en-US", "fr-FR"]
                },
                entities={
                    "query_type": "weather",
                    "location": "San Francisco"
                }
            )
            db.add(outcome1)

            logger.info(f"  Step 1: Weather check (en-US, fr-FR variants)")

            # =====================================================================
            # STEP 2: Check Calendar (ONE step with language_variants)
            # =====================================================================
            step2 = ScenarioStep(
                script_id=scenario.id,
                step_order=2,
                user_utterance="What's on my calendar today?",  # Primary utterance
                step_metadata={
                    "primary_language": "en-US",
                    "variant_group": "calendar_check",
                    "context": "User checks schedule",
                    "language_variants": [
                        {
                            "language_code": "en-US",
                            "user_utterance": "What's on my calendar today?"
                        },
                        {
                            "language_code": "fr-FR",
                            "user_utterance": "Qu'est-ce que j'ai au calendrier aujourd'hui?"
                        }
                    ]
                }
            )
            db.add(step2)
            await db.flush()

            # ExpectedOutcome for Step 2
            outcome2 = ExpectedOutcome(
                outcome_code="morning_routine_calendar",
                name="Calendar Check",
                description="Check calendar (any language)",
                scenario_step_id=step2.id,
                expected_command_kind="CalendarCommand",
                expected_asr_confidence_min=0.75,
                validation_rules={
                    "response_should_contain": ["calendar", "calendrier", "today", "aujourd'hui"],
                    "languages": ["en-US", "fr-FR"]
                },
                entities={
                    "query_type": "calendar",
                    "time_reference": "today"
                }
            )
            db.add(outcome2)

            logger.info(f"  Step 2: Calendar check (en-US, fr-FR variants)")

            # =====================================================================
            # STEP 3: Get Directions (ONE step with language_variants)
            # =====================================================================
            step3 = ScenarioStep(
                script_id=scenario.id,
                step_order=3,
                user_utterance="Get directions to the nearest coffee shop",  # Primary utterance
                step_metadata={
                    "primary_language": "en-US",
                    "variant_group": "coffee_directions",
                    "context": "User gets directions to coffee before work",
                    "language_variants": [
                        {
                            "language_code": "en-US",
                            "user_utterance": "Get directions to the nearest coffee shop"
                        },
                        {
                            "language_code": "fr-FR",
                            "user_utterance": "Trouve-moi le cafe le plus proche"
                        }
                    ]
                }
            )
            db.add(step3)
            await db.flush()

            # ExpectedOutcome for Step 3
            outcome3 = ExpectedOutcome(
                outcome_code="morning_routine_directions",
                name="Coffee Directions",
                description="Get directions to coffee shop (any language)",
                scenario_step_id=step3.id,
                expected_command_kind="MapCommand",
                expected_asr_confidence_min=0.75,
                validation_rules={
                    "response_should_contain": ["directions", "coffee", "cafe"],
                    "languages": ["en-US", "fr-FR"]
                },
                entities={
                    "query_type": "directions",
                    "destination_type": "coffee_shop"
                }
            )
            db.add(outcome3)

            logger.info(f"  Step 3: Coffee directions (en-US, fr-FR variants)")

            # Commit all changes
            await db.commit()

            logger.info(f"\n{'='*70}")
            logger.info("Corrected Morning Routine scenario successfully seeded!")
            logger.info(f"{'='*70}")
            logger.info(f"\nScenario: {scenario.name}")
            logger.info(f"ID: {scenario.id}")
            logger.info(f"\nCORRECT Structure:")
            logger.info(f"  Step 1 (order=1): Weather - has language_variants [en-US, fr-FR]")
            logger.info(f"  Step 2 (order=2): Calendar - has language_variants [en-US, fr-FR]")
            logger.info(f"  Step 3 (order=3): Directions - has language_variants [en-US, fr-FR]")
            logger.info(f"\nTotal ScenarioStep records in DB: 3")
            logger.info(f"Language variants per step: 2 (stored in step_metadata)")
            logger.info(f"Languages: en-US, fr-FR")

            return True

        except Exception as e:
            logger.error(f"Error seeding scenario: {str(e)}")
            import traceback
            traceback.print_exc()
            await db.rollback()
            return False
        finally:
            await engine.dispose()


async def main():
    """Main entry point."""
    success = await seed_morning_routine_fixed()
    if success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
