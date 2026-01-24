# Phase 1 Quick Start Guide

## ✅ What We Just Built

**Edge Case Auto-Capture**: When validators mark something as "edge_case", it now automatically creates a searchable library entry with full context, auto-detected categories, and smart tags.

---

## 🚀 How to Deploy & Test

### Step 1: Apply Database Migration

```bash
cd backend
../venv/bin/alembic upgrade head
```

**Expected output**:
```
INFO  [alembic.runtime.migration] Running upgrade k9l0m1n2o3p4 -> 032c4d0d6846, add_edge_case_validation_links
```

### Step 2: Restart Backend

```bash
cd backend
../venv/bin/uvicorn api.main:app --reload
```

### Step 3: Test the Flow

1. **Start Frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

2. **Navigate to Validation Dashboard**:
   - Go to http://localhost:5173/validation
   - Claim a validation item

3. **Mark as Edge Case**:
   - Review the validation
   - Click the yellow "Edge Case" button
   - Add feedback: "Testing Phase 1 auto-capture"
   - Click Submit

4. **Verify Toast Notification**:
   - Should see: "ℹ️ Edge Case Recorded"
   - Message: "This edge case has been added to the library..."
   - Duration: 5 seconds

5. **Check Edge Case Library**:
   - Navigate to http://localhost:5173/edge-cases
   - Should see new entry with:
     - Title: "Edge Case: {scenario} - Step {N}"
     - Your feedback in description
     - Auto-detected category
     - Auto-generated tags
     - Status: "new"
     - Auto Created: true

---

## 🔍 What to Look For

### In the Edge Case Library

**Title Format**:
```
Edge Case: Restaurant Reservation - Step 3
Edge Case: Weather Query - Step 1
```

**Auto-Detected Categories**:
- `high_confidence_failure` - AI was very confident but wrong (red flag!)
- `boundary_condition` - Scores near threshold (needs analysis)
- `low_confidence` - Expected uncertainty (might be okay)
- `needs_classification` - Requires human categorization

**Auto-Generated Tags** (examples):
```json
[
  "en-US",                    // Language
  "category:weather",         // Scenario category
  "low-confidence",           // Confidence level
  "review:needs_review",      // Why in queue
  "multi-turn",               // From scenario tags
  "edge-case-2024-12"         // Date stamp
]
```

**Scenario Definition** (comprehensive JSON):
```json
{
  "scenario_id": "abc-123",
  "scenario_name": "Weather Query",
  "step_order": 2,
  "user_utterance": "What about tomorrow?",
  "expected_response": "Tomorrow will be sunny with highs of 75°F",
  "actual_response": "Today will be sunny with highs of 72°F",
  "language_code": "en-US",
  "confidence_score": 0.45,
  "review_status": "needs_review",
  "validation_result_id": "...",
  "human_validation_id": "...",
  "multi_turn_execution_id": "..."
}
```

---

## 🐛 Troubleshooting

### Edge Case Not Created

**Symptom**: Clicked "edge_case" but nothing in library

**Check**:
1. Backend logs for errors:
   ```bash
   # Look for errors in HumanValidationService
   tail -f backend/logs/app.log | grep "edge_case"
   ```

2. Database migration ran:
   ```bash
   cd backend
   ../venv/bin/alembic current
   # Should show: 032c4d0d6846 (head)
   ```

3. API response includes `edge_case_id`:
   ```bash
   # In browser DevTools Network tab, check submit response:
   {
     "success": true,
     "data": {
       "edge_case_id": "..."  // Should be present
     }
   }
   ```

### Wrong Category Detected

**Symptom**: All edge cases show "needs_classification"

**Reason**: Detection service needs validation result with scores

**Fix**: Ensure validation results have:
- `confidence_score` populated
- `review_status` set
- Related to actual test execution

### No Tags Generated

**Symptom**: Edge case created but `tags` array is empty

**Check**:
1. Scenario has metadata:
   ```sql
   SELECT script_metadata FROM scenario_scripts WHERE id = '...';
   ```

2. Multi-turn execution has language_code:
   ```sql
   SELECT language_code FROM multi_turn_executions WHERE id = '...';
   ```

---

## 📊 Monitoring Edge Cases

### Quick Stats Query

```sql
-- Count auto-created edge cases
SELECT COUNT(*) FROM edge_cases WHERE auto_created = true;

-- Edge cases by category
SELECT category, COUNT(*) as count
FROM edge_cases
WHERE auto_created = true
GROUP BY category
ORDER BY count DESC;

-- Edge cases by severity
SELECT severity, COUNT(*) as count
FROM edge_cases
WHERE auto_created = true
GROUP BY severity;

-- Most common tags
SELECT tag, COUNT(*) as frequency
FROM edge_cases, unnest(tags) as tag
WHERE auto_created = true
GROUP BY tag
ORDER BY frequency DESC
LIMIT 10;

-- Edge cases created today
SELECT COUNT(*) FROM edge_cases
WHERE auto_created = true
AND discovered_date = CURRENT_DATE;
```

### Dashboard Queries

```sql
-- Edge case rate (% of validations marked as edge_case)
SELECT
  COUNT(CASE WHEN validation_decision = 'edge_case' THEN 1 END) * 100.0 /
  COUNT(*) as edge_case_rate
FROM human_validations
WHERE submitted_at >= NOW() - INTERVAL '7 days';

-- Top scenarios producing edge cases
SELECT
  s.name,
  COUNT(ec.id) as edge_case_count
FROM edge_cases ec
JOIN scenario_scripts s ON s.id = ec.script_id
WHERE ec.auto_created = true
GROUP BY s.name
ORDER BY edge_case_count DESC
LIMIT 10;
```

---

## 🎯 Success Criteria

### Week 1 Goals:
- [ ] At least 10 edge cases auto-created
- [ ] All edge cases have valid categories (not all "needs_classification")
- [ ] Tags are relevant and searchable
- [ ] Validators report seeing "Edge Case Recorded" toast
- [ ] No errors in backend logs

### Month 1 Goals:
- [ ] 100+ edge cases in library
- [ ] Clear category distribution (not 90% one category)
- [ ] Edge cases linked properly to validations
- [ ] Search by tags works effectively
- [ ] Patterns emerging (top 3-5 categories identified)

---

## 📈 Next Steps After Phase 1

Once Phase 1 is running smoothly:

1. **Analyze Patterns** (Week 2-3)
   - Group edge cases by category
   - Identify top 5 failure patterns
   - Share insights with team

2. **Plan Phase 2** (Week 4)
   - Pattern recognition & grouping
   - Automatic similarity detection
   - Pattern group creation

3. **Iterate on Detection** (Ongoing)
   - Refine category detection logic
   - Add new categories as patterns emerge
   - Improve tag generation

---

## 🆘 Getting Help

### Backend Issues
- Check: `backend/services/human_validation_service.py:168` - `_create_edge_case_entry()`
- Check: `backend/services/edge_case_detection_service.py` - Category/tag logic

### Frontend Issues
- Check: `frontend/src/components/Validation/ValidationModal.tsx:517` - Toast logic

### Database Issues
- Check migration: `backend/alembic/versions/032c4d0d6846_add_edge_case_validation_links.py`
- Rollback if needed: `alembic downgrade -1`

---

## ✅ Deployment Checklist

Before marking Phase 1 complete:

- [ ] Migration applied successfully
- [ ] Backend restarted with new code
- [ ] Frontend showing new toast message
- [ ] Test edge case created manually
- [ ] Edge case appears in `/edge-cases`
- [ ] Edge case has correct fields:
  - [ ] `auto_created = true`
  - [ ] `human_validation_id` links to validation
  - [ ] `validation_result_id` links to result
  - [ ] `category` is set
  - [ ] `tags` array has items
  - [ ] `severity` is set
  - [ ] `scenario_definition` has full context
- [ ] No errors in logs
- [ ] Validators tested and approve

---

**🎉 You're Ready to Go!**

Phase 1 transforms edge case marking from a dead-end action into an actionable intelligence pipeline. Every "edge_case" decision now builds your knowledge base and sets the foundation for future AI improvements.
