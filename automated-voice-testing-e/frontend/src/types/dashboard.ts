export type ExecutiveKpis = {
  testsExecuted: number;
  systemHealthPct: number;
  issuesDetected: number;
  avgResponseTimeMs: number;
};

export type RealTimeExecutionSnapshot = {
  currentRunId: string | null;
  progressPct: number;
  testsPassed: number;
  testsFailed: number;
  underReview: number;
  queued: number;
};

export type ValidationAccuracySnapshot = {
  overallAccuracyPct: number;
  totalValidations: number;
  humanReviews: number;
  agreements: number;
  disagreements: number;
  aiOverturned: number;
  timeSavedHours: number;
};

export type LanguageCoverageEntry = {
  languageCode: string;
  testCases: number;
  passRatePct: number;
};

export type DefectSummary = {
  open: number;
  critical: number;
  high: number;
  medium: number;
  low: number;
};

export type DefectTrendPoint = {
  date: string;
  open: number;
};

export type TestCoverageEntry = {
  area: string;
  coveragePct: number;
  automatedPct: number;
};

export type PipelineStatus = {
  id: string;
  name: string;
  status: 'success' | 'failed' | 'running' | 'cancelled' | string;
  lastRunAt: string | null;
};

export type CicdStatus = {
  pipelines: PipelineStatus[];
  incidents: number;
};

export type EdgeCaseCategoryBreakdown = {
  category: string;
  count: number;
};

export type EdgeCaseStatisticsSnapshot = {
  total: number;
  resolved: number;
  categories: EdgeCaseCategoryBreakdown[];
};

export type ScenarioStats = {
  total: number;
};

export type TestSuiteStats = {
  total: number;
};

export type SuiteRunStats = {
  total: number;
  completed: number;
  failed: number;
  running: number;
};

export type ValidationQueueStats = {
  pendingReviews: number;
};

export type PassRateTrendPoint = {
  date: string;
  pass_rate_pct: number;
  tests_passed: number;
  tests_failed: number;
  total_tests: number;
};

export type DashboardSnapshot = {
  kpis: ExecutiveKpis;
  realTimeExecution: RealTimeExecutionSnapshot;
  validationAccuracy: ValidationAccuracySnapshot;
  validationQueue?: ValidationQueueStats;
  languageCoverage: LanguageCoverageEntry[];
  defects: DefectSummary;
  defectTrend: DefectTrendPoint[];
  testCoverage: TestCoverageEntry[];
  cicdStatus: CicdStatus;
  edgeCases: EdgeCaseStatisticsSnapshot;
  passRateTrend: PassRateTrendPoint[];
  scenarios?: ScenarioStats;
  testSuites?: TestSuiteStats;
  suiteRuns?: SuiteRunStats;
  updatedAt: string;
};

export type DashboardTestCoverage = TestCoverageEntry[];

export type RealTimeQueueDepth = {
  total: number;
  queued: number;
  processing: number;
  completed: number;
  failed: number;
  averagePriority: number;
  oldestQueuedSeconds: number | null;
};

export type RealTimeRun = {
  id: string;
  suiteId: string | null;
  suiteName: string | null;
  status: string;
  progressPct: number;
  totalTests: number;
  passedTests: number;
  failedTests: number;
  skippedTests: number;
  startedAt: string | null;
  completedAt: string | null;
};

export type RealTimeThroughput = {
  testsPerMinute: number;
  sampleSize: number;
  windowMinutes: number;
  lastUpdated: string;
};

export type RealTimeRunCounts = {
  pending: number;
  running: number;
  completed: number;
  failed: number;
  cancelled: number;
};

export type RealTimeIssueSummary = {
  openDefects: number;
  criticalDefects: number;
  edgeCasesActive: number;
  edgeCasesNew: number;
};

export type RealTimeMetrics = {
  currentRuns: RealTimeRun[];
  queueDepth: RealTimeQueueDepth;
  throughput: RealTimeThroughput;
  runCounts: RealTimeRunCounts;
  issueSummary: RealTimeIssueSummary;
};

export type DashboardFilters = {
  timeRange: '1h' | '24h' | '7d' | '30d';
  language: string | 'all';
  testSuite: string | 'all';
};
