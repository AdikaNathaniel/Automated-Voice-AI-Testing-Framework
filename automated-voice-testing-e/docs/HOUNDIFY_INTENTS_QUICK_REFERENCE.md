# Houndify Intents - Quick Reference

**20 Discovered Intents | 161 Successful Queries | 73% Success Rate**

---

## 🎯 Most Common Intents

### InformationCommand (34 queries)
General knowledge, math, weather (with location), facts
```
"What's the weather in San Francisco?"
"What's 5 plus 7?"
"Who is Barack Obama?"
"Convert 50 miles to kilometers"
```

### CalendarCommand (10 queries)
Scheduling, reminders, calendar events
```
"What's on my calendar today?"
"Schedule a meeting for 3pm"
"Set a reminder to buy milk"
```

### MusicCommand (7 queries)
Music search and playback
```
"Play Bohemian Rhapsody by Queen"
"Play some jazz"
```

---

## 📋 Complete Intent List

| # | Intent | Use Case | Example |
|---|--------|----------|---------|
| 1 | **InformationCommand** | Knowledge, math, weather | "What's 5 + 7?" |
| 2 | **CalendarCommand** | Events, reminders | "Schedule meeting for 3pm" |
| 3 | **MusicCommand** | Music playback | "Play jazz music" |
| 4 | **NoResultCommand** | No results found | "Book a table at Pizza Palace" |
| 5 | **ErrorCommand** | Missing context | "What's the weather?" (no location) |
| 6 | **FlightBookingCommand** | Flight search | "Find flights to Miami" |
| 7 | **PhoneCommand** | Make calls | "Dial 555-1234" |
| 8 | **FlightStatusModeCommand** | Flight info | "When does my flight leave?" |
| 9 | **MusicPlayerCommand** | Player controls | "Pause the music" |
| 10 | **MapCommand** | Directions | "Get directions to San Francisco" |
| 11 | **DictionaryCommand** | Definitions | "What is photosynthesis?" |
| 12 | **AlarmCommand** | Alarms | "Set alarm for 7am" |
| 13 | **SoundHoundNowCommand** | Song ID | "What song is this?" |
| 14 | **TipCalculatorCommand** | Tip calc | "Calculate tip on 45 dollars" |
| 15 | **CurrencyConverterCommand** | Currency | "How much is Bitcoin worth?" |
| 16 | **TimerCommand** | Timers | "Set timer for 10 minutes" |
| 17 | **NavigationControlCommand** | Nav features | "What's my ETA?" |
| 18 | **SMSCommand** | Text messages | "Send text to Sarah" |
| 19 | **DeviceControlCommand** | Device control | "Turn up the volume" |
| 20 | **ClientCommand** | Client-specific | "What time does Olive Garden close?" |

---

## ⚠️ Common Pitfalls

### Always Include Location
```diff
- "What's the weather?" → ErrorCommand
+ "What's the weather in San Francisco?" → InformationCommand ✓

- "What time is it?" → ErrorCommand
+ "What time is it in Tokyo?" → InformationCommand ✓
```

### Be Specific
```diff
- "Find restaurants" → NoResultCommand
+ "Find Italian restaurants in San Francisco" → Better results

- "Book a flight" → Requires follow-up
+ "Find flights from NYC to Miami on Dec 1st" → More complete
```

### Multi-Turn Conversations
Some intents require follow-up:
- FlightBookingCommand → asks for departure date
- CalendarCommand → asks for event title
- FlightStatusModeCommand → asks for airline

---

## 🧪 Test Case Template

```json
{
  "test_case_name": "Weather Query - Specific Location",
  "input_text": "What's the weather in San Francisco?",
  "expected_outcome": {
    "intent": "InformationCommand",
    "entities": {
      "Location": "San Francisco"
    },
    "confidence_threshold": 0.85,
    "validation_rules": {
      "response_contains": ["weather", "San Francisco"]
    }
  }
}
```

---

## 📊 Domain Status

| Domain | Status | Intents Working |
|--------|--------|-----------------|
| Weather | ✅ Enabled | InformationCommand |
| Music | ✅ Enabled | MusicCommand, MusicPlayerCommand |
| Calendar | ✅ Enabled | CalendarCommand |
| Flights | ✅ Enabled | FlightBookingCommand, FlightStatusModeCommand |
| Maps | ✅ Enabled | MapCommand |
| Finance | ❌ Disabled | CurrencyConverterCommand (partial) |
| Sports | ❌ Disabled | NoResultCommand |
| Restaurants | ⚠️ Partial | NoResultCommand for most |
| Movies | ❌ Disabled | Rate limit hit |
| Shopping | ❌ Disabled | Rate limit hit |

---

## 🚀 Quick Start

1. **Choose an intent** from the list above
2. **Write specific query** with all required context
3. **Set expected intent** in test case
4. **Add validation rules** (entities, confidence, response)
5. **Run test** and verify results

---

## 📁 Files

- **Full Reference:** `/docs/HOUNDIFY_INTENTS_REFERENCE.md`
- **Discovery Results:** `/discovered_intents.json`
- **Discovery Script:** `/scripts/discover_intents.py`
- **Test Queries:** `/scripts/discovery_queries.txt`

---

**Last Updated:** November 24, 2025
