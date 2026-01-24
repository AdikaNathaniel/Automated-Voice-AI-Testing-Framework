#!/usr/bin/env python3
"""
Fix Defective Scenarios Script

This script fixes:
1. Language codes: Normalize 2-char codes to 5-char (en → en-US, es → es-ES, etc.)
2. Step order: Fix duplicate step_order values
3. Expected outcomes: Add sample expected outcomes to steps without them

Run with: python scripts/fix_scenarios.py
"""

import asyncio
import sys
import os
import json
from uuid import uuid4

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text, select, update
from sqlalchemy.orm import selectinload
from api.database import SessionLocal

# Language code mapping (2-char to 5-char)
LANGUAGE_CODE_MAP = {
    'en': 'en-US',
    'es': 'es-ES',
    'fr': 'fr-FR',
    'de': 'de-DE',
    'it': 'it-IT',
    'pt': 'pt-BR',
    'zh': 'zh-CN',
    'ja': 'ja-JP',
    'ko': 'ko-KR',
    'ar': 'ar-SA',
    'ru': 'ru-RU',
    'nl': 'nl-NL',
    'pl': 'pl-PL',
    'sv': 'sv-SE',
    'da': 'da-DK',
    'no': 'nb-NO',
    'fi': 'fi-FI',
    'tr': 'tr-TR',
    'he': 'he-IL',
    'th': 'th-TH',
    'vi': 'vi-VN',
    'id': 'id-ID',
    'ms': 'ms-MY',
    'hi': 'hi-IN',
}

# Command kind mapping for expected outcomes
COMMAND_KIND_MAP = {
    'weather': 'WeatherCommand',
    'music': 'MusicCommand',
    'navigation': 'NavigationCommand',
    'smart_home': 'SmartHomeCommand',
    'lights': 'SmartHomeCommand',
    'timer': 'TimerCommand',
    'alarm': 'AlarmCommand',
    'reminder': 'ReminderCommand',
    'calendar': 'CalendarCommand',
    'call': 'PhoneCallCommand',
    'message': 'MessageCommand',
    'reservation': 'ConversationCommand',
}


def normalize_language_code(code: str) -> str:
    """Convert 2-char language code to 5-char format (e.g., en → en-US)."""
    if not code:
        return 'en-US'

    code = code.strip()

    # Already 5-char format - normalize case (en-us → en-US)
    if len(code) >= 4 and '-' in code:
        parts = code.split('-')
        return f'{parts[0].lower()}-{parts[1].upper()}'

    # Map 2-char to 5-char
    code_lower = code.lower()
    return LANGUAGE_CODE_MAP.get(code_lower, f'{code_lower}-{code_lower.upper()}')


def detect_command_kind(user_utterance: str) -> str | None:
    """Detect likely command kind from user utterance."""
    utterance_lower = user_utterance.lower()

    for keyword, command_kind in COMMAND_KIND_MAP.items():
        if keyword in utterance_lower:
            return command_kind

    return None


def generate_expected_response_content(user_utterance: str) -> dict:
    """Generate expected response content patterns based on user utterance."""
    utterance_lower = user_utterance.lower()

    # Weather queries
    if 'weather' in utterance_lower:
        return {"contains": ["weather", "temperature"]}

    # Smart home / lights
    if 'light' in utterance_lower or 'turn on' in utterance_lower or 'turn off' in utterance_lower:
        return {"contains": ["done", "light"]}

    # Music
    if 'music' in utterance_lower or 'play' in utterance_lower:
        return {"contains": ["playing", "music"]}

    # Navigation
    if 'navigate' in utterance_lower or 'directions' in utterance_lower:
        return {"contains": ["navigation", "route"]}

    # Timer / Alarm
    if 'timer' in utterance_lower:
        return {"contains": ["timer", "set"]}
    if 'alarm' in utterance_lower:
        return {"contains": ["alarm", "set"]}

    # Default - no specific content required
    return {}


async def fix_scenarios():
    """Fix all defective scenarios in the database."""

    print("=" * 60)
    print("FIX SCENARIOS - Repairing Defective Data")
    print("=" * 60)
    print()

    async with SessionLocal() as db:
        # ============================================================
        # STEP 1: Fix language codes in scenario_scripts.script_metadata
        # ============================================================
        print("STEP 1: Fixing language codes in script_metadata...")

        result = await db.execute(text("""
            SELECT id, name, script_metadata
            FROM scenario_scripts
            WHERE script_metadata IS NOT NULL
        """))
        scripts = result.fetchall()

        scripts_fixed = 0
        for script in scripts:
            script_id, name, metadata = script
            if not metadata:
                continue

            modified = False
            if isinstance(metadata, str):
                metadata = json.loads(metadata)

            # Fix language code
            if 'language' in metadata:
                old_lang = metadata['language']
                new_lang = normalize_language_code(old_lang)
                if old_lang != new_lang:
                    metadata['language'] = new_lang
                    modified = True
                    print(f"  ✓ {name}: language '{old_lang}' → '{new_lang}'")

            if modified:
                await db.execute(text("""
                    UPDATE scenario_scripts
                    SET script_metadata = :metadata
                    WHERE id = :id
                """), {'id': script_id, 'metadata': json.dumps(metadata)})
                scripts_fixed += 1

        await db.commit()
        print(f"  Fixed {scripts_fixed} script metadata records")
        print()

        # ============================================================
        # STEP 2: Fix language codes in scenario_steps.step_metadata
        # ============================================================
        print("STEP 2: Fixing language codes in step_metadata...")

        result = await db.execute(text("""
            SELECT st.id, s.name, st.step_order, st.step_metadata
            FROM scenario_steps st
            JOIN scenario_scripts s ON s.id = st.script_id
            WHERE st.step_metadata IS NOT NULL
        """))
        steps = result.fetchall()

        steps_fixed = 0
        for step in steps:
            step_id, scenario_name, step_order, metadata = step
            if not metadata:
                continue

            modified = False
            if isinstance(metadata, str):
                metadata = json.loads(metadata)

            # Fix step-level language
            if 'language' in metadata:
                old_lang = metadata['language']
                new_lang = normalize_language_code(old_lang)
                if old_lang != new_lang:
                    metadata['language'] = new_lang
                    modified = True

            # Fix primary_language
            if 'primary_language' in metadata:
                old_lang = metadata['primary_language']
                new_lang = normalize_language_code(old_lang)
                if old_lang != new_lang:
                    metadata['primary_language'] = new_lang
                    modified = True

            # Fix language_variants array
            if 'language_variants' in metadata and metadata['language_variants']:
                for variant in metadata['language_variants']:
                    if 'language_code' in variant:
                        old_code = variant['language_code']
                        new_code = normalize_language_code(old_code)
                        if old_code != new_code:
                            variant['language_code'] = new_code
                            modified = True

            if modified:
                await db.execute(text("""
                    UPDATE scenario_steps
                    SET step_metadata = :metadata
                    WHERE id = :id
                """), {'id': step_id, 'metadata': json.dumps(metadata)})
                steps_fixed += 1
                print(f"  ✓ {scenario_name} Step {step_order}: Language codes normalized")

        await db.commit()
        print(f"  Fixed {steps_fixed} step metadata records")
        print()

        # ============================================================
        # STEP 3: Fix duplicate step_order values
        # ============================================================
        print("STEP 3: Checking for duplicate step_order values...")

        result = await db.execute(text("""
            SELECT script_id, COUNT(*) as cnt
            FROM scenario_steps
            GROUP BY script_id, step_order
            HAVING COUNT(*) > 1
        """))
        duplicates = result.fetchall()

        if duplicates:
            print(f"  Found {len(duplicates)} scenarios with duplicate step_order")
            # Fix by renumbering steps
            for script_id, _ in duplicates:
                result = await db.execute(text("""
                    SELECT id FROM scenario_steps
                    WHERE script_id = :script_id
                    ORDER BY created_at, id
                """), {'script_id': script_id})
                step_ids = [row[0] for row in result.fetchall()]

                for i, step_id in enumerate(step_ids, start=1):
                    await db.execute(text("""
                        UPDATE scenario_steps
                        SET step_order = :order
                        WHERE id = :id
                    """), {'id': step_id, 'order': i})

            await db.commit()
            print(f"  ✓ Renumbered steps for {len(duplicates)} scenarios")
        else:
            print("  ✓ No duplicate step_order values found")
        print()

        # ============================================================
        # STEP 4: Add sample expected outcomes to steps without them
        # ============================================================
        print("STEP 4: Adding sample expected outcomes...")

        # Check if any expected outcomes exist
        result = await db.execute(text("SELECT COUNT(*) FROM expected_outcomes"))
        existing_count = result.scalar()

        # Get steps without expected outcomes
        result = await db.execute(text("""
            SELECT st.id, s.name, st.step_order, st.user_utterance
            FROM scenario_steps st
            JOIN scenario_scripts s ON s.id = st.script_id
            LEFT JOIN expected_outcomes eo ON eo.scenario_step_id = st.id
            WHERE eo.id IS NULL
            ORDER BY s.name, st.step_order
        """))
        steps_without_outcomes = result.fetchall()

        if not steps_without_outcomes:
            print(f"  ✓ All steps already have expected outcomes")
        else:
            outcomes_added = 0
            for step in steps_without_outcomes:
                step_id, scenario_name, step_order, user_utterance = step

                # Detect command kind
                command_kind = detect_command_kind(user_utterance)

                # Generate expected response content patterns
                response_content = generate_expected_response_content(user_utterance)

                # Create expected outcome
                outcome_code = f"{scenario_name.lower().replace(' ', '_')}_step{step_order}_success"
                outcome_name = f"{scenario_name} - Step {step_order} Success"

                await db.execute(text("""
                    INSERT INTO expected_outcomes (
                        id, outcome_code, name, description,
                        expected_command_kind, expected_asr_confidence_min,
                        expected_response_content,
                        scenario_step_id,
                        confirmation_required, allow_partial_success,
                        created_at, updated_at
                    ) VALUES (
                        :id, :outcome_code, :name, :description,
                        :command_kind, :confidence_min,
                        :response_content,
                        :step_id,
                        false, false,
                        NOW(), NOW()
                    )
                """), {
                    'id': str(uuid4()),
                    'outcome_code': outcome_code,
                    'name': outcome_name,
                    'description': f"Expected successful outcome for: {user_utterance}",
                    'command_kind': command_kind,
                    'confidence_min': 0.7,
                    'response_content': json.dumps(response_content) if response_content else None,
                    'step_id': step_id
                })
                outcomes_added += 1
                print(f"  ✓ Added outcome: {outcome_name}")

            await db.commit()
            print(f"  Added {outcomes_added} expected outcomes")
        print()

        # ============================================================
        # Summary
        # ============================================================
        print("=" * 60)
        print("FIX SCENARIOS COMPLETE")
        print("=" * 60)

        # Final counts
        result = await db.execute(text("SELECT COUNT(*) FROM scenario_scripts"))
        print(f"  Scenarios: {result.scalar()}")

        result = await db.execute(text("SELECT COUNT(*) FROM scenario_steps"))
        print(f"  Steps: {result.scalar()}")

        result = await db.execute(text("SELECT COUNT(*) FROM expected_outcomes"))
        print(f"  Expected Outcomes: {result.scalar()}")


if __name__ == "__main__":
    asyncio.run(fix_scenarios())
