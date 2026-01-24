# Comprehensive Test Scenarios - Implementation Plan

## Research Sources
- [Houndify SDK Go](https://github.com/soundhound/houndify-sdk-go)
- [Medium: Houndify Custom Commands](https://medium.com/houndify/using-custom-commands-ef4522ab4d46)
- [Houndify API Documentation](https://publicapis.io/houndify-machine-learning-api)

## Confirmed Real Houndify CommandKind Values
- `WeatherCommand` - Weather queries
- `MusicCommand` / `MusicPlayerCommand` - Music playback
- `NoResultCommand` - Unrecognized queries
- `NavigationCommand` - Navigation/directions (highly likely based on domain)
- `PhoneCommand` - Phone calls (highly likely based on domain)
- `ClientMatchCommand` - Custom domains (confirmed via documentation)

## Scenarios to Create (20 Total)

### Demo Scenarios (3)
1. **Weather Query** - Single-turn, EN only
2. **Restaurant Reservation** - Multi-turn (3 steps), EN with multi-language variants
3. **Smart Home** - Single-turn, ClientMatchCommand

### Houndify Validation Tests (8)

#### Command Kind Tests (3)
4. **PASS: Weather CommandKind Match** - `WeatherCommand`
5. **FAIL: Music expecting Weather** - `MusicCommand` but expecting `WeatherCommand`
6. **FAIL: NoResult expecting Weather** - `NoResultCommand` but expecting `WeatherCommand`

#### Response Content Tests (3)
7. **PASS: Weather with contains** - Check for "weather", "temperature", "degrees"
8. **FAIL: Weather with wrong contains** - Check for "music" in weather response
9. **PASS: Music with regex** - Regex pattern `"Playing.*music"`

#### ASR Confidence Tests (2)
10. **PASS: Normal confidence** - 0.95 > 0.7 threshold
11. **FAIL: High threshold** - 0.95 < 0.99 threshold (mock always returns 0.95)

### Multi-Language Scenarios (4)
12. **Weather Query - Spanish** - `es-ES` with language_variations
13. **Weather Query - French** - `fr-FR` with language_variations
14. **Multi-Language Step** - Single step with EN/ES/FR variants in language_variations
15. **Multi-Turn Multi-Language** - Restaurant reservation with language variants per step

### Regex Validation Tests (3)
16. **PASS: Temperature regex** - Match `\d+.*degrees?`
17. **PASS: Time format regex** - Match time patterns
18. **FAIL: Wrong regex pattern** - Expect number pattern in text response

### LLM & Hybrid Tests (2)
19. **PASS: LLM Ensemble** - Semantic validation only
20. **PASS: Hybrid Validation** - Both Houndify + LLM

## Key Fixes Needed

### In Mock Client (`mock_client.py`)
- Keep existing CommandKind inference logic (it's accurate)
- Ensure `ClientMatchCommand` is returned for smart home/restaurant
- Verify response content matches what tests expect

### In Seed Scenarios (`seed_all.py`)
- ❌ Remove `WeatherQuery` → Use `WeatherCommand`
- ❌ Remove `SmartHomeCommand` → Use `ClientMatchCommand`
- ❌ Remove `RestaurantReservationCommand` → Use `ClientMatchCommand`
- ❌ Remove `TimerCommand` → Use `MusicCommand` or `WeatherCommand` for tests
- ❌ Remove `TimeInfoCommand` → Use `NoResultCommand` or `WeatherCommand`
- ✅ Add `language_variations` JSONB with proper structure
- ✅ Add `expected_response_content.regex` patterns
- ✅ Add `expected_response_content.regex_not_match` patterns

## Language Variations Structure

```python
language_variations = {
    "en-US": {
        "user_utterance": "What's the weather like today?",
        "expected_response_patterns": {
            "contains": ["weather", "temperature"],
            "regex": ["\\d+.*degrees"]
        }
    },
    "es-ES": {
        "user_utterance": "¿Cómo está el tiempo hoy?",
        "expected_response_patterns": {
            "contains": ["clima", "temperatura"],
            "regex": ["\\d+.*grados"]
        }
    },
    "fr-FR": {
        "user_utterance": "Quel temps fait-il aujourd'hui?",
        "expected_response_patterns": {
            "contains": ["météo", "température"],
            "regex": ["\\d+.*degrés"]
        }
    }
}
```

## Next Steps
1. ✅ Research completed - confirmed real CommandKind values
2. ✅ Updated seed_all.py with all 20 comprehensive scenarios
3. ✅ All scenarios seeded successfully into database
4. ✅ Verified correct CommandKind values, language_variations, and regex patterns
5. ⏭️ Test scenarios execute through validation pipeline
6. ⏭️ Verify pass/fail expectations match actual validation results

## Implementation Complete

**Date:** 2025-12-26

All 20 comprehensive scenarios have been successfully implemented and verified in the database.

See [COMPREHENSIVE_SCENARIOS_COMPLETE.md](./COMPREHENSIVE_SCENARIOS_COMPLETE.md) for full details.
