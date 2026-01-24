# Frontend Quick Reference Guide

## File Locations

### Pages
```
/frontend/src/pages/
├── Dashboard/Dashboard.tsx                  - Main dashboard with 12 widgets
├── TestRuns/TestRunDetail.tsx              - Test run execution details
├── TestRunsPage.tsx                        - Virtual-scrolled test run list
├── Validation/ValidationDashboard.tsx      - Validation queue dashboard
├── Validation/ValidationInterface.tsx      - Human validator review UI
├── Validation/ValidatorStats.tsx           - Validator statistics page
├── TestCases/TestCaseList.tsx             - Test case listing with filters
├── TestCases/TestCaseCreatePage.tsx       - Create test case form
├── TestCases/TestCaseDetail.tsx           - Test case detail view
├── Analytics/Analytics.tsx                - Trend analysis and comparisons
├── Regressions/RegressionList.tsx         - Regression findings list
├── Regressions/RegressionComparison.tsx   - Baseline vs current comparison
├── Regressions/BaselineManagement.tsx     - Baseline approval workflow
├── Defects/DefectList.tsx                 - Defects table with filters
├── Defects/DefectDetail.tsx               - Defect detail with comments
├── EdgeCases/EdgeCaseLibrary.tsx          - Edge case scenarios list
├── EdgeCases/EdgeCaseCreate.tsx           - Create edge case
├── EdgeCases/EdgeCaseDetail.tsx           - Edge case details
├── Integrations/IntegrationsDashboard.tsx - Integration status overview
├── Integrations/GitHub.tsx                - GitHub config page
├── Integrations/Jira.tsx                  - Jira config page
├── Integrations/Slack.tsx                 - Slack config page
├── KnowledgeBase/KnowledgeBase.tsx        - Article grid listing
├── KnowledgeBase/ArticleEditor.tsx        - Create/edit articles
├── KnowledgeBase/ArticleView.tsx          - Display article
├── KnowledgeBase/KnowledgeBaseSearch.tsx  - Search articles
├── Configurations/ConfigurationList.tsx   - Config management
├── Configurations/ConfigurationEditor.tsx - Edit configuration
├── CICD/CICDRuns.tsx                      - Pipeline execution history
├── Translation/TranslationWorkflow.tsx    - Translation management
├── LoginPage.tsx                           - Authentication UI
├── HomePage.tsx                            - Landing page
└── DashboardPage.tsx                       - Dashboard page wrapper
```

### Components
```
/frontend/src/components/
├── Dashboard/
│   ├── ExecutiveSummary.tsx       - KPIs widget
│   ├── RealTimeExecution.tsx      - Queue & execution widget
│   ├── ValidationAccuracy.tsx     - Accuracy metrics
│   ├── LanguageCoverage.tsx       - Language coverage chart
│   ├── TestCoverage.tsx           - Test area coverage
│   ├── DefectTracking.tsx         - Defect summary
│   ├── CICDStatus.tsx             - Pipeline status
│   ├── EdgeCaseStatistics.tsx     - Edge case breakdown
│   ├── SystemHealth.tsx           - Health metrics
│   ├── QueueMetrics.tsx           - Queue status
│   ├── RecentTestRuns.tsx         - Latest runs
│   └── KPICard.tsx                - Generic KPI card
├── Validation/
│   ├── ExpectedActualComparison.tsx - Side-by-side comparison
│   └── AudioPlayer.tsx             - Audio playback
├── TestCase/
│   ├── TestCaseForm.tsx            - Create/edit form
│   ├── LanguageVariations.tsx      - Language management
│   ├── ScenarioEditor.tsx          - Scenario config
│   ├── VersionHistory.tsx          - Version timeline
│   └── TestCaseSearch.tsx          - Search component
├── TestRun/
│   └── ExecutionTable.tsx          - Execution list
├── Defects/
│   ├── DefectForm.tsx              - Defect creation
│   └── DefectAssignmentModal.tsx   - Assign defect
├── Analytics/
│   ├── PassRateTrendCard.tsx       - Pass rate chart
│   ├── DefectTrendCard.tsx         - Defect count chart
│   ├── PerformanceTrendCard.tsx    - Response time chart
│   └── ComparisonView.tsx          - Multi-dimensional comparison
├── Charts/
│   ├── TrendChart.tsx              - Line chart
│   ├── BarChart.tsx                - Bar chart
│   ├── PieChart.tsx                - Pie chart
│   └── Heatmap.tsx                 - Heatmap
├── Layout/
│   ├── MainLayout.tsx              - AppBar + Drawer wrapper
│   ├── Sidebar.tsx                 - Navigation menu
│   ├── Header.tsx                  - Header component
│   └── UserMenu.tsx                - User dropdown
├── Common/
│   ├── LanguageSelector.tsx        - Language dropdown
│   ├── StatusBadge.tsx             - Status indicator
│   ├── ProgressBar.tsx             - Progress indicator
│   └── TagSelector.tsx             - Tag multi-select
├── Configuration/
│   ├── ActivationToggle.tsx        - Toggle component
│   └── ConfigHistory.tsx           - Change audit trail
├── CICD/
│   └── PipelineView.tsx            - Pipeline visualization
├── Integrations/
│   └── IntegrationLogs.tsx         - Event logs
├── Activity/
│   └── ActivityFeed.tsx            - Activity timeline
├── Comments/
│   └── CommentThread.tsx           - Comment thread
├── ProtectedRoute.tsx              - Route guard
├── UserProfile.tsx                 - Profile display
└── PageLoader.tsx                  - Loading indicator
```

### Services
```
/frontend/src/services/
├── api.ts                      - Axios instance
├── auth.service.ts             - Authentication
├── validation.service.ts       - Validation workflow
├── testRun.service.ts          - Test run operations
├── testCase.service.ts         - Test case CRUD
├── testCaseVersion.service.ts  - Version management
├── dashboard.service.ts        - Dashboard data
├── realTimeMetrics.service.ts  - Live metrics/WebSocket
├── regression.service.ts       - Regression detection
├── defect.service.ts           - Defect management
├── edgeCase.service.ts         - Edge case operations
├── knowledgeBase.service.ts    - Knowledge base articles
├── configuration.service.ts    - Configuration management
├── analytics.service.ts        - Analytics/trends
├── translation.service.ts      - Translation tasks
├── activity.service.ts         - Activity feed
├── comment.service.ts          - Comments/threads
├── cicd.service.ts             - CI/CD operations
├── languageStatistics.service.ts
├── reportBuilder.service.ts
└── websocket.service.ts        - Real-time streaming
```

### Redux
```
/frontend/src/store/
├── index.ts                         - Store configuration
└── slices/
    ├── authSlice.ts                - Authentication state
    ├── validationSlice.ts          - Validation workflow state
    ├── testCaseSlice.ts            - Test case state
    ├── slackIntegrationSlice.ts    - Slack integration state
    ├── jiraIntegrationSlice.ts     - Jira integration state
    └── githubIntegrationSlice.ts   - GitHub integration state
```

### Types
```
/frontend/src/types/
├── auth.ts                   - User, auth types
├── validation.ts             - Validation domain types
├── testRun.ts                - Test run types
├── testCase.ts               - Test case types
├── dashboard.ts              - Dashboard widget types
├── defect.ts                 - Defect types
├── regression.ts             - Regression types
├── edgeCase.ts               - Edge case types
├── knowledgeBase.ts          - Article types
├── configuration.ts          - Config types
├── analytics.ts              - Analytics types
├── translation.ts            - Translation types
├── activity.ts               - Activity types
├── comments.ts               - Comment types
├── cicd.ts                   - CI/CD types
├── api.ts                    - API response types
└── languageStatistics.ts     - Language stats types
```

---

## Common Tasks

### Add a New Page
1. Create file: `/frontend/src/pages/MyFeature/MyPage.tsx`
2. Add route in `App.tsx`:
   ```tsx
   const MyPage = lazy(() => import('./pages/MyFeature/MyPage'));
   
   <Route path="/my-feature" element={<ProtectedRoute><MyPage /></ProtectedRoute>} />
   ```
3. Add to sidebar menu in `Sidebar.tsx`
4. Create service: `/frontend/src/services/myFeature.service.ts`
5. Create types: `/frontend/src/types/myFeature.ts`
6. Add test file: `/frontend/src/pages/__tests__/MyPage.test.tsx`

### Add a New Dashboard Widget
1. Create file: `/frontend/src/components/Dashboard/MyWidget.tsx`
2. Define props interface:
   ```tsx
   export type MyWidgetProps = {
     data: MyWidgetData;
     loading?: boolean;
     error?: string | null;
     onRetry?: () => void;
   };
   ```
3. Handle loading/error/data states
4. Import in `Dashboard.tsx`:
   ```tsx
   import MyWidget from '../../components/Dashboard/MyWidget';
   ```
5. Add to grid:
   ```tsx
   <Grid size={{ xs: 12, md: 6 }}>
     <MyWidget data={data} loading={loading} error={error} />
   </Grid>
   ```

### Fetch Data from API
1. Create service method:
   ```tsx
   // services/myFeature.service.ts
   export const getMyData = async (filters?: MyFilters) => {
     const response = await apiClient.get<MyDataResponse>('/v1/my-data', { params: filters });
     return response.data;
   };
   ```
2. Use in component:
   ```tsx
   const [data, setData] = useState(null);
   const [loading, setLoading] = useState(true);
   
   useEffect(() => {
     const fetch = async () => {
       try {
         const result = await getMyData(filters);
         setData(result);
       } catch (err) {
         setError(err.message);
       } finally {
         setLoading(false);
       }
     };
     fetch();
   }, [filters]);
   ```

### Add Redux State
1. Create slice:
   ```tsx
   // store/slices/mySlice.ts
   import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
   
   export const fetchMyData = createAsyncThunk('my/fetchData', async (params) => {
     const response = await myService.getData(params);
     return response;
   });
   
   export const mySlice = createSlice({
     name: 'my',
     initialState: { data: null, loading: false, error: null },
     extraReducers: (builder) => {
       builder.addCase(fetchMyData.pending, (state) => { state.loading = true; })
              .addCase(fetchMyData.fulfilled, (state, action) => {
                state.data = action.payload;
                state.loading = false;
              });
     }
   });
   ```
2. Add to store:
   ```tsx
   // store/index.ts
   import { mySlice } from './slices/mySlice';
   
   export const store = configureStore({
     reducer: {
       my: mySlice.reducer,
       // ...
     }
   });
   ```
3. Use in component:
   ```tsx
   const dispatch = useDispatch<AppDispatch>();
   const { data, loading } = useSelector((state: RootState) => state.my);
   
   useEffect(() => {
     dispatch(fetchMyData(params));
   }, [dispatch, params]);
   ```

### Create a Filter/Search Component
1. Create component with Material-UI TextField and Select
2. Add to page with useCallback for debounce
3. Integrate with service params

### Handle Loading/Error States
Pattern:
```tsx
const { loading, error, data } = // from service or Redux

if (loading) {
  return <CircularProgress />;
}

if (error) {
  return (
    <Alert 
      severity="error" 
      action={<Button onClick={handleRetry}>Retry</Button>}
    >
      {error}
    </Alert>
  );
}

return <div>{/* render data */}</div>;
```

---

## Key Hooks & Patterns

### Virtual Scrolling Pattern
```tsx
const [virtualRange, setVirtualRange] = useState({ start: 0, end: 0 });

const updateVirtualRange = useCallback((scrollTop, clientHeight) => {
  const firstVisible = Math.floor(scrollTop / ROW_HEIGHT);
  const visibleCount = Math.ceil(clientHeight / ROW_HEIGHT) + OVERSCAN * 2;
  setVirtualRange({
    start: Math.max(0, firstVisible - OVERSCAN),
    end: Math.min(data.length, start + visibleCount)
  });
}, [data.length]);

const visibleItems = data.slice(start, end);
```

### Form Submission Pattern
```tsx
const [formData, setFormData] = useState(initialData);
const [errors, setErrors] = useState({});

const handleSubmit = async (e) => {
  e.preventDefault();
  try {
    await service.create(formData);
    onSuccess();
  } catch (err) {
    setErrors(err.fieldErrors);
  }
};
```

### API Call with Cleanup
```tsx
useEffect(() => {
  let cancelled = false;

  const fetch = async () => {
    try {
      const result = await service.getData();
      if (!cancelled) setData(result);
    } catch (err) {
      if (!cancelled) setError(err.message);
    }
  };

  fetch();
  return () => { cancelled = true; };
}, []);
```

---

## Material-UI Grid Breakpoints

- `xs`: 0px (mobile)
- `sm`: 600px (mobile)
- `md`: 900px (tablet)
- `lg`: 1200px (desktop)
- `xl`: 1536px (large desktop)

Example:
```tsx
<Grid size={{ xs: 12, sm: 6, md: 4, lg: 3 }}>
  {/* Full width on mobile, half on tablet, quarter on desktop */}
</Grid>
```

---

## Redux Dispatch Pattern

```tsx
import { useDispatch, useSelector } from 'react-redux';
import type { AppDispatch, RootState } from '../../store';

const Component = () => {
  const dispatch = useDispatch<AppDispatch>();
  const state = useSelector((state: RootState) => state.mySlice);

  useEffect(() => {
    dispatch(fetchData(params));
  }, [dispatch, params]);

  return <div>{state.data}</div>;
};
```

---

## Testing Pattern

```tsx
// Component.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import MyComponent from './MyComponent';

describe('MyComponent', () => {
  test('renders loading state', () => {
    render(<MyComponent loading={true} />);
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  test('renders data', async () => {
    const data = { id: '1', name: 'Test' };
    render(<MyComponent data={data} loading={false} />);
    
    await waitFor(() => {
      expect(screen.getByText('Test')).toBeInTheDocument();
    });
  });

  test('shows error state with retry', () => {
    const onRetry = vi.fn();
    render(
      <MyComponent 
        error="Failed to load" 
        onRetry={onRetry} 
      />
    );
    
    const retryBtn = screen.getByRole('button', { name: /retry/i });
    fireEvent.click(retryBtn);
    
    expect(onRetry).toHaveBeenCalled();
  });
});
```

---

## API Response Format

Backend responses follow this pattern:
```json
{
  "success": true,
  "data": { /* actual data */ },
  "message": "Optional message",
  "request_id": "optional-id"
}
```

Or for errors:
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error description",
    "details": {}
  },
  "request_id": "optional-id"
}
```

---

## Styling Conventions

Use `sx` prop with Material-UI:
```tsx
<Box sx={{
  display: 'flex',
  gap: 2,
  p: 3,
  bgcolor: 'background.paper',
  border: '1px solid',
  borderColor: 'divider',
  borderRadius: 1
}}>
  {/* content */}
</Box>
```

Common theme tokens:
- Colors: `primary`, `secondary`, `error`, `warning`, `info`, `success`
- Spacing: `p` (padding), `m` (margin), `gap` (gap in flex)
- Typography: `variant`: `h1`-`h6`, `body1`, `body2`, `caption`

---

## Debug Tips

1. Redux DevTools: Install Redux DevTools browser extension
2. React DevTools: Inspect component hierarchy and props
3. Network tab: Monitor API calls
4. Console: Check for errors
5. Breakpoints: Use `debugger` in code

