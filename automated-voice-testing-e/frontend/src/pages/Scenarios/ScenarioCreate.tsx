/**
 * Scenario Creation Page
 *
 * Complete workflow for creating new multi-turn scenarios:
 * - Step 1: Scenario metadata (ScenarioForm)
 * - Step 2: Add and configure steps (StepManager)
 * - Step 3: Configure expected outcomes for each step (ExpectedOutcomeForm)
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, ArrowRight, Save, AlertCircle, FileText } from 'lucide-react';
import { ScenarioForm, type ScenarioFormData } from './ScenarioForm';
import { StepManager, type ScenarioStepData } from './StepManager';
import { ExpectedOutcomeForm, type ExpectedOutcomeData } from './ExpectedOutcomeForm';
import { multiTurnService } from '../../services/multiTurn.service';

type WizardStep = 'metadata' | 'steps' | 'outcomes';

export const ScenarioCreate: React.FC = () => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState<WizardStep>('metadata');
  const [selectedStepIndex, setSelectedStepIndex] = useState<number>(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form data
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

  const [steps, setSteps] = useState<ScenarioStepData[]>([
    {
      step_order: 1,
      user_utterance: '',
      step_metadata: {},
      expected_outcomes: [],
    },
  ]);

  const handleScenarioDataChange = (data: ScenarioFormData) => {
    setScenarioData(data);
    setError(null); // Clear any previous errors when user updates form
  };

  const handleStepsChange = (newSteps: ScenarioStepData[]) => {
    setSteps(newSteps);
  };

  const handleOutcomesChange = (outcomes: ExpectedOutcomeData[]) => {
    const newSteps = [...steps];
    newSteps[selectedStepIndex] = {
      ...newSteps[selectedStepIndex],
      expected_outcomes: outcomes,
    };
    setSteps(newSteps);
  };

  const validateMetadata = (): boolean => {
    if (!scenarioData.name.trim()) {
      setError('Scenario name is required');
      return false;
    }
    if (!scenarioData.version.trim()) {
      setError('Version is required');
      return false;
    }
    setError(null);
    return true;
  };

  const validateSteps = (): boolean => {
    if (steps.length === 0) {
      setError('At least one step is required');
      return false;
    }
    for (let i = 0; i < steps.length; i++) {
      if (!steps[i].user_utterance.trim()) {
        setError(`Step ${i + 1}: User utterance is required`);
        return false;
      }
      // Note: expected_response is now optional if expected_outcomes will be configured
      // Users can define validation criteria via ExpectedOutcome in the next step
    }
    setError(null);
    return true;
  };

  const handleNext = () => {
    if (currentStep === 'metadata') {
      if (validateMetadata()) {
        setCurrentStep('steps');
      }
    } else if (currentStep === 'steps') {
      if (validateSteps()) {
        setCurrentStep('outcomes');
      }
    }
  };

  const handleBack = () => {
    if (currentStep === 'outcomes') {
      setCurrentStep('steps');
    } else if (currentStep === 'steps') {
      setCurrentStep('metadata');
    }
  };

  const handleSubmit = async () => {
    if (!validateMetadata() || !validateSteps()) {
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      // Build the complete scenario payload (including validation_mode)
      const payload = {
        name: scenarioData.name,
        description: scenarioData.description,
        version: scenarioData.version,
        is_active: scenarioData.is_active,
        validation_mode: scenarioData.validation_mode,
        script_metadata: scenarioData.script_metadata,
        approval_status: 'draft',
        steps: steps.map((step) => ({
          step_order: step.step_order,
          user_utterance: step.user_utterance,
          step_metadata: step.step_metadata || {},
          follow_up_action: step.follow_up_action,
          expected_outcomes: step.expected_outcomes || [],
        })),
      };

      const createdScenario = await multiTurnService.createScenario(payload);
      navigate(`/scenarios/${createdScenario.id}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create scenario');
    } finally {
      setIsSubmitting(false);
    }
  };

  const stepLabels: Record<WizardStep, string> = {
    metadata: 'Scenario Details',
    steps: 'Configure Steps',
    outcomes: 'Expected Outcomes (Optional)',
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => navigate('/scenarios')}
          className="flex items-center gap-2 text-[var(--color-content-secondary)] hover:text-[var(--color-content-primary)] mb-4 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Scenarios
        </button>
        <h1 className="text-2xl font-bold text-[var(--color-content-primary)] flex items-center gap-3">
          <FileText className="w-6 h-6" style={{ color: '#2A6B6E' }} />
          Create New Scenario
        </h1>
        <p className="text-[var(--color-content-secondary)] mt-2">
          Build a multi-turn conversation scenario. Define steps with expected responses, then optionally add advanced validation.
        </p>
      </div>

      {/* Progress Indicator */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          {(['metadata', 'steps', 'outcomes'] as WizardStep[]).map((step, index) => (
            <React.Fragment key={step}>
              <div className="flex items-center">
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold shadow-sm ${
                    currentStep === step
                      ? 'text-white'
                      : index <
                        (['metadata', 'steps', 'outcomes'] as WizardStep[]).indexOf(currentStep)
                      ? 'bg-[var(--color-status-success)] text-white'
                      : 'bg-[var(--color-interactive-active)] text-[var(--color-content-secondary)]'
                  }`}
                  style={currentStep === step ? { background: 'linear-gradient(135deg, #2A6B6E 0%, #11484D 100%)' } : undefined}
                >
                  {index + 1}
                </div>
                <span
                  className={`ml-3 font-medium hidden sm:inline ${
                    currentStep === step ? 'text-[var(--color-brand-primary)]' : 'text-[var(--color-content-secondary)]'
                  }`}
                >
                  {stepLabels[step]}
                </span>
              </div>
              {index < 2 && (
                <div
                  className={`flex-1 h-1 mx-4 rounded-full ${
                    index <
                    (['metadata', 'steps', 'outcomes'] as WizardStep[]).indexOf(currentStep)
                      ? 'bg-[var(--color-status-success)]'
                      : 'bg-[var(--color-interactive-active)]'
                  }`}
                />
              )}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-6 p-4 bg-[var(--color-status-danger-bg)] border border-[var(--color-status-danger)]/50 rounded-lg flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-[var(--color-status-danger)] mt-0.5" />
          <div>
            <h3 className="font-semibold text-[var(--color-status-danger)]">Error</h3>
            <p className="text-[var(--color-status-danger)]">{error}</p>
          </div>
        </div>
      )}

      {/* Form Content */}
      <div className="bg-[var(--color-surface-raised)] rounded-lg shadow-md p-6 mb-6">
        {currentStep === 'metadata' && (
          <ScenarioForm
            initialData={scenarioData}
            onSubmit={handleScenarioDataChange}
            isLoading={isSubmitting}
          />
        )}

        {currentStep === 'steps' && (
          <StepManager
            steps={steps}
            onChange={handleStepsChange}
            onStepSelect={setSelectedStepIndex}
            selectedStepIndex={selectedStepIndex}
          />
        )}

        {currentStep === 'outcomes' && (
          <div className="space-y-6">
            {/* Info Banner */}
            <div className="bg-[var(--color-status-info-bg)] border border-[var(--color-status-info)]/50 rounded-lg p-4">
              <h3 className="font-semibold text-[var(--color-status-info)] mb-2">ℹ️ Expected Outcomes (Optional)</h3>
              <p className="text-sm text-[var(--color-status-info)]/90 mb-2">
                This step is <strong>optional</strong>. Use it only if you need advanced validation:
              </p>
              <ul className="text-sm text-[var(--color-status-info)]/90 list-disc list-inside space-y-1">
                <li><strong>CommandKind validation</strong> - Verify Houndify's classification (NavigationCommand, MusicCommand, etc.)</li>
                <li><strong>Confidence thresholds</strong> - Ensure AI understood with minimum confidence score</li>
                <li><strong>Entity extraction</strong> - Validate specific data was extracted (destination, artist, etc.)</li>
              </ul>
              <p className="text-sm text-[var(--color-status-info)]/90 mt-2">
                💡 <strong>For most scenarios</strong>, the Expected Response in Step 2 is sufficient. You can skip this step.
              </p>
            </div>

            {/* Step Selector */}
            <div>
              <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-2">
                Configure outcomes for:
              </label>
              <select
                value={selectedStepIndex}
                onChange={(e) => setSelectedStepIndex(parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-[var(--color-border-strong)] rounded-md bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-border-focus)]"
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

      {/* Navigation Buttons */}
      <div className="flex justify-between">
        <button
          onClick={handleBack}
          disabled={currentStep === 'metadata' || isSubmitting}
          className="flex items-center gap-2 px-6 py-3 border border-[var(--color-border-strong)] text-[var(--color-content-secondary)] rounded-lg hover:bg-[var(--color-interactive-hover)] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Back
        </button>

        <div className="flex gap-3">
          <button
            onClick={() => navigate('/scenarios')}
            disabled={isSubmitting}
            className="px-6 py-3 border border-[var(--color-border-strong)] text-[var(--color-content-secondary)] rounded-lg hover:bg-[var(--color-interactive-hover)] disabled:opacity-50 transition-colors"
          >
            Cancel
          </button>

          {currentStep !== 'outcomes' ? (
            <button
              onClick={handleNext}
              disabled={isSubmitting}
              className="flex items-center gap-2 px-6 py-3 text-white rounded-lg hover:shadow-lg hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              style={{ background: 'linear-gradient(135deg, #2A6B6E 0%, #11484D 100%)' }}
            >
              Next
              <ArrowRight className="w-4 h-4" />
            </button>
          ) : (
            <>
              {/* Skip button for optional step */}
              <button
                onClick={handleSubmit}
                disabled={isSubmitting}
                className="flex items-center gap-2 px-6 py-3 border border-[var(--color-border-strong)] text-[var(--color-content-secondary)] rounded-lg hover:bg-[var(--color-interactive-hover)] disabled:opacity-50 transition-colors"
              >
                Skip & Create
              </button>
              <button
                onClick={handleSubmit}
                disabled={isSubmitting}
                className="flex items-center gap-2 px-6 py-3 text-white rounded-lg hover:shadow-lg hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                style={{ background: 'linear-gradient(135deg, #2A6B6E 0%, #11484D 100%)' }}
              >
                <Save className="w-4 h-4" />
                {isSubmitting ? 'Creating...' : 'Create Scenario'}
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default ScenarioCreate;

