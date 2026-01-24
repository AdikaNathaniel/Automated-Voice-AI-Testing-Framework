# Frontend Architecture Map

## Component Hierarchy & Data Flow

```
App.tsx (Router)
├── HomePage (public)
├── LoginPage (public)
└── Protected Routes
    ├── Dashboard
    │   ├── ExecutiveSummary (snapshot data)
    │   ├── RealTimeExecution (live metrics)
    │   ├── ValidationAccuracy (accuracy metrics)
    │   ├── LanguageCoverage (per-language stats)
    │   ├── TestCoverage (area coverage %)
    │   ├── DefectTracking (severity breakdown)
    │   ├── CICDStatus (pipeline status)
    │   ├── EdgeCaseStatistics (category breakdown)
    │   ├── SystemHealth (health metrics)
    │   ├── QueueMetrics (queue status)
    │   └── RecentTestRuns (latest executions)
    │
    ├── TestCases Management
    │   ├── TestCaseList (paginated with search/filters)
    │   │   └── TestCaseSearch, LanguageSelector, StatusBadge
    │   ├── TestCaseCreatePage
    │   │   └── TestCaseForm, LanguageVariations, ScenarioEditor
    │   └── TestCaseDetail
    │       ├── VersionHistory, TestCaseLanguage
    │       └── CommentThread
    │
    ├── Test Runs
    │   ├── TestRunsPage (virtual-scrolled table)
    │   │   └── LanguageSelector, Chip badges
    │   └── TestRunDetail
    │       └── ExecutionTable
    │
    ├── Validation Workflow
    │   ├── ValidationDashboard
    │   │   ├── Queue Stats Card
    │   │   ├── Validator Stats Card
    │   │   ├── Priority Distribution
    │   │   └── Language Distribution
    │   └── ValidationInterface
    │       ├── ExpectedActualComparison
    │       ├── AudioPlayer
    │       ├── Timer Display
    │       └── Decision Buttons (pass/fail/edge_case)
    │
    ├── Regression Management
    │   ├── RegressionList
    │   ├── RegressionComparison
    │   └── BaselineManagement
    │
    ├── Edge Cases
    │   ├── EdgeCaseLibrary
    │   ├── EdgeCaseCreate
    │   └── EdgeCaseDetail
    │
    ├── Analytics
    │   ├── Analytics (main page)
    │   ├── PassRateTrendCard (TrendChart)
    │   ├── DefectTrendCard (TrendChart)
    │   ├── PerformanceTrendCard (TrendChart)
    │   └── ComparisonView (BarChart/PieChart)
    │
    ├── Defects
    │   ├── DefectList (filtered table)
    │   │   └── StatusBadge, Chip (severity)
    │   └── DefectDetail
    │       ├── DefectForm, DefectAssignmentModal
    │       └── CommentThread, RelatedExecutions
    │
    ├── Integrations
    │   ├── IntegrationsDashboard
    │   ├── GitHub, Jira, Slack (individual config pages)
    │   └── IntegrationLogs
    │
    ├── Knowledge Base
    │   ├── KnowledgeBase (article grid)
    │   ├── ArticleEditor
    │   ├── ArticleView
    │   └── KnowledgeBaseSearch
    │
    ├── Configurations
    │   ├── ConfigurationList
    │   └── ConfigurationEditor
    │       ├── ActivationToggle
    │       └── ConfigHistory
    │
    ├── CI/CD
    │   ├── CICDRuns
    │   └── PipelineView
    │
    ├── Translation
    │   └── TranslationWorkflow
    │
    └── Layout Wrapper (MainLayout)
        ├── AppBar (Header)
        ├── Drawer (Sidebar)
        │   └── Menu items with active state
        └── Main Content Area
```

---

## Redux State Tree

```
store/
├── auth (authSlice)
│   ├── user: { id, email, name, role }
│   ├── token: string | null
│   ├── loading: boolean
│   └── error: string | null
│
├── validation (validationSlice)
│   ├── queue: ValidationQueue[]
│   ├── current: ValidationQueue | null
│   ├── stats: ValidationStats | null
│   ├── validatorSummary: ValidatorPersonalStats | null
│   ├── validatorLeaderboard: ValidatorLeaderboardEntry[]
│   ├── validatorAccuracyTrend: ValidatorAccuracyPoint[]
│   ├── timeSpent: number
│   ├── timerStarted: number | null
│   ├── loading: boolean
│   └── error: string | null
│
├── testCase (testCaseSlice)
│   ├── testCases: TestCase[]
│   ├── currentTestCase: TestCase | null
│   ├── filters: TestCaseFilters
│   ├── pagination: { page, pageSize, total }
│   ├── loading: boolean
│   └── error: string | null
│
├── slackIntegration (slackIntegrationSlice)
│   ├── config: SlackIntegrationConfig | null
│   ├── status: 'connected' | 'disconnected' | 'error'
│   ├── loading: boolean
│   └── error: string | null
│
├── jiraIntegration (jiraIntegrationSlice)
│   ├── config: JiraIntegrationConfig | null
│   ├── status: 'connected' | 'disconnected' | 'error'
│   ├── loading: boolean
│   └── error: string | null
│
└── githubIntegration (githubIntegrationSlice)
    ├── config: GitHubIntegrationConfig | null
    ├── status: 'connected' | 'disconnected' | 'error'
    ├── loading: boolean
    └── error: string | null
```

---

## Service Layer Architecture

```
services/
├── api.ts (Axios instance with interceptors)
│   └── Used by all other services
│
├── auth.service.ts
│   ├── login(email, password)
│   ├── logout()
│   ├── refreshToken()
│   └── getCurrentUser()
│
├── validation.service.ts
│   ├── fetchValidationQueue(filters)
│   ├── claimValidation(itemId)
│   ├── submitValidation(data)
│   ├── releaseValidation(itemId)
│   └── fetchValidationStats()
│
├── testRun.service.ts
│   ├── getTestRuns(params)
│   ├── getTestRunDetail(runId)
│   └── getTestRunExecutions(runId)
│
├── testCase.service.ts
│   ├── getTestCases(filters, pagination)
│   ├── getTestCaseById(id)
│   ├── createTestCase(data)
│   ├── updateTestCase(id, data)
│   ├── deleteTestCase(id)
│   └── duplicateTestCase(id)
│
├── testCaseVersion.service.ts
│   ├── getVersionHistory(caseId)
│   ├── compareVersions(caseId, v1, v2)
│   └── revertVersion(caseId, versionId)
│
├── dashboard.service.ts
│   ├── getDashboardSnapshot(filters)
│   └── getRealTimeMetrics(filters)
│
├── realTimeMetrics.service.ts
│   └── Provides WebSocket/polling for live data
│
├── regression.service.ts
│   ├── getRegressions(params)
│   ├── getComparison(caseId)
│   └── approveBaseline(caseId, data)
│
├── defect.service.ts
│   ├── getDefects(filters)
│   ├── getDefectDetail(id)
│   ├── createDefect(data)
│   ├── updateDefect(id, data)
│   └── assignDefect(id, userId)
│
├── edgeCase.service.ts
│   ├── getEdgeCases(filters)
│   ├── createEdgeCase(data)
│   └── getEdgeCaseDetail(id)
│
├── knowledgeBase.service.ts
│   ├── getKnowledgeBaseArticles(params)
│   ├── getArticleDetail(id)
│   ├── createArticle(data)
│   ├── updateArticle(id, data)
│   └── deleteArticle(id)
│
├── configuration.service.ts
│   ├── getConfigurations(params)
│   ├── getConfigDetail(id)
│   ├── updateConfiguration(id, data)
│   └── getConfigHistory(id)
│
├── analytics.service.ts
│   └── getTrendAnalytics(filters) → (trends, comparisons)
│
├── translation.service.ts
│   ├── getTranslationTasks()
│   ├── updateTranslation(taskId, data)
│   └── verifyTranslation(taskId)
│
├── activity.service.ts
│   └── getActivityFeed(filters)
│
├── comment.service.ts
│   ├── getComments(entityId)
│   ├── createComment(data)
│   └── deleteComment(commentId)
│
├── cicd.service.ts
│   ├── getCICDRuns()
│   └── getPipelineStatus()
│
└── websocket.service.ts
    ├── connectMetricsStream()
    ├── subscribeToQueue()
    └── subscribeToExecution()
```

---

## Data Flow Examples

### 1. Human Validation Workflow

```
User logs in
    ↓
authSlice.login() → API → JWT token
    ↓
ProtectedRoute allows access
    ↓
ValidationDashboard mounts
    ↓
useEffect triggers:
  - dispatch(fetchValidationStats()) → validation service
  - dispatch(fetchValidationQueue()) → validation service
    ↓
Redux state updated with queue and stats
    ↓
User clicks "Claim Next Validation"
    ↓
dispatch(claimValidation(itemId)) → validation service
    ↓
Redux state updated: current = claimed item
    ↓
Navigate to ValidationInterface
    ↓
ValidationInterface renders:
  - Displays test case info from current item
  - Shows AudioPlayer if audio available
  - Shows ExpectedActualComparison
  - Starts timer (updateValidationTimer action)
    ↓
User reviews and makes decision (pass/fail/uncertain)
    ↓
dispatch(submitValidation(decision, feedback)) → validation service
    ↓
API submits decision to backend
    ↓
Redux state cleared
    ↓
Navigate back to ValidationDashboard
```

### 2. Dashboard Data Loading

```
Dashboard mounted
    ↓
useEffect triggers:
  Promise.all([
    getDashboardSnapshot(filters),    ← API call
    getRealTimeMetrics(filters)       ← API call
  ])
    ↓
Data fetched → State (snapshot, realTimeMetrics)
    ↓
12 widget components render in parallel:
  - ExecutiveSummary (from snapshot.kpis)
  - RealTimeExecution (from realTimeMetrics)
  - ValidationAccuracy (from snapshot.validationAccuracy)
  - LanguageCoverage (from snapshot.languageCoverage)
  - TestCoverage (from snapshot.testCoverage)
  - DefectTracking (from snapshot.defects/defectTrend)
  - CICDStatus (from snapshot.cicdStatus)
  - EdgeCaseStatistics (from snapshot.edgeCases)
  - etc.
    ↓
30-second interval refreshes data
```

### 3. Test Case List with Filters

```
TestCaseList mounted
    ↓
useEffect triggers:
  dispatch(fetchTestCases(filters))
    ↓
Redux testCaseSlice thunk calls testCase service
    ↓
testCase.service.getTestCases(filters, pagination) → API
    ↓
Data fetched → Redux state
    ↓
Component renders table with:
  - Search box (debounced)
  - Filter dropdowns (category, type, suite, status)
  - Language selector
  - Paginated table (handles sort, pagination)
    ↓
User changes filter
    ↓
setFilters() → useEffect → dispatch(fetchTestCases(newFilters))
    ↓
API called with new filters
    ↓
Table updates with new results
```

---

## Component Composition Patterns

### Pattern 1: Data Display Widget
```
Widget Component (e.g., ExecutiveSummary)
  ├── Props: data, loading, error, onRetry
  ├── Conditional Rendering:
  │   ├── if (loading) → CircularProgress
  │   ├── if (error) → Alert with Retry button
  │   └── else → Display formatted data
  └── Used by: Dashboard page
```

### Pattern 2: List with Filters
```
List Page Component (e.g., TestCaseList)
  ├── Local State:
  │   ├── filters (search, category, type, etc.)
  │   ├── pagination (page, pageSize)
  │   └── selected items (for bulk actions)
  ├── useEffect: dispatch(fetch) on filter/page change
  ├── Children:
  │   ├── Filter controls (TextField, Select, Dropdown)
  │   ├── Table/Grid with data
  │   └── Pagination controls
  └── Actions: create, edit, delete, bulk operations
```

### Pattern 3: Form Dialog
```
Form Component (e.g., DefectForm)
  ├── Props: initialData (optional), onSubmit
  ├── Local State: formData, errors
  ├── Children:
  │   ├── TextField inputs (title, description, etc.)
  │   ├── Select dropdowns (category, severity)
  │   └── Buttons (Submit, Cancel)
  └── onSubmit: Validation → Service call → Callback
```

### Pattern 4: Async Data Component
```
DataComponent
  ├── useEffect: Fetch data on mount
  ├── useCallback: Handle refresh, filter changes
  ├── isMountedRef: Prevent state update on unmount
  ├── Local State: data, loading, error
  └── Conditional Rendering:
      ├── Loading state
      ├── Error state with retry
      └── Data display
```

---

## Key Integration Points

### Frontend ↔ Backend Communication

```
Frontend                          API Endpoints                Backend
─────────────────────────────────────────────────────────────────────

auth.service                  →  POST /api/v1/auth/login      → FastAPI
                              ←  Returns JWT token

validation.service            →  GET  /api/v1/validation      → FastAPI
                              →  POST /api/v1/validation/{id}/claim
                              →  POST /api/v1/validation/submit

testCase.service              →  GET  /api/v1/test-cases      → FastAPI
                              →  POST /api/v1/test-cases
                              →  PUT  /api/v1/test-cases/{id}
                              →  DELETE /api/v1/test-cases/{id}

testRun.service               →  GET  /api/v1/test-runs       → FastAPI

dashboard.service             →  GET  /api/v1/dashboard/snapshot

realTimeMetrics.service       →  WebSocket /ws/metrics        → FastAPI
                              ←  Real-time stream updates

[Similar patterns for defects, regressions, integrations, etc.]
```

---

## Performance Optimization Strategy

```
Virtual Scrolling
└── TestRunsPage
    ├── Row height: 64px
    ├── Overscan: 4 rows (buffer for smooth scroll)
    └── Supports 1000+ items with minimal re-renders

Memoization
├── useMemo: Widget data computations
├── useCallback: Event handlers
└── React.memo: Component wrapping (if needed)

Code Splitting
├── React.lazy: Page components
├── Suspense: Loading boundary
└── PageLoader: Fallback UI

Async Loading
├── isMountedRef: Prevent memory leaks
├── Cancellation: Abort fetch on unmount
└── Separate loading states: Per-widget granularity
```

