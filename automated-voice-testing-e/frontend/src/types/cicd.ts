/**
 * CI/CD run types.
 */

export type CICDRunStatus = 'pending' | 'running' | 'success' | 'failed';

export interface CICDRunRecord {
  id: string;
  pipelineName: string;
  status: CICDRunStatus;
  branch: string;
  commitSha: string;
  commitUrl: string;
  triggeredBy: string;
  startedAt: string;
  completedAt?: string | null;
  totalTests: number;
  passedTests: number;
  failedTests: number;
}

export interface CICDRunListResponse {
  runs: CICDRunRecord[];
}

export interface CICDRunListParams {
  status?: CICDRunStatus | null;
}
