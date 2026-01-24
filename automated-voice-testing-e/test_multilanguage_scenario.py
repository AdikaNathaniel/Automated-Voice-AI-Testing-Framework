#!/usr/bin/env python3
"""
Test Multi-Language Houndify Scenario

This script demonstrates executing the 3-step multi-language scenario
with the MockHoundifyClient to validate it passes all steps.

Steps:
1. English: Math calculation "What's 10 plus 15?"
2. French: Calendar query "Qu'est-ce que j'ai au calendrier aujourd'hui?"
3. English: Music request "Play some jazz music"

Usage:
    python test_multilanguage_scenario.py
"""

import asyncio
import json
import logging
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from integrations.houndify.mock_client import MockHoundifyClient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_scenario():
    """Load the multi-language scenario from JSON file."""
    with open('MULTILANGUAGE_SCENARIO_SOUNDHOUND.json', 'r') as f:
        return json.load(f)


async def execute_step(client, step_num, step_data, scenario_config):
    """
    Execute a single scenario step and validate results.

    Args:
        client: MockHoundifyClient instance
        step_num: Step number (1, 2, 3)
        step_data: Step configuration from scenario
        scenario_config: Test configuration from scenario

    Returns:
        dict: Execution results with validation status
    """
    logger.info(f"\n{'='*70}")
    logger.info(f"STEP {step_num}: {step_data['step_metadata']['description']}")
    logger.info(f"{'='*70}")

    # Extract step details
    utterance = step_data['user_utterance']
    request_info = step_data['step_metadata']['request_info']
    expected_outcome = step_data['expected_outcomes'][0]

    logger.info(f"User Utterance: '{utterance}'")
    logger.info(f"Language: {request_info['LanguageCode']}")
    logger.info(f"Expected Intent: {expected_outcome['expected_command_kind']}")

    # Execute query
    try:
        result = await client.text_query(
            query=utterance,
            user_id=f"test_user_{step_num}",
            request_id=f"req_{step_num}",
            request_info=request_info
        )

        logger.info(f"\n✓ Query executed successfully")
        logger.info(f"Response Status: {result.get('Status', 'N/A')}")

        # Extract result details
        if result.get('AllResults') and len(result['AllResults']) > 0:
            first_result = result['AllResults'][0]

            command_kind = first_result.get('CommandKind', 'N/A')
            spoken_response = first_result.get('SpokenResponse', 'N/A')
            raw_transcription = first_result.get('RawTranscription', 'N/A')

            logger.info(f"Command Kind: {command_kind}")
            logger.info(f"Spoken Response: '{spoken_response}'")
            logger.info(f"Transcription: '{raw_transcription}'")

            # Validate intent
            expected_intent = expected_outcome['expected_command_kind']
            intent_match = command_kind == expected_intent

            if intent_match:
                logger.info(f"\n✅ VALIDATION PASSED: Intent matches ({expected_intent})")
            else:
                logger.warning(f"\n⚠️  VALIDATION WARNING: Intent mismatch")
                logger.warning(f"   Expected: {expected_intent}")
                logger.warning(f"   Got: {command_kind}")

            # Validate response content
            validation_rules = expected_outcome['validation_rules']
            response_checks = validation_rules.get('response_should_contain', [])

            content_valid = True
            for check_term in response_checks:
                term_lower = check_term.lower()
                response_lower = spoken_response.lower()

                if term_lower in response_lower or term_lower in raw_transcription.lower():
                    logger.info(f"✓ Response contains '{check_term}'")
                else:
                    logger.warning(f"⚠️  Response missing '{check_term}'")
                    content_valid = False

            # Final result
            overall_pass = intent_match and content_valid

            return {
                'step': step_num,
                'status': 'PASS' if overall_pass else 'PARTIAL',
                'utterance': utterance,
                'language': request_info['LanguageCode'],
                'expected_intent': expected_intent,
                'actual_intent': command_kind,
                'intent_match': intent_match,
                'content_valid': content_valid,
                'spoken_response': spoken_response,
                'raw_response': result
            }
        else:
            logger.error("❌ No results returned in response")
            return {
                'step': step_num,
                'status': 'FAIL',
                'error': 'No results in response',
                'raw_response': result
            }

    except Exception as e:
        logger.error(f"❌ EXECUTION FAILED: {str(e)}")
        return {
            'step': step_num,
            'status': 'ERROR',
            'error': str(e)
        }


async def run_scenario():
    """Execute the complete 3-step scenario."""
    logger.info("\n" + "="*70)
    logger.info("MULTI-LANGUAGE HOUNDIFY SCENARIO TEST")
    logger.info("="*70 + "\n")

    # Load scenario
    scenario = load_scenario()
    logger.info(f"Scenario: {scenario['scenario_name']}")
    logger.info(f"Description: {scenario['description']}")
    logger.info(f"Languages: {', '.join(scenario['script_metadata']['languages'])}")

    # Configure mock client
    test_config = scenario['test_configuration']

    logger.info("\nConfiguring MockHoundifyClient...")
    client = MockHoundifyClient(
        response_patterns=test_config['response_patterns'],
        error_rate=test_config['mock_client_config']['error_rate'],
        latency_ms=test_config['mock_client_config']['latency_ms']
    )
    logger.info(f"✓ Client configured with {len(test_config['response_patterns'])} response patterns")

    # Execute steps
    results = []
    for step_data in scenario['steps']:
        step_num = step_data['step_order']
        result = await execute_step(client, step_num, step_data, test_config)
        results.append(result)

    # Summary
    logger.info("\n" + "="*70)
    logger.info("SCENARIO EXECUTION SUMMARY")
    logger.info("="*70 + "\n")

    passed = sum(1 for r in results if r.get('status') == 'PASS')
    partial = sum(1 for r in results if r.get('status') == 'PARTIAL')
    failed = sum(1 for r in results if r.get('status') in ['FAIL', 'ERROR'])

    logger.info(f"Total Steps: {len(results)}")
    logger.info(f"✅ Passed: {passed}")
    logger.info(f"⚠️  Partial: {partial}")
    logger.info(f"❌ Failed: {failed}")

    # Detailed results
    logger.info("\nDetailed Results:")
    logger.info("-" * 70)
    for result in results:
        status_icon = {
            'PASS': '✅',
            'PARTIAL': '⚠️',
            'FAIL': '❌',
            'ERROR': '❌'
        }.get(result.get('status'), '?')

        logger.info(f"\n{status_icon} Step {result['step']}: {result['status']}")
        logger.info(f"   Language: {result.get('language', 'N/A')}")
        logger.info(f"   Utterance: {result.get('utterance', 'N/A')}")

        if result.get('status') in ['PASS', 'PARTIAL']:
            logger.info(f"   Intent Match: {'Yes' if result.get('intent_match') else 'No'}")
            logger.info(f"   Content Valid: {'Yes' if result.get('content_valid') else 'No'}")
            logger.info(f"   Response: {result.get('spoken_response', 'N/A')}")
        elif result.get('error'):
            logger.info(f"   Error: {result.get('error')}")

    # Final verdict
    logger.info("\n" + "="*70)
    if failed == 0 and partial == 0:
        logger.info("🎉 ALL STEPS PASSED! Scenario is ready for production use.")
        return 0
    elif failed == 0:
        logger.info("⚠️  SCENARIO PASSED WITH WARNINGS - Review partial results")
        return 1
    else:
        logger.info("❌ SCENARIO FAILED - Fix errors before proceeding")
        return 2


async def main():
    """Main entry point."""
    try:
        exit_code = await run_scenario()
        sys.exit(exit_code)
    except FileNotFoundError:
        logger.error("❌ Scenario file not found: MULTILANGUAGE_SCENARIO_SOUNDHOUND.json")
        logger.error("   Make sure the file is in the current directory")
        sys.exit(3)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(4)


if __name__ == "__main__":
    asyncio.run(main())
