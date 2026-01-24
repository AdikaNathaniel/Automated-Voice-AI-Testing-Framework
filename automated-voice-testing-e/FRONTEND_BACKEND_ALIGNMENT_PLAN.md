# Frontend-Backend Alignment Plan

**Created:** 2025-12-07  
**Status:** In Progress  
**Goal:** Ensure frontend UI properly supports all backend features and fix language code inconsistencies

---

## Issue Summary

### Issue 1: Language Code Inconsistency ❌
- **Problem**: Test cases use 2-character codes (`en`, `es`, `fr`) but system uses 5-character codes (`en-US`, `es-ES`, `fr-FR`)
- **Impact**: Prompt text extraction requires fallback logic, inconsistent data
- **Decision**: Standardize on **5-character ISO codes** (`en-US`, `es-ES`, `fr-FR`)

### Issue 2: Missing Language Selection in UI ❌
- **Problem**: No way to select which languages to test when running a test
- **Impact**: Always defaults to `en-US` only, can't test multi-language scenarios
- **Solution**: Add language selector to test execution UI

### Issue 3: "Run Test" Button Runs Entire Suite ❌
- **Problem**: Button says "Run Test" (singular) but executes all 6 test cases in the suite
- **Impact**: Confusing UX, unexpected behavior, wastes API calls
- **Solution**: Fix backend to respect `test_case_ids` parameter when provided

---

## Phase 1: Language Code Standardization

### Task 1.1: Update Test Case Data ✅
**File**: Database  
**Action**: Update `scenario_definition.queries` to use 5-character codes

```sql
-- Update all test cases to use 5-character language codes
UPDATE test_cases 
SET scenario_definition = jsonb_set(
  jsonb_set(
    jsonb_set(
      scenario_definition,
      '{queries, en-US}',
      scenario_definition->'queries'->'en'
    ),
    '{queries, es-ES}',
    scenario_definition->'queries'->'es'
  ),
  '{queries, fr-FR}',
  scenario_definition->'queries'->'fr'
) - 'queries'->'en' - 'queries'->'es' - 'queries'->'fr'
WHERE scenario_definition->'queries' ? 'en';
```

**Verification**: Query database to confirm all test cases use 5-character codes

### Task 1.2: Update Prompt Extraction Logic ✅
**File**: `backend/services/voice_execution_service.py`  
**Action**: Simplify `_extract_prompt_text()` to only check 5-character codes

**Current** (lines 835-864):
```python
# Checks both 2-char and 5-char codes with fallback
for lang_code in ("en", "en-US", "en-GB", "es", "fr", "de"):
```

**Updated**:
```python
# Only check 5-character codes matching our config
for lang_code in ("en-US", "es-ES", "fr-FR", "de-DE", "it-IT", "pt-BR", "ja-JP", "zh-CN"):
```

### Task 1.3: Update Language Extraction to Use Execution Language ✅
**File**: `backend/services/voice_execution_service.py`  
**Action**: Use the `language_code` parameter passed to execution instead of hardcoded list

**Better approach**:
```python
def _extract_prompt_text(self, test_case: TestCase, language_code: str) -> Optional[str]:
    """Extract prompt text for specific language."""
    scenario = getattr(test_case, "scenario_definition", None) or {}
    queries = scenario.get("queries")
    
    if isinstance(queries, dict):
        # Try exact language match first
        value = queries.get(language_code)
        if isinstance(value, str) and value.strip():
            return value.strip()
        
        # Fallback to base language (en-US -> en)
        base_lang = language_code.split('-')[0]
        for key in queries.keys():
            if key.startswith(base_lang):
                value = queries.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()
    
    return None
```

---

## Phase 2: Fix "Run Test" Button Behavior

### Task 2.1: Fix Backend Test Case Selection Logic ✅
**File**: `backend/services/test_run_service.py`  
**Method**: `_get_test_cases()` (lines 261-300)

**Problem**: When both `suite_id` and `test_case_ids` are provided, it ignores `test_case_ids`

**Current Logic**:
```python
if suite_id:
    # Gets ALL test cases from suite
    return list(result.scalars().all())
elif test_case_ids:
    # Only used if suite_id is None
    return test_cases
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
    # Fall back to entire suite
    query = select(TestCase).filter(
        and_(TestCase.suite_id == suite_id, TestCase.is_active == True)
    )
    # ... rest of logic
```

**Impact**: When user clicks "Run Test" on a single test case, only that test case will run

---

## Phase 3: Add Language Selection to UI

### Task 3.1: Add Language Selector to Test Case Detail Page ✅
**File**: `frontend/src/pages/TestCases/TestCaseDetail.tsx`

**Changes**:
1. Add state for selected languages
2. Add language selector component before "Run Test" button
3. Pass selected languages to `executeTestCase()`

**UI Mockup**:
```
┌─────────────────────────────────────────────────────┐
│ Test Case: Basic Weather Query                      │
├─────────────────────────────────────────────────────┤
│                                                      │
│ Languages to test:                                  │
│ ☑ English (en-US)                                   │
│ ☐ Spanish (es-ES)                                   │
│ ☐ French (fr-FR)                                    │
│                                                      │
│ [Run Test]  [Edit]  [Duplicate]  [Delete]          │
└─────────────────────────────────────────────────────┘
```

**Code Changes**:
```typescript
const [selectedLanguages, setSelectedLanguages] = useState<string[]>(['en-US']);

const handleRunTest = async () => {
  if (!id || !selected?.suiteId) return;

  setRunLoading(true);
  try {
    const testRun = await executeTestCase(
      id,
      selected.suiteId,
      selectedLanguages  // ← Pass selected languages
    );
    // ...
  }
};
```

### Task 3.2: Create Language Selector Component ✅
**File**: `frontend/src/components/LanguageSelector.tsx` (new file)

**Features**:
- Multi-select checkboxes for all supported languages
- Display language name and native name
- Default to `en-US` selected
- Validation: At least one language must be selected

### Task 3.3: Add Language API Endpoint ✅
**File**: `backend/api/routes/languages.py` (new file)

**Endpoint**: `GET /api/languages`
**Response**:
```json
{
  "success": true,
  "data": [
    {
      "code": "en-US",
      "name": "English (United States)",
      "native_name": "English",
      "soundhound_model": "en-US-v3.2"
    },
    {
      "code": "es-ES",
      "name": "Spanish (Spain)",
      "native_name": "Español",
      "soundhound_model": "es-ES-v2.8"
    }
  ]
}
```

**Implementation**: Use existing `language_service.get_supported_languages()`

---

## Phase 4: Frontend Feature Audit

### Task 4.1: Audit Core Features ✅
**Goal**: Identify all backend features and check if frontend supports them

**Backend Features to Check**:
- [ ] Test Runs
  - [x] Create test run from suite
  - [ ] Create test run from specific test cases
  - [ ] View test run details
  - [ ] View test run executions
  - [ ] Retry failed tests
  - [ ] Cancel running test
  - [ ] Export test results
  - [ ] Filter by status, date, language

- [ ] Test Cases
  - [x] List test cases
  - [x] View test case details
  - [x] Create test case
  - [x] Edit test case
  - [x] Delete test case
  - [x] Run single test case
  - [ ] Duplicate test case
  - [ ] Import/export test cases
  - [ ] Bulk operations

- [ ] Test Suites
  - [x] List test suites
  - [x] View suite details
  - [x] Create suite
  - [x] Edit suite
  - [x] Delete suite
  - [ ] Add/remove test cases from suite
  - [ ] Reorder test cases in suite

- [ ] Defects
  - [x] List defects
  - [x] View defect details
  - [ ] Create defect
  - [ ] Update defect status
  - [ ] Link defect to test execution
  - [ ] Export defects

- [ ] Regressions
  - [x] List regressions
  - [ ] View regression details
  - [ ] Create regression baseline
  - [ ] Compare against baseline

- [ ] Integrations
  - [ ] Jira integration
  - [ ] Slack integration
  - [ ] GitHub integration
  - [ ] View integration logs

- [ ] CI/CD
  - [ ] Trigger test from CI/CD
  - [ ] View CI/CD pipeline status
  - [ ] Configure webhooks

- [ ] Analytics
  - [x] Dashboard with metrics
  - [ ] Test execution trends
  - [ ] Language-specific analytics
  - [ ] Failure analysis
  - [ ] Performance metrics

- [ ] Settings
  - [ ] User profile
  - [ ] API keys management
  - [ ] Notification preferences
  - [ ] Language preferences
  - [ ] Tenant settings

### Task 4.2: Create Feature Parity Matrix ✅
**File**: `FEATURE_PARITY_MATRIX.md` (new file)

**Format**:
```markdown
| Feature | Backend API | Frontend UI | Status | Priority | Notes |
|---------|-------------|-------------|--------|----------|-------|
| Run single test | ✅ | ✅ | Complete | High | Works but runs entire suite |
| Select languages | ✅ | ❌ | Missing | High | No UI for selection |
| Retry failed tests | ✅ | ❌ | Missing | Medium | Backend ready, no UI |
```

### Task 4.3: Prioritize Missing Features ✅
**Criteria**:
- **P0 (Critical)**: Blocking core functionality
- **P1 (High)**: Important for usability
- **P2 (Medium)**: Nice to have
- **P3 (Low)**: Future enhancement

---

## Phase 5: Implementation Plan

### Sprint 1: Language Standardization & Core Fixes (This Sprint)
**Duration**: 2-3 days
**Tasks**:
- [x] Task 1.1: Update test case data to use 5-character codes
- [x] Task 1.2: Update prompt extraction logic
- [x] Task 1.3: Use execution language parameter
- [x] Task 2.1: Fix backend test case selection logic
- [x] Task 3.1: Add language selector to UI
- [x] Task 3.2: Create language selector component
- [x] Task 3.3: Add language API endpoint

**Success Criteria**:
- ✅ All test cases use 5-character language codes
- ✅ "Run Test" button only runs selected test case
- ✅ User can select which languages to test
- ✅ Multi-language tests execute correctly

### Sprint 2: Feature Parity - High Priority (Next Sprint)
**Duration**: 3-5 days
**Tasks**:
- [ ] Retry failed tests UI
- [ ] Cancel running test UI
- [ ] Export test results UI
- [ ] Test run filtering UI
- [ ] Duplicate test case UI
- [ ] Add/remove test cases from suite UI

### Sprint 3: Feature Parity - Medium Priority
**Duration**: 3-5 days
**Tasks**:
- [ ] Defect management UI
- [ ] Regression baseline UI
- [ ] Integration configuration UI
- [ ] Analytics enhancements

### Sprint 4: Feature Parity - Low Priority
**Duration**: 2-3 days
**Tasks**:
- [ ] Bulk operations
- [ ] Import/export
- [ ] Advanced settings

---

## Testing Strategy

### Unit Tests
- [ ] Test language code validation
- [ ] Test prompt extraction with 5-character codes
- [ ] Test test case selection logic
- [ ] Test language selector component

### Integration Tests
- [ ] Test single test case execution
- [ ] Test multi-language execution
- [ ] Test suite execution
- [ ] Test language API endpoint

### E2E Tests
- [ ] User selects languages and runs test
- [ ] User runs single test case (not suite)
- [ ] User views multi-language results
- [ ] User retries failed tests

---

## Rollout Plan

### Phase 1: Database Migration (Non-breaking)
1. Create migration script to update test case language codes
2. Run migration on development database
3. Verify all test cases updated correctly
4. Test prompt extraction with new codes

### Phase 2: Backend Updates (Non-breaking)
1. Deploy updated prompt extraction logic
2. Deploy fixed test case selection logic
3. Deploy language API endpoint
4. Verify backward compatibility

### Phase 3: Frontend Updates (Breaking for language selection)
1. Deploy language selector component
2. Deploy updated test case detail page
3. Update documentation
4. Notify users of new feature

### Phase 4: Validation
1. Run full test suite
2. Execute multi-language tests
3. Verify single test case execution
4. Monitor logs for errors

---

## Success Metrics

### Technical Metrics
- ✅ 100% of test cases use 5-character language codes
- ✅ 0 prompt extraction failures due to language code mismatch
- ✅ Single test execution creates exactly 1 execution per language
- ✅ Multi-language tests execute all selected languages

### User Experience Metrics
- ✅ Users can select languages before running tests
- ✅ "Run Test" button behavior matches user expectation
- ✅ Clear indication of which languages will be tested
- ✅ Test results show language-specific outcomes

### Performance Metrics
- ✅ No increase in API response time
- ✅ No increase in database query time
- ✅ No increase in test execution time

---

## Risk Mitigation

### Risk 1: Breaking Existing Tests
**Mitigation**:
- Create database backup before migration
- Test migration on copy of production data
- Implement rollback script

### Risk 2: Frontend-Backend Version Mismatch
**Mitigation**:
- Deploy backend first (backward compatible)
- Deploy frontend after backend validation
- Use feature flags for gradual rollout

### Risk 3: User Confusion
**Mitigation**:
- Add tooltips explaining language selection
- Update documentation
- Provide migration guide
- Add in-app notifications

---

## Next Steps

1. **Review this plan** with team/stakeholders
2. **Create tasks** in project management tool
3. **Start Sprint 1** with language standardization
4. **Complete feature audit** (Task 4.1)
5. **Create feature parity matrix** (Task 4.2)
6. **Prioritize missing features** (Task 4.3)

---

## Questions for Discussion

1. Should we support both 2-character and 5-character codes for backward compatibility?
2. Should language selection be per-test-case or per-test-run?
3. Should we add a "Run All Languages" quick action?
4. Should we show estimated API cost before running multi-language tests?
5. Should we add language-specific test case validation?

---

**Last Updated**: 2025-12-07
**Next Review**: After Sprint 1 completion


