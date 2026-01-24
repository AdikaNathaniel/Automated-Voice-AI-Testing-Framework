/**
 * Suite run service helpers.
 *
 * Provides access to suite run listing with optional language filters.
 */

import apiClient from './api';
import type {
  SuiteRunListParams,
  SuiteRunListResponse,
  SuiteRunDetail,
  SuiteRunExecution,
} from '../types/suiteRun';

export const getSuiteRuns = async (
  params: SuiteRunListParams = {}
): Promise<SuiteRunListResponse> => {
  const response = await apiClient.get('/suite-runs', {
    params: {
      language_code: params.languageCode ?? null,
      limit: params.limit ?? null,
    },
  });

  const data = response.data;

  // Map the response to include both runs and items formats
  const items = (data.runs || data || []).map((run: Record<string, unknown>) => ({
    id: run.id,
    suiteName: run.suite_name ?? run.suiteName ?? null,
    testSuiteId: run.suite_id ?? run.testSuiteId ?? '',
    status: run.status ?? 'pending',
    startedAt: run.started_at ?? run.startedAt ?? null,
    completedAt: run.completed_at ?? run.completedAt ?? null,
    createdAt: run.created_at ?? run.createdAt ?? null,
    totalTests: run.total_tests ?? run.totalTests ?? 0,
    passedTests: run.passed_tests ?? run.passedTests ?? 0,
    failedTests: run.failed_tests ?? run.failedTests ?? 0,
    skippedTests: run.skipped_tests ?? run.skippedTests ?? 0,
    languageCode: run.language_code ?? run.languageCode ?? null,
    is_categorical: run.is_categorical ?? false,
    category_name: run.category_name ?? null,
  }));

  return {
    total: data.total ?? items.length,
    runs: items,  // Use the properly mapped items as runs
    items,
  };
};

export const getSuiteRunDetail = async (runId: string): Promise<SuiteRunDetail> => {
  const response = await apiClient.get(`/suite-runs/${runId}`);
  const data = response.data;

  return {
    id: data.id,
    testSuiteId: data.suite_id ?? '',
    status: data.status,
    startedAt: data.started_at ?? null,
    completedAt: data.completed_at ?? null,
    createdAt: data.created_at ?? '',
    totalTests: data.total_tests ?? 0,
    passedTests: data.passed_tests ?? 0,
    failedTests: data.failed_tests ?? 0,
    skippedTests: data.skipped_tests ?? 0,
    languageCode: data.trigger_metadata?.language_code ?? null,
    triggerType: data.trigger_type ?? null,
  };
};

export const getSuiteRunExecutions = async (
  runId: string
): Promise<SuiteRunExecution[]> => {
  const response = await apiClient.get(`/suite-runs/${runId}/executions`);
  const executions = response.data as Array<Record<string, unknown>>;

  return executions.map((execution) => ({
    id: execution.id,
    scriptId: execution.script_id,
    scriptName: execution.script_name ?? null,
    languageCode: execution.language_code ?? null,
    status: execution.status,
    responseSummary:
      execution.response_summary ??
      execution.result?.response_summary ??
      execution.result?.response_entities?.transcript ??
      null,
    responseTimeSeconds:
      execution.response_time_seconds ?? execution.execution_time ?? null,
    confidenceScore:
      execution.confidence_score ??
      execution.result?.response_entities?.confidence ??
      null,
    validationResultId: execution.validation_result_id ?? null,
    validationReviewStatus: execution.validation_review_status ?? null,
    validationDetails: execution.validation_details ?? null,
    pendingValidationQueueId: execution.pending_validation_queue_id ?? null,
    latestHumanValidationId: execution.latest_human_validation_id ?? null,
    inputAudioUrl: execution.input_audio_url ?? null,
    responseAudioUrl: execution.response_audio_url ?? null,
    stepExecutions: execution.step_executions ?? null,
    totalSteps: execution.total_steps ?? null,
    completedSteps: execution.completed_steps ?? null,
  }));
};

/**
 * Execute a single script/scenario
 */
export const executeScript = async (
  scriptId: string,
  suiteId: string,
  languages?: string[]
): Promise<SuiteRunDetail> => {
  const response = await apiClient.post('/suite-runs/', {
    suite_id: suiteId,
    script_ids: [scriptId],
    languages: languages || null,
    trigger_type: 'manual',
  });

  const data = response.data;

  return {
    id: data.id,
    testSuiteId: data.suite_id ?? '',
    status: data.status,
    startedAt: data.started_at ?? null,
    completedAt: data.completed_at ?? null,
    createdAt: data.created_at ?? '',
    totalTests: data.total_tests ?? 0,
    passedTests: data.passed_tests ?? 0,
    failedTests: data.failed_tests ?? 0,
    skippedTests: data.skipped_tests ?? 0,
    languageCode: data.trigger_metadata?.language_code ?? null,
    triggerType: data.trigger_type ?? null,
  };
};

/**
 * Get executions for a specific script/scenario
 */
export const getScriptExecutions = async (
  scriptId: string,
  limit: number = 10,
  statusFilter?: string
): Promise<SuiteRunExecution[]> => {
  try {
    const params: Record<string, unknown> = { limit };
    if (statusFilter) {
      params.status_filter = statusFilter;
    }

    const response = await apiClient.get(`/scenarios/${scriptId}/executions`, {
      params,
    });

    const data = response.data;

    if (!Array.isArray(data)) {
      console.error('Expected array response from executions endpoint');
      return [];
    }

    return data.map((execution: unknown) => ({
      id: execution.id,
      suiteRunId: execution.suite_run_id,
      scriptId: execution.script_id,
      languageCode: execution.language_code,
      status: execution.status,
      createdAt: execution.created_at,
      startedAt: execution.started_at,
      completedAt: execution.completed_at,
      errorMessage: execution.error_message,
      processingTime: execution.processing_time,
      audioDuration: execution.audio_duration,
    }));
  } catch (error: unknown) {
    console.error('Failed to fetch script executions:', error);
    return [];
  }
};

export default {
  getSuiteRuns,
  getSuiteRunDetail,
  getSuiteRunExecutions,
  executeScript,
  getScriptExecutions,
};
