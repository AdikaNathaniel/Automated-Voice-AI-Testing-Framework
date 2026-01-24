#!/usr/bin/env python3
"""
Test Morning Routine - Coherent Multi-Language Scenario

This scenario makes sense as a continuous conversation:
1. Check weather in San Francisco (English) - decide what to wear
2. Check calendar (French) - see today's schedule
3. Get directions to coffee shop (English) - prepare to leave

A realistic morning routine for a bilingual professional.

Usage:
    python3 test_morning_routine.py
"""

import asyncio
import json
import logging
from typing import Dict, Any

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


class SimpleMockHoundifyClient:
    """Simplified mock client for testing."""

    def __init__(self, response_patterns: Dict[str, Any]):
        self.response_patterns = response_patterns
        self.conversation_state = {"TurnCount": 0}

    def _match_pattern(self, query: str) -> Any:
        """Match query against response patterns."""
        query_lower = query.lower()
        for keyword, response in self.response_patterns.items():
            if keyword.lower() in query_lower:
                return response
        return None

    async def text_query(
        self,
        query: str,
        user_id: str,
        request_id: str,
        request_info: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Execute text query with conversation state."""
        # Simulate latency
        await asyncio.sleep(0.05)

        # Update conversation state
        self.conversation_state["TurnCount"] += 1

        # Match pattern
        matched = self._match_pattern(query)

        if matched:
            # Return matched response with conversation state
            response = matched.copy()
            response['userId'] = user_id
            response['requestId'] = request_id

            # Add conversation state to first result
            if response.get('AllResults') and len(response['AllResults']) > 0:
                if 'ConversationState' not in response['AllResults'][0]:
                    response['AllResults'][0]['ConversationState'] = self.conversation_state.copy()

            return response
        else:
            # Return default response
            return {
                "Status": "OK",
                "NumToReturn": 1,
                "AllResults": [{
                    "CommandKind": "InformationCommand",
                    "SpokenResponse": f"I processed your query: {query}",
                    "RawTranscription": query.lower(),
                    "FormattedTranscription": query,
                    "ConversationState": self.conversation_state.copy()
                }],
                "userId": user_id,
                "requestId": request_id
            }


def print_narrative(step_num: int, context: str, utterance: str, language: str):
    """Print narrative context for each step."""
    emojis = {1: "🌅", 2: "📅", 3: "☕"}

    print(f"\n{emojis.get(step_num, '💬')} STEP {step_num} CONTEXT:")
    print(f"   {context}")
    print(f"\n   User says ({language}): \"{utterance}\"")


async def execute_step(client, step_num, step_data):
    """Execute a single scenario step with narrative context."""
    logger.info(f"\n{'='*70}")
    logger.info(f"STEP {step_num} - {step_data['step_metadata']['description'][:50]}...")
    logger.info(f"{'='*70}")

    # Show narrative context
    print_narrative(
        step_num,
        step_data['step_metadata']['context'],
        step_data['user_utterance'],
        step_data['step_metadata']['language_code']
    )

    utterance = step_data['user_utterance']
    request_info = step_data['step_metadata']['request_info']
    expected_outcome = step_data['expected_outcomes'][0]

    # Execute query
    result = await client.text_query(
        query=utterance,
        user_id="morning_user",
        request_id=f"morning_req_{step_num}",
        request_info=request_info
    )

    print(f"\n   Assistant responds:")

    # Extract result details
    if result.get('AllResults') and len(result['AllResults']) > 0:
        first_result = result['AllResults'][0]

        command_kind = first_result.get('CommandKind', 'N/A')
        spoken_response = first_result.get('SpokenResponse', 'N/A')

        print(f"   \"{spoken_response}\"")
        print(f"\n   ✓ Intent: {command_kind}")

        # Validate intent
        expected_intent = expected_outcome['expected_command_kind']
        intent_match = command_kind == expected_intent

        if intent_match:
            print(f"   ✅ Intent matches (expected: {expected_intent})")
        else:
            print(f"   ❌ Intent mismatch (expected: {expected_intent}, got: {command_kind})")

        # Show follow-up
        follow_up = step_data.get('follow_up_action', '')
        if follow_up:
            print(f"\n   → Next: {follow_up}")

        return {
            'step': step_num,
            'status': 'PASS' if intent_match else 'FAIL',
            'utterance': utterance,
            'language': request_info['LanguageCode'],
            'expected_intent': expected_intent,
            'actual_intent': command_kind,
            'spoken_response': spoken_response,
            'intent_match': intent_match
        }
    else:
        print("   ❌ No results returned")
        return {
            'step': step_num,
            'status': 'FAIL',
            'error': 'No results in response'
        }


async def run_scenario():
    """Execute the morning routine scenario."""
    print("\n" + "="*70)
    print("MORNING ROUTINE SCENARIO - Bilingual Assistant")
    print("="*70)

    # Load scenario
    with open('MORNING_ROUTINE_SCENARIO.json', 'r') as f:
        scenario = json.load(f)

    print(f"\n{scenario['scenario_name']}")
    print(f"{scenario['description']}\n")

    # Show narrative
    print("📖 STORY:")
    for story_line in scenario['narrative_flow']['story']:
        print(f"   {story_line}")

    print("\n💡 WHY THIS MAKES SENSE:")
    for reason in scenario['narrative_flow']['why_it_makes_sense']:
        print(f"   • {reason}")

    # Configure mock client
    test_config = scenario['test_configuration']

    print(f"\n⚙️  Configuring MockHoundifyClient with {len(test_config['response_patterns'])} patterns...")
    client = SimpleMockHoundifyClient(
        response_patterns=test_config['response_patterns']
    )

    # Execute steps
    print("\n" + "="*70)
    print("EXECUTING MORNING ROUTINE")
    print("="*70)

    results = []
    for step_data in scenario['steps']:
        step_num = step_data['step_order']
        result = await execute_step(client, step_num, step_data)
        results.append(result)

        # Small pause between steps for readability
        await asyncio.sleep(0.1)

    # Summary
    print("\n" + "="*70)
    print("SCENARIO EXECUTION SUMMARY")
    print("="*70)

    passed = sum(1 for r in results if r.get('status') == 'PASS')
    failed = sum(1 for r in results if r.get('status') == 'FAIL')

    print(f"\nTotal Steps: {len(results)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")

    # Detailed results
    print("\n📊 DETAILED RESULTS:")
    print("-" * 70)
    for result in results:
        status_icon = '✅' if result.get('status') == 'PASS' else '❌'

        print(f"\n{status_icon} Step {result['step']}: {result['status']}")
        print(f"   Language: {result.get('language', 'N/A')}")
        print(f"   Query: \"{result.get('utterance', 'N/A')}\"")
        print(f"   Intent: {result.get('actual_intent', 'N/A')} (expected: {result.get('expected_intent', 'N/A')})")
        print(f"   Response: \"{result.get('spoken_response', 'N/A')}\"")

    # Final verdict
    print("\n" + "="*70)
    if failed == 0:
        print("🎉 SCENARIO COMPLETE!")
        print("\nThe user successfully:")
        print("   ✓ Checked the weather (knows how to dress)")
        print("   ✓ Reviewed their calendar (knows their schedule)")
        print("   ✓ Got directions to coffee (ready to leave)")
        print("\n   👔 User is now prepared for their day!")
        return 0
    else:
        print("❌ SCENARIO FAILED - Review results above")
        return 2


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(run_scenario())
        exit(exit_code)
    except FileNotFoundError:
        logger.error("❌ Scenario file not found: MORNING_ROUTINE_SCENARIO.json")
        exit(3)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(4)
