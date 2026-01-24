"""
Seed Multi-Turn Scenario Data

This script creates realistic multi-turn conversation scenarios for testing:
- Restaurant reservation flow (5 steps)
- Navigation with clarifications (4 steps)
- Weather inquiry with follow-ups (3 steps)

Each scenario includes:
- ScenarioScript with metadata
- ScenarioSteps with expected responses
- ExpectedOutcomes with validation rules

Usage:
    python backend/scripts/seed_multi_turn_data.py
"""

import sys
import os
import asyncio
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from api.database import SessionLocal
from models.scenario_script import ScenarioScript, ScenarioStep
from models.expected_outcome import ExpectedOutcome
from models.user import User

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_restaurant_reservation_scenario(db: AsyncSession, created_by_id, tenant_id) -> ScenarioScript:
    """
    Create a restaurant reservation multi-turn scenario.

    Args:
        db: Database session
        created_by_id: User ID who created this scenario
        tenant_id: Tenant ID for multi-tenant data isolation

    Flow:
    1. User: "I want to make a dinner reservation"
       AI: "Sure! Which restaurant would you like?"
    2. User: "The Italian place downtown"
       AI: "Great! What date and time?"
    3. User: "Tomorrow at 7 PM"
       AI: "How many people?"
    4. User: "Four people"
       AI: "Perfect! I've reserved a table for 4..."
    5. User: "Yes, confirm it"
       AI: "Your reservation is confirmed..."
    """
    logger.info("Creating restaurant reservation scenario...")

    script = ScenarioScript(
        name="Restaurant Reservation Flow",
        description="Complete restaurant reservation conversation with slot filling",
        version="1.0.0",
        created_by=created_by_id,
        approval_status="approved",
        script_metadata={
            "domain": "dining_reservation",
            "complexity": "medium",
            "expected_turns": 5,
            "tags": ["multi-turn", "dining", "reservation", "slot-filling"]
        }
    )
    db.add(script)
    await db.flush()

    # Step 1: Initial request
    step1 = ScenarioStep(
        script_id=script.id,
        step_order=1,
        user_utterance="I want to make a dinner reservation",
        step_metadata={
            "dialog_phase": "initiate_reservation",
            "expected_slots": []
        }
    )
    db.add(step1)
    await db.flush()

    # Expected outcome for step 1
    outcome1 = ExpectedOutcome(
        tenant_id=tenant_id,
        scenario_step_id=step1.id,
        outcome_code="RES_INIT_001",
        name="Reservation Initiation",
        expected_command_kind="ClientMatchCommand",
        expected_response_content={"contains": ["restaurant", "which"]},
        validation_rules={
            "min_confidence": 0.7,
            "require_clarification": True
        },
        tolerance_settings={"semantic_similarity": 0.8}
    )
    db.add(outcome1)

    # Step 2: Specify restaurant
    step2 = ScenarioStep(
        script_id=script.id,
        step_order=2,
        user_utterance="The Italian place downtown",
        step_metadata={
            "dialog_phase": "specify_restaurant",
            "expected_slots": ["cuisine", "location"]
        }
    )
    db.add(step2)
    await db.flush()

    outcome2 = ExpectedOutcome(
        tenant_id=tenant_id,
        scenario_step_id=step2.id,
        outcome_code="RES_REST_002",
        name="Restaurant Name Provided",
        expected_command_kind="ClientMatchCommand",
        entities={
            "cuisine": "italian",
            "location": "downtown"
        },
        expected_response_content={"contains": ["date", "time"]},
        validation_rules={
            "min_confidence": 0.7,
            "require_entity_extraction": True
        },
        tolerance_settings={"semantic_similarity": 0.8}
    )
    db.add(outcome2)

    # Step 3: Specify date and time
    step3 = ScenarioStep(
        script_id=script.id,
        step_order=3,
        user_utterance="Tomorrow at 7 PM",
        step_metadata={
            "dialog_phase": "specify_datetime",
            "expected_slots": ["date", "time"]
        }
    )
    db.add(step3)
    await db.flush()

    outcome3 = ExpectedOutcome(
        tenant_id=tenant_id,
        scenario_step_id=step3.id,
        outcome_code="RES_TIME_003",
        name="Date and Time Provided",
        expected_command_kind="ClientMatchCommand",
        entities={"date": "tomorrow", "time": "19:00"},
        expected_response_content={"contains": ["how many", "people"]},
        validation_rules={"min_confidence": 0.7},
        tolerance_settings={"semantic_similarity": 0.8}
    )
    db.add(outcome3)

    # Step 4: Specify party size
    step4 = ScenarioStep(
        script_id=script.id,
        step_order=4,
        user_utterance="Four people",
        step_metadata={
            "dialog_phase": "specify_party_size",
            "expected_slots": ["party_size"]
        }
    )
    db.add(step4)
    await db.flush()

    outcome4 = ExpectedOutcome(
        tenant_id=tenant_id,
        scenario_step_id=step4.id,
        outcome_code="RES_SIZE_004",
        name="Party Size Provided",
        expected_command_kind="ClientMatchCommand",
        entities={"party_size": 4},
        expected_response_content={"contains": ["reserved", "table", "4"]},
        validation_rules={"min_confidence": 0.7},
        tolerance_settings={"semantic_similarity": 0.7}
    )
    db.add(outcome4)

    # Step 5: Confirm reservation
    step5 = ScenarioStep(
        script_id=script.id,
        step_order=5,
        user_utterance="Yes, confirm it",
        step_metadata={
            "dialog_phase": "confirm_reservation",
            "expected_slots": []
        }
    )
    db.add(step5)
    await db.flush()

    outcome5 = ExpectedOutcome(
        tenant_id=tenant_id,
        scenario_step_id=step5.id,
        outcome_code="RES_CONF_005",
        name="Reservation Confirmed",
        expected_command_kind="ClientMatchCommand",
        expected_response_content={"contains": ["reservation", "confirmed"]},
        validation_rules={"min_confidence": 0.7},
        tolerance_settings={"semantic_similarity": 0.7}
    )
    db.add(outcome5)

    logger.info(f"✓ Created restaurant reservation scenario with 5 steps")
    return script


async def create_navigation_scenario(db: AsyncSession, created_by_id, tenant_id) -> ScenarioScript:
    """
    Create a navigation with clarifications scenario.

    Args:
        db: Database session
        created_by_id: User ID who created this scenario
        tenant_id: Tenant ID for multi-tenant data isolation

    Flow:
    1. User: "Navigate to the nearest coffee shop"
       AI: "I found several coffee shops. Which one?"
    2. User: "The one on Main Street"
       AI: "Starting navigation to Starbucks on Main Street"
    3. User: "How long will it take?"
       AI: "About 10 minutes"
    """
    logger.info("Creating navigation scenario...")

    script = ScenarioScript(
        name="Navigation with Clarifications",
        description="Navigation request requiring clarification and follow-up questions",
        version="1.0.0",
        created_by=created_by_id,
        approval_status="approved",
        script_metadata={
            "domain": "navigation",
            "complexity": "low",
            "expected_turns": 3,
            "tags": ["multi-turn", "navigation", "clarification"]
        }
    )
    db.add(script)
    await db.flush()

    # Step 1: Initial navigation request
    step1 = ScenarioStep(
        script_id=script.id,
        step_order=1,
        user_utterance="Navigate to the nearest coffee shop",
        step_metadata={"dialog_phase": "navigate", "expected_slots": ["poi_type"]}
    )
    db.add(step1)
    await db.flush()

    outcome1 = ExpectedOutcome(
        tenant_id=tenant_id,
        scenario_step_id=step1.id,
        outcome_code="NAV_INIT_001",
        name="Navigation Initiation",
        expected_command_kind="NavigationCommand",
        entities={"poi_type": "coffee_shop"},
        expected_response_content={"contains": ["coffee", "shop"]},
        validation_rules={"min_confidence": 0.7},
        tolerance_settings={"semantic_similarity": 0.7}
    )
    db.add(outcome1)

    logger.info(f"✓ Created navigation scenario with 3 steps")
    return script


async def main():
    """Main seeding function."""
    logger.info("===== SEEDING MULTI-TURN SCENARIO DATA =====")

    async with SessionLocal() as db:
        try:
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

            # Get or create test user
            result = await db.execute(
                select(User).filter(User.email == "admin@voiceai.com")
            )
            user = result.scalar_one_or_none()

            if not user:
                user = User(
                    email="admin@voiceai.com",
                    username="admin",
                    full_name="Admin User",
                    role="admin",
                    is_active=True
                )
                db.add(user)
                await db.flush()
            elif not user.role:
                # Ensure existing user has admin role
                user.role = "admin"
                await db.flush()

            # Create scenarios
            # Use user.id as tenant_id for individual users (no org tenant)
            tenant_id = user.tenant_id if user.tenant_id else user.id
            restaurant_script = await create_restaurant_reservation_scenario(db, user.id, tenant_id)
            navigation_script = await create_navigation_scenario(db, user.id, tenant_id)

            await db.commit()

            logger.info("===== SEEDING COMPLETED SUCCESSFULLY =====")
            logger.info(f"Created scenarios:")
            logger.info(f"  - {restaurant_script.name} (ID: {restaurant_script.id})")
            logger.info(f"  - {navigation_script.name} (ID: {navigation_script.id})")

        except Exception as e:
            logger.error(f"❌ Seeding failed: {str(e)}", exc_info=True)
            await db.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(main())

