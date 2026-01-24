/**
 * Regression service helpers.
 */

import apiClient from './api';
import type {
  RegressionListParams,
  RegressionListResponse,
  RegressionSummary,
  RegressionFinding,
  RegressionComparison,
  RegressionDifference,
  RegressionMetricDetail,
  RegressionSnapshot,
  BaselineHistoryResponse,
  BaselineHistoryEntry,
  PendingBaselineSnapshot,
  BaselineApprovalPayload,
  BaselineApprovalResult,
  BaselineMetrics,
} from '../types/regression';

type ApiRegressionSummary = {
  total_regressions?: number;
  status_regressions?: number;
  metric_regressions?: number;
};

type ApiRegressionFinding = {
  script_id: string;
  category: string;
  detail?: Record<string, unknown>;
  regression_detected_at?: string | null;
};

type ApiRegressionListResponse = {
  summary?: ApiRegressionSummary;
  items?: ApiRegressionFinding[];
};

type ApiRegressionMetricDetail = {
  value?: number | null;
  threshold?: number | null;
  unit?: string | null;
};

type ApiRegressionSnapshot = {
  status?: string | null;
  metrics?: Record<string, ApiRegressionMetricDetail | undefined>;
  media_uri?: string | null;
};

type ApiRegressionDifference = {
  metric?: string;
  baseline_value?: number | null;
  current_value?: number | null;
  delta?: number | null;
  delta_pct?: number | null;
};

type ApiRegressionComparisonResponse = {
  script_id?: string;
  baseline?: ApiRegressionSnapshot;
  current?: ApiRegressionSnapshot;
  differences?: ApiRegressionDifference[];
};

type ApiBaselineHistoryEntry = {
  version?: number;
  status?: string;
  metrics?: Record<string, unknown> | null;
  approved_at?: string | null;
  approved_by?: string | null;
  note?: string | null;
};

type ApiValidationSummary = {
  total_steps?: number;
  passed_steps?: number;
  failed_steps?: number;
  all_passed?: boolean;
};

type ApiStepDetail = {
  step_order?: number;
  validation_passed?: boolean | null;
  user_utterance?: string | null;
  ai_response?: string | null;
  validation_details?: Record<string, unknown> | null;
  confidence_score?: number | null;
};

type ApiPendingBaseline = {
  status?: string | null;
  metrics?: Record<string, unknown> | null;
  detected_at?: string | null;
  proposed_by?: string | null;
  execution_id?: string | null;
  validation_summary?: ApiValidationSummary | null;
  step_details?: ApiStepDetail[] | null;
};

type ApiBaselineHistoryResponse = {
  script_id?: string;
  history?: ApiBaselineHistoryEntry[];
  pending?: ApiPendingBaseline | null;
};

type ApiBaselineApprovalResponse = {
  script_id?: string;
  status?: string;
  metrics?: Record<string, unknown> | null;
  version?: number;
  approved_at?: string | null;
  approved_by?: string | null;
  note?: string | null;
};

const mapSummary = (summary: ApiRegressionSummary | undefined): RegressionSummary => ({
  totalRegressions: summary?.total_regressions ?? 0,
  statusRegressions: summary?.status_regressions ?? 0,
  metricRegressions: summary?.metric_regressions ?? 0,
});

const mapFinding = (finding: ApiRegressionFinding): RegressionFinding => ({
  scriptId: finding.script_id,
  category: finding.category,
  detail: finding.detail ?? {},
  detectedAt: finding.regression_detected_at ?? null,
});

const mapMetricDetail = (detail: ApiRegressionMetricDetail | undefined): RegressionMetricDetail => ({
  value: typeof detail?.value === 'number' ? detail.value : null,
  threshold: typeof detail?.threshold === 'number' ? detail.threshold : null,
  unit: typeof detail?.unit === 'string' && detail.unit.trim() ? detail.unit : null,
});

const mapSnapshot = (snapshot: ApiRegressionSnapshot | undefined): RegressionSnapshot => {
  const metrics: Record<string, RegressionMetricDetail> = {};

  if (snapshot?.metrics) {
    for (const [metric, value] of Object.entries(snapshot.metrics)) {
      metrics[metric] = mapMetricDetail(value);
    }
  }

  return {
    status: snapshot?.status ?? null,
    metrics,
    mediaUri: snapshot?.media_uri ?? null,
  };
};

const mapDifference = (difference: ApiRegressionDifference): RegressionDifference => ({
  metric: difference.metric ?? 'unknown',
  baselineValue: typeof difference.baseline_value === 'number' ? difference.baseline_value : null,
  currentValue: typeof difference.current_value === 'number' ? difference.current_value : null,
  delta: typeof difference.delta === 'number' ? difference.delta : null,
  deltaPercent: typeof difference.delta_pct === 'number' ? difference.delta_pct : null,
});

const mapBaselineMetrics = (metrics: Record<string, unknown> | null | undefined): BaselineMetrics => {
  const result: BaselineMetrics = {};
  if (!metrics) {
    return result;
  }

  for (const [key, value] of Object.entries(metrics)) {
    if (typeof value === 'number' || typeof value === 'string' || value === null) {
      result[key] = value;
    } else {
      result[key] = null;
    }
  }

  return result;
};

const mapBaselineHistoryEntry = (entry: ApiBaselineHistoryEntry): BaselineHistoryEntry => ({
  version: typeof entry.version === 'number' ? entry.version : 0,
  status: entry.status ?? 'unknown',
  metrics: mapBaselineMetrics(entry.metrics),
  approvedAt: entry.approved_at ?? null,
  approvedBy: entry.approved_by ?? null,
  note: entry.note ?? null,
});

const mapValidationSummary = (summary: ApiValidationSummary | null | undefined) => {
  if (!summary) {
    return null;
  }
  return {
    totalSteps: summary.total_steps ?? 0,
    passedSteps: summary.passed_steps ?? 0,
    failedSteps: summary.failed_steps ?? 0,
    allPassed: summary.all_passed ?? false,
  };
};

const mapStepDetails = (steps: ApiStepDetail[] | null | undefined) => {
  if (!steps || !Array.isArray(steps)) {
    return null;
  }
  return steps.map((step) => ({
    stepOrder: step.step_order ?? 0,
    validationPassed: step.validation_passed ?? null,
    userUtterance: step.user_utterance ?? null,
    aiResponse: step.ai_response ?? null,
    validationDetails: step.validation_details ?? null,
    confidenceScore: step.confidence_score ?? null,
  }));
};

const mapPendingBaseline = (pending: ApiPendingBaseline | null | undefined): PendingBaselineSnapshot | null => {
  if (!pending) {
    return null;
  }

  return {
    status: pending.status ?? null,
    metrics: mapBaselineMetrics(pending.metrics),
    detectedAt: pending.detected_at ?? null,
    proposedBy: pending.proposed_by ?? null,
    executionId: pending.execution_id ?? null,
    validationSummary: mapValidationSummary(pending.validation_summary),
    stepDetails: mapStepDetails(pending.step_details),
  };
};

const mapBaselineApproval = (
  payload: ApiBaselineApprovalResponse,
  fallbackScriptId: string
): BaselineApprovalResult => ({
  scriptId: payload.script_id ?? fallbackScriptId,
  status: payload.status ?? 'unknown',
  metrics: mapBaselineMetrics(payload.metrics),
  version: typeof payload.version === 'number' ? payload.version : 0,
  approvedAt: payload.approved_at ?? null,
  approvedBy: payload.approved_by ?? null,
  note: payload.note ?? null,
});

export const getRegressions = async (
  params: RegressionListParams = {}
): Promise<RegressionListResponse> => {
  const response = await apiClient.get<ApiRegressionListResponse>('/regressions', {
    params: {
      status: params.status ?? null,
      suite_id: params.suiteId ?? null,
      skip: params.skip ?? 0,
      limit: params.limit ?? 50,
    },
  });

  const data = response.data ?? {};
  return {
    summary: mapSummary(data.summary),
    items: (data.items ?? []).map(mapFinding),
  };
};

export const getRegressionComparison = async (scriptId: string): Promise<RegressionComparison> => {
  const response = await apiClient.get<ApiRegressionComparisonResponse>(
    `/regressions/${scriptId}/comparison`
  );

  const data = response.data ?? {};

  return {
    scriptId: data.script_id ?? scriptId,
    baseline: mapSnapshot(data.baseline),
    current: mapSnapshot(data.current),
    differences: (data.differences ?? []).map(mapDifference),
  };
};

export const getBaselineHistory = async (scriptId: string): Promise<BaselineHistoryResponse> => {
  const response = await apiClient.get<ApiBaselineHistoryResponse>(`/regressions/${scriptId}/baselines`);
  const data = response.data ?? {};

  return {
    scriptId: data.script_id ?? scriptId,
    history: (data.history ?? []).map(mapBaselineHistoryEntry),
    pending: mapPendingBaseline(data.pending),
  };
};

export const approveBaseline = async (
  scriptId: string,
  payload: BaselineApprovalPayload
): Promise<BaselineApprovalResult> => {
  const response = await apiClient.post<ApiBaselineApprovalResponse>(
    `/regressions/${scriptId}/baseline`,
    payload
  );

  return mapBaselineApproval(response.data ?? {}, scriptId);
};

// ============================================================================
// Persistent Regression Tracking
// ============================================================================

export interface RegressionRecord {
  id: string;
  tenantId: string | null;
  scriptId: string;
  scriptName: string | null;
  category: string;
  severity: string;
  status: string;
  baselineVersion: number | null;
  detectionDate: string;
  resolutionDate: string | null;
  lastSeenDate: string;
  occurrenceCount: number;
  details: Record<string, unknown>;
  linkedDefectId: string | null;
  resolvedBy: string | null;
  resolutionNote: string | null;
  createdAt: string;
  updatedAt: string;
}

export interface RegressionRecordListResponse {
  total: number;
  active: number;
  resolved: number;
  items: RegressionRecord[];
}

export interface RegressionRecordListParams {
  status?: string;
  category?: string;
  scriptId?: string;
  skip?: number;
  limit?: number;
}

export interface ResolveRegressionPayload {
  note?: string;
}

export interface CreateDefectFromRegressionPayload {
  severity?: string;
  additional_notes?: string;
}

export interface CreateDefectFromRegressionResponse {
  defect_id: string;
  regression_id: string;
  message: string;
}

export const getRegressionRecords = async (
  params: RegressionRecordListParams = {}
): Promise<RegressionRecordListResponse> => {
  const response = await apiClient.get<RegressionRecordListResponse>('/regressions/records', {
    params: {
      status: params.status ?? null,
      category: params.category ?? null,
      script_id: params.scriptId ?? null,
      skip: params.skip ?? 0,
      limit: params.limit ?? 50,
    },
  });

  return response.data ?? { total: 0, active: 0, resolved: 0, items: [] };
};

export const resolveRegression = async (
  regressionId: string,
  payload: ResolveRegressionPayload = {}
): Promise<RegressionRecord> => {
  const response = await apiClient.post<RegressionRecord>(
    `/regressions/records/${regressionId}/resolve`,
    payload
  );

  return response.data;
};

export const createDefectFromRegression = async (
  regressionId: string,
  payload: CreateDefectFromRegressionPayload = {}
): Promise<CreateDefectFromRegressionResponse> => {
  const response = await apiClient.post<CreateDefectFromRegressionResponse>(
    `/regressions/records/${regressionId}/create-defect`,
    payload
  );

  return response.data;
};

export default {
  getRegressions,
  getRegressionComparison,
  getBaselineHistory,
  approveBaseline,
  getRegressionRecords,
  resolveRegression,
  createDefectFromRegression,
};
