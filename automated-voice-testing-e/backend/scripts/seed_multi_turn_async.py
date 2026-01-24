#!/usr/bin/env python3
"""
Seed Multi-Turn Scenario Data (Async Version)

Creates realistic multi-turn conversation scenarios for testing.
"""

import sys
import os
import asyncio
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select

from api.config import get_settings
from models.scenario_script import ScenarioScript, ScenarioStep
from models.expected_outcome import ExpectedOutcome
from models.user import User

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def seed_multi_turn_data():
    """Seed multi-turn scenario data."""
    settings = get_settings()

    # Convert DATABASE_URL to async version (postgresql+asyncpg://)
    database_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

    # Create async engine
    engine = create_async_engine(database_url, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        try:
            # Get admin user
            result = await db.execute(select(User).where(User.email == "admin@voiceai.com"))
            user = result.scalar_one_or_none()
            
            if not user:
                logger.error("Admin user not found. Please run seed_test_data.py first.")
                return

            # Check if scenarios already exist
            result = await db.execute(
                select(ScenarioScript).filter(
                    ScenarioScript.name.in_([
                        "Restaurant Reservation Flow",
                        "Navigation with Clarifications"
                    ])
                )
            )
            existing = result.scalars().all()

            if existing:
                logger.info("✓ Scenarios already exist, skipping seeding:")
                for script in existing:
                    logger.info(f"  - {script.name} (ID: {script.id})")
                return

            # Create Restaurant Reservation Scenario
            restaurant_script = ScenarioScript(
                name="Restaurant Reservation Flow",
                description="Complete restaurant reservation conversation with slot filling",
                version="1.0.0",
                created_by=user.id,
                script_metadata={
                    "domain": "dining_reservation",
                    "complexity": "medium",
                    "expected_turns": 5,
                    "tags": ["multi-turn", "dining", "reservation", "slot-filling"]
                }
            )
            db.add(restaurant_script)
            await db.flush()
            
            # Step 1: Initial request
            step1 = ScenarioStep(
                script_id=restaurant_script.id,
                step_order=1,
                user_utterance="I want to make a dinner reservation",
                step_metadata={"dialog_phase": "initial", "slot_to_collect": "restaurant_name"}
            )
            db.add(step1)
            await db.flush()
            
            outcome1 = ExpectedOutcome(
                outcome_code="RESERVATION_INIT",
                name="Reservation Initiation",
                scenario_step_id=step1.id,
                expected_command_kind="ClientMatchCommand",  # Custom command for reservation
                expected_response_content={"contains": ["restaurant", "which"]},
                tolerance_settings={"semantic_similarity": 0.75}
            )
            db.add(outcome1)

            # Step 2: Restaurant name
            step2 = ScenarioStep(
                script_id=restaurant_script.id,
                step_order=2,
                user_utterance="The Italian place downtown",
                step_metadata={"dialog_phase": "collecting", "slot_to_collect": "datetime"}
            )
            db.add(step2)
            await db.flush()

            outcome2 = ExpectedOutcome(
                outcome_code="RESERVATION_RESTAURANT",
                name="Restaurant Name Provided",
                scenario_step_id=step2.id,
                expected_command_kind="ClientMatchCommand",  # Custom command for restaurant selection
                entities={"restaurant_name": "Italian place"},
                expected_response_content={"contains": ["date", "time"]},
                tolerance_settings={"semantic_similarity": 0.75}
            )
            db.add(outcome2)
            
            # Step 3: Date and time
            step3 = ScenarioStep(
                script_id=restaurant_script.id,
                step_order=3,
                user_utterance="Tomorrow at 7 PM",
                step_metadata={"dialog_phase": "collecting", "slot_to_collect": "party_size"}
            )
            db.add(step3)
            await db.flush()
            
            outcome3 = ExpectedOutcome(
                outcome_code="RESERVATION_DATETIME",
                name="Date and Time Provided",
                scenario_step_id=step3.id,
                expected_command_kind="ClientMatchCommand",  # Custom command for datetime
                entities={"datetime": "tomorrow 7pm"},
                expected_response_content={"contains": ["how many", "people"]},
                tolerance_settings={"semantic_similarity": 0.75}
            )
            db.add(outcome3)
            
            await db.commit()
            
            logger.info("✅ Multi-turn scenarios seeded successfully!")
            logger.info(f"  - {restaurant_script.name} (3 steps)")
            
        except Exception as e:
            logger.error(f"❌ Seeding failed: {str(e)}", exc_info=True)
            await db.rollback()
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_multi_turn_data())

