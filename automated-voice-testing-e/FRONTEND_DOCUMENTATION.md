# Frontend Documentation Index

This directory contains comprehensive documentation of the frontend codebase for the Voice AI Automated Testing Framework.

## Documents Included

### 1. FRONTEND_FEATURE_ANALYSIS.md (21 KB)
**Comprehensive feature analysis of the entire frontend**

A detailed examination of all UI capabilities, components, and features:
- Complete page inventory with functionality descriptions
- 45+ component architecture breakdown by category
- 6 Redux slices with state management details
- 21 service files with API integration methods
- 17 type definition files with interfaces
- Feature capabilities (testing, validation, analytics, etc.)
- UI components library and patterns
- Performance optimizations
- Data flow architecture

**Use this when:** You need to understand what UI capabilities exist, how features work, or what components are available.

### 2. FRONTEND_ARCHITECTURE_MAP.md (15 KB)
**Visual architecture and data flow diagrams**

Shows how the frontend is structured and how data flows through the system:
- Component hierarchy tree from App.tsx down to leaf components
- Redux state tree structure
- Service layer architecture with all 21 services
- Three detailed data flow examples:
  - Human validation workflow
  - Dashboard data loading
  - Test case list with filters
- Component composition patterns
- Integration points between frontend and backend

**Use this when:** You need to understand system architecture, how components relate to each other, or how data flows through the application.

### 3. FRONTEND_QUICK_REFERENCE.md (16 KB)
**Quick reference guide and development patterns**

Practical guide for developers working with the codebase:
- File location index for pages, components, services, Redux, and types
- Common development tasks with code examples:
  - Adding a new page
  - Adding a dashboard widget
  - Fetching data from API
  - Adding Redux state
  - Creating filters
  - Handling loading/error states
- Key hooks and patterns:
  - Virtual scrolling
  - Form submission
  - API calls with cleanup
- Material-UI grid breakpoints
- Redux dispatch pattern
- Testing patterns
- API response format
- Styling conventions
- Debug tips

**Use this when:** You're actively developing features and need quick code patterns, file locations, or development examples.

---

## Frontend Overview

### Tech Stack
- **Framework**: React 18 with TypeScript
- **State Management**: Redux Toolkit
- **Styling**: Material-UI (MUI)
- **API Communication**: Axios
- **Routing**: React Router v6
- **Build Tool**: Vite
- **Testing**: Vitest

### Key Statistics
- **Component Files**: 45
- **Lines of Code**: ~9,300
- **Service Files**: 21
- **Type Definition Files**: 17
- **Redux Slices**: 6
- **Pages**: ~37
- **Routes**: 20+
- **Dashboard Widgets**: 12+

### Core Features
1. **Test Execution & Monitoring** - Real-time test run tracking
2. **Human Validation Workflow** - Queue-based item assignment with decision capture
3. **Advanced Analytics** - Multi-dimensional trend analysis
4. **Regression Detection** - Automatic regression finding with baseline management
5. **Edge Case Management** - Scenario library and tracking
6. **Defect Management** - Issue tracking with severity and status
7. **Integration Management** - Slack, Jira, GitHub integration setup
8. **Knowledge Base** - Article creation and publishing
9. **CI/CD Integration** - Pipeline monitoring
10. **Configuration Management** - Environment-specific settings

---

## How to Navigate the Documentation

### If you need to understand...

**What UI features exist?**
→ Start with FRONTEND_FEATURE_ANALYSIS.md Section 1 (Pages) and Section 6 (Key Features)

**How validation workflow works?**
→ FRONTEND_FEATURE_ANALYSIS.md Section 1 "Validation Workflow Pages" + FRONTEND_ARCHITECTURE_MAP.md "Data Flow Examples - Human Validation Workflow"

**Where to find a specific component?**
→ FRONTEND_QUICK_REFERENCE.md "File Locations - Components"

**How to add a new dashboard widget?**
→ FRONTEND_QUICK_REFERENCE.md "Common Tasks - Add a New Dashboard Widget"

**How data flows in the application?**
→ FRONTEND_ARCHITECTURE_MAP.md "Data Flow Examples"

**What services are available?**
→ FRONTEND_FEATURE_ANALYSIS.md Section 4 (Services) or FRONTEND_ARCHITECTURE_MAP.md "Service Layer Architecture"

**What are the Redux slices and state structure?**
→ FRONTEND_FEATURE_ANALYSIS.md Section 3 (State Management) or FRONTEND_ARCHITECTURE_MAP.md "Redux State Tree"

**How to implement virtual scrolling for large lists?**
→ FRONTEND_QUICK_REFERENCE.md "Key Hooks & Patterns - Virtual Scrolling Pattern"

**What testing patterns should I use?**
→ FRONTEND_QUICK_REFERENCE.md "Testing Pattern"

**How to set up API calls with proper cleanup?**
→ FRONTEND_QUICK_REFERENCE.md "Key Hooks & Patterns - API Call with Cleanup"

---

## Component Organization

### By Feature Domain

**Test Execution** (pages + components):
- TestRunsPage, TestRunDetail
- ExecutionTable
- Services: testRun.service.ts

**Test Case Management**:
- TestCaseList, TestCaseCreatePage, TestCaseDetail
- TestCaseForm, LanguageVariations, ScenarioEditor, VersionHistory
- Services: testCase.service.ts, testCaseVersion.service.ts
- Redux: testCaseSlice

**Human Validation**:
- ValidationDashboard, ValidationInterface
- ExpectedActualComparison, AudioPlayer
- Services: validation.service.ts
- Redux: validationSlice

**Analytics & Reporting**:
- Analytics page
- PassRateTrendCard, DefectTrendCard, PerformanceTrendCard, ComparisonView
- TrendChart, BarChart, PieChart, Heatmap
- Services: analytics.service.ts

**Regression Management**:
- RegressionList, RegressionComparison, BaselineManagement
- Services: regression.service.ts

**Defect Management**:
- DefectList, DefectDetail
- DefectForm, DefectAssignmentModal
- Services: defect.service.ts

**Integrations**:
- IntegrationsDashboard, GitHub, Jira, Slack
- IntegrationLogs
- Services: integration-specific slices

**Knowledge Base**:
- KnowledgeBase, ArticleEditor, ArticleView, KnowledgeBaseSearch
- Services: knowledgeBase.service.ts

**Dashboard**:
- Dashboard page
- 12 widget components (ExecutiveSummary, RealTimeExecution, etc.)
- Services: dashboard.service.ts, realTimeMetrics.service.ts

---

## Key Concepts

### Redux Pattern
All async data fetching uses Redux Toolkit thunks. Example structure:
```
Service (API call) ← Thunk (handles async) ← Component (dispatch + selector)
```

### Service Layer
All API communication goes through service files:
- Services use Axios with custom interceptors
- Services handle request/response transformation
- Services throw errors that components catch

### Component Pattern
Most components follow this pattern:
1. Props with typed data + loading/error/onRetry callbacks
2. Conditional rendering for loading → error → success states
3. useEffect with proper cleanup (cancelled flag)
4. Memoization for expensive computations

### Type Safety
- All data is fully typed with TypeScript interfaces
- Services have request/response types
- Components have Props types
- Redux state is typed (RootState)

---

## Common Workflows

### Reading Data
1. Component mounts
2. useEffect triggers service call or Redux dispatch
3. Loading state shown
4. Data received, state updated
5. Component re-renders with data

### Submitting Data
1. User fills form
2. Form validation
3. Service call triggered
4. Loading state shown
5. Success/error response
6. Callback triggered (navigation, state reset, etc.)

### Real-Time Updates
1. WebSocket connection established
2. Real-time metrics stream data
3. Component listens to Redux state changes
4. Auto-refresh on updates

---

## Development Guidelines

### When Adding Features
1. Create types first (types/myFeature.ts)
2. Create service (services/myFeature.service.ts)
3. Create Redux slice if needed (store/slices/mySlice.ts)
4. Create components (components/)
5. Create pages (pages/)
6. Add routes (App.tsx)
7. Add to navigation (Sidebar.tsx)
8. Add tests

### File Size Guidelines
- Pages: typically 100-300 lines
- Components: typically 50-150 lines
- Services: typically 50-200 lines
- Keep functions small and focused

### Error Handling
- Always show loading state
- Always show error state with retry option
- Use Alert component for errors
- Log errors to console in development

### Performance
- Use Virtual scrolling for large lists
- Use useMemo for expensive computations
- Use useCallback for event handlers
- Lazy load pages (React.lazy)
- Implement proper cleanup in useEffect

---

## Getting Started

1. **Review architecture**: Read FRONTEND_ARCHITECTURE_MAP.md sections 1-2
2. **Understand features**: Skim FRONTEND_FEATURE_ANALYSIS.md for overview
3. **Learn patterns**: Study FRONTEND_QUICK_REFERENCE.md patterns
4. **Explore code**: Navigate to specific files mentioned in quick reference
5. **Start developing**: Use quick reference as guide for common tasks

---

## Related Documentation

- **Backend API**: See backend/api/routes/ for endpoint details
- **Project Setup**: See CLAUDE.md for development commands
- **Tasks**: See TODOS.md for current development tasks

---

## Document Maintenance

These documents are auto-generated analyses of the codebase. If the codebase structure changes:
1. New major features added
2. Significant refactoring completed
3. New service layers created

Update the documentation by re-analyzing the codebase.

---

**Last Updated**: November 18, 2025
**Frontend Code Size**: 9,300+ lines across 45+ components
**Documentation Size**: 52 KB across 3 detailed documents
