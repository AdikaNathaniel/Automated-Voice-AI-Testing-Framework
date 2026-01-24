#!/usr/bin/env python3
"""
Analyze all scenarios to verify their validation patterns match mock Houndify client behavior.

This script:
1. Loads all scenarios from the database
2. Simulates what the mock Houndify client would return
3. Checks if validation patterns match expected responses
4. Reports any mismatches

Usage:
    cd backend
    python scripts/analyze_scenarios.py
"""

from __future__ import annotations

import asyncio
import os
import sys
import re

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

from api.config import get_settings
from models.scenario_script import ScenarioScript, ScenarioStep
from models.expected_outcome import ExpectedOutcome
from integrations.houndify.mock_client import MockHoundifyClient


async def analyze_scenarios():
    """Analyze all scenarios against mock client behavior."""

    # Setup database connection
    settings = get_settings()
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        # Load all scenarios
        result = await db.execute(
            select(ScenarioScript).order_by(ScenarioScript.created_at)
        )
        scenarios = list(result.scalars().all())

        print("=" * 80)
        print("SCENARIO VALIDATION PATTERN ANALYSIS")
        print("=" * 80)
        print(f"\nAnalyzing {len(scenarios)} scenarios...\n")

        # Initialize mock client
        mock_client = MockHoundifyClient()

        total_checks = 0
        passed_checks = 0
        failed_checks = 0
        issues_found = []

        for idx, scenario in enumerate(scenarios, 1):
            print(f"\n[{idx}/{len(scenarios)}] {scenario.name}")
            print("-" * 80)

            # Load steps
            steps_result = await db.execute(
                select(ScenarioStep)
                .where(ScenarioStep.script_id == scenario.id)
                .order_by(ScenarioStep.step_order)
            )
            steps = list(steps_result.scalars().all())

            # Analyze each step
            for step in steps:
                # Load expected outcome
                outcome_result = await db.execute(
                    select(ExpectedOutcome)
                    .where(ExpectedOutcome.scenario_step_id == step.id)
                )
                outcome = outcome_result.scalar_one_or_none()

                if not outcome:
                    print(f"  ⚠️  Step {step.step_order}: No expected outcome defined")
                    continue

                # Get language variants or default to single language
                step_metadata = step.step_metadata or {}
                language_variants = step_metadata.get('language_variants', [])

                if not language_variants:
                    # Single language scenario
                    language_variants = [{
                        'language_code': step_metadata.get('language_code', 'en-US'),
                        'user_utterance': step.user_utterance
                    }]

                # Check each language variant
                for variant in language_variants:
                    lang_code = variant['language_code']
                    utterance = variant['user_utterance']
                    lang = lang_code.split('-')[0].lower()

                    # Simulate mock client response
                    try:
                        response = await mock_client._build_response(
                            prompt=utterance,
                            user_id="test_user",
                            request_id="test_request",
                            request_info={"LanguageCode": lang_code}
                        )
                    except Exception as e:
                        print(f"  ❌ Step {step.step_order} ({lang_code}): Error simulating mock client: {e}")
                        failed_checks += 1
                        total_checks += 1
                        issues_found.append({
                            'scenario': scenario.name,
                            'step': step.step_order,
                            'language': lang_code,
                            'issue': f'Mock client error: {e}'
                        })
                        continue

                    total_checks += 1

                    # Extract mock response details
                    mock_command_kind = response['AllResults'][0]['CommandKind']
                    mock_spoken_response = response['AllResults'][0]['SpokenResponse']

                    # Check 1: CommandKind match
                    expected_command_kind = outcome.expected_command_kind
                    command_kind_match = (mock_command_kind == expected_command_kind)

                    # Check 2: Response content validation
                    expected_response_content = None

                    # Check for language-specific patterns first
                    if hasattr(outcome, 'language_variations') and outcome.language_variations:
                        lang_variation = outcome.language_variations.get(lang_code, {})
                        if 'expected_response_patterns' in lang_variation:
                            expected_response_content = lang_variation['expected_response_patterns']

                    # Fall back to default expected_response_content
                    if not expected_response_content and outcome.expected_response_content:
                        expected_response_content = outcome.expected_response_content

                    content_match = True
                    missing_words = []

                    if expected_response_content and 'contains' in expected_response_content:
                        required_words = expected_response_content['contains']
                        mock_response_lower = mock_spoken_response.lower()

                        for word in required_words:
                            if word.lower() not in mock_response_lower:
                                content_match = False
                                missing_words.append(word)

                    # Report results
                    if command_kind_match and content_match:
                        status = "✅ PASS"
                        passed_checks += 1
                    else:
                        status = "❌ FAIL"
                        failed_checks += 1

                        issue_details = []
                        if not command_kind_match:
                            issue_details.append(
                                f"CommandKind mismatch: expected '{expected_command_kind}', "
                                f"got '{mock_command_kind}'"
                            )
                        if not content_match:
                            issue_details.append(
                                f"Missing words in response: {missing_words}"
                            )

                        issues_found.append({
                            'scenario': scenario.name,
                            'step': step.step_order,
                            'language': lang_code,
                            'utterance': utterance,
                            'issue': ' | '.join(issue_details),
                            'mock_response': mock_spoken_response
                        })

                    print(f"  {status} Step {step.step_order} ({lang_code})")
                    print(f"      Utterance: \"{utterance}\"")
                    print(f"      Mock says: \"{mock_spoken_response}\"")
                    print(f"      CommandKind: {mock_command_kind} (expected: {expected_command_kind})")

                    if expected_response_content and 'contains' in expected_response_content:
                        print(f"      Expected words: {expected_response_content['contains']}")
                        if missing_words:
                            print(f"      ❌ Missing: {missing_words}")

    # Summary
    print("\n" + "=" * 80)
    print("ANALYSIS SUMMARY")
    print("=" * 80)
    print(f"\nTotal checks: {total_checks}")
    print(f"Passed: {passed_checks} ({passed_checks/total_checks*100:.1f}%)")
    print(f"Failed: {failed_checks} ({failed_checks/total_checks*100:.1f}%)")

    if issues_found:
        print("\n" + "=" * 80)
        print("ISSUES FOUND")
        print("=" * 80)

        for issue in issues_found:
            print(f"\n❌ {issue['scenario']} - Step {issue['step']} ({issue['language']})")
            print(f"   Utterance: {issue['utterance']}")
            print(f"   Issue: {issue['issue']}")
            if 'mock_response' in issue:
                print(f"   Mock response: {issue['mock_response']}")
    else:
        print("\n🎉 All validation patterns match mock client behavior!")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(analyze_scenarios())
