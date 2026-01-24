import apiClient from './api';
import type {
  DashboardSnapshot,
  ExecutiveKpis,
  RealTimeExecutionSnapshot,
  ValidationAccuracySnapshot,
  LanguageCoverageEntry,
  DefectSummary,
  TestCoverageEntry,
  CicdStatus,
  DefectTrendPoint,
  DashboardFilters,
  EdgeCaseStatisticsSnapshot,
} from '../types/dashboard';

type ApiDashboardResponse = {
  kpis: {
    tests_executed: number;
    system_health_pct: number;
    issues_detected: number;
    avg_response_time_ms: number;
  };
  real_time_execution: {
    current_run_id: string | null;
    progress_pct: number;
    tests_passed: number;
    tests_failed: number;
    under_review: number;
    queued: number;
  };
  validation_accuracy: {
    overall_accuracy_pct: number;
    total_validations: number;
    human_reviews: number;
    agreements: number;
    disagreements: number;
    ai_overturned: number;
    time_saved_hours: number;
  };
  language_coverage?: Array<{
    language_code: string;
    test_cases: number;
    pass_rate_pct: number;
  }>;
  defects: {
    open: number;
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
  defects_trend?: Array<{
    date: string;
    open: number;
  }>;
  test_coverage?: Array<{
    area: string;
    coverage_pct: number;
    automated_pct: number;
  }>;
  cicd_status?: {
    pipelines?: Array<{
      id: string;
      name: string;
      status: string;
      last_run_at: string | null;
    }>;
    incidents?: number;
  };
  updated_at: string;
  edge_cases?: {
    total?: number;
    resolved?: number;
    categories?: Array<{
      category: string;
      count: number;
    }>;
  };
  scenarios?: {
    total: number;
  };
  test_suites?: {
    total: number;
  };
  suite_runs?: {
    total: number;
    completed: number;
    failed: number;
    running: number;
  };
  pass_rate_trend?: Array<{
    date: string;
    pass_rate_pct: number;
    tests_passed: number;
    tests_failed: number;
    total_tests: number;
  }>;
  validation_queue?: {
    pending_reviews: number;
  };
};

const toExecutiveKpis = (payload: ApiDashboardResponse['kpis']): ExecutiveKpis => ({
  testsExecuted: payload.tests_executed,
  systemHealthPct: payload.system_health_pct,
  issuesDetected: payload.issues_detected,
  avgResponseTimeMs: payload.avg_response_time_ms,
});

const toRealTimeExecution = (
  payload: ApiDashboardResponse['real_time_execution']
): RealTimeExecutionSnapshot => ({
  currentRunId: payload.current_run_id,
  progressPct: payload.progress_pct,
  testsPassed: payload.tests_passed,
  testsFailed: payload.tests_failed,
  underReview: payload.under_review,
  queued: payload.queued,
});

const toValidationAccuracy = (
  payload: ApiDashboardResponse['validation_accuracy']
): ValidationAccuracySnapshot => ({
  overallAccuracyPct: payload.overall_accuracy_pct,
  totalValidations: payload.total_validations,
  humanReviews: payload.human_reviews,
  agreements: payload.agreements,
  disagreements: payload.disagreements,
  aiOverturned: payload.ai_overturned,
  timeSavedHours: payload.time_saved_hours,
});

const toLanguageCoverage = (
  entries: NonNullable<ApiDashboardResponse['language_coverage']>
): LanguageCoverageEntry[] =>
  entries.map((entry) => ({
    languageCode: entry.language_code,
    testCases: entry.test_cases,
    passRatePct: entry.pass_rate_pct,
  }));

const toDefectSummary = (payload: ApiDashboardResponse['defects']): DefectSummary => ({
  open: payload.open,
  critical: payload.critical,
  high: payload.high,
  medium: payload.medium,
  low: payload.low,
});

const toDefectTrend = (
  entries: NonNullable<ApiDashboardResponse['defects_trend']>
): DefectTrendPoint[] =>
  entries.map((entry) => ({
    date: entry.date,
    open: entry.open,
  }));

const toTestCoverage = (
  entries: NonNullable<ApiDashboardResponse['test_coverage']>
): TestCoverageEntry[] =>
  entries.map((entry) => ({
    area: entry.area,
    coveragePct: entry.coverage_pct,
    automatedPct: entry.automated_pct,
  }));

const toCicdStatus = (payload?: ApiDashboardResponse['cicd_status']): CicdStatus => ({
  pipelines:
    payload?.pipelines?.map((pipeline) => ({
      id: pipeline.id,
      name: pipeline.name,
      status: pipeline.status,
      lastRunAt: pipeline.last_run_at,
    })) ?? [],
  incidents: payload?.incidents ?? 0,
});

const toEdgeCaseStatistics = (
  payload?: ApiDashboardResponse['edge_cases']
): EdgeCaseStatisticsSnapshot => ({
  total: payload?.total ?? 0,
  resolved: payload?.resolved ?? 0,
  categories:
    payload?.categories?.map((entry) => ({
      category: entry.category,
      count: entry.count,
    })) ?? [],
});

const toDashboardParams = (filters?: DashboardFilters) => ({
  // Backend only supports time_range parameter
  // language and testSuite filters are applied client-side
  time_range: filters?.timeRange,
});

export const getDashboardSnapshot = async (
  filters?: DashboardFilters
): Promise<DashboardSnapshot> => {
  try {
    console.log('[Dashboard Service] Fetching dashboard snapshot with filters:', filters);
    const response = await apiClient.get<ApiDashboardResponse>('/reports/dashboard', {
      params: toDashboardParams(filters),
    });
    console.log('[Dashboard Service] Received response:', response.data);
    const data = response.data;

    const result: DashboardSnapshot = {
      kpis: toExecutiveKpis(data.kpis),
      realTimeExecution: toRealTimeExecution(data.real_time_execution),
      validationAccuracy: toValidationAccuracy(data.validation_accuracy),
      languageCoverage: data.language_coverage ? toLanguageCoverage(data.language_coverage) : [],
      defects: toDefectSummary(data.defects),
      defectTrend: data.defects_trend ? toDefectTrend(data.defects_trend) : [],
      testCoverage: data.test_coverage ? toTestCoverage(data.test_coverage) : [],
      cicdStatus: toCicdStatus(data.cicd_status),
      edgeCases: toEdgeCaseStatistics(data.edge_cases),
      passRateTrend: data.pass_rate_trend?.map(p => ({
        date: p.date,
        pass_rate_pct: p.pass_rate_pct,
        tests_passed: p.tests_passed,
        tests_failed: p.tests_failed,
        total_tests: p.total_tests,
      })) ?? [],
      scenarios: data.scenarios ? { total: data.scenarios.total } : undefined,
      testSuites: data.test_suites ? { total: data.test_suites.total } : undefined,
      suiteRuns: data.suite_runs ? {
        total: data.suite_runs.total,
        completed: data.suite_runs.completed,
        failed: data.suite_runs.failed,
        running: data.suite_runs.running,
      } : undefined,
      validationQueue: data.validation_queue ? {
        pendingReviews: data.validation_queue.pending_reviews,
      } : { pendingReviews: 0 },
      updatedAt: data.updated_at,
    };
    console.log('[Dashboard Service] Transformed data:', result);
    return result;
  } catch (error) {
    console.error('[Dashboard Service] Error fetching dashboard snapshot:', error);
    throw error;
  }
};

export interface DashboardSettings {
  responseTimeSlaMs: number;
}

type ApiDashboardSettingsResponse = {
  response_time_sla_ms: number;
};

export const getDashboardSettings = async (): Promise<DashboardSettings> => {
  try {
    const response = await apiClient.get<ApiDashboardSettingsResponse>('/reports/dashboard/settings');
    return {
      responseTimeSlaMs: response.data.response_time_sla_ms,
    };
  } catch (error) {
    console.error('[Dashboard Service] Error fetching dashboard settings:', error);
    // Return default on error
    return { responseTimeSlaMs: 2000 };
  }
};

export default {
  getDashboardSnapshot,
  getDashboardSettings,
};
