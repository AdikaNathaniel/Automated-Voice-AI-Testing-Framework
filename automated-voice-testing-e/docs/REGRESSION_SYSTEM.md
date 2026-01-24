# Regression Detection & Tracking System

## Overview

The regression detection and tracking system provides comprehensive monitoring of test quality over time, automatically detecting when tests that previously passed start failing or when performance metrics degrade. The system intelligently handles LLM non-determinism by using tiered detection strategies.

## Key Features

- **Persistent Regression Tracking**: Historical record of all regressions with occurrence counting
- **Baseline Management**: Approve test executions as baselines for future comparison
- **Smart LLM Handling**: Tiered approach that accounts for LLM non-determinism
- **Automatic Detection**: Runs automatically after suite execution completes
- **Defect Workflow Integration**: Seamlessly create defects from regressions
- **Resolution Tracking**: Manual resolution with notes and auto-resolution when tests pass

## Architecture

### Tiered Detection Strategy

The system uses a three-tier approach to handle different types of metrics appropriately:

#### Tier 1: Deterministic Metrics (Strict Gating)
**Purpose**: Reliable regression detection with tight tolerances

**Metrics**:
- `command_kind_match` - Exact command matching
- `asr_confidence` - Speech recognition confidence
- `execution_success` - Test execution success
- `response_time_ms` - Response time
- `steps_completed` - Completion percentage

**Tolerance**: 5% degradation threshold
**Severity**: High for status regressions, variable for metrics based on magnitude

#### Tier 2: LLM Final Verdict (Advisory)
**Purpose**: Track LLM verdict changes without strict gating

**Metric**:
- `llm_final_verdict` - Final ensemble decision (pass/fail) ONLY
- **Does NOT track**: Individual evaluator scores (relevance, correctness, tone, entity_accuracy)

**Tolerance**: Wide tolerances, advisory status
**Severity**: Medium (advisory, not high-severity alerts)

**Important**: LLM variance means individual scores fluctuate naturally. Only the final ensemble verdict is stable enough to track.

#### Tier 3: Suite-Level Aggregates (Future)
**Purpose**: Trend analysis across multiple test runs

**Metrics** (planned):
- Average pass rate over time
- Median response times
- Overall suite health scores

### Components

```
┌──────────────────────────────────────────────────────────────────┐
│                      Suite Execution Flow                         │
└───────────────────┬──────────────────────────────────────────────┘
                    │
                    ▼
    ┌───────────────────────────────┐
    │  Execute Test Suite           │
    │  (tasks/execution.py)         │
    └───────────────┬───────────────┘
                    │
                    ▼
    ┌───────────────────────────────┐
    │  Finalize Suite Run           │
    │  (_maybe_finalize_suite_run)  │
    └───────────────┬───────────────┘
                    │
                    ▼
    ┌───────────────────────────────┐
    │  Trigger Regression Detection │
    │  (detect_suite_regressions)   │
    └───────────────┬───────────────┘
                    │
                    ▼
    ┌──────────────────────────────────────────────────────┐
    │  Smart Regression Detector                           │
    │  - Fetch baselines for each scenario                 │
    │  - Compare current vs baseline (tiered strategy)     │
    │  - Record/update regressions                         │
    │  - Auto-resolve passing tests                        │
    └───────────────┬──────────────────────────────────────┘
                    │
                    ▼
    ┌───────────────────────────────┐
    │  Regression Tracking Service  │
    │  - Record regressions         │
    │  - Update occurrence counts   │
    │  - Link to defects            │
    │  - Resolve regressions        │
    └───────────────────────────────┘
```

## Database Schema

### regressions Table

```sql
CREATE TABLE regressions (
    id UUID PRIMARY KEY,
    tenant_id UUID,  -- Multi-tenant scoping
    script_id UUID NOT NULL REFERENCES scenario_scripts(id) ON DELETE CASCADE,
    category VARCHAR(50) NOT NULL,  -- 'status', 'metric', 'llm'
    severity VARCHAR(50) NOT NULL DEFAULT 'medium',  -- 'low', 'medium', 'high', 'critical'
    status VARCHAR(50) NOT NULL DEFAULT 'active',  -- 'active', 'investigating', 'resolved', 'ignored'
    baseline_version INT,  -- Version of baseline used for detection
    detection_date TIMESTAMP WITH TIME ZONE NOT NULL,  -- First detection
    resolution_date TIMESTAMP WITH TIME ZONE,  -- When resolved
    last_seen_date TIMESTAMP WITH TIME ZONE NOT NULL,  -- Most recent occurrence
    occurrence_count INT NOT NULL DEFAULT 1,  -- How many times detected
    details JSONB NOT NULL DEFAULT '{}',  -- Regression-specific data
    linked_defect_id UUID REFERENCES defects(id) ON DELETE SET NULL,
    resolved_by UUID REFERENCES users(id) ON DELETE SET NULL,
    resolution_note TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Indexes for efficient queries
CREATE INDEX ix_regressions_status ON regressions(status);
CREATE INDEX ix_regressions_category ON regressions(category);
CREATE INDEX ix_regressions_detection_date ON regressions(detection_date);
CREATE INDEX ix_regressions_script_status ON regressions(script_id, status);
```

### regression_baselines Table (Existing)

Stores approved baseline snapshots for scenarios.

## API Endpoints

### Baseline Management

#### GET /regressions/{script_id}/baselines
Get baseline history for a scenario.

**Response**:
```json
{
  "scriptId": "uuid",
  "history": [
    {
      "version": 1,
      "status": "pass",
      "metrics": {...},
      "approvedAt": "2025-01-15T10:30:00Z",
      "approvedBy": "user-uuid",
      "note": "Initial baseline"
    }
  ],
  "pending": {
    "status": "pass",
    "metrics": {...},
    "detectedAt": "2025-01-16T14:00:00Z"
  }
}
```

#### POST /regressions/{script_id}/baseline
Approve a baseline for a scenario.

**Request**:
```json
{
  "status": "pass",
  "metrics": {
    "command_kind_match": 1.0,
    "asr_confidence": 0.95
  },
  "note": "Baseline after feature release"
}
```

**Permissions**: Admin, QA Lead

### Regression Tracking

#### GET /regressions/records
List tracked regression records.

**Query Parameters**:
- `status` - Filter by status (active, investigating, resolved, ignored)
- `category` - Filter by category (status, metric, llm)
- `script_id` - Filter by scenario script
- `skip`, `limit` - Pagination

**Response**:
```json
{
  "total": 15,
  "active": 8,
  "resolved": 7,
  "items": [
    {
      "id": "uuid",
      "scriptId": "uuid",
      "scriptName": "Login Flow",
      "category": "status",
      "severity": "high",
      "status": "active",
      "occurrenceCount": 3,
      "detectionDate": "2025-01-15T10:00:00Z",
      "lastSeenDate": "2025-01-16T15:00:00Z",
      "linkedDefectId": null
    }
  ]
}
```

#### POST /regressions/records/{regression_id}/resolve
Manually resolve a regression.

**Request**:
```json
{
  "note": "Fixed by PR #123"
}
```

**Permissions**: Admin, QA Lead

#### POST /regressions/records/{regression_id}/create-defect
Create a defect from a regression.

**Request**:
```json
{
  "severity": "high",
  "additional_notes": "Impacts production users"
}
```

**Response**:
```json
{
  "defect_id": "uuid",
  "regression_id": "uuid",
  "message": "Defect created successfully from regression"
}
```

**Permissions**: Admin, QA Lead

## User Workflows

### 1. Setting Up Baselines

1. **Execute Scenario**: Run a test scenario to completion
2. **Navigate to Scenario Detail**: View the scenario detail page
3. **Review Pending Baseline**: See "Pending Baseline Approval" section
4. **Approve Baseline**: Click "Approve as Baseline" button
5. **Add Notes**: Optionally add approval notes
6. **Confirm**: Baseline is now active for regression detection

**Entry Points**:
- Scenario Detail page (primary)
- Suite Run Detail page (batch approval - future)
- Comparison view (from execution detail - future)

### 2. Managing Regressions

1. **View Regressions**: Navigate to `/regressions`
2. **Filter**: Use status dropdown (active, investigating, resolved, ignored)
3. **Review Details**:
   - See occurrence count
   - View detection date and last seen date
   - Check linked defects
4. **Take Action**:
   - **Compare**: View baseline vs current comparison
   - **Create Defect**: Convert regression to defect for tracking
   - **Resolve**: Mark as resolved with notes

### 3. Regression → Defect Workflow

1. **Identify Regression**: See active regression in list
2. **Create Defect**: Click "Create Defect" button
3. **Defect Auto-Created**:
   - Title: Generated from regression details
   - Description: Includes baseline comparison
   - Severity: Inherits from regression
   - Linked: Regression links to defect
4. **Track Resolution**: Manage defect through normal workflow
5. **Auto-Update**: Regression status changes to "investigating"

## Implementation Details

### SmartRegressionDetector

Location: `backend/services/smart_regression_detector.py`

**Key Methods**:
- `detect_suite_regressions(suite_run_id, tenant_id)` - Main entry point
- `_detect_execution_regressions(execution, baseline)` - Per-execution detection
- `_check_status_regression()` - Tier 1: Status regression
- `_check_deterministic_metrics()` - Tier 1: Metric regression
- `_check_llm_verdict_regression()` - Tier 2: LLM verdict

**Metric Extraction** (`_extract_metrics`):
```python
# ✅ DOES extract:
- command_kind_match
- asr_confidence
- execution_success
- response_time_ms
- steps_completed
- llm_final_verdict (pass/fail ONLY)

# ❌ DOES NOT extract:
- Individual LLM evaluator scores (relevance, correctness, tone, etc.)
- These fluctuate due to LLM non-determinism
```

### RegressionTrackingService

Location: `backend/services/regression_tracking_service.py`

**Key Methods**:
- `record_regression(finding, tenant_id, baseline_version)` - Create or update regression
- `resolve_regression(regression_id, resolved_by, note)` - Manual resolution
- `auto_resolve_passing_tests(script_id)` - Auto-resolution when test passes
- `create_defect_from_regression(regression_id, created_by, severity_override)` - Defect creation
- `list_regressions(filters, pagination)` - Query regressions

**Occurrence Tracking**:
- First detection: Creates new regression record
- Subsequent detections: Increments `occurrence_count`, updates `last_seen_date`
- Helps identify persistent vs intermittent issues

### Celery Task Integration

Location: `backend/tasks/regression.py`

**Task**: `detect_suite_regressions`
- **Trigger**: Automatically after suite run completes
- **Process**:
  1. Fetch all executions for suite
  2. For each execution, get baseline and detect regressions
  3. Record findings in database
  4. Auto-resolve passing tests
- **Result**: Returns count and details of detected regressions

## UI Components

### RegressionListNew

Location: `frontend/src/pages/Regressions/RegressionListNew.tsx`

**Features**:
- Status filtering (all, active, investigating, resolved, ignored)
- Stats cards (total, active, resolved)
- Action buttons:
  - **Compare**: View baseline vs current comparison
  - **Create Defect**: Convert to defect (only for active, non-linked)
  - **Resolve**: Mark as resolved (only for active)
- Color-coded severity and status badges
- Occurrence count display
- Links to linked defects

### Baseline Approval UI

Location: `frontend/src/pages/Scenarios/ScenarioDetail.tsx`

**Sections**:
1. **Regression Baseline** - Only shown for active scenarios
2. **Current Baseline** - Shows active baseline version, status, approval info
3. **Pending Baseline** - Shows awaiting approval with metrics preview
4. **Approval Modal** - Clean modal with explanation and notes field
5. **Baseline History Link** - Quick access to full history page

**Permissions**:
- Only Admin and QA Lead can approve baselines
- Permission checks prevent unauthorized approval

## Best Practices

### 1. Baseline Approval

- ✅ **DO**: Approve baselines after successful releases or major updates
- ✅ **DO**: Add descriptive notes explaining why baseline was approved
- ✅ **DO**: Review metrics before approval to ensure quality
- ❌ **DON'T**: Approve failing tests as baselines
- ❌ **DON'T**: Approve without reviewing the execution details

### 2. Regression Management

- ✅ **DO**: Create defects for high-severity regressions immediately
- ✅ **DO**: Add resolution notes when manually resolving
- ✅ **DO**: Monitor occurrence counts to identify persistent issues
- ✅ **DO**: Review regressions regularly to prevent accumulation
- ❌ **DON'T**: Ignore active regressions without investigation
- ❌ **DON'T**: Resolve without understanding root cause

### 3. LLM Verdict Handling

- ✅ **DO**: Treat LLM verdict regressions as advisory signals
- ✅ **DO**: Investigate when LLM verdict changes consistently
- ✅ **DO**: Use deterministic metrics for strict gating decisions
- ❌ **DON'T**: Gate deployments on LLM verdict changes alone
- ❌ **DON'T**: Compare individual LLM evaluator scores

## Troubleshooting

### No Regressions Detected

**Possible Causes**:
1. No baselines set for scenarios
2. Suite run not yet finalized
3. Regression detection task failed

**Solutions**:
1. Approve baselines for scenarios (see Scenario Detail page)
2. Wait for suite run to complete fully
3. Check Celery worker logs for errors

### False Positives

**Possible Causes**:
1. Baseline needs updating after intentional changes
2. Tolerance too strict for metric
3. Environment-specific variations

**Solutions**:
1. Approve new baseline after verifying changes are intentional
2. Adjust metric tolerances in `SmartRegressionDetector.DETERMINISTIC_METRICS`
3. Investigate environment differences

### Regressions Not Auto-Resolving

**Possible Causes**:
1. Test still failing
2. Different scenario variant
3. Auto-resolution task not running

**Solutions**:
1. Verify test passes successfully
2. Ensure same scenario (check script_id)
3. Check Celery task execution in logs

## Configuration

### Environment Variables

```bash
# Enable automatic regression detection (default: true)
ENABLE_AUTO_REGRESSION=true

# Regression detection tolerances (future)
REGRESSION_TOLERANCE_DETERMINISTIC=0.05  # 5% for deterministic metrics
REGRESSION_TOLERANCE_LLM=0.15  # 15% for LLM verdicts
```

### Permissions

Regression mutation operations require one of:
- `ADMIN` role
- `ORG_ADMIN` role
- `QA_LEAD` role

Read operations are available to all authenticated users.

## Future Enhancements

### Planned Features

1. **Batch Baseline Approval**: Approve multiple baselines from suite run detail
2. **Tier 3 Suite Aggregates**: Track suite-level health trends
3. **Custom Metric Rules**: Per-scenario tolerance configuration
4. **Regression Notifications**: Slack/email alerts for new regressions
5. **Regression Reports**: Weekly summaries and trend analysis
6. **Baseline Diff View**: Visual comparison of baseline changes
7. **Regression Grouping**: Group related regressions by root cause

### Potential Improvements

- Machine learning for severity classification
- Automatic root cause analysis
- Integration with CI/CD for gating
- Regression heat maps and visualizations
- Historical regression trending

## References

- [Validation Pipeline Documentation](./VALIDATION_PIPELINE.md)
- [Database Schema](./database-schema.md)
- [API Guide](./api-guide.md)
- Migration: `a4b5c6d7e8f9_add_regressions_table.py`
- Model: `backend/models/regression.py`
- Services: `backend/services/regression_*.py`
- Frontend: `frontend/src/pages/Regressions/`
