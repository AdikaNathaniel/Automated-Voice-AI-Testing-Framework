# Pattern Analysis Configuration - Feature Testing Checklist

**Feature**: Tenant-specific AI-powered pattern discovery configuration
**Date**: 2025-12-29
**Status**: Ready for Testing

---

## Pre-Testing Setup

### Backend Setup
- [ ] Run database migration: `cd backend && alembic upgrade head`
- [ ] Verify migration success: Check for `pattern_analysis_configs` table in database
- [ ] Start backend server: `uvicorn api.main:app --reload`
- [ ] Backend accessible at `http://localhost:8000`

### Frontend Setup
- [ ] Install dependencies (if needed): `cd frontend && npm install`
- [ ] Start dev server: `npm run dev`
- [ ] Frontend accessible at `http://localhost:3001`

### Test User Setup
- [ ] Create/have admin user account
- [ ] Create/have super_admin user account
- [ ] Verify both users belong to an organization

---

## 1. Navigation & Access Control

### Access Control
- [ ] **Admin user** can access `/admin/settings`
- [ ] **Super admin user** can access `/admin/settings`
- [ ] **Regular user** is denied access (403 or redirect)
- [ ] Unauthenticated user is redirected to login

### Navigation
- [ ] "Settings" appears in Admin Console sidebar
- [ ] Settings icon (gear) is visible
- [ ] Click "Settings" navigates to `/admin/settings`
- [ ] Settings tab is highlighted when active
- [ ] URL updates correctly: `http://localhost:3001/admin/settings`

---

## 2. Page Load & UI

### Initial Load
- [ ] Page loads without errors
- [ ] Loading spinner appears briefly
- [ ] Page title: "Organization Settings"
- [ ] Subtitle: "Configure your organization's preferences and behavior"
- [ ] Five tabs are visible:
  - [ ] General
  - [ ] Pattern Analysis
  - [ ] Notifications
  - [ ] Integrations
  - [ ] CI/CD

### Pattern Analysis Tab
- [ ] Click "Pattern Analysis" tab
- [ ] Tab becomes active (purple underline)
- [ ] Configuration loads successfully
- [ ] Loading state shows during fetch
- [ ] All form fields are populated with current values
- [ ] No console errors

### UI Components Present
- [ ] Blue info box: "About Pattern Analysis"
- [ ] Section: "Time Window Settings"
  - [ ] Field: Recent Edge Cases (days)
  - [ ] Field: Maximum Age (days)
- [ ] Section: "Pattern Formation"
  - [ ] Field: Minimum Pattern Size
  - [ ] Field: Similarity Threshold
- [ ] Section: "AI/LLM Settings"
  - [ ] Checkbox: Enable LLM-powered analysis
  - [ ] Field: LLM Confidence Threshold
  - [ ] Field: Max LLM Calls Per Run (optional)
- [ ] Section: "Scheduling"
  - [ ] Checkbox: Enable automatic pattern analysis
  - [ ] Field: Schedule (Cron)
- [ ] Section: "Notifications"
  - [ ] Checkbox: Notify on new patterns
  - [ ] Checkbox: Alert on critical patterns
- [ ] Action buttons:
  - [ ] "Reset to Defaults" (left)
  - [ ] "Run Analysis Now" (right)
  - [ ] "Save Changes" (right, primary button)

---

## 3. Default Values Verification

### Check Default Values Match
- [ ] Recent Edge Cases: **7 days**
- [ ] Maximum Age: **90 days**
- [ ] Minimum Pattern Size: **3**
- [ ] Similarity Threshold: **0.85**
- [ ] Enable LLM Analysis: **checked**
- [ ] LLM Confidence Threshold: **0.70**
- [ ] Max LLM Calls Per Run: **empty (unlimited)**
- [ ] Enable Auto Analysis: **checked**
- [ ] Schedule: **0 2 * * ***
- [ ] Notify New Patterns: **checked**
- [ ] Notify Critical Patterns: **checked**

---

## 3.5. Removed Features Verification

**Verify max_llm_calls_per_run is completely removed:**
- [ ] Field does NOT appear in UI
- [ ] GET API response does NOT include max_llm_calls_per_run
- [ ] Database column does NOT exist: `\d pattern_analysis_configs`
- [ ] No references in logs or error messages
- [ ] Migration applied successfully: `alembic current` shows `x1y2z3a4b5c6`

## 3.6. Configuration Parameter Usage Verification

**Verify min_pattern_size is used correctly:**
- [ ] Set min_pattern_size to 5
- [ ] Create 4 similar edge cases
- [ ] Run analysis - should NOT create pattern
- [ ] Create 5th similar edge case
- [ ] Run analysis - should create pattern
- [ ] Check logs confirm: "cases (min: 5)"

**Verify llm_confidence_threshold is used correctly:**
- [ ] Set llm_confidence_threshold to 0.90
- [ ] Check logs during analysis show threshold being used
- [ ] Pattern matching respects higher confidence requirement

**Verify edge case data includes validation criteria:**
- [ ] Create new edge case via human validation
- [ ] Check scenario_definition in database includes:
  - [ ] expected_command_kind
  - [ ] expected_response_content
  - [ ] expected_asr_confidence_min
  - [ ] forbidden_phrases
  - [ ] command_kind_match_score
  - [ ] houndify_passed
  - [ ] llm_passed
  - [ ] final_decision
- [ ] Verify expected_response is NOT in scenario_definition

---

## 4. Form Validation

### Time Window Settings
- [ ] Recent days: Accept values 1-365
- [ ] Recent days: Reject values < 1
- [ ] Recent days: Reject values > 365
- [ ] Maximum age: Accept values 1-730
- [ ] Maximum age: Reject values < 1
- [ ] Maximum age: Reject values > 730
- [ ] **Validation**: Recent days ≤ Maximum age
  - [ ] Set Recent = 30, Max = 20 → Should show error on save
  - [ ] Set Recent = 20, Max = 30 → Should save successfully

### Pattern Formation
- [ ] Min pattern size: Accept values 2-50
- [ ] Min pattern size: Reject values < 2
- [ ] Min pattern size: Reject values > 50
- [ ] Similarity threshold: Accept 0.0-1.0
- [ ] Similarity threshold: Reject < 0.0
- [ ] Similarity threshold: Reject > 1.0
- [ ] Similarity threshold: Accept decimals (e.g., 0.85)

### LLM Settings
- [ ] LLM confidence: Accept 0.0-1.0
- [ ] LLM confidence: Reject < 0.0
- [ ] LLM confidence: Reject > 1.0
- [ ] Max LLM calls: Accept positive integers
- [ ] Max LLM calls: Accept empty (unlimited)
- [ ] When "Enable LLM" unchecked:
  - [ ] LLM confidence field is disabled
  - [ ] Max LLM calls field is disabled

### Schedule Format
- [ ] Accept valid cron: `0 2 * * *`
- [ ] Accept valid cron: `0 0 * * 0` (weekly)
- [ ] Accept valid cron: `*/30 * * * *` (every 30 min)
- [ ] Field disabled when auto-analysis unchecked

---

## 5. Save Changes Functionality

### Basic Save
- [ ] Change "Recent Edge Cases" from 7 to 14
- [ ] "Save Changes" button becomes enabled
- [ ] Click "Save Changes"
- [ ] Button shows "Saving..." state
- [ ] Button is disabled during save
- [ ] Success message appears (green banner)
- [ ] Success message: "Configuration saved successfully"
- [ ] Form values remain updated
- [ ] "Save Changes" button becomes disabled again

### Persistence Test
- [ ] Make changes and save
- [ ] Refresh the page (F5)
- [ ] Navigate away and come back
- [ ] Verify changes are still present
- [ ] Check database directly: `SELECT * FROM pattern_analysis_configs;`

### Multiple Field Changes
- [ ] Change 3+ fields at once
- [ ] Save successfully
- [ ] All changes persist

### Error Handling
- [ ] Stop backend server
- [ ] Try to save changes
- [ ] Error message appears (red banner)
- [ ] Error message indicates connection failure
- [ ] Form values remain in modified state
- [ ] Restart backend
- [ ] Retry save - should succeed

---

## 6. Reset to Defaults

- [ ] Modify several fields
- [ ] Click "Reset to Defaults"
- [ ] All fields revert to default values (see section 3)
- [ ] "Save Changes" button becomes enabled
- [ ] Must click "Save" to persist the reset
- [ ] Clicking "Save" after reset saves defaults
- [ ] Refresh page shows defaults persisted

---

## 7. Manual Analysis Trigger

### Basic Trigger
- [ ] Click "Run Analysis Now"
- [ ] Button shows "Starting..." state
- [ ] Button is disabled during request
- [ ] Success message appears
- [ ] Message includes: "Pattern analysis started"
- [ ] Message includes: "Task ID: xxx"
- [ ] Button re-enables after completion
- [ ] **NO reference to LLM budget or max calls**

### Notifications (NEW)
- [ ] Enable "Notify on new patterns"
- [ ] Run analysis that creates new patterns
- [ ] Check Slack/email for new pattern notifications
- [ ] Enable "Notify on critical patterns"
- [ ] Create critical pattern (severity: critical)
- [ ] Verify high-priority alert sent

### Error Cases
- [ ] Stop backend
- [ ] Click "Run Analysis Now"
- [ ] Error message appears
- [ ] Button re-enables

### Backend Verification
- [ ] Check Celery logs for task execution
- [ ] Verify task was queued with correct tenant_id
- [ ] Verify task runs with organization's config parameters

---

## 8. LLM Toggle Behavior

### Enable/Disable Flow
- [ ] LLM Analysis enabled by default
- [ ] Both LLM fields are enabled
- [ ] Uncheck "Enable LLM Analysis"
- [ ] LLM Confidence field becomes disabled
- [ ] Max LLM Calls field becomes disabled
- [ ] Can still save configuration
- [ ] Re-check "Enable LLM Analysis"
- [ ] Fields become enabled again
- [ ] Previous values are retained

---

## 9. Auto-Analysis Toggle Behavior

### Enable/Disable Flow
- [ ] Auto-Analysis enabled by default
- [ ] Schedule field is enabled
- [ ] Uncheck "Enable Auto Analysis"
- [ ] Schedule field becomes disabled
- [ ] Can still save configuration
- [ ] Backend respects this setting (check `get_all_active()`)
- [ ] Re-check "Enable Auto Analysis"
- [ ] Schedule field enabled again

---

## 10. Other Tabs (Placeholder Verification)

- [ ] Click "General" tab → Shows placeholder message
- [ ] Click "Notifications" tab → Shows placeholder message
- [ ] Click "Integrations" tab → Shows placeholder message
- [ ] Click "CI/CD" tab → Shows placeholder message
- [ ] Switch between tabs without errors
- [ ] Pattern Analysis tab retains unsaved changes when switching

---

## 11. Responsive Design

### Desktop (1920x1080)
- [ ] All sections visible
- [ ] Two-column grid for form fields
- [ ] No horizontal scrolling
- [ ] Buttons properly aligned

### Tablet (iPad - 768px)
- [ ] Tabs scroll horizontally if needed
- [ ] Form fields stack to single column
- [ ] All content readable
- [ ] No layout breaking

### Mobile (375px)
- [ ] Settings page accessible
- [ ] Tabs visible (may scroll)
- [ ] Form fields full-width
- [ ] Buttons stack vertically
- [ ] All functionality works

---

## 12. Dark Mode

- [ ] Switch to dark mode
- [ ] Settings page renders correctly
- [ ] All text is readable (proper contrast)
- [ ] Form fields have dark backgrounds
- [ ] Borders are visible
- [ ] Success/error messages have dark variants
- [ ] Buttons maintain visibility
- [ ] Tabs are styled correctly
- [ ] Switch back to light mode - all still works

---

## 13. API Integration Tests

### GET Configuration
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/pattern-analysis/config
```
- [ ] Returns 200 OK
- [ ] Response includes all 12 config fields
- [ ] Response includes `id`, `tenant_id`, `created_at`, `updated_at`

### UPDATE Configuration
```bash
curl -X PUT \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"lookback_days_recent": 14}' \
  http://localhost:8000/api/v1/pattern-analysis/config
```
- [ ] Returns 200 OK
- [ ] Response shows updated value
- [ ] Only updated field changed
- [ ] Other fields unchanged

### Manual Trigger
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}' \
  http://localhost:8000/api/v1/pattern-analysis/config/analyze/manual
```
- [ ] Returns 202 Accepted
- [ ] Response includes `task_id`
- [ ] Response includes `status: "queued"`

### Get Defaults
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/pattern-analysis/config/defaults
```
- [ ] Returns 200 OK
- [ ] Response includes all default values
- [ ] Values match defaults in section 3

---

## 14. Database Verification

### Schema Check
```sql
\d pattern_analysis_configs
```
- [ ] Table exists
- [ ] Has columns: id, tenant_id, lookback_days_recent, lookback_days_max, etc.
- [ ] Has unique constraint on tenant_id
- [ ] Has index on tenant_id

### Data Check
```sql
SELECT * FROM pattern_analysis_configs;
```
- [ ] One row per organization
- [ ] Values match what's shown in UI
- [ ] `created_at` and `updated_at` timestamps present

### Migration Check
```bash
alembic current
```
- [ ] Shows revision: `w0x1y2z3a4b5 (head)`

---

## 15. Celery Integration

### Task Configuration
- [ ] Verify task registered: `celery -A celery_app inspect registered`
- [ ] Task `analyze_edge_case_patterns` is listed

### Manual Task Execution
```python
from tasks.edge_case_analysis import analyze_edge_case_patterns
result = analyze_edge_case_patterns.delay(
    tenant_id="YOUR_TENANT_ID"
)
```
- [ ] Task queued successfully
- [ ] Task executes without errors
- [ ] Task uses tenant's configuration
- [ ] Logs show correct parameters

### Configuration Usage
- [ ] Check task logs for: `lookback_days_recent=X`
- [ ] Check task logs for: `lookback_days_max=Y`
- [ ] Verify X and Y match UI configuration

---

## 16. Edge Cases

### Empty/Null Handling
- [ ] Clear "Max LLM Calls" field → Saves as null (unlimited)
- [ ] Empty schedule field → Shows validation error

### Extreme Values
- [ ] Set Recent days to 1 → Saves successfully
- [ ] Set Recent days to 365 → Saves successfully
- [ ] Set Max days to 730 → Saves successfully
- [ ] Set Min pattern size to 2 → Saves successfully
- [ ] Set Min pattern size to 50 → Saves successfully
- [ ] Set Similarity to 0.00 → Saves successfully
- [ ] Set Similarity to 1.00 → Saves successfully

### Concurrent Edits
- [ ] Open settings in two browser tabs
- [ ] Modify and save in tab 1
- [ ] Modify and save in tab 2
- [ ] Last save wins (no data corruption)

### Browser Refresh
- [ ] Make changes (don't save)
- [ ] Refresh page (F5)
- [ ] Unsaved changes are lost (expected)
- [ ] Confirm user is warned about unsaved changes (if implemented)

---

## 17. Performance

- [ ] Page loads in < 2 seconds
- [ ] Save operation completes in < 1 second
- [ ] Manual trigger responds in < 1 second
- [ ] No memory leaks (check DevTools)
- [ ] No excessive re-renders (React DevTools)

---

## 18. Accessibility

- [ ] Tab through all form fields
- [ ] All fields reachable via keyboard
- [ ] Form labels are associated with inputs
- [ ] Buttons have clear focus states
- [ ] Error messages are announced
- [ ] Success messages are announced
- [ ] ARIA labels present where needed

---

## 19. Browser Compatibility

### Chrome
- [ ] All features work
- [ ] UI renders correctly

### Firefox
- [ ] All features work
- [ ] UI renders correctly

### Safari
- [ ] All features work
- [ ] UI renders correctly

### Edge
- [ ] All features work
- [ ] UI renders correctly

---

## 20. Multi-Tenant Isolation

### Setup
- [ ] Create/have two organizations (Org A, Org B)
- [ ] Create admin user for each org

### Test Isolation
- [ ] Login as Org A admin
- [ ] Set Recent days to 14 for Org A
- [ ] Save configuration
- [ ] Logout
- [ ] Login as Org B admin
- [ ] Verify Recent days is still 7 (default) for Org B
- [ ] Set Recent days to 21 for Org B
- [ ] Save configuration
- [ ] Logout
- [ ] Login as Org A admin again
- [ ] Verify Recent days is still 14 (not affected by Org B)

---

## Post-Testing Verification

### Cleanup
- [ ] No console errors in browser
- [ ] No errors in backend logs
- [ ] No failed network requests
- [ ] Database integrity intact

### Documentation
- [ ] All failing tests documented with:
  - [ ] Steps to reproduce
  - [ ] Expected behavior
  - [ ] Actual behavior
  - [ ] Screenshots (if applicable)

---

## Testing Summary

**Total Tests**: ~150+
**Tester**: _______________
**Date Tested**: _______________
**Pass Rate**: _____% (____ passed / ____ total)

### Critical Issues Found
1. _______________________
2. _______________________
3. _______________________

### Minor Issues Found
1. _______________________
2. _______________________
3. _______________________

### Recommendations
1. _______________________
2. _______________________
3. _______________________

---

## Quick Start Testing (Minimal)

**For rapid smoke testing, focus on these critical tests:**

1. [ ] Navigate to `/admin/settings`
2. [ ] Click "Pattern Analysis" tab
3. [ ] Verify all fields load with default values
4. [ ] **Verify "Max LLM Calls" field does NOT exist**
5. [ ] Change Recent days to 14
6. [ ] Change Min pattern size to 5
7. [ ] Click "Save Changes"
8. [ ] See success message
9. [ ] Refresh page
10. [ ] Verify Recent days still shows 14
11. [ ] Verify Min pattern size shows 5
12. [ ] Click "Run Analysis Now"
13. [ ] See success message with task ID
14. [ ] **No mention of LLM budget or call limits**

**If all 14 pass → Feature is functional ✅**

---

**End of Testing Checklist**
