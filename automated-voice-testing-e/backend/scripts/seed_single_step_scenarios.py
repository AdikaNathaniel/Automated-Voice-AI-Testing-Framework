#!/usr/bin/env python3
"""
Seed single-step scenarios (converted from old test cases).

Creates ScenarioScripts with single steps to demonstrate that single-turn
tests are just multi-turn scenarios with one step.

This recreates the 5 test cases that were previously converted:
1. Basic Weather Query (Weather)
2. Weather Forecast Query (Weather)
3. Play Music Command (Music)
4. Pause Music Command (Music)
5. Turn On Lights (SmartHome)
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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def seed_single_step_scenarios():
    """Seed single-step scenario scripts."""
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
                return

            # Check if scenarios already exist
            scenario_names = [
                "Basic Weather Query",
                "Weather Forecast Query",
                "Play Music Command",
                "Pause Music Command",
                "Turn On Lights"
            ]
            result = await db.execute(
                select(ScenarioScript).filter(ScenarioScript.name.in_(scenario_names))
            )
            existing = result.scalars().all()

            if existing:
                logger.info("✓ Single-step scenarios already exist, skipping seeding:")
                for script in existing:
                    logger.info(f"  - {script.name} (ID: {script.id})")
                return

            logger.info("Creating single-step scenarios...")

            # Get effective tenant_id (user's own id for individual users)
            tenant_id = user.tenant_id if user.tenant_id else user.id

            # Define single-step scenarios
            scenarios = [
                {
                    "name": "Basic Weather Query",
                    "description": "Single-turn weather query test",
                    "category": "weather",
                    "command_kind": "WeatherCommand",
                    "queries": {
                        "en-US": "What's the weather like today?",
                        "es-ES": "¿Cómo está el clima hoy?",
                        "fr-FR": "Quel temps fait-il aujourd'hui?"
                    },
                    "expected_response": "It's sunny and 72 degrees"
                },
                {
                    "name": "Weather Forecast Query",
                    "description": "Single-turn weather forecast test",
                    "category": "weather",
                    "command_kind": "WeatherCommand",
                    "queries": {
                        "en-US": "What's the weather forecast for tomorrow?",
                        "es-ES": "¿Cuál es el pronóstico del tiempo para mañana?",
                        "fr-FR": "Quelles sont les prévisions météo pour demain?"
                    },
                    "expected_response": "Tomorrow will be partly cloudy with a high of 68"
                },
                {
                    "name": "Play Music Command",
                    "description": "Single-turn music playback test",
                    "category": "media",
                    "command_kind": "MusicCommand",
                    "queries": {
                        "en-US": "Play some jazz music",
                        "es-ES": "Reproduce música jazz",
                        "fr-FR": "Joue de la musique jazz"
                    },
                    "expected_response": "Playing jazz music"
                },
                {
                    "name": "Pause Music Command",
                    "description": "Single-turn music pause test",
                    "category": "media",
                    "command_kind": "MusicCommand",
                    "queries": {
                        "en-US": "Pause the music",
                        "es-ES": "Pausa la música",
                        "fr-FR": "Mets la musique en pause"
                    },
                    "expected_response": "Music paused"
                },
                {
                    "name": "Turn On Lights",
                    "description": "Single-turn smart home light control test",
                    "category": "smart_home",
                    "command_kind": "ClientMatchCommand",  # Custom command for smart home
                    "queries": {
                        "en-US": "Turn on the living room lights",
                        "es-ES": "Enciende las luces de la sala",
                        "fr-FR": "Allume les lumières du salon"
                    },
                    "expected_response": "Turning on living room lights"
                }
            ]
            
            created_count = 0
            
            for scenario_data in scenarios:
                # Create scenario script
                script = ScenarioScript(
                    name=scenario_data["name"],
                    description=scenario_data["description"],
                    version="1.0.0",
                    created_by=user.id,
                    script_metadata={
                        "category": scenario_data["category"],
                        "is_single_turn": True,
                        "languages": list(scenario_data["queries"].keys()),
                        "tags": ["single-turn", scenario_data["category"].lower()]
                    }
                )
                db.add(script)
                await db.flush()
                
                # Create one step per language
                for lang, query in scenario_data["queries"].items():
                    step = ScenarioStep(
                        script_id=script.id,
                        step_order=1,
                        user_utterance=query,
                        step_metadata={
                            "language": lang,
                            "is_single_turn": True
                        }
                    )
                    db.add(step)
                    await db.flush()

                    # Create expected outcome
                    outcome = ExpectedOutcome(
                        tenant_id=tenant_id,
                        outcome_code=f"{scenario_data['name'].upper().replace(' ', '_')}_{lang.replace('-', '_')}",
                        name=f"{scenario_data['name']} - {lang}",
                        scenario_step_id=step.id,
                        expected_command_kind=scenario_data["command_kind"],
                        expected_response_content={"contains": [scenario_data["expected_response"].lower()]},
                        tolerance_settings={"semantic_similarity": 0.75}
                    )
                    db.add(outcome)

                created_count += 1
                logger.info(f"✓ Created: {scenario_data['name']} ({len(scenario_data['queries'])} languages)")

            await db.commit()
            logger.info(f"✅ Successfully created {created_count} single-step scenarios")

        except Exception as e:
            logger.error(f"❌ Seeding failed: {e}")
            await db.rollback()
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_single_step_scenarios())

