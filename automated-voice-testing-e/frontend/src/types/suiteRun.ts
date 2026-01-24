/**
 * Suite run domain types.
 */

export type SuiteRunStatus =
  | 'pending'
  | 'running'
  | 'completed'
  | 'failed'
  | 'cancelled';

export interface SuiteRunSummary {
  id: string;
  testSuiteId: string;
  suiteName?: string | null;
  status: SuiteRunStatus;
  startedAt: string | null;
  completedAt?: string | null;
  createdAt?: string | null;
  totalTests: number;
  passedTests: number;
  failedTests: number;
  skippedTests: number;
  languageCode?: string | null;
  is_categorical?: boolean;
  category_name?: string | null;
}

export interface SuiteRunListItem {
  id: string;
  suiteName?: string | null;
  testSuiteId: string;
  status: string;
  startedAt: string | null;
  completedAt?: string | null;
  createdAt?: string | null;
  totalTests: number;
  passedTests: number;
  failedTests: number;
  skippedTests: number;
  languageCode?: string | null;
}

export interface SuiteRunListResponse {
  total: number;
  runs: SuiteRunSummary[];
  items: SuiteRunListItem[];
}

export interface SuiteRunListParams {
  languageCode?: string | null;
  limit?: number;
}

export interface SuiteRunDetail extends SuiteRunSummary {
  createdAt: string;
  triggerType?: string | null;
}

/**
 * Step execution within a multi-turn scenario
 */
export interface StepExecutionDetail {
  id: string;
  stepOrder: number;
  userUtterance: string;
  aiResponse?: string | null;
  transcription?: string | null;
  commandKind?: string | null;
  confidenceScore?: number | null;
  validationPassed?: boolean | null;
  validationDetails?: ValidationDetails | null;
  responseTimeMs?: number | null;
  audioDataUrls?: Record<string, string> | null; // Map of language codes to input audio URLs
  responseAudioUrls?: Record<string, string> | null; // Map of language codes to response audio URLs
  executedAt?: string | null;
  errorMessage?: string | null;
}

/**
 * Entity validation result from backend
 */
export interface EntityValidationResult {
  passed: boolean;
  score: number;
  errors: string[];
  details: {
    expected: Record<string, unknown> | null;
    actual: Record<string, unknown> | null;
    matched: string[];
    missing: string[];
    mismatched: Array<{
      key: string;
      expected: unknown;
      actual: unknown;
    }>;
  };
}

/**
 * Houndify validation result
 */
export interface HoundifyResult {
  passed: boolean;
  commandKindMatch?: boolean;
  expectedCommandKind?: string;
  actualCommandKind?: string;
  asrConfidence?: number;
  expectedEntities?: unknown;
  actualEntities?: unknown;
  entityValidation?: EntityValidationResult | null;
  errors?: string[];
  /** Houndify validation latency in milliseconds */
  latency_ms?: number;
  /** Total parallel validation latency in milliseconds (wall-clock time) */
  total_validation_latency_ms?: number;
}

/**
 * LLM ensemble validation result
 */
export interface LLMEnsembleResult {
  finalScore: number;
  finalDecision: string;
  confidence: string;
  consensusType: string;
  evaluatorAScore?: number;
  evaluatorBScore?: number;
  evaluatorAReasoning?: string;
  evaluatorBReasoning?: string;
  curatorDecision?: string;
  curatorReasoning?: string;
  scoreDifference?: number;
  /** Total LLM pipeline latency in milliseconds */
  latency_ms?: number;
  /** Evaluator A latency in milliseconds */
  evaluatorALatencyMs?: number;
  /** Evaluator B latency in milliseconds */
  evaluatorBLatencyMs?: number;
  /** Curator latency in milliseconds (0 if not called) */
  curatorLatencyMs?: number;
  /** Total parallel validation latency in milliseconds (wall-clock time) */
  total_validation_latency_ms?: number;
}

/**
 * Validation details from both Houndify and LLM
 */
export interface ValidationDetails {
  houndifyPassed?: boolean | null;
  houndifyResult?: HoundifyResult | null;
  llmPassed?: boolean | null;
  ensembleResult?: LLMEnsembleResult | null;
  finalDecision?: string | null;
  reviewStatus?: string | null;
  errors?: string[];
  perLanguageResults?: Record<string, {
    passed: boolean;
    errors?: string[];
  }>;
}

export interface SuiteRunExecution {
  id: string;
  scriptId: string;
  scriptName?: string | null;
  languageCode?: string | null;
  status: string;
  responseSummary?: string | null;
  responseTimeSeconds?: number | null;
  confidenceScore?: number | null;
  validationResultId?: string | null;
  validationReviewStatus?: string | null;
  validationDetails?: ValidationDetails | null;
  pendingValidationQueueId?: string | null;
  latestHumanValidationId?: string | null;
  inputAudioUrl?: string | null;
  responseAudioUrl?: string | null;
  stepExecutions?: StepExecutionDetail[] | null;
  totalSteps?: number | null;
  completedSteps?: number | null;
  startedAt?: string | null;
  completedAt?: string | null;
}
