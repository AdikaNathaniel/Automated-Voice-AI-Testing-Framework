/**
 * CI/CD Configuration Page
 *
 * User-friendly interface for configuring webhook-to-test-suite mappings.
 * Supports GitHub, GitLab, and Jenkins with provider-specific settings.
 */

import React, { useEffect, useState, useCallback } from 'react';
import { GitBranch } from 'lucide-react';
import { SiGithub, SiGitlab, SiJenkins } from 'react-icons/si';
import type { IconType } from 'react-icons';
import {
  getCICDConfig,
  updateCICDConfig,
  testWebhookConfig,
  getWebhookInstructions,
} from '../../services/cicdConfig.service';
import { getTestSuites, type TestSuite } from '../../services/testSuite.service';
import type {
  CICDConfig,
  CICDProvider,
  ProviderConfig,
  WebhookInstructions,
  WebhookTestResult,
} from '../../types/cicdConfig';
import { LoadingSpinner, ErrorState } from '../../components/common';

// Provider display information with brand icons
const PROVIDER_INFO: Record<CICDProvider, { name: string; icon: IconType; color: string; bgColor: string }> = {
  github: {
    name: 'GitHub',
    icon: SiGithub,
    color: 'text-[var(--color-content-primary)]',
    bgColor: 'bg-[var(--color-surface-inset)]'
  },
  gitlab: {
    name: 'GitLab',
    icon: SiGitlab,
    color: 'text-[var(--color-status-amber)]',
    bgColor: 'bg-[var(--color-status-amber-bg)]'
  },
  jenkins: {
    name: 'Jenkins',
    icon: SiJenkins,
    color: 'text-[var(--color-status-danger)]',
    bgColor: 'bg-[var(--color-status-danger-bg)]'
  },
};

const CICDConfig: React.FC = () => {
  // State
  const [config, setConfig] = useState<CICDConfig | null>(null);
  const [testSuites, setTestSuites] = useState<TestSuite[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [activeProvider, setActiveProvider] = useState<CICDProvider>('github');
  const [instructions, setInstructions] = useState<WebhookInstructions | null>(null);
  const [showInstructions, setShowInstructions] = useState(false);
  const [testResult, setTestResult] = useState<WebhookTestResult | null>(null);
  const [testing, setTesting] = useState(false);

  // Local form state for the active provider
  const [formState, setFormState] = useState<ProviderConfig | null>(null);
  const [webhookSecret, setWebhookSecret] = useState('');

  // Load config and test suites on mount
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        setError(null);

        const [configData, suitesData] = await Promise.all([
          getCICDConfig(),
          getTestSuites({ is_active: true }),
        ]);

        setConfig(configData);
        setTestSuites(suitesData.test_suites);

        // Initialize form state with active provider
        if (configData.providers[activeProvider]) {
          setFormState(configData.providers[activeProvider]);
        }
      } catch (err: unknown) {
        const message = err instanceof Error ? err.message : 'Failed to load configuration';
        setError(message);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  // Update form state when provider changes
  useEffect(() => {
    if (config?.providers[activeProvider]) {
      setFormState(config.providers[activeProvider]);
      setWebhookSecret('');
      setTestResult(null);
      setShowInstructions(false);
    }
  }, [activeProvider, config]);

  // Handle form field changes
  const handleFieldChange = useCallback((field: keyof ProviderConfig, value: unknown) => {
    setFormState(prev => prev ? { ...prev, [field]: value } : prev);
  }, []);

  // Handle branch filter changes
  const handleBranchFilterChange = useCallback((field: string, value: unknown) => {
    setFormState(prev => {
      if (!prev) return prev;
      return {
        ...prev,
        branch_filter: { ...prev.branch_filter, [field]: value },
      };
    });
  }, []);

  // Handle event filter changes
  const handleEventFilterChange = useCallback((field: string, value: boolean) => {
    setFormState(prev => {
      if (!prev) return prev;
      return {
        ...prev,
        event_filter: { ...prev.event_filter, [field]: value },
      };
    });
  }, []);

  // Save configuration
  const handleSave = async () => {
    if (!formState) return;

    try {
      setSaving(true);
      setError(null);
      setSuccess(null);

      const payload = {
        providers: {
          [activeProvider]: {
            ...formState,
            webhook_secret: webhookSecret || undefined,
          },
        },
      };

      const updatedConfig = await updateCICDConfig(payload);
      setConfig(updatedConfig);
      setFormState(updatedConfig.providers[activeProvider]);
      setWebhookSecret('');
      setSuccess('Configuration saved successfully');

      setTimeout(() => setSuccess(null), 3000);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to save configuration';
      setError(message);
    } finally {
      setSaving(false);
    }
  };

  // Test webhook configuration
  const handleTestWebhook = async () => {
    try {
      setTesting(true);
      setTestResult(null);

      const result = await testWebhookConfig(activeProvider);
      setTestResult(result);
    } catch (err: unknown) {
      setTestResult({
        success: false,
        message: err instanceof Error ? err.message : 'Test failed',
        provider: activeProvider,
      });
    } finally {
      setTesting(false);
    }
  };

  // Load setup instructions
  const handleShowInstructions = async () => {
    if (showInstructions) {
      setShowInstructions(false);
      return;
    }

    try {
      const instrData = await getWebhookInstructions(activeProvider);
      setInstructions(instrData);
      setShowInstructions(true);
    } catch (err) {
      console.error('Failed to load instructions:', err);
    }
  };

  // Copy webhook URL to clipboard
  const handleCopyWebhookUrl = () => {
    if (config?.webhook_url) {
      navigator.clipboard.writeText(config.webhook_url);
      setSuccess('Webhook URL copied to clipboard');
      setTimeout(() => setSuccess(null), 2000);
    }
  };

  if (loading) {
    return <LoadingSpinner message="Loading CI/CD Configuration..." />;
  }

  if (error && !config) {
    return <ErrorState message={error} variant="alert" />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-md">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-2xl font-bold text-[var(--color-content-primary)] flex items-center gap-3">
              <GitBranch className="w-6 h-6" style={{ color: '#2A6B6E' }} />
              CI/CD Configuration
            </h1>
            <p className="text-sm text-[var(--color-content-muted)] mt-1">
              Configure webhook triggers to automatically run test suites when code is pushed.
            </p>
          </div>
          <div className="flex items-center gap-2">
            {config?.is_configured && (
              <span className="px-3 py-1 text-xs font-semibold rounded-full bg-[var(--color-status-success-bg)] text-[var(--color-status-success)]">
                Active
              </span>
            )}
          </div>
        </div>

        {/* Webhook URL */}
        {config?.webhook_url && (
          <div className="mt-4 p-5 bg-gradient-to-r from-[var(--color-status-info-bg)] to-[var(--color-status-indigo-bg)] rounded-lg border border-[var(--color-status-info)]">
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <p className="text-sm font-semibold text-[var(--color-content-primary)]">
                    Webhook URL
                  </p>
                  <span className="px-2 py-0.5 text-xs font-medium rounded bg-[var(--color-status-info-bg)] text-[var(--color-status-info)]">
                    Unique
                  </span>
                </div>
                <div className="p-3 bg-[var(--color-surface-inset)] rounded border border-[var(--color-border-strong)] mb-2">
                  <p className="text-sm font-mono text-[var(--color-content-primary)] break-all">
                    {config.webhook_url}
                  </p>
                </div>
                <div className="flex items-start gap-2 text-xs text-[var(--color-status-amber)]">
                  <svg className="w-4 h-4 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                  <span>
                    Keep this URL secure. The token at the end is unique to your organization and grants access to trigger test runs.
                  </span>
                </div>
              </div>
              <button
                onClick={handleCopyWebhookUrl}
                className="px-4 py-2 text-sm font-medium rounded-lg bg-[var(--color-status-info)] text-white hover:opacity-90 transition-colors flex-shrink-0"
              >
                Copy URL
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Success/Error Messages */}
      {success && (
        <div className="bg-[var(--color-status-success-bg)] border border-[var(--color-status-success)] rounded-lg p-4">
          <p className="text-sm text-[var(--color-status-success)]">{success}</p>
        </div>
      )}
      {error && (
        <div className="bg-[var(--color-status-danger-bg)] border border-[var(--color-status-danger)] rounded-lg p-4">
          <p className="text-sm text-[var(--color-status-danger)]">{error}</p>
        </div>
      )}

      {/* Provider Tabs */}
      <div className="bg-[var(--color-surface-raised)] rounded-xl shadow-md overflow-hidden">
        <div className="flex border-b border-[var(--color-border-default)]">
          {(Object.keys(PROVIDER_INFO) as CICDProvider[]).map((provider) => {
            const info = PROVIDER_INFO[provider];
            const providerConfig = config?.providers[provider];
            const isActive = activeProvider === provider;

            return (
              <button
                key={provider}
                onClick={() => setActiveProvider(provider)}
                className={`flex-1 px-6 py-4 text-sm font-medium transition-colors relative ${
                  isActive
                    ? 'text-primary border-b-2 border-primary bg-primary/5'
                    : 'text-[var(--color-content-muted)] hover:text-[var(--color-content-secondary)]'
                }`}
              >
                <div className="flex items-center justify-center gap-2">
                  <span
                    className={`w-8 h-8 rounded-lg flex items-center justify-center ${info.bgColor}`}
                  >
                    <info.icon className={`w-5 h-5 ${info.color}`} />
                  </span>
                  <span>{info.name}</span>
                  {providerConfig?.enabled && (
                    <span className="w-2 h-2 rounded-full bg-[var(--color-status-success)]" />
                  )}
                </div>
              </button>
            );
          })}
        </div>

        {/* Provider Configuration Form */}
        {formState && (
          <div className="p-6 space-y-6">
            {/* Enable Toggle */}
            <div className="flex items-center justify-between p-4 bg-[var(--color-surface-inset)]/50 rounded-lg">
              <div>
                <h3 className="text-sm font-semibold text-[var(--color-content-primary)]">
                  Enable {PROVIDER_INFO[activeProvider].name} Integration
                </h3>
                <p className="text-xs text-[var(--color-content-muted)] mt-1">
                  Automatically run tests when webhooks are received from{' '}
                  {PROVIDER_INFO[activeProvider].name}
                </p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={formState.enabled}
                  onChange={(e) => handleFieldChange('enabled', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-[var(--color-accent-500)]/40 rounded-full peer bg-[var(--color-interactive-hover)] peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-[var(--color-border-default)] after:border after:rounded-full after:h-5 after:w-5 after:transition-all border-[var(--color-border-default)] peer-checked:bg-primary" />
              </label>
            </div>

            {formState.enabled && (
              <>
                {/* Test Suite Selection */}
                <div>
                  <label className="block text-sm font-semibold text-[var(--color-content-primary)] mb-2">
                    Test Suite to Run
                  </label>
                  <select
                    value={formState.suite_id || ''}
                    onChange={(e) => handleFieldChange('suite_id', e.target.value || null)}
                    className="w-full px-4 py-3 border border-[var(--color-border-default)] rounded-lg text-sm bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/10"
                  >
                    <option value="">Select a test suite...</option>
                    {testSuites.map((suite) => (
                      <option key={suite.id} value={suite.id}>
                        {suite.name}
                        {suite.category ? ` (${suite.category})` : ''}
                      </option>
                    ))}
                  </select>
                  <p className="text-xs text-[var(--color-content-muted)] mt-1">
                    This test suite will be executed when a webhook is received.
                  </p>
                </div>

                {/* Webhook Secret */}
                <div>
                  <label className="block text-sm font-semibold text-[var(--color-content-primary)] mb-2">
                    Webhook Secret
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="password"
                      value={webhookSecret}
                      onChange={(e) => setWebhookSecret(e.target.value)}
                      placeholder={
                        formState.webhook_secret_set
                          ? '••••••••••••••••'
                          : 'Enter webhook secret...'
                      }
                      className="flex-1 px-4 py-3 border border-[var(--color-border-default)] rounded-lg text-sm bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/10"
                    />
                    {formState.webhook_secret_set && (
                      <span className="flex items-center px-3 text-xs font-medium text-[var(--color-status-success)] bg-[var(--color-status-success-bg)] rounded-lg">
                        Secret Set
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-[var(--color-content-muted)] mt-1">
                    Used to verify webhook signatures. Must match the secret configured in{' '}
                    {PROVIDER_INFO[activeProvider].name}.
                  </p>
                </div>

                {/* Event Filters */}
                <div>
                  <label className="block text-sm font-semibold text-[var(--color-content-primary)] mb-3">
                    Trigger Events
                  </label>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    {[
                      { key: 'push', label: 'Push Events' },
                      { key: 'pull_request', label: 'Pull Requests' },
                      { key: 'workflow_run', label: 'Workflow Runs' },
                      { key: 'deployment', label: 'Deployments' },
                    ].map(({ key, label }) => (
                      <label
                        key={key}
                        className="flex items-center gap-2 p-3 bg-[var(--color-surface-inset)]/50 rounded-lg cursor-pointer hover:bg-[var(--color-interactive-hover)]/70 transition-colors"
                      >
                        <input
                          type="checkbox"
                          checked={formState.event_filter[key as keyof typeof formState.event_filter]}
                          onChange={(e) => handleEventFilterChange(key, e.target.checked)}
                          className="w-4 h-4 text-primary bg-[var(--color-interactive-hover)] border-[var(--color-border-default)] rounded focus:ring-primary"
                        />
                        <span className="text-sm text-[var(--color-content-secondary)]">{label}</span>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Branch Filters */}
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <label className="text-sm font-semibold text-[var(--color-content-primary)]">
                      Branch Filtering
                    </label>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={formState.branch_filter.enabled}
                        onChange={(e) =>
                          handleBranchFilterChange('enabled', e.target.checked)
                        }
                        className="sr-only peer"
                      />
                      <div className="w-9 h-5 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/20 rounded-full peer bg-[var(--color-interactive-hover)] peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-[var(--color-border-default)] after:border after:rounded-full after:h-4 after:w-4 after:transition-all border-[var(--color-border-default)] peer-checked:bg-primary" />
                    </label>
                  </div>

                  {formState.branch_filter.enabled && (
                    <div className="space-y-3 p-4 bg-[var(--color-surface-inset)]/50 rounded-lg">
                      <div>
                        <label className="block text-xs font-medium text-[var(--color-content-secondary)] mb-1">
                          Include Branches (comma-separated)
                        </label>
                        <input
                          type="text"
                          value={formState.branch_filter.branches.join(', ')}
                          onChange={(e) =>
                            handleBranchFilterChange(
                              'branches',
                              e.target.value.split(',').map((b) => b.trim()).filter(Boolean)
                            )
                          }
                          placeholder="main, develop, release/*"
                          className="w-full px-3 py-2 border border-[var(--color-border-default)] rounded-lg text-sm bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/10"
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-[var(--color-content-secondary)] mb-1">
                          Exclude Branches (comma-separated)
                        </label>
                        <input
                          type="text"
                          value={formState.branch_filter.exclude_branches.join(', ')}
                          onChange={(e) =>
                            handleBranchFilterChange(
                              'exclude_branches',
                              e.target.value.split(',').map((b) => b.trim()).filter(Boolean)
                            )
                          }
                          placeholder="feature/*, hotfix/*"
                          className="w-full px-3 py-2 border border-[var(--color-border-default)] rounded-lg text-sm bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/10"
                        />
                      </div>
                    </div>
                  )}
                </div>

                {/* Regression Tests Option */}
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 bg-[var(--color-surface-inset)]/50 rounded-lg">
                    <div>
                      <h3 className="text-sm font-semibold text-[var(--color-content-primary)]">
                        Run Regression Tests on Deployments
                      </h3>
                      <p className="text-xs text-[var(--color-content-muted)] mt-1">
                        Additionally run regression test suites when deployment events are received.
                      </p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={formState.run_regression_tests}
                        onChange={(e) =>
                          handleFieldChange('run_regression_tests', e.target.checked)
                        }
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-[var(--color-accent-500)]/40 rounded-full peer bg-[var(--color-interactive-hover)] peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-[var(--color-border-default)] after:border after:rounded-full after:h-5 after:w-5 after:transition-all border-[var(--color-border-default)] peer-checked:bg-primary" />
                    </label>
                  </div>

                  {/* Regression Suite Selection (shown when enabled) */}
                  {formState.run_regression_tests && (
                    <div className="p-4 bg-[var(--color-surface-raised)] rounded-lg border border-[var(--color-border-default)]">
                      <label className="block text-sm font-semibold text-[var(--color-content-primary)] mb-2">
                        Regression Test Suites
                      </label>
                      <div className="space-y-2 max-h-60 overflow-y-auto">
                        {testSuites.length === 0 ? (
                          <p className="text-sm text-[var(--color-content-muted)] italic">
                            No test suites available. Create a test suite first.
                          </p>
                        ) : (
                          testSuites.map((suite) => (
                            <label
                              key={suite.id}
                              className="flex items-center gap-3 p-3 rounded-lg border border-[var(--color-border-default)] hover:bg-[var(--color-interactive-hover)]/50 cursor-pointer transition-colors"
                            >
                              <input
                                type="checkbox"
                                checked={formState.regression_suite_ids.includes(suite.id)}
                                onChange={(e) => {
                                  const newIds = e.target.checked
                                    ? [...formState.regression_suite_ids, suite.id]
                                    : formState.regression_suite_ids.filter((id) => id !== suite.id);
                                  handleFieldChange('regression_suite_ids', newIds);
                                }}
                                className="w-4 h-4 text-primary bg-[var(--color-surface-raised)] border-[var(--color-border-strong)] rounded focus:ring-primary focus:ring-2"
                              />
                              <div className="flex-1">
                                <p className="text-sm font-medium text-[var(--color-content-primary)]">
                                  {suite.name}
                                </p>
                                {suite.category && (
                                  <p className="text-xs text-[var(--color-content-muted)]">
                                    {suite.category}
                                  </p>
                                )}
                              </div>
                            </label>
                          ))
                        )}
                      </div>
                      <p className="text-xs text-[var(--color-content-muted)] mt-2">
                        Selected regression suites will run only on deployment events. Select one or more comprehensive test suites for thorough validation.
                      </p>
                      {formState.event_filter.deployment && (
                        <div className="mt-3 p-3 bg-[var(--color-status-info-bg)] border border-[var(--color-status-info)] rounded-lg">
                          <p className="text-xs text-[var(--color-status-info)]">
                            💡 <strong>Tip:</strong> You have 'deployment' enabled in your event filter above. This means the main test suite will also run on deployments. Consider unchecking 'deployment' above if you only want regression tests to run on deployments.
                          </p>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </>
            )}

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-3 pt-4 border-t border-[var(--color-border-default)]">
              <button
                onClick={handleSave}
                disabled={saving}
                className="flex-1 px-6 py-3 text-sm font-semibold rounded-lg text-white bg-gradient-to-r from-[#2A6B6E] to-[#11484D] hover:from-[#4a9a9d] hover:to-[#0d3a3d] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {saving ? 'Saving...' : 'Save Configuration'}
              </button>

              {formState.enabled && (
                <>
                  <button
                    onClick={handleTestWebhook}
                    disabled={testing}
                    className="px-6 py-3 text-sm font-semibold rounded-lg border border-[var(--color-border-strong)] text-[var(--color-content-secondary)] hover:bg-[var(--color-interactive-hover)] transition-colors disabled:opacity-50"
                  >
                    {testing ? 'Testing...' : 'Test Configuration'}
                  </button>

                  <button
                    onClick={handleShowInstructions}
                    className="px-6 py-3 text-sm font-semibold rounded-lg border border-[var(--color-border-strong)] text-[var(--color-content-secondary)] hover:bg-[var(--color-interactive-hover)] transition-colors"
                  >
                    {showInstructions ? 'Hide' : 'Setup'} Instructions
                  </button>
                </>
              )}
            </div>

            {/* Test Result */}
            {testResult && (
              <div
                className={`p-4 rounded-lg ${
                  testResult.success
                    ? 'bg-[var(--color-status-success-bg)] border border-[var(--color-status-success)]'
                    : 'bg-[var(--color-status-danger-bg)] border border-[var(--color-status-danger)]'
                }`}
              >
                <div className="flex items-start gap-3">
                  <span
                    className={`text-lg ${
                      testResult.success ? 'text-[var(--color-status-success)]' : 'text-[var(--color-status-danger)]'
                    }`}
                  >
                    {testResult.success ? '✓' : '✗'}
                  </span>
                  <div>
                    <p
                      className={`text-sm font-medium ${
                        testResult.success
                          ? 'text-[var(--color-status-success)]'
                          : 'text-[var(--color-status-danger)]'
                      }`}
                    >
                      {testResult.message}
                    </p>
                    {testResult.details?.issues && testResult.details.issues.length > 0 && (
                      <ul className="mt-2 text-sm text-[var(--color-status-danger)] list-disc list-inside">
                        {testResult.details.issues.map((issue, idx) => (
                          <li key={idx}>{issue}</li>
                        ))}
                      </ul>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Setup Instructions */}
            {showInstructions && instructions && (
              <div className="p-4 bg-[var(--color-status-info-bg)] border border-[var(--color-status-info)] rounded-lg">
                <h4 className="text-sm font-semibold text-[var(--color-status-info)] mb-3">
                  {instructions.title}
                </h4>
                <ol className="space-y-2">
                  {instructions.steps.map((step, idx) => (
                    <li key={idx} className="flex gap-2 text-sm text-[var(--color-status-info)]">
                      <span className="font-semibold text-[var(--color-status-info)]">
                        {idx + 1}.
                      </span>
                      <span>{step}</span>
                    </li>
                  ))}
                </ol>
                <div className="mt-4 pt-3 border-t border-[var(--color-status-info-bg)]">
                  <a
                    href={instructions.docs_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-[var(--color-status-info)] hover:underline"
                  >
                    View {PROVIDER_INFO[activeProvider].name} webhook documentation →
                  </a>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Configuration Summary */}
      {config && (
        <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-md">
          <h2 className="text-lg font-semibold text-[var(--color-content-primary)] mb-4">
            Configuration Summary
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {(Object.keys(PROVIDER_INFO) as CICDProvider[]).map((provider) => {
              const info = PROVIDER_INFO[provider];
              const providerConfig = config.providers[provider];

              return (
                <div
                  key={provider}
                  className={`p-4 rounded-lg border ${
                    providerConfig?.enabled
                      ? 'border-[var(--color-status-success)] bg-[var(--color-status-success-bg)]'
                      : 'border-[var(--color-border-default)] bg-[var(--color-surface-inset)]/50'
                  }`}
                >
                  <div className="flex items-center gap-2 mb-2">
                    <span className={`w-8 h-8 rounded-lg flex items-center justify-center ${info.bgColor}`}>
                      <info.icon className={`w-5 h-5 ${info.color}`} />
                    </span>
                    <span className="text-sm font-semibold text-[var(--color-content-primary)]">
                      {info.name}
                    </span>
                  </div>
                  {providerConfig?.enabled ? (
                    <div className="space-y-1 text-xs text-[var(--color-content-secondary)]">
                      <p>Suite: {providerConfig.suite_name || 'Not selected'}</p>
                      <p>Secret: {providerConfig.webhook_secret_set ? 'Configured' : 'Not set'}</p>
                      <p>
                        Triggers:{' '}
                        {Object.entries(providerConfig.event_filter)
                          .filter(([, enabled]) => enabled)
                          .map(([event]) => event)
                          .join(', ') || 'None'}
                      </p>
                    </div>
                  ) : (
                    <p className="text-xs text-[var(--color-content-muted)]">Not enabled</p>
                  )}
                </div>
              );
            })}
          </div>
          {config.last_updated && (
            <p className="text-xs text-[var(--color-content-muted)] mt-4">
              Last updated: {new Date(config.last_updated).toLocaleString()}
            </p>
          )}
        </div>
      )}
    </div>
  );
};

export default CICDConfig;
