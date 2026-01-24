# API Issues Detailed by File

## Summary Table

| File | Issues | Severity | Lines |
|------|--------|----------|-------|
| auth.py | Generic dict responses, Duplicate auth | HIGH | 150, 383 |
| test_cases.py | Generic dict response, Duplicate auth, TODO | MEDIUM | 217, 715, 758 |
| test_runs.py | Generic dict response, Duplicate auth, TODO | MEDIUM | 186, 220, 389 |
| test_suites.py | Generic dict response, Duplicate auth | MEDIUM | 114 |
| regressions.py | Generic dict responses (3), No RBAC | MEDIUM | 24, 57, 89 |
| defects.py | Missing RBAC, Query validation | MEDIUM | - |
| edge_cases.py | Missing RBAC on create | MEDIUM | - |
| configurations.py | Generic exception handling | MEDIUM | - |
| webhooks.py | No authentication/validation | HIGH | 48+ |
| scenarios.py | Duplicate auth, Generic exceptions | MEDIUM | - |
| knowledge_base.py | Missing RBAC (verify) | MEDIUM | - |
| translations.py | Missing RBAC (verify), Query validation | MEDIUM | - |
| human_validation.py | Missing RBAC, No tests | MEDIUM | - |

## File-by-File Issues

### auth.py (474 lines)
**Location:** `/home/ubuntu/workspace/automated-testing/backend/api/routes/auth.py`

**Issues:**
1. **Line 150** - `register` endpoint uses `response_model=dict`
   - Should use: `AuthRegisterResponse`
   - Impact: No Swagger schema, type-unsafe

2. **Line 383** - `logout` endpoint uses `response_model=dict`
   - Should use: `AuthLogoutResponse`
   - Impact: No Swagger schema

3. **Lines 72-142** - Duplicate `get_current_user` implementation
   - Also in test_cases.py, test_runs.py, scenarios.py
   - Should extract to: `api/dependencies.py`

**Recommendations:**
- Extract get_current_user to shared location
- Create AuthRegisterResponse and AuthLogoutResponse schemas
- Update response_model decorators

---

### test_cases.py (771 lines)
**Location:** `/home/ubuntu/workspace/automated-testing/backend/api/routes/test_cases.py`

**Issues:**
1. **Line 217** - `list_test_cases` uses `response_model=dict`
   - Should use: `PaginatedTestCaseResponse`
   - Complex pagination logic with caching

2. **Line 715** - `get_test_case_history` uses `response_model=dict`
   - Should use: `TestCaseHistoryResponse`
   - Currently returns placeholder

3. **Line 758** - TODO: "Implement actual history tracking"
   - Endpoint returns placeholder data
   - Needs full implementation

4. **Lines 69-137** - Duplicate `get_current_user`
   - Also in 3 other files

5. **Lines 144-166** - Cache key building with hashlib
   - Complex but not documented

**Validation Issues:**
- `suite_id: Optional[UUID]` - No validation
- `test_type: Optional[str]` - No length constraints
- `category: Optional[str]` - No constraints
- `cursor: Optional[str]` - No format validation
- `fields: Optional[str]` - Custom parsing, no validation

**Recommendations:**
- Create PaginatedTestCaseResponse schema
- Implement actual history tracking
- Move cache building to utility
- Add validation to query params

---

### test_runs.py (613 lines)
**Location:** `/home/ubuntu/workspace/automated-testing/backend/api/routes/test_runs.py`

**Issues:**
1. **Line 186** - `list_test_runs` uses `response_model=dict`
   - Should use: `PaginatedTestRunResponse`

2. **Line 220** - TODO: "Implement language filtering when the data model supports it"
   - Incomplete feature

3. **Line 389** - TODO: "Implement get_test_run in orchestration service"
   - Using direct model access instead of service

4. **Line 244** - Error handling has malformed parenthesis
   - `detail=f"Failed to list test runs: {str(e)}" )` - Extra closing paren

5. **Lines 53-101** - Duplicate `get_current_user` (slightly different implementation)

**Validation Issues:**
- `suite_id: Optional[UUID]` - No validation
- `status_filter: Optional[str]` - No enum validation
- `created_by: Optional[UUID]` - No validation
- `language_code: Optional[str]` - No validation

**Recommendations:**
- Create PaginatedTestRunResponse
- Implement language filtering properly
- Use orchestration_service.get_test_run
- Fix error handling syntax
- Add enum validation to status_filter

---

### test_suites.py (351 lines)
**Location:** `/home/ubuntu/workspace/automated-testing/backend/api/routes/test_suites.py`

**Issues:**
1. **Line 114** - `list_test_suites` uses `response_model=dict`
   - Should use: `PaginatedTestSuiteResponse`

2. **Lines 50-98** - Another duplicate `get_current_user` implementation

**Recommendations:**
- Create PaginatedTestSuiteResponse
- Extract shared get_current_user

---

### regressions.py (108 lines)
**Location:** `/home/ubuntu/workspace/automated-testing/backend/api/routes/regressions.py`

**Issues:**
1. **Line 24** - `list_regressions` uses `response_model=dict`
   - Should use: `PaginatedRegressionResponse`

2. **Line 57** - `approve_baseline` uses `response_model=dict`
   - Should use: `RegressionBaselineResponse`

3. **Line 89** - `get_regression_comparison` uses `response_model=dict`
   - Should use: `RegressionComparisonResponse`

4. **Missing operations:**
   - No Update endpoint for regressions
   - No Delete endpoint for regressions
   - Only has R (list), R (compare), and partial U (approve)

**RBAC Issues:**
- No RBAC on endpoints (anyone authenticated can approve baselines)

**Recommendations:**
- Create proper response schemas
- Add RBAC (should require QA_LEAD/ADMIN)
- Consider adding Update and Delete operations

---

### defects.py (178 lines)
**Location:** `/home/ubuntu/workspace/automated-testing/backend/api/routes/defects.py`

**Issues:**
1. **Missing RBAC:**
   - `POST /defects/` - No role check
   - `PATCH /defects/{id}` - No role check
   - `POST /defects/{id}/assign` - No role check
   - `POST /defects/{id}/resolve` - No role check

2. **Query validation issues:**
   - `status_filter: Optional[str]` - No enum validation
   - `severity: Optional[str]` - No enum validation
   - `category: Optional[str]` - No constraints

**Good patterns:**
- Uses `DefectListResponse` instead of dict (correct!)
- Proper exception mapping with `_map_exception`

**Recommendations:**
- Add RBAC checks (require QA role minimum)
- Add enum validation to filter parameters
- Document valid status/severity values

---

### edge_cases.py (246 lines)
**Location:** `/home/ubuntu/workspace/automated-testing/backend/api/routes/edge_cases.py`

**Issues:**
1. **Missing RBAC on create:**
   - `POST /edge-cases/` - Only checks authentication, not role
   - Should require QA role

2. **Missing RBAC on update:**
   - `PATCH /edge-cases/{id}` - No role check

3. **Query validation:**
   - `query: str` in search endpoint needs min length validation

**Recommendations:**
- Add role-based access control to mutations
- Add query validation

---

### configurations.py (303 lines)
**Location:** `/home/ubuntu/workspace/automated-testing/backend/api/routes/configurations.py`

**Issues:**
1. **Generic exception handling:**
   - Multiple `except` clauses catch all exceptions
   - Exposes internal details

2. **Sync/Async mixing:**
   - Uses `await db.run_sync()` pattern
   - Could cause performance issues

**Positive:**
- Has RBAC checks (requires ADMIN/QA_LEAD)
- Implements caching

**Recommendations:**
- Implement specific exception handling
- Review sync/async performance

---

### webhooks.py (varies, but starts around line 48)
**Location:** `/home/ubuntu/workspace/automated-testing/backend/api/routes/webhooks.py`

**CRITICAL SECURITY ISSUE:**
1. **Line 48+** - `POST /webhooks/ci-cd` has NO authentication
   - Anyone can send webhooks
   - No signature validation
   - No API key verification

**Missing:**
- HMAC-SHA256 signature validation
- X-Signature header verification
- Rate limiting on webhook endpoint
- Request body validation
- Webhook ID/secret management

**Recommendations (URGENT):**
- Implement HMAC-SHA256 verification
- Verify X-Signature-256 header
- Add secret key management
- Document webhook signature format
- Implement in security context

---

### scenarios.py (575 lines)
**Location:** `/home/ubuntu/workspace/automated-testing/backend/api/routes/scenarios.py`

**Issues:**
1. **Lines 52-117** - Another duplicate `get_current_user`

2. **Generic exception handling:**
   - Multiple catch-all exception handlers
   - Expose internal details in errors

3. **Missing tests:**
   - No test files for scenario routes
   - 11 endpoints without tests

**Recommendations:**
- Extract get_current_user
- Implement specific exception handling
- Write integration tests

---

### knowledge_base.py
**Location:** `/home/ubuntu/workspace/automated-testing/backend/api/routes/knowledge_base.py`

**Potential Issues (verify):**
1. RBAC on create/update/delete endpoints
   - Need to verify if role checks present
   
2. Query validation on search/list endpoints

---

### translations.py
**Location:** `/home/ubuntu/workspace/automated-testing/backend/api/routes/translations.py`

**Potential Issues (verify):**
1. RBAC enforcement on:
   - POST create endpoint
   - POST assign endpoint
   - PATCH status update endpoint

2. Query validation:
   - status_filter - No enum validation
   - assigned_to - No validation

---

### human_validation.py (443 lines)
**Location:** `/home/ubuntu/workspace/automated-testing/backend/api/routes/human_validation.py`

**Issues:**
1. **Missing RBAC:**
   - Queue operations don't enforce role restrictions
   - Should require validator role

2. **No test coverage:**
   - 7 endpoints with no tests

3. **Complex logic:**
   - Claim/release/submit operations need validation

---

### Other Route Files Summary

| File | Status | Notes |
|------|--------|-------|
| activity.py | OK | Read-only, proper auth |
| analytics.py | OK | Proper response model |
| dashboard.py | OK | Proper response model |
| language_statistics.py | OK | Single endpoint |
| metrics.py | OK | Prometheus metrics intentionally public |
| reports.py | OK | Custom report builder |
| workers.py | OK | Health check only |

---

## Cross-File Patterns

### Duplicate Code Pattern
Files with `get_current_user`:
1. `/home/ubuntu/workspace/automated-testing/backend/api/routes/auth.py` - Lines 72-142 (71 lines)
2. `/home/ubuntu/workspace/automated-testing/backend/api/routes/test_cases.py` - Lines 69-137 (69 lines)
3. `/home/ubuntu/workspace/automated-testing/backend/api/routes/test_runs.py` - Lines 53-101 (49 lines)
4. `/home/ubuntu/workspace/automated-testing/backend/api/routes/scenarios.py` - Lines 52-117 (66 lines)

**Total duplicated:** ~255 lines
**Solution:** Extract to `api/dependencies.py` (~80 lines, saves ~175 lines)

### Generic Dict Response Pattern
Files with `response_model=dict`:
1. auth.py - Lines 150, 383
2. test_cases.py - Lines 217, 715
3. test_runs.py - Line 186
4. test_suites.py - Line 114
5. regressions.py - Lines 24, 57, 89

**Total affected:** 9 endpoints
**Solution time:** 1-2 hours for all

### Missing RBAC Pattern
Files needing RBAC:
1. defects.py - All mutation endpoints
2. edge_cases.py - Create and update
3. knowledge_base.py - Verify needed
4. translations.py - Verify needed
5. human_validation.py - All endpoints

**Solution pattern:** Add authorization helper function

---

## Immediate Action List

### 1. Critical (Do Today)
- [ ] Review webhooks.py security
- [ ] Create issue for webhook HMAC validation
- [ ] Review defects.py RBAC requirements

### 2. High Priority (This Week)
- [ ] Extract get_current_user to dependencies.py
- [ ] Create paginated response models
- [ ] Replace generic dict responses (9 endpoints)
- [ ] Add RBAC to defects, edge_cases, knowledge_base

### 3. Medium Priority (This Month)
- [ ] Add query parameter validation
- [ ] Write API integration tests
- [ ] Document rate limiting strategy
- [ ] Implement proper exception handling

### 4. Low Priority (Next Month)
- [ ] Standardize naming conventions
- [ ] Implement per-endpoint rate limits
- [ ] Add API versioning strategy

