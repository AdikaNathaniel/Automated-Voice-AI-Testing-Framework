/**
 * Pattern Group types for LLM-enhanced edge case pattern recognition.
 */

export interface PatternGroup {
  id: string;
  name: string;
  description: string | null;
  pattern_type: string | null;
  severity: string;
  first_seen: string;
  last_seen: string;
  occurrence_count: number;
  status: string;
  suggested_actions: string[];
  pattern_metadata: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface PatternGroupListResponse {
  total: number;
  items: PatternGroup[];
}

export interface PatternGroupDetailResponse {
  pattern: PatternGroup;
  edge_cases: any[];
  total_edge_cases: number;
}

export interface PatternGroupCreate {
  name: string;
  description?: string | null;
  pattern_type?: string | null;
  severity?: string;
  status?: string;
  suggested_actions?: string[];
  pattern_metadata?: Record<string, any>;
}

export interface PatternGroupUpdate {
  name?: string;
  description?: string | null;
  pattern_type?: string | null;
  severity?: string;
  status?: string;
  suggested_actions?: string[];
  pattern_metadata?: Record<string, any>;
}
