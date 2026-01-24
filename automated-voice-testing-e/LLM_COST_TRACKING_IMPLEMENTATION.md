# LLM Cost Tracking - Implementation Summary

**Date**: 2025-12-29
**Status**: ✅ COMPLETE - Database-Driven Pricing with Audit Trail

**UPDATE (2025-12-29)**: Pricing is now database-driven instead of hardcoded. See `LLM_PRICING_AND_AUDIT_SYSTEM.md` for the new system.

---

## Overview

Implemented automated cost tracking for all LLM API calls in the pattern analysis system. Every LLM API call is now automatically logged with token usage and estimated costs for monitoring, budgeting, and cost optimization.

---

## Features Implemented

### 1. LLM Usage Logging Database Table

**Model**: `backend/models/llm_usage_log.py`

**Table**: `llm_usage_logs`

**Columns**:
- `id` (UUID): Primary key
- `tenant_id` (UUID): Organization that made the call
- `service_name` (String): Service that made the call (e.g., "pattern_analysis")
- `operation` (String): Specific operation (e.g., "analyze_edge_case", "match_pattern")
- `model` (String): LLM model used (e.g., "claude-sonnet-4.5")
- `provider` (String): API provider (e.g., "openrouter")
- `prompt_tokens` (Integer): Tokens in the prompt
- `completion_tokens` (Integer): Tokens in the completion
- `total_tokens` (Integer): Total tokens used
- `estimated_cost_usd` (Numeric): Estimated cost in USD
- `request_metadata` (JSONB): Additional context (edge_case_id, pattern_id, etc.)
- `response_metadata` (JSONB): Provider response metadata
- `duration_ms` (Integer): API call duration in milliseconds
- `success` (Boolean): Whether the call succeeded
- `error_message` (Text): Error message if failed
- `created_at` (DateTime): When the call was made

**Indexes**:
- Individual indexes on: tenant_id, service_name, model, provider, total_tokens, success, created_at
- Composite indexes for analytics:
  - (tenant_id, created_at)
  - (service_name, created_at)
  - (model, created_at)
  - (success, created_at)

### 2. Cost Calculation System

**File**: `backend/models/llm_usage_log.py`

**⚠️ DEPRECATED Pricing Dictionary**: `LLM_PRICING_FALLBACK` (kept as fallback only)

**✅ NEW: Database-Driven Pricing**: `llm_model_pricing` table

Pricing is now stored in the database and can be updated at runtime without code changes. The hardcoded dictionary is kept only as a fallback if database is unavailable.

**Function**: `calculate_cost(model, prompt_tokens, completion_tokens, db=None, provider="openrouter")`

- **Primary**: Queries `llm_model_pricing` table for active pricing
- **Fallback**: Uses hardcoded `LLM_PRICING_FALLBACK` if database unavailable
- **Default**: Returns conservative estimate if model not found

**Pricing Models Supported**:
- **Anthropic Claude**: Sonnet 4.5, Opus 4.5, 3.5 Sonnet, 3 Opus, 3 Haiku
- **OpenAI**: GPT-4 Turbo, GPT-4, GPT-3.5 Turbo
- **Google**: Gemini Pro, Gemini Pro Vision
- **Default**: Fallback pricing for unknown models

**See**: `LLM_PRICING_AND_AUDIT_SYSTEM.md` for complete database-driven pricing documentation.

### 3. Automatic Cost Tracking in LLM Service

**File**: `backend/services/llm_pattern_analysis_service.py`

**Changes**:

1. **Updated `__init__`**:
   - Added `db` parameter for database session
   - Added `tenant_id` parameter for cost attribution

2. **Updated `_call_llm` method**:
   - Tracks start time
   - Extracts token usage from API response
   - Calculates duration
   - Logs usage to database (success or failure)
   - Accepts `operation` and `metadata` parameters for detailed tracking

3. **New `_log_llm_usage` method**:
   - Creates LLMUsageLog entry
   - Calculates estimated cost
   - Writes to database
   - Logs cost information to application logs
   - Gracefully handles logging failures (doesn't break main flow)

4. **Updated all LLM method calls**:
   - `analyze_edge_case`: Tracks with edge_case_id, category, language
   - `generate_pattern_details`: Tracks with edge_case_count, categories
   - `match_to_existing_pattern`: Tracks with pattern_count, pattern_names

### 4. Integration with Edge Case Similarity Service

**File**: `backend/services/edge_case_similarity_service.py`

**Changes**:
- Passes database session to LLMPatternAnalysisService
- Sets `tenant_id` before each LLM call for accurate cost attribution
- Tenant extracted from edge_case object

---

## Database Migration

**File**: `backend/alembic/versions/y2z3a4b5c6d7_add_llm_usage_logs_table.py`

**Revision ID**: y2z3a4b5c6d7
**Revises**: x1y2z3a4b5c6

**To apply**:
```bash
cd backend
alembic upgrade head
```

**To verify**:
```bash
alembic current
# Should show: y2z3a4b5c6d7 (head)
```

---

## Usage Examples

### Query Daily Costs by Tenant

```sql
SELECT
    DATE(created_at) as date,
    COUNT(*) as api_calls,
    SUM(total_tokens) as total_tokens,
    SUM(estimated_cost_usd) as daily_cost
FROM llm_usage_logs
WHERE tenant_id = 'YOUR_TENANT_ID'
    AND created_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;
```

### Query Costs by Model

```sql
SELECT
    model,
    COUNT(*) as calls,
    AVG(prompt_tokens) as avg_prompt_tokens,
    AVG(completion_tokens) as avg_completion_tokens,
    SUM(estimated_cost_usd) as total_cost
FROM llm_usage_logs
WHERE tenant_id = 'YOUR_TENANT_ID'
    AND created_at >= NOW() - INTERVAL '7 days'
GROUP BY model
ORDER BY total_cost DESC;
```

### Query by Operation

```sql
SELECT
    operation,
    COUNT(*) as calls,
    AVG(duration_ms) as avg_duration_ms,
    AVG(estimated_cost_usd) as avg_cost_per_call,
    SUM(estimated_cost_usd) as total_cost
FROM llm_usage_logs
WHERE service_name = 'pattern_analysis'
    AND created_at >= NOW() - INTERVAL '7 days'
GROUP BY operation
ORDER BY total_cost DESC;
```

### Check Failed Calls

```sql
SELECT
    created_at,
    operation,
    model,
    error_message,
    request_metadata
FROM llm_usage_logs
WHERE success = false
    AND tenant_id = 'YOUR_TENANT_ID'
ORDER BY created_at DESC
LIMIT 20;
```

---

## Log Output Example

When an LLM call is made, you'll see logs like:

```
INFO - LLM usage logged: analyze_edge_case | Tokens: 1250 | Cost: $0.018750 | Duration: 1523ms
INFO - LLM usage logged: match_to_existing_pattern | Tokens: 856 | Cost: $0.012840 | Duration: 982ms
INFO - LLM usage logged: generate_pattern_details | Tokens: 2103 | Cost: $0.031545 | Duration: 2341ms
```

---

## Cost Monitoring Workflow

1. **Real-time Logging**: Every LLM call is automatically logged with cost estimate
2. **Daily Reports**: Query costs by tenant, service, model, or operation
3. **Budget Alerts**: Set up alerts based on daily/weekly/monthly cost thresholds
4. **Optimization**: Identify expensive operations and optimize prompts or models
5. **Attribution**: Accurately attribute costs to tenants for billing

---

## Files Modified/Created

### New Files (2)
1. `backend/models/llm_usage_log.py` - Database model and cost calculation
2. `backend/alembic/versions/y2z3a4b5c6d7_add_llm_usage_logs_table.py` - Migration

### Modified Files (3)
3. `backend/models/__init__.py` - Added llm_usage_log import
4. `backend/services/llm_pattern_analysis_service.py` - Added cost tracking
5. `backend/services/edge_case_similarity_service.py` - Pass db session and tenant_id

---

## Testing Checklist

### Database
- [ ] Migration applies successfully: `alembic upgrade head`
- [ ] Table exists: `\d llm_usage_logs` in psql
- [ ] All indexes created
- [ ] Migration can be rolled back: `alembic downgrade -1`

### Functionality
- [ ] Run pattern analysis with LLM enabled
- [ ] Check logs for cost tracking messages
- [ ] Query llm_usage_logs table for entries
- [ ] Verify tenant_id is correctly set
- [ ] Verify estimated_cost_usd is calculated
- [ ] Verify token counts are accurate
- [ ] Verify duration_ms is recorded

### Cost Calculation
- [ ] Cost for Claude Sonnet 4.5 matches expected: ~$0.018/1000 tokens
- [ ] Different models have different costs
- [ ] Cost increases with token usage
- [ ] Prompt and completion tokens counted separately

### Error Handling
- [ ] Cost tracking still works when API call fails
- [ ] error_message is recorded for failed calls
- [ ] success = false for failed calls
- [ ] Application doesn't crash if cost logging fails

### Analytics Queries
- [ ] Can query costs by tenant
- [ ] Can query costs by date range
- [ ] Can query costs by model
- [ ] Can query costs by operation
- [ ] Can identify most expensive operations

---

## Next Steps (Optional Enhancements)

### 1. Cost Dashboard API Endpoints

Create endpoints for cost analytics:
```python
@router.get("/analytics/llm-costs/daily")
async def get_daily_llm_costs(
    tenant_id: UUID,
    days: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """Get daily LLM costs for tenant."""
    # Query and aggregate costs
```

### 2. Budget Alerts

Implement automatic budget alerts:
```python
async def check_budget_alerts(tenant_id: UUID):
    """Check if tenant has exceeded budget thresholds."""
    daily_cost = await get_today_llm_cost(tenant_id)
    config = await get_tenant_config(tenant_id)

    if daily_cost > config.daily_budget_threshold:
        await send_budget_alert(tenant_id, daily_cost)
```

### 3. Cost Optimization Recommendations

Analyze usage patterns and suggest optimizations:
- Identify operations with high token usage
- Suggest prompt optimizations
- Recommend model downgrades for simple tasks

### 4. Export to BI Tools

Export cost data to:
- Grafana dashboards
- Datadog metrics
- Custom reporting tools

---

## Pricing Updates

**✅ NEW: Database-Driven Pricing** (December 2025)

Model pricing is now stored in the database and can be updated via API without code changes!

**Update process (NEW)**:
1. Admin logs into admin panel
2. Navigate to LLM Pricing management (`/api/v1/llm-pricing`)
3. Find the model to update
4. Update pricing via PATCH endpoint
5. Pricing takes effect immediately
6. Audit trail automatically logged

**Alternative - API Update**:
```bash
curl -X PATCH "http://localhost:8000/api/v1/llm-pricing/{pricing_id}" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt_price_per_1m": 3.50,
    "completion_price_per_1m": 16.00,
    "notes": "Price increase effective January 2026"
  }'
```

**Benefits**:
- ✅ No code deployment needed
- ✅ Instant updates
- ✅ Full audit trail of changes
- ✅ Historical pricing preserved
- ✅ Scheduled price changes supported

**Fallback**: If database is unavailable, system falls back to `LLM_PRICING_FALLBACK` dictionary in `backend/models/llm_usage_log.py`

**See**: `LLM_PRICING_AND_AUDIT_SYSTEM.md` for complete documentation.

---

## Summary

✅ **Complete automatic cost tracking for LLM API calls**
✅ **Database model with comprehensive tracking**
✅ **Real-time cost calculation and logging**
✅ **Per-tenant cost attribution**
✅ **Detailed metadata for analytics**
✅ **Performance tracking (duration_ms)**
✅ **Error tracking for failed calls**
✅ **Indexed for fast analytics queries**

**Status**: Ready for production use. Run migration and test with pattern analysis.
