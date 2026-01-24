# Houndify Intents Reference

**Generated:** November 24, 2025
**Source:** Automated intent discovery via Houndify API
**Total Intents Discovered:** 20
**Successful Queries:** 161/220 (73%)

This document serves as a reference for creating test cases in the Voice AI Testing Framework.

---

## Table of Contents

- [Core Intents](#core-intents)
- [Music & Media](#music--media)
- [Navigation & Location](#navigation--location)
- [Travel & Transportation](#travel--transportation)
- [Time & Scheduling](#time--scheduling)
- [Communication](#communication)
- [Device Control](#device-control)
- [Utility & Calculation](#utility--calculation)
- [Error & Special Cases](#error--special-cases)

---

## Core Intents

### 1. InformationCommand
**Purpose:** General knowledge queries, facts, calculations, and information retrieval

**Query Count:** 34 successful queries

**Example Queries:**
```
✅ "What's the weather in San Francisco?"
   → Response: "The weather is fifty nine degrees and sunny in San Francisco."

✅ "What's 5 plus 7?"
   → Response: "twelve"

✅ "Who is Barack Obama?"
   → Response: "Barack Hussein Obama II is an American politician..."

✅ "What is the capital of France?"
   → Response: "The Capital of France is Paris."

✅ "Convert 50 miles to kilometers"
   → Response: "80.4672 kilometers"

✅ "What's 100 degrees Fahrenheit in Celsius?"
   → Response: "37.778 degrees Celsius"
```

**Common Use Cases:**
- Weather queries (with location specified)
- Mathematical calculations
- Unit conversions
- General knowledge questions
- Historical facts
- Geographic information

**Test Case Template:**
```json
{
  "test_case_name": "Weather Query - San Francisco",
  "input_text": "What's the weather in San Francisco?",
  "expected_outcome": {
    "intent": "InformationCommand",
    "entities": {
      "Location": "San Francisco"
    },
    "confidence_threshold": 0.85
  }
}
```

---

### 2. DictionaryCommand
**Purpose:** Word definitions and linguistic information

**Query Count:** 3 successful queries

**Example Queries:**
```
✅ "What is quantum physics?"
   → Response: "Definition of quantum physics: the branch of physics based on quantum theory."

✅ "What is photosynthesis?"
   → Response: "Definition of photosynthesis: synthesis of compounds with the aid of radiant energy..."

✅ "What's trending?"
   → Response: "Definition of trend: a general direction in which something tends to move."
```

**Test Case Template:**
```json
{
  "test_case_name": "Dictionary Definition Query",
  "input_text": "What is photosynthesis?",
  "expected_outcome": {
    "intent": "DictionaryCommand",
    "validation_rules": {
      "response_contains": ["Definition", "photosynthesis"]
    }
  }
}
```

---

## Music & Media

### 3. MusicCommand
**Purpose:** Music playback and search

**Query Count:** 7 successful queries

**Example Queries:**
```
✅ "Play some jazz"
   → Response: "I couldn't find any songs that match your query."
   → Note: Requires music service integration

✅ "Play Bohemian Rhapsody by Queen"
   → Response: "Auto-playback is not available. Here are the songs matching Bohemian Rhapsody."

✅ "What are the top stories?"
   → Response: "Here are some of the top songs by Stories."
```

**Test Case Template:**
```json
{
  "test_case_name": "Music Search - Specific Song",
  "input_text": "Play Bohemian Rhapsody by Queen",
  "expected_outcome": {
    "intent": "MusicCommand",
    "entities": {
      "SongTitle": "Bohemian Rhapsody",
      "Artist": "Queen"
    }
  }
}
```

---

### 4. MusicPlayerCommand
**Purpose:** Music player controls (play, pause, skip)

**Query Count:** 3 successful queries

**Example Queries:**
```
✅ "Play music"
   → Response: "This version of this client does not support that music player control command."

✅ "Skip this song"
   → Response: "This version of this client does not support that music player control command."

✅ "Pause the music"
   → Response: "This version of this client does not support that music player control command."
```

**Note:** Requires music player integration to function fully.

---

### 5. SoundHoundNowCommand
**Purpose:** Audio identification (song recognition)

**Query Count:** 2 successful queries

**Example Queries:**
```
✅ "What song is this?"
   → Response: "This client does not support audio identification."

✅ "Who sings this song?"
   → Response: "This client does not support audio identification."
```

**Note:** Requires audio input capability.

---

## Navigation & Location

### 6. MapCommand
**Purpose:** Directions and location mapping

**Query Count:** 3 successful queries

**Example Queries:**
```
✅ "Get directions to 123 Main Street"
   → Response: "Here are directions to 123 Main street Delta."

✅ "How do I get to San Francisco?"
   → Response: "Here are directions to San Francisco."

✅ "Find a post office"
   → Response: "Here is Post Office."
```

**Test Case Template:**
```json
{
  "test_case_name": "Get Directions",
  "input_text": "How do I get to San Francisco?",
  "expected_outcome": {
    "intent": "MapCommand",
    "entities": {
      "Destination": "San Francisco"
    },
    "validation_rules": {
      "response_contains": ["directions"]
    }
  }
}
```

---

### 7. NavigationControlCommand
**Purpose:** Navigation features (ETA, route options)

**Query Count:** 1 successful query

**Example Queries:**
```
✅ "What's my ETA?"
   → Response: "This client does not support the command to estimate arrival time."
```

**Note:** Requires active navigation session.

---

## Travel & Transportation

### 8. FlightBookingCommand
**Purpose:** Flight search and booking

**Query Count:** 4 successful queries

**Example Queries:**
```
✅ "Find cheap flights to Miami"
   → Response: "What is the departure date?"

✅ "Book a flight to Chicago"
   → Response: "What is the departure date?"

✅ "Find one-way flights"
   → Response: "Where did you want to travel?"

✅ "Show me direct flights only"
   → Response: "Where did you want to travel?"
```

**Behavior:** Multi-turn conversation - requests additional details

**Test Case Template:**
```json
{
  "test_case_name": "Flight Search",
  "input_text": "Find cheap flights to Miami",
  "expected_outcome": {
    "intent": "FlightBookingCommand",
    "entities": {
      "Destination": "Miami"
    },
    "conversation_state": {
      "requires_followup": true,
      "expected_question": "departure date"
    }
  }
}
```

---

### 9. FlightStatusModeCommand
**Purpose:** Flight status and information

**Query Count:** 3 successful queries

**Example Queries:**
```
✅ "Find flights to New York"
   → Response: "Which city or airport is the flight departing from?"

✅ "When does my flight leave?"
   → Response: "What is the airline of the flight?"

✅ "What time does the flight arrive?"
   → Response: "What is the airline of the flight?"
```

**Behavior:** Multi-turn conversation - requests flight details

---

## Time & Scheduling

### 10. CalendarCommand
**Purpose:** Calendar events, meetings, and reminders

**Query Count:** 10 successful queries

**Example Queries:**
```
✅ "What's on my calendar today?"
   → Response: "Here is what is on your calendar for today."

✅ "Schedule a meeting for 3pm"
   → Response: "Okay, let me create your calendar event. What should I title your event?"

✅ "Set a reminder to buy milk"
   → Response: "Okay, let me create your calendar event. What date should I set your event for?"

✅ "What do I have tomorrow?"
   → Response: "Here's what you have on your calendar."

✅ "What meetings do I have this week?"
   → Response: "Here's what you have on your calendar."
```

**Test Case Template:**
```json
{
  "test_case_name": "Schedule Calendar Event",
  "input_text": "Schedule a meeting for 3pm",
  "expected_outcome": {
    "intent": "CalendarCommand",
    "entities": {
      "Time": "3pm"
    },
    "conversation_state": {
      "requires_followup": true,
      "expected_question": "title"
    }
  }
}
```

---

### 11. AlarmCommand
**Purpose:** Set and manage alarms

**Query Count:** 2 successful queries

**Example Queries:**
```
✅ "Set an alarm for 7am"
   → Response: "Setting an alarm is not supported by this client."

✅ "Cancel my alarm"
   → Response: "This client does not support deleting alarms."
```

**Note:** Requires device integration.

---

### 12. TimerCommand
**Purpose:** Set and manage timers

**Query Count:** 1 successful query

**Example Queries:**
```
✅ "Set a timer for 10 minutes"
   → Response: "Setting a timer is not supported by this client."
```

**Note:** Requires device integration.

---

## Communication

### 13. PhoneCommand
**Purpose:** Make phone calls

**Query Count:** 4 successful queries

**Example Queries:**
```
✅ "Dial 555-1234"
   → Response: "Placing phone calls is not supported by this client."

✅ "Call the last number"
   → Response: "Placing phone calls is not supported by this client."

✅ "Redial"
   → Response: "Placing phone calls is not supported by this client."

✅ "Show my contacts"
   → Response: "Showing contacts is not supported by this client."
```

**Note:** Requires phone integration and contact sync.

---

### 14. SMSCommand
**Purpose:** Send text messages

**Query Count:** 1 successful query

**Example Queries:**
```
✅ "Send a text to Sarah"
   → Response: "Sorry, this client doesn't support text messaging."
```

**Note:** Requires messaging integration and contact sync.

---

## Device Control

### 15. DeviceControlCommand
**Purpose:** Control device features (volume, etc.)

**Query Count:** 1 successful query

**Example Queries:**
```
✅ "Turn up the volume"
   → Response: "This client does not support the command to adjust the volume."
```

**Note:** Requires device control integration.

---

## Utility & Calculation

### 16. TipCalculatorCommand
**Purpose:** Calculate tips

**Query Count:** 1 successful query

**Example Queries:**
```
✅ "Calculate the tip on 45 dollars"
   → Response: "A 15 percent tip is 6 dollars and 75 cents"
```

**Test Case Template:**
```json
{
  "test_case_name": "Tip Calculation",
  "input_text": "Calculate the tip on 45 dollars",
  "expected_outcome": {
    "intent": "TipCalculatorCommand",
    "entities": {
      "Amount": 45,
      "Currency": "dollars"
    },
    "validation_rules": {
      "response_contains": ["6 dollars", "75 cents"]
    }
  }
}
```

---

### 17. CurrencyConverterCommand
**Purpose:** Currency conversion and crypto prices

**Query Count:** 1 successful query

**Example Queries:**
```
✅ "How much is Bitcoin worth?"
   → Response: "88821 U S dollars and 80 cents"
```

**Test Case Template:**
```json
{
  "test_case_name": "Cryptocurrency Price",
  "input_text": "How much is Bitcoin worth?",
  "expected_outcome": {
    "intent": "CurrencyConverterCommand",
    "entities": {
      "Currency": "Bitcoin"
    },
    "validation_rules": {
      "response_contains": ["dollars"]
    }
  }
}
```

---

## Error & Special Cases

### 18. ErrorCommand
**Purpose:** Errors requiring additional context or location

**Query Count:** 21 successful queries

**Example Queries:**
```
❌ "What's the weather?"
   → Response: "This weather information is not available. Turn on location services..."
   → Solution: Add location → "What's the weather in San Francisco?"

❌ "What time is it?"
   → Response: "This information is not available. Turn on location services..."
   → Solution: Add location → "What time is it in London?"

❌ "Call John"
   → Response: "Contact information is not available until it is synchronized..."
   → Solution: Sync contacts with Hound cloud
```

**Common Causes:**
1. Missing location context
2. Missing required entities
3. Service not configured (contacts, calendar)

**How to Handle:**
- For test cases, always provide complete context (location, time zone, etc.)
- Use specific queries rather than implicit ones
- Test both with and without context to validate error handling

---

### 19. NoResultCommand
**Purpose:** Queries that found no matching results

**Query Count:** 58 successful queries

**Example Queries:**
```
⚠️  "Book a table at Pizza Palace"
   → Response: (empty)

⚠️  "What's the stock price of Apple?"
   → Response: (empty)

⚠️  "Who won the Super Bowl?"
   → Response: (empty)
```

**Common Causes:**
1. Domain not enabled (Stocks, Sports, Restaurants)
2. Query requires real-time data not available
3. Query too vague or ambiguous

**Note:** Many of these may work with proper domain enablement in Houndify account.

---

### 20. ClientCommand
**Purpose:** Client-specific commands

**Query Count:** 1 successful query

**Example Queries:**
```
✅ "What time does Olive Garden close?"
   → Response: (client-specific response)
```

**Note:** Behavior depends on client configuration and enabled domains.

---

## Best Practices for Test Cases

### 1. Always Provide Context
```
❌ Bad:  "What's the weather?"
✅ Good: "What's the weather in San Francisco?"

❌ Bad:  "What time is it?"
✅ Good: "What time is it in Tokyo?"
```

### 2. Use Specific Queries
```
❌ Vague:    "Find restaurants"
✅ Specific: "Find Italian restaurants in San Francisco"

❌ Vague:    "Book a flight"
✅ Specific: "Find flights from New York to Miami on December 1st"
```

### 3. Test Multi-Turn Conversations
```json
{
  "conversation_flow": [
    {
      "user": "Find flights to New York",
      "expected_intent": "FlightBookingCommand",
      "expected_response_contains": ["departure"]
    },
    {
      "user": "From Los Angeles",
      "expected_response_contains": ["date"]
    },
    {
      "user": "December 15th",
      "expected_response_contains": ["flight options"]
    }
  ]
}
```

### 4. Validate Entity Extraction
```json
{
  "input_text": "What's the weather in San Francisco on Friday?",
  "expected_entities": {
    "Location": "San Francisco",
    "Date": "Friday"
  }
}
```

### 5. Check Confidence Thresholds
```json
{
  "validation": {
    "min_confidence": 0.85,
    "expected_intent": "InformationCommand",
    "alternative_intents_allowed": false
  }
}
```

---

## Domain Enablement Notes

Some intents require specific domains to be enabled in your Houndify account:

| Intent Category | Required Domain | Status |
|----------------|-----------------|---------|
| Weather | Weather | ✅ Enabled |
| Music | Music | ✅ Enabled |
| Flights | Travel | ✅ Enabled |
| Calendar | Productivity | ✅ Enabled |
| Restaurants | Local Search | ⚠️  Partial |
| Stocks/Finance | Finance | ❌ Not Enabled |
| Sports | Sports | ❌ Not Enabled |
| Movies | Entertainment | ❌ Not Enabled |
| Shopping | Commerce | ❌ Not Enabled |
| Translation | Translation | ❌ Not Enabled |

**To enable additional domains:**
1. Log into houndify.com
2. Select your client application
3. Navigate to "Domains" section
4. Enable desired domains

---

## Rate Limiting

**Observed Limits:**
- Approximately 160-200 queries per session before rate limit
- Error: "Invalid ID or Key" when limit exceeded
- Likely resets after 24 hours

**Recommendations:**
- Implement rate limiting in test execution (0.5-1 second delay between queries)
- Batch test runs to stay within limits
- Consider upgrading to paid tier for higher limits

---

## Related Files

- **Full Discovery Results:** `/discovered_intents.json`
- **Discovery Logs:** `/scripts/intent_discovery_log.txt`
- **Test Queries:** `/scripts/discovery_queries.txt`
- **Failed Queries:** `/scripts/failed_queries.txt`
- **Discovery Script:** `/scripts/discover_intents.py`

---

## Appendix: Intent Statistics

### Intent Distribution

| Intent | Query Count | Percentage |
|--------|-------------|------------|
| InformationCommand | 34 | 21.1% |
| NoResultCommand | 58 | 36.0% |
| ErrorCommand | 21 | 13.0% |
| CalendarCommand | 10 | 6.2% |
| MusicCommand | 7 | 4.3% |
| FlightBookingCommand | 4 | 2.5% |
| PhoneCommand | 4 | 2.5% |
| MusicPlayerCommand | 3 | 1.9% |
| Others (12 intents) | 20 | 12.4% |

### Success Rate by Category

| Category | Success | Failed | Rate |
|----------|---------|--------|------|
| Math & Calculation | 10 | 0 | 100% |
| Weather (with location) | 2 | 0 | 100% |
| Weather (no location) | 0 | 8 | 0% |
| Calendar | 10 | 0 | 100% |
| Music | 10 | 0 | 100% |
| Flight | 7 | 0 | 100% |
| General Knowledge | 15 | 5 | 75% |

---

**Last Updated:** November 24, 2025
**Next Update:** After retry of failed queries (wait 24h for rate limit reset)
