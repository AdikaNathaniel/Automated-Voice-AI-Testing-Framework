/**
 * Pattern Analysis Configuration Service
 *
 * API client for managing pattern analysis settings
 */

import axios from 'axios';
import type {
  PatternAnalysisConfig,
  PatternAnalysisConfigUpdate,
  ManualAnalysisRequest,
  ManualAnalysisResponse,
  DefaultConfig,
} from '../types/patternAnalysisConfig';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('accessToken');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

/**
 * Get pattern analysis configuration for current tenant
 */
export const getPatternAnalysisConfig = async (): Promise<PatternAnalysisConfig> => {
  const response = await api.get<PatternAnalysisConfig>('/pattern-analysis/config');
  return response.data;
};

/**
 * Update pattern analysis configuration
 */
export const updatePatternAnalysisConfig = async (
  updates: PatternAnalysisConfigUpdate
): Promise<PatternAnalysisConfig> => {
  const response = await api.put<PatternAnalysisConfig>('/pattern-analysis/config', updates);
  return response.data;
};

/**
 * Trigger manual pattern analysis
 */
export const triggerManualAnalysis = async (
  request: ManualAnalysisRequest
): Promise<ManualAnalysisResponse> => {
  const response = await api.post<ManualAnalysisResponse>(
    '/pattern-analysis/config/analyze/manual',
    request
  );
  return response.data;
};

/**
 * Get default configuration values
 */
export const getDefaultConfig = async (): Promise<DefaultConfig> => {
  const response = await api.get<DefaultConfig>('/pattern-analysis/config/defaults');
  return response.data;
};
