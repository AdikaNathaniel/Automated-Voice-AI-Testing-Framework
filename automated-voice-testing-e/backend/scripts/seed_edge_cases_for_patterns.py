"""
Seed script to create realistic edge cases for pattern recognition testing.

Creates edge cases with:
- Proper FK relationships to existing scenarios and users
- Similar characteristics to form patterns
- Different categories and severities
- Valid tenant IDs

Run with: docker-compose exec backend python scripts/seed_edge_cases_for_patterns.py
"""

import asyncio
import sys
import os
from datetime import date, datetime, timedelta
from uuid import uuid4
from random import choice, randint, sample

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from api.database import get_async_session
from models.edge_case import EdgeCase
from models.scenario_script import ScenarioScript
from models.user import User


# Pattern templates - edge cases that share similar characteristics
PATTERN_TEMPLATES = {
    "audio_quality": {
        "category": "audio_quality",
        "severity": "high",
        "cases": [
            {
                "title": "Background noise interference with wake word",
                "description": "System fails to detect wake word when background noise (traffic, music, conversation) is present",
                "tags": ["audio", "noise", "wake-word", "detection-failure"],
            },
            {
                "title": "Audio cutoff during wake word detection",
                "description": "Wake word audio is cut off or clipped, causing recognition failure",
                "tags": ["audio", "clipping", "wake-word", "detection-failure"],
            },
            {
                "title": "Microphone sensitivity issues with wake word",
                "description": "Low microphone sensitivity prevents wake word detection from distance",
                "tags": ["audio", "microphone", "wake-word", "detection-failure"],
            },
            {
                "title": "Echo interference affecting wake word recognition",
                "description": "Room echo causes wake word detection to fail or trigger incorrectly",
                "tags": ["audio", "echo", "wake-word", "detection-failure"],
            },
        ],
    },
    "ambiguity": {
        "category": "ambiguity",
        "severity": "medium",
        "cases": [
            {
                "title": "Ambiguous time reference in scheduling",
                "description": "User says 'tomorrow' but system interprets it as 'today' when crossing midnight",
                "tags": ["ambiguity", "time", "scheduling", "context"],
            },
            {
                "title": "Unclear pronoun reference in multi-turn",
                "description": "User refers to 'it' or 'that' but system loses context of what was discussed",
                "tags": ["ambiguity", "pronouns", "context", "multi-turn"],
            },
            {
                "title": "Multiple entity matches causing confusion",
                "description": "User says 'call John' but there are multiple contacts named John",
                "tags": ["ambiguity", "entities", "contacts", "disambiguation"],
            },
            {
                "title": "Vague location reference in navigation",
                "description": "User says 'take me home' but has multiple saved home addresses",
                "tags": ["ambiguity", "location", "navigation", "context"],
            },
        ],
    },
    "context_loss": {
        "category": "context_loss",
        "severity": "high",
        "cases": [
            {
                "title": "Context lost after timeout in conversation",
                "description": "System loses conversation context after 30 second pause, forcing user to restart",
                "tags": ["context", "timeout", "conversation", "state-management"],
            },
            {
                "title": "Session state cleared on interruption",
                "description": "Phone call or notification interrupts conversation and clears all context",
                "tags": ["context", "interruption", "session", "state-management"],
            },
            {
                "title": "Cross-domain context not preserved",
                "description": "Switching from music to navigation loses music playback context",
                "tags": ["context", "cross-domain", "state", "integration"],
            },
            {
                "title": "Multi-step command context forgotten",
                "description": "System forgets earlier steps when executing multi-step commands",
                "tags": ["context", "multi-step", "memory", "state-management"],
            },
        ],
    },
    "pronunciation": {
        "category": "pronunciation",
        "severity": "medium",
        "cases": [
            {
                "title": "Foreign name pronunciation not recognized",
                "description": "System fails to recognize non-English contact names with proper pronunciation",
                "tags": ["pronunciation", "names", "accents", "asr"],
            },
            {
                "title": "Regional accent affecting command recognition",
                "description": "Strong regional accent causes command misinterpretation",
                "tags": ["pronunciation", "accent", "dialect", "asr"],
            },
            {
                "title": "Homophones causing incorrect entity selection",
                "description": "Words that sound alike (to/two/too) cause wrong entity to be selected",
                "tags": ["pronunciation", "homophones", "entities", "asr"],
            },
            {
                "title": "Speech impediment affecting wake word",
                "description": "Users with speech impediments cannot reliably trigger wake word",
                "tags": ["pronunciation", "accessibility", "wake-word", "asr"],
            },
        ],
    },
    "multi_intent": {
        "category": "multi_intent",
        "severity": "medium",
        "cases": [
            {
                "title": "Compound command splits incorrectly",
                "description": "User says 'play music and navigate home' but system only executes first part",
                "tags": ["multi-intent", "compound", "parsing", "nlu"],
            },
            {
                "title": "Sequential intents processed out of order",
                "description": "Multiple commands are executed in wrong order, causing errors",
                "tags": ["multi-intent", "sequence", "execution", "nlu"],
            },
            {
                "title": "Conditional intent not recognized",
                "description": "If-then style commands not properly parsed ('if traffic is bad, take alternate route')",
                "tags": ["multi-intent", "conditional", "logic", "nlu"],
            },
            {
                "title": "Intent priority unclear in complex request",
                "description": "System doesn't know which intent to prioritize in multi-part request",
                "tags": ["multi-intent", "priority", "disambiguation", "nlu"],
            },
        ],
    },
}


async def get_random_scenario(db: AsyncSession) -> ScenarioScript | None:
    """Get a random active scenario from the database."""
    result = await db.execute(
        select(ScenarioScript)
        .where(ScenarioScript.is_active == True)
        .limit(10)
    )
    scenarios = result.scalars().all()
    return choice(scenarios) if scenarios else None


async def get_random_user(db: AsyncSession) -> User | None:
    """Get a random user from the database."""
    result = await db.execute(select(User).limit(10))
    users = result.scalars().all()
    return choice(users) if users else None


async def create_edge_case_from_template(
    db: AsyncSession,
    template: dict,
    pattern_type: str,
    category: str,
    severity: str,
    tenant_id: str,
    discovered_by_id: str,
    script_id: str | None,
    days_ago: int = 0,
) -> EdgeCase:
    """Create an edge case from a template."""
    discovered_date = date.today() - timedelta(days=days_ago)

    # Create scenario definition matching EdgeCaseSimilarityService expectations
    scenario_definition = {
        "user_utterance": template['title'].lower(),
        "expected_response": "Proper handling of the request",
        "actual_response": "Unexpected behavior or failure",
        "language_code": "en-US",
        "confidence_score": 0.3,  # Low confidence indicates failure
        "pattern_type": pattern_type,
        "failure_mode": category,
    }

    edge_case = EdgeCase(
        id=uuid4(),
        title=template["title"],
        description=template["description"],
        category=category,
        severity=severity,
        scenario_definition=scenario_definition,
        script_id=script_id,
        discovered_date=discovered_date,
        discovered_by=discovered_by_id,
        tenant_id=tenant_id,
        status="new",  # Set to 'new' so pattern analysis will process them
        tags=template["tags"],
        auto_created=True,  # Mark as auto-created for realism
    )

    db.add(edge_case)
    return edge_case


async def seed_edge_cases():
    """Seed edge cases with proper FK relationships."""
    print("Starting edge case seeding for pattern recognition...")

    async with get_async_session() as db:
        # Get a user to use as tenant and discoverer
        user = await get_random_user(db)
        if not user:
            print("ERROR: No users found in database. Please create a user first.")
            return

        print(f"Using user: {user.email} (ID: {user.id})")

        # Get some scenarios to link to
        result = await db.execute(
            select(ScenarioScript)
            .where(ScenarioScript.is_active == True)
            .limit(20)
        )
        scenarios = result.scalars().all()

        if not scenarios:
            print("WARNING: No active scenarios found. Edge cases will not be linked to scenarios.")
        else:
            print(f"Found {len(scenarios)} active scenarios to link to")

        # Create edge cases for each pattern type
        total_created = 0

        for pattern_type, config in PATTERN_TEMPLATES.items():
            print(f"\nCreating '{pattern_type}' pattern edge cases...")

            category = config["category"]
            severity = config["severity"]
            cases = config["cases"]

            # Create all cases from this template with slight time variations
            # This makes them recent enough to be picked up by pattern analysis
            for i, case_template in enumerate(cases):
                # Randomly assign to a scenario (or None)
                script_id = None
                if scenarios and randint(0, 100) < 70:  # 70% chance of linking to scenario
                    scenario = choice(scenarios)
                    script_id = scenario.id

                # Spread out discovered dates over last 5 days
                days_ago = i % 5

                edge_case = await create_edge_case_from_template(
                    db=db,
                    template=case_template,
                    pattern_type=pattern_type,
                    category=category,
                    severity=severity,
                    tenant_id=user.id,
                    discovered_by_id=user.id,
                    script_id=script_id,
                    days_ago=days_ago,
                )

                total_created += 1
                print(f"  ✓ Created: {edge_case.title}")

        # Commit all edge cases
        await db.commit()

        print(f"\n{'='*70}")
        print(f"Successfully created {total_created} edge cases")
        print(f"{'='*70}")
        print("\nPattern distribution:")
        for pattern_type, config in PATTERN_TEMPLATES.items():
            print(f"  • {pattern_type}: {len(config['cases'])} edge cases")

        print("\nNext steps:")
        print("1. Go to Edge Cases page → Pattern Groups tab")
        print("2. Click 'Run Analysis' button")
        print("3. Wait for analysis to complete (~30 seconds)")
        print("4. You should see 5 pattern groups detected")
        print("\nPattern analysis parameters:")
        print("  • Lookback: 7 days")
        print("  • Min pattern size: 3 edge cases")
        print("  • Similarity threshold: 0.85")


if __name__ == "__main__":
    asyncio.run(seed_edge_cases())
