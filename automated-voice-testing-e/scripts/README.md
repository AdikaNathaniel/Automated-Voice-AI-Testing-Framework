# Intent Discovery Scripts

Tools for discovering Houndify intents automatically.

## Files

- **`discover_intents.py`** - Main discovery script
- **`discovery_queries.txt`** - Pre-written test queries (200+ queries covering 25+ domains)
- **`discovered_intents.json`** - Output file with discovered intents (generated after running script)

## Quick Start

### Run discovery with all pre-written queries:
```bash
cd scripts
python3 discover_intents.py
```

This will:
- Process all 200+ queries from `discovery_queries.txt`
- Call Houndify API for each query
- Extract `CommandKind` (intent) from responses
- Save results to `discovered_intents.json`
- Print summary of discovered intents

### Test a single query:
```bash
python3 discover_intents.py --query "What's the weather?"
```

### Interactive mode (manual testing):
```bash
python3 discover_intents.py --interactive
```

### Custom queries file:
```bash
python3 discover_intents.py --queries-file my_queries.txt
```

### Custom output file:
```bash
python3 discover_intents.py --output my_results.json
```

## Query File Format

The `discovery_queries.txt` file contains one query per line:
- Lines starting with `#` are comments (ignored)
- Empty lines are ignored
- All other lines are treated as queries

Example:
```
# Weather queries
What's the weather?
Will it rain tomorrow?

# Restaurant queries
Book a table at Pizza Palace
Find Italian restaurants
```

## Output Format

The script generates `discovered_intents.json` with this structure:

```json
{
  "discovered_at": "2025-01-24T10:30:00",
  "summary": {
    "total_queries": 200,
    "unique_intents": 45,
    "successful_queries": 185,
    "failed_queries": 15
  },
  "intents": {
    "WeatherForecast": [
      "What's the weather?",
      "Will it rain tomorrow?"
    ],
    "ClientMatchRestaurantReservation": [
      "Book a table at Pizza Palace",
      "Reserve a table for 4"
    ]
  },
  "failures": [
    {
      "query": "Some invalid query",
      "error": "Error message"
    }
  ]
}
```

## Rate Limiting

By default, the script waits 0.5 seconds between requests. Adjust with `--rate-limit`:

```bash
python3 discover_intents.py --rate-limit 1.0  # Wait 1 second between requests
```

## Use Cases

1. **Discover available intents** - Run full discovery to see what Houndify supports
2. **Validate queries** - Test if your queries map to expected intents
3. **Build test cases** - Use discovered intents to create accurate test cases
4. **Documentation** - Generate reference of intent names for your team

## Pre-Written Query Coverage

The `discovery_queries.txt` file includes queries for:

- ✅ Weather (10 queries)
- ✅ Restaurant (10 queries)
- ✅ Music (10 queries)
- ✅ Navigation (10 queries)
- ✅ Local Business (10 queries)
- ✅ Hotel/Travel (10 queries)
- ✅ Flights (10 queries)
- ✅ Stocks/Finance (10 queries)
- ✅ Sports (10 queries)
- ✅ Math/Calculator (10 queries)
- ✅ Time/Date/Alarm (10 queries)
- ✅ General Knowledge (10 queries)
- ✅ News (10 queries)
- ✅ Home Automation (10 queries)
- ✅ Phone/Contacts (10 queries)
- ✅ Calendar/Reminders (10 queries)
- ✅ Shopping (10 queries)
- ✅ Movies (10 queries)
- ✅ Uber/Ride Sharing (10 queries)
- ✅ Translation (10 queries)
- ✅ Unit Conversion (10 queries)
- ✅ Miscellaneous (10 queries)

**Total: 220+ queries covering 22 domains**

## Next Steps

After running discovery:

1. Review `discovered_intents.json` to see all found intents
2. Use the intent names when creating test cases in the system
3. Add any missing queries to `discovery_queries.txt` and re-run
4. Share the discovered intents with your team for reference

## Troubleshooting

**Error: "SOUNDHOUND_CLIENT_ID and SOUNDHOUND_API_KEY must be set"**
- Make sure your `.env` file has valid Houndify credentials
- The script looks for `.env` in the project root

**Many queries failing**
- Check your Houndify account has enabled the relevant domains
- Verify your API credentials are correct
- Some domains may not be available in your region/plan

**Slow execution**
- Increase `--rate-limit` value (more delay between requests)
- Or reduce the number of queries in `discovery_queries.txt`
