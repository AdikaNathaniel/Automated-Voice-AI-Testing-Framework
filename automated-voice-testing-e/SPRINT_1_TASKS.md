# Sprint 1: Language Standardization & Core Fixes

**Sprint Goal**: Fix critical P0 issues blocking multi-language testing and single test case execution
**Duration**: 2-3 days
**Start Date**: 2025-12-07
**Status**: ✅ COMPLETE

---

## Sprint Objectives

1. ✅ Standardize all language codes to 5-character format (`en-US`, `es-ES`, `fr-FR`)
2. ✅ Fix "Run Test" button to execute only selected test case (not entire suite)
3. ✅ Add language selection UI to test case detail page
4. ✅ Enable multi-language test execution from UI

---

## Tasks

### Task 1: Update Test Case Language Codes in Database
**Priority**: P0  
**Estimated Time**: 30 minutes  
**Status**: ⏳ Not Started

**Description**: Update all test cases in database to use 5-character language codes instead of 2-character codes

**Files**:
- Database: `test_cases` table

**Steps**:
1. Create SQL migration script to update `scenario_definition.queries`
2. Backup current test case data
3. Run migration to convert:
   - `en` → `en-US`
   - `es` → `es-ES`
   - `fr` → `fr-FR`
4. Verify all 6 test cases updated correctly
5. Test prompt extraction with new codes

**SQL Script**:
```sql
-- Backup first
CREATE TABLE test_cases_backup AS SELECT * FROM test_cases;

-- Update language codes
UPDATE test_cases 
SET scenario_definition = jsonb_build_object(
  'queries', jsonb_build_object(
    'en-US', scenario_definition->'queries'->'en',
    'es-ES', scenario_definition->'queries'->'es',
    'fr-FR', scenario_definition->'queries'->'fr'
  ),
  'expected_intent', scenario_definition->'expected_intent',
  'expected_entities', scenario_definition->'expected_entities'
)
WHERE scenario_definition->'queries' ? 'en';

-- Verify
SELECT id, name, scenario_definition->'queries' as queries FROM test_cases;
```

**Acceptance Criteria**:
- [ ] All test cases use `en-US`, `es-ES`, `fr-FR` keys
- [ ] No test cases have `en`, `es`, `fr` keys
- [ ] All expected_intent and expected_entities preserved
- [ ] Backup created successfully

---

### Task 2: Update Prompt Extraction Logic
**Priority**: P0  
**Estimated Time**: 1 hour  
**Status**: ⏳ Not Started

**Description**: Simplify prompt extraction to use execution language parameter and only check 5-character codes

**Files**:
- `backend/services/voice_execution_service.py` (lines 835-864)

**Changes**:
1. Update `_extract_prompt_text()` signature to accept `language_code` parameter
2. Remove fallback logic for 2-character codes
3. Use exact language match first, then base language fallback
4. Update all callers to pass `language_code`

**Implementation**:
```python
def _extract_prompt_text(
    self, 
    test_case: TestCase, 
    language_code: str
) -> Optional[str]:
    """
    Extract prompt text for specific language from test case.
    
    Args:
        test_case: Test case with scenario_definition
        language_code: Language code (e.g., 'en-US', 'es-ES')
    
    Returns:
        Prompt text for the language, or None if not found
    """
    scenario = getattr(test_case, "scenario_definition", None) or {}
    queries = scenario.get("queries")
    
    if not isinstance(queries, dict):
        logger.warning(
            f"[VOICE_EXEC] No queries dict in test case {test_case.id}"
        )
        return None
    
    # Try exact language match first (e.g., 'en-US')
    value = queries.get(language_code)
    if isinstance(value, str) and value.strip():
        logger.info(
            f"[VOICE_EXEC] Found prompt for {language_code}: {value[:50]}..."
        )
        return value.strip()
    
    # Fallback to base language (en-US -> en)
    base_lang = language_code.split('-')[0]
    for key in queries.keys():
        if key.startswith(base_lang):
            value = queries.get(key)
            if isinstance(value, str) and value.strip():
                logger.info(
                    f"[VOICE_EXEC] Found prompt for base {base_lang}: {value[:50]}..."
                )
                return value.strip()
    
    logger.warning(
        f"[VOICE_EXEC] No prompt found for {language_code} or {base_lang} "
        f"in test case {test_case.id}. Available: {list(queries.keys())}"
    )
    return None
```

**Acceptance Criteria**:
- [ ] Method accepts `language_code` parameter
- [ ] Exact language match works (e.g., `en-US`)
- [ ] Base language fallback works (e.g., `en-US` → `en`)
- [ ] Logs show which language was matched
- [ ] No more "No prompt text found" warnings for valid test cases

---

### Task 3: Fix Backend Test Case Selection Logic
**Priority**: P0  
**Estimated Time**: 1 hour  
**Status**: ⏳ Not Started

**Description**: Fix `_get_test_cases()` to prioritize `test_case_ids` over `suite_id` when both are provided

**Files**:
- `backend/services/test_run_service.py` (lines 261-300)

**Current Problem**:
```python
if suite_id:
    # Gets ALL test cases from suite (ignores test_case_ids)
    return all_suite_test_cases
elif test_case_ids:
    # Only used if suite_id is None
    return specific_test_cases
```

**Fixed Logic**:
```python
if test_case_ids:
    # Prioritize specific test case IDs
    query = select(TestCase).filter(TestCase.id.in_(test_case_ids))
    if tenant_id:
        query = query.where(TestCase.tenant_id == tenant_id)
    
    result = await db.execute(query)
    test_cases = list(result.scalars().all())
    
    if len(test_cases) != len(test_case_ids):
        raise ValueError("One or more test case IDs are invalid")
    
    return test_cases

elif suite_id:
    # Fall back to entire suite if no specific test cases
    suite = await db.get(TestSuite, suite_id)
    if not suite:
        raise ValueError(f"Test suite with ID {suite_id} not found")
    
    suite_tenant = getattr(suite, "tenant_id", None)
    if tenant_id and suite_tenant not in (None, tenant_id):
        raise ValueError("Test suite not accessible for this tenant")
    
    query = select(TestCase).filter(
        and_(TestCase.suite_id == suite_id, TestCase.is_active == True)
    )
    if tenant_id:
        query = query.where(TestCase.tenant_id == tenant_id)
    
    result = await db.execute(query)
    return list(result.scalars().all())

return []
```

**Acceptance Criteria**:
- [ ] When `test_case_ids` provided, only those test cases are returned
- [ ] When only `suite_id` provided, all suite test cases are returned
- [ ] When both provided, `test_case_ids` takes priority
- [ ] Tenant isolation still enforced
- [ ] Error raised if test case IDs are invalid

---

### Task 4: Add Language API Endpoint
**Priority**: P0  
**Estimated Time**: 30 minutes  
**Status**: ⏳ Not Started

**Description**: Create API endpoint to fetch supported languages for UI

**Files**:
- `backend/api/routes/languages.py` (new file)
- `backend/api/main.py` (register route)

**Implementation**:
```python
# backend/api/routes/languages.py
from fastapi import APIRouter
from api.schemas.responses import SuccessResponse
from services.language_service import get_supported_languages

router = APIRouter(prefix="/languages", tags=["languages"])

@router.get("")
async def list_languages() -> SuccessResponse:
    """
    Get list of supported languages.
    
    Returns language codes, names, and SoundHound model mappings.
    """
    languages = get_supported_languages()
    return SuccessResponse(data=languages)
```

**Register in main.py**:
```python
from api.routes import languages

app.include_router(languages.router, prefix="/api")
```

**Acceptance Criteria**:
- [ ] Endpoint returns 200 OK
- [ ] Response includes all 8 languages from config
- [ ] Each language has: code, name, native_name, soundhound_model
- [ ] Response follows SuccessResponse schema

---

### Task 5: Create Language Selector Component
**Priority**: P0  
**Estimated Time**: 2 hours  
**Status**: ⏳ Not Started

**Description**: Create reusable React component for selecting languages

**Files**:
- `frontend/src/components/LanguageSelector.tsx` (new file)
- `frontend/src/components/LanguageSelector.module.css` (new file)

**Component Features**:
- Multi-select checkboxes
- Display language name and native name
- Default to `en-US` selected
- Validation: At least one language must be selected
- Disabled state support
- Loading state while fetching languages

**Props Interface**:
```typescript
interface LanguageSelectorProps {
  selectedLanguages: string[];
  onChange: (languages: string[]) => void;
  disabled?: boolean;
  maxSelections?: number;
}
```

**Acceptance Criteria**:
- [ ] Component renders all available languages
- [ ] User can select/deselect languages
- [ ] At least one language must remain selected
- [ ] onChange callback fires with updated selection
- [ ] Component is accessible (keyboard navigation, ARIA labels)
- [ ] Loading state shows while fetching languages
- [ ] Error state shows if API fails

---

### Task 6: Update Test Case Detail Page
**Priority**: P0  
**Estimated Time**: 1.5 hours  
**Status**: ⏳ Not Started

**Description**: Add language selector to test case detail page and pass selected languages to execution

**Files**:
- `frontend/src/pages/TestCases/TestCaseDetail.tsx`

**Changes**:
1. Add state for selected languages
2. Import and render LanguageSelector component
3. Update `handleRunTest()` to pass selected languages
4. Add UI section showing which languages will be tested

**Implementation**:
```typescript
const [selectedLanguages, setSelectedLanguages] = useState<string[]>(['en-US']);

const handleRunTest = async () => {
  if (!id || !selected?.suiteId) return;
  
  setRunLoading(true);
  setLocalError(null);
  setRunSuccess(null);
  
  try {
    const testRun = await executeTestCase(
      id, 
      selected.suiteId,
      selectedLanguages  // ← Pass selected languages
    );
    
    setRunSuccess(
      `Test execution started for ${selectedLanguages.length} language(s)! ` +
      `Test run ID: ${testRun.id}`
    );
    
    setTimeout(() => {
      navigate(`/test-runs/${testRun.id}`);
    }, 2000);
  } catch (err: unknown) {
    const message = err instanceof Error 
      ? err.message 
      : 'Failed to start test execution';
    setLocalError(message);
  } finally {
    setRunLoading(false);
  }
};
```

**Acceptance Criteria**:
- [ ] Language selector appears above "Run Test" button
- [ ] Selected languages are passed to API
- [ ] Success message shows number of languages
- [ ] Test run executes for all selected languages
- [ ] UI is responsive and accessible

---

## Testing Checklist

### Unit Tests
- [ ] Test prompt extraction with 5-character codes
- [ ] Test prompt extraction with base language fallback
- [ ] Test test case selection logic (test_case_ids priority)
- [ ] Test language API endpoint
- [ ] Test LanguageSelector component

### Integration Tests
- [ ] Test single test case execution (1 test case × N languages)
- [ ] Test suite execution (M test cases × N languages)
- [ ] Test language API integration with frontend

### E2E Tests
- [ ] User selects multiple languages and runs test
- [ ] User runs single test case (not suite)
- [ ] User views multi-language results
- [ ] Test run shows correct number of executions

---

## Definition of Done

- [ ] All 6 tasks completed
- [ ] All acceptance criteria met
- [ ] All tests passing
- [ ] Code reviewed
- [ ] Documentation updated
- [ ] Backend deployed
- [ ] Frontend deployed
- [ ] Smoke tests passed in production
- [ ] No regressions detected

---

## Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Database migration fails | High | Low | Create backup, test on copy first |
| Breaking existing tests | High | Medium | Comprehensive testing before deploy |
| Frontend-backend version mismatch | Medium | Low | Deploy backend first, verify, then frontend |
| User confusion with new UI | Low | Medium | Add tooltips, update docs |

---

## Success Metrics

- ✅ 100% of test cases use 5-character language codes
- ✅ Single test execution creates exactly N executions (N = number of selected languages)
- ✅ Users can select 1-8 languages before running test
- ✅ No "No prompt text found" errors for valid test cases
- ✅ Test execution time proportional to number of languages selected

---

**Next Sprint**: Feature Parity - High Priority (Retry, Cancel, Defect Management)
