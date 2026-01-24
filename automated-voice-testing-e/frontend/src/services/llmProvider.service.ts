/**
 * LLM Provider service.
 *
 * Provides access to LLM provider configuration endpoints.
 */

import apiClient from './api';
import type {
  LLMProviderConfig,
  LLMProviderConfigCreate,
  LLMProviderConfigUpdate,
  LLMProviderConfigListResponse,
  LLMProvidersSummaryResponse,
  TestProviderRequest,
  TestProviderResponse,
} from '../types/llmProvider';

/**
 * Get summary of all LLM providers and their configuration status.
 */
export const getProvidersSummary = async (): Promise<LLMProvidersSummaryResponse> => {
  const response = await apiClient.get<LLMProvidersSummaryResponse>('/llm-providers/summary');
  return response.data;
};

/**
 * List all LLM provider configurations.
 */
export const listProviderConfigs = async (params?: {
  provider?: string;
  is_active?: boolean;
}): Promise<LLMProviderConfigListResponse> => {
  const response = await apiClient.get<LLMProviderConfigListResponse>('/llm-providers', {
    params,
  });
  return response.data;
};

/**
 * Get a specific provider configuration by ID.
 */
export const getProviderConfig = async (configId: string): Promise<LLMProviderConfig> => {
  const response = await apiClient.get<LLMProviderConfig>(`/llm-providers/${configId}`);
  return response.data;
};

/**
 * Create a new provider configuration.
 */
export const createProviderConfig = async (
  data: LLMProviderConfigCreate
): Promise<LLMProviderConfig> => {
  const response = await apiClient.post<LLMProviderConfig>('/llm-providers', data);
  return response.data;
};

/**
 * Update a provider configuration.
 */
export const updateProviderConfig = async (
  configId: string,
  data: LLMProviderConfigUpdate
): Promise<LLMProviderConfig> => {
  const response = await apiClient.patch<LLMProviderConfig>(
    `/llm-providers/${configId}`,
    data
  );
  return response.data;
};

/**
 * Delete a provider configuration.
 */
export const deleteProviderConfig = async (configId: string): Promise<void> => {
  await apiClient.delete(`/llm-providers/${configId}`);
};

/**
 * Test a provider configuration.
 */
export const testProvider = async (data: TestProviderRequest): Promise<TestProviderResponse> => {
  const response = await apiClient.post<TestProviderResponse>('/llm-providers/test', data);
  return response.data;
};
