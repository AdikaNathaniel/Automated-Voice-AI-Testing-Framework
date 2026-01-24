/**
 * Pattern Group API Service
 *
 * Handles all API interactions for LLM-enhanced pattern recognition.
 */

import apiClient from './api';
import type {
  PatternGroup,
  PatternGroupListResponse,
  PatternGroupDetailResponse,
  PatternGroupCreate,
  PatternGroupUpdate,
} from '../types/patternGroup';

/**
 * List pattern groups with optional filters.
 */
export async function listPatternGroups(params: {
  status?: string;
  severity?: string;
  pattern_type?: string;
  skip?: number;
  limit?: number;
}): Promise<PatternGroupListResponse> {
  const response = await apiClient.get<PatternGroupListResponse>(
    '/pattern-groups',
    { params }
  );
  return response.data;
}

/**
 * Get trending patterns.
 */
export async function getTrendingPatterns(params: {
  days?: number;
  limit?: number;
}): Promise<PatternGroup[]> {
  const response = await apiClient.get<PatternGroup[]>(
    '/pattern-groups/trending',
    { params }
  );
  return response.data;
}

/**
 * Get pattern group by ID.
 */
export async function getPatternGroup(id: string): Promise<PatternGroup> {
  const response = await apiClient.get<PatternGroup>(
    `/pattern-groups/${id}`
  );
  return response.data;
}

/**
 * Get pattern group with linked edge cases.
 */
export async function getPatternGroupDetails(
  id: string,
  limit = 50
): Promise<PatternGroupDetailResponse> {
  const response = await apiClient.get<PatternGroupDetailResponse>(
    `/pattern-groups/${id}/details`,
    { params: { limit } }
  );
  return response.data;
}

/**
 * Create a new pattern group.
 */
export async function createPatternGroup(
  data: PatternGroupCreate
): Promise<PatternGroup> {
  const response = await apiClient.post<PatternGroup>(
    '/pattern-groups',
    data
  );
  return response.data;
}

/**
 * Update pattern group.
 */
export async function updatePatternGroup(
  id: string,
  data: PatternGroupUpdate
): Promise<PatternGroup> {
  const response = await apiClient.patch<PatternGroup>(
    `/pattern-groups/${id}`,
    data
  );
  return response.data;
}

/**
 * Delete pattern group.
 */
export async function deletePatternGroup(id: string): Promise<void> {
  await apiClient.delete(`/pattern-groups/${id}`);
}

/**
 * Trigger pattern recognition analysis manually.
 */
export async function triggerPatternAnalysis(params: {
  lookback_days?: number;
  min_pattern_size?: number;
  similarity_threshold?: number;
}): Promise<{
  task_id: string;
  status: string;
  message: string;
  parameters: {
    lookback_days: number;
    min_pattern_size: number;
    similarity_threshold: number;
  };
}> {
  const response = await apiClient.post(
    '/pattern-groups/analyze/trigger',
    null,
    { params }
  );
  return response.data;
}

/**
 * Check pattern analysis job status.
 */
export async function checkAnalysisStatus(taskId: string): Promise<{
  task_id: string;
  status: string;
  message: string;
  result?: any;
  error?: string;
}> {
  const response = await apiClient.get(
    `/pattern-groups/analyze/status/${taskId}`
  );
  return response.data;
}
