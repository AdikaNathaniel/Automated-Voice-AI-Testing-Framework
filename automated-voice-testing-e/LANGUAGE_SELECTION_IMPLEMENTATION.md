# Language Selection Implementation Summary

**Date:** December 24, 2024
**Status:** ✅ Backend Complete, Frontend UI Pending

---

## What Was Implemented

### 1. ✅ Updated Scenario Structure

**File:** [backend/scripts/seed_morning_routine_fixed.py](backend/scripts/seed_morning_routine_fixed.py)

**Changes:**
- ALL 3 steps now have both English and French language variants
- Total DB rows: 6 (2 variants × 3 steps)
- Scenario ID: `be301282-f3d2-462b-bc0c-a73813e45ba9`

**Structure:**
```
Step 1 (order=1): Weather - English variant + French variant
Step 2 (order=2): Calendar - English variant + French variant
Step 3 (order=3): Directions - English variant + French variant
```

### 2. ✅ Backend Language Filtering

**File:** [backend/services/multi_turn_execution_service.py](backend/services/multi_turn_execution_service.py)

**New Method:** `_filter_steps_by_language()`
- Filters steps based on `language_codes` parameter
- Groups steps by `step_order`
- Selects appropriate variants based on language preference

**Behavior:**
- `language_codes=None` → Executes ALL variants (6 steps)
- `language_codes=["en-US"]` → Executes ONLY English variants (3 steps)
- `language_codes=["fr-FR"]` → Executes ONLY French variants (3 steps)
- `language_codes=["en-US", "fr-FR"]` → Executes BOTH (6 steps)

### 3. ✅ API Endpoint Updated

**File:** [backend/api/routes/multi_turn.py](backend/api/routes/multi_turn.py)

**New Request Schema:**
```python
class ExecuteScenarioRequest(BaseModel):
    language_codes: Optional[List[str]] = None  # ["en-US", "fr-FR"]
    suite_run_id: Optional[UUID] = None
```

**Endpoint:** `POST /api/v1/multi-turn/execute/{script_id}`

**Request Body:**
```json
{
  "language_codes": ["en-US"],
  "suite_run_id": null
}
```

### 4. ✅ Frontend Type Updated

**File:** [frontend/src/types/multiTurn.ts](frontend/src/types/multiTurn.ts)

```typescript
export interface ExecuteScenarioRequest {
  script_id: string;
  language_codes?: string[]; // Optional language filter
}
```

---

## Testing the Backend

### Test 1: Execute Only English Variants

```bash
curl -X POST http://localhost:8000/api/v1/multi-turn/execute/be301282-f3d2-462b-bc0c-a73813e45ba9 \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "language_codes": ["en-US"]
  }'
```

**Expected:** 3 steps executed (English variants only)

### Test 2: Execute Only French Variants

```bash
curl -X POST http://localhost:8000/api/v1/multi-turn/execute/be301282-f3d2-462b-bc0c-a73813e45ba9 \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "language_codes": ["fr-FR"]
  }'
```

**Expected:** 3 steps executed (French variants only)

### Test 3: Execute All Variants

```bash
curl -X POST http://localhost:8000/api/v1/multi-turn/execute/be301282-f3d2-462b-bc0c-a73813e45ba9 \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "language_codes": null
  }'
```

**Expected:** 6 steps executed (all variants)

### Test 4: Execute Both English and French

```bash
curl -X POST http://localhost:8000/api/v1/multi-turn/execute/be301282-f3d2-462b-bc0c-a73813e45ba9 \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "language_codes": ["en-US", "fr-FR"]
  }'
```

**Expected:** 6 steps executed (both language variants)

---

## What's Still Needed: Frontend UI

### Required Changes

1. **Update Frontend Service**
   - File: `frontend/src/services/multiTurn.service.ts`
   - Modify `executeScenario()` to accept and pass `language_codes`

2. **Create Language Selection UI Component**
   - Location: `frontend/src/components/Scenarios/LanguageSelector.tsx`
   - Features:
     - Multi-select checkbox list for available languages
     - "All Languages" option
     - Display available languages from scenario metadata

3. **Update Scenario Execution Page**
   - File: `frontend/src/pages/Scenarios/ScenarioExecution.tsx` (or similar)
   - Add language selector before "Execute" button
   - Pass selected languages to `executeScenario()`

### Proposed UI Design

```
┌─────────────────────────────────────────┐
│ Execute Scenario                        │
├─────────────────────────────────────────┤
│                                         │
│ Select Languages to Execute:            │
│ ☑ All Languages                        │
│ ☐ English (en-US)                      │
│ ☐ French (fr-FR)                       │
│                                         │
│ [Execute Scenario]                      │
└─────────────────────────────────────────┘
```

**Behavior:**
- If "All Languages" is checked, disable individual language checkboxes
- If individual languages are selected, pass them to the API
- If "All Languages" is checked, pass `language_codes: null`

---

## Database Verification

Check the new scenario structure:

```sql
SELECT
    step_order,
    user_utterance,
    step_metadata->>'primary_language' as language,
    step_metadata->>'is_language_variant' as is_variant,
    step_metadata->>'variant_group' as variant_group
FROM scenario_steps
WHERE script_id = 'be301282-f3d2-462b-bc0c-a73813e45ba9'
ORDER BY step_order, id;
```

**Expected Output:**

| step_order | user_utterance | language | is_variant | variant_group |
|------------|----------------|----------|------------|---------------|
| 1 | What's the weather... | en-US | true | weather_check |
| 1 | Quel temps fait-il... | fr-FR | true | weather_check |
| 2 | What's on my calendar... | en-US | true | calendar_check |
| 2 | Qu'est-ce que j'ai... | fr-FR | true | calendar_check |
| 3 | Get directions... | en-US | true | coffee_directions |
| 3 | Trouve-moi le café... | fr-FR | true | coffee_directions |

---

## Key Implementation Details

### Language Filtering Logic

```python
def _filter_steps_by_language(steps, language_codes):
    # Group by step_order
    steps_by_order = {}
    for step in steps:
        steps_by_order[step.step_order].append(step)

    # Filter each step_order group
    for step_order, variants in steps_by_order.items():
        if len(variants) == 1:
            # No variants, always include
            yield variants[0]
        elif language_codes is None:
            # No filter, include all
            yield from variants
        else:
            # Filter by language
            for step in variants:
                if step.step_metadata['primary_language'] in language_codes:
                    yield step
```

### Step Metadata Structure

```python
{
    "primary_language": "fr-FR",
    "is_language_variant": True,
    "variant_group": "weather_check",
    "translation": {
        "en": "What's the weather in San Francisco today?",
        "fr": "Quel temps fait-il à San Francisco aujourd'hui?"
    },
    "context": "User checks weather in French"
}
```

---

## Migration Notes

### Backward Compatibility

- Scenarios WITHOUT language variants continue to work unchanged
- If `language_codes` is not specified, behavior is identical to before (executes all steps)
- Existing scenarios with single-language steps are not affected

### For Existing Scenarios

To add language variants to an existing scenario:
1. Create additional `ScenarioStep` rows with same `step_order`
2. Set `step_metadata.is_language_variant = True`
3. Set `step_metadata.variant_group` to group related variants
4. Set `step_metadata.primary_language` to the language code

---

## Next Steps

1. ✅ **Backend Complete** - Language filtering implemented and tested
2. ⏳ **Frontend UI** - Add language selector component to scenario execution page
3. ⏳ **Testing** - Test end-to-end with frontend UI
4. ⏳ **Documentation** - Update user guide with language selection feature

---

**Created:** December 24, 2024
**Last Updated:** December 24, 2024
