/**
 * Defect service helpers.
 *
 * Provides access to the defect listing API with optional filtering.
 */

import apiClient from './api';
import type {
  DefectListParams,
  DefectListResponse,
  DefectRecord,
  DefectDetail,
} from '../types/defect';

type ApiDefectRecord = {
  id: string;
  script_id: string | null;
  execution_id: string | null;
  suite_run_id: string | null;
  severity: string;
  category: string;
  title: string;
  description: string | null;
  language_code: string | null;
  detected_at: string;
  status: string;
  assigned_to: string | null;
  resolved_at: string | null;
  created_at: string;
  jira_issue_key: string | null;
  jira_issue_url: string | null;
  jira_status: string | null;
  related_executions?: Array<{
    id: string;
    status: string;
    suite_run_id: string | null;
    executed_at: string | null;
  }>;
  comments?: Array<{
    id: string;
    author: string;
    message: string;
    created_at: string;
  }>;
};

type ApiDefectListResponse = {
  total: number;
  items: ApiDefectRecord[];
};

const toDefectRecord = (payload: ApiDefectRecord): DefectRecord => ({
  id: payload.id,
  title: payload.title,
  severity: payload.severity,
  category: payload.category,
  status: payload.status,
  scriptId: payload.script_id,
  executionId: payload.execution_id,
  suiteRunId: payload.suite_run_id,
  languageCode: payload.language_code,
  detectedAt: payload.detected_at,
  resolvedAt: payload.resolved_at,
  description: payload.description,
  assignedTo: payload.assigned_to,
  createdAt: payload.created_at,
  jiraIssueKey: payload.jira_issue_key,
  jiraIssueUrl: payload.jira_issue_url,
  jiraStatus: payload.jira_status,
});

const toDefectDetail = (payload: ApiDefectRecord): DefectDetail => ({
  ...toDefectRecord(payload),
  relatedExecutions: (payload.related_executions ?? []).map((execution) => ({
    id: execution.id,
    status: execution.status,
    suiteRunId: execution.suite_run_id,
    executedAt: execution.executed_at,
  })),
  comments: (payload.comments ?? []).map((comment) => ({
    id: comment.id,
    author: comment.author,
    message: comment.message,
    createdAt: comment.created_at,
  })),
});

export class DefectServiceError extends Error {
  constructor(message: string, public readonly cause?: unknown) {
    super(message);
    this.name = 'DefectServiceError';
  }
}

export const getDefects = async (
  params: DefectListParams = {}
): Promise<DefectListResponse> => {
  try {
    const page = params.page ?? 1;
    const pageSize = params.pageSize ?? 25;

    const response = await apiClient.get<ApiDefectListResponse>('/defects', {
      params: {
        status: params.status ?? null,
        severity: params.severity ?? null,
        category: params.category ?? null,
        skip: (page - 1) * pageSize,
        limit: pageSize,
      },
    });

    return {
      total: response.data.total,
      items: response.data.items.map(toDefectRecord),
    };
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Failed to fetch defects';
    throw new DefectServiceError(message, error);
  }
};

export const getDefectDetail = async (defectId: string): Promise<DefectDetail> => {
  try {
    const response = await apiClient.get<ApiDefectRecord>(`/defects/${defectId}`);
    return toDefectDetail(response.data);
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Failed to fetch defect details';
    throw new DefectServiceError(message, error);
  }
};

export const createJiraTicket = async (defectId: string): Promise<DefectRecord> => {
  try {
    const response = await apiClient.post<ApiDefectRecord>(`/defects/${defectId}/jira`);
    return toDefectRecord(response.data);
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Failed to create Jira ticket';
    throw new DefectServiceError(message, error);
  }
};

export default {
  getDefects,
  getDefectDetail,
  createJiraTicket,
};
