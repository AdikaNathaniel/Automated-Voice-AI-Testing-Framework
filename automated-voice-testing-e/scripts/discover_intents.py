#!/usr/bin/env python3
"""
Houndify Intent Discovery Tool

Automatically discovers Houndify intents by sending test queries to the API
and extracting CommandKind values from responses.

Usage:
    python discover_intents.py --queries-file discovery_queries.txt
    python discover_intents.py --query "What's the weather?"
    python discover_intents.py --interactive
"""

import os
import sys
import json
import time
import argparse
import ssl
import certifi
from datetime import datetime, UTC
from typing import Dict, List, Optional
from collections import defaultdict

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import houndify
from dotenv import load_dotenv

# Load environment variables from project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(project_root, '.env')
load_dotenv(dotenv_path=env_path, override=True)

# Fix SSL certificate verification issues
ssl._create_default_https_context = ssl._create_unverified_context


class HoundifyClient:
    """Client for making requests to Houndify API using official SDK"""

    def __init__(self, client_id: str, client_key: str):
        self.client_id = client_id
        self.client_key = client_key
        self.user_id = "intent_discovery_user"

    def query_text(self, query: str) -> Dict:
        """Send text query to Houndify and get response"""
        try:
            # Create client for this query
            client = houndify.TextHoundClient(
                self.client_id,
                self.client_key,
                self.user_id
            )

            # Send query and get response directly
            response = client.query(query)

            # Check for errors in response
            if isinstance(response, dict) and 'Status' in response:
                if response['Status'] == 'Error':
                    return {
                        'error': response.get('ErrorMessage', 'Unknown error'),
                        'query': query
                    }

            return response

        except Exception as e:
            return {
                'error': str(e),
                'query': query
            }


class IntentDiscovery:
    """Tool for discovering Houndify intents"""

    def __init__(self, client: HoundifyClient):
        self.client = client
        self.intent_to_queries: Dict[str, List[str]] = defaultdict(list)
        self.failed_queries: List[Dict] = []
        self.processed_count = 0

    def discover_intent(self, query: str, debug: bool = False) -> Optional[str]:
        """Send query and extract intent (CommandKind)"""
        print(f"  Testing: {query}")

        response = self.client.query_text(query)
        self.processed_count += 1

        # Debug: Show full response
        if debug:
            print(f"    🔍 DEBUG - Full response:")
            print(json.dumps(response, indent=2)[:1000])  # First 1000 chars
            print()

        # Check for errors
        if 'error' in response:
            print(f"    ❌ Error: {response['error']}")
            self.failed_queries.append({
                'query': query,
                'error': response['error'],
                'status_code': response.get('status_code')
            })
            return None

        # Extract CommandKind from response
        try:
            all_results = response.get('AllResults', [])
            if not all_results:
                print(f"    ⚠️  No results returned")
                print(f"    🔍 Response keys: {list(response.keys())}")
                self.failed_queries.append({
                    'query': query,
                    'error': 'No results in response',
                    'response_keys': list(response.keys())
                })
                return None

            # Get first result's CommandKind
            first_result = all_results[0]
            command_kind = first_result.get('CommandKind')

            if command_kind:
                print(f"    ✅ Intent: {command_kind}")

                # Show additional info if available
                if 'SpokenResponse' in first_result:
                    spoken = first_result['SpokenResponse'][:100]
                    print(f"    💬 Response: {spoken}...")

                self.intent_to_queries[command_kind].append(query)
                return command_kind
            else:
                print(f"    ⚠️  No CommandKind in response")
                print(f"    🔍 Result keys: {list(first_result.keys())}")
                self.failed_queries.append({
                    'query': query,
                    'error': 'No CommandKind field',
                    'result_keys': list(first_result.keys())
                })
                return None

        except Exception as e:
            print(f"    ❌ Parse error: {e}")
            import traceback
            if debug:
                traceback.print_exc()
            self.failed_queries.append({
                'query': query,
                'error': f'Parse error: {str(e)}'
            })
            return None

    def discover_from_file(self, filepath: str, rate_limit_delay: float = 0.5):
        """Discover intents from queries in file"""
        print(f"\n📖 Reading queries from: {filepath}\n")

        with open(filepath, 'r') as f:
            queries = []
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if line and not line.startswith('#'):
                    queries.append(line)

        print(f"Found {len(queries)} queries to process\n")
        print("=" * 80)

        for i, query in enumerate(queries, 1):
            print(f"\n[{i}/{len(queries)}]")
            self.discover_intent(query)

            # Rate limiting - be nice to the API
            if i < len(queries):
                time.sleep(rate_limit_delay)

        print("\n" + "=" * 80)

    def print_summary(self):
        """Print summary of discovered intents"""
        print("\n" + "=" * 80)
        print("DISCOVERY SUMMARY")
        print("=" * 80)

        print(f"\n📊 Statistics:")
        print(f"  Total queries processed: {self.processed_count}")
        print(f"  Unique intents found: {len(self.intent_to_queries)}")
        print(f"  Successful queries: {sum(len(queries) for queries in self.intent_to_queries.values())}")
        print(f"  Failed queries: {len(self.failed_queries)}")

        if self.intent_to_queries:
            print(f"\n✅ Discovered Intents:")
            for intent, queries in sorted(self.intent_to_queries.items()):
                print(f"\n  📌 {intent}")
                print(f"     Queries: {len(queries)}")
                for query in queries[:3]:  # Show first 3 examples
                    print(f"       - {query}")
                if len(queries) > 3:
                    print(f"       ... and {len(queries) - 3} more")

        if self.failed_queries:
            print(f"\n❌ Failed Queries ({len(self.failed_queries)}):")
            for failure in self.failed_queries[:10]:  # Show first 10
                print(f"  - {failure['query']}")
                print(f"    Error: {failure['error']}")
            if len(self.failed_queries) > 10:
                print(f"  ... and {len(self.failed_queries) - 10} more")

    def save_results(self, output_file: str = "discovered_intents.json"):
        """Save results to JSON file"""
        results = {
            'discovered_at': datetime.now(UTC).isoformat(),
            'summary': {
                'total_queries': self.processed_count,
                'unique_intents': len(self.intent_to_queries),
                'successful_queries': sum(len(q) for q in self.intent_to_queries.values()),
                'failed_queries': len(self.failed_queries)
            },
            'intents': dict(self.intent_to_queries),
            'failures': self.failed_queries
        }

        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\n💾 Results saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Discover Houndify intents by testing queries'
    )
    parser.add_argument(
        '--queries-file',
        default='discovery_queries.txt',
        help='File containing queries (one per line)'
    )
    parser.add_argument(
        '--query',
        help='Single query to test'
    )
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Interactive mode - enter queries manually'
    )
    parser.add_argument(
        '--output',
        default='discovered_intents.json',
        help='Output file for results'
    )
    parser.add_argument(
        '--rate-limit',
        type=float,
        default=0.5,
        help='Delay between requests in seconds (default: 0.5)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug output showing full API responses'
    )

    args = parser.parse_args()

    # Get credentials from environment
    client_id = os.getenv('SOUNDHOUND_CLIENT_ID')
    client_key = os.getenv('SOUNDHOUND_API_KEY')

    if not client_id or not client_key:
        print("❌ Error: SOUNDHOUND_CLIENT_ID and SOUNDHOUND_API_KEY must be set")
        print("   Make sure your .env file is configured correctly")
        sys.exit(1)

    print("=" * 80)
    print("HOUNDIFY INTENT DISCOVERY TOOL")
    print("=" * 80)
    print(f"\n🔑 Using Client ID: {client_id[:20]}...")

    # Create client and discovery tool
    client = HoundifyClient(client_id, client_key)
    discovery = IntentDiscovery(client)

    try:
        if args.query:
            # Single query mode
            print(f"\n🔍 Testing single query\n")
            discovery.discover_intent(args.query, debug=args.debug)

        elif args.interactive:
            # Interactive mode
            print(f"\n💬 Interactive mode (type 'quit' to exit)\n")
            while True:
                query = input("Enter query: ").strip()
                if query.lower() in ['quit', 'exit', 'q']:
                    break
                if query:
                    discovery.discover_intent(query, debug=args.debug)
                    print()

        else:
            # File mode (default)
            queries_file = args.queries_file
            if not os.path.exists(queries_file):
                print(f"❌ Error: Queries file not found: {queries_file}")
                sys.exit(1)

            discovery.discover_from_file(queries_file, args.rate_limit)

        # Print summary and save results
        discovery.print_summary()

        if discovery.processed_count > 0:
            discovery.save_results(args.output)

        print("\n✨ Discovery complete!")

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        discovery.print_summary()
        if discovery.processed_count > 0:
            discovery.save_results(args.output)

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
