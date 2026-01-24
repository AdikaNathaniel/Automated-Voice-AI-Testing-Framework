/**
 * CI/CD Configuration Service
 *
 * API service for managing webhook-to-test-suite mappings
 */

import axios from 'axios';
import type {
  CICDConfig,
  CICDConfigUpdatePayload,
  CICDProvider,
  WebhookInstructions,
  WebhookTestResult,
} from '../types/cicdConfig';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const getAuthHeaders = () => {
  const token = localStorage.getItem('accessToken');
  return {
    Authorization: token ? `Bearer ${token}` : 'Bearer ',
  };
};

/**
 * Get CI/CD configuration for the current tenant
 */
export const getCICDConfig = async (): Promise<CICDConfig> => {
  const response = await axios.get<{ data: CICDConfig }>(
    `${API_BASE_URL}/cicd-config`,
    { headers: getAuthHeaders() }
  );
  return response.data.data;
};

/**
 * Update CI/CD configuration
 */
export const updateCICDConfig = async (
  payload: CICDConfigUpdatePayload
): Promise<CICDConfig> => {
  const response = await axios.put<{ data: CICDConfig }>(
    `${API_BASE_URL}/cicd-config`,
    payload,
    { headers: getAuthHeaders() }
  );
  return response.data.data;
};

/**
 * Test webhook configuration for a provider
 */
export const testWebhookConfig = async (
  provider: CICDProvider
): Promise<WebhookTestResult> => {
  const response = await axios.post<{ data: WebhookTestResult }>(
    `${API_BASE_URL}/cicd-config/test-webhook/${provider}`,
    undefined,
    { headers: getAuthHeaders() }
  );
  return response.data.data;
};

/**
 * Get webhook setup instructions for a provider
 */
export const getWebhookInstructions = async (
  provider: CICDProvider
): Promise<WebhookInstructions> => {
  const response = await axios.get<{ data: WebhookInstructions }>(
    `${API_BASE_URL}/cicd-config/webhook-instructions/${provider}`,
    { headers: getAuthHeaders() }
  );
  return response.data.data;
};
