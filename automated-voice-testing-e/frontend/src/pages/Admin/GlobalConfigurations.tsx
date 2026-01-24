/**
 * Global Configurations Page (Super Admin)
 *
 * Super admin page for managing global default configurations:
 * - General settings
 * - Pattern Analysis configuration (AI-powered edge case discovery)
 *
 * These configurations serve as defaults for all organizations.
 * Individual organizations can override these via /configurations.
 *
 * Note: Integrations, CI/CD, and Slack notifications are organization-specific
 * and managed by org admins via dedicated pages.
 */

import React, { useState, useEffect } from 'react';
import {
  Building2,
  Bot,
  Settings,
  Save,
  RotateCw,
  AlertCircle,
  CheckCircle,
  Info,
  Play,
} from 'lucide-react';
import {
  getPatternAnalysisConfig,
  updatePatternAnalysisConfig,
  triggerManualAnalysis,
  getDefaultConfig,
} from '../../services/patternAnalysisConfig.service';
import type {
  PatternAnalysisConfig,
  PatternAnalysisConfigUpdate,
  ManualAnalysisResponse,
} from '../../types/patternAnalysisConfig';

type Tab = 'general' | 'pattern-analysis';

const GlobalConfigurations: React.FC = () => {
  const [activeTab, setActiveTab] = useState<Tab>('general');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Pattern Analysis state
  const [config, setConfig] = useState<PatternAnalysisConfig | null>(null);
  const [formData, setFormData] = useState<Partial<PatternAnalysisConfigUpdate>>({});
  const [hasChanges, setHasChanges] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);

  useEffect(() => {
    if (activeTab === 'pattern-analysis') {
      loadPatternAnalysisConfig();
    }
  }, [activeTab]);

  const loadPatternAnalysisConfig = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getPatternAnalysisConfig();
      setConfig(data);
      setFormData({});
      setHasChanges(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load configuration');
    } finally {
      setLoading(false);
    }
  };

  const handleFieldChange = <K extends keyof PatternAnalysisConfigUpdate>(
    field: K,
    value: PatternAnalysisConfigUpdate[K]
  ) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setHasChanges(true);
    setSuccess(null);
  };

  const handleSave = async () => {
    if (!hasChanges || !config) return;

    try {
      setSaving(true);
      setError(null);
      await updatePatternAnalysisConfig(formData);
      setSuccess('Configuration saved successfully');
      await loadPatternAnalysisConfig();
      setHasChanges(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save configuration');
    } finally {
      setSaving(false);
    }
  };

  const handleReset = async () => {
    try {
      setLoading(true);
      const defaults = await getDefaultConfig();
      setFormData(defaults);
      setHasChanges(true);
      setSuccess(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load defaults');
    } finally {
      setLoading(false);
    }
  };

  const handleTriggerAnalysis = async () => {
    try {
      setAnalyzing(true);
      setError(null);
      const result = await triggerManualAnalysis({});
      setSuccess(`Pattern analysis started (Task ID: ${result.task_id})`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to trigger analysis');
    } finally {
      setAnalyzing(false);
    }
  };

  const tabs = [
    { id: 'general' as Tab, label: 'General', icon: Building2 },
    { id: 'pattern-analysis' as Tab, label: 'Pattern Analysis', icon: Bot },
  ];

  const getValue = <K extends keyof PatternAnalysisConfigUpdate>(field: K): any => {
    if (field in formData && formData[field] !== undefined) {
      return formData[field];
    }
    return config?.[field as keyof PatternAnalysisConfig];
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-md">
        <div className="flex items-center gap-3">
          <Settings className="w-8 h-8 text-[var(--color-status-purple)]" />
          <div>
            <h1 className="text-3xl font-bold text-[var(--color-content-primary)]">
              Global Configurations
            </h1>
            <p className="text-sm text-[var(--color-content-muted)] mt-1">
              Configure global defaults for all organizations. Individual organizations can override these configurations.
            </p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-[var(--color-surface-raised)] rounded-xl shadow-md overflow-hidden">
        <div className="border-b border-[var(--color-border-default)]">
          <nav className="flex overflow-x-auto">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-6 py-4 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${
                    activeTab === tab.id
                      ? 'border-[var(--color-status-purple)] text-[var(--color-status-purple)]'
                      : 'border-transparent text-[var(--color-content-muted)] hover:text-[var(--color-content-secondary)] hover:border-[var(--color-border-default)]'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {tab.label}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="p-6">
          {/* General Tab */}
          {activeTab === 'general' && (
            <div className="space-y-6">
              <div className="flex items-center gap-2 text-[var(--color-content-muted)]">
                <Info className="w-5 h-5" />
                <p className="text-sm">General organization settings will be added here</p>
              </div>
            </div>
          )}

          {/* Pattern Analysis Tab */}
          {activeTab === 'pattern-analysis' && (
            <div className="space-y-6">
              {/* Alerts */}
              {error && (
                <div className="p-4 bg-[var(--color-status-danger-bg)] border border-[var(--color-status-danger)] rounded-lg flex items-start gap-3">
                  <AlertCircle className="w-5 h-5 text-[var(--color-status-danger)] flex-shrink-0 mt-0.5" />
                  <div className="text-sm text-[var(--color-status-danger)]">{error}</div>
                </div>
              )}

              {success && (
                <div className="p-4 bg-[var(--color-status-success-bg)] border border-[var(--color-status-success)] rounded-lg flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-[var(--color-status-success)] flex-shrink-0 mt-0.5" />
                  <div className="text-sm text-[var(--color-status-success)]">{success}</div>
                </div>
              )}

              {loading ? (
                <div className="flex flex-col items-center justify-center p-12">
                  <div className="w-12 h-12 border-4 border-[var(--color-border-default)] rounded-full animate-spin mb-4" style={{ borderTopColor: '#9333EA' }}></div>
                  <div className="text-lg font-semibold text-[var(--color-content-primary)]">
                    Loading configuration...
                  </div>
                </div>
              ) : config ? (
                <>
                  {/* Description */}
                  <div className="bg-[var(--color-status-purple-bg)] border border-[var(--color-status-purple)] rounded-lg p-4">
                    <h3 className="text-sm font-semibold text-[var(--color-status-purple)] mb-2">
                      About Pattern Analysis
                    </h3>
                    <p className="text-sm text-[var(--color-status-purple)]">
                      Configure how the AI-powered pattern discovery system analyzes your edge cases.
                      The system automatically groups similar failures, identifies root causes, and
                      generates actionable insights to improve your voice AI system.
                    </p>
                  </div>

                  {/* Time Window Settings */}
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold text-[var(--color-content-primary)]">
                      Time Window Settings
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-2">
                          Lookback Period (days)
                        </label>
                        <input
                          type="number"
                          min="1"
                          max="365"
                          value={getValue('lookback_days')}
                          onChange={(e) => handleFieldChange('lookback_days', parseInt(e.target.value))}
                          className="w-full px-4 py-2.5 border border-[var(--color-border-default)] rounded-xl bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                        />
                        <p className="text-xs text-[var(--color-content-muted)] mt-1">
                          Analyze edge cases from the last N days
                        </p>
                      </div>

                      <div className="flex items-start pt-8">
                        <div className="bg-[var(--color-status-purple-bg)] border border-[var(--color-status-purple)] rounded-lg p-3">
                          <p className="text-xs text-[var(--color-status-purple)]">
                            <strong>Tip:</strong> A shorter lookback period (7-14 days) focuses on recent issues.
                            A longer period (30-90 days) catches recurring patterns.
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Pattern Formation Settings */}
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold text-[var(--color-content-primary)]">
                      Pattern Formation
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-2">
                          Minimum Pattern Size
                        </label>
                        <input
                          type="number"
                          min="2"
                          max="50"
                          value={getValue('min_pattern_size')}
                          onChange={(e) => handleFieldChange('min_pattern_size', parseInt(e.target.value))}
                          className="w-full px-4 py-2.5 border border-[var(--color-border-default)] rounded-xl bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                        />
                        <p className="text-xs text-[var(--color-content-muted)] mt-1">
                          Minimum edge cases required to form a pattern
                        </p>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-2">
                          Similarity Threshold
                        </label>
                        <input
                          type="number"
                          min="0"
                          max="1"
                          step="0.05"
                          value={getValue('similarity_threshold')}
                          onChange={(e) => handleFieldChange('similarity_threshold', parseFloat(e.target.value))}
                          className="w-full px-4 py-2.5 border border-[var(--color-border-default)] rounded-xl bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                        />
                        <p className="text-xs text-[var(--color-content-muted)] mt-1">
                          Semantic similarity threshold (0.0 - 1.0)
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Defect Auto-Creation */}
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold text-[var(--color-content-primary)]">
                      Defect Auto-Creation
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-2">
                          Consecutive Failure Threshold
                        </label>
                        <input
                          type="number"
                          min="1"
                          max="100"
                          value={getValue('defect_auto_creation_threshold')}
                          onChange={(e) => handleFieldChange('defect_auto_creation_threshold', parseInt(e.target.value))}
                          className="w-full px-4 py-2.5 border border-[var(--color-border-default)] rounded-xl bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                        />
                        <p className="text-xs text-[var(--color-content-muted)] mt-1">
                          Number of consecutive AI validation failures before creating a defect
                        </p>
                      </div>
                      <div className="flex items-start pt-8">
                        <div className="bg-[var(--color-status-amber-bg)] border border-[var(--color-status-amber-bg)] rounded-lg p-3">
                          <p className="text-xs text-[var(--color-status-amber)]">
                            <strong>How it works:</strong> When AI validation fails (<code className="bg-[var(--color-status-amber-bg)] px-1 rounded">auto_fail</code>) {getValue('defect_auto_creation_threshold') || 3} times consecutively,
                            a defect is automatically created. Any pass or human review resets the counter.
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* LLM Settings */}
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold text-[var(--color-content-primary)]">
                      AI/LLM Settings
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="flex items-center gap-3">
                        <input
                          type="checkbox"
                          id="enable_llm"
                          checked={getValue('enable_llm_analysis')}
                          onChange={(e) => handleFieldChange('enable_llm_analysis', e.target.checked)}
                          className="w-5 h-5 rounded border-[var(--color-border-strong)] text-[var(--color-status-purple)] focus:ring-2 focus:ring-[var(--color-status-purple)]"
                        />
                        <label htmlFor="enable_llm" className="text-sm font-medium text-[var(--color-content-secondary)]">
                          Enable LLM-powered analysis
                        </label>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-2">
                          LLM Confidence Threshold
                        </label>
                        <input
                          type="number"
                          min="0"
                          max="1"
                          step="0.05"
                          value={getValue('llm_confidence_threshold')}
                          onChange={(e) => handleFieldChange('llm_confidence_threshold', parseFloat(e.target.value))}
                          disabled={!getValue('enable_llm_analysis')}
                          className="w-full px-4 py-2.5 border border-[var(--color-border-default)] rounded-xl bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:ring-2 focus:ring-purple-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
                        />
                        <p className="text-xs text-[var(--color-content-muted)] mt-1">
                          Minimum LLM confidence for pattern matching
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Scheduling */}
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold text-[var(--color-content-primary)]">
                      Scheduling
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="flex items-center gap-3">
                        <input
                          type="checkbox"
                          id="enable_auto"
                          checked={getValue('enable_auto_analysis')}
                          onChange={(e) => handleFieldChange('enable_auto_analysis', e.target.checked)}
                          className="w-5 h-5 rounded border-[var(--color-border-strong)] text-[var(--color-status-purple)] focus:ring-2 focus:ring-[var(--color-status-purple)]"
                        />
                        <label htmlFor="enable_auto" className="text-sm font-medium text-[var(--color-content-secondary)]">
                          Enable automatic pattern analysis
                        </label>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-2">
                          Schedule (Cron)
                        </label>
                        <input
                          type="text"
                          value={getValue('analysis_schedule')}
                          onChange={(e) => handleFieldChange('analysis_schedule', e.target.value)}
                          disabled={!getValue('enable_auto_analysis')}
                          className="w-full px-4 py-2.5 border border-[var(--color-border-default)] rounded-xl bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:ring-2 focus:ring-purple-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed font-mono text-sm"
                          placeholder="0 2 * * *"
                        />
                        <p className="text-xs text-[var(--color-content-muted)] mt-1">
                          Cron expression (default: daily at 2 AM)
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Notifications */}
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold text-[var(--color-content-primary)]">
                      Notifications
                    </h3>
                    <div className="space-y-3">
                      <div className="flex items-center gap-3">
                        <input
                          type="checkbox"
                          id="notify_new"
                          checked={getValue('notify_on_new_patterns')}
                          onChange={(e) => handleFieldChange('notify_on_new_patterns', e.target.checked)}
                          className="w-5 h-5 rounded border-[var(--color-border-strong)] text-[var(--color-status-purple)] focus:ring-2 focus:ring-[var(--color-status-purple)]"
                        />
                        <label htmlFor="notify_new" className="text-sm font-medium text-[var(--color-content-secondary)]">
                          Notify when new patterns are discovered
                        </label>
                      </div>

                      <div className="flex items-center gap-3">
                        <input
                          type="checkbox"
                          id="notify_critical"
                          checked={getValue('notify_on_critical_patterns')}
                          onChange={(e) => handleFieldChange('notify_on_critical_patterns', e.target.checked)}
                          className="w-5 h-5 rounded border-[var(--color-border-strong)] text-[var(--color-status-purple)] focus:ring-2 focus:ring-[var(--color-status-purple)]"
                        />
                        <label htmlFor="notify_critical" className="text-sm font-medium text-[var(--color-content-secondary)]">
                          Send alerts for critical severity patterns
                        </label>
                      </div>
                    </div>
                  </div>

                  {/* Performance Settings */}
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold text-[var(--color-content-primary)]">
                      Performance Settings
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-2">
                          Response Time SLA (ms)
                        </label>
                        <input
                          type="number"
                          min="100"
                          max="30000"
                          step="100"
                          value={getValue('response_time_sla_ms') ?? 2000}
                          onChange={(e) => handleFieldChange('response_time_sla_ms', parseInt(e.target.value))}
                          className="w-full px-4 py-2.5 border border-[var(--color-border-default)] rounded-xl bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                        />
                        <p className="text-xs text-[var(--color-content-muted)] mt-1">
                          Maximum acceptable response time in milliseconds (100-30000)
                        </p>
                      </div>
                      <div className="flex items-start pt-8">
                        <div className="bg-[var(--color-status-info-bg)] border border-[var(--color-status-info)] rounded-lg p-3">
                          <p className="text-xs text-[var(--color-status-info)]">
                            <strong>SLA Monitoring:</strong> Responses exceeding {getValue('response_time_sla_ms') ?? 2000}ms
                            will be flagged in dashboards and reports. This helps identify performance degradation in your voice AI system.
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex flex-wrap items-center justify-between gap-4 pt-4 border-t border-[var(--color-border-default)]">
                    <button
                      onClick={handleReset}
                      className="px-4 py-2.5 border border-[var(--color-border-default)] rounded-xl text-[var(--color-content-secondary)] hover:bg-[var(--color-interactive-hover)] transition-colors inline-flex items-center gap-2"
                    >
                      <RotateCw className="w-4 h-4" />
                      Reset to Defaults
                    </button>

                    <div className="flex items-center gap-3">
                      <button
                        onClick={handleTriggerAnalysis}
                        disabled={analyzing}
                        className="px-4 py-2.5 border border-[var(--color-status-purple-bg)] rounded-xl text-[var(--color-status-purple)] hover:bg-[var(--color-status-purple-bg)] transition-colors inline-flex items-center gap-2 disabled:opacity-50"
                      >
                        <Play className="w-4 h-4" />
                        {analyzing ? 'Starting...' : 'Run Analysis Now'}
                      </button>

                      <button
                        onClick={handleSave}
                        disabled={!hasChanges || saving}
                        className="px-4 py-2.5 bg-[var(--color-status-purple)] text-white rounded-xl hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors inline-flex items-center gap-2"
                      >
                        <Save className="w-4 h-4" />
                        {saving ? 'Saving...' : 'Save Changes'}
                      </button>
                    </div>
                  </div>
                </>
              ) : null}
            </div>
          )}

        </div>
      </div>
    </div>
  );
};

export default GlobalConfigurations;
