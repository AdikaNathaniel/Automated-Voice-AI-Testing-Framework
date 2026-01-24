#!/usr/bin/env python3
"""
Unified seed script for all initial data.

This script creates:
1. Super admin user (platform-wide access, no organization)
2. Demo organization with an org_admin user
3. Demo scenarios belonging to the demo organization

Multi-tenancy model:
- super_admin: role="super_admin", tenant_id=None, is_organization_owner=False
- org_admin: role="org_admin", tenant_id=None, is_organization_owner=True
  (their user.id becomes the tenant_id for all org data)
- org members: tenant_id=org_admin.id

Usage:
    cd backend
    python -m scripts.seed_all

Environment Variables:
    SUPER_ADMIN_EMAIL - Email for super admin (default: admin@voiceai.local)
    SUPER_ADMIN_USERNAME - Username for super admin (default: superadmin)
    SUPER_ADMIN_PASSWORD - Password for super admin (default: SuperAdmin123!)
    DATABASE_URL - Database connection string
"""

from __future__ import annotations

import asyncio
import os
import sys
from uuid import uuid4

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from api.config import get_settings
from api.auth.password import hash_password
from models.user import User
from models.scenario_script import ScenarioScript, ScenarioStep
from models.expected_outcome import ExpectedOutcome


# Default credentials
DEFAULT_SUPER_ADMIN_EMAIL = "admin@voiceai.dev"
DEFAULT_SUPER_ADMIN_USERNAME = "superadmin"
DEFAULT_SUPER_ADMIN_PASSWORD = "SuperAdmin123!"

DEFAULT_DEMO_ORG_NAME = "Demo Organization"
DEFAULT_DEMO_ORG_EMAIL = "demo@voiceai.dev"
DEFAULT_DEMO_ORG_USERNAME = "demo_admin"
DEFAULT_DEMO_ORG_PASSWORD = "DemoAdmin123!"


async def seed_super_admin(db: AsyncSession) -> User | None:
    """Create the super admin user if it doesn't exist.

    Super admin is platform-wide and doesn't belong to any organization.

    Returns:
        The super admin User object, or None on error.
    """
    email = os.getenv("SUPER_ADMIN_EMAIL", DEFAULT_SUPER_ADMIN_EMAIL)
    username = os.getenv("SUPER_ADMIN_USERNAME", DEFAULT_SUPER_ADMIN_USERNAME)
    password = os.getenv("SUPER_ADMIN_PASSWORD", DEFAULT_SUPER_ADMIN_PASSWORD)

    # Check if super admin already exists
    result = await db.execute(
        select(User).where(User.role == "super_admin")
    )
    existing = result.scalar_one_or_none()

    if existing:
        print(f"  Super admin already exists: {existing.email}")
        return existing

    # Also check by email/username
    result = await db.execute(
        select(User).where(
            (User.email == email) | (User.username == username)
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        print(f"  User with email/username already exists: {existing.email}")
        if existing.role != "super_admin":
            existing.role = "super_admin"
            await db.flush()
            print(f"  Updated {existing.email} to super_admin role")
        return existing

    # Create new super admin
    super_admin = User(
        id=uuid4(),
        email=email,
        username=username,
        password_hash=hash_password(password),
        full_name="Super Administrator",
        role="super_admin",
        is_active=True,
        is_organization_owner=False,
        tenant_id=None,
    )

    db.add(super_admin)
    await db.flush()
    await db.refresh(super_admin)

    print("=" * 60)
    print("  Super Admin Created Successfully!")
    print("=" * 60)
    print(f"    Email:    {email}")
    print(f"    Username: {username}")
    print(f"    Password: {password}")
    print(f"    User ID:  {super_admin.id}")
    print("=" * 60)
    print("  Access admin console at: /admin")
    print()

    return super_admin


async def seed_demo_organization(db: AsyncSession) -> User | None:
    """Create the demo organization if it doesn't exist.

    The organization owner (org_admin) user represents the organization.
    Their user.id becomes the tenant_id for all org data.

    Returns:
        The demo organization User object (org_admin), or None on error.
    """
    org_name = os.getenv("DEMO_ORG_NAME", DEFAULT_DEMO_ORG_NAME)
    email = os.getenv("DEMO_ORG_EMAIL", DEFAULT_DEMO_ORG_EMAIL)
    username = os.getenv("DEMO_ORG_USERNAME", DEFAULT_DEMO_ORG_USERNAME)
    password = os.getenv("DEMO_ORG_PASSWORD", DEFAULT_DEMO_ORG_PASSWORD)

    # Check if demo org already exists
    result = await db.execute(
        select(User).where(User.organization_name == org_name)
    )
    existing = result.scalar_one_or_none()

    if existing:
        print(f"  Demo organization already exists: {existing.organization_name}")
        return existing

    # Also check by email/username
    result = await db.execute(
        select(User).where(
            (User.email == email) | (User.username == username)
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        print(f"  User with email/username already exists: {existing.email}")
        return existing

    # Create demo organization (as org_admin user)
    demo_org = User(
        id=uuid4(),
        email=email,
        username=username,
        password_hash=hash_password(password),
        full_name="Demo Organization Admin",
        role="org_admin",
        is_active=True,
        is_organization_owner=True,
        organization_name=org_name,
        organization_settings={},
        tenant_id=None,  # Org owners don't have tenant_id
    )

    db.add(demo_org)
    await db.flush()
    await db.refresh(demo_org)

    print("=" * 60)
    print("  Demo Organization Created Successfully!")
    print("=" * 60)
    print(f"    Organization: {org_name}")
    print(f"    Admin Email:  {email}")
    print(f"    Username:     {username}")
    print(f"    Password:     {password}")
    print(f"    Org ID:       {demo_org.id}")
    print("=" * 60)
    print("  This org admin can log in and see demo scenarios.")
    print()

    return demo_org


async def seed_demo_scenarios(db: AsyncSession, org_id, created_by_id) -> None:
    """Seed comprehensive test scenarios for the demo organization.

    Creates 20 scenarios covering:
    - Demo scenarios (3)
    - Houndify validation tests (8)
    - Multi-language scenarios (4)
    - Regex validation tests (3)
    - LLM & Hybrid tests (2)

    Args:
        db: Database session
        org_id: The organization's ID (tenant_id for all data)
        created_by_id: The user ID who "created" the scenarios
    """
    from models.expected_outcome import ExpectedOutcome
    from models.scenario_script import ScenarioStep

    # Check if scenarios have already been seeded
    result = await db.execute(
        select(ScenarioScript).where(
            ScenarioScript.tenant_id == org_id
        )
    )
    existing = list(result.scalars().all())

    if len(existing) >= 20:  # We create 20 scenarios total
        print(f"  Demo scenarios already exist ({len(existing)} found), skipping...")
        return

    # Delete existing scenarios if any (to allow re-seeding)
    if existing:
        print(f"  Found {len(existing)} existing scenarios, cleaning up for re-seed...")

        # Use raw SQL to ensure deletion works
        from sqlalchemy import text

        # Delete ExpectedOutcome records
        await db.execute(
            text("DELETE FROM expected_outcomes WHERE tenant_id = :tenant_id"),
            {"tenant_id": str(org_id)}
        )
        print(f"    Deleted ExpectedOutcome records for tenant {org_id}")

        # Delete ScenarioStep records (cascade from ScenarioScript won't work if done via SQL)
        await db.execute(
            text("""
                DELETE FROM scenario_steps
                WHERE script_id IN (
                    SELECT id FROM scenario_scripts WHERE tenant_id = :tenant_id
                )
            """),
            {"tenant_id": str(org_id)}
        )
        print(f"    Deleted ScenarioStep records")

        # Delete ScenarioScript records
        await db.execute(
            text("DELETE FROM scenario_scripts WHERE tenant_id = :tenant_id"),
            {"tenant_id": str(org_id)}
        )
        print(f"    Deleted ScenarioScript records")

        await db.commit()  # Commit all deletions

    print("  Creating 20 comprehensive test scenarios...")

    # ========================================================================
    # DEMO SCENARIOS (3)
    # ========================================================================

    # === Demo 1: Single-step Weather Query (EN only) ===
    weather_script = ScenarioScript(
        name="Demo: Weather Query",
        description="Simple weather query - single turn scenario (English only)",
        is_active=True,
        created_by=created_by_id,
        tenant_id=org_id,
        validation_mode="hybrid",
        script_metadata={
            "category": "weather",
            "priority": "medium",
            "tags": ["demo", "weather", "single-turn"],
            "demo": True,
            "difficulty": "easy"
        }
    )
    db.add(weather_script)
    await db.flush()

    weather_step = ScenarioStep(
        script_id=weather_script.id,
        step_order=1,
        user_utterance="What's the weather like today?",
        step_metadata={
            "expected_intent": "GetWeather",
            "expected_entities": {"time": "today"},
            "description": "User asks about current weather",
            "language_code": "en-US"
        }
    )
    db.add(weather_step)
    await db.flush()

    weather_outcome = ExpectedOutcome(
        tenant_id=org_id,
        scenario_step_id=weather_step.id,
        outcome_code="DEMO_WEATHER_QUERY",
        name="Weather Query Expected Outcome",
        description="Expected outcome for weather query",
        expected_command_kind="WeatherCommand",  # FIXED: Was WeatherQuery
        expected_response_content={"contains": ["weather", "temperature"]},
        expected_asr_confidence_min=0.7,
        validation_rules={"min_confidence": 0.7},
        entities={"time": "today"}
    )
    db.add(weather_outcome)

    # === Demo 2: Multi-turn Restaurant Reservation (with multi-language) ===
    restaurant_script = ScenarioScript(
        name="Demo: Restaurant Reservation (Multi-Language)",
        description="Multi-turn restaurant reservation flow with language variants",
        is_active=True,
        created_by=created_by_id,
        tenant_id=org_id,
        validation_mode="hybrid",
        script_metadata={
            "category": "reservation",
            "priority": "high",
            "tags": ["demo", "reservation", "multi-turn", "multi-language"],
            "demo": True,
            "difficulty": "medium",
            "language": "multi",
            "supported_languages": ["en-US", "es-ES", "fr-FR"]
        }
    )
    db.add(restaurant_script)
    await db.flush()

    # Step 1: Initial request (with language variations in step metadata)
    res_step1 = ScenarioStep(
        script_id=restaurant_script.id,
        step_order=1,
        user_utterance="I want to make a dinner reservation",
        step_metadata={
            "expected_intent": "StartReservation",
            "description": "User initiates reservation",
            "primary_language": "en-US",
            "language_code": "en-US",
            "language_variants": [
                {
                    "language_code": "en-US",
                    "user_utterance": "I want to make a dinner reservation"
                },
                {
                    "language_code": "es-ES",
                    "user_utterance": "Quiero hacer una reserva para cenar"
                },
                {
                    "language_code": "fr-FR",
                    "user_utterance": "Je veux faire une réservation pour dîner"
                }
            ]
        }
    )
    db.add(res_step1)
    await db.flush()

    res_step1_outcome = ExpectedOutcome(
        tenant_id=org_id,
        scenario_step_id=res_step1.id,
        outcome_code="DEMO_RES_STEP1",
        name="Restaurant Reservation Step 1",
        description="Initial reservation request with language variants",
        expected_command_kind="ClientMatchCommand",  # FIXED: Was RestaurantReservationCommand
        expected_response_content={"contains": ["restaurant"]},
        expected_asr_confidence_min=0.7,
        validation_rules={"min_confidence": 0.7},
        language_variations={
            "en-US": {
                "user_utterance": "I want to make a dinner reservation",
                "expected_response_patterns": {
                    "contains": ["restaurant"]
                }
            },
            "es-ES": {
                "user_utterance": "Quiero hacer una reserva para cenar",
                "expected_response_patterns": {
                    "contains": ["restaurante"]
                }
            },
            "fr-FR": {
                "user_utterance": "Je veux faire une réservation pour dîner",
                "expected_response_patterns": {
                    "contains": ["restaurant"]
                }
            }
        }
    )
    db.add(res_step1_outcome)

    # Step 2: Restaurant selection
    res_step2 = ScenarioStep(
        script_id=restaurant_script.id,
        step_order=2,
        user_utterance="Italian restaurant please",
        step_metadata={
            "expected_intent": "SelectCuisine",
            "expected_entities": {"cuisine": "italian"},
            "description": "User specifies cuisine type",
            "language_code": "en-US",
            "primary_language": "en-US",
            "language_variants": [
                {
                    "language_code": "en-US",
                    "user_utterance": "Italian restaurant please"
                },
                {
                    "language_code": "es-ES",
                    "user_utterance": "Restaurante italiano por favor"
                },
                {
                    "language_code": "fr-FR",
                    "user_utterance": "Restaurant italien sil vous plaît"
                }
            ]
        }
    )
    db.add(res_step2)
    await db.flush()

    res_step2_outcome = ExpectedOutcome(
        tenant_id=org_id,
        scenario_step_id=res_step2.id,
        outcome_code="DEMO_RES_STEP2",
        name="Restaurant Reservation Step 2",
        description="Cuisine selection",
        expected_command_kind="ClientMatchCommand",
        expected_response_content={"contains": ["italian"]},
        expected_asr_confidence_min=0.7,
        validation_rules={"min_confidence": 0.7},
        language_variations={
            "en-US": {
                "user_utterance": "Italian restaurant please",
                "expected_response_patterns": {
                    "contains": ["date"]
                }
            },
            "es-ES": {
                "user_utterance": "Restaurante italiano por favor",
                "expected_response_patterns": {
                    "contains": ["fecha"]
                }
            },
            "fr-FR": {
                "user_utterance": "Restaurant italien sil vous plaît",
                "expected_response_patterns": {
                    "contains": ["date"]
                }
            }
        }
    )
    db.add(res_step2_outcome)

    # Step 3: Time and party size
    res_step3 = ScenarioStep(
        script_id=restaurant_script.id,
        step_order=3,
        user_utterance="Tomorrow at 7pm for 4 people",
        step_metadata={
            "expected_intent": "SetReservationDetails",
            "expected_entities": {"time": "7pm", "date": "tomorrow", "party_size": "4"},
            "description": "User provides reservation details",
            "language_code": "en-US",
            "primary_language": "en-US",
            "language_variants": [
                {
                    "language_code": "en-US",
                    "user_utterance": "Tomorrow at 7pm for 4 people"
                },
                {
                    "language_code": "es-ES",
                    "user_utterance": "Mañana a las 7pm para 4 personas"
                },
                {
                    "language_code": "fr-FR",
                    "user_utterance": "Demain à 19h pour 4 personnes"
                }
            ]
        }
    )
    db.add(res_step3)
    await db.flush()

    res_step3_outcome = ExpectedOutcome(
        tenant_id=org_id,
        scenario_step_id=res_step3.id,
        outcome_code="DEMO_RES_STEP3",
        name="Restaurant Reservation Step 3",
        description="Datetime and party size",
        expected_command_kind="ClientMatchCommand",
        expected_response_content={"contains": ["tomorrow", "7", "4", "people"]},
        expected_asr_confidence_min=0.7,
        validation_rules={"min_confidence": 0.7},
        language_variations={
            "en-US": {
                "user_utterance": "Tomorrow at 7pm for 4 people",
                "expected_response_patterns": {
                    "contains": ["table"]
                }
            },
            "es-ES": {
                "user_utterance": "Mañana a las 7pm para 4 personas",
                "expected_response_patterns": {
                    "contains": ["mesa"]
                }
            },
            "fr-FR": {
                "user_utterance": "Demain à 19h pour 4 personnes",
                "expected_response_patterns": {
                    "contains": ["table"]
                }
            }
        }
    )
    db.add(res_step3_outcome)

    # === Demo 3: Smart Home Control ===
    smarthome_script = ScenarioScript(
        name="Demo: Smart Home Control",
        description="Smart home device control scenario (ClientMatchCommand)",
        is_active=True,
        created_by=created_by_id,
        tenant_id=org_id,
        validation_mode="hybrid",
        script_metadata={
            "category": "smart_home",
            "priority": "medium",
            "tags": ["demo", "smart-home", "single-turn"],
            "demo": True,
            "difficulty": "easy"
        }
    )
    db.add(smarthome_script)
    await db.flush()

    smarthome_step = ScenarioStep(
        script_id=smarthome_script.id,
        step_order=1,
        user_utterance="Turn on the living room lights",
        step_metadata={
            "expected_intent": "ControlDevice",
            "expected_entities": {"device": "lights", "location": "living room", "action": "on"},
            "description": "User controls smart home device",
            "language_code": "en-US"
        }
    )
    db.add(smarthome_step)
    await db.flush()

    smarthome_outcome = ExpectedOutcome(
        tenant_id=org_id,
        scenario_step_id=smarthome_step.id,
        outcome_code="DEMO_SMART_HOME_CONTROL",
        name="Smart Home Control Expected Outcome",
        description="Expected outcome for smart home control",
        expected_command_kind="ClientMatchCommand",  # FIXED: Was SmartHomeCommand
        expected_response_content={"contains": ["lights", "living room"]},
        expected_asr_confidence_min=0.7,
        validation_rules={"min_confidence": 0.7},
        entities={"device": "lights", "location": "living room", "action": "on"}
    )
    db.add(smarthome_outcome)

    # ========================================================================
    # HOUNDIFY VALIDATION TESTS (8)
    # ========================================================================

    # === Test 4: CommandKind Match - PASS (WeatherCommand) ===
    test4_script = ScenarioScript(
        name="Test: CommandKind Match PASS",
        description="Weather query matching WeatherCommand - should PASS",
        is_active=True,
        created_by=created_by_id,
        tenant_id=org_id,
        validation_mode="hybrid",
        script_metadata={
            "category": "other",
            "priority": "high",
            "tags": ["test", "houndify", "pass", "command-kind"],
            "expected_result": "pass"
        }
    )
    db.add(test4_script)
    await db.flush()

    test4_step = ScenarioStep(
        script_id=test4_script.id,
        step_order=1,
        user_utterance="What's the weather forecast for tomorrow?",
        step_metadata={
            "description": "Weather query that should match WeatherCommand",
            "validation_type": "houndify_command_kind",
            "language_code": "en-US"
        }
    )
    db.add(test4_step)
    await db.flush()

    test4_outcome = ExpectedOutcome(
        tenant_id=org_id,
        scenario_step_id=test4_step.id,
        outcome_code="TEST_COMMAND_KIND_PASS",
        name="CommandKind Match Test (PASS)",
        description="Expected to PASS - weather query matches WeatherCommand",
        expected_command_kind="WeatherCommand",  # Correct - matches mock client
        expected_asr_confidence_min=0.7,
        expected_response_content={
            "contains": ["weather", "temperature"]
        },
        validation_rules={"min_confidence": 0.7}
    )
    db.add(test4_outcome)

    # === Test 5: CommandKind Mismatch - FAIL (Music expecting Weather) ===
    test5_script = ScenarioScript(
        name="Test: CommandKind Mismatch FAIL",
        description="Music query expecting WeatherCommand - should FAIL",
        is_active=True,
        created_by=created_by_id,
        tenant_id=org_id,
        validation_mode="hybrid",
        script_metadata={
            "category": "other",
            "priority": "high",
            "tags": ["test", "houndify", "fail", "command-kind"],
            "expected_result": "fail"
        }
    )
    db.add(test5_script)
    await db.flush()

    test5_step = ScenarioStep(
        script_id=test5_script.id,
        step_order=1,
        user_utterance="Play some music",
        step_metadata={
            "description": "Music command expecting wrong CommandKind (should fail)",
            "validation_type": "houndify_command_kind",
            "language_code": "en-US"
        }
    )
    db.add(test5_step)
    await db.flush()

    test5_outcome = ExpectedOutcome(
        tenant_id=org_id,
        scenario_step_id=test5_step.id,
        outcome_code="TEST_COMMAND_KIND_FAIL",
        name="CommandKind Mismatch Test (FAIL)",
        description="Expected to FAIL - returns MusicCommand but expecting WeatherCommand",
        expected_command_kind="WeatherCommand",  # Wrong - will get MusicCommand instead
        expected_asr_confidence_min=0.7,
        validation_rules={"min_confidence": 0.7}
    )
    db.add(test5_outcome)

    # === Test 6: NoResultCommand - FAIL (Gibberish expecting Weather) ===
    test6_script = ScenarioScript(
        name="Test: NoResultCommand FAIL",
        description="Gibberish query expecting WeatherCommand - should FAIL",
        is_active=True,
        created_by=created_by_id,
        tenant_id=org_id,
        validation_mode="hybrid",
        script_metadata={
            "category": "other",
            "priority": "high",
            "tags": ["test", "houndify", "fail", "no-result"],
            "expected_result": "fail"
        }
    )
    db.add(test6_script)
    await db.flush()

    test6_step = ScenarioStep(
        script_id=test6_script.id,
        step_order=1,
        user_utterance="asdfghjkl qwertyuiop zxcvbnm",
        step_metadata={
            "description": "Gibberish input expecting WeatherCommand (should fail)",
            "validation_type": "houndify_command_kind",
            "language_code": "en-US"
        }
    )
    db.add(test6_step)
    await db.flush()

    test6_outcome = ExpectedOutcome(
        tenant_id=org_id,
        scenario_step_id=test6_step.id,
        outcome_code="TEST_NO_RESULT_FAIL",
        name="NoResultCommand Test (FAIL)",
        description="Expected to FAIL - returns NoResultCommand but expecting WeatherCommand",
        expected_command_kind="WeatherCommand",  # Wrong - will get NoResultCommand instead
        expected_asr_confidence_min=0.7,
        validation_rules={"min_confidence": 0.7}
    )
    db.add(test6_outcome)

    # === Test 7: Response Content Contains - PASS ===
    test7_script = ScenarioScript(
        name="Test: Response Content Contains PASS",
        description="Weather query with 'contains' validation - should PASS",
        is_active=True,
        created_by=created_by_id,
        tenant_id=org_id,
        validation_mode="hybrid",
        script_metadata={
            "category": "other",
            "priority": "high",
            "tags": ["test", "houndify", "pass", "response-content", "contains"],
            "expected_result": "pass"
        }
    )
    db.add(test7_script)
    await db.flush()

    test7_step = ScenarioStep(
        script_id=test7_script.id,
        step_order=1,
        user_utterance="What's the weather today?",
        step_metadata={
            "description": "Weather query checking response contains specific words",
            "validation_type": "houndify_response_content",
            "language_code": "en-US"
        }
    )
    db.add(test7_step)
    await db.flush()

    test7_outcome = ExpectedOutcome(
        tenant_id=org_id,
        scenario_step_id=test7_step.id,
        outcome_code="TEST_RESPONSE_CONTENT_PASS",
        name="Response Content Contains Test (PASS)",
        description="Expected to PASS - response contains weather, temperature, degrees",
        expected_command_kind="WeatherCommand",
        expected_response_content={
            "contains": ["weather", "temperature", "degrees"]
        },
        expected_asr_confidence_min=0.7,
        validation_rules={"min_confidence": 0.7}
    )
    db.add(test7_outcome)

    # === Test 8: Response Content Wrong Contains - FAIL ===
    test8_script = ScenarioScript(
        name="Test: Response Content Wrong Contains FAIL",
        description="Weather query expecting wrong content words - should FAIL",
        is_active=True,
        created_by=created_by_id,
        tenant_id=org_id,
        validation_mode="hybrid",
        script_metadata={
            "category": "other",
            "priority": "high",
            "tags": ["test", "houndify", "fail", "response-content"],
            "expected_result": "fail"
        }
    )
    db.add(test8_script)
    await db.flush()

    test8_step = ScenarioStep(
        script_id=test8_script.id,
        step_order=1,
        user_utterance="What's the weather like?",
        step_metadata={
            "description": "Weather query expecting music-related words (should fail)",
            "validation_type": "houndify_response_content",
            "language_code": "en-US"
        }
    )
    db.add(test8_step)
    await db.flush()

    test8_outcome = ExpectedOutcome(
        tenant_id=org_id,
        scenario_step_id=test8_step.id,
        outcome_code="TEST_RESPONSE_CONTENT_FAIL",
        name="Response Content Wrong Contains Test (FAIL)",
        description="Expected to FAIL - weather response won't contain 'music' or 'playing'",
        expected_command_kind="WeatherCommand",
        expected_response_content={
            "contains": ["music", "playing", "song"]  # Wrong - weather response won't have these
        },
        expected_asr_confidence_min=0.7,
        validation_rules={"min_confidence": 0.7}
    )
    db.add(test8_outcome)

    # === Test 9: Music Response with Regex - PASS ===
    test9_script = ScenarioScript(
        name="Test: Music Regex PASS",
        description="Music query with regex validation - should PASS",
        is_active=True,
        created_by=created_by_id,
        tenant_id=org_id,
        validation_mode="hybrid",
        script_metadata={
            "category": "other",
            "priority": "high",
            "tags": ["test", "houndify", "pass", "response-content", "regex"],
            "expected_result": "pass"
        }
    )
    db.add(test9_script)
    await db.flush()

    test9_step = ScenarioStep(
        script_id=test9_script.id,
        step_order=1,
        user_utterance="Play some jazz music",
        step_metadata={
            "description": "Music query with regex pattern validation",
            "validation_type": "houndify_response_content",
            "language_code": "en-US"
        }
    )
    db.add(test9_step)
    await db.flush()

    test9_outcome = ExpectedOutcome(
        tenant_id=org_id,
        scenario_step_id=test9_step.id,
        outcome_code="TEST_MUSIC_REGEX_PASS",
        name="Music Regex Test (PASS)",
        description="Expected to PASS - response matches 'Playing.*music' regex",
        expected_command_kind="MusicCommand",
        expected_response_content={
            "regex": ["Playing.*music", "jazz"]
        },
        expected_asr_confidence_min=0.7,
        validation_rules={"min_confidence": 0.7}
    )
    db.add(test9_outcome)

    # === Test 10: Normal ASR Confidence - PASS ===
    test10_script = ScenarioScript(
        name="Test: Normal ASR Confidence PASS",
        description="Normal ASR confidence check - should PASS",
        is_active=True,
        created_by=created_by_id,
        tenant_id=org_id,
        validation_mode="hybrid",
        script_metadata={
            "category": "other",
            "priority": "high",
            "tags": ["test", "houndify", "pass", "asr-confidence"],
            "expected_result": "pass"
        }
    )
    db.add(test10_script)
    await db.flush()

    test10_step = ScenarioStep(
        script_id=test10_script.id,
        step_order=1,
        user_utterance="What's the weather like?",
        step_metadata={
            "description": "Clear audio with normal confidence threshold",
            "validation_type": "houndify_asr_confidence",
            "language_code": "en-US"
        }
    )
    db.add(test10_step)
    await db.flush()

    test10_outcome = ExpectedOutcome(
        tenant_id=org_id,
        scenario_step_id=test10_step.id,
        outcome_code="TEST_ASR_CONFIDENCE_PASS",
        name="Normal ASR Confidence Test (PASS)",
        description="Expected to PASS - mock returns 0.95, threshold is 0.7",
        expected_command_kind="WeatherCommand",
        expected_asr_confidence_min=0.7,  # Mock always returns 0.95
        validation_rules={"min_confidence": 0.7}
    )
    db.add(test10_outcome)

    # === Test 11: High ASR Confidence Threshold - FAIL ===
    test11_script = ScenarioScript(
        name="Test: High ASR Confidence Threshold FAIL",
        description="ASR confidence validation with unrealistic threshold - should FAIL",
        is_active=True,
        created_by=created_by_id,
        tenant_id=org_id,
        validation_mode="hybrid",
        script_metadata={
            "category": "other",
            "priority": "high",
            "tags": ["test", "houndify", "fail", "asr-confidence"],
            "expected_result": "fail"
        }
    )
    db.add(test11_script)
    await db.flush()

    test11_step = ScenarioStep(
        script_id=test11_script.id,
        step_order=1,
        user_utterance="What's the weather forecast?",
        step_metadata={
            "description": "Normal query but expecting unrealistically high confidence (should fail)",
            "validation_type": "houndify_asr_confidence",
            "language_code": "en-US"
        }
    )
    db.add(test11_step)
    await db.flush()

    test11_outcome = ExpectedOutcome(
        tenant_id=org_id,
        scenario_step_id=test11_step.id,
        outcome_code="TEST_ASR_HIGH_THRESHOLD_FAIL",
        name="High ASR Confidence Threshold Test (FAIL)",
        description="Expected to FAIL - mock returns 0.95 but threshold is 0.99",
        expected_command_kind="WeatherCommand",
        expected_asr_confidence_min=0.99,  # Too high - mock returns 0.95
        validation_rules={"min_confidence": 0.99}
    )
    db.add(test11_outcome)

    # ========================================================================
    # MULTI-LANGUAGE SCENARIOS (4)
    # ========================================================================

    # === Test 12: Spanish Weather Query ===
    test12_script = ScenarioScript(
        name="Test: Spanish Weather Query",
        description="Weather query in Spanish (es-ES)",
        is_active=True,
        created_by=created_by_id,
        tenant_id=org_id,
        validation_mode="hybrid",
        script_metadata={
            "category": "other",
            "priority": "high",
            "tags": ["test", "multi-language", "spanish", "weather"],
            "expected_result": "pass",
            "language": "es-ES",
            "supported_languages": ["es-ES"]
        }
    )
    db.add(test12_script)
    await db.flush()

    test12_step = ScenarioStep(
        script_id=test12_script.id,
        step_order=1,
        user_utterance="¿Cómo está el tiempo hoy?",
        step_metadata={
            "description": "Spanish weather query",
            "language_code": "es-ES",
            "primary_language": "es-ES",
            "language_variants": [
                {
                    "language_code": "es-ES",
                    "user_utterance": "¿Cómo está el tiempo hoy?"
                }
            ]
        }
    )
    db.add(test12_step)
    await db.flush()

    test12_outcome = ExpectedOutcome(
        tenant_id=org_id,
        scenario_step_id=test12_step.id,
        outcome_code="TEST_SPANISH_WEATHER",
        name="Spanish Weather Test",
        description="Spanish weather query with language variations",
        expected_command_kind="WeatherCommand",
        expected_response_content={"contains": ["clima", "temperatura"]},
        expected_asr_confidence_min=0.7,
        validation_rules={"min_confidence": 0.7},
        language_variations={
            "es-ES": {
                "user_utterance": "¿Cómo está el tiempo hoy?",
                "expected_response_patterns": {
                    "contains": ["clima", "temperatura", "grados"]
                }
            }
        }
    )
    db.add(test12_outcome)

    # === Test 13: French Weather Query ===
    test13_script = ScenarioScript(
        name="Test: French Weather Query",
        description="Weather query in French (fr-FR)",
        is_active=True,
        created_by=created_by_id,
        tenant_id=org_id,
        validation_mode="hybrid",
        script_metadata={
            "category": "other",
            "priority": "high",
            "tags": ["test", "multi-language", "french", "weather"],
            "expected_result": "pass",
            "language": "fr-FR",
            "supported_languages": ["fr-FR"]
        }
    )
    db.add(test13_script)
    await db.flush()

    test13_step = ScenarioStep(
        script_id=test13_script.id,
        step_order=1,
        user_utterance="Quel temps fait-il aujourd'hui?",
        step_metadata={
            "description": "French weather query",
            "language_code": "fr-FR",
            "primary_language": "fr-FR",
            "language_variants": [
                {
                    "language_code": "fr-FR",
                    "user_utterance": "Quel temps fait-il aujourd'hui?"
                }
            ]
        }
    )
    db.add(test13_step)
    await db.flush()

    test13_outcome = ExpectedOutcome(
        tenant_id=org_id,
        scenario_step_id=test13_step.id,
        outcome_code="TEST_FRENCH_WEATHER",
        name="French Weather Test",
        description="French weather query with language variations",
        expected_command_kind="WeatherCommand",
        expected_response_content={"contains": ["météo", "température"]},
        expected_asr_confidence_min=0.7,
        validation_rules={"min_confidence": 0.7},
        language_variations={
            "fr-FR": {
                "user_utterance": "Quel temps fait-il aujourd'hui?",
                "expected_response_patterns": {
                    "contains": ["météo", "température", "degrés"]
                }
            }
        }
    )
    db.add(test13_outcome)

    # === Test 14: Multi-Language Single Step ===
    test14_script = ScenarioScript(
        name="Test: Multi-Language Single Step",
        description="Single step with EN/ES/FR variants in language_variations",
        is_active=True,
        created_by=created_by_id,
        tenant_id=org_id,
        validation_mode="hybrid",
        script_metadata={
            "category": "other",
            "priority": "high",
            "tags": ["test", "multi-language", "variants"],
            "expected_result": "pass",
            "language": "multi",
            "supported_languages": ["en-US", "es-ES", "fr-FR"]
        }
    )
    db.add(test14_script)
    await db.flush()

    test14_step = ScenarioStep(
        script_id=test14_script.id,
        step_order=1,
        user_utterance="What's the weather like today?",
        step_metadata={
            "description": "Weather query with three language variants",
            "primary_language": "en-US",
            "language_code": "en-US",
            "language_variants": [
                {
                    "language_code": "en-US",
                    "user_utterance": "What's the weather like today?"
                },
                {
                    "language_code": "es-ES",
                    "user_utterance": "¿Cómo está el tiempo hoy?"
                },
                {
                    "language_code": "fr-FR",
                    "user_utterance": "Quel temps fait-il aujourd'hui?"
                }
            ]
        }
    )
    db.add(test14_step)
    await db.flush()

    test14_outcome = ExpectedOutcome(
        tenant_id=org_id,
        scenario_step_id=test14_step.id,
        outcome_code="TEST_MULTI_LANG_SINGLE_STEP",
        name="Multi-Language Single Step Test",
        description="Single step with EN/ES/FR variants",
        expected_command_kind="WeatherCommand",
        expected_response_content={"contains": ["weather", "temperature"]},
        expected_asr_confidence_min=0.7,
        validation_rules={"min_confidence": 0.7},
        language_variations={
            "en-US": {
                "user_utterance": "What's the weather like today?",
                "expected_response_patterns": {
                    "contains": ["weather", "temperature", "degrees"]
                }
            },
            "es-ES": {
                "user_utterance": "¿Cómo está el tiempo hoy?",
                "expected_response_patterns": {
                    "contains": ["clima", "temperatura", "grados"]
                }
            },
            "fr-FR": {
                "user_utterance": "Quel temps fait-il aujourd'hui?",
                "expected_response_patterns": {
                    "contains": ["météo", "température", "degrés"]
                }
            }
        }
    )
    db.add(test14_outcome)

    # === Test 15: Multi-Turn Multi-Language ===
    # Note: Demo 2 already has this (Restaurant Reservation), so marking as additional test
    test15_script = ScenarioScript(
        name="Test: Multi-Turn Multi-Language Navigation",
        description="Multi-turn navigation with language variants per step",
        is_active=True,
        created_by=created_by_id,
        tenant_id=org_id,
        validation_mode="hybrid",
        script_metadata={
            "category": "other",
            "priority": "high",
            "tags": ["test", "multi-language", "multi-turn", "navigation"],
            "expected_result": "pass",
            "language": "multi",
            "supported_languages": ["en-US", "es-ES"]
        }
    )
    db.add(test15_script)
    await db.flush()

    test15_step1 = ScenarioStep(
        script_id=test15_script.id,
        step_order=1,
        user_utterance="Navigate to downtown",
        step_metadata={
            "description": "Navigation request",
            "primary_language": "en-US",
            "language_code": "en-US",
            "language_variants": [
                {
                    "language_code": "en-US",
                    "user_utterance": "Navigate to downtown"
                },
                {
                    "language_code": "es-ES",
                    "user_utterance": "Navega al centro"
                }
            ]
        }
    )
    db.add(test15_step1)
    await db.flush()

    test15_step1_outcome = ExpectedOutcome(
        tenant_id=org_id,
        scenario_step_id=test15_step1.id,
        outcome_code="TEST_MULTITURN_MULTILANG_NAV_STEP1",
        name="Multi-Turn Multi-Language Nav Step 1",
        description="Navigation request with language variants",
        expected_command_kind="NavigationCommand",
        expected_response_content={"contains": ["navigat", "downtown"]},
        expected_asr_confidence_min=0.7,
        validation_rules={"min_confidence": 0.7},
        language_variations={
            "en-US": {
                "user_utterance": "Navigate to downtown",
                "expected_response_patterns": {
                    "contains": ["navigat", "downtown"]
                }
            },
            "es-ES": {
                "user_utterance": "Navega al centro",
                "expected_response_patterns": {
                    "contains": ["navega", "centro"]
                }
            }
        }
    )
    db.add(test15_step1_outcome)

    # ========================================================================
    # REGEX VALIDATION TESTS (3)
    # ========================================================================

    # === Test 16: Temperature Regex - PASS ===
    test16_script = ScenarioScript(
        name="Test: Temperature Regex PASS",
        description="Weather query with temperature regex validation - should PASS",
        is_active=True,
        created_by=created_by_id,
        tenant_id=org_id,
        validation_mode="hybrid",
        script_metadata={
            "category": "other",
            "priority": "high",
            "tags": ["test", "regex", "pass", "temperature"],
            "expected_result": "pass"
        }
    )
    db.add(test16_script)
    await db.flush()

    test16_step = ScenarioStep(
        script_id=test16_script.id,
        step_order=1,
        user_utterance="What's the temperature?",
        step_metadata={
            "description": "Temperature query with regex pattern",
            "language_code": "en-US"
        }
    )
    db.add(test16_step)
    await db.flush()

    test16_outcome = ExpectedOutcome(
        tenant_id=org_id,
        scenario_step_id=test16_step.id,
        outcome_code="TEST_TEMPERATURE_REGEX_PASS",
        name="Temperature Regex Test (PASS)",
        description="Expected to PASS - response matches temperature pattern",
        expected_command_kind="WeatherCommand",
        expected_response_content={
            "regex": [r"\d+.*degree"]  # Matches "72 degrees", "22 degrees Celsius", etc.
        },
        expected_asr_confidence_min=0.7,
        validation_rules={"min_confidence": 0.7}
    )
    db.add(test16_outcome)

    # === Test 17: Time Format Regex - PASS ===
    test17_script = ScenarioScript(
        name="Test: Navigation Time Regex PASS",
        description="Navigation query with time/duration regex - should PASS",
        is_active=True,
        created_by=created_by_id,
        tenant_id=org_id,
        validation_mode="hybrid",
        script_metadata={
            "category": "other",
            "priority": "high",
            "tags": ["test", "regex", "pass", "time"],
            "expected_result": "pass"
        }
    )
    db.add(test17_script)
    await db.flush()

    test17_step = ScenarioStep(
        script_id=test17_script.id,
        step_order=1,
        user_utterance="Navigate to downtown Seattle",
        step_metadata={
            "description": "Navigation query expecting time pattern in response",
            "language_code": "en-US"
        }
    )
    db.add(test17_step)
    await db.flush()

    test17_outcome = ExpectedOutcome(
        tenant_id=org_id,
        scenario_step_id=test17_step.id,
        outcome_code="TEST_TIME_REGEX_PASS",
        name="Navigation Time Regex Test (PASS)",
        description="Expected to PASS - response matches time/duration pattern",
        expected_command_kind="NavigationCommand",
        expected_response_content={
            "regex": [r"\d+\s*minute"]  # Matches "15 minutes", "20 minute", etc.
        },
        expected_asr_confidence_min=0.7,
        validation_rules={"min_confidence": 0.7}
    )
    db.add(test17_outcome)

    # === Test 18: Wrong Regex Pattern - FAIL ===
    test18_script = ScenarioScript(
        name="Test: Wrong Regex Pattern FAIL",
        description="Weather query expecting number pattern in text - should FAIL",
        is_active=True,
        created_by=created_by_id,
        tenant_id=org_id,
        validation_mode="hybrid",
        script_metadata={
            "category": "other",
            "priority": "high",
            "tags": ["test", "regex", "fail"],
            "expected_result": "fail"
        }
    )
    db.add(test18_script)
    await db.flush()

    test18_step = ScenarioStep(
        script_id=test18_script.id,
        step_order=1,
        user_utterance="What's the weather?",
        step_metadata={
            "description": "Weather query expecting wrong regex (should fail)",
            "language_code": "en-US"
        }
    )
    db.add(test18_step)
    await db.flush()

    test18_outcome = ExpectedOutcome(
        tenant_id=org_id,
        scenario_step_id=test18_step.id,
        outcome_code="TEST_WRONG_REGEX_FAIL",
        name="Wrong Regex Pattern Test (FAIL)",
        description="Expected to FAIL - expects phone number pattern that won't appear",
        expected_command_kind="WeatherCommand",
        expected_response_content={
            "regex": [r"\d{3}-\d{3}-\d{4}"]  # Phone number pattern - won't match weather response
        },
        expected_asr_confidence_min=0.7,
        validation_rules={"min_confidence": 0.7}
    )
    db.add(test18_outcome)

    # ========================================================================
    # LLM & HYBRID TESTS (2)
    # ========================================================================

    # === Test 19: LLM Ensemble - PASS ===
    test19_script = ScenarioScript(
        name="Test: LLM Ensemble PASS",
        description="Restaurant reservation with LLM semantic validation - should PASS",
        is_active=True,
        created_by=created_by_id,
        tenant_id=org_id,
        validation_mode="hybrid",
        script_metadata={
            "category": "other",
            "priority": "high",
            "tags": ["test", "llm", "pass", "ensemble"],
            "expected_result": "pass"
        }
    )
    db.add(test19_script)
    await db.flush()

    test19_step = ScenarioStep(
        script_id=test19_script.id,
        step_order=1,
        user_utterance="I'd like to book a table for dinner tonight",
        step_metadata={
            "description": "Restaurant reservation (LLM validation only)",
            "validation_type": "llm_ensemble",
            "language_code": "en-US"
        }
    )
    db.add(test19_step)
    await db.flush()

    test19_outcome = ExpectedOutcome(
        tenant_id=org_id,
        scenario_step_id=test19_step.id,
        outcome_code="TEST_LLM_ENSEMBLE_PASS",
        name="LLM Ensemble Test (PASS)",
        description="Expected to PASS with LLM semantic validation",
        expected_command_kind="ClientMatchCommand",
        expected_response_content={
            "contains": ["reservation", "table", "book"]
        },
        expected_asr_confidence_min=0.7,
        validation_rules={
            "min_confidence": 0.7,
            "llm_validation": True
        }
    )
    db.add(test19_outcome)

    # === Test 20: Hybrid Validation - PASS ===
    test20_script = ScenarioScript(
        name="Test: Hybrid Validation PASS",
        description="Navigation with both Houndify + LLM validation - should PASS",
        is_active=True,
        created_by=created_by_id,
        tenant_id=org_id,
        validation_mode="hybrid",
        script_metadata={
            "category": "other",
            "priority": "high",
            "tags": ["test", "hybrid", "pass", "both"],
            "expected_result": "pass"
        }
    )
    db.add(test20_script)
    await db.flush()

    test20_step = ScenarioStep(
        script_id=test20_script.id,
        step_order=1,
        user_utterance="Navigate to the nearest coffee shop",
        step_metadata={
            "description": "Navigation command with hybrid validation",
            "validation_type": "hybrid",
            "language_code": "en-US"
        }
    )
    db.add(test20_step)
    await db.flush()

    test20_outcome = ExpectedOutcome(
        tenant_id=org_id,
        scenario_step_id=test20_step.id,
        outcome_code="TEST_HYBRID_VALIDATION_PASS",
        name="Hybrid Validation Test (PASS)",
        description="Expected to PASS with both Houndify and LLM validation",
        expected_command_kind="NavigationCommand",
        expected_response_content={
            "contains": ["coffee", "navigat"]
        },
        expected_asr_confidence_min=0.7,
        entities={"destination": "coffee shop", "modifier": "nearest"},
        validation_rules={
            "min_confidence": 0.7,
            "llm_validation": True,
            "houndify_validation": True
        }
    )
    db.add(test20_outcome)

    await db.flush()
    print("  Created 20 comprehensive test scenarios:")
    print("    ========== DEMO SCENARIOS (3) ==========")
    print("    [1]  Demo: Weather Query (EN only)")
    print("    [2]  Demo: Restaurant Reservation (Multi-turn with multi-language)")
    print("    [3]  Demo: Smart Home Control")
    print()
    print("    ========== HOUNDIFY VALIDATION TESTS (8) ==========")
    print("    [4]  PASS: CommandKind Match (WeatherCommand)")
    print("    [5]  FAIL: CommandKind Mismatch (Music expecting Weather)")
    print("    [6]  FAIL: NoResultCommand (Gibberish expecting Weather)")
    print("    [7]  PASS: Response Content Contains")
    print("    [8]  FAIL: Response Content Wrong Contains")
    print("    [9]  PASS: Music with Regex")
    print("    [10] PASS: Normal ASR Confidence")
    print("    [11] FAIL: High ASR Confidence Threshold")
    print()
    print("    ========== MULTI-LANGUAGE SCENARIOS (4) ==========")
    print("    [12] Spanish Weather Query (es-ES)")
    print("    [13] French Weather Query (fr-FR)")
    print("    [14] Multi-Language Single Step (EN/ES/FR)")
    print("    [15] Multi-Turn Multi-Language Navigation")
    print()
    print("    ========== REGEX VALIDATION TESTS (3) ==========")
    print("    [16] PASS: Temperature Regex")
    print("    [17] PASS: Navigation Time Regex")
    print("    [18] FAIL: Wrong Regex Pattern")
    print()
    print("    ========== LLM & HYBRID TESTS (2) ==========")
    print("    [19] PASS: LLM Ensemble")
    print("    [20] PASS: Hybrid Validation")


async def main():
    """Main entry point - seeds all data."""
    settings = get_settings()

    # Create async engine
    database_url = settings.DATABASE_URL
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    engine = create_async_engine(database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    print("=" * 60)
    print("SEEDING ALL DATA")
    print("=" * 60)

    async with async_session() as session:
        try:
            # Step 1: Create super admin (platform-wide access)
            print("\n[1/3] Seeding super admin...")
            super_admin = await seed_super_admin(session)

            if not super_admin:
                print("ERROR: Could not create super admin. Aborting.")
                return

            # Step 2: Create demo organization
            print("\n[2/3] Seeding demo organization...")
            demo_org = await seed_demo_organization(session)

            if not demo_org:
                print("ERROR: Could not create demo organization. Aborting.")
                return

            # Step 3: Create demo scenarios for the demo org
            # org_id = demo_org.id (tenant for all data)
            # created_by_id = demo_org.id (the org admin created them)
            print(f"\n[3/3] Seeding demo scenarios (org_id={demo_org.id})...")
            await seed_demo_scenarios(session, org_id=demo_org.id, created_by_id=demo_org.id)

            # Commit all changes
            await session.commit()
            print("\n" + "=" * 60)
            print("ALL DATA SEEDED SUCCESSFULLY!")
            print("=" * 60)
            print("\nLogin credentials:")
            print("  Super Admin (platform):  superadmin / SuperAdmin123!")
            print("  Demo Org Admin:          demo_admin / DemoAdmin123!")
            print("=" * 60)

        except Exception as e:
            print(f"\nERROR: Failed to seed data: {e}")
            await session.rollback()
            raise

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
