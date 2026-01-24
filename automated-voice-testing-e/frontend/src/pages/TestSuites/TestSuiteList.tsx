/**
 * Test Suite List Page
 *
 * Displays all test suites with:
 * - Filtering by status and category
 * - Search functionality
 * - Create, Edit, Delete suite operations
 * - Run all scenarios in suite
 * - Manage scenarios in suite
 */

import React, { useState, useEffect } from 'react';
import {
  Play,
  Plus,
  Edit2,
  Trash2,
  Layers,
  FolderOpen,
  Check,
  MoreVertical,
  X,
  Tag,
  Globe,
  ArrowRight,
  Zap,
  ChevronRight,
  FileText,
  Search,
} from 'lucide-react';
import { SearchInput, Dropdown } from '../../components/common';
import {
  getTestSuites,
  getTestSuiteWithScenarios,
  createTestSuite,
  updateTestSuite,
  deleteTestSuite,
  addScenariosToSuite,
  removeScenariosFromSuite,
  runTestSuite,
  getCategoricalSuites,
  type TestSuite,
  type TestSuiteWithScenarios,
  type CategoricalSuite,
  type LanguageConfig,
} from '../../services/testSuite.service';
import { multiTurnService } from '../../services/multiTurn.service';
import type { ScenarioScript } from '../../types/multiTurn';
import Modal from '../../components/Modal/Modal';
import { useModal } from '../../hooks/useModal';
import LanguageConfigForm from '../../components/TestSuites/LanguageConfigForm';

const TestSuiteList: React.FC = () => {
  const { modalState, showError, showSuccess, closeModal } = useModal();
  const [suites, setSuites] = useState<TestSuite[]>([]);
  const [categoricalSuites, setCategoricalSuites] = useState<CategoricalSuite[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [executing, setExecuting] = useState<string | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);

  // Create/Edit modal state
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [createStep, setCreateStep] = useState<'method' | 'details'>('method');
  const [selectedCategory, setSelectedCategory] = useState<CategoricalSuite | null>(null);
  const [editingSuite, setEditingSuite] = useState<TestSuite | null>(null);
  const [formData, setFormData] = useState({ name: '', description: '', category: '' });
  const [languageConfig, setLanguageConfig] = useState<LanguageConfig | null>(null);
  const [createSelectedScenarios, setCreateSelectedScenarios] = useState<string[]>([]);
  const [createScenarioSearch, setCreateScenarioSearch] = useState('');

  // Manage scenarios modal state
  const [managingSuite, setManagingSuite] = useState<TestSuiteWithScenarios | null>(null);
  const [availableScenarios, setAvailableScenarios] = useState<ScenarioScript[]>([]);
  const [selectedScenarioIds, setSelectedScenarioIds] = useState<string[]>([]);
  const [loadingScenarios, setLoadingScenarios] = useState(false);
  const [scenarioSearch, setScenarioSearch] = useState('');

  useEffect(() => {
    loadSuites();
  }, [statusFilter]);

  const loadSuites = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load both custom and categorical suites in parallel
      const [customResponse, categoricalResponse] = await Promise.all([
        getTestSuites({
          is_active: statusFilter === 'active' ? true : statusFilter === 'inactive' ? false : undefined,
        }),
        getCategoricalSuites(),
      ]);

      setSuites(customResponse.test_suites || []);
      setCategoricalSuites(categoricalResponse.categorical_suites || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load test suites');
    } finally {
      setLoading(false);
    }
  };

  const handleRunSuite = async (suiteId: string) => {
    try {
      setExecuting(suiteId);
      const result = await runTestSuite(suiteId);
      showSuccess(`Suite execution started! Running ${result.total_scenarios} scenarios.`);
      // Could navigate to a suite execution details page if available
      // navigate(`/test-suites/executions/${result.suite_run_id}`);
    } catch (err: any) {
      showError(`Failed to run suite: ${err.message}`);
    } finally {
      setExecuting(null);
    }
  };

  const handleSelectCategory = (suite: CategoricalSuite) => {
    setSelectedCategory(suite);
    setFormData({
      name: suite.name,
      description: `${suite.name} - Auto-generated suite`,
      category: suite.name.toLowerCase().replace(/\s+/g, '_'),
    });
    setCreateSelectedScenarios(suite.scenario_ids);
    setCreateStep('details');
  };

  const handleCreateFromCategory = async () => {
    if (!selectedCategory) return;

    try {
      setExecuting(selectedCategory.name);

      await createTestSuite({
        name: formData.name || selectedCategory.name,
        description: formData.description || `${selectedCategory.name} - Created by category`,
        category: formData.category || selectedCategory.name.toLowerCase().replace(/\s+/g, '_'),
        is_active: true,
        scenario_ids: selectedCategory.scenario_ids,
        language_config: languageConfig,
      });

      showSuccess(`Test suite "${formData.name || selectedCategory.name}" created with ${selectedCategory.scenario_count} scenarios!`);

      // Close modal and reload suites
      resetCreateModal();
      loadSuites();
    } catch (err: any) {
      showError(`Failed to create suite from category: ${err.message}`);
    } finally {
      setExecuting(null);
    }
  };

  const resetCreateModal = () => {
    setShowCreateModal(false);
    setCreateStep('method');
    setSelectedCategory(null);
    setFormData({ name: '', description: '', category: '' });
    setLanguageConfig(null);
    setCreateSelectedScenarios([]);
    setCreateScenarioSearch('');
  };

  const handleDeleteSuite = async (suiteId: string) => {
    try {
      await deleteTestSuite(suiteId);
      setDeleteConfirm(null);
      loadSuites();
      showSuccess('Test suite deleted successfully');
    } catch (err: any) {
      showError(`Failed to delete suite: ${err.message}`);
    }
  };

  const handleCreateSuite = async () => {
    try {
      if (!formData.name.trim()) {
        showError('Suite name is required');
        return;
      }
      await createTestSuite({
        name: formData.name,
        description: formData.description || undefined,
        category: formData.category || undefined,
        language_config: languageConfig || undefined,
        scenario_ids: createSelectedScenarios.length > 0 ? createSelectedScenarios : undefined,
      });
      setShowCreateModal(false);
      setFormData({ name: '', description: '', category: '' });
      setLanguageConfig(null);
      setCreateSelectedScenarios([]);
      setCreateScenarioSearch('');
      loadSuites();
      showSuccess('Test suite created successfully');
    } catch (err: any) {
      showError(`Failed to create suite: ${err.message}`);
    }
  };

  const openCreateModal = async () => {
    setShowCreateModal(true);
    setFormData({ name: '', description: '', category: '' });
    setLanguageConfig(null);
    setCreateSelectedScenarios([]);
    setCreateScenarioSearch('');
    setAvailableScenarios([]); // Reset to show loading state

    // Load available scenarios
    try {
      const response = await multiTurnService.listScenarios({ is_active: true });
      setAvailableScenarios(response.scenarios || []);
    } catch (err) {
      console.error('Failed to load scenarios:', err);
      showError('Failed to load scenarios. Please try again.');
      setAvailableScenarios([]);
    }
  };

  const handleUpdateSuite = async () => {
    try {
      if (!editingSuite || !formData.name.trim()) {
        showError('Suite name is required');
        return;
      }
      await updateTestSuite(editingSuite.id, {
        name: formData.name,
        description: formData.description || undefined,
        category: formData.category || undefined,
        language_config: languageConfig || undefined,
      });
      setEditingSuite(null);
      setFormData({ name: '', description: '', category: '' });
      setLanguageConfig(null);
      loadSuites();
      showSuccess('Test suite updated successfully');
    } catch (err: any) {
      showError(`Failed to update suite: ${err.message}`);
    }
  };

  const openEditModal = (suite: TestSuite) => {
    setEditingSuite(suite);
    setLanguageConfig(suite.language_config || null);
    setFormData({
      name: suite.name,
      description: suite.description || '',
      category: suite.category || '',
    });
  };

  const openManageScenariosModal = async (suiteId: string) => {
    try {
      setLoadingScenarios(true);
      const [suiteWithScenarios, scenariosResponse] = await Promise.all([
        getTestSuiteWithScenarios(suiteId),
        multiTurnService.listScenarios({ is_active: true }),
      ]);
      setManagingSuite(suiteWithScenarios);
      setAvailableScenarios(scenariosResponse.scenarios || []);
      setSelectedScenarioIds(suiteWithScenarios.scenarios.map((s) => s.scenario_id));
    } catch (err: any) {
      showError(`Failed to load scenarios: ${err.message}`);
    } finally {
      setLoadingScenarios(false);
    }
  };

  const handleToggleScenario = (scenarioId: string) => {
    setSelectedScenarioIds((prev) =>
      prev.includes(scenarioId)
        ? prev.filter((id) => id !== scenarioId)
        : [...prev, scenarioId]
    );
  };

  const handleSaveScenarios = async () => {
    if (!managingSuite) return;

    try {
      const currentIds = managingSuite.scenarios.map((s) => s.scenario_id);
      const toAdd = selectedScenarioIds.filter((id) => !currentIds.includes(id));
      const toRemove = currentIds.filter((id) => !selectedScenarioIds.includes(id));

      if (toAdd.length > 0) {
        await addScenariosToSuite(managingSuite.id, toAdd);
      }
      if (toRemove.length > 0) {
        await removeScenariosFromSuite(managingSuite.id, toRemove);
      }

      setManagingSuite(null);
      setScenarioSearch('');
      showSuccess('Scenarios updated successfully');
    } catch (err: any) {
      showError(`Failed to update scenarios: ${err.message}`);
    }
  };

  // Filter custom suites
  const filteredCustomSuites = suites.filter(
    (suite) =>
      suite.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (suite.description && suite.description.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const hasResults = filteredCustomSuites.length > 0;

  return (
    <>
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-bold text-[var(--color-content-primary)] flex items-center gap-3">
            <Layers className="w-6 h-6" style={{ color: '#2A6B6E' }} />
            Test Suites
          </h1>
          <p className="text-sm text-[var(--color-content-secondary)] mt-1">
            Group and run multiple scenarios together
          </p>
        </div>
        <button
          onClick={openCreateModal}
          className="px-4 py-2.5 rounded-lg text-sm font-semibold transition-all inline-flex items-center gap-2 text-white hover:shadow-lg hover:-translate-y-0.5"
          style={{ background: 'linear-gradient(135deg, #2A6B6E 0%, #11484D 100%)' }}
        >
          <Plus size={14} /> Create Suite
        </button>
      </div>

      {/* Filter Bar */}
      <div className="bg-[var(--color-surface-raised)] p-4 rounded-xl mb-5 shadow-sm flex flex-col sm:flex-row gap-3 sm:items-center">
        <SearchInput
          placeholder="Search test suites..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
        <Dropdown
          value={statusFilter}
          onChange={setStatusFilter}
          options={[
            { value: 'all', label: 'All Status' },
            { value: 'active', label: 'Active Only' },
            { value: 'inactive', label: 'Inactive Only' },
          ]}
        />
      </div>

      {/* Loading State */}
      {loading && (
        <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-sm">
          <div className="flex flex-col items-center justify-center p-20">
            <div
              className="w-12 h-12 border-4 border-[var(--color-border-default)] rounded-full animate-spin mb-4"
              style={{ borderTopColor: '#2A6B6E' }}
            ></div>
            <div className="text-lg font-semibold text-[var(--color-content-primary)] mb-2">Loading Test Suites...</div>
          </div>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-sm">
          <div className="p-10 text-center text-[var(--color-status-danger)]">{error}</div>
        </div>
      )}

      {/* Suites Grid */}
      {!loading && !error && hasResults && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredCustomSuites.map((suite) => (
            <SuiteCard
              key={suite.id}
              suite={suite}
              onRun={handleRunSuite}
              onEdit={openEditModal}
              onDelete={handleDeleteSuite}
              onManageScenarios={openManageScenariosModal}
              executing={executing === suite.id}
              deleteConfirm={deleteConfirm}
              setDeleteConfirm={setDeleteConfirm}
            />
          ))}
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && !hasResults && (
        <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-sm">
          <div className="text-center py-12">
            <FolderOpen className="w-16 h-16 mx-auto text-[var(--color-content-muted)] mb-4" />
            <p className="text-[var(--color-content-secondary)] mb-4">No test suites found</p>
            <button
              onClick={openCreateModal}
              className="px-4 py-2 rounded-lg text-sm font-medium text-white"
              style={{ background: 'linear-gradient(135deg, #2A6B6E 0%, #11484D 100%)' }}
            >
              Create your first suite
            </button>
          </div>
        </div>
      )}

      {/* Enhanced Create Suite Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-[var(--color-surface-raised)] rounded-2xl w-full max-w-3xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
            {/* Modal Header */}
            <div className="px-6 py-5 border-b border-[var(--color-border-default)] bg-gradient-to-r from-[var(--color-surface-raised)] to-[var(--color-surface-inset)]">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg" style={{ background: 'linear-gradient(135deg, #2A6B6E 0%, #11484D 100%)' }}>
                    <Layers className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h2 className="text-xl font-bold text-[var(--color-content-primary)]">
                      {createStep === 'method' ? 'Create Test Suite' : selectedCategory ? `Create from "${selectedCategory.name}"` : 'Configure Suite'}
                    </h2>
                    <p className="text-sm text-[var(--color-content-muted)] mt-0.5">
                      {createStep === 'method' ? 'Choose how to start building your suite' : 'Configure your test suite details'}
                    </p>
                  </div>
                </div>
                <button
                  onClick={resetCreateModal}
                  className="p-2 hover:bg-[var(--color-interactive-hover)] rounded-lg transition-colors"
                >
                  <X className="w-5 h-5 text-[var(--color-content-muted)]" />
                </button>
              </div>

              {/* Step Indicator */}
              <div className="flex items-center gap-3 mt-4">
                <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium transition-all ${
                  createStep === 'method'
                    ? 'bg-[#2A6B6E]/10 text-[#2A6B6E] border border-[#2A6B6E]/30'
                    : 'bg-[var(--color-status-success-bg)] text-[var(--color-status-success)]'
                }`}>
                  {createStep === 'method' ? (
                    <span className="w-5 h-5 rounded-full bg-[#2A6B6E] text-white flex items-center justify-center text-xs font-bold">1</span>
                  ) : (
                    <Check className="w-4 h-4" />
                  )}
                  Choose Method
                </div>
                <ChevronRight className="w-4 h-4 text-[var(--color-content-muted)]" />
                <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium transition-all ${
                  createStep === 'details'
                    ? 'bg-[#2A6B6E]/10 text-[#2A6B6E] border border-[#2A6B6E]/30'
                    : 'bg-[var(--color-surface-inset)] text-[var(--color-content-muted)]'
                }`}>
                  <span className="w-5 h-5 rounded-full bg-[var(--color-interactive-active)] text-[var(--color-content-secondary)] flex items-center justify-center text-xs font-bold">2</span>
                  Configure Details
                </div>
              </div>
            </div>

            {/* Modal Body */}
            <div className="flex-1 overflow-y-auto p-6">
              {/* Step 1: Method Selection */}
              {createStep === 'method' && (
                <div className="space-y-4">
                  {/* Start from Scratch Option */}
                  <button
                    onClick={() => {
                      setSelectedCategory(null);
                      setFormData({ name: '', description: '', category: '' });
                      setCreateSelectedScenarios([]);
                      setCreateStep('details');
                    }}
                    className="w-full p-5 rounded-xl border-2 border-[var(--color-border-default)] hover:border-[#2A6B6E] hover:border-[var(--color-accent-500)] bg-[var(--color-surface-raised)] hover:bg-[var(--color-brand-muted)] transition-all text-left group"
                  >
                    <div className="flex items-start gap-4">
                      <div className="p-3 rounded-lg bg-[var(--color-surface-inset)] group-hover:bg-[#2A6B6E]/20 transition-colors">
                        <FileText className="w-6 h-6 text-[var(--color-content-secondary)] group-hover:text-[#2A6B6E]" />
                      </div>
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-[var(--color-content-primary)] group-hover:text-[#2A6B6E] transition-colors">
                          Start from Scratch
                        </h3>
                        <p className="text-sm text-[var(--color-content-muted)] mt-1">
                          Create an empty suite and manually select which scenarios to include
                        </p>
                      </div>
                      <ArrowRight className="w-5 h-5 text-[var(--color-content-muted)] group-hover:text-[#2A6B6E] group-hover:translate-x-1 transition-all" />
                    </div>
                  </button>

                  {/* Divider */}
                  <div className="flex items-center gap-4">
                    <div className="flex-1 h-px bg-[var(--color-interactive-active)]"></div>
                    <span className="text-sm text-[var(--color-content-muted)] font-medium">OR</span>
                    <div className="flex-1 h-px bg-[var(--color-interactive-active)]"></div>
                  </div>

                  {/* Quick Start from Category */}
                  <div className="space-y-3">
                    <div className="flex items-center gap-2">
                      <Zap className="w-5 h-5 text-[#2A6B6E]" />
                      <h3 className="text-base font-semibold text-[var(--color-content-primary)]">Quick Start from Category</h3>
                      <span className="px-2 py-0.5 bg-[#2A6B6E]/10 text-[#2A6B6E] rounded-full text-xs font-medium">
                        {categoricalSuites.length} available
                      </span>
                    </div>
                    <p className="text-sm text-[var(--color-content-muted)]">
                      Start with all scenarios from a category pre-selected
                    </p>

                    {categoricalSuites.length === 0 ? (
                      <div className="p-6 text-center bg-[var(--color-surface-inset)]/50 rounded-xl border border-[var(--color-border-default)]">
                        <Tag className="w-8 h-8 text-[var(--color-content-muted)] mx-auto mb-2" />
                        <p className="text-sm text-[var(--color-content-muted)]">No category templates available yet</p>
                        <p className="text-xs text-[var(--color-content-muted)] mt-1">Categories are created based on your scenarios</p>
                      </div>
                    ) : (
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        {categoricalSuites.map((cat) => (
                          <button
                            key={cat.name}
                            onClick={() => handleSelectCategory(cat)}
                            className="p-4 rounded-xl border-2 border-dashed border-[var(--color-border-default)] hover:border-[#2A6B6E] hover:border-[var(--color-accent-500)] bg-gradient-to-br from-[var(--color-surface-raised)] to-[var(--color-surface-inset)] hover:from-[#2A6B6E]/5 hover:to-[#11484D]/5 transition-all text-left group"
                          >
                            <div className="flex items-center justify-between mb-2">
                              <div className="flex items-center gap-2">
                                <Tag className="w-4 h-4 text-[#2A6B6E]" />
                                <span className="font-semibold text-[var(--color-content-primary)] group-hover:text-[#2A6B6E] transition-colors">
                                  {cat.name}
                                </span>
                              </div>
                              <ArrowRight className="w-4 h-4 text-[var(--color-content-muted)] group-hover:text-[#2A6B6E] group-hover:translate-x-1 transition-all" />
                            </div>
                            <div className="flex items-center gap-2">
                              <span className="px-2 py-0.5 bg-[var(--color-surface-inset)] text-[var(--color-content-secondary)] rounded-full text-xs">
                                {cat.scenario_count} scenario{cat.scenario_count !== 1 ? 's' : ''}
                              </span>
                            </div>
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Step 2: Details Configuration */}
              {createStep === 'details' && (
                <div className="space-y-5">
                  {/* Selected Category Banner */}
                  {selectedCategory && (
                    <div className="p-4 bg-gradient-to-r from-[#2A6B6E]/10 to-[#11484D]/10 rounded-xl border border-[#2A6B6E]/30">
                      <div className="flex items-center gap-3">
                        <div className="p-2 bg-[#2A6B6E]/20 rounded-lg">
                          <Tag className="w-5 h-5 text-[#2A6B6E]" />
                        </div>
                        <div className="flex-1">
                          <p className="text-sm font-medium text-[var(--color-content-primary)]">
                            Starting from "{selectedCategory.name}" category
                          </p>
                          <p className="text-xs text-[var(--color-content-secondary)] mt-0.5">
                            {selectedCategory.scenario_count} scenarios pre-selected • You can customize below
                          </p>
                        </div>
                        <button
                          onClick={() => {
                            setCreateStep('method');
                            setSelectedCategory(null);
                            setCreateSelectedScenarios([]);
                          }}
                          className="text-sm text-[#2A6B6E] hover:underline font-medium"
                        >
                          Change
                        </button>
                      </div>
                    </div>
                  )}

                  {/* Form Fields */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="md:col-span-2">
                      <label className="block text-sm font-semibold text-[var(--color-content-secondary)] mb-1.5">
                        Suite Name <span className="text-[var(--color-status-danger)]">*</span>
                      </label>
                      <input
                        type="text"
                        value={formData.name}
                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                        className="w-full px-4 py-2.5 border border-[var(--color-border-strong)] rounded-lg text-sm bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] placeholder:text-[var(--color-content-muted)] focus:outline-none focus:border-[#2A6B6E] focus:ring-2 focus:ring-[#2A6B6E]/20 transition-all"
                        placeholder="e.g., Regression Suite v2.0"
                      />
                    </div>
                    <div className="md:col-span-2">
                      <label className="block text-sm font-semibold text-[var(--color-content-secondary)] mb-1.5">Description</label>
                      <textarea
                        value={formData.description}
                        onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                        className="w-full px-4 py-2.5 border border-[var(--color-border-strong)] rounded-lg text-sm bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] placeholder:text-[var(--color-content-muted)] focus:outline-none focus:border-[#2A6B6E] focus:ring-2 focus:ring-[#2A6B6E]/20 transition-all resize-none"
                        rows={2}
                        placeholder="Brief description of what this suite tests..."
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-semibold text-[var(--color-content-secondary)] mb-1.5">Category Tag</label>
                      <input
                        type="text"
                        value={formData.category}
                        onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                        className="w-full px-4 py-2.5 border border-[var(--color-border-strong)] rounded-lg text-sm bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] placeholder:text-[var(--color-content-muted)] focus:outline-none focus:border-[#2A6B6E] focus:ring-2 focus:ring-[#2A6B6E]/20 transition-all"
                        placeholder="e.g., regression, smoke"
                      />
                    </div>
                    <div>
                      {/* Placeholder for symmetry */}
                    </div>
                  </div>

                  {/* Language Configuration */}
                  <div className="bg-[var(--color-surface-inset)]/50 rounded-xl p-4 border border-[var(--color-border-default)]">
                    <LanguageConfigForm
                      value={languageConfig}
                      onChange={setLanguageConfig}
                    />
                  </div>

                  {/* Scenario Selection */}
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <label className="text-sm font-semibold text-[var(--color-content-secondary)]">
                        Scenarios
                      </label>
                      <span className="px-2.5 py-1 bg-[#2A6B6E]/10 text-[#2A6B6E] rounded-full text-xs font-semibold">
                        {createSelectedScenarios.length} selected
                      </span>
                    </div>
                    <div className="border border-[var(--color-border-default)] rounded-xl overflow-hidden">
                      {/* Search & Actions Bar */}
                      <div className="p-3 bg-[var(--color-surface-inset)]/50 border-b border-[var(--color-border-default)]">
                        <div className="flex items-center gap-3">
                          <div className="flex-1 relative">
                            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-[var(--color-content-muted)] w-4 h-4" />
                            <input
                              type="text"
                              placeholder="Search scenarios..."
                              value={createScenarioSearch}
                              onChange={(e) => setCreateScenarioSearch(e.target.value)}
                              className="w-full pl-9 pr-4 py-2 border border-[var(--color-border-default)] rounded-lg text-sm bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] placeholder:text-[var(--color-content-muted)] focus:outline-none focus:border-[#2A6B6E] transition-all"
                            />
                          </div>
                          <div className="flex items-center gap-2">
                            <button
                              onClick={() => {
                                const filtered = availableScenarios.filter((s) =>
                                  s.name.toLowerCase().includes(createScenarioSearch.toLowerCase()) ||
                                  (s.description && s.description.toLowerCase().includes(createScenarioSearch.toLowerCase()))
                                );
                                setCreateSelectedScenarios(filtered.map((s) => s.id));
                              }}
                              className="px-3 py-1.5 text-xs font-medium text-[#2A6B6E] hover:bg-[#2A6B6E]/10 rounded-lg transition-colors"
                            >
                              Select All
                            </button>
                            {createSelectedScenarios.length > 0 && (
                              <button
                                onClick={() => setCreateSelectedScenarios([])}
                                className="px-3 py-1.5 text-xs font-medium text-[var(--color-content-secondary)] hover:bg-[var(--color-interactive-active)] rounded-lg transition-colors"
                              >
                                Clear
                              </button>
                            )}
                          </div>
                        </div>
                      </div>
                      {/* Scenario List */}
                      <div className="max-h-48 overflow-y-auto bg-[var(--color-surface-raised)]">
                        {availableScenarios.length === 0 ? (
                          <div className="p-8 text-center">
                            <div className="w-8 h-8 border-3 border-[var(--color-border-default)] border-t-[#2A6B6E] rounded-full animate-spin mx-auto mb-3"></div>
                            <p className="text-sm text-[var(--color-content-muted)]">Loading scenarios...</p>
                          </div>
                        ) : (
                          <>
                            {availableScenarios
                              .filter((s) =>
                                s.name.toLowerCase().includes(createScenarioSearch.toLowerCase()) ||
                                (s.description && s.description.toLowerCase().includes(createScenarioSearch.toLowerCase()))
                              )
                              .map((scenario) => {
                                const isSelected = createSelectedScenarios.includes(scenario.id);
                                return (
                                  <div
                                    key={scenario.id}
                                    className={`px-4 py-3 flex items-center gap-3 cursor-pointer border-b border-[var(--color-border-subtle)] last:border-b-0 transition-colors ${
                                      isSelected ? 'bg-[var(--color-brand-muted)]' : 'hover:bg-[var(--color-interactive-hover)]/50'
                                    }`}
                                    onClick={() => {
                                      setCreateSelectedScenarios((prev) =>
                                        prev.includes(scenario.id)
                                          ? prev.filter((id) => id !== scenario.id)
                                          : [...prev, scenario.id]
                                      );
                                    }}
                                  >
                                    <div
                                      className={`w-5 h-5 rounded flex items-center justify-center flex-shrink-0 transition-all ${
                                        isSelected
                                          ? 'bg-[#2A6B6E] text-white shadow-sm'
                                          : 'border-2 border-[var(--color-border-strong)]'
                                      }`}
                                    >
                                      {isSelected && <Check className="w-3 h-3" strokeWidth={3} />}
                                    </div>
                                    <div className="flex-1 min-w-0">
                                      <span className="text-sm font-medium text-[var(--color-content-primary)] block truncate">
                                        {scenario.name}
                                      </span>
                                      {scenario.description && (
                                        <span className="text-xs text-[var(--color-content-muted)] block truncate mt-0.5">
                                          {scenario.description}
                                        </span>
                                      )}
                                    </div>
                                    <span className="px-2 py-0.5 bg-[var(--color-surface-inset)] text-[var(--color-content-muted)] rounded text-xs flex-shrink-0">
                                      {scenario.steps_count || 0} steps
                                    </span>
                                  </div>
                                );
                              })}
                            {availableScenarios.filter((s) =>
                              s.name.toLowerCase().includes(createScenarioSearch.toLowerCase()) ||
                              (s.description && s.description.toLowerCase().includes(createScenarioSearch.toLowerCase()))
                            ).length === 0 && (
                              <div className="p-6 text-center text-[var(--color-content-muted)] text-sm">
                                No scenarios match "{createScenarioSearch}"
                              </div>
                            )}
                          </>
                        )}
                      </div>
                    </div>
                    <p className="text-xs text-[var(--color-content-muted)] mt-2">
                      Select scenarios to include in your suite. You can always add or remove scenarios later.
                    </p>
                  </div>
                </div>
              )}
            </div>

            {/* Modal Footer */}
            <div className="px-6 py-4 border-t border-[var(--color-border-default)] bg-[var(--color-surface-inset)]/50 flex items-center justify-between">
              <div>
                {createStep === 'details' && (
                  <button
                    onClick={() => {
                      setCreateStep('method');
                      if (!selectedCategory) {
                        setFormData({ name: '', description: '', category: '' });
                        setCreateSelectedScenarios([]);
                      }
                    }}
                    className="flex items-center gap-2 px-4 py-2.5 text-sm font-medium text-[var(--color-content-secondary)] hover:text-[var(--color-content-primary)] transition-colors"
                  >
                    <ArrowRight className="w-4 h-4 rotate-180" />
                    Back
                  </button>
                )}
              </div>
              <div className="flex gap-3">
                <button
                  onClick={resetCreateModal}
                  className="px-5 py-2.5 border border-[var(--color-border-strong)] rounded-lg text-sm font-medium text-[var(--color-content-secondary)] hover:bg-[var(--color-interactive-hover)] transition-all"
                >
                  Cancel
                </button>
                {createStep === 'details' && (
                  <button
                    onClick={selectedCategory ? handleCreateFromCategory : handleCreateSuite}
                    disabled={!formData.name.trim()}
                    className="px-6 py-2.5 rounded-lg text-sm font-semibold text-white transition-all hover:shadow-lg hover:-translate-y-0.5 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:shadow-none disabled:hover:translate-y-0"
                    style={{ background: 'linear-gradient(135deg, #2A6B6E 0%, #11484D 100%)' }}
                  >
                    Create Suite
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Edit Suite Modal */}
      {editingSuite && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-[var(--color-surface-raised)] rounded-lg p-6 w-full max-w-md mx-4">
            <h2 className="text-xl font-semibold text-[var(--color-content-primary)] mb-4">Edit Test Suite</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1">Name *</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-3 py-2 border border-[var(--color-border-strong)] rounded-lg text-sm bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:outline-none focus:border-primary"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1">Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-3 py-2 border border-[var(--color-border-strong)] rounded-lg text-sm bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:outline-none focus:border-primary"
                  rows={3}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1">Category</label>
                <input
                  type="text"
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  className="w-full px-3 py-2 border border-[var(--color-border-strong)] rounded-lg text-sm bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:outline-none focus:border-primary"
                />
              </div>
              {/* Language Configuration */}
              <LanguageConfigForm
                value={languageConfig}
                onChange={setLanguageConfig}
              />
            </div>
            <div className="flex gap-3 mt-6">
              <button
                onClick={() => {
                  setEditingSuite(null);
                  setFormData({ name: '', description: '', category: '' });
                  setLanguageConfig(null);
                }}
                className="flex-1 px-4 py-2 border border-[var(--color-border-strong)] rounded-lg text-[var(--color-content-secondary)] hover:bg-[var(--color-interactive-hover)]"
              >
                Cancel
              </button>
              <button
                onClick={handleUpdateSuite}
                className="flex-1 px-4 py-2 rounded-lg text-white"
                style={{ background: 'linear-gradient(135deg, #2A6B6E 0%, #11484D 100%)' }}
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Manage Scenarios Modal */}
      {managingSuite && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-[var(--color-surface-raised)] rounded-xl w-full max-w-2xl max-h-[85vh] flex flex-col shadow-2xl">
            {/* Modal Header */}
            <div className="px-6 py-4 border-b border-[var(--color-border-default)] flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold text-[var(--color-content-primary)]">
                  Manage Scenarios
                </h2>
                <p className="text-sm text-[var(--color-content-muted)] mt-0.5">{managingSuite.name}</p>
              </div>
              <button
                onClick={() => {
                  setManagingSuite(null);
                  setScenarioSearch('');
                }}
                className="p-2 hover:bg-[var(--color-interactive-hover)] rounded-lg transition-colors"
              >
                <X className="w-5 h-5 text-[var(--color-content-muted)]" />
              </button>
            </div>

            {/* Search Bar */}
            <div className="px-6 py-3 border-b border-[var(--color-border-default)]">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-[var(--color-content-muted)] w-4 h-4" />
                <input
                  type="text"
                  placeholder="Search scenarios..."
                  value={scenarioSearch}
                  onChange={(e) => setScenarioSearch(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-[var(--color-border-default)] rounded-lg text-sm bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] placeholder:text-[var(--color-content-muted)] focus:outline-none focus:border-[#2A6B6E] focus:ring-2 focus:ring-[#2A6B6E]/10"
                />
              </div>
            </div>

            {/* Selection Info */}
            <div className="px-6 py-2.5 bg-[var(--color-surface-inset)] border-b border-[var(--color-border-default)] flex items-center justify-between">
              <span className="text-sm text-[var(--color-content-secondary)]">
                {selectedScenarioIds.length} of {availableScenarios.length} selected
              </span>
              <div className="flex items-center gap-3">
                <button
                  onClick={() => {
                    const filteredScenarios = availableScenarios.filter((scenario) =>
                      scenario.name.toLowerCase().includes(scenarioSearch.toLowerCase()) ||
                      (scenario.description && scenario.description.toLowerCase().includes(scenarioSearch.toLowerCase()))
                    );
                    setSelectedScenarioIds(filteredScenarios.map((s) => s.id));
                  }}
                  className="text-sm text-[#2A6B6E] hover:underline"
                >
                  Select all
                </button>
                {selectedScenarioIds.length > 0 && (
                  <button
                    onClick={() => setSelectedScenarioIds([])}
                    className="text-sm text-[#2A6B6E] hover:underline"
                  >
                    Clear all
                  </button>
                )}
              </div>
            </div>

            {/* Scenarios List */}
            <div className="flex-1 overflow-y-auto">
              {loadingScenarios ? (
                <div className="p-12 text-center">
                  <div className="w-8 h-8 border-3 border-[var(--color-border-default)] border-t-[#2A6B6E] rounded-full animate-spin mx-auto mb-3"></div>
                  <p className="text-[var(--color-content-muted)]">Loading scenarios...</p>
                </div>
              ) : availableScenarios.length === 0 ? (
                <div className="p-12 text-center">
                  <Layers className="w-12 h-12 text-[var(--color-content-muted)] mx-auto mb-3" />
                  <p className="text-[var(--color-content-muted)]">No active scenarios available</p>
                  <p className="text-sm text-[var(--color-content-muted)] mt-1">Create scenarios first to add them to this suite</p>
                </div>
              ) : (
                <div className="divide-y divide-[var(--color-border-subtle)]">
                  {availableScenarios
                    .filter((scenario) =>
                      scenario.name.toLowerCase().includes(scenarioSearch.toLowerCase()) ||
                      (scenario.description && scenario.description.toLowerCase().includes(scenarioSearch.toLowerCase()))
                    )
                    .map((scenario) => {
                      const isSelected = selectedScenarioIds.includes(scenario.id);
                      return (
                        <div
                          key={scenario.id}
                          className={`px-6 py-4 flex items-center gap-4 cursor-pointer transition-colors ${
                            isSelected ? 'bg-[var(--color-brand-muted)]' : 'hover:bg-[var(--color-interactive-hover)]'
                          }`}
                          onClick={() => handleToggleScenario(scenario.id)}
                        >
                          <div
                            className={`w-5 h-5 rounded flex items-center justify-center flex-shrink-0 transition-colors ${
                              isSelected
                                ? 'bg-[#2A6B6E] text-white'
                                : 'border-2 border-[var(--color-border-strong)]'
                            }`}
                          >
                            {isSelected && <Check className="w-3.5 h-3.5" strokeWidth={3} />}
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="font-medium text-[var(--color-content-primary)]">{scenario.name}</div>
                            {scenario.description && (
                              <div className="text-sm text-[var(--color-content-muted)] truncate mt-0.5">
                                {scenario.description}
                              </div>
                            )}
                          </div>
                          <div className="flex-shrink-0 px-2.5 py-1 bg-[var(--color-surface-inset)] rounded-full text-xs text-[var(--color-content-secondary)]">
                            {scenario.steps_count || 0} steps
                          </div>
                        </div>
                      );
                    })}
                  {availableScenarios.filter((s) =>
                    s.name.toLowerCase().includes(scenarioSearch.toLowerCase()) ||
                    (s.description && s.description.toLowerCase().includes(scenarioSearch.toLowerCase()))
                  ).length === 0 && scenarioSearch && (
                    <div className="p-8 text-center text-[var(--color-content-muted)]">
                      No scenarios match "{scenarioSearch}"
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Modal Footer */}
            <div className="px-6 py-4 border-t border-[var(--color-border-default)] bg-[var(--color-surface-inset)] flex gap-3">
              <button
                onClick={() => {
                  setManagingSuite(null);
                  setScenarioSearch('');
                }}
                className="flex-1 px-4 py-2.5 border border-[var(--color-border-strong)] rounded-lg text-[var(--color-content-secondary)] font-medium hover:bg-[var(--color-interactive-hover)] transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveScenarios}
                className="flex-1 px-4 py-2.5 rounded-lg text-white font-medium transition-all hover:shadow-lg"
                style={{ background: 'linear-gradient(135deg, #2A6B6E 0%, #11484D 100%)' }}
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Alert Modal */}
      <Modal
        isOpen={modalState.isOpen}
        onClose={closeModal}
        onConfirm={modalState.onConfirm}
        title={modalState.title}
        message={modalState.message}
        type={modalState.type}
        confirmText={modalState.confirmText}
        cancelText={modalState.cancelText}
        showCancel={modalState.showCancel}
      />
    </>
  );
};

/**
 * Suite Card Component
 */
interface SuiteCardProps {
  suite: TestSuite;
  onRun: (suiteId: string) => void;
  onEdit: (suite: TestSuite) => void;
  onDelete: (suiteId: string) => void;
  onManageScenarios: (suiteId: string) => void;
  executing: boolean;
  deleteConfirm: string | null;
  setDeleteConfirm: (id: string | null) => void;
}

const SuiteCard: React.FC<SuiteCardProps> = ({
  suite,
  onRun,
  onEdit,
  onDelete,
  onManageScenarios,
  executing,
  deleteConfirm,
  setDeleteConfirm,
}) => {
  const [showMenu, setShowMenu] = useState(false);

  return (
    <div className="bg-[var(--color-surface-raised)] rounded-xl shadow-sm hover:shadow-md transition-all border border-[var(--color-border-subtle)] overflow-hidden flex flex-col h-full">
      {/* Card Header with Menu */}
      <div className="px-5 pt-5 pb-3 flex-1">
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            <h3 className="text-lg font-semibold text-[var(--color-content-primary)] truncate">{suite.name}</h3>
            <div className="flex items-center gap-2 mt-1.5">
              {suite.is_active ? (
                <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-[var(--color-status-success-bg)] text-[var(--color-status-success)]">
                  Active
                </span>
              ) : (
                <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-[var(--color-surface-inset)] text-[var(--color-content-secondary)]">
                  Inactive
                </span>
              )}
              {suite.category && (
                <span className="px-2 py-0.5 bg-[var(--color-surface-inset)] text-[var(--color-content-muted)] rounded text-xs font-mono uppercase">
                  {suite.category}
                </span>
              )}
              {suite.language_config && (
                <span className="px-2 py-0.5 bg-gradient-to-r from-[#2A6B6E]/10 to-[#11484D]/10 border border-[#2A6B6E]/30 text-[var(--color-brand-primary)] rounded text-xs font-medium flex items-center gap-1">
                  <Globe className="w-3 h-3" />
                  {suite.language_config.mode === 'primary' && 'Primary Only'}
                  {suite.language_config.mode === 'specific' && `${suite.language_config.languages?.length || 0} Languages`}
                  {suite.language_config.mode === 'all' && 'All Languages'}
                </span>
              )}
            </div>
          </div>

          {/* Dropdown Menu */}
          <div className="relative">
            <button
              onClick={() => setShowMenu(!showMenu)}
              className="p-1.5 hover:bg-[var(--color-interactive-hover)] rounded-lg transition-colors"
            >
              <MoreVertical className="w-5 h-5 text-[var(--color-content-muted)]" />
            </button>
            {showMenu && (
              <>
                <div className="fixed inset-0 z-10" onClick={() => setShowMenu(false)} />
                <div className="absolute right-0 mt-1 w-36 bg-[var(--color-surface-raised)] rounded-lg shadow-lg border border-[var(--color-border-default)] py-1 z-20">
                  <button
                    onClick={() => {
                      setShowMenu(false);
                      onEdit(suite);
                    }}
                    className="w-full px-4 py-2 text-left text-sm text-[var(--color-content-secondary)] hover:bg-[var(--color-interactive-hover)] flex items-center gap-2"
                  >
                    <Edit2 className="w-4 h-4" />
                    Edit
                  </button>
                  <button
                    onClick={() => {
                      setShowMenu(false);
                      setDeleteConfirm(suite.id);
                    }}
                    className="w-full px-4 py-2 text-left text-sm text-[var(--color-status-danger)] hover:bg-[var(--color-status-danger-bg)] flex items-center gap-2"
                  >
                    <Trash2 className="w-4 h-4" />
                    Delete
                  </button>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Description */}
        {suite.description && (
          <p className="text-[var(--color-content-muted)] text-sm mt-3 line-clamp-2">{suite.description}</p>
        )}
      </div>

      {/* Metadata */}
      <div className="px-5 py-2.5 bg-[var(--color-surface-inset)] text-xs text-[var(--color-content-muted)] border-t border-[var(--color-border-subtle)]">
        Created {new Date(suite.created_at).toLocaleDateString('en-US', {
          month: 'short',
          day: 'numeric',
          year: 'numeric',
        })}
      </div>

      {/* Actions */}
      <div className="px-5 py-4 flex gap-3">
        <button
          onClick={() => onManageScenarios(suite.id)}
          className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 border border-[var(--color-border-default)] rounded-lg text-[var(--color-content-secondary)] font-medium text-sm hover:bg-[var(--color-interactive-hover)] hover:border-[var(--color-border-strong)] transition-colors"
        >
          <Layers className="w-4 h-4" />
          Scenarios
        </button>
        <button
          onClick={() => onRun(suite.id)}
          disabled={executing || !suite.is_active}
          className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 text-white rounded-lg font-medium text-sm transition-all disabled:cursor-not-allowed disabled:opacity-50 hover:shadow-md"
          style={
            !executing && suite.is_active
              ? { background: 'linear-gradient(135deg, #2A6B6E 0%, #11484D 100%)' }
              : { background: '#9CA3AF' }
          }
        >
          {executing ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-2 border-white/30 border-t-white"></div>
              Running...
            </>
          ) : (
            <>
              <Play className="w-4 h-4" />
              Run Suite
            </>
          )}
        </button>
      </div>

      {/* Delete Confirmation */}
      {deleteConfirm === suite.id && (
        <div className="px-5 py-3 bg-[var(--color-status-danger-bg)] border-t border-[var(--color-status-danger-bg)] flex items-center justify-between">
          <span className="text-sm text-[var(--color-status-danger)]">Delete this suite?</span>
          <div className="flex gap-2">
            <button
              onClick={() => setDeleteConfirm(null)}
              className="px-3 py-1.5 text-sm text-[var(--color-content-secondary)] hover:bg-[var(--color-status-danger-bg)] rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={() => onDelete(suite.id)}
              className="px-3 py-1.5 text-sm bg-[var(--color-status-danger)] text-white rounded-lg hover:opacity-90 transition-colors"
            >
              Delete
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default TestSuiteList;
