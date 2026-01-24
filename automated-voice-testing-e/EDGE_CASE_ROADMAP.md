# Edge Case Workflow Implementation Roadmap

## Current State Analysis
~~When validators mark a result as "edge_case", the decision is stored but NO automatic edge case library entry is created.~~ **UPDATE (Dec 2025)**: Phase 1, 2, and 3 are now complete. Edge cases are automatically created when validators mark items as "edge_case", LLM-powered pattern recognition groups similar edge cases together, and KB articles can be auto-generated from patterns.

---

## Phase 1: Basic Edge Case Auto-Capture ✅ COMPLETE
**Goal**: Automatically create edge case library entries when validators mark something as edge_case

**Status**: ✅ Fully implemented

### Backend Changes

#### 1. Update `HumanValidationService.submit_decision()`
**File**: `backend/services/human_validation_service.py`

```python
async def submit_decision(self, ...):
    # ... existing code ...

    # NEW: Auto-create edge case if decision is "edge_case"
    if validation_data.validation_decision == "edge_case":
        await self._create_edge_case_entry(
            db=db,
            queue_item=queue_item,
            validator_id=validator_id,
            feedback=validation_data.feedback,
            human_validation_id=human_validation.id
        )

    await db.commit()
    # ...

async def _create_edge_case_entry(
    self,
    db: AsyncSession,
    queue_item: ValidationQueue,
    validator_id: UUID,
    feedback: Optional[str],
    human_validation_id: UUID
) -> None:
    """
    Automatically create an edge case library entry from validation decision.
    """
    # Get validation result details
    validation_result = await db.get(ValidationResult, queue_item.validation_result_id)
    multi_turn_execution = validation_result.multi_turn_execution
    scenario = multi_turn_execution.scenario

    # Auto-generate title
    title = f"Edge Case: {scenario.name} - Step {queue_item.step_order}"

    # Build scenario definition from execution data
    scenario_definition = {
        "scenario_id": str(scenario.id),
        "scenario_name": scenario.name,
        "step_order": queue_item.step_order,
        "user_utterance": queue_item.user_utterance,
        "expected_response": queue_item.expected_response,
        "actual_response": queue_item.actual_response,
        "language_code": queue_item.language_code,
        "validation_result_id": str(validation_result.id),
        "human_validation_id": str(human_validation_id),
        "ai_scores": {
            "houndify": {...},  # Extract from validation_result
            "llm_ensemble": {...}
        }
    }

    # Auto-detect category based on failure patterns
    category = await self._detect_edge_case_category(validation_result)

    # Create edge case
    edge_case = EdgeCase(
        title=title,
        description=feedback or "Marked as edge case during human validation",
        scenario_definition=scenario_definition,
        tags=await self._generate_edge_case_tags(validation_result),
        severity="medium",  # Default, can be updated later
        category=category,
        status="new",
        script_id=scenario.id,
        discovered_date=datetime.utcnow(),
        discovered_by=str(validator_id),
        tenant_id=scenario.tenant_id
    )
    db.add(edge_case)
```

#### 2. Add Edge Case Pattern Detection
**File**: `backend/services/edge_case_detection_service.py` (NEW)

```python
class EdgeCaseDetectionService:
    """
    Detects patterns in edge cases and auto-categorizes them.
    """

    async def detect_category(
        self,
        validation_result: ValidationResult
    ) -> str:
        """
        Auto-detect edge case category based on validation scores and context.

        Categories:
        - ambiguous_intent: Low intent match, high semantic similarity
        - boundary_condition: Scores near threshold values
        - unexpected_behavior: Pass on one validator, fail on another
        - language_specific: Only fails in certain languages
        - context_dependent: Depends on conversation history
        """
        # Implementation logic
        pass

    async def generate_tags(
        self,
        validation_result: ValidationResult
    ) -> List[str]:
        """Generate relevant tags based on failure patterns"""
        tags = []

        # Language tag
        if validation_result.multi_turn_execution.language_code:
            tags.append(validation_result.multi_turn_execution.language_code)

        # Confidence level tags
        if validation_result.confidence_score:
            if validation_result.confidence_score < 0.5:
                tags.append("low-confidence")
            elif validation_result.confidence_score > 0.8:
                tags.append("high-confidence-failure")

        # Scenario category
        if validation_result.multi_turn_execution.scenario.script_metadata:
            category = validation_result.multi_turn_execution.scenario.script_metadata.get("category")
            if category:
                tags.append(f"category:{category}")

        return tags
```

#### 3. Database Schema Updates
**File**: `backend/models/edge_case.py`

Ensure edge case model includes:
- `human_validation_id` (FK to HumanValidation) - links back to the decision that created it
- `validation_result_id` (FK to ValidationResult) - links to the test result
- `auto_created` (Boolean) - distinguish manual vs auto-created
- `pattern_group_id` (UUID, nullable) - for grouping similar edge cases

### Frontend Changes

#### 4. Edge Case Quick View from Validation Dashboard
**File**: `frontend/src/pages/Validation/ValidationDashboardNew.tsx`

Add a "View Edge Cases" button for completed items that were marked as edge_case:

```typescript
{itemStatus === 'completed' && (item as any).humanValidationDecision === 'edge_case' && (
  <button
    onClick={(e) => {
      e.stopPropagation();
      // Navigate to edge case library filtered by this validation
      navigate(`/edge-cases?validation_id=${item.queueId}`);
    }}
    className="text-xs text-amber-600 dark:text-amber-400 hover:underline"
  >
    View Edge Case
  </button>
)}
```

#### 5. Edge Case Created Notification
**File**: `frontend/src/components/Validation/ValidationModal.tsx`

Update submit success message:

```typescript
if (decision === 'edge_case') {
  showToast({
    type: 'info',
    title: 'Edge Case Recorded',
    message: 'Edge case added to library for analysis',
    duration: 5000,
  });
}
```

### Testing Requirements
- ✅ Unit test: Edge case auto-creation on "edge_case" decision
- ✅ Unit test: No edge case created for "pass" or "fail"
- ✅ Integration test: Full flow from validation submission to edge case in library
- ✅ Test: Edge case links back to validation result correctly

### Implementation Files
- `backend/services/human_validation_service.py` - `_create_edge_case_entry()` method
- `backend/services/edge_case_detection_service.py` - Category detection and tag generation
- `backend/models/edge_case.py` - Extended with `human_validation_id`, `validation_result_id`, `auto_created` fields

---

## Phase 2: Pattern Recognition & Grouping ✅ COMPLETE
**Goal**: Identify similar edge cases and group them for analysis

**Status**: ✅ Fully implemented with LLM-first approach

### Backend

#### 1. Similarity Detection Service
**File**: `backend/services/edge_case_similarity_service.py` (NEW)

```python
class EdgeCaseSimilarityService:
    """
    Finds similar edge cases using semantic similarity and clustering.
    """

    async def find_similar_edge_cases(
        self,
        edge_case: EdgeCase,
        threshold: float = 0.85
    ) -> List[EdgeCase]:
        """Find edge cases with similar utterances and failure patterns"""
        pass

    async def create_pattern_group(
        self,
        db: AsyncSession,
        edge_cases: List[EdgeCase],
        pattern_description: str
    ) -> PatternGroup:
        """Group related edge cases together"""
        pass
```

#### 2. Background Job: Pattern Analysis
**File**: `backend/tasks/edge_case_analysis.py` (NEW)

```python
@celery_app.task
def analyze_edge_case_patterns():
    """
    Nightly job to analyze edge cases and identify patterns.
    Groups similar cases, detects trends, generates insights.
    """
    pass
```

### Frontend

#### 3. Pattern Group View ✅
**File**: `frontend/src/pages/EdgeCases/EdgeCaseLibrary.tsx` (integrated as tab)

Show grouped edge cases with:
- Common characteristics ✅
- Frequency trend (trending patterns section) ✅
- Suggested actions ✅
- Filter edge cases by pattern group ✅

### Implementation Files
- `backend/services/edge_case_similarity_service.py` - LLM-first pattern detection + semantic similarity fallback
- `backend/services/llm_pattern_analysis_service.py` - LLM-powered pattern analysis
- `backend/tasks/edge_case_analysis.py` - Celery background job for batch pattern analysis
- `backend/models/pattern_group.py` - PatternGroup and EdgeCasePatternLink models
- `backend/api/routes/pattern_groups.py` - Pattern group CRUD + analysis trigger + trending
- `frontend/src/pages/EdgeCases/EdgeCaseLibrary.tsx` - Integrated tabs for Edge Cases & Pattern Groups
- `frontend/src/pages/PatternGroups/PatternGroupDetail.tsx` - Individual pattern group detail view
- `frontend/src/services/patternGroup.service.ts` - Pattern group API client

### How Pattern Recognition Works
1. **Batch Processing Only**: Pattern analysis runs via "Run Analysis" button or Celery scheduled task
2. **LLM-First Approach**: Claude/GPT analyzes edge cases to identify patterns (primary)
3. **Semantic Similarity Fallback**: If LLM unavailable, uses semantic similarity clustering
4. **All Edge Cases Analyzed**: Both auto-created and manually created edge cases are included

---

## Phase 3: Knowledge Base Integration ✅ COMPLETE
**Goal**: Convert edge case patterns into searchable knowledge

**Status**: ✅ Fully implemented

### Backend Implementation

#### 1. Database Schema Updates
**File**: `backend/models/knowledge_base.py`
- Added `pattern_group_id` (UUID FK to pattern_groups, SET NULL on delete)
- Added `source_type` ('manual' | 'auto_generated' | 'pattern_derived')
- Added `tags` (ARRAY of strings for multi-label categorization)
- Added `pattern_group` relationship

#### 2. KB Generation Service
**File**: `backend/services/kb_generation_service.py` (NEW)
```python
class KBGenerationService:
    """
    Generates Knowledge Base articles from Pattern Groups using LLM.
    Supports LLM-powered content generation with template fallback.
    """

    async def generate_from_pattern_group(
        self, db: AsyncSession, pattern_group_id: UUID, author_id: UUID, auto_publish: bool = False
    ) -> KnowledgeBase:
        """Auto-generate KB article from pattern group."""
```

#### 3. New API Endpoints
**File**: `backend/api/routes/knowledge_base.py`
- `POST /knowledge-base/generate-from-pattern/{pattern_group_id}` - Generate KB article from pattern
- `GET /knowledge-base/by-pattern/{pattern_group_id}` - Get articles linked to pattern
- Added filters: `source_type`, `pattern_group_id`, `tags`

### Frontend Implementation

#### 4. Knowledge Base Page Revamp
**File**: `frontend/src/pages/KnowledgeBase/KnowledgeBase.tsx`
- Tabs: All Articles | Pattern Insights | Guides | Troubleshooting
- Stats bar: Total, Pattern-Linked, Auto-Generated, Published counts
- Source type filter dropdown (All, Manual, Auto-Generated, Pattern Derived)
- Pattern link badges on article cards
- Tags display on cards
- Modern design matching Edge Cases page

#### 5. Pattern Group Detail Updates
**File**: `frontend/src/pages/PatternGroups/PatternGroupDetail.tsx`
- "Generate KB Article" button in header
- "Related Documentation" section showing linked KB articles
- Success/error status messages for generation
- Click-through navigation to article detail

### Implementation Files
- `backend/models/knowledge_base.py` - Extended with pattern group integration fields
- `backend/alembic/versions/p3k1b2a3c4d5_add_pattern_group_to_knowledge_base.py` - Migration
- `backend/services/kb_generation_service.py` - LLM-powered article generation
- `backend/api/routes/knowledge_base.py` - New endpoints and filters
- `backend/services/knowledge_base_service.py` - Updated with new filters
- `frontend/src/types/knowledgeBase.ts` - Extended types
- `frontend/src/services/knowledgeBase.service.ts` - New API functions
- `frontend/src/pages/KnowledgeBase/KnowledgeBase.tsx` - Complete UI revamp
- `frontend/src/pages/PatternGroups/PatternGroupDetail.tsx` - KB integration

---

## Phase 4: Edge Case Re-run & Verification ✅ COMPLETE (Simplified)
**Goal**: ~~Convert edge cases into new test scenarios~~ → Verify edge case fixes by re-running original scenario

**Status**: ✅ Implemented with simplified approach

### Original Plan vs Implementation

The original Phase 4 proposed a complex `ScenarioGeneratorService` to convert edge cases into new test scenarios. However, this was **redundant** because:
- Edge cases already have a `script_id` linking to the original scenario
- "Converting to scenario" just duplicates existing data
- The real need is to **re-run the original scenario** to verify if the issue is fixed

### Simplified Implementation

#### Backend: Re-run Edge Case Endpoint
**File**: `backend/api/routes/edge_cases.py`

```python
@router.post("/{edge_case_id}/rerun")
async def rerun_edge_case_scenario(edge_case_id: UUID, ...):
    """
    Re-run the scenario that caused this edge case.
    Returns pass/fail result to verify if the issue is fixed.
    """
    # Fetches edge case → gets script_id → executes scenario
    # Returns: { passed: bool, message: str, execution_id: str, ... }
```

#### Frontend: Re-run & Resolution UI
**File**: `frontend/src/pages/EdgeCases/EdgeCaseDetail.tsx`

- **Re-run Scenario** button - Executes the linked scenario
- **Mark Resolved** button - Changes status to "resolved" when fix verified
- **Reopen** button - Changes status back to "active" if issue recurs
- Result banner shows pass/fail after re-run
- View Scenario link to navigate to original scenario

#### Service Layer
**File**: `frontend/src/services/edgeCase.service.ts`

```typescript
export const rerunEdgeCaseScenario = async (id: string): Promise<RerunResult>
export const updateEdgeCase = async (id: string, input: EdgeCaseUpdateInput): Promise<EdgeCase>
```

### Workflow

```
Edge Case Detail Page
        │
        ├── [Re-run Scenario] → Executes linked scenario
        │           │
        │           ├── PASSED → [Mark Resolved] → status: "resolved"
        │           │
        │           └── FAILED → Still broken, investigate further
        │
        └── [View Scenario] → Navigate to /scenarios/{scriptId}
```

### Why This Approach is Better

| Original Plan | Simplified Implementation |
|---------------|---------------------------|
| Create duplicate scenarios | Re-use existing scenario |
| Generate variations with LLM | Test exact failing case |
| Complex ScenarioGeneratorService | Simple re-run endpoint |
| More scenarios to maintain | No duplication |

---

## Phase 5: Analytics & Reporting ✅ COMPLETE
**Goal**: Track edge case metrics and trends

**Status**: ✅ Fully implemented

### Backend Implementation

#### 1. Edge Case Analytics Service
**File**: `backend/services/edge_case_analytics_service.py` (NEW)
```python
class EdgeCaseAnalyticsService:
    """Aggregates edge case metrics for analytics dashboards."""

    def get_analytics(date_from, date_to) -> Dict:
        """Returns: summary, count_over_time, category/severity/status distributions,
        resolution_metrics, top_patterns, auto_vs_manual breakdown"""

    def get_trend_comparison(date_to, period_days) -> Dict:
        """Compares current vs previous period for trend analysis"""
```

#### 2. Analytics Endpoint
**File**: `backend/api/routes/edge_cases.py`
- `GET /edge-cases/analytics` - Returns comprehensive analytics
  - Query params: `date_from`, `date_to`, `include_trend`
  - Returns: summary, time series, distributions, patterns, resolution rate

#### 3. Pydantic Schemas
**File**: `backend/api/schemas/edge_case.py`
- Added: `EdgeCaseAnalyticsResponse`, `AnalyticsSummary`, `TimeSeriesPoint`,
  `DistributionItem`, `ResolutionMetrics`, `TopPattern`, `AutoVsManual`,
  `TrendComparison`, `TrendPeriod`

### Frontend Implementation

#### 4. Edge Case Analytics Dashboard
**File**: `frontend/src/pages/EdgeCases/EdgeCaseAnalytics.tsx` (NEW)

Features:
- Summary stat cards (total, active, resolved, critical, resolution rate)
- Date range selector (7d, 30d, 90d)
- Time series bar chart for edge case counts over time
- Distribution charts (by severity, status, category)
- Auto-created vs manual breakdown
- Top patterns listing with click-through to pattern detail
- Resolution breakdown metrics
- Trend comparison badge (up/down/stable vs previous period)

#### 5. Service & Types
- `frontend/src/services/edgeCase.service.ts` - Added `getEdgeCaseAnalytics()`
- `frontend/src/types/edgeCase.ts` - Added analytics types

#### 6. Navigation
- Route: `/edge-cases/analytics`
- "Analytics" button added to Edge Case Library header

### Testing
**File**: `backend/tests/test_edge_case_analytics_service.py`
- 11 tests covering all analytics functionality
- Summary counts, date filtering, distributions, resolution metrics
- Pattern linking, trend comparison, empty database handling

---

## Phase 6: AI Model Improvement Loop (3-4 weeks)
**Goal**: Use edge cases to improve AI validation accuracy

### Backend

#### 1. Model Retraining Pipeline
**File**: `backend/ml/model_retraining_service.py` (NEW)

```python
class ModelRetrainingService:
    """
    Uses validated edge cases to fine-tune LLM ensemble models.
    """

    async def prepare_training_data_from_edge_cases(
        self,
        db: AsyncSession,
        min_samples: int = 100
    ) -> TrainingDataset:
        """
        Extract edge cases with human decisions as training data.
        """
        pass

    async def fine_tune_evaluator_models(
        self,
        training_data: TrainingDataset
    ):
        """Fine-tune Gemini, GPT-4, Claude with edge case examples"""
        pass
```

#### 2. Confidence Threshold Adjustment
**File**: `backend/services/threshold_optimization_service.py` (NEW)

Analyze edge cases to optimize:
- When to auto-pass vs. send to queue
- Confidence score thresholds
- Which validators to use for which scenarios

---

## Phase 7: Notifications & Integrations (1 week)
**Goal**: Alert stakeholders about critical edge cases

### Backend

#### 1. Edge Case Alerts
**File**: `backend/services/alert_service.py`

```python
async def notify_critical_edge_case(
    edge_case: EdgeCase,
    notification_channels: List[str]  # ['slack', 'email', 'jira']
):
    """Send alerts when critical edge cases are found"""
    pass
```

### Frontend

#### 2. Edge Case Notification Settings
**File**: `frontend/src/pages/Settings/EdgeCaseNotifications.tsx` (NEW)

Configure:
- Alert thresholds (e.g., notify if >10 edge cases/day)
- Notification channels
- Severity levels to alert on

---

## Success Metrics

### Immediate (Phase 1-2) ✅ ACHIEVED
- ✅ 100% of "edge_case" decisions create library entries
- ✅ Validators can view edge cases from validation dashboard
- ✅ Similar edge cases are grouped (via batch pattern analysis)

### Medium-term (Phase 3-5) ✅ COMPLETE
- 📊 Edge case rate decreases by 20% month-over-month (due to test improvements)
- ✅ KB articles can be auto-generated from pattern groups
- ✅ Edge cases can be re-run to verify fixes (simplified from "convert to scenario")
- ✅ Analytics dashboard for edge case trends (Phase 5)

### Long-term (Phase 6-7) ⏳ PENDING
- 🤖 "Needs review" queue reduced by 30% (AI getting smarter)
- 🎯 Edge case resolution time < 48 hours average
- 📈 Product team uses edge case trends to prioritize voice AI improvements

---

## Estimated Total Effort
- **Phase 1**: ~~1-2 weeks~~ ✅ COMPLETE
- **Phase 2**: ~~2-3 weeks~~ ✅ COMPLETE
- **Phase 3**: ~~1 week~~ ✅ COMPLETE
- **Phase 4**: ~~2-3 weeks~~ ✅ COMPLETE (simplified to re-run approach)
- **Phase 5**: ~~1-2 weeks~~ ✅ COMPLETE
- **Phase 6**: 3-4 weeks ⏳ NOT STARTED
- **Phase 7**: 1 week ⏳ NOT STARTED

**Remaining: 4-5 weeks** (Phases 6-7)

## Recommended Next Steps
1. ~~**Start with Phase 1** (auto-capture)~~ ✅ DONE
2. ~~Run Phase 1 for 2-4 weeks to collect data~~ ✅ DONE
3. ~~Then proceed with Phases 2~~ ✅ DONE
4. ~~Phase 3 (Knowledge Base Integration)~~ ✅ DONE
5. ~~Phase 4 (Test Suite Enhancement)~~ ✅ DONE (simplified to re-run scenario approach)
6. ~~Phase 5 (Analytics & Reporting)~~ ✅ DONE
7. **Next**: Phase 6 (AI Model Improvement Loop) OR Phase 7 (Notifications)
8. Phase 6 can be done in parallel by different developers

## Dependencies
- Existing edge case library (✅ already built)
- Validation workflow (✅ already built)
- Knowledge base system (✅ already built)
- LLM ensemble validation (✅ already built)
- Pattern group system (✅ already built)

**Status (Dec 2025)**: Phases 1-5 complete. Core edge case workflow is fully functional with KB integration, pattern recognition, and analytics. Pattern recognition with LLM-first approach is operational. KB articles can be auto-generated from pattern groups using configurable LLM provider. Phase 4 simplified from "convert to scenario" to "re-run scenario" approach. Phase 5 analytics dashboard provides comprehensive edge case metrics, trends, and distributions. Ready to proceed with Phase 6 (AI Model Improvement) or Phase 7 (Notifications).

---

## Deferred: UI/UX Performance Optimizations

**Status**: Partially complete, to be revisited

The following UI/UX optimizations have been started but should be completed across remaining pages:

### Completed
- ✅ Shared components created: `LoadingSpinner`, `ErrorState`, `EmptyState`, `StatCard` (in `components/common/`)
- ✅ `usePageVisibility` hook for tab visibility detection (in `hooks/`)
- ✅ `useVisibilityPolling` hook for auto-pausing polling when tab hidden
- ✅ Pages updated: DefectList, CICDRuns, RegressionList, EdgeCaseLibrary, Analytics
- ✅ Chart optimizations: useMemo for TrendLineChart and SimpleBarChart in Analytics.tsx
- ✅ 70 tests for shared components and hooks

### Remaining Work
- ⏳ Apply shared components to more pages (Validation, Scenarios, TestSuites, etc.)
- ⏳ Integrate `useVisibilityPolling` into pages with auto-refresh functionality
- ⏳ Add virtualized lists for pages with large datasets (react-window or similar)
- ⏳ Memoize filter operations across remaining pages

### Notes
- All shared components support dark mode
- Components use Lucide React icons (no emojis)
- StatCard supports trend indicators and click actions
- usePageVisibility provides onVisible/onHidden callbacks for data refresh

---

## Changelog

### December 26, 2025 - Phase 5 Complete (Analytics & Reporting)
- Created `EdgeCaseAnalyticsService` with comprehensive aggregation queries
- Added `GET /edge-cases/analytics` endpoint with date range filtering
- Metrics include: summary counts, time series, distributions, resolution rate, top patterns
- Added trend comparison (current vs previous period)
- Created `EdgeCaseAnalytics.tsx` dashboard with charts and stat cards
- Date range selector (7d, 30d, 90d) for flexible analysis
- Distribution bars for severity, status, and category
- Auto-created vs manual breakdown visualization
- Top patterns listing with click-through navigation
- Added "Analytics" button to Edge Case Library header
- 11 unit tests for analytics service

### December 26, 2025 - Phase 4 Complete (Simplified Approach)
- Simplified Phase 4 from "convert to scenario" to "re-run scenario" approach
- Added `POST /edge-cases/{id}/rerun` endpoint to re-run linked scenario
- Added `PATCH /edge-cases/{id}` endpoint for status updates
- Updated EdgeCaseDetail.tsx with Re-run Scenario, Mark Resolved, Reopen buttons
- Added result banner showing pass/fail after scenario re-run
- Added `updateEdgeCase()` and `rerunEdgeCaseScenario()` to frontend service
- Edge cases can now be verified and resolved directly from the detail page

### December 26, 2025 - Phase 3 LLM Enhancement
- Added `KB_GENERATION_LLM_PROVIDER` env var to configure LLM provider (openai/anthropic/google)
- Added `KB_GENERATION_LLM_MODEL` env var to override default model per provider
- Implemented `generate_text()` method in all LLM adapters for plain text generation
- KB generation now uses configured LLM with automatic fallback to template
- Default models: gpt-4o (OpenAI), claude-sonnet-4-5-20250929 (Anthropic), gemini-1.5-pro (Google)

### December 25, 2025 - Phase 3 Complete
- Knowledge Base page completely revamped with modern UI (tabs, stats, filters)
- KB articles can now link to pattern groups via `pattern_group_id` field
- New `source_type` field tracks article origin (manual, auto_generated, pattern_derived)
- Tags array added to KB articles for multi-label categorization
- `KBGenerationService` generates structured markdown articles from patterns
- "Generate KB Article" button added to Pattern Group detail page
- "Related Documentation" section shows linked KB articles on pattern detail
- New API endpoints: `/generate-from-pattern/`, `/by-pattern/`
- Filter support for source_type, pattern_group_id, and tags
- Migration `p3k1b2a3c4d5` added pattern_group_id, source_type, tags to knowledge_base table

### December 2025 - Phases 1-2
- Phase 1 implemented: Auto-creation of edge cases from "edge_case" validation decisions
- Phase 2 implemented: LLM-powered pattern recognition with semantic similarity fallback
- Batch pattern analysis via Celery background job
- Pattern Groups integrated into Edge Cases page as tab
- Pattern group filter added to edge cases list view
- All edge cases (both auto-created and manual) included in pattern analysis
