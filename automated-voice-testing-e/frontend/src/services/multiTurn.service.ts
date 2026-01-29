/**
 * Multi-Turn Scenario Service
 *
 * This service provides API calls for multi-turn conversation scenario execution.
 * It handles:
 * - Listing scenario scripts
 * - Executing multi-turn scenarios
 * - Retrieving execution status and results
 * - Fetching step-by-step execution details
 *
 * @example
 * ```typescript
 * import { multiTurnService } from './services/multiTurn.service';
 *
 * // List all scenarios
 * const scenarios = await multiTurnService.listScenarios();
 *
 * // Execute a scenario
 * const result = await multiTurnService.executeScenario(scriptId);
 *
 * // Get execution status
 * const status = await multiTurnService.getExecutionStatus(executionId);
 * ```
 */

import apiClient from './api';
import type {
  ScenarioScript,
  MultiTurnExecution,
  StepExecution,
  ExecuteScenarioRequest,
  ExecuteScenarioResponse,
  ExecutionStatusResponse,
  StepExecutionsResponse,
  ScenarioListResponse,
  NoiseProfile,
} from '../types/multiTurn';

class MultiTurnService {
  private readonly baseUrl = '/multi-turn';

  /**
   * List all scenario scripts
   *
   * @param params - Query parameters for filtering and pagination
   * @returns Promise with list of scenario scripts
   */
  async listScenarios(params?: {
    is_active?: boolean;
    approval_status?: string;
    page?: number;
    page_size?: number;
  }): Promise<ScenarioListResponse> {
    const response = await apiClient.get<{ success: boolean; data: ScenarioListResponse }>(
      `${this.baseUrl}/scenarios`,
      { params }
    );
    return response.data.data;
  }

  /**
   * Get a specific scenario script by ID
   *
   * @param scriptId - UUID of the scenario script
   * @returns Promise with scenario script details
   */
  async getScenario(scriptId: string): Promise<ScenarioScript> {
    const response = await apiClient.get<{ success: boolean; data: ScenarioScript }>(
      `${this.baseUrl}/scenarios/${scriptId}`
    );
    return response.data.data;
  }

  /**
   * Create a new scenario script
   *
   * @param scenarioData - Scenario data including steps and expected outcomes
   * @returns Promise with created scenario
   */
  async createScenario(scenarioData: any): Promise<ScenarioScript> {
    const response = await apiClient.post<{ success: boolean; data: ScenarioScript }>(
      `${this.baseUrl}/scenarios`,
      scenarioData
    );
    return response.data.data;
  }

  /**
   * Update an existing scenario script
   *
   * @param scriptId - UUID of the scenario script
   * @param scenarioData - Updated scenario data
   * @returns Promise with updated scenario
   */
  async updateScenario(scriptId: string, scenarioData: any): Promise<ScenarioScript> {
    const response = await apiClient.put<{ success: boolean; data: ScenarioScript }>(
      `${this.baseUrl}/scenarios/${scriptId}`,
      scenarioData
    );
    return response.data.data;
  }

  /**
   * Delete a scenario script
   *
   * @param scriptId - UUID of the scenario script
   * @returns Promise with deletion result
   */
  async deleteScenario(scriptId: string): Promise<void> {
    await apiClient.delete(`${this.baseUrl}/scenarios/${scriptId}`);
  }

  /**
   * Submit scenario for review
   *
   * @param scriptId - UUID of the scenario script
   * @returns Promise with updated scenario
   */
  async submitForReview(scriptId: string): Promise<ScenarioScript> {
    const response = await apiClient.post<{ success: boolean; data: ScenarioScript }>(
      `${this.baseUrl}/scenarios/${scriptId}/submit-for-review`
    );
    return response.data.data;
  }

  /**
   * Approve a scenario
   *
   * @param scriptId - UUID of the scenario script
   * @param reviewNotes - Optional review notes
   * @returns Promise with approved scenario
   */
  async approveScenario(scriptId: string, reviewNotes?: string): Promise<ScenarioScript> {
    const response = await apiClient.post<{ success: boolean; data: ScenarioScript }>(
      `${this.baseUrl}/scenarios/${scriptId}/approve`,
      { review_notes: reviewNotes }
    );
    return response.data.data;
  }

  /**
   * Reject a scenario
   *
   * @param scriptId - UUID of the scenario script
   * @param reviewNotes - Required review notes explaining rejection
   * @returns Promise with rejected scenario
   */
  async rejectScenario(scriptId: string, reviewNotes: string): Promise<ScenarioScript> {
    const response = await apiClient.post<{ success: boolean; data: ScenarioScript }>(
      `${this.baseUrl}/scenarios/${scriptId}/reject`,
      { review_notes: reviewNotes }
    );
    return response.data.data;
  }

  /**
   * Execute a multi-turn scenario
   *
   * @param scriptId - UUID of the scenario script to execute
   * @param request - Optional execution parameters
   * @returns Promise with execution result
   */
  async executeScenario(
    scriptId: string,
    request?: ExecuteScenarioRequest
  ): Promise<ExecuteScenarioResponse> {
    const response = await apiClient.post<{ success: boolean; data: ExecuteScenarioResponse }>(
      `${this.baseUrl}/execute/${scriptId}`,
      request || {}
    );
    return response.data.data;
  }

  /**
   * Get execution status and summary
   *
   * @param executionId - UUID of the multi-turn execution
   * @returns Promise with execution status
   */
  async getExecutionStatus(executionId: string): Promise<MultiTurnExecution> {
    const response = await apiClient.get<{ success: boolean; data: MultiTurnExecution }>(
      `${this.baseUrl}/executions/${executionId}`
    );
    return response.data.data;
  }

  /**
   * Get step-by-step execution results
   *
   * @param executionId - UUID of the multi-turn execution
   * @returns Promise with step execution details
   */
  async getStepExecutions(executionId: string): Promise<StepExecutionsResponse> {
    const response = await apiClient.get<{ success: boolean; data: StepExecutionsResponse }>(
      `${this.baseUrl}/executions/${executionId}/steps`
    );
    return response.data.data;
  }

  /**
   * List all multi-turn executions
   *
   * @param params - Query parameters for filtering and pagination
   * @returns Promise with list of executions and pagination info
   */
  async listExecutions(params?: {
    suite_run_id?: string;
    script_id?: string;
    status?: string;
    page?: number;
    page_size?: number;
  }): Promise<{ executions: MultiTurnExecution[]; total: number; pagination?: any }> {
    const response = await apiClient.get<{
      data: MultiTurnExecution[];
      pagination: {
        page: number;
        page_size: number;
        total_items: number;
        total_pages: number;
      };
    }>(`${this.baseUrl}/executions`, {
      params,
    });
    return {
      executions: response.data.data,
      total: response.data.pagination.total_items,
      pagination: response.data.pagination,
    };
  }

  /**
   * Cancel a running multi-turn execution
   *
   * @param executionId - UUID of the multi-turn execution
   * @returns Promise with cancellation result
   */
  async cancelExecution(executionId: string): Promise<void> {
    await apiClient.post(`${this.baseUrl}/executions/${executionId}/cancel`);
  }

  /**
   * Get available noise profiles for audio testing
   *
   * @param category - Optional category filter (vehicle, environmental, industrial)
   * @returns Promise with list of noise profiles
   */
  async getNoiseProfiles(category?: string): Promise<NoiseProfile[]> {
    const params: Record<string, string> = {};
    if (category) {
      params.category = category;
    }
    const response = await apiClient.get<{ success: boolean; data: NoiseProfile[] }>(
      `/scenarios/noise-profiles`,
      { params }
    );
    return response.data.data;
  }

  /**
   * Synthesize text to speech audio
   *
   * @param text - Text to convert to speech
   * @param language - Language code (e.g. 'en', 'es', 'fr')
   * @returns Promise with audio Blob (MP3)
   */
  async synthesizeUtterance(text: string, language: string = 'en'): Promise<Blob> {
    const response = await apiClient.post(
      `/scenarios/tts/synthesize`,
      { text, language },
      { responseType: 'blob' }
    );
    return response.data;
  }
}

// Export singleton instance
export const multiTurnService = new MultiTurnService();
export default multiTurnService;

