/**
 * Pattern Analysis Configuration Types
 *
 * TypeScript types for AI-powered pattern discovery settings
 */

export interface PatternAnalysisConfig {
  id: string;
  tenant_id: string | null;  // null for global defaults (super_admin)
  lookback_days: number;
  min_pattern_size: number;
  similarity_threshold: number;
  enable_llm_analysis: boolean;
  llm_confidence_threshold: number;
  analysis_schedule: string;
  enable_auto_analysis: boolean;
  notify_on_new_patterns: boolean;
  notify_on_critical_patterns: boolean;
  defect_auto_creation_threshold: number;
  response_time_sla_ms: number;
  created_at: string;
  updated_at: string;
}

export interface PatternAnalysisConfigUpdate {
  lookback_days?: number;
  min_pattern_size?: number;
  similarity_threshold?: number;
  defect_auto_creation_threshold?: number;
  enable_llm_analysis?: boolean;
  llm_confidence_threshold?: number;
  analysis_schedule?: string;
  enable_auto_analysis?: boolean;
  notify_on_new_patterns?: boolean;
  notify_on_critical_patterns?: boolean;
  response_time_sla_ms?: number;
}

export interface ManualAnalysisRequest {
  overrides?: Record<string, any>;
}

export interface ManualAnalysisResponse {
  status: string;
  task_id: string;
  message: string;
}

export interface DefaultConfig {
  lookback_days: number;
  min_pattern_size: number;
  similarity_threshold: number;
  enable_llm_analysis: boolean;
  llm_confidence_threshold: number;
  analysis_schedule: string;
  enable_auto_analysis: boolean;
  notify_on_new_patterns: boolean;
  notify_on_critical_patterns: boolean;
  response_time_sla_ms: number;
}
