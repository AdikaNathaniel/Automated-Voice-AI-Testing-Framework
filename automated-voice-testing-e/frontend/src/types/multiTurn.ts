/**
 * TypeScript types for multi-turn conversation scenarios.
 * 
 * Corresponds to backend models:
 * - ScenarioScript
 * - ScenarioStep
 * - MultiTurnExecution
 * - StepExecution
 */

export interface LanguageVariant {
  language_code: string;
  user_utterance: string;
}

export interface StepMetadata {
  is_single_turn?: boolean;
  primary_language?: string;
  language_variants?: LanguageVariant[];
  dialog_phase?: string;
  slot_to_collect?: string;
  [key: string]: any;
}

export interface ScenarioStep {
  id: string;
  script_id: string;
  step_order: number;
  user_utterance: string;
  step_metadata?: StepMetadata;
  follow_up_action?: string;
  created_at: string;
  updated_at: string;
}

export interface ScenarioScript {
  id: string;
  tenant_id?: string;
  name: string;
  description?: string;
  version?: string;
  is_active: boolean;
  validation_mode: 'houndify' | 'llm_ensemble' | 'hybrid';
  script_metadata?: Record<string, any>;
  noise_config?: NoiseConfig;  // Extracted from script_metadata
  created_by?: string;
  owner_id?: string;
  approval_status: 'draft' | 'pending_review' | 'approved' | 'rejected';
  reviewed_by?: string;
  reviewed_at?: string;
  review_notes?: string;
  steps?: ScenarioStep[];
  steps_count?: number;
  languages?: string[];  // Language codes available (e.g., ['en', 'es', 'fr'])
  created_at: string;
  updated_at: string;
}

export interface ConversationState {
  Domain?: string;
  TurnCount?: number;
  DialogPhase?: string;
  PendingSlots?: string[];
  CollectedSlots?: Record<string, any>;
  ConversationStateId?: string;
  ConversationStateTime?: number;
}

export interface StepExecution {
  id: string;
  multi_turn_execution_id: string;
  step_id: string;
  step_order: number;
  user_utterance: string;
  audio_data_urls?: Record<string, string>; // Map of language codes to audio URLs
  response_audio_url?: string; // TTS response audio from Houndify
  request_id: string;
  ai_response?: string;
  transcription?: string;
  command_kind?: string;
  confidence_score?: number;
  conversation_state_before?: ConversationState;
  conversation_state_after?: ConversationState;
  validation_passed: boolean;
  validation_details?: Record<string, any>;
  response_time_ms?: number;
  executed_at: string;
  error_message?: string;
}

export interface MultiTurnExecution {
  id: string;
  suite_run_id: string;
  script_id: string;
  scenario_name?: string;  // Name of the executed scenario
  user_id: string;
  conversation_state_id?: string;
  current_step_order: number;
  total_steps: number;
  status: 'pending' | 'in_progress' | 'completed' | 'failed' | 'cancelled';
  conversation_state?: ConversationState;
  started_at?: string;
  completed_at?: string;
  error_message?: string;
  all_steps_passed?: boolean;
  step_executions?: StepExecution[];
  created_at: string;
  updated_at: string;
}

export interface ExecuteScenarioRequest {
  script_id: string;
  language_codes?: string[]; // Optional list of language codes to execute (e.g., ["en-US", "fr-FR"])
}

export interface ExecuteScenarioResponse {
  script_id: string;
  suite_run_id: string;
  execution_id: string;
  status: string;
  total_steps: number;
  completed_steps: number;
  all_passed: boolean;
}

export interface GetExecutionResponse {
  execution_id: string;
  script_id: string;
  suite_run_id: string;
  status: string;
  current_step_order: number;
  total_steps: number;
  all_steps_passed: boolean;
  conversation_state?: ConversationState;
  started_at?: string;
  completed_at?: string;
  error_message?: string;
}

export interface GetStepsResponse {
  execution_id: string;
  total_steps: number;
  steps: StepExecution[];
}

export interface ListExecutionsParams {
  page?: number;
  page_size?: number;
  status?: string;
  script_id?: string;
}

export interface ScenarioScriptCreate {
  name: string;
  description?: string;
  version?: string;
  validation_mode?: 'houndify' | 'llm_ensemble' | 'hybrid';
  script_metadata?: Record<string, any>;
  steps?: ScenarioStepCreate[];
}

export interface ScenarioStepCreate {
  step_order: number;
  user_utterance: string;
  step_metadata?: Record<string, any>;
}

// Additional API Response Types for Service Layer

export interface ExecutionStatusResponse extends MultiTurnExecution {
  // The API returns the execution data directly, not wrapped in an "execution" field
}

export interface StepExecutionsResponse {
  execution_id: string;
  total_steps: number;
  steps: StepExecution[];
}

export interface ScenarioListResponse {
  scenarios: ScenarioScript[];
  total: number;
  page?: number;
  page_size?: number;
}

// Noise Configuration Types
export interface NoiseConfig {
  enabled: boolean;
  profile: string;
  snr_db?: number;
  randomize_snr: boolean;
  snr_variance: number;
}

export interface NoiseProfile {
  name: string;
  category: string;
  description?: string;
  default_snr_db: number;
  difficulty: 'easy' | 'medium' | 'hard' | 'very_hard' | 'extreme';
  estimated_wer_increase?: number;
}

export interface NoiseProfileListResponse {
  profiles: NoiseProfile[];
}
