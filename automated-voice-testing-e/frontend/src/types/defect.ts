/**
 * Defect type definitions for frontend consumption.
 */

export interface DefectRecord {
  id: string;
  title: string;
  severity: string;
  category: string;
  status: string;
  scriptId?: string | null;
  executionId?: string | null;
  suiteRunId?: string | null;
  languageCode?: string | null;
  detectedAt: string;
  resolvedAt?: string | null;
  description?: string | null;
  assignedTo?: string | null;
  createdAt?: string;
  jiraIssueKey?: string | null;
  jiraIssueUrl?: string | null;
  jiraStatus?: string | null;
}

export interface DefectListParams {
  status?: string | null;
  severity?: string | null;
  category?: string | null;
  scriptId?: string | null;
  executionId?: string | null;
  page?: number;
  pageSize?: number;
}

export interface DefectListResponse {
  total: number;
  items: DefectRecord[];
}

export interface DefectRelatedExecution {
  id: string;
  status: string;
  suiteRunId?: string | null;
  executedAt?: string | null;
}

export interface DefectComment {
  id: string;
  author: string;
  message: string;
  createdAt: string;
}

export interface DefectDetail extends DefectRecord {
  relatedExecutions: DefectRelatedExecution[];
  comments: DefectComment[];
}
