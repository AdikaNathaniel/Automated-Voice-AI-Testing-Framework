import apiClient from './api';
import type {
  RealTimeMetrics,
  RealTimeRun,
  RealTimeQueueDepth,
  RealTimeThroughput,
  RealTimeRunCounts,
  RealTimeIssueSummary,
  DashboardFilters,
} from '../types/dashboard';

type ApiRealTimeMetrics = {
  current_runs: Array<{
    id: string;
    suite_id: string | null;
    suite_name: string | null;
    status: string;
    progress_pct: number;
    total_tests: number;
    passed_tests: number;
    failed_tests: number;
    skipped_tests: number;
    started_at: string | null;
    completed_at: string | null;
  }>;
  queue_depth: {
    total: number;
    queued: number;
    processing: number;
    completed: number;
    failed: number;
    average_priority: number;
    oldest_queued_seconds: number | null;
  };
  throughput: {
    tests_per_minute: number;
    sample_size: number;
    window_minutes: number;
    last_updated: string;
  };
  run_counts: {
    pending: number;
    running: number;
    completed: number;
    failed: number;
    cancelled: number;
  };
  issue_summary: {
    open_defects: number;
    critical_defects: number;
    edge_cases_active: number;
    edge_cases_new: number;
  };
};

const toRun = (payload: ApiRealTimeMetrics['current_runs'][number]): RealTimeRun => ({
  id: payload.id,
  suiteId: payload.suite_id,
  suiteName: payload.suite_name,
  status: payload.status,
  progressPct: payload.progress_pct,
  totalTests: payload.total_tests,
  passedTests: payload.passed_tests,
  failedTests: payload.failed_tests,
  skippedTests: payload.skipped_tests,
  startedAt: payload.started_at,
  completedAt: payload.completed_at,
});

const toQueueDepth = (
  payload: ApiRealTimeMetrics['queue_depth']
): RealTimeQueueDepth => ({
  total: payload.total,
  queued: payload.queued,
  processing: payload.processing,
  completed: payload.completed,
  failed: payload.failed,
  averagePriority: payload.average_priority,
  oldestQueuedSeconds: payload.oldest_queued_seconds,
});

const toThroughput = (
  payload: ApiRealTimeMetrics['throughput']
): RealTimeThroughput => ({
  testsPerMinute: payload.tests_per_minute,
  sampleSize: payload.sample_size,
  windowMinutes: payload.window_minutes,
  lastUpdated: payload.last_updated,
});

const toRunCounts = (payload: ApiRealTimeMetrics['run_counts']): RealTimeRunCounts => ({
  pending: payload.pending,
  running: payload.running,
  completed: payload.completed,
  failed: payload.failed,
  cancelled: payload.cancelled,
});

const toIssueSummary = (
  payload: ApiRealTimeMetrics['issue_summary']
): RealTimeIssueSummary => ({
  openDefects: payload.open_defects,
  criticalDefects: payload.critical_defects,
  edgeCasesActive: payload.edge_cases_active,
  edgeCasesNew: payload.edge_cases_new,
});

const toRealTimeParams = (filters?: DashboardFilters) => ({
  // Backend only supports time_range parameter
  // language and testSuite filters are applied client-side
  time_range: filters?.timeRange,
});

export const getRealTimeMetrics = async (
  filters?: DashboardFilters
): Promise<RealTimeMetrics> => {
  try {
    console.log('[RealTime Metrics Service] Fetching real-time metrics with filters:', filters);
    const response = await apiClient.get<ApiRealTimeMetrics>('/metrics/real-time', {
      params: toRealTimeParams(filters),
    });
    console.log('[RealTime Metrics Service] Received response:', response.data);
    const data = response.data;

    const result = {
      currentRuns: data.current_runs.map(toRun),
      queueDepth: toQueueDepth(data.queue_depth),
      throughput: toThroughput(data.throughput),
      runCounts: toRunCounts(data.run_counts),
      issueSummary: toIssueSummary(data.issue_summary),
    };
    console.log('[RealTime Metrics Service] Transformed data:', result);
    return result;
  } catch (error) {
    console.error('[RealTime Metrics Service] Error fetching real-time metrics:', error);
    throw error;
  }
};

export default {
  getRealTimeMetrics,
};
