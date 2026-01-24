/**
 * CI/CD Configuration Types
 *
 * Types for webhook-to-test-suite mapping configuration
 */

export type CICDProvider = 'github' | 'gitlab' | 'jenkins';

export interface ProviderBranchFilter {
  enabled: boolean;
  branches: string[];
  exclude_branches: string[];
}

export interface ProviderEventFilter {
  push: boolean;
  pull_request: boolean;
  workflow_run: boolean;
  deployment: boolean;
}

export interface ProviderConfig {
  enabled: boolean;
  webhook_secret?: string;
  webhook_secret_set: boolean;
  suite_id: string | null;
  suite_name: string | null;
  scenario_ids: string[];
  branch_filter: ProviderBranchFilter;
  event_filter: ProviderEventFilter;
  run_regression_tests: boolean;
  regression_suite_ids: string[];
}

export interface CICDConfig {
  is_configured: boolean;
  webhook_url: string;
  webhook_token: string;
  default_suite_id: string | null;
  default_suite_name: string | null;
  providers: Record<CICDProvider, ProviderConfig>;
  last_updated: string | null;
}

export interface CICDConfigUpdatePayload {
  default_suite_id?: string | null;
  providers: Partial<Record<CICDProvider, Partial<ProviderConfig>>>;
}

export interface WebhookTestResult {
  success: boolean;
  message: string;
  provider: string;
  details?: {
    issues?: string[];
    suite_id?: string;
    webhook_secret_set?: boolean;
    branch_filter_enabled?: boolean;
  };
}

export interface WebhookInstructions {
  title: string;
  steps: string[];
  webhook_url: string;
  content_type: string;
  events: string[];
  docs_url: string;
}

export interface CICDConfigState {
  config: CICDConfig | null;
  loading: boolean;
  saving: boolean;
  testing: boolean;
  error: string | null;
  success: string | null;
  instructions: WebhookInstructions | null;
  testResult: WebhookTestResult | null;
}

// Default provider configuration
export const defaultProviderConfig: ProviderConfig = {
  enabled: false,
  webhook_secret_set: false,
  suite_id: null,
  suite_name: null,
  scenario_ids: [],
  branch_filter: {
    enabled: false,
    branches: [],
    exclude_branches: [],
  },
  event_filter: {
    push: true,
    pull_request: false,
    workflow_run: true,
    deployment: true,
  },
  run_regression_tests: false,
  regression_suite_ids: [],
};

// Default CI/CD configuration
export const defaultCICDConfig: CICDConfig = {
  is_configured: false,
  webhook_url: '',
  webhook_token: '',
  default_suite_id: null,
  default_suite_name: null,
  providers: {
    github: { ...defaultProviderConfig },
    gitlab: { ...defaultProviderConfig },
    jenkins: { ...defaultProviderConfig },
  },
  last_updated: null,
};
