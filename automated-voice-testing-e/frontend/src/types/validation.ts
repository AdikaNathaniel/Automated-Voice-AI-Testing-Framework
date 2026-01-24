/**
 * Validation TypeScript type definitions
 *
 * This module defines TypeScript interfaces and types for human validation workflow
 * including validation queue management, human validation decisions, validator
 * performance tracking, and related data structures.
 *
 * @module types/validation
 */

/**
 * ValidationStatus enum
 *
 * Status values for validation queue items.
 */
export enum ValidationStatus {
  PENDING = 'pending',
  CLAIMED = 'claimed',
  COMPLETED = 'completed',
}

/**
 * ValidationDecision enum
 *
 * Possible decisions a validator can make when reviewing a test result.
 * Values match the backend API expected values.
 */
export enum ValidationDecision {
  PASS = 'pass',
  FAIL = 'fail',
  EDGE_CASE = 'edge_case',
}

/**
 * AIValidationScores interface
 *
 * Contains validation scores from Houndify deterministic and LLM ensemble validation.
 *
 * Validation Architecture:
 * 1. Houndify Deterministic: CommandKind match, ASR confidence, response content patterns
 * 2. LLM Ensemble: Semantic understanding with multiple models
 * 3. Combined Decision: final_decision (pass/fail/uncertain), review_status
 */
export interface AIValidationScores {
  /** Houndify CommandKind match score (1.0 = match, 0.0 = mismatch) */
  commandKindMatchScore: number | null;

  /** ASR confidence from Houndify speech recognition (0-1) */
  asrConfidenceScore: number | null;

  /** Whether Houndify validation passed */
  houndifyPassed: boolean | null;

  /** Full Houndify validation result with response content details */
  houndifyResult: HoundifyValidationResult | null;

  /** Whether LLM ensemble validation passed */
  llmPassed: boolean | null;

  /** LLM ensemble result with judge details */
  ensembleResult: LLMEnsembleResult | null;

  /** Final combined decision (pass, fail, uncertain) */
  finalDecision: string | null;

  /** Review status determined by validation (auto_pass, needs_review, auto_fail) */
  reviewStatus: string | null;
}

/**
 * Response content validation result
 *
 * Contains detailed results of response content pattern matching.
 */
export interface ResponseContentResult {
  /** Overall result of response content validation */
  passed: boolean;

  /** Whether required phrases were found */
  contains_passed?: boolean;

  /** Whether forbidden phrases were absent */
  not_contains_passed?: boolean;

  /** Whether required regex patterns matched */
  regex_passed?: boolean;

  /** Whether forbidden regex patterns did not match */
  regex_not_match_passed?: boolean;

  /** Errors for missing required phrases */
  contains_errors?: string[];

  /** Errors for found forbidden phrases */
  not_contains_errors?: string[];

  /** Errors for unmatched required patterns */
  regex_errors?: string[];

  /** Errors for matched forbidden patterns */
  regex_not_match_errors?: string[];
}

/**
 * Entity validation result from backend
 */
export interface EntityValidationResult {
  /** Whether entity validation passed (all expected entities matched) */
  passed: boolean;

  /** Entity match score (0.0-1.0) */
  score: number;

  /** List of validation errors */
  errors: string[];

  /** Detailed entity comparison */
  details: {
    /** Expected entities */
    expected: Record<string, unknown> | null;
    /** Actual entities from response */
    actual: Record<string, unknown> | null;
    /** List of matched entity keys */
    matched: string[];
    /** List of missing entity keys */
    missing: string[];
    /** List of mismatched entities with expected/actual values */
    mismatched: Array<{
      key: string;
      expected: unknown;
      actual: unknown;
    }>;
  };
}

/**
 * HoundifyValidationResult interface
 *
 * Contains the detailed Houndify validation results.
 */
export interface HoundifyValidationResult {
  /** Whether Houndify validation passed */
  passed: boolean;

  /** List of validation errors if any */
  errors: string[];

  /** Validation method used (expected_outcome, expected_response) */
  method: string;

  /** Whether CommandKind matched expected */
  command_kind_match: boolean;

  /** Expected CommandKind from expected outcome */
  expected_command_kind?: string | null;

  /** Actual CommandKind from Houndify response */
  actual_command_kind?: string | null;

  /** ASR confidence score (0-1) */
  asr_confidence: number | null;

  /** Minimum required ASR confidence threshold */
  expected_asr_confidence_min?: number | null;

  /** Composite validation score for deterministic checks (0-1) */
  validation_score: number;

  /** ID of the expected outcome if used */
  expected_outcome_id: string | null;

  /** Response content validation result (if performed) */
  response_content_result?: ResponseContentResult | null;

  /** Entity validation result from backend */
  entity_validation?: EntityValidationResult | null;

  /** Expected entities from expected outcome */
  expected_entities?: Record<string, unknown> | null;

  /** Actual entities extracted from response */
  actual_entities?: Record<string, unknown> | null;

  /** Houndify validation latency in milliseconds */
  latency_ms?: number;

  /** Total parallel validation latency in milliseconds (wall-clock time) */
  total_validation_latency_ms?: number;
}

/**
 * LLMEnsembleResult interface
 *
 * Contains the LLM ensemble evaluation results from the three-stage pipeline.
 * Matches the PipelineResult.to_dict() output from the backend.
 */
export interface LLMEnsembleResult {
  /** Final consensus decision (pass, fail, needs_review) */
  final_decision: string;

  /** Final weighted score (0.0-1.0) */
  final_score: number;

  /** Confidence level (high, medium, low) */
  confidence: string;

  /** Evaluator A score (0.0-1.0) - typically Gemini */
  evaluator_a_score: number;

  /** Evaluator B score (0.0-1.0) - typically GPT */
  evaluator_b_score: number;

  /** Evaluator A reasoning */
  evaluator_a_reasoning: string | null;

  /** Evaluator B reasoning */
  evaluator_b_reasoning: string | null;

  /** Curator decision (when called for tie-breaking) */
  curator_decision: string | null;

  /** Curator reasoning (when called for tie-breaking) */
  curator_reasoning: string | null;

  /** Score difference between evaluators */
  score_difference: number;

  /** Consensus type: high_consensus, curator_resolved, human_review */
  consensus_type: string;

  /** Total pipeline latency in milliseconds */
  latency_ms: number;

  /** Evaluator A latency in milliseconds */
  evaluator_a_latency_ms: number;

  /** Evaluator B latency in milliseconds */
  evaluator_b_latency_ms: number;

  /** Curator latency in milliseconds (0 if not called) */
  curator_latency_ms: number;

  /** Total parallel validation latency in milliseconds (wall-clock time) */
  total_validation_latency_ms?: number;
}

/**
 * LLMJudgeResult interface
 *
 * Contains the result from a single LLM judge.
 */
export interface LLMJudgeResult {
  /** Judge ID */
  judge_id: string;

  /** Judge name */
  judge_name: string;

  /** LLM provider (openai, anthropic, google) */
  provider: string;

  /** Model name */
  model: string;

  /** Weight of this judge (0-1) */
  weight: number;

  /** Judge's decision (pass, fail, uncertain) */
  decision: string;

  /** Overall score from this judge (0-10) */
  overall_score: number;

  /** Individual criterion scores */
  scores: {
    relevance: number;
    correctness: number;
    completeness: number;
    tone: number;
    entity_accuracy: number;
  };

  /** Judge's reasoning */
  reasoning: string;

  /** Response latency in milliseconds */
  latency_ms: number;
}

/**
 * ValidationHistoryEntry interface
 *
 * Represents a single human validation decision in the history.
 */
export interface ValidationHistoryEntry {
  /** Unique identifier for this validation record */
  id: string;

  /** ID of the validator */
  validatorId: string | null;

  /** Display name of the validator */
  validatorName: string | null;

  /** Decision made (pass, fail, edge_case) */
  decision: string;

  /** Feedback/notes provided by validator */
  feedback: string | null;

  /** Time spent validating in seconds */
  timeSpentSeconds: number | null;

  /** Whether this was a second opinion review */
  isSecondOpinion: boolean;

  /** When the validator claimed this item */
  claimedAt: string | null;

  /** When the validation was submitted */
  submittedAt: string | null;

  /** Creation timestamp */
  createdAt: string | null;
}

/**
 * ValidationQueue interface
 *
 * Represents a validation task in the queue for human review.
 * Items with confidence scores between 40-75% are automatically added to this queue.
 */
export interface ValidationQueue {
  /** Unique identifier for the queue item */
  id: string;

  /** ID of the validation result that needs review */
  validationResultId: string;

  /** Priority level (calculated from confidence score, lower confidence = higher priority) */
  priority: number;

  /** Confidence score from automated validation (40-75%) */
  confidenceScore: number;

  /** Language code for the test case (e.g., 'en', 'es', 'fr') */
  languageCode: string;

  /** Current status of the validation queue item */
  status: ValidationStatus;

  /** ID of the validator who claimed this item (null if unclaimed) */
  claimedBy: string | null;

  /** Timestamp when the item was claimed (null if unclaimed) */
  claimedAt: string | null;

  /** Creation timestamp */
  createdAt?: string;

  /** Last update timestamp */
  updatedAt?: string;

  /** Descriptive test case name */
  testCaseName?: string;

  /** Input text or transcript evaluated */
  inputText?: string;

  /** Expected Houndify CommandKind (e.g., WeatherCommand, MusicCommand) */
  expectedCommandKind?: string;

  /** Actual Houndify CommandKind from response */
  actualCommandKind?: string;

  /** Expected entities payload */
  expectedEntities?: unknown;

  /** Actual entities payload */
  actualEntities?: unknown;

  /** Entity validation result from backend */
  entityValidation?: EntityValidationResult | null;

  /** Expected response text or payload */
  expectedResponse?: unknown;

  /** Actual response text or payload */
  actualResponse?: unknown;

  /** Conversational context */
  context?: string | null;

  /** URL to input audio file (if available) */
  inputAudioUrl?: string | null;

  /** URL to response audio file (if available) */
  responseAudioUrl?: string | null;

  /** AI validation scores (detailed breakdown) */
  aiScores?: AIValidationScores;

  /** Human validation decision (if completed) */
  humanValidationDecision?: string | null;

  /** Human validation feedback/notes (if completed) */
  humanValidationFeedback?: string | null;

  /** Human validation submission timestamp (if completed) */
  humanValidationSubmittedAt?: string | null;

  /** Name of the validator who submitted (if completed) */
  humanValidationValidatorName?: string | null;

  /** Full validation history (all validators' decisions) */
  validationHistory?: ValidationHistoryEntry[];
}

/**
 * StepValidation interface
 *
 * Represents a single step validation within a multi-turn execution.
 */
export interface StepValidation {
  /** Queue item ID */
  queueId: string;

  /** Validation result ID */
  validationResultId: string;

  /** Step execution ID */
  stepExecutionId: string;

  /** Step order in the scenario */
  stepOrder: number;

  /** User utterance for this step */
  userUtterance: string;

  /** Confidence score for this step (0.0-1.0) */
  confidenceScore: number | null;

  /** Review status (auto_pass, needs_review, auto_fail) */
  reviewStatus: string;

  /** Queue status (pending, claimed, completed) */
  queueStatus: string;

  /** Priority level (1-10, 1=highest) */
  priority: number;

  /** Language code */
  languageCode: string | null;

  /** Creation timestamp */
  createdAt: string;
}

/**
 * GroupedValidationQueue interface
 *
 * Represents validation queue items grouped by multi-turn execution.
 * This allows validators to see all steps from a single execution together.
 */
export interface GroupedValidationQueue {
  /** Multi-turn execution ID */
  executionId: string;

  /** Scenario name */
  scenarioName: string;

  /** Scenario ID */
  scenarioId: string;

  /** Total number of steps in execution */
  totalSteps: number;

  /** Number of steps needing review */
  stepsNeedingReview: number;

  /** Average confidence score across all steps (0.0-1.0) */
  avgConfidence: number | null;

  /** Minimum confidence score (0.0-1.0) */
  minConfidence: number | null;

  /** Maximum confidence score (0.0-1.0) */
  maxConfidence: number | null;

  /** Overall status (needs_review, in_progress, completed) */
  status: string;

  /** Creation timestamp */
  createdAt: string;

  /** List of step validations */
  stepValidations: StepValidation[];
}

/**
 * HumanValidation interface
 *
 * Represents a human validator's decision and feedback on a test result.
 */
export interface HumanValidation {
  /** Unique identifier for the human validation record */
  id: string;

  /** ID of the validation result being reviewed */
  validationResultId: string;

  /** ID of the validator who made the decision */
  validatorId: string;

  /** Validator's decision (pass, fail, edge_case) */
  decision: ValidationDecision;

  /** Optional feedback or notes from the validator */
  feedback: string | null;

  /** Time spent on validation in seconds */
  timeSpent: number;

  /** Creation timestamp */
  createdAt?: string;

  /** Last update timestamp */
  updatedAt?: string;
}

/**
 * ValidatorPerformance interface
 *
 * Tracks performance metrics for a validator on a specific date.
 */
export interface ValidatorPerformance {
  /** Unique identifier for the performance record */
  id?: string;

  /** ID of the validator */
  validatorId: string;

  /** Date for this performance record (ISO 8601 date string) */
  date: string;

  /** Number of validations completed on this date */
  validationsCompleted: number;

  /** Agreement rate with peer validators (0-100%) */
  agreementWithPeers: number;

  /** Agreement rate with final/consensus decisions (0-100%) */
  agreementWithFinal: number;

  /** Average time spent per validation in seconds */
  averageTimeSpent?: number;

  /** Creation timestamp */
  createdAt?: string;

  /** Last update timestamp */
  updatedAt?: string;
}

/**
 * Throughput Metrics interface
 *
 * Validation throughput metrics for various time windows.
 */
export interface ThroughputMetrics {
  /** Validations completed in the last hour */
  last_hour: number;

  /** Validations completed in the last 24 hours */
  last_24_hours: number;

  /** Validations completed in the last 7 days */
  last_7_days: number;

  /** Average validations completed per hour (based on 7-day data) */
  avg_per_hour: number;
}

/**
 * SLA Metrics interface
 *
 * Service Level Agreement metrics for validation queue processing times.
 */
export interface SLAMetrics {
  /** Average time from pending to claimed (in seconds) */
  avg_time_to_claim_seconds: number | null;

  /** Average time from claimed to completed (in seconds) */
  avg_time_to_complete_seconds: number | null;

  /** Average total time from pending to completed (in seconds) */
  avg_total_time_seconds: number | null;
}

/**
 * ValidationStats interface
 *
 * Summary statistics for the validation queue.
 * Note: Uses camelCase to match backend API response format.
 */
export interface ValidationStats {
  /** Pending count (pending queue items) */
  pendingCount: number;

  /** Claimed count (in-progress items) */
  claimedCount: number;

  /** Completed count */
  completedCount: number;

  /** Total queue items */
  totalCount?: number;

  /** Average confidence score of pending items */
  averageConfidence?: number;

  /** Oldest pending item age in minutes */
  oldestPendingAge?: number;

  /** Priority distribution for pending items (priority level -> count) */
  priorityDistribution?: Record<string, number>;

  /** Language distribution (language code -> count) */
  languageDistribution?: Record<string, number>;

  /** Throughput metrics (validations processed per time window) */
  throughput?: ThroughputMetrics;

  /** SLA metrics (processing time averages) */
  sla?: SLAMetrics;
}

/**
 * ValidatorPersonalStats interface
 *
 * Aggregated statistics for the currently authenticated validator.
 */
export interface ValidatorPersonalStats {
  /** Total validations completed by the validator */
  completedValidations: number;

  /** Total approvals recorded by the validator */
  approvals: number;

  /** Total rejections recorded by the validator */
  rejections: number;

  /** Overall accuracy (agreement rate) expressed as 0-1 float */
  accuracy: number;

  /** Average time spent per validation in seconds */
  averageTimeSeconds: number;

  /** Current consecutive days streak */
  currentStreakDays: number;
}

/**
 * ValidatorLeaderboardEntry interface
 *
 * Represents a leaderboard row summarizing a validator.
 */
export interface ValidatorLeaderboardEntry {
  /** Numeric rank within the leaderboard */
  rank: number;

  /** Unique identifier of the validator */
  validatorId: string;

  /** Display name shown in the leaderboard */
  displayName: string;

  /** Total completed validations */
  completedValidations: number;

  /** Accuracy (agreement rate) expressed as 0-1 float */
  accuracy: number;

  /** Average time spent per validation in seconds */
  averageTimeSeconds?: number;
}

/**
 * ValidatorAccuracyPoint interface
 *
 * Represents a historical accuracy data point for trend charts.
 */
export interface ValidatorAccuracyPoint {
  /** ISO-8601 date string for this data point */
  date: string;

  /** Accuracy (agreement rate) expressed as 0-1 float */
  accuracy: number;

  /** Number of validations contributing to this accuracy */
  validations: number;
}

/**
 * ValidatorStatisticsPayload interface
 *
 * Combined data payload for validator statistics page.
 */
export interface ValidatorStatisticsPayload {
  /** Personal stats for current validator */
  personal: ValidatorPersonalStats;

  /** Leaderboard entries */
  leaderboard: ValidatorLeaderboardEntry[];

  /** Accuracy trend over time */
  accuracyTrend: ValidatorAccuracyPoint[];
}

/**
 * ValidationQueue Create type
 *
 * Data required to create a new validation queue item.
 */
export interface ValidationQueueCreate {
  /** ID of the validation result that needs review */
  validationResultId: string;

  /** Priority level */
  priority: number;

  /** Confidence score from automated validation */
  confidenceScore: number;

  /** Language code for the test case */
  languageCode: string;
}

/**
 * HumanValidation Create type
 *
 * Data required to submit a human validation decision.
 */
export interface HumanValidationCreate {
  /** ID of the validation result being reviewed */
  validationResultId: string;

  /** Validator's decision - must be 'pass', 'fail', or 'edge_case' */
  decision: 'pass' | 'fail' | 'edge_case';

  /** Optional feedback or notes */
  feedback?: string;

  /** Time spent on validation in seconds */
  timeSpent: number;
}

/**
 * Validation Queue Filters interface
 *
 * Available filters for validation queue queries.
 */
export interface ValidationQueueFilters {
  /** Filter by status */
  status?: ValidationStatus;

  /** Filter by language code */
  languageCode?: string;

  /** Filter by minimum priority */
  minPriority?: number;

  /** Filter by maximum priority */
  maxPriority?: number;

  /** Filter by validator ID (claimed items) */
  validatorId?: string;

  /** Page number (1-indexed) */
  page?: number;

  /** Number of items per page */
  pageSize?: number;
}
