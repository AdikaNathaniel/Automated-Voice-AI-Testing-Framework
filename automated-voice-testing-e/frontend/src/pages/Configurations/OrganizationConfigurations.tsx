/**
 * Organization Configurations Page
 *
 * ORG_ADMIN-only page for managing organization-level configurations:
 * - General settings
 * - Pattern Analysis settings
 * - Categories
 *
 * Note: Integrations, CI/CD, and Slack notifications are accessed via their
 * dedicated nav pages (/integrations, /cicd-config, /integrations/slack).
 */

import React, { useEffect, useState } from 'react';
import { useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import {
  Settings,
  Bot,
  Save,
  RotateCw,
  AlertCircle,
  CheckCircle,
  Tag,
  Plus,
  Edit2,
  Trash2,
  X,
} from 'lucide-react';

import type { RootState } from '../../store';
import {
  getPatternAnalysisConfig,
  updatePatternAnalysisConfig,
  triggerManualAnalysis,
  getDefaultConfig,
} from '../../services/patternAnalysisConfig.service';
import type {
  PatternAnalysisConfig,
  PatternAnalysisConfigUpdate,
} from '../../types/patternAnalysisConfig';
import categoryService from '../../services/category.service';
import type { Category, CategoryCreate, CategoryUpdate } from '../../services/category.service';

// Tab imports removed - all features now accessed via dedicated nav pages:
// - LLMProvidersTab: Hidden for now
// - IntegrationsTab: /integrations
// - CICDTab: /cicd-config
// - NotificationsTab: /integrations/slack

type Tab = 'general' | 'pattern-analysis' | 'categories';

const ConfigurationList: React.FC = () => {
  const navigate = useNavigate();
  const user = useSelector((state: RootState) => state.auth.user);
  const isOrgAdmin = user?.role === 'org_admin';

  // Redirect non-org-admins
  useEffect(() => {
    if (user && !isOrgAdmin) {
      navigate('/dashboard');
    }
  }, [user, isOrgAdmin, navigate]);

  const [activeTab, setActiveTab] = useState<Tab>('general');
  const [config, setConfig] = useState<PatternAnalysisConfig | null>(null);
  const [formData, setFormData] = useState<Partial<PatternAnalysisConfigUpdate>>({});
  const [hasChanges, setHasChanges] = useState(false);
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [analyzing, setAnalyzing] = useState(false);

  // Categories state
  const [categories, setCategories] = useState<Category[]>([]);
  const [showCategoryModal, setShowCategoryModal] = useState(false);
  const [editingCategory, setEditingCategory] = useState<Category | null>(null);
  const [categoryFormData, setCategoryFormData] = useState({
    name: '',
    display_name: '',
    description: '',
    color: '#6B7280',
    icon: '',
    is_active: true,
  });

  useEffect(() => {
    if (activeTab === 'pattern-analysis') {
      loadPatternAnalysisConfig();
    } else if (activeTab === 'categories') {
      loadCategories();
    }
  }, [activeTab]);

  // Clear messages after 5 seconds
  useEffect(() => {
    if (success) {
      const timer = setTimeout(() => setSuccess(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [success]);

  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(null), 8000);
      return () => clearTimeout(timer);
    }
  }, [error]);

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

  const getValue = <K extends keyof PatternAnalysisConfigUpdate>(field: K): PatternAnalysisConfigUpdate[K] | PatternAnalysisConfig[K & keyof PatternAnalysisConfig] | undefined => {
    if (field in formData && formData[field] !== undefined) {
      return formData[field];
    }
    return config?.[field as keyof PatternAnalysisConfig];
  };

  // Category management functions
  const loadCategories = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await categoryService.getCategories({
        include_system: false,
      });
      setCategories(response.categories);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load categories');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateCategory = () => {
    setEditingCategory(null);
    setCategoryFormData({
      name: '',
      display_name: '',
      description: '',
      color: '#6B7280',
      icon: '',
      is_active: true,
    });
    setShowCategoryModal(true);
  };

  const handleEditCategory = (category: Category) => {
    setEditingCategory(category);
    setCategoryFormData({
      name: category.name,
      display_name: category.display_name,
      description: category.description || '',
      color: category.color || '#6B7280',
      icon: category.icon || '',
      is_active: category.is_active,
    });
    setShowCategoryModal(true);
  };

  const handleDeleteCategory = async (category: Category) => {
    if (!confirm(`Delete category "${category.display_name}"?`)) return;

    try {
      await categoryService.deleteCategory(category.id);
      await loadCategories();
      setSuccess('Category deleted successfully');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete category');
    }
  };

  const handleCategorySubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    try {
      setSaving(true);

      if (editingCategory) {
        const updateData: CategoryUpdate = {};
        if (categoryFormData.name !== editingCategory.name) updateData.name = categoryFormData.name;
        if (categoryFormData.display_name !== editingCategory.display_name) updateData.display_name = categoryFormData.display_name;
        if (categoryFormData.description !== editingCategory.description) updateData.description = categoryFormData.description;
        if (categoryFormData.color !== editingCategory.color) updateData.color = categoryFormData.color;
        if (categoryFormData.icon !== editingCategory.icon) updateData.icon = categoryFormData.icon;
        if (categoryFormData.is_active !== editingCategory.is_active) updateData.is_active = categoryFormData.is_active;

        await categoryService.updateCategory(editingCategory.id, updateData);
        setSuccess('Category updated successfully');
      } else {
        const createData: CategoryCreate = {
          name: categoryFormData.name,
          display_name: categoryFormData.display_name || categoryFormData.name,
          description: categoryFormData.description,
          color: categoryFormData.color,
          icon: categoryFormData.icon,
          is_active: categoryFormData.is_active,
        };

        await categoryService.createCategory(createData);
        setSuccess('Category created successfully');
      }

      await loadCategories();
      setShowCategoryModal(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save category');
    } finally {
      setSaving(false);
    }
  };

  const tabs = [
    { id: 'general' as Tab, label: 'General', icon: Settings },
    { id: 'pattern-analysis' as Tab, label: 'Pattern Analysis', icon: Bot },
    { id: 'categories' as Tab, label: 'Categories', icon: Tag },
  ];

  if (!isOrgAdmin) {
    return null;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-[var(--color-content-primary)] flex items-center gap-3">
            <Settings className="w-6 h-6" style={{ color: '#2A6B6E' }} />
            Organization Configurations
          </h1>
          <p className="text-sm text-[var(--color-content-muted)] mt-1">
            Configure your organization's preferences and behavior
          </p>
        </div>
      </div>

      {/* Global Messages */}
      {error && (
        <div className="bg-[var(--color-status-danger-bg)] border border-[var(--color-status-danger)] rounded-lg p-4 flex items-start justify-between">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-5 h-5 text-[var(--color-status-danger)]" />
            <p className="text-[var(--color-status-danger)]">{error}</p>
          </div>
          <button onClick={() => setError(null)} className="text-[var(--color-status-danger)] hover:text-[var(--color-status-danger)] text-sm">Dismiss</button>
        </div>
      )}
      {success && (
        <div className="bg-[var(--color-status-success-bg)] border border-[var(--color-status-success)] rounded-lg p-4 flex items-start justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle className="w-5 h-5 text-[var(--color-status-success)]" />
            <p className="text-[var(--color-status-success)]">{success}</p>
          </div>
          <button onClick={() => setSuccess(null)} className="text-[var(--color-status-success)] hover:text-[var(--color-status-success)] text-sm">Dismiss</button>
        </div>
      )}

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
                      ? 'border-primary text-primary'
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
              <div className="bg-[var(--color-surface-inset)]/50 border border-[var(--color-border-default)] rounded-lg p-6">
                <h3 className="text-lg font-semibold text-[var(--color-content-primary)] mb-4">
                  Organization Information
                </h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-2">
                      Organization Name
                    </label>
                    <input
                      type="text"
                      disabled
                      value={user?.organization_name || 'Default Organization'}
                      className="w-full px-4 py-2.5 border border-[var(--color-border-default)] rounded-xl bg-[var(--color-surface-inset)] text-[var(--color-content-muted)] cursor-not-allowed"
                    />
                    <p className="text-xs text-[var(--color-content-muted)] mt-1">
                      Contact support to change your organization name
                    </p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-2">
                      Your Role
                    </label>
                    <div className="flex items-center gap-2">
                      <span className="px-3 py-1.5 bg-primary/10 text-primary rounded-full text-sm font-medium">
                        Organization Admin
                      </span>
                    </div>
                    <p className="text-xs text-[var(--color-content-muted)] mt-1">
                      You have full access to manage this organization's settings
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-[var(--color-status-info-bg)] border border-[var(--color-status-info)] rounded-lg p-4">
                <h4 className="font-medium text-[var(--color-status-info)] mb-2">Quick Links</h4>
                <p className="text-sm text-[var(--color-status-info)]">
                  Use the tabs above to configure LLM providers, pattern analysis settings, integrations, CI/CD pipelines, and notification preferences for your organization.
                </p>
              </div>
            </div>
          )}

          {/* LLM Providers Tab - Hidden for now */}
          {/* {activeTab === 'llm-providers' && (
            <LLMProvidersTab
              onError={setError}
              onSuccess={setSuccess}
            />
          )} */}

          {/* Pattern Analysis Tab */}
          {activeTab === 'pattern-analysis' && (
            <div className="space-y-6">
              {loading ? (
                <div className="flex flex-col items-center justify-center p-12">
                  <div className="w-12 h-12 border-4 border-[var(--color-border-default)] rounded-full animate-spin mb-4" style={{ borderTopColor: '#2A6B6E' }}></div>
                  <div className="text-lg font-semibold text-[var(--color-content-primary)]">Loading configuration...</div>
                </div>
              ) : config ? (
                <>
                  {/* Analysis Controls */}
                  <div className="flex items-center justify-between flex-wrap gap-4">
                    <div>
                      <h3 className="text-lg font-semibold text-[var(--color-content-primary)]">Pattern Analysis Settings</h3>
                      <p className="text-sm text-[var(--color-content-muted)]">Configure how the system analyzes and detects patterns for your organization</p>
                    </div>
                    <div className="flex items-center gap-3 flex-wrap">
                      <button onClick={handleReset} disabled={loading} className="btn btn-secondary flex items-center gap-2">
                        <RotateCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                        Reset to Defaults
                      </button>
                      <button onClick={handleTriggerAnalysis} disabled={analyzing} className="btn btn-secondary flex items-center gap-2">
                        <Bot className={`w-4 h-4 ${analyzing ? 'animate-pulse' : ''}`} />
                        {analyzing ? 'Analyzing...' : 'Run Analysis Now'}
                      </button>
                      <button onClick={handleSave} disabled={!hasChanges || saving} className="btn btn-primary flex items-center gap-2">
                        <Save className="w-4 h-4" />
                        {saving ? 'Saving...' : 'Save Changes'}
                      </button>
                    </div>
                  </div>

                  {/* Time Window Settings */}
                  <div className="bg-[var(--color-surface-inset)]/50 border border-[var(--color-border-default)] rounded-lg p-5">
                    <h4 className="font-semibold text-[var(--color-content-primary)] mb-4">Time Window Settings</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-2">
                          Lookback Period (days)
                        </label>
                        <input
                          type="number"
                          min="1"
                          max="365"
                          value={getValue('lookback_days') ?? 30}
                          onChange={(e) => handleFieldChange('lookback_days', parseInt(e.target.value))}
                          className="w-full px-4 py-2.5 border border-[var(--color-border-default)] bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] rounded-lg"
                        />
                        <p className="text-xs text-[var(--color-content-muted)] mt-1">Analyze edge cases from the last N days</p>
                      </div>
                      <div className="flex items-start pt-8">
                        <div className="bg-[var(--color-status-info-bg)] border border-[var(--color-status-info)] rounded-lg p-3">
                          <p className="text-xs text-[var(--color-status-info)]">
                            <strong>Tip:</strong> A shorter lookback period (7-14 days) focuses on recent issues.
                            A longer period (30-90 days) catches recurring patterns.
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Pattern Formation & Defect Settings */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Pattern Formation */}
                    <div className="bg-[var(--color-surface-inset)]/50 border border-[var(--color-border-default)] rounded-lg p-5">
                      <h4 className="font-semibold text-[var(--color-content-primary)] mb-4">Pattern Formation</h4>
                      <div className="space-y-4">
                        <div>
                          <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-2">
                            Minimum Pattern Size
                          </label>
                          <input
                            type="number"
                            min="2"
                            max="50"
                            value={getValue('min_pattern_size') ?? 3}
                            onChange={(e) => handleFieldChange('min_pattern_size', parseInt(e.target.value))}
                            className="w-full px-4 py-2.5 border border-[var(--color-border-default)] bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] rounded-lg"
                          />
                          <p className="text-xs text-[var(--color-content-muted)] mt-1">Minimum edge cases required to form a pattern</p>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-2">
                            Similarity Threshold ({((getValue('similarity_threshold') as number) ?? 0.85) * 100}%)
                          </label>
                          <input
                            type="range"
                            min="0.5"
                            max="1"
                            step="0.05"
                            value={getValue('similarity_threshold') ?? 0.85}
                            onChange={(e) => handleFieldChange('similarity_threshold', parseFloat(e.target.value))}
                            className="w-full accent-primary"
                          />
                          <p className="text-xs text-[var(--color-content-muted)] mt-1">Semantic similarity threshold (0.0 - 1.0)</p>
                        </div>
                      </div>
                    </div>

                    {/* Defect Auto-Creation */}
                    <div className="bg-[var(--color-surface-inset)]/50 border border-[var(--color-border-default)] rounded-lg p-5">
                      <h4 className="font-semibold text-[var(--color-content-primary)] mb-4">Defect Auto-Creation</h4>
                      <div className="space-y-4">
                        <div>
                          <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-2">
                            Consecutive Failure Threshold
                          </label>
                          <input
                            type="number"
                            min="1"
                            max="100"
                            value={getValue('defect_auto_creation_threshold') ?? 3}
                            onChange={(e) => handleFieldChange('defect_auto_creation_threshold', parseInt(e.target.value))}
                            className="w-full px-4 py-2.5 border border-[var(--color-border-default)] bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] rounded-lg"
                          />
                          <p className="text-xs text-[var(--color-content-muted)] mt-1">Number of consecutive AI validation failures before creating a defect</p>
                        </div>
                        <div className="bg-[var(--color-status-amber-bg)] border border-[var(--color-status-amber-bg)] rounded-lg p-3">
                          <p className="text-xs text-[var(--color-status-amber)]">
                            <strong>How it works:</strong> When AI validation fails (<code className="bg-[var(--color-status-amber-bg)] px-1 rounded">auto_fail</code>) {getValue('defect_auto_creation_threshold') ?? 3} times consecutively,
                            a defect is automatically created. Any pass or human review resets the counter.
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* AI/LLM Settings */}
                  <div className="bg-[var(--color-surface-inset)]/50 border border-[var(--color-border-default)] rounded-lg p-5">
                    <h4 className="font-semibold text-[var(--color-content-primary)] mb-4">AI/LLM Settings</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <label className="flex items-center gap-3 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={getValue('enable_llm_analysis') ?? true}
                          onChange={(e) => handleFieldChange('enable_llm_analysis', e.target.checked)}
                          className="w-5 h-5 text-primary bg-[var(--color-surface-inset)] border-[var(--color-border-default)] rounded focus:ring-primary"
                        />
                        <div>
                          <span className="text-sm font-medium text-[var(--color-content-primary)]">Enable LLM-powered analysis</span>
                          <p className="text-xs text-[var(--color-content-muted)]">Use AI for advanced pattern matching</p>
                        </div>
                      </label>
                      <div>
                        <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-2">
                          LLM Confidence Threshold
                        </label>
                        <input
                          type="number"
                          min="0"
                          max="1"
                          step="0.05"
                          value={getValue('llm_confidence_threshold') ?? 0.7}
                          onChange={(e) => handleFieldChange('llm_confidence_threshold', parseFloat(e.target.value))}
                          disabled={!getValue('enable_llm_analysis')}
                          className="w-full px-4 py-2.5 border border-[var(--color-border-default)] bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
                        />
                        <p className="text-xs text-[var(--color-content-muted)] mt-1">Minimum LLM confidence for pattern matching</p>
                      </div>
                    </div>
                  </div>

                  {/* Scheduling & Notifications */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Scheduling */}
                    <div className="bg-[var(--color-surface-inset)]/50 border border-[var(--color-border-default)] rounded-lg p-5">
                      <h4 className="font-semibold text-[var(--color-content-primary)] mb-4">Scheduling</h4>
                      <div className="space-y-4">
                        <label className="flex items-center gap-3 cursor-pointer">
                          <input
                            type="checkbox"
                            checked={getValue('enable_auto_analysis') ?? true}
                            onChange={(e) => handleFieldChange('enable_auto_analysis', e.target.checked)}
                            className="w-5 h-5 text-primary bg-[var(--color-surface-inset)] border-[var(--color-border-default)] rounded focus:ring-primary"
                          />
                          <div>
                            <span className="text-sm font-medium text-[var(--color-content-primary)]">Enable automatic analysis</span>
                            <p className="text-xs text-[var(--color-content-muted)]">Run pattern analysis on the global schedule set by super admin</p>
                          </div>
                        </label>
                        <div className="bg-[var(--color-status-info-bg)] border border-[var(--color-status-info)] rounded-lg p-3">
                          <p className="text-xs text-[var(--color-status-info)]">
                            <strong>Note:</strong> The analysis schedule (cron) is configured globally by the super admin.
                            Toggle this setting to opt your organization in or out of scheduled analysis.
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Notifications */}
                    <div className="bg-[var(--color-surface-inset)]/50 border border-[var(--color-border-default)] rounded-lg p-5">
                      <h4 className="font-semibold text-[var(--color-content-primary)] mb-4">Notifications</h4>
                      <div className="space-y-4">
                        <label className="flex items-center gap-3 cursor-pointer">
                          <input
                            type="checkbox"
                            checked={getValue('notify_on_new_patterns') ?? true}
                            onChange={(e) => handleFieldChange('notify_on_new_patterns', e.target.checked)}
                            className="w-5 h-5 text-primary bg-[var(--color-surface-inset)] border-[var(--color-border-default)] rounded focus:ring-primary"
                          />
                          <div>
                            <span className="text-sm font-medium text-[var(--color-content-primary)]">Notify on new patterns</span>
                            <p className="text-xs text-[var(--color-content-muted)]">Send notifications when new patterns are discovered</p>
                          </div>
                        </label>
                        <label className="flex items-center gap-3 cursor-pointer">
                          <input
                            type="checkbox"
                            checked={getValue('notify_on_critical_patterns') ?? true}
                            onChange={(e) => handleFieldChange('notify_on_critical_patterns', e.target.checked)}
                            className="w-5 h-5 text-primary bg-[var(--color-surface-inset)] border-[var(--color-border-default)] rounded focus:ring-primary"
                          />
                          <div>
                            <span className="text-sm font-medium text-[var(--color-content-primary)]">Alert on critical patterns</span>
                            <p className="text-xs text-[var(--color-content-muted)]">Send alerts for critical severity patterns</p>
                          </div>
                        </label>
                      </div>
                    </div>
                  </div>

                  {/* Performance Settings */}
                  <div className="bg-[var(--color-surface-inset)]/50 border border-[var(--color-border-default)] rounded-lg p-5">
                    <h4 className="font-semibold text-[var(--color-content-primary)] mb-4">Performance Settings</h4>
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
                          className="w-full px-4 py-2.5 border border-[var(--color-border-default)] bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] rounded-lg"
                        />
                        <p className="text-xs text-[var(--color-content-muted)] mt-1">Maximum acceptable response time in milliseconds (100-30000)</p>
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

                  {/* Current Status */}
                  <div className="bg-[var(--color-surface-inset)]/50 border border-[var(--color-border-default)] rounded-lg p-5">
                    <h4 className="font-semibold text-[var(--color-content-primary)] mb-4">Current Configuration</h4>
                    <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
                      <div className="text-center p-3 bg-[var(--color-surface-raised)] rounded-lg border border-[var(--color-border-default)]">
                        <div className="text-2xl font-bold text-primary">{config.enable_auto_analysis ? 'On' : 'Off'}</div>
                        <div className="text-xs text-[var(--color-content-muted)]">Auto Analysis</div>
                      </div>
                      <div className="text-center p-3 bg-[var(--color-surface-raised)] rounded-lg border border-[var(--color-border-default)]">
                        <div className="text-2xl font-bold text-[var(--color-content-primary)]">{config.lookback_days}</div>
                        <div className="text-xs text-[var(--color-content-muted)]">Lookback (days)</div>
                      </div>
                      <div className="text-center p-3 bg-[var(--color-surface-raised)] rounded-lg border border-[var(--color-border-default)]">
                        <div className="text-2xl font-bold text-[var(--color-content-primary)]">{(config.similarity_threshold * 100).toFixed(0)}%</div>
                        <div className="text-xs text-[var(--color-content-muted)]">Similarity</div>
                      </div>
                      <div className="text-center p-3 bg-[var(--color-surface-raised)] rounded-lg border border-[var(--color-border-default)]">
                        <div className="text-2xl font-bold text-[var(--color-content-primary)]">{config.min_pattern_size}</div>
                        <div className="text-xs text-[var(--color-content-muted)]">Min Size</div>
                      </div>
                      <div className="text-center p-3 bg-[var(--color-surface-raised)] rounded-lg border border-[var(--color-border-default)]">
                        <div className="text-2xl font-bold text-[var(--color-content-primary)]">{config.defect_auto_creation_threshold}</div>
                        <div className="text-xs text-[var(--color-content-muted)]">Defect Threshold</div>
                      </div>
                      <div className="text-center p-3 bg-[var(--color-surface-raised)] rounded-lg border border-[var(--color-border-default)]">
                        <div className="text-2xl font-bold text-[var(--color-content-primary)]">{config.response_time_sla_ms ?? 2000}ms</div>
                        <div className="text-xs text-[var(--color-content-muted)]">SLA</div>
                      </div>
                    </div>
                  </div>
                </>
              ) : (
                <div className="text-center py-12">
                  <AlertCircle className="w-12 h-12 text-[var(--color-content-muted)] mx-auto mb-4" />
                  <p className="text-[var(--color-content-secondary)]">No configuration found</p>
                </div>
              )}
            </div>
          )}

          {/* Categories Tab */}
          {activeTab === 'categories' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-[var(--color-content-primary)]">Scenario Categories</h3>
                  <p className="text-sm text-[var(--color-content-muted)]">Manage categories for organizing test scenarios</p>
                </div>
                <button onClick={handleCreateCategory} className="btn btn-primary flex items-center gap-2">
                  <Plus className="w-4 h-4" />
                  Add Category
                </button>
              </div>

              {loading ? (
                <div className="flex flex-col items-center justify-center p-12">
                  <div className="w-12 h-12 border-4 border-[var(--color-border-default)] rounded-full animate-spin mb-4" style={{ borderTopColor: '#2A6B6E' }}></div>
                  <div className="text-lg font-semibold text-[var(--color-content-primary)]">Loading categories...</div>
                </div>
              ) : categories.length === 0 ? (
                <div className="text-center py-12 bg-[var(--color-surface-inset)]/50 border border-[var(--color-border-default)] rounded-lg">
                  <Tag className="w-12 h-12 text-[var(--color-content-muted)] mx-auto mb-4" />
                  <h4 className="font-medium text-[var(--color-content-primary)] mb-2">No Categories Yet</h4>
                  <p className="text-[var(--color-content-secondary)] mb-4">Create your first category to organize test scenarios</p>
                  <button onClick={handleCreateCategory} className="btn btn-primary">
                    <Plus className="w-4 h-4 mr-2" />
                    Create Category
                  </button>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {categories.map((category) => (
                    <div
                      key={category.id}
                      className="bg-[var(--color-surface-raised)] border border-[var(--color-border-default)] rounded-lg p-4 hover:shadow-md transition-shadow"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex items-center gap-3">
                          <div
                            className="w-10 h-10 rounded-lg flex items-center justify-center text-white"
                            style={{ backgroundColor: category.color || '#6B7280' }}
                          >
                            {category.icon ? (
                              <span className="text-lg">{category.icon}</span>
                            ) : (
                              <Tag className="w-5 h-5" />
                            )}
                          </div>
                          <div>
                            <h4 className="font-semibold text-[var(--color-content-primary)]">{category.display_name}</h4>
                            <p className="text-xs text-[var(--color-content-muted)]">{category.name}</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-1">
                          <button
                            onClick={() => handleEditCategory(category)}
                            className="p-1.5 text-[var(--color-content-muted)] hover:text-[var(--color-content-secondary)]"
                            title="Edit category"
                          >
                            <Edit2 className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleDeleteCategory(category)}
                            className="p-1.5 text-[var(--color-content-muted)] hover:text-[var(--color-status-danger)]"
                            title="Delete category"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                      {category.description && (
                        <p className="text-sm text-[var(--color-content-secondary)] mt-3">{category.description}</p>
                      )}
                      <div className="mt-3 flex items-center gap-2">
                        <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                          category.is_active
                            ? 'bg-[var(--color-status-success-bg)] text-[var(--color-status-success)]'
                            : 'bg-[var(--color-surface-inset)] text-[var(--color-content-secondary)]'
                        }`}>
                          {category.is_active ? 'Active' : 'Inactive'}
                        </span>
                        {category.is_system && (
                          <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-[var(--color-status-info-bg)] text-[var(--color-status-info)]">
                            System
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Category Modal */}
              {showCategoryModal && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                  <div className="bg-[var(--color-surface-raised)] rounded-xl shadow-xl max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto">
                    <div className="flex items-center justify-between p-5 border-b border-[var(--color-border-default)]">
                      <h3 className="text-lg font-semibold text-[var(--color-content-primary)]">
                        {editingCategory ? 'Edit Category' : 'Create Category'}
                      </h3>
                      <button onClick={() => setShowCategoryModal(false)} className="text-[var(--color-content-muted)] hover:text-[var(--color-content-secondary)]">
                        <X className="w-5 h-5" />
                      </button>
                    </div>
                    <form onSubmit={handleCategorySubmit} className="p-5 space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-2">Name (identifier)</label>
                        <input
                          type="text"
                          value={categoryFormData.name}
                          onChange={(e) => setCategoryFormData(prev => ({ ...prev, name: e.target.value.toLowerCase().replace(/\s+/g, '_') }))}
                          required
                          placeholder="category_name"
                          className="w-full px-4 py-2.5 border border-[var(--color-border-default)] bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] rounded-lg"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-2">Display Name</label>
                        <input
                          type="text"
                          value={categoryFormData.display_name}
                          onChange={(e) => setCategoryFormData(prev => ({ ...prev, display_name: e.target.value }))}
                          placeholder="Category Name"
                          className="w-full px-4 py-2.5 border border-[var(--color-border-default)] bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] rounded-lg"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-2">Description</label>
                        <textarea
                          value={categoryFormData.description}
                          onChange={(e) => setCategoryFormData(prev => ({ ...prev, description: e.target.value }))}
                          rows={3}
                          placeholder="Optional description..."
                          className="w-full px-4 py-2.5 border border-[var(--color-border-default)] bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] rounded-lg"
                        />
                      </div>
                      <div className="flex items-center gap-4">
                        <div className="flex-1">
                          <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-2">Color</label>
                          <div className="flex items-center gap-2">
                            <input
                              type="color"
                              value={categoryFormData.color}
                              onChange={(e) => setCategoryFormData(prev => ({ ...prev, color: e.target.value }))}
                              className="w-10 h-10 rounded border border-[var(--color-border-default)] cursor-pointer"
                            />
                            <input
                              type="text"
                              value={categoryFormData.color}
                              onChange={(e) => setCategoryFormData(prev => ({ ...prev, color: e.target.value }))}
                              className="flex-1 px-3 py-2 border border-[var(--color-border-default)] bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] rounded-lg text-sm"
                            />
                          </div>
                        </div>
                        <div className="flex-1">
                          <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-2">Icon (emoji)</label>
                          <input
                            type="text"
                            value={categoryFormData.icon}
                            onChange={(e) => setCategoryFormData(prev => ({ ...prev, icon: e.target.value }))}
                            placeholder="e.g. 📱"
                            className="w-full px-4 py-2.5 border border-[var(--color-border-default)] bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] rounded-lg"
                          />
                        </div>
                      </div>
                      <label className="flex items-center gap-3 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={categoryFormData.is_active}
                          onChange={(e) => setCategoryFormData(prev => ({ ...prev, is_active: e.target.checked }))}
                          className="w-5 h-5 text-primary bg-[var(--color-surface-inset)] border-[var(--color-border-default)] rounded focus:ring-primary"
                        />
                        <span className="text-sm font-medium text-[var(--color-content-primary)]">Active</span>
                      </label>
                      <div className="flex justify-end gap-3 pt-4 border-t border-[var(--color-border-default)]">
                        <button type="button" onClick={() => setShowCategoryModal(false)} className="btn btn-secondary">Cancel</button>
                        <button type="submit" disabled={saving} className="btn btn-primary">
                          {saving ? 'Saving...' : editingCategory ? 'Update' : 'Create'}
                        </button>
                      </div>
                    </form>
                  </div>
                </div>
              )}
            </div>
          )}

        </div>
      </div>
    </div>
  );
};

export default ConfigurationList;
