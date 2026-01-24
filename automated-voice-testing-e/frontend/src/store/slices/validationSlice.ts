/**
 * Validation Redux Slice
 *
 * This module manages the state for the human validation workflow, including:
 * - Validation queue management
 * - Claiming validation items
 * - Submitting validation decisions
 * - Tracking validation statistics
 * - Managing current validation item and timer
 *
 * @module store/slices/validationSlice
 */

import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';
import axios from 'axios';
import type {
  ValidationQueue,
  ValidationStats,
  HumanValidationCreate,
  ValidationQueueFilters,
  ValidatorPersonalStats,
  ValidatorLeaderboardEntry,
  ValidatorAccuracyPoint,
  ValidatorStatisticsPayload,
  GroupedValidationQueue,
} from '../../types/validation';

const VALIDATION_BASE_URL = '/api/v1/validation';

/**
 * Helper function to get authorization headers
 * @returns Authorization headers with Bearer token
 */
const authorizationHeaders = () => {
  const token = localStorage.getItem('accessToken');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

/**
 * ValidationState interface
 *
 * Defines the shape of the validation slice state.
 */
export interface ValidationState {
  /** Array of validation queue items */
  queue: ValidationQueue[];

  /** Grouped validation queue items (by multi-turn execution) */
  groupedQueue: GroupedValidationQueue[];

  /** Pagination info for grouped queue */
  groupedQueuePagination: {
    page: number;
    pageSize: number;
    total: number;
    totalPages: number;
  };

  /** Currently claimed validation item (null if none) */
  current: ValidationQueue | null;

  /** Loading state for async operations */
  loading: boolean;

  /** Error message (null if no error) */
  error: string | null;

  /** Validation statistics */
  stats: ValidationStats | null;

  /** Personal statistics for the current validator */
  validatorSummary: ValidatorPersonalStats | null;

  /** Leaderboard entries for top validators */
  validatorLeaderboard: ValidatorLeaderboardEntry[];

  /** Accuracy trend data points for charts */
  validatorAccuracyTrend: ValidatorAccuracyPoint[];

  /** Time spent on current validation in seconds */
  timeSpent: number;

  /** Timer start timestamp for current validation */
  timerStarted: number | null;
}

/**
 * Initial state for validation slice
 */
const initialState: ValidationState = {
  queue: [],
  groupedQueue: [],
  groupedQueuePagination: {
    page: 1,
    pageSize: 20,
    total: 0,
    totalPages: 0,
  },
  current: null,
  loading: false,
  error: null,
  stats: null,
  validatorSummary: null,
  validatorLeaderboard: [],
  validatorAccuracyTrend: [],
  timeSpent: 0,
  timerStarted: null,
};

// ============================================================================
// Async Thunks
// ============================================================================

/**
 * Transform snake_case API response to camelCase for ValidationQueue
 */
function transformValidationQueueItem(item: any): ValidationQueue {
  // Transform AI scores if present
  const aiScores = item.ai_scores ? {
    confidenceScore: item.ai_scores.confidence_score,
    accuracyScore: item.ai_scores.accuracy_score,
    semanticSimilarityScore: item.ai_scores.semantic_similarity_score,
    werScore: item.ai_scores.wer_score,
    cerScore: item.ai_scores.cer_score,
    serScore: item.ai_scores.ser_score,
    commandKindMatchScore: item.ai_scores.command_kind_match_score,
    asrConfidenceScore: item.ai_scores.asr_confidence_score,
    reviewStatus: item.ai_scores.review_status,
    // LLM Ensemble validation fields
    houndifyPassed: item.ai_scores.houndify_passed,
    houndifyResult: item.ai_scores.houndify_result,
    llmPassed: item.ai_scores.llm_passed,
    ensembleResult: item.ai_scores.ensemble_result,
    finalDecision: item.ai_scores.final_decision,
  } : undefined;

  // Transform validation history if present
  const validationHistory = item.validation_history?.map((hv: any) => ({
    id: hv.id,
    validatorId: hv.validator_id,
    validatorName: hv.validator_name,
    decision: hv.decision,
    feedback: hv.feedback,
    timeSpentSeconds: hv.time_spent_seconds,
    isSecondOpinion: hv.is_second_opinion,
    claimedAt: hv.claimed_at,
    submittedAt: hv.submitted_at,
    createdAt: hv.created_at,
  }));

  return {
    id: item.id,
    validationResultId: item.validation_result_id,
    priority: item.priority,
    confidenceScore: item.confidence_score,
    languageCode: item.language_code,
    status: item.status,
    claimedBy: item.claimed_by,
    claimedAt: item.claimed_at,
    createdAt: item.created_at,
    updatedAt: item.updated_at,
    testCaseName: item.test_case_name,
    inputText: item.input_text,
    expectedCommandKind: item.expected_command_kind,
    actualCommandKind: item.actual_command_kind,
    expectedEntities: item.expected_entities,
    actualEntities: item.actual_entities,
    // Extract entity validation from houndify_result
    entityValidation: item.ai_scores?.houndify_result?.entity_validation ?? null,
    expectedResponse: item.expected_response,
    actualResponse: item.actual_response,
    context: item.context,
    inputAudioUrl: item.input_audio_url,
    responseAudioUrl: item.response_audio_url,
    // AI validation scores
    aiScores,
    // Human validation data (if completed)
    humanValidationDecision: item.human_validation_decision,
    humanValidationFeedback: item.human_validation_feedback,
    humanValidationSubmittedAt: item.human_validation_submitted_at,
    humanValidationValidatorName: item.human_validation_validator_name,
    // Full validation history
    validationHistory,
  };
}

/**
 * Fetch validation queue items
 *
 * Retrieves pending validation items from the API based on optional filters.
 *
 * @param filters - Optional filters to apply to the queue query
 * @returns Promise resolving to array of ValidationQueue items
 */
export const fetchValidationQueue = createAsyncThunk(
  'validation/fetchQueue',
  async (filters?: ValidationQueueFilters) => {
    const params = new URLSearchParams();

    if (filters?.status) params.append('status', filters.status);
    if (filters?.languageCode) params.append('language_code', filters.languageCode);
    if (filters?.minPriority !== undefined) params.append('minPriority', filters.minPriority.toString());
    if (filters?.maxPriority !== undefined) params.append('maxPriority', filters.maxPriority.toString());

    const queryString = params.toString();
    const url = `${VALIDATION_BASE_URL}/queue${queryString ? `?${queryString}` : ''}`;

    const response = await axios.get(url, {
      headers: authorizationHeaders(),
    });

    // Transform snake_case API response to camelCase
    const data = response.data.data || [];
    return data.map(transformValidationQueueItem);
  }
);

/**
 * Transform snake_case API response to camelCase TypeScript interface
 */
function transformGroupedQueueItem(item: any): GroupedValidationQueue {
  return {
    executionId: item.execution_id,
    scenarioName: item.scenario_name,
    scenarioId: item.scenario_id,
    totalSteps: item.total_steps,
    stepsNeedingReview: item.steps_needing_review,
    avgConfidence: item.avg_confidence,
    minConfidence: item.min_confidence,
    maxConfidence: item.max_confidence,
    status: item.status,
    createdAt: item.created_at,
    stepValidations: (item.step_validations || []).map((step: any) => ({
      queueId: step.queue_id,
      validationResultId: step.validation_result_id,
      stepExecutionId: step.step_execution_id,
      stepOrder: step.step_order,
      userUtterance: step.user_utterance,
      confidenceScore: step.confidence_score,
      reviewStatus: step.review_status,
      queueStatus: step.queue_status,
      priority: step.priority,
      languageCode: step.language_code,
      createdAt: step.created_at,
    })),
  };
}

/**
 * Fetch grouped validation queue items
 *
 * Retrieves validation queue items grouped by multi-turn execution.
 * This allows validators to see all steps from a single execution together.
 *
 * @param filters - Optional filters to apply to the queue query (including pagination)
 * @returns Promise resolving to paginated GroupedValidationQueue response
 */
export const fetchGroupedValidationQueue = createAsyncThunk(
  'validation/fetchGroupedQueue',
  async (filters?: ValidationQueueFilters) => {
    const params = new URLSearchParams();

    if (filters?.status) params.append('status', filters.status);
    if (filters?.languageCode) params.append('language_code', filters.languageCode);
    if (filters?.page) params.append('page', filters.page.toString());
    if (filters?.pageSize) params.append('page_size', filters.pageSize.toString());

    const queryString = params.toString();
    const url = `${VALIDATION_BASE_URL}/queue/grouped${queryString ? `?${queryString}` : ''}`;

    const response = await axios.get(url, {
      headers: authorizationHeaders(),
    });

    // Transform snake_case API response to camelCase
    const data = response.data.data || {};
    const items = (data.items || []).map(transformGroupedQueueItem);

    return {
      items,
      total: data.total || 0,
      page: data.page || 1,
      pageSize: data.page_size || 20,
      totalPages: data.total_pages || 0,
    };
  }
);

/**
 * Fetch a specific validation item by ID
 *
 * Retrieves full validation data for a specific queue item.
 * Used when navigating directly to a validation item (e.g., from claimed items list).
 *
 * @param queueId - UUID of the validation queue item
 * @returns Promise resolving to the ValidationQueue item with full data
 */
export const fetchValidationById = createAsyncThunk(
  'validation/fetchById',
  async (queueId: string) => {
    const response = await axios.get(
      `${VALIDATION_BASE_URL}/${queueId}`,
      {
        headers: authorizationHeaders(),
      }
    );

    // Transform snake_case API response to camelCase
    const data = response.data.data;
    return transformValidationQueueItem(data);
  }
);

/**
 * Claim a validation item
 *
 * Claims a validation item from the queue for the current user.
 * Sets the item status to 'claimed' and starts the validation timer.
 * Returns full validation data including test case info and expected/actual values.
 *
 * @param itemId - ID of the validation queue item to claim
 * @returns Promise resolving to the claimed ValidationQueue item with full data
 */
export const claimValidation = createAsyncThunk(
  'validation/claim',
  async (itemId: string) => {
    const response = await axios.post(
      `${VALIDATION_BASE_URL}/${itemId}/claim`,
      {},
      {
        headers: authorizationHeaders(),
      }
    );

    // Transform snake_case API response to camelCase
    const data = response.data.data;
    return transformValidationQueueItem(data);
  }
);

/**
 * Submit validation decision
 *
 * Submits the human validator's decision for the current validation item.
 * Clears the current item and resets the timer upon success.
 *
 * @param validationData - Human validation decision data
 * @returns Promise resolving to success confirmation
 */
interface SubmitValidationParams {
  queueId: string;
  validation: HumanValidationCreate;
}

export const submitValidation = createAsyncThunk(
  'validation/submit',
  async ({ queueId, validation }: SubmitValidationParams) => {
    const payload = {
      validation_decision: validation.decision,
      feedback: validation.feedback,
      time_spent_seconds: validation.timeSpent,
    };
    const response = await axios.post(
      `${VALIDATION_BASE_URL}/${queueId}/submit`,
      payload,
      {
        headers: authorizationHeaders(),
      }
    );
    return response.data.data as Record<string, unknown>;
  }
);

/**
 * Release current validation
 *
 * Releases the currently claimed validation item back to the queue.
 * This allows another validator to claim it.
 *
 * @param itemId - ID of the validation queue item to release
 * @returns Promise resolving to success confirmation
 */
export const releaseValidation = createAsyncThunk(
  'validation/release',
  async (itemId: string) => {
    const response = await axios.post(
      `${VALIDATION_BASE_URL}/${itemId}/release`,
      {},
      {
        headers: authorizationHeaders(),
      }
    );
    return response.data.data as Record<string, unknown>;
  }
);

/**
 * Fetch validation statistics
 *
 * Retrieves current validation queue statistics including counts
 * by status and average metrics.
 *
 * @returns Promise resolving to ValidationStats object
 */
export const fetchValidationStats = createAsyncThunk(
  'validation/fetchStats',
  async () => {
    const response = await axios.get(`${VALIDATION_BASE_URL}/stats`, {
      headers: authorizationHeaders(),
    });
    return response.data.data as ValidationStats;
  }
);

/**
 * Fetch validator statistics summary
 *
 * Retrieves personal validator metrics, leaderboard data,
 * and accuracy trend information.
 *
 * @returns Promise resolving to ValidatorStatisticsPayload object
 */
export const fetchValidatorStatistics = createAsyncThunk(
  'validation/fetchValidatorStatistics',
  async () => {
    const response = await axios.get(`${VALIDATION_BASE_URL}/validators/stats`, {
      headers: authorizationHeaders(),
    });
    return response.data.data as ValidatorStatisticsPayload;
  }
);

// ============================================================================
// Slice Definition
// ============================================================================

/**
 * Validation slice
 *
 * Manages validation workflow state with reducers and async thunk handlers.
 */
const validationSlice = createSlice({
  name: 'validation',
  initialState,
  reducers: {
    /**
     * Set current validation item
     *
     * @param state - Current validation state
     * @param action - Payload containing validation item or null
     */
    setCurrentValidation(state, action: PayloadAction<ValidationQueue | null>) {
      state.current = action.payload;

      if (action.payload) {
        // Start timer when setting current validation
        state.timerStarted = Date.now();
        state.timeSpent = 0;
      } else {
        // Clear timer when clearing current validation
        state.timerStarted = null;
        state.timeSpent = 0;
      }
    },

    /**
     * Update validation timer
     *
     * Increments the time spent on current validation.
     * Should be called periodically (e.g., every second) while validating.
     *
     * @param state - Current validation state
     */
    updateValidationTimer(state) {
      if (state.timerStarted) {
        state.timeSpent = Math.floor((Date.now() - state.timerStarted) / 1000);
      }
    },

    /**
     * Clear validation error
     *
     * Resets the error state to null.
     *
     * @param state - Current validation state
     */
    clearError(state) {
      state.error = null;
    },

    /**
     * Reset validation state
     *
     * Resets the entire validation state to initial values.
     *
     * @param state - Current validation state
     */
    resetValidationState(state) {
      state.queue = [];
      state.groupedQueue = [];
      state.current = null;
      state.loading = false;
      state.error = null;
      state.stats = null;
      state.validatorSummary = null;
      state.validatorLeaderboard = [];
      state.validatorAccuracyTrend = [];
      state.timeSpent = 0;
      state.timerStarted = null;
    },
  },
  extraReducers: (builder) => {
    // ========================================================================
    // Fetch Validation Queue
    // ========================================================================
    builder.addCase(fetchValidationQueue.pending, (state) => {
      state.loading = true;
      state.error = null;
    });
    builder.addCase(fetchValidationQueue.fulfilled, (state, action) => {
      state.loading = false;
      state.queue = action.payload;
    });
    builder.addCase(fetchValidationQueue.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || 'Failed to fetch validation queue';
    });

    // ========================================================================
    // Fetch Grouped Validation Queue
    // ========================================================================
    builder.addCase(fetchGroupedValidationQueue.pending, (state) => {
      state.loading = true;
      state.error = null;
    });
    builder.addCase(fetchGroupedValidationQueue.fulfilled, (state, action) => {
      state.loading = false;
      state.groupedQueue = action.payload.items;
      state.groupedQueuePagination = {
        page: action.payload.page,
        pageSize: action.payload.pageSize,
        total: action.payload.total,
        totalPages: action.payload.totalPages,
      };
    });
    builder.addCase(fetchGroupedValidationQueue.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || 'Failed to fetch grouped validation queue';
    });

    // ========================================================================
    // Fetch Validation By ID
    // ========================================================================
    builder.addCase(fetchValidationById.pending, (state) => {
      state.loading = true;
      state.error = null;
    });
    builder.addCase(fetchValidationById.fulfilled, (state, action) => {
      state.loading = false;
      state.current = action.payload;
      // Start timer if not already started
      if (!state.timerStarted) {
        state.timerStarted = Date.now();
        state.timeSpent = 0;
      }
    });
    builder.addCase(fetchValidationById.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || 'Failed to fetch validation item';
    });

    // ========================================================================
    // Claim Validation
    // ========================================================================
    builder.addCase(claimValidation.pending, (state) => {
      state.loading = true;
      state.error = null;
    });
    builder.addCase(claimValidation.fulfilled, (state, action) => {
      state.loading = false;
      state.current = action.payload;
      state.timerStarted = Date.now();
      state.timeSpent = 0;

      // Remove claimed item from queue
      state.queue = state.queue.filter((item) => item.id !== action.payload.id);
    });
    builder.addCase(claimValidation.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || 'Failed to claim validation item';
    });

    // ========================================================================
    // Submit Validation
    // ========================================================================
    builder.addCase(submitValidation.pending, (state) => {
      state.loading = true;
      state.error = null;
    });
    builder.addCase(submitValidation.fulfilled, (state) => {
      state.loading = false;
      state.current = null;
      state.timerStarted = null;
      state.timeSpent = 0;
    });
    builder.addCase(submitValidation.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || 'Failed to submit validation';
    });

    // ========================================================================
    // Release Validation
    // ========================================================================
    builder.addCase(releaseValidation.pending, (state) => {
      state.loading = true;
      state.error = null;
    });
    builder.addCase(releaseValidation.fulfilled, (state) => {
      state.loading = false;
      state.current = null;
      state.timerStarted = null;
      state.timeSpent = 0;
    });
    builder.addCase(releaseValidation.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || 'Failed to release validation item';
    });

    // ========================================================================
    // Fetch Validation Stats
    // ========================================================================
    builder.addCase(fetchValidationStats.pending, (state) => {
      state.loading = true;
      state.error = null;
    });
    builder.addCase(fetchValidationStats.fulfilled, (state, action) => {
      state.loading = false;
      state.stats = action.payload;
    });
    builder.addCase(fetchValidationStats.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || 'Failed to fetch validation statistics';
    });

    // ========================================================================
    // Fetch Validator Statistics (personal/leaderboard/accuracy)
    // ========================================================================
    builder.addCase(fetchValidatorStatistics.pending, (state) => {
      state.loading = true;
      state.error = null;
    });
    builder.addCase(fetchValidatorStatistics.fulfilled, (state, action) => {
      state.loading = false;
      state.validatorSummary = action.payload.personal;
      state.validatorLeaderboard = action.payload.leaderboard;
      state.validatorAccuracyTrend = action.payload.accuracyTrend;
    });
    builder.addCase(fetchValidatorStatistics.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || 'Failed to fetch validator statistics';
    });
  },
});

// ============================================================================
// Exports
// ============================================================================

export const {
  setCurrentValidation,
  updateValidationTimer,
  clearError,
  resetValidationState,
} = validationSlice.actions;

export default validationSlice.reducer;
