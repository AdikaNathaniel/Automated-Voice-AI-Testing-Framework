/**
 * Scenario Edit Page
 *
 * Edit existing multi-turn scenarios:
 * - Load existing scenario data
 * - Allow editing all fields (metadata, steps, outcomes)
 * - Show unsaved changes warning
 * - Handle updates to steps and outcomes
 */

import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, Save, AlertCircle, AlertTriangle, FileText } from 'lucide-react';
import { ScenarioForm, type ScenarioFormData } from './ScenarioForm';
import { StepManager, type ScenarioStepData } from './StepManager';
import { ExpectedOutcomeForm, type ExpectedOutcomeData } from './ExpectedOutcomeForm';
import { multiTurnService } from '../../services/multiTurn.service';
import type { ScenarioScript } from '../../types/multiTurn';
import Modal from '../../components/Modal/Modal';
import { useModal } from '../../hooks/useModal';

export const ScenarioEdit: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const { modalState, showConfirm, closeModal } = useModal();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [selectedStepIndex, setSelectedStepIndex] = useState<number>(0);
  const [activeTab, setActiveTab] = useState<'metadata' | 'steps' | 'outcomes'>('metadata');

  // Form data
  const [originalScenario, setOriginalScenario] = useState<ScenarioScript | null>(null);
  const [scenarioData, setScenarioData] = useState<ScenarioFormData>({
    name: '',
    description: '',
    version: '1.0.0',
    is_active: true,
    validation_mode: 'hybrid',
    script_metadata: {
      category: '',
      tags: [],
    },
  });

  const [steps, setSteps] = useState<ScenarioStepData[]>([]);

  useEffect(() => {
    if (id) {
      loadScenario();
    }
  }, [id]);

  useEffect(() => {
    // Warn user about unsaved changes when leaving page
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (hasUnsavedChanges) {
        e.preventDefault();
        e.returnValue = '';
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [hasUnsavedChanges]);

  const loadScenario = async () => {
    if (!id) return;

    try {
      setLoading(true);
      setError(null);
      const scenario = await multiTurnService.getScenario(id);
      setOriginalScenario(scenario);

      // Set scenario metadata (including validation_mode)
      setScenarioData({
        name: scenario.name,
        description: scenario.description || '',
        version: scenario.version,
        is_active: scenario.is_active,
        validation_mode: scenario.validation_mode || 'hybrid',
        script_metadata: scenario.script_metadata || { category: '', tags: [] },
      });

      // Set steps with expected outcomes
      const loadedSteps: ScenarioStepData[] = (scenario.steps || []).map((step: any) => ({
        id: step.id,
        step_order: step.step_order,
        user_utterance: step.user_utterance,
        step_metadata: step.step_metadata || {},
        follow_up_action: step.follow_up_action,
        expected_outcomes: (step.expected_outcomes || []).map((outcome: any) => ({
          id: outcome.id,
          outcome_code: outcome.outcome_code,
          name: outcome.name,
          description: outcome.description,
          expected_command_kind: outcome.expected_command_kind,
          expected_asr_confidence_min: outcome.expected_asr_confidence_min,
          expected_response_content: outcome.expected_response_content,
          entities: outcome.entities || {},
          validation_rules: outcome.validation_rules || {},
        })),
      }));

      setSteps(loadedSteps);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load scenario');
    } finally {
      setLoading(false);
    }
  };

  const handleScenarioDataChange = (data: ScenarioFormData) => {
    setScenarioData(data);
    setHasUnsavedChanges(true);
  };

  const handleStepsChange = (newSteps: ScenarioStepData[]) => {
    setSteps(newSteps);
    setHasUnsavedChanges(true);
  };

  const handleOutcomesChange = (outcomes: ExpectedOutcomeData[]) => {
    const newSteps = [...steps];
    newSteps[selectedStepIndex] = {
      ...newSteps[selectedStepIndex],
      expected_outcomes: outcomes,
    };
    setSteps(newSteps);
    setHasUnsavedChanges(true);
  };

  const validateForm = (): boolean => {
    if (!scenarioData.name.trim()) {
      setError('Scenario name is required');
      setActiveTab('metadata');
      return false;
    }
    if (!scenarioData.version.trim()) {
      setError('Version is required');
      setActiveTab('metadata');
      return false;
    }
    if (steps.length === 0) {
      setError('At least one step is required');
      setActiveTab('steps');
      return false;
    }
    for (let i = 0; i < steps.length; i++) {
      if (!steps[i].user_utterance.trim()) {
        setError(`Step ${i + 1}: User utterance is required`);
        setActiveTab('steps');
        return false;
      }
      // Note: expected_response is now optional if expected_outcomes are configured
      // Validation can be done via ExpectedOutcome records instead
    }
    setError(null);
    return true;
  };

  const handleSubmit = async () => {
    if (!id || !validateForm()) {
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      // Build the update payload (including validation_mode)
      const payload = {
        name: scenarioData.name,
        description: scenarioData.description,
        version: scenarioData.version,
        is_active: scenarioData.is_active,
        validation_mode: scenarioData.validation_mode,
        script_metadata: scenarioData.script_metadata,
        steps: steps.map((step) => ({
          id: step.id, // Include ID for existing steps
          step_order: step.step_order,
          user_utterance: step.user_utterance,
          step_metadata: step.step_metadata || {},
          follow_up_action: step.follow_up_action,
          expected_outcomes: (step.expected_outcomes || []).map((outcome: any) => ({
            id: outcome.id, // Include ID for existing outcomes
            outcome_code: outcome.outcome_code,
            name: outcome.name,
            description: outcome.description,
            expected_command_kind: outcome.expected_command_kind,
            expected_asr_confidence_min: outcome.expected_asr_confidence_min,
            expected_response_content: outcome.expected_response_content,
            entities: outcome.entities || {},
            validation_rules: outcome.validation_rules || {},
          })),
        })),
      };

      await multiTurnService.updateScenario(id, payload);
      setHasUnsavedChanges(false);
      navigate(`/scenarios/${id}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update scenario');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancel = () => {
    if (hasUnsavedChanges) {
      showConfirm(
        'You have unsaved changes. Are you sure you want to leave?',
        () => navigate(`/scenarios/${id}`),
        {
          title: 'Unsaved Changes',
          confirmText: 'Leave',
          cancelText: 'Stay',
        }
      );
    } else {
      navigate(`/scenarios/${id}`);
    }
  };

  if (loading) {
    return (
      <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-sm">
        <div className="flex flex-col items-center justify-center p-20">
          <div className="w-12 h-12 border-4 border-[var(--color-border-default)] rounded-full animate-spin mb-4" style={{ borderTopColor: '#2A6B6E' }}></div>
          <div className="text-lg font-semibold text-[var(--color-content-primary)] mb-2">Loading Scenario...</div>
        </div>
      </div>
    );
  }

  if (error && !originalScenario) {
    return (
      <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-sm">
        <div className="bg-[var(--color-status-danger-bg)] border border-[var(--color-status-danger)] rounded-lg p-4">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-[var(--color-status-danger)] mt-0.5" />
            <div>
              <h3 className="font-semibold text-[var(--color-status-danger)]">Error Loading Scenario</h3>
              <p className="text-[var(--color-status-danger)]">{error}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <>
      {/* Header */}
      <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 mb-6 shadow-md">
        <button
          onClick={handleCancel}
          className="flex items-center gap-2 text-[var(--color-content-secondary)] hover:text-[var(--color-content-primary)] mb-4"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Scenario
        </button>
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-bold text-[var(--color-content-primary)] flex items-center gap-3">
              <FileText className="w-6 h-6" style={{ color: '#2A6B6E' }} />
              Edit Scenario
            </h1>
            <p className="text-[var(--color-content-muted)] mt-2">{originalScenario?.name}</p>
          </div>
          {hasUnsavedChanges && (
            <div className="flex items-center gap-2 px-4 py-2 bg-[var(--color-status-warning-bg)] border border-[var(--color-status-warning-bg)] rounded-lg">
              <AlertTriangle className="w-5 h-5 text-[var(--color-status-warning)]" />
              <span className="text-sm font-medium text-[var(--color-status-warning)]">Unsaved changes</span>
            </div>
          )}
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 mb-6 shadow-sm">
        <nav className="flex gap-8 border-b border-[var(--color-border-default)] pb-4">
          {[
            { id: 'metadata' as const, label: 'Scenario Details' },
            { id: 'steps' as const, label: 'Steps' },
            { id: 'outcomes' as const, label: 'Expected Outcomes' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`pb-2 px-1 border-b-2 font-medium transition-colors ${
                activeTab === tab.id
                  ? 'border-primary text-primary'
                  : 'border-transparent text-[var(--color-content-muted)] hover:text-primary'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>

        {/* Error Message */}
        {error && (
          <div className="mt-6 p-4 bg-[var(--color-status-danger-bg)] border border-[var(--color-status-danger)] rounded-lg flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-[var(--color-status-danger)] mt-0.5" />
            <div>
              <h3 className="font-semibold text-[var(--color-status-danger)]">Error</h3>
              <p className="text-[var(--color-status-danger)]">{error}</p>
            </div>
          </div>
        )}

        {/* Form Content */}
        <div className="mt-6">
        {activeTab === 'metadata' && (
          <ScenarioForm
            initialData={scenarioData}
            onSubmit={handleScenarioDataChange}
            isLoading={isSubmitting}
          />
        )}

        {activeTab === 'steps' && (
          <StepManager
            steps={steps}
            onChange={handleStepsChange}
            onStepSelect={setSelectedStepIndex}
            selectedStepIndex={selectedStepIndex}
            scenarioId={id}
          />
        )}

        {activeTab === 'outcomes' && (
          <div className="space-y-6">
            {/* Step Selector */}
            <div>
              <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-2">
                Configure outcomes for:
              </label>
              <select
                value={selectedStepIndex}
                onChange={(e) => setSelectedStepIndex(parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-[var(--color-border-default)] rounded-lg bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/10"
              >
                {steps.map((step, index) => (
                  <option key={index} value={index}>
                    Step {step.step_order}: {step.user_utterance || '(No utterance)'}
                  </option>
                ))}
              </select>
            </div>

            {/* Expected Outcomes Form */}
            <ExpectedOutcomeForm
              outcomes={(steps[selectedStepIndex]?.expected_outcomes as ExpectedOutcomeData[]) || []}
              onChange={handleOutcomesChange}
              stepNumber={steps[selectedStepIndex]?.step_order}
            />
          </div>
        )}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex justify-between">
        <button
          onClick={handleCancel}
          disabled={isSubmitting}
          className="px-6 py-3 border border-[var(--color-border-strong)] text-[var(--color-content-secondary)] rounded-lg hover:bg-[var(--color-interactive-hover)] disabled:opacity-50 transition-all"
        >
          Cancel
        </button>

        <button
          onClick={handleSubmit}
          disabled={isSubmitting || !hasUnsavedChanges}
          className="flex items-center gap-2 px-6 py-3 text-white rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg hover:-translate-y-0.5"
          style={!isSubmitting && hasUnsavedChanges ? { background: 'linear-gradient(135deg, #2A6B6E 0%, #11484D 100%)' } : { background: '#9CA3AF' }}
        >
          <Save className="w-4 h-4" />
          {isSubmitting ? 'Saving...' : 'Save Changes'}
        </button>
      </div>

      {/* Modal for confirmations */}
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

export default ScenarioEdit;
