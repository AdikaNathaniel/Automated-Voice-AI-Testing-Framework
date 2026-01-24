/**
 * LLM Providers Tab Component
 * Manages LLM provider configurations for the organization
 */

import React, { useEffect, useState, useCallback } from 'react';
import {
  getProvidersSummary,
  listProviderConfigs,
  createProviderConfig,
  updateProviderConfig,
  deleteProviderConfig,
  testProvider,
} from '../../../services/llmProvider.service';
import type {
  LLMProviderConfig,
  LLMProviderConfigCreate,
  LLMProviderConfigUpdate,
  LLMProviderSummary,
  TestProviderResponse,
} from '../../../types/llmProvider';
import { PROVIDER_INFO } from '../../../types/llmProvider';

interface LLMProviderFormData {
  provider: 'openai' | 'anthropic' | 'google';
  display_name: string;
  api_key: string;
  default_model: string;
  is_active: boolean;
  temperature: number;
  max_tokens: number;
  timeout_seconds: number;
}

const DEFAULT_FORM_DATA: LLMProviderFormData = {
  provider: 'openai',
  display_name: '',
  api_key: '',
  default_model: '',
  is_active: true,
  temperature: 0,
  max_tokens: 1024,
  timeout_seconds: 30,
};

interface LLMProvidersTabProps {
  onError: (error: string | null) => void;
  onSuccess: (message: string) => void;
}

const LLMProvidersTab: React.FC<LLMProvidersTabProps> = ({ onError, onSuccess }) => {
  const [summary, setSummary] = useState<LLMProviderSummary[]>([]);
  const [configs, setConfigs] = useState<LLMProviderConfig[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [editingConfig, setEditingConfig] = useState<LLMProviderConfig | null>(null);
  const [formData, setFormData] = useState<LLMProviderFormData>(DEFAULT_FORM_DATA);
  const [testResult, setTestResult] = useState<TestProviderResponse | null>(null);
  const [testing, setTesting] = useState(false);

  const loadProviders = useCallback(async () => {
    try {
      setLoading(true);
      onError(null);
      const [summaryResponse, configsResponse] = await Promise.all([
        getProvidersSummary(),
        listProviderConfigs(),
      ]);
      setSummary(summaryResponse.providers);
      setConfigs(configsResponse.items);
    } catch (err) {
      onError(err instanceof Error ? err.message : 'Failed to load LLM providers');
    } finally {
      setLoading(false);
    }
  }, [onError]);

  useEffect(() => {
    loadProviders();
  }, [loadProviders]);

  const handleAddProvider = (provider: 'openai' | 'anthropic' | 'google') => {
    const info = PROVIDER_INFO[provider];
    setFormData({
      ...DEFAULT_FORM_DATA,
      provider,
      display_name: info.name,
      default_model: info.defaultModel,
    });
    setEditingConfig(null);
    setTestResult(null);
    setShowForm(true);
  };

  const handleEditProvider = (config: LLMProviderConfig) => {
    setFormData({
      provider: config.provider,
      display_name: config.display_name,
      api_key: '',
      default_model: config.default_model || '',
      is_active: config.is_active,
      temperature: config.temperature,
      max_tokens: config.max_tokens,
      timeout_seconds: config.timeout_seconds,
    });
    setEditingConfig(config);
    setTestResult(null);
    setShowForm(true);
  };

  const handleDeleteProvider = async (config: LLMProviderConfig) => {
    if (!window.confirm(`Delete ${config.display_name} configuration?`)) return;
    try {
      await deleteProviderConfig(config.id);
      await loadProviders();
      onSuccess('Provider deleted successfully');
    } catch (err) {
      onError(err instanceof Error ? err.message : 'Failed to delete provider');
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
    onError(null);
    if (!formData.display_name.trim()) {
      onError('Display name is required');
      return;
    }
    if (!editingConfig && !formData.api_key.trim()) {
      onError('API key is required for new configurations');
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
      onSuccess('Provider configuration saved');
      await loadProviders();
    } catch (err) {
      onError(err instanceof Error ? err.message : 'Failed to save provider');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center p-12">
        <div className="w-12 h-12 border-4 border-[var(--color-border-default)] rounded-full animate-spin mb-4" style={{ borderTopColor: '#2A6B6E' }}></div>
        <div className="text-lg font-semibold text-[var(--color-content-primary)]">Loading providers...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Provider Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {summary.map((provider) => {
          const info = PROVIDER_INFO[provider.provider] || { name: provider.display_name, icon: '?', description: '' };
          const existingConfig = configs.find((c) => c.provider === provider.provider);
          return (
            <div key={provider.provider} className={`p-5 border rounded-xl shadow-sm ${provider.is_configured ? provider.is_active ? 'border-[var(--color-status-success)] bg-[var(--color-status-success-bg)]' : 'border-[var(--color-status-warning)] bg-[var(--color-status-warning-bg)]' : 'border-[var(--color-border-default)] bg-[var(--color-surface-raised)]'}`}>
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center">
                  <span className="text-2xl mr-2">{info.icon}</span>
                  <span className="font-semibold text-[var(--color-content-primary)]">{info.name}</span>
                </div>
                <span className={`px-2 py-1 text-xs rounded ${provider.is_configured ? provider.is_active ? 'bg-[var(--color-status-success-bg)] text-[var(--color-status-success)]' : 'bg-[var(--color-status-warning-bg)]/50 text-[var(--color-status-warning)]' : 'bg-[var(--color-surface-inset)] text-[var(--color-content-muted)]'}`}>
                  {provider.is_configured ? (provider.is_active ? 'Active' : 'Inactive') : 'Not Configured'}
                </span>
              </div>
              <p className="text-sm text-[var(--color-content-secondary)] mb-2">{info.description}</p>
              <div className="text-sm text-[var(--color-content-muted)] mb-3">
                Default: <code className="bg-[var(--color-surface-inset)] px-1 text-xs">{provider.default_model}</code>
              </div>
              <div className="flex gap-2">
                {provider.is_configured ? (
                  <>
                    <button onClick={() => existingConfig && handleEditProvider(existingConfig)} className="px-3 py-1.5 text-sm font-medium bg-[var(--color-surface-raised)] text-[var(--color-content-secondary)] border border-[var(--color-border-strong)] rounded-lg hover:bg-[var(--color-interactive-hover)] transition-colors">Edit</button>
                    <button onClick={() => existingConfig && handleDeleteProvider(existingConfig)} className="px-3 py-1.5 text-sm font-medium bg-[var(--color-surface-raised)] text-[var(--color-status-danger)] border border-[var(--color-status-danger-bg)] rounded-lg hover:bg-[var(--color-status-danger-bg)] transition-colors">Delete</button>
                  </>
                ) : (
                  <button onClick={() => handleAddProvider(provider.provider as 'openai' | 'anthropic' | 'google')} className="btn btn-primary text-sm">Configure</button>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Configured Providers Table */}
      {configs.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-[var(--color-content-primary)] mb-3">Configured Providers</h3>
          <div className="bg-[var(--color-surface-raised)] rounded-xl shadow-sm border border-[var(--color-border-default)] overflow-hidden">
            <table className="w-full">
              <thead className="bg-[var(--color-surface-inset)]/50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-[var(--color-content-muted)] uppercase">Provider</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-[var(--color-content-muted)] uppercase">Display Name</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-[var(--color-content-muted)] uppercase">Model</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-[var(--color-content-muted)] uppercase">API Key</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-[var(--color-content-muted)] uppercase">Status</th>
                  <th className="px-4 py-3 text-right text-xs font-semibold text-[var(--color-content-muted)] uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--color-border-subtle)]">
                {configs.map((config) => (
                  <tr key={config.id} className="hover:bg-[var(--color-interactive-hover)]/50 transition-colors">
                    <td className="px-4 py-3 text-[var(--color-content-primary)]">{PROVIDER_INFO[config.provider]?.icon} {config.provider}</td>
                    <td className="px-4 py-3 text-[var(--color-content-primary)]">{config.display_name}</td>
                    <td className="px-4 py-3"><code className="bg-[var(--color-surface-inset)] px-1 text-xs text-[var(--color-content-primary)]">{config.default_model || '-'}</code></td>
                    <td className="px-4 py-3"><code className="bg-[var(--color-surface-inset)] px-1 text-xs text-[var(--color-content-primary)]">{config.api_key_preview || '****'}</code></td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 text-xs rounded ${config.is_active ? 'bg-[var(--color-status-success-bg)] text-[var(--color-status-success)]' : 'bg-[var(--color-surface-inset)] text-[var(--color-content-muted)]'}`}>{config.is_active ? 'Active' : 'Inactive'}</span>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <button onClick={() => handleEditProvider(config)} className="text-primary hover:text-primary/80 font-medium mr-3 transition-colors text-sm">Edit</button>
                      <button onClick={() => handleDeleteProvider(config)} className="text-[var(--color-status-danger)] hover:text-[var(--color-status-danger)] font-medium transition-colors text-sm">Delete</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Form Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-[var(--color-surface-raised)] rounded-xl shadow-lg w-full max-w-md p-6">
            <h2 className="text-xl font-semibold mb-4 text-[var(--color-content-primary)]">{editingConfig ? 'Edit Provider' : 'Configure Provider'}</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1 text-[var(--color-content-secondary)]">Provider</label>
                <div className="flex items-center"><span className="text-2xl mr-2">{PROVIDER_INFO[formData.provider]?.icon}</span><span className="font-medium text-[var(--color-content-primary)]">{PROVIDER_INFO[formData.provider]?.name || formData.provider}</span></div>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1 text-[var(--color-content-secondary)]">Display Name</label>
                <input type="text" value={formData.display_name} onChange={(e) => setFormData({ ...formData, display_name: e.target.value })} className="w-full px-4 py-2.5 border border-[var(--color-border-default)] rounded-lg bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all" placeholder="e.g., OpenAI Production" />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1 text-[var(--color-content-secondary)]">API Key {editingConfig && '(leave blank to keep existing)'}</label>
                <input type="password" value={formData.api_key} onChange={(e) => setFormData({ ...formData, api_key: e.target.value })} className="w-full px-4 py-2.5 border border-[var(--color-border-default)] rounded-lg bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all" placeholder={editingConfig ? '••••••••' : 'sk-...'} />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1 text-[var(--color-content-secondary)]">Default Model</label>
                <input type="text" value={formData.default_model} onChange={(e) => setFormData({ ...formData, default_model: e.target.value })} className="w-full px-4 py-2.5 border border-[var(--color-border-default)] rounded-lg bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all" placeholder={PROVIDER_INFO[formData.provider]?.defaultModel} />
              </div>
              <div className="grid grid-cols-3 gap-3">
                <div><label className="block text-sm font-medium mb-1 text-[var(--color-content-secondary)]">Temperature</label><input type="number" min="0" max="2" step="0.1" value={formData.temperature} onChange={(e) => setFormData({ ...formData, temperature: parseFloat(e.target.value) })} className="w-full px-3 py-2 border border-[var(--color-border-default)] rounded-lg bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all" /></div>
                <div><label className="block text-sm font-medium mb-1 text-[var(--color-content-secondary)]">Max Tokens</label><input type="number" min="1" max="100000" value={formData.max_tokens} onChange={(e) => setFormData({ ...formData, max_tokens: parseInt(e.target.value, 10) })} className="w-full px-3 py-2 border border-[var(--color-border-default)] rounded-lg bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all" /></div>
                <div><label className="block text-sm font-medium mb-1 text-[var(--color-content-secondary)]">Timeout (s)</label><input type="number" min="1" max="300" value={formData.timeout_seconds} onChange={(e) => setFormData({ ...formData, timeout_seconds: parseInt(e.target.value, 10) })} className="w-full px-3 py-2 border border-[var(--color-border-default)] rounded-lg bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all" /></div>
              </div>
              <div>
                <label className="flex items-center"><input type="checkbox" checked={formData.is_active} onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })} className="mr-2 w-4 h-4 rounded text-primary focus:ring-primary" /><span className="text-sm text-[var(--color-content-secondary)]">Active</span></label>
              </div>
              {testResult && (
                <div className={`p-3 rounded text-sm ${testResult.success ? 'bg-[var(--color-status-success-bg)] border border-[var(--color-status-success)] text-[var(--color-status-success)]' : 'bg-[var(--color-status-danger-bg)] border border-[var(--color-status-danger)] text-[var(--color-status-danger)]'}`}>
                  <div className="font-medium">{testResult.success ? 'Test Passed' : 'Test Failed'}</div>
                  <div>{testResult.message}</div>
                  {testResult.latency_ms && <div className="text-xs mt-1">Latency: {testResult.latency_ms}ms</div>}
                </div>
              )}
              <div className="flex justify-between pt-2">
                <button type="button" onClick={handleTestProvider} disabled={testing || (!formData.api_key && !editingConfig)} className="px-4 py-2 bg-[var(--color-surface-inset)] text-[var(--color-content-secondary)] rounded-lg hover:bg-[var(--color-interactive-active)] disabled:opacity-50 text-sm">{testing ? 'Testing...' : 'Test Connection'}</button>
                <div className="flex gap-2">
                  <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 border border-[var(--color-border-strong)] rounded-lg hover:bg-[var(--color-interactive-hover)] text-[var(--color-content-secondary)] text-sm">Cancel</button>
                  <button type="submit" disabled={saving} className="btn btn-primary text-sm">{saving ? 'Saving...' : 'Save'}</button>
                </div>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default LLMProvidersTab;
