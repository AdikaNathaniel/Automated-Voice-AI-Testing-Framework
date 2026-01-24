/**
 * Validation Service
 *
 * This module provides API service methods for human validation workflow operations.
 * Handles communication with the backend validation API endpoints for:
 * - Fetching validation queue items
 * - Claiming validation items
 * - Submitting validation decisions
 * - Releasing validation items
 * - Fetching validation statistics
 *
 * @module services/validation.service
 */

import apiClient from './api';
import type {
  ValidationQueue,
  ValidationQueueFilters,
  HumanValidationCreate,
  ValidationStats,
} from '../types/validation';

/**
 * Base URL for validation API endpoints
 */
const VALIDATION_BASE_URL = '/validation';

/**
 * Fetch validation queue items
 *
 * Retrieves validation queue items from the API with optional filtering.
 * Returns items that are pending human review, ordered by priority.
 *
 * @param filters - Optional filters to apply to the queue query
 * @returns Promise resolving to array of ValidationQueue items
 *
 * @example
 * ```typescript
 * // Fetch all pending validation items
 * const queue = await fetchValidationQueue();
 *
 * // Fetch with filters
 * const filtered = await fetchValidationQueue({
 *   status: ValidationStatus.PENDING,
 *   languageCode: 'en',
 *   minPriority: 5
 * });
 * ```
 */
export const fetchValidationQueue = async (
  filters?: ValidationQueueFilters
): Promise<ValidationQueue[]> => {
  try {
    const params = new URLSearchParams();

    if (filters) {
      if (filters.status) params.append('status', filters.status);
      if (filters.languageCode) params.append('languageCode', filters.languageCode);
      if (filters.minPriority !== undefined) params.append('minPriority', filters.minPriority.toString());
      if (filters.maxPriority !== undefined) params.append('maxPriority', filters.maxPriority.toString());
      if (filters.validatorId) params.append('validatorId', filters.validatorId);
    }

    const queryString = params.toString();
    const url = `${VALIDATION_BASE_URL}/queue${queryString ? `?${queryString}` : ''}`;

    const response = await apiClient.get(url);
    return response.data.data as ValidationQueue[];
  } catch (error) {
    console.error('Error fetching validation queue:', error);
    throw error;
  }
};

/**
 * Claim a validation item
 *
 * Claims a specific validation item from the queue for the current user.
 * Sets the item status to 'claimed' and assigns it to the current validator.
 * The item will be locked for 10 minutes before auto-release.
 *
 * @param itemId - ID of the validation queue item to claim
 * @returns Promise resolving to the claimed ValidationQueue item
 *
 * @example
 * ```typescript
 * const claimedItem = await claimValidation('queue-item-123');
 * console.log(`Claimed item ${claimedItem.id} for validation`);
 * ```
 */
export const claimValidation = async (itemId: string): Promise<ValidationQueue> => {
  try {
    const url = `${VALIDATION_BASE_URL}/${itemId}/claim`;
    const response = await apiClient.post(url);
    return response.data.data as ValidationQueue;
  } catch (error) {
    console.error(`Error claiming validation item ${itemId}:`, error);
    throw error;
  }
};

/**
 * Submit validation decision
 *
 * Submits the human validator's decision for a validation item.
 * Includes the decision (approve/reject/uncertain), optional feedback,
 * and time spent on the validation.
 *
 * @param queueId - Validation queue item identifier
 * @param validationData - Human validation decision data
 * @returns Promise resolving to success confirmation
 *
 * @example
 * ```typescript
 * await submitValidation(queueId, {
 *   validationResultId: 'result-123',
 *   decision: ValidationDecision.APPROVE,
 *   feedback: 'Response matches expected outcome',
 *   timeSpent: 45
 * });
 * ```
 */
export const submitValidation = async (
  queueId: string,
  validationData: HumanValidationCreate
): Promise<Record<string, unknown>> => {
  try {
    const url = `${VALIDATION_BASE_URL}/${queueId}/submit`;
    const payload = {
      validation_decision: validationData.decision,
      feedback: validationData.feedback,
      time_spent_seconds: validationData.timeSpent,
    };
    const response = await apiClient.post(url, payload);
    return response.data.data as Record<string, unknown>;
  } catch (error) {
    console.error('Error submitting validation:', error);
    throw error;
  }
};

/**
 * Release validation item
 *
 * Releases a currently claimed validation item back to the queue.
 * This allows another validator to claim the item.
 * Use this when a validator cannot complete the validation.
 *
 * @param itemId - ID of the validation queue item to release
 * @returns Promise resolving to success confirmation
 *
 * @example
 * ```typescript
 * await releaseValidation('queue-item-123');
 * console.log('Item released back to queue');
 * ```
 */
export const releaseValidation = async (
  itemId: string
): Promise<Record<string, unknown>> => {
  try {
    const url = `${VALIDATION_BASE_URL}/${itemId}/release`;
    const response = await apiClient.post(url);
    return response.data.data as Record<string, unknown>;
  } catch (error) {
    console.error(`Error releasing validation item ${itemId}:`, error);
    throw error;
  }
};

/**
 * Fetch validation statistics
 *
 * Retrieves current validation queue statistics including:
 * - Total pending items
 * - Total claimed items
 * - Total completed items
 * - Average confidence scores
 * - Queue age metrics
 *
 * @returns Promise resolving to ValidationStats object
 *
 * @example
 * ```typescript
 * const stats = await fetchValidationStats();
 * console.log(`Pending validations: ${stats.pendingCount}`);
 * console.log(`Completion rate: ${stats.completedCount / stats.totalCount! * 100}%`);
 * ```
 */
export const fetchValidationStats = async (): Promise<ValidationStats> => {
  try {
    const url = `${VALIDATION_BASE_URL}/stats`;
    const response = await apiClient.get(url);
    return response.data.data as ValidationStats;
  } catch (error) {
    console.error('Error fetching validation statistics:', error);
    throw error;
  }
};

/**
 * Get next validation item
 *
 * Convenience method that fetches the queue and automatically claims
 * the highest priority pending item for the current user.
 *
 * @returns Promise resolving to the claimed ValidationQueue item or null if queue is empty
 *
 * @example
 * ```typescript
 * const nextItem = await getNextValidationItem();
 * if (nextItem) {
 *   console.log(`Starting validation for item ${nextItem.id}`);
 * } else {
 *   console.log('No items available for validation');
 * }
 * ```
 */
export const getNextValidationItem = async (): Promise<ValidationQueue | null> => {
  try {
    // Fetch pending items
    const queue = await fetchValidationQueue({
      status: 'pending' as unknown, // Cast to unknown to avoid enum issues
    });

    if (queue.length === 0) {
      return null;
    }

    // Claim the first item (highest priority)
    const firstItem = queue[0];
    const claimedItem = await claimValidation(firstItem.id);
    return claimedItem;
  } catch (error) {
    console.error('Error getting next validation item:', error);
    throw error;
  }
};

/**
 * Validation result details interface
 *
 * Contains results from Houndify deterministic and LLM ensemble validation.
 *
 * Validation Architecture:
 * 1. Houndify Deterministic: CommandKind match, ASR confidence, response content
 * 2. LLM Ensemble: Semantic understanding with multiple models
 * 3. Combined Decision: final_decision (pass/fail/uncertain), review_status
 */
export interface ValidationResultDetail {
  id: string;
  suite_run_id: string | null;
  multi_turn_execution_id: string | null;
  expected_outcome_id: string | null;

  // Houndify deterministic validation
  command_kind_match_score: number | null;
  asr_confidence_score: number | null;
  houndify_passed: boolean | null;
  houndify_result: Record<string, unknown> | null;

  // LLM ensemble validation
  llm_passed: boolean | null;
  ensemble_result: Record<string, unknown> | null;

  // Combined decision
  final_decision: string | null;
  review_status: string | null;

  // Metadata
  created_at: string | null;
  updated_at: string | null;
}

/**
 * Fetch validation result details
 *
 * Retrieves complete AI validation result including all calculated scores:
 * - Houndify CommandKind match score
 * - Houndify ASR confidence score
 * - LLM ensemble result with pass/fail decision
 * - Review status (auto_pass, needs_review, auto_fail)
 *
 * @param validationResultId - ID of the validation result to fetch
 * @returns Promise resolving to ValidationResultDetail object
 *
 * @example
 * ```typescript
 * const result = await fetchValidationResult('result-123');
 * console.log(`CommandKind Match: ${(result.command_kind_match_score || 0) * 100}%`);
 * console.log(`Final Decision: ${result.final_decision}`);
 * console.log(`Status: ${result.review_status}`);
 * ```
 */
export const fetchValidationResult = async (
  validationResultId: string
): Promise<ValidationResultDetail> => {
  try {
    const url = `/suite-runs/validation-results/${validationResultId}`;
    const response = await apiClient.get(url);
    return response.data as ValidationResultDetail;
  } catch (error) {
    console.error(`Error fetching validation result ${validationResultId}:`, error);
    throw error;
  }
};
