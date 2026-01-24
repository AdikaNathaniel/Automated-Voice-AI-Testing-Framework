/**
 * Test Suite Service
 *
 * Provides API calls for test suite management including:
 * - CRUD operations for test suites
 * - Scenario management within suites
 * - Suite execution
 */

import apiClient from './api';

// =============================================================================
// Interfaces
// =============================================================================

export interface LanguageConfig {
  mode: 'primary' | 'specific' | 'all';
  languages?: string[];
  fallback_behavior: 'smart' | 'skip' | 'fail';
}

export interface SuiteScenarioInfo {
  scenario_id: string;
  name: string;
  description?: string;
  version?: string;
  is_active: boolean;
  order: number;
  languages?: string[];
}

export interface TestSuite {
  id: string;
  name: string;
  description?: string;
  category?: string;
  is_active: boolean;
  language_config?: LanguageConfig;
  created_by?: string;
  created_at: string;
  updated_at: string;
}

export interface TestSuiteWithScenarios extends TestSuite {
  scenarios: SuiteScenarioInfo[];
  scenario_count: number;
}

export interface TestSuitesListResponse {
  test_suites: TestSuite[];
  total: number;
  skip: number;
  limit: number;
}

export interface CreateTestSuiteRequest {
  name: string;
  description?: string;
  category?: string;
  is_active?: boolean;
  language_config?: LanguageConfig;
  scenario_ids?: string[];
}

export interface UpdateTestSuiteRequest {
  name?: string;
  description?: string;
  category?: string;
  is_active?: boolean;
  language_config?: LanguageConfig;
}

export interface SuiteExecutionScenarioResult {
  scenario_id: string;
  scenario_name: string;
  execution_id?: string;
  status: string;
  error_message?: string;
}

export interface RunSuiteResponse {
  suite_id: string;
  suite_name: string;
  suite_run_id: string;
  total_scenarios: number;
  status: string;
  scenario_results: SuiteExecutionScenarioResult[];
  started_at?: string;
  completed_at?: string;
}

export interface CategoricalScenario {
  id: string;
  name: string;
  description?: string;
  steps_count: number;
}

export interface CategoricalSuite {
  name: string;
  scenario_count: number;
  scenario_ids: string[];
  scenarios: CategoricalScenario[];
}

export interface CategoricalSuitesResponse {
  categorical_suites: CategoricalSuite[];
  total: number;
}

// =============================================================================
// Test Suite CRUD Operations
// =============================================================================

/**
 * Fetch all test suites with optional filtering
 */
export const getTestSuites = async (params?: {
  skip?: number;
  limit?: number;
  category?: string;
  is_active?: boolean;
}): Promise<TestSuitesListResponse> => {
  const response = await apiClient.get<TestSuitesListResponse>('/test-suites', {
    params: {
      skip: params?.skip ?? 0,
      limit: params?.limit ?? 100,
      ...(params?.category && { category: params.category }),
      ...(params?.is_active !== undefined && { is_active: params.is_active }),
    },
  });
  return response.data;
};

/**
 * Fetch a single test suite by ID (without scenarios)
 */
export const getTestSuiteById = async (suiteId: string): Promise<TestSuite> => {
  const response = await apiClient.get<TestSuite>(`/test-suites/${suiteId}`);
  return response.data;
};

/**
 * Fetch a test suite with its scenarios
 */
export const getTestSuiteWithScenarios = async (
  suiteId: string
): Promise<TestSuiteWithScenarios> => {
  const response = await apiClient.get<TestSuiteWithScenarios>(
    `/test-suites/${suiteId}/scenarios`
  );
  return response.data;
};

/**
 * Create a new test suite
 */
export const createTestSuite = async (
  data: CreateTestSuiteRequest
): Promise<TestSuite> => {
  const response = await apiClient.post<TestSuite>('/test-suites', data);
  return response.data;
};

/**
 * Update an existing test suite
 */
export const updateTestSuite = async (
  suiteId: string,
  data: UpdateTestSuiteRequest
): Promise<TestSuite> => {
  const response = await apiClient.put<TestSuite>(`/test-suites/${suiteId}`, data);
  return response.data;
};

/**
 * Delete a test suite
 */
export const deleteTestSuite = async (suiteId: string): Promise<void> => {
  await apiClient.delete(`/test-suites/${suiteId}`);
};

// =============================================================================
// Scenario Management within Suites
// =============================================================================

/**
 * Add scenarios to a test suite
 */
export const addScenariosToSuite = async (
  suiteId: string,
  scenarioIds: string[]
): Promise<TestSuiteWithScenarios> => {
  const response = await apiClient.post<TestSuiteWithScenarios>(
    `/test-suites/${suiteId}/scenarios`,
    { scenario_ids: scenarioIds }
  );
  return response.data;
};

/**
 * Remove scenarios from a test suite
 */
export const removeScenariosFromSuite = async (
  suiteId: string,
  scenarioIds: string[]
): Promise<TestSuiteWithScenarios> => {
  const response = await apiClient.delete<TestSuiteWithScenarios>(
    `/test-suites/${suiteId}/scenarios`,
    { data: { scenario_ids: scenarioIds } }
  );
  return response.data;
};

/**
 * Reorder scenarios within a test suite
 */
export const reorderSuiteScenarios = async (
  suiteId: string,
  scenarioOrder: string[]
): Promise<TestSuiteWithScenarios> => {
  const response = await apiClient.put<TestSuiteWithScenarios>(
    `/test-suites/${suiteId}/scenarios/reorder`,
    { scenario_order: scenarioOrder }
  );
  return response.data;
};

// =============================================================================
// Suite Execution
// =============================================================================

/**
 * Run all scenarios in a test suite
 */
export const runTestSuite = async (
  suiteId: string,
  languageCode?: string
): Promise<RunSuiteResponse> => {
  const response = await apiClient.post<RunSuiteResponse>(
    `/test-suites/${suiteId}/run`,
    { language_code: languageCode ?? 'en-US' }
  );
  return response.data;
};

// =============================================================================
// Categorical Suites (Virtual suites grouped by scenario category)
// =============================================================================

/**
 * Fetch categorical suites (scenarios grouped by category)
 */
export const getCategoricalSuites = async (): Promise<CategoricalSuitesResponse> => {
  const response = await apiClient.get<CategoricalSuitesResponse>('/test-suites/categorical');
  return response.data;
};

/**
 * Run all scenarios in a category (categorical suite)
 */
export const runCategoricalSuite = async (
  categoryName: string,
  scenarioIds: string[],
  languageCode?: string
): Promise<RunSuiteResponse> => {
  const response = await apiClient.post<RunSuiteResponse>(
    '/test-suites/categorical/run',
    {
      category_name: categoryName,
      scenario_ids: scenarioIds,
      language_code: languageCode ?? 'en-US'
    }
  );
  return response.data;
};

// =============================================================================
// Default Export
// =============================================================================
// NOTE: For Suite Runs (execution history), use suiteRun.service.ts instead

export default {
  getTestSuites,
  getTestSuiteById,
  getTestSuiteWithScenarios,
  createTestSuite,
  updateTestSuite,
  deleteTestSuite,
  addScenariosToSuite,
  removeScenariosFromSuite,
  reorderSuiteScenarios,
  runTestSuite,
  getCategoricalSuites,
  runCategoricalSuite,
};
