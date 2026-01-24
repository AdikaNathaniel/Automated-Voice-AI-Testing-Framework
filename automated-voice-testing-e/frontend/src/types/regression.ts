export interface RegressionSummary {
  totalRegressions: number;
  statusRegressions: number;
  metricRegressions: number;
}

export interface RegressionFinding {
  scriptId: string;
  category: string;
  detail: Record<string, unknown>;
  detectedAt?: string | null;
}

export interface RegressionListResponse {
  summary: RegressionSummary;
  items: RegressionFinding[];
}

export interface RegressionListParams {
  suiteId?: string;
  status?: string;
  skip?: number;
  limit?: number;
}

export interface RegressionMetricDetail {
  value: number | null;
  threshold: number | null;
  unit: string | null;
}

export interface RegressionSnapshot {
  status: string | null;
  metrics: Record<string, RegressionMetricDetail>;
  mediaUri: string | null;
}

export interface RegressionDifference {
  metric: string;
  baselineValue: number | null;
  currentValue: number | null;
  delta: number | null;
  deltaPercent: number | null;
}

export interface RegressionComparison {
  scriptId: string;
  baseline: RegressionSnapshot;
  current: RegressionSnapshot;
  differences: RegressionDifference[];
}

export type BaselineMetrics = Record<string, number | string | null>;

export interface BaselineHistoryEntry {
  version: number;
  status: string;
  metrics: BaselineMetrics;
  approvedAt: string | null;
  approvedBy: string | null;
  note: string | null;
}

export interface ValidationSummary {
  totalSteps: number;
  passedSteps: number;
  failedSteps: number;
  allPassed: boolean;
}

export interface StepDetail {
  stepOrder: number;
  validationPassed: boolean | null;
  userUtterance: string | null;
  aiResponse: string | null;
  validationDetails: Record<string, unknown> | null;
  confidenceScore: number | null;
}

export interface PendingBaselineSnapshot {
  status: string | null;
  metrics: BaselineMetrics;
  detectedAt: string | null;
  proposedBy: string | null;
  executionId: string | null;
  validationSummary: ValidationSummary | null;
  stepDetails: StepDetail[] | null;
}

export interface BaselineHistoryResponse {
  scriptId?: string;
  history: BaselineHistoryEntry[];
  pending?: PendingBaselineSnapshot | null;
}

export interface BaselineApprovalPayload {
  status: string;
  metrics: BaselineMetrics;
  note?: string | null;
}

export interface BaselineApprovalResult {
  scriptId: string;
  status: string;
  metrics: BaselineMetrics;
  version: number;
  approvedAt: string | null;
  approvedBy: string | null;
  note: string | null;
}
