/**
 * TypeScript types for LLM Provider Configuration.
 */

export interface LLMProviderConfig {
  id: string;
  tenant_id: string | null;
  provider: 'openai' | 'anthropic' | 'google';
  display_name: string;
  default_model: string | null;
  is_active: boolean;
  is_default: boolean;
  temperature: number;
  max_tokens: number;
  timeout_seconds: number;
  config: Record<string, unknown> | null;
  api_key_preview: string | null;
  created_at: string;
  updated_at: string;
}

export interface LLMProviderConfigCreate {
  provider: 'openai' | 'anthropic' | 'google';
  display_name: string;
  api_key: string;
  default_model?: string | null;
  is_active?: boolean;
  is_default?: boolean;
  temperature?: number;
  max_tokens?: number;
  timeout_seconds?: number;
  config?: Record<string, unknown> | null;
}

export interface LLMProviderConfigUpdate {
  display_name?: string;
  api_key?: string;
  default_model?: string | null;
  is_active?: boolean;
  is_default?: boolean;
  temperature?: number;
  max_tokens?: number;
  timeout_seconds?: number;
  config?: Record<string, unknown> | null;
}

export interface LLMProviderConfigListResponse {
  total: number;
  items: LLMProviderConfig[];
}

export interface LLMProviderSummary {
  provider: string;
  display_name: string;
  default_model: string;
  is_configured: boolean;
  is_active: boolean;
}

export interface LLMProvidersSummaryResponse {
  providers: LLMProviderSummary[];
  total_configured: number;
  total_active: number;
}

export interface TestProviderRequest {
  provider: string;
  api_key?: string;
  model?: string;
}

export interface TestProviderResponse {
  success: boolean;
  provider: string;
  model: string;
  message: string;
  latency_ms: number | null;
  error: string | null;
}

// Provider display info
export const PROVIDER_INFO: Record<string, { name: string; icon: string; description: string; defaultModel: string }> = {
  openai: {
    name: 'OpenAI',
    icon: '🤖',
    description: 'GPT-4o and other OpenAI models for evaluation',
    defaultModel: 'gpt-4o',
  },
  anthropic: {
    name: 'Anthropic',
    icon: '🧠',
    description: 'Claude Sonnet 4.5 and other Anthropic models',
    defaultModel: 'claude-sonnet-4-5-20250929',
  },
  google: {
    name: 'Google',
    icon: '🔮',
    description: 'Gemini 1.5 Pro and other Google AI models',
    defaultModel: 'gemini-1.5-pro',
  },
};
