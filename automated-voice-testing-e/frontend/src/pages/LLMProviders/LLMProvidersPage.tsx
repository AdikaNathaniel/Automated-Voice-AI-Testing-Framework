/**
 * LLM Providers Configuration Page
 *
 * Admin interface for managing LLM provider API keys.
 * Allows configuring OpenAI, Anthropic, and Google API keys.
 */

import React, { useEffect, useState, useCallback } from 'react';
import { Cpu } from 'lucide-react';
import {
  getProvidersSummary,
  listProviderConfigs,
  createProviderConfig,
  updateProviderConfig,
  deleteProviderConfig,
  testProvider,
} from '../../services/llmProvider.service';
import type {
  LLMProviderConfig,
  LLMProviderConfigCreate,
  LLMProviderConfigUpdate,
  LLMProviderSummary,
  TestProviderResponse,
} from '../../types/llmProvider';
import { PROVIDER_INFO } from '../../types/llmProvider';

interface ProviderFormData {
  provider: 'openai' | 'anthropic' | 'google';
  display_name: string;
  api_key: string;
  default_model: string;
  is_active: boolean;
  temperature: number;
  max_tokens: number;
  timeout_seconds: number;
}

const DEFAULT_FORM_DATA: ProviderFormData = {
  provider: 'openai',
  display_name: '',
  api_key: '',
  default_model: '',
  is_active: true,
  temperature: 0,
  max_tokens: 1024,
  timeout_seconds: 30,
};

const LLMProvidersPage: React.FC = () => {
  const [summary, setSummary] = useState<LLMProviderSummary[]>([]);
  const [configs, setConfigs] = useState<LLMProviderConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editingConfig, setEditingConfig] = useState<LLMProviderConfig | null>(null);
  const [formData, setFormData] = useState<ProviderFormData>(DEFAULT_FORM_DATA);
  const [formError, setFormError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [testResult, setTestResult] = useState<TestProviderResponse | null>(null);
  const [testing, setTesting] = useState(false);

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const [summaryResponse, configsResponse] = await Promise.all([
        getProvidersSummary(),
        listProviderConfigs(),
      ]);
      setSummary(summaryResponse.providers);
      setConfigs(configsResponse.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleAddNew = (provider: 'openai' | 'anthropic' | 'google') => {
    const info = PROVIDER_INFO[provider];
    setFormData({
      ...DEFAULT_FORM_DATA,
      provider,
      display_name: info.name,
      default_model: info.defaultModel,
    });
    setEditingConfig(null);
    setFormError(null);
    setTestResult(null);
    setShowForm(true);
  };

  const handleEdit = (config: LLMProviderConfig) => {
    setFormData({
      provider: config.provider,
      display_name: config.display_name,
      api_key: '', // Don't pre-fill API key for security
      default_model: config.default_model || '',
      is_active: config.is_active,
      temperature: config.temperature,
      max_tokens: config.max_tokens,
      timeout_seconds: config.timeout_seconds,
    });
    setEditingConfig(config);
    setFormError(null);
    setTestResult(null);
    setShowForm(true);
  };

  const handleDelete = async (config: LLMProviderConfig) => {
    if (!window.confirm(`Delete ${config.display_name} configuration?`)) {
      return;
    }
    try {
      await deleteProviderConfig(config.id);
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete');
    }
  };

  const handleTestProvider = async () => {
    try {
      setTesting(true);
      setTestResult(null);
      const result = await testProvider({
        provider: formData.provider,
        api_key: formData.api_key || undefined,
        model: formData.default_model || undefined,
      });
      setTestResult(result);
    } catch (err) {
      setTestResult({
        success: false,
        provider: formData.provider,
        model: formData.default_model,
        message: err instanceof Error ? err.message : 'Test failed',
        latency_ms: null,
        error: 'TEST_FAILED',
      });
    } finally {
      setTesting(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);

    if (!formData.display_name.trim()) {
      setFormError('Display name is required');
      return;
    }

    if (!editingConfig && !formData.api_key.trim()) {
      setFormError('API key is required for new configurations');
      return;
    }

    try {
      setSaving(true);

      if (editingConfig) {
        const updateData: LLMProviderConfigUpdate = {
          display_name: formData.display_name,
          default_model: formData.default_model || null,
          is_active: formData.is_active,
          temperature: formData.temperature,
          max_tokens: formData.max_tokens,
          timeout_seconds: formData.timeout_seconds,
        };
        if (formData.api_key.trim()) {
          updateData.api_key = formData.api_key;
        }
        await updateProviderConfig(editingConfig.id, updateData);
      } else {
        const createData: LLMProviderConfigCreate = {
          provider: formData.provider,
          display_name: formData.display_name,
          api_key: formData.api_key,
          default_model: formData.default_model || undefined,
          is_active: formData.is_active,
          temperature: formData.temperature,
          max_tokens: formData.max_tokens,
          timeout_seconds: formData.timeout_seconds,
        };
        await createProviderConfig(createData);
      }

      setShowForm(false);
      await loadData();
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Failed to save');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-[var(--color-content-primary)] flex items-center gap-3">
              <Cpu className="w-6 h-6" style={{ color: '#2A6B6E' }} />
              LLM Provider Configuration
            </h1>
            <p className="text-sm text-[var(--color-content-muted)] mt-1">Configure API keys for LLM providers used in ensemble validation</p>
          </div>
        </div>
        <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-md">
          <div className="flex flex-col items-center justify-center p-20">
            <div className="w-12 h-12 border-4 border-[var(--color-border-default)] rounded-full animate-spin mb-4" style={{ borderTopColor: '#9333EA' }}></div>
            <div className="text-lg font-semibold text-[var(--color-content-primary)] mb-2">Loading Providers...</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-[var(--color-content-primary)] flex items-center gap-3">
            <Cpu className="w-6 h-6" style={{ color: '#2A6B6E' }} />
            LLM Provider Configuration
          </h1>
          <p className="text-sm text-[var(--color-content-muted)] mt-1">
            Configure API keys for LLM providers used in ensemble validation
          </p>
        </div>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-[var(--color-status-danger-bg)] border border-[var(--color-status-danger)] rounded text-[var(--color-status-danger)]">
          {error}
        </div>
      )}

      {/* Provider Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {summary.map((provider) => {
          const info = PROVIDER_INFO[provider.provider] || {
            name: provider.display_name,
            icon: '?',
            description: '',
          };
          const existingConfig = configs.find((c) => c.provider === provider.provider);

          return (
            <div
              key={provider.provider}
              className={`p-6 border rounded-xl shadow-md ${
                provider.is_configured
                  ? provider.is_active
                    ? 'border-[var(--color-status-success)] bg-[var(--color-status-success-bg)]'
                    : 'border-[var(--color-status-warning)] bg-[var(--color-status-warning-bg)]'
                  : 'border-[var(--color-border-default)] bg-[var(--color-surface-raised)]'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center">
                  <span className="text-2xl mr-2">{info.icon}</span>
                  <span className="font-semibold text-[var(--color-content-primary)]">{info.name}</span>
                </div>
                <span
                  className={`px-2 py-1 text-xs rounded ${
                    provider.is_configured
                      ? provider.is_active
                        ? 'bg-[var(--color-status-success-bg)] text-[var(--color-status-success)]'
                        : 'bg-[var(--color-status-warning-bg)]/50 text-[var(--color-status-warning)]'
                      : 'bg-[var(--color-surface-inset)] text-[var(--color-content-muted)]'
                  }`}
                >
                  {provider.is_configured
                    ? provider.is_active
                      ? 'Active'
                      : 'Inactive'
                    : 'Not Configured'}
                </span>
              </div>
              <p className="text-sm text-[var(--color-content-secondary)] mb-3">{info.description}</p>
              <div className="text-sm text-[var(--color-content-muted)] mb-3">
                Default: <code className="bg-[var(--color-surface-inset)] px-1">{provider.default_model}</code>
              </div>
              <div className="flex gap-2">
                {provider.is_configured ? (
                  <>
                    <button
                      onClick={() => existingConfig && handleEdit(existingConfig)}
                      className="px-4 py-2 text-sm font-medium bg-[var(--color-surface-raised)] text-[var(--color-content-secondary)] border border-[var(--color-border-strong)] rounded-lg hover:bg-[var(--color-interactive-hover)] transition-colors"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => existingConfig && handleDelete(existingConfig)}
                      className="px-4 py-2 text-sm font-medium bg-[var(--color-surface-raised)] text-[var(--color-status-danger)] border border-[var(--color-status-danger-bg)] rounded-lg hover:bg-[var(--color-status-danger-bg)] transition-colors"
                    >
                      Delete
                    </button>
                  </>
                ) : (
                  <button
                    onClick={() => handleAddNew(provider.provider as 'openai' | 'anthropic' | 'google')}
                    className="px-4 py-2.5 rounded-lg text-sm font-semibold transition-all inline-flex items-center gap-2 text-white hover:shadow-lg hover:-translate-y-0.5"
                    style={{ background: 'linear-gradient(135deg, #9333EA 0%, #7E22CE 100%)' }}
                  >
                    Configure
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Configuration List */}
      {configs.length > 0 && (
        <div>
          <h2 className="text-xl font-semibold mb-3 text-[var(--color-content-primary)]">Configured Providers</h2>
          <div className="bg-[var(--color-surface-raised)] rounded-xl shadow-md border border-[var(--color-border-default)] overflow-hidden">
            <table className="w-full">
              <thead className="bg-[var(--color-surface-inset)]/50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-[var(--color-content-muted)] uppercase tracking-wider">Provider</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-[var(--color-content-muted)] uppercase tracking-wider">Display Name</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-[var(--color-content-muted)] uppercase tracking-wider">Model</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-[var(--color-content-muted)] uppercase tracking-wider">API Key</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-[var(--color-content-muted)] uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-[var(--color-content-muted)] uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--color-border-subtle)]">
                {configs.map((config) => (
                  <tr key={config.id} className="hover:bg-[var(--color-interactive-hover)]/50 transition-colors">
                    <td className="px-6 py-4 text-[var(--color-content-primary)]">
                      {PROVIDER_INFO[config.provider]?.icon} {config.provider}
                    </td>
                    <td className="px-6 py-4 text-[var(--color-content-primary)]">{config.display_name}</td>
                    <td className="px-6 py-4">
                      <code className="bg-[var(--color-surface-inset)] px-1 text-sm text-[var(--color-content-primary)]">
                        {config.default_model || '-'}
                      </code>
                    </td>
                    <td className="px-6 py-4">
                      <code className="bg-[var(--color-surface-inset)] px-1 text-sm text-[var(--color-content-primary)]">
                        {config.api_key_preview || '****'}
                      </code>
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`px-2 py-1 text-xs rounded ${
                          config.is_active
                            ? 'bg-[var(--color-status-success-bg)] text-[var(--color-status-success)]'
                            : 'bg-[var(--color-surface-inset)] text-[var(--color-content-muted)]'
                        }`}
                      >
                        {config.is_active ? 'Active' : 'Inactive'}
                      </span>
                      {config.is_default && (
                        <span className="ml-1 px-2 py-1 text-xs rounded bg-[var(--color-status-info-bg)]/50 text-[var(--color-status-info)]">
                          Default
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <button
                        onClick={() => handleEdit(config)}
                        className="text-[var(--color-status-purple)] hover:text-[var(--color-status-purple)] font-medium mr-3 transition-colors"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDelete(config)}
                        className="text-[var(--color-status-danger)] hover:text-[var(--color-status-danger)] font-medium transition-colors"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Add/Edit Form Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-[var(--color-surface-raised)] rounded-lg shadow-lg w-full max-w-md p-6">
            <h2 className="text-xl font-semibold mb-4 text-[var(--color-content-primary)]">
              {editingConfig ? 'Edit Provider' : 'Configure Provider'}
            </h2>

            {formError && (
              <div className="mb-4 p-3 bg-[var(--color-status-danger-bg)] border border-[var(--color-status-danger)] rounded text-[var(--color-status-danger)] text-sm">
                {formError}
              </div>
            )}

            <form onSubmit={handleSubmit}>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-1 text-[var(--color-content-secondary)]">Provider</label>
                <div className="flex items-center">
                  <span className="text-2xl mr-2">
                    {PROVIDER_INFO[formData.provider]?.icon}
                  </span>
                  <span className="font-medium text-[var(--color-content-primary)]">
                    {PROVIDER_INFO[formData.provider]?.name || formData.provider}
                  </span>
                </div>
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium mb-1 text-[var(--color-content-secondary)]">Display Name</label>
                <input
                  type="text"
                  value={formData.display_name}
                  onChange={(e) =>
                    setFormData({ ...formData, display_name: e.target.value })
                  }
                  className="w-full px-4 py-2.5 border border-[var(--color-border-default)] rounded-lg bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-status-purple)]/10 focus:border-[var(--color-status-purple)] transition-all"
                  placeholder="e.g., OpenAI Production"
                />
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium mb-1 text-[var(--color-content-secondary)]">
                  API Key {editingConfig && '(leave blank to keep existing)'}
                </label>
                <input
                  type="password"
                  value={formData.api_key}
                  onChange={(e) => setFormData({ ...formData, api_key: e.target.value })}
                  className="w-full px-4 py-2.5 border border-[var(--color-border-default)] rounded-lg bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-status-purple)]/10 focus:border-[var(--color-status-purple)] transition-all"
                  placeholder={editingConfig ? '••••••••' : 'sk-...'}
                />
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium mb-1 text-[var(--color-content-secondary)]">Default Model</label>
                <input
                  type="text"
                  value={formData.default_model}
                  onChange={(e) =>
                    setFormData({ ...formData, default_model: e.target.value })
                  }
                  className="w-full px-4 py-2.5 border border-[var(--color-border-default)] rounded-lg bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-status-purple)]/10 focus:border-[var(--color-status-purple)] transition-all"
                  placeholder={PROVIDER_INFO[formData.provider]?.defaultModel}
                />
              </div>

              <div className="grid grid-cols-3 gap-3 mb-4">
                <div>
                  <label className="block text-sm font-medium mb-1 text-[var(--color-content-secondary)]">Temperature</label>
                  <input
                    type="number"
                    min="0"
                    max="2"
                    step="0.1"
                    value={formData.temperature}
                    onChange={(e) =>
                      setFormData({ ...formData, temperature: parseFloat(e.target.value) })
                    }
                    className="w-full px-4 py-2.5 border border-[var(--color-border-default)] rounded-lg bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-status-purple)]/10 focus:border-[var(--color-status-purple)] transition-all"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1 text-[var(--color-content-secondary)]">Max Tokens</label>
                  <input
                    type="number"
                    min="1"
                    max="100000"
                    value={formData.max_tokens}
                    onChange={(e) =>
                      setFormData({ ...formData, max_tokens: parseInt(e.target.value, 10) })
                    }
                    className="w-full px-4 py-2.5 border border-[var(--color-border-default)] rounded-lg bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-status-purple)]/10 focus:border-[var(--color-status-purple)] transition-all"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1 text-[var(--color-content-secondary)]">Timeout (s)</label>
                  <input
                    type="number"
                    min="1"
                    max="300"
                    value={formData.timeout_seconds}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        timeout_seconds: parseInt(e.target.value, 10),
                      })
                    }
                    className="w-full px-4 py-2.5 border border-[var(--color-border-default)] rounded-lg bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-status-purple)]/10 focus:border-[var(--color-status-purple)] transition-all"
                  />
                </div>
              </div>

              <div className="mb-4">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.is_active}
                    onChange={(e) =>
                      setFormData({ ...formData, is_active: e.target.checked })
                    }
                    className="mr-2"
                  />
                  <span className="text-sm text-[var(--color-content-secondary)]">Active</span>
                </label>
              </div>

              {/* Test Result */}
              {testResult && (
                <div
                  className={`mb-4 p-3 rounded text-sm ${
                    testResult.success
                      ? 'bg-[var(--color-status-success-bg)] border border-[var(--color-status-success)] text-[var(--color-status-success)]'
                      : 'bg-[var(--color-status-danger-bg)] border border-[var(--color-status-danger)] text-[var(--color-status-danger)]'
                  }`}
                >
                  <div className="font-medium">
                    {testResult.success ? 'Test Passed' : 'Test Failed'}
                  </div>
                  <div>{testResult.message}</div>
                  {testResult.latency_ms && (
                    <div className="text-xs mt-1">Latency: {testResult.latency_ms}ms</div>
                  )}
                </div>
              )}

              <div className="flex justify-between">
                <button
                  type="button"
                  onClick={handleTestProvider}
                  disabled={testing || (!formData.api_key && !editingConfig)}
                  className="px-4 py-2 bg-[var(--color-surface-inset)] text-[var(--color-content-secondary)] rounded hover:bg-[var(--color-interactive-active)] disabled:opacity-50"
                >
                  {testing ? 'Testing...' : 'Test Connection'}
                </button>

                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={() => setShowForm(false)}
                    className="px-4 py-2 border border-[var(--color-border-strong)] rounded hover:bg-[var(--color-interactive-hover)] text-[var(--color-content-secondary)]"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={saving}
                    className="px-4 py-2 bg-[var(--color-status-info)] text-white rounded hover:bg-[var(--color-status-info)]/80 disabled:opacity-50"
                  >
                    {saving ? 'Saving...' : 'Save'}
                  </button>
                </div>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default LLMProvidersPage;
