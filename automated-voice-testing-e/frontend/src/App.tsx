/**
 * Main App component with React Router configuration
 * Defines all application routes including protected routes
 * Uses AppLayout for sidebar navigation
 */

import { Suspense, lazy, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import ProtectedRoute from './components/ProtectedRoute';
import PageLoader from './components/PageLoader';
import ErrorBoundary from './components/common/ErrorBoundary';
import SkipLink from './components/common/SkipLink';
import { ToastProvider } from './components/common/Toast';
import AppLayout from './components/Layout/AppLayout';
import { initializeAuth } from './store/slices/authSlice';
import type { AppDispatch } from './store';
import './App.css';

/**
 * Error handler for logging caught errors
 */
const handleError = (error: Error, errorInfo: React.ErrorInfo) => {
  // Log to console in development
  console.error('App Error:', error, errorInfo);

  // TODO: Send to monitoring service (Sentry, etc.)
  // This will be implemented when monitoring service is integrated
};

const HomePage = lazy(() => import('./pages/HomePage'));
const LoginPage = lazy(() => import('./pages/LoginPage'));
const RegisterPage = lazy(() => import('./pages/Register'));
const DashboardPage = lazy(() => import('./pages/Dashboard/DashboardNew'));
const ValidationDashboardPage = lazy(() => import('./pages/Validation/ValidationDashboardNew'));
const ValidationResultDetailPage = lazy(() => import('./pages/Validation/ValidationResultDetail'));
const GitHubIntegrationPage = lazy(() => import('./pages/Integrations/GitHub'));
const JiraIntegrationPage = lazy(() => import('./pages/Integrations/Jira'));
const SlackIntegrationPage = lazy(() => import('./pages/Integrations/Slack'));
const IntegrationsDashboardPage = lazy(() => import('./pages/Integrations/IntegrationsDashboard'));
const RegressionListPage = lazy(() => import('./pages/Regressions/RegressionListNew'));
const RegressionComparisonPage = lazy(() => import('./pages/Regressions/RegressionComparison'));
const BaselineManagementPage = lazy(() => import('./pages/Regressions/BaselineManagement'));
const KnowledgeBasePage = lazy(() => import('./pages/KnowledgeBase/KnowledgeBase'));
const KnowledgeBaseArticlePage = lazy(() => import('./pages/KnowledgeBase/ArticleView'));
const KnowledgeBaseEditorPage = lazy(() => import('./pages/KnowledgeBase/ArticleEditor'));
const KnowledgeBaseSearchPage = lazy(() => import('./pages/KnowledgeBase/KnowledgeBaseSearch'));
const AnalyticsPage = lazy(() => import('./pages/Analytics/Analytics'));
const CICDDashboardPage = lazy(() => import('./pages/CICD/CICDDashboard'));
const OrganizationConfigurationsPage = lazy(() => import('./pages/Configurations/OrganizationConfigurations'));
const ConfigurationEditorPage = lazy(() => import('./pages/Configurations/ConfigurationEditor'));
const DefectListPage = lazy(() => import('./pages/Defects/DefectList'));
const DefectDetailPage = lazy(() => import('./pages/Defects/DefectDetail'));
const EdgeCaseLibraryPage = lazy(() => import('./pages/EdgeCases/EdgeCaseLibrary'));
const EdgeCaseDetailPage = lazy(() => import('./pages/EdgeCases/EdgeCaseDetail'));
const EdgeCaseCreatePage = lazy(() => import('./pages/EdgeCases/EdgeCaseCreate'));
const EdgeCaseEditPage = lazy(() => import('./pages/EdgeCases/EdgeCaseEdit'));
const EdgeCaseAnalyticsPage = lazy(() => import('./pages/EdgeCases/EdgeCaseAnalytics'));
const PatternGroupDetailPage = lazy(() => import('./pages/PatternGroups/PatternGroupDetail'));
const ReportBuilderPage = lazy(() => import('./pages/Reports/ReportBuilder'));
const ScenarioListPage = lazy(() => import('./pages/Scenarios/ScenarioList'));
const ScenarioDetailPage = lazy(() => import('./pages/Scenarios/ScenarioDetail'));
const ScenarioCreatePage = lazy(() => import('./pages/Scenarios/ScenarioCreate'));
const ScenarioEditPage = lazy(() => import('./pages/Scenarios/ScenarioEdit'));
const ScenarioExecutionPage = lazy(() => import('./pages/Scenarios/ScenarioExecution'));
const ExecutionsListPage = lazy(() => import('./pages/Scenarios/ExecutionsList'));
const TestSuiteListPage = lazy(() => import('./pages/TestSuites/TestSuiteList'));
const SuiteRunsPage = lazy(() => import('./pages/SuiteRuns/SuiteRunsPage'));
const SuiteRunDetailPage = lazy(() => import('./pages/SuiteRuns/SuiteRunDetail'));
// LLM Providers - Hidden for now
// const LLMProvidersPage = lazy(() => import('./pages/LLMProviders/LLMProvidersPage'));

// Admin Console Pages
const AdminLayout = lazy(() => import('./components/Layout/AdminLayout'));
const AdminDashboardPage = lazy(() => import('./pages/Admin/AdminDashboard'));
const AdminOrganizationsPage = lazy(() => import('./pages/Admin/OrganizationsPage'));
const AdminUsersPage = lazy(() => import('./pages/Admin/UsersPage'));
const AdminCategoriesPage = lazy(() => import('./pages/Admin/CategoriesPage'));
const GlobalConfigurationsPage = lazy(() => import('./pages/Admin/GlobalConfigurations'));

function App() {
  const dispatch = useDispatch<AppDispatch>();

  // Initialize auth on app load (validate token and restore user)
  useEffect(() => {
    dispatch(initializeAuth());
  }, [dispatch]);

  return (
    <BrowserRouter>
      <ToastProvider>
        <SkipLink />
        <ErrorBoundary onError={handleError}>
          <Suspense fallback={<PageLoader />}>
            <Routes>
            {/* Public Routes */}
            <Route path="/" element={<HomePage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />

            {/* Protected Routes - All wrapped in AppLayout (sidebar) */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <DashboardPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />

            <Route
              path="/validation"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <ValidationDashboardPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/validation/result"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <ValidationResultDetailPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/integrations/github"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <GitHubIntegrationPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/integrations/jira"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <JiraIntegrationPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/integrations/slack"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <SlackIntegrationPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/integrations"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <IntegrationsDashboardPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/knowledge-base"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <KnowledgeBasePage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/knowledge-base/search"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <KnowledgeBaseSearchPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/knowledge-base/new"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <KnowledgeBaseEditorPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/knowledge-base/:articleId"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <KnowledgeBaseArticlePage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/knowledge-base/:articleId/edit"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <KnowledgeBaseEditorPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/regressions"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <RegressionListPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/regressions/:scriptId/comparison"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <RegressionComparisonPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/regressions/:scriptId/baselines"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <BaselineManagementPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/analytics"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <AnalyticsPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/cicd"
              element={
                <ProtectedRoute allowedRoles={['org_admin']}>
                  <AppLayout>
                    <CICDDashboardPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/configurations"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <OrganizationConfigurationsPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/configurations/new"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <ConfigurationEditorPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/configurations/:id/edit"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <ConfigurationEditorPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/defects"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <DefectListPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/defects/:id"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <DefectDetailPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/edge-cases"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <EdgeCaseLibraryPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/edge-cases/analytics"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <EdgeCaseAnalyticsPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/edge-cases/new"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <EdgeCaseCreatePage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/edge-cases/:edgeCaseId/edit"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <EdgeCaseEditPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/edge-cases/:edgeCaseId"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <EdgeCaseDetailPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            {/* Redirect old pattern-groups URL to edge-cases with tab */}
            <Route
              path="/pattern-groups"
              element={<Navigate to="/edge-cases?tab=pattern-groups" replace />}
            />
            <Route
              path="/pattern-groups/:id"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <PatternGroupDetailPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/reports"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <ReportBuilderPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/scenarios"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <ScenarioListPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/scenarios/new"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <ScenarioCreatePage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/scenarios/:id/edit"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <ScenarioEditPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/scenarios/:id"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <ScenarioDetailPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/executions"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <ExecutionsListPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/scenarios/executions/:executionId"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <ScenarioExecutionPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/test-suites"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <TestSuiteListPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/suite-runs"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <SuiteRunsPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/suite-runs/:id"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <SuiteRunDetailPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            {/* Super Admin Console Routes */}
            <Route
              path="/admin"
              element={
                <ProtectedRoute allowedRoles={['super_admin']}>
                  <AdminLayout>
                    <AdminDashboardPage />
                  </AdminLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin/organizations"
              element={
                <ProtectedRoute allowedRoles={['super_admin']}>
                  <AdminLayout>
                    <AdminOrganizationsPage />
                  </AdminLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin/users"
              element={
                <ProtectedRoute allowedRoles={['super_admin']}>
                  <AdminLayout>
                    <AdminUsersPage />
                  </AdminLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin/categories"
              element={
                <ProtectedRoute allowedRoles={['super_admin', 'org_admin']}>
                  <AdminLayout>
                    <AdminCategoriesPage />
                  </AdminLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin/configurations"
              element={
                <ProtectedRoute allowedRoles={['super_admin']}>
                  <AdminLayout>
                    <GlobalConfigurationsPage />
                  </AdminLayout>
                </ProtectedRoute>
              }
            />
            {/* LLM Providers - Hidden for now */}
            {/* <Route
              path="/admin/llm-providers"
              element={
                <ProtectedRoute allowedRoles={['super_admin']}>
                  <AdminLayout>
                    <LLMProvidersPage />
                  </AdminLayout>
                </ProtectedRoute>
              }
            /> */}
            </Routes>
          </Suspense>
        </ErrorBoundary>
      </ToastProvider>
    </BrowserRouter>
  );
}

export default App;
