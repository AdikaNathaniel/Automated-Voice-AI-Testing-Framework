/**
 * Scenario Execution Page
 *
 * Displays real-time execution progress for multi-turn scenarios with:
 * - Live step-by-step progress updates via Socket.IO
 * - Conversation state tracking
 * - Validation results for each step (Houndify + LLM ensemble)
 * - Overall execution status
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link as RouterLink } from 'react-router-dom';
import {
  ArrowLeft,
  CheckCircle,
  XCircle,
  Clock,
  MessageSquare,
  Activity,
  Mic,
  Volume2,
  Brain,
  Zap,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  AlertCircle,
  ArrowRight,
} from 'lucide-react';
import { multiTurnService } from '../../services/multiTurn.service';
import { websocketService } from '../../services/websocket.service';
import AudioPlayer from '../../components/Validation/AudioPlayer';
import ValidationDetailsCard from '../../components/Validation/ValidationDetailsCard';
import type { MultiTurnExecution, StepExecution } from '../../types/multiTurn';

const ScenarioExecution: React.FC = () => {
  const { executionId } = useParams<{ executionId: string }>();
  const navigate = useNavigate();
  const [execution, setExecution] = useState<MultiTurnExecution | null>(null);
  const [steps, setSteps] = useState<StepExecution[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedLanguage, setSelectedLanguage] = useState<string>('');

  useEffect(() => {
    if (!executionId) return;

    loadExecutionData();
    setupSocketListeners();

    return () => {
      cleanupSocketListeners();
    };
  }, [executionId]);

  // Handle race condition: If execution completed before WebSocket listeners were set up,
  // reload data once to get the final results
  useEffect(() => {
    if (execution?.status === 'completed' && steps.length === 0) {
      console.log('[ScenarioExecution] Execution completed but no steps loaded - reloading data');
      loadExecutionData();
    }
  }, [execution?.status, steps.length]);

  // Extract available languages from all steps
  const availableLanguages = React.useMemo(() => {
    const langs = new Set<string>();
    steps.forEach(step => {
      if (step.audio_data_urls) {
        Object.keys(step.audio_data_urls).forEach(lang => langs.add(lang));
      }
      if (step.response_audio_urls) {
        Object.keys(step.response_audio_urls).forEach(lang => langs.add(lang));
      }
    });
    return Array.from(langs).sort();
  }, [steps]);

  // Set initial selected language
  React.useEffect(() => {
    if (availableLanguages.length > 0 && !selectedLanguage) {
      setSelectedLanguage(availableLanguages[0]);
    }
  }, [availableLanguages, selectedLanguage]);

  // Helper function to get language flag emoji
  const getLanguageFlag = (langCode: string): string => {
    const flagMap: { [key: string]: string } = {
      'en-US': '🇺🇸',
      'es-ES': '🇪🇸',
      'fr-FR': '🇫🇷',
      'en': '🇺🇸',
      'es': '🇪🇸',
      'fr': '🇫🇷',
    };
    return flagMap[langCode] || '🌐';
  };

  const loadExecutionData = async () => {
    if (!executionId) return;

    try {
      setLoading(true);
      setError(null);

      // Load execution status
      const execution = await multiTurnService.getExecutionStatus(executionId);
      setExecution(execution);

      // Load step executions
      const stepsResponse = await multiTurnService.getStepExecutions(executionId);
      setSteps(stepsResponse.steps || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load execution data');
    } finally {
      setLoading(false);
    }
  };

  const setupSocketListeners = () => {
    if (!executionId) return;

    // Listen for execution started
    websocketService.on('multi_turn_execution_started', handleExecutionStarted);

    // Listen for step started
    websocketService.on('multi_turn_step_started', handleStepStarted);

    // Listen for step completed
    websocketService.on('multi_turn_step_completed', handleStepCompleted);

    // Listen for execution completed
    websocketService.on('multi_turn_execution_completed', handleExecutionCompleted);

    // Listen for execution failed
    websocketService.on('multi_turn_execution_failed', handleExecutionFailed);
  };

  const cleanupSocketListeners = () => {
    websocketService.off('multi_turn_execution_started', handleExecutionStarted);
    websocketService.off('multi_turn_step_started', handleStepStarted);
    websocketService.off('multi_turn_step_completed', handleStepCompleted);
    websocketService.off('multi_turn_execution_completed', handleExecutionCompleted);
    websocketService.off('multi_turn_execution_failed', handleExecutionFailed);
  };

  const handleExecutionStarted = (data: any) => {
    if (data.execution_id === executionId) {
      setExecution((prev) => prev ? { ...prev, status: 'in_progress' } : null);
    }
  };

  const handleStepStarted = (data: any) => {
    if (data.execution_id === executionId) {
      setExecution((prev) => prev ? { ...prev, current_step_order: data.step_order } : null);
    }
  };

  const handleStepCompleted = (data: any) => {
    if (data.execution_id === executionId) {
      // Add or update step in the list
      setSteps((prev) => {
        const existingIndex = prev.findIndex((s) => s.id === data.step_execution_id);
        const newStep: StepExecution = {
          id: data.step_execution_id,
          step_id: data.step_id || '',
          multi_turn_execution_id: executionId,
          step_order: data.step_order,
          user_utterance: data.user_utterance,
          audio_data_urls: data.audio_data_urls,  // Map of language codes to input audio URLs
          response_audio_urls: data.response_audio_urls,  // Map of language codes to response audio URLs
          request_id: data.request_id,
          ai_response: data.ai_response,
          transcription: data.transcription,
          command_kind: data.command_kind,
          confidence_score: data.confidence_score,
          validation_passed: data.validation_passed,
          validation_details: data.validation_details,
          response_time_ms: data.response_time_ms,
          executed_at: data.executed_at,
          conversation_state_before: null,
          conversation_state_after: null,
        };

        if (existingIndex >= 0) {
          const updated = [...prev];
          updated[existingIndex] = newStep;
          return updated;
        }
        return [...prev, newStep].sort((a, b) => a.step_order - b.step_order);
      });
    }
  };

  const handleExecutionCompleted = (data: any) => {
    if (data.execution_id === executionId) {
      setExecution((prev) =>
        prev
          ? {
              ...prev,
              status: 'completed',
              all_steps_passed: data.all_steps_passed,
              completed_at: data.completed_at,
            }
          : null
      );
    }
  };

  const handleExecutionFailed = (data: any) => {
    if (data.execution_id === executionId) {
      setExecution((prev) =>
        prev
          ? {
              ...prev,
              status: 'failed',
              error_message: data.error_message,
            }
          : null
      );
    }
  };

  // Count steps by final decision, not just validation_passed
  // final_decision can be 'pass', 'fail', or 'uncertain'
  const passedSteps = steps.filter(s => {
    const finalDecision = s.validation_details?.final_decision;
    return finalDecision === 'pass' || (finalDecision === undefined && s.validation_passed === true);
  }).length;
  const failedSteps = steps.filter(s => {
    const finalDecision = s.validation_details?.final_decision;
    return finalDecision === 'fail';
  }).length;
  const needsReviewSteps = steps.filter(s => {
    const finalDecision = s.validation_details?.final_decision;
    return finalDecision === 'uncertain' || (s.validation_passed === false && finalDecision === undefined);
  }).length;

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-6">
        <RouterLink
          to="/executions"
          className="inline-flex items-center gap-2 text-sm text-[var(--color-content-secondary)] hover:text-[var(--color-content-primary)] mb-4 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Executions
        </RouterLink>

        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h1 className="text-2xl font-bold text-[var(--color-content-primary)]">Scenario Execution</h1>
            {execution && (
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                execution.status === 'completed' ? 'bg-[var(--color-status-success-bg)] text-[var(--color-status-success)]' :
                execution.status === 'failed' ? 'bg-[var(--color-status-danger-bg)] text-[var(--color-status-danger)]' :
                execution.status === 'in_progress' ? 'bg-[var(--color-status-info-bg)] text-[var(--color-status-info)]' :
                'bg-[var(--color-surface-inset)] text-[var(--color-content-secondary)]'
              }`}>
                {execution.status.replace('_', ' ')}
              </span>
            )}
          </div>
          <button
            onClick={loadExecutionData}
            className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-[var(--color-content-secondary)] bg-[var(--color-surface-raised)] border border-[var(--color-border-strong)] rounded-lg hover:bg-[var(--color-interactive-hover)] transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
        </div>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="flex flex-col items-center justify-center py-20">
          <div className="w-12 h-12 border-4 border-[var(--color-border-default)] rounded-full animate-spin mb-4" style={{ borderTopColor: '#2A6B6E' }}></div>
          <p className="text-[var(--color-content-secondary)]">Loading execution data...</p>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="bg-[var(--color-status-danger-bg)] border border-[var(--color-status-danger)] rounded-xl p-5 mb-6">
          <div className="flex items-center gap-2 text-[var(--color-status-danger)]">
            <XCircle className="w-5 h-5" />
            <p>{error}</p>
          </div>
        </div>
      )}

      {/* Execution Summary */}
      {!loading && execution && (
        <>
          {/* Stats Cards */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
            <div className="bg-[var(--color-surface-raised)] rounded-xl p-5 shadow-sm border border-[var(--color-border-default)]">
              <div className="flex items-center gap-3 mb-2">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                  execution.status === 'completed' ? 'bg-[var(--color-status-success-bg)]' :
                  execution.status === 'failed' ? 'bg-[var(--color-status-danger-bg)]' :
                  execution.status === 'in_progress' ? 'bg-[var(--color-status-info-bg)]' : 'bg-[var(--color-surface-inset)]'
                }`}>
                  {execution.status === 'completed' && <CheckCircle className="w-5 h-5 text-[var(--color-status-success)]" />}
                  {execution.status === 'failed' && <XCircle className="w-5 h-5 text-[var(--color-status-danger)]" />}
                  {execution.status === 'in_progress' && <Activity className="w-5 h-5 text-[var(--color-status-info)] animate-pulse" />}
                  {execution.status === 'pending' && <Clock className="w-5 h-5 text-[var(--color-content-secondary)]" />}
                </div>
                <div>
                  <p className="text-sm font-semibold text-[var(--color-content-primary)] capitalize">
                    {execution.status.replace('_', ' ')}
                  </p>
                  <p className="text-xs text-[var(--color-content-muted)]">Status</p>
                </div>
              </div>
            </div>

            <div className="bg-[var(--color-surface-raised)] rounded-xl p-5 shadow-sm border border-[var(--color-border-default)]">
              <div className="flex items-center gap-3 mb-2">
                <div className="w-10 h-10 rounded-lg bg-[var(--color-surface-inset)] flex items-center justify-center">
                  <MessageSquare className="w-5 h-5 text-[var(--color-content-secondary)]" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-[var(--color-content-primary)]">
                    {execution.current_step_order || 0}/{execution.total_steps}
                  </p>
                  <p className="text-xs text-[var(--color-content-muted)]">Steps Completed</p>
                </div>
              </div>
              <div className="w-full bg-[var(--color-surface-inset)] rounded-full h-2 overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{
                    width: `${((execution.current_step_order || 0) / execution.total_steps) * 100}%`,
                    background: 'linear-gradient(135deg, #2A6B6E 0%, #11484D 100%)',
                  }}
                />
              </div>
            </div>

            <div className="bg-[var(--color-surface-raised)] rounded-xl p-5 shadow-sm border border-[var(--color-border-default)]">
              <div className="flex items-center gap-3 mb-2">
                <div className="w-10 h-10 rounded-lg bg-[var(--color-status-success-bg)] flex items-center justify-center">
                  <CheckCircle className="w-5 h-5 text-[var(--color-status-success)]" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-[var(--color-status-success)]">{passedSteps}</p>
                  <p className="text-xs text-[var(--color-content-muted)]">Steps Passed</p>
                </div>
              </div>
            </div>

            <div className="bg-[var(--color-surface-raised)] rounded-xl p-5 shadow-sm border border-[var(--color-border-default)]">
              <div className="flex items-center gap-3 mb-2">
                <div className="w-10 h-10 rounded-lg bg-[var(--color-status-warning-bg)] flex items-center justify-center">
                  <AlertCircle className="w-5 h-5 text-[var(--color-status-warning)]" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-[var(--color-status-warning)]">{needsReviewSteps}</p>
                  <p className="text-xs text-[var(--color-content-muted)]">Needs Review</p>
                </div>
              </div>
            </div>

            <div className="bg-[var(--color-surface-raised)] rounded-xl p-5 shadow-sm border border-[var(--color-border-default)]">
              <div className="flex items-center gap-3 mb-2">
                <div className="w-10 h-10 rounded-lg bg-[var(--color-status-danger-bg)] flex items-center justify-center">
                  <XCircle className="w-5 h-5 text-[var(--color-status-danger)]" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-[var(--color-status-danger)]">{failedSteps}</p>
                  <p className="text-xs text-[var(--color-content-muted)]">Steps Failed</p>
                </div>
              </div>
            </div>
          </div>

          {/* Execution Details */}
          <div className="bg-[var(--color-surface-raised)] rounded-xl p-5 shadow-sm border border-[var(--color-border-default)] mb-6">
            <h2 className="text-lg font-semibold text-[var(--color-content-primary)] mb-4">Execution Details</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <p className="text-[var(--color-content-muted)] mb-1">Execution ID</p>
                <p className="font-mono text-xs text-[var(--color-content-secondary)]">{executionId}</p>
              </div>
              <div>
                <p className="text-[var(--color-content-muted)] mb-1">Scenario</p>
                <p className="text-[var(--color-content-secondary)]">{execution.scenario_name || 'Unknown'}</p>
              </div>
              <div>
                <p className="text-[var(--color-content-muted)] mb-1">Started</p>
                <p className="text-[var(--color-content-secondary)]">
                  {execution.started_at ? new Date(execution.started_at).toLocaleString() : '—'}
                </p>
              </div>
              <div>
                <p className="text-[var(--color-content-muted)] mb-1">Completed</p>
                <p className="text-[var(--color-content-secondary)]">
                  {execution.completed_at ? new Date(execution.completed_at).toLocaleString() : '—'}
                </p>
              </div>
            </div>

            {/* Error Message */}
            {execution.error_message && (
              <div className="mt-4 p-4 bg-[var(--color-status-danger-bg)] border border-[var(--color-status-danger)] rounded-lg">
                <div className="flex items-center gap-2 text-[var(--color-status-danger)] mb-1">
                  <AlertCircle className="w-4 h-4" />
                  <span className="font-semibold">Execution Error</span>
                </div>
                <p className="text-sm text-[var(--color-status-danger)]">{execution.error_message}</p>
              </div>
            )}
          </div>

          {/* Step Executions */}
          <div className="bg-[var(--color-surface-raised)] rounded-xl shadow-sm border border-[var(--color-border-default)]">
            <div className="p-5 border-b border-[var(--color-border-subtle)]">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-[var(--color-content-primary)]">
                  Conversation Timeline
                  <span className="ml-2 text-sm font-normal text-[var(--color-content-muted)]">
                    ({steps.length} steps)
                  </span>
                </h2>

                {/* Language Tabs - Page Level */}
                {availableLanguages.length > 1 && (
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-medium text-[var(--color-content-muted)] mr-1">Language:</span>
                    <div className="flex gap-1.5">
                      {availableLanguages.map((lang) => (
                        <button
                          key={lang}
                          onClick={() => setSelectedLanguage(lang)}
                          className={`px-2.5 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5 ${
                            selectedLanguage === lang
                              ? 'bg-gradient-to-r from-[#2A6B6E] to-[#11484D] text-white shadow-md'
                              : 'bg-[var(--color-surface-raised)] text-[var(--color-content-secondary)] border border-[var(--color-border-default)] hover:border-[#2A6B6E] hover:border-[var(--color-accent-500)] hover:shadow-sm'
                          }`}
                        >
                          <span className="text-base">{getLanguageFlag(lang)}</span>
                          <span>{lang.toUpperCase()}</span>
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>

            <div className="p-5">
              {steps.length === 0 && (
                <div className="text-center py-12">
                  <Clock className="w-12 h-12 text-[var(--color-content-muted)] mx-auto mb-4 animate-pulse" />
                  {execution.status === 'in_progress' ? (
                    <p className="text-[var(--color-content-muted)]">Waiting for steps to execute...</p>
                  ) : execution.status === 'completed' ? (
                    <p className="text-[var(--color-content-muted)]">Loading step results...</p>
                  ) : (
                    <p className="text-[var(--color-content-muted)]">No steps executed</p>
                  )}
                </div>
              )}

              <div className="space-y-0">
                {steps.map((step, index) => (
                  <StepExecutionCard
                    key={step.id}
                    step={step}
                    isLast={index === steps.length - 1}
                    selectedLanguage={selectedLanguage}
                  />
                ))}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

/**
 * Step Execution Card Component with timeline layout
 */
interface StepExecutionCardProps {
  step: StepExecution;
  isLast: boolean;
  selectedLanguage: string;
}

const StepExecutionCard: React.FC<StepExecutionCardProps> = ({ step, isLast, selectedLanguage }) => {
  const [expanded, setExpanded] = useState(false);

  // Determine validation style based on final_decision (not just validation_passed)
  // final_decision: 'pass' | 'fail' | 'uncertain'
  const finalDecision = step.validation_details?.final_decision;

  // Helper to get language-specific utterance
  const getUtteranceForLanguage = (lang: string): string => {
    // Check if step has per-language results with utterances
    const perLangResults = step.validation_details?.per_language_results || step.validation_details?.perLanguageResults;
    if (perLangResults && perLangResults[lang]) {
      // Try snake_case
      if (perLangResults[lang].user_utterance) {
        return perLangResults[lang].user_utterance;
      }
      // Try camelCase
      if (perLangResults[lang].userUtterance) {
        return perLangResults[lang].userUtterance;
      }
    }

    // Check if validation_details has it at top level (some backends send it differently)
    const langKey = lang.toLowerCase().replace('-', '_');
    if (step.validation_details?.[`${langKey}_user_utterance`]) {
      return step.validation_details[`${langKey}_user_utterance`];
    }

    // Fallback to default utterance
    return step.user_utterance;
  };

  // Helper to get language-specific AI response
  const getAIResponseForLanguage = (lang: string): string => {
    // Check if step has per-language results with AI responses
    const perLangResults = step.validation_details?.per_language_results || step.validation_details?.perLanguageResults;
    if (perLangResults && perLangResults[lang]) {
      // Try snake_case
      if (perLangResults[lang].ai_response) {
        return perLangResults[lang].ai_response;
      }
      // Try camelCase
      if (perLangResults[lang].aiResponse) {
        return perLangResults[lang].aiResponse;
      }
      // Try transcription as fallback
      if (perLangResults[lang].transcription) {
        return perLangResults[lang].transcription;
      }
    }

    // Check if validation_details has it at top level
    const langKey = lang.toLowerCase().replace('-', '_');
    if (step.validation_details?.[`${langKey}_ai_response`]) {
      return step.validation_details[`${langKey}_ai_response`];
    }

    // Fallback to default response
    return step.ai_response || step.transcription || '—';
  };

  const getValidationStyle = () => {
    if (finalDecision === 'pass') {
      return { icon: <CheckCircle className="w-4 h-4 text-[var(--color-status-success)]" />, color: 'border-[var(--color-status-success)] bg-[var(--color-status-success-bg)]', label: 'Passed', labelColor: 'bg-[var(--color-status-success-bg)] text-[var(--color-status-success)]' };
    }
    if (finalDecision === 'fail') {
      return { icon: <XCircle className="w-4 h-4 text-[var(--color-status-danger)]" />, color: 'border-[var(--color-status-danger)] bg-[var(--color-status-danger-bg)]', label: 'Failed', labelColor: 'bg-[var(--color-status-danger-bg)] text-[var(--color-status-danger)]' };
    }
    if (finalDecision === 'uncertain') {
      return { icon: <AlertCircle className="w-4 h-4 text-[var(--color-status-warning)]" />, color: 'border-[var(--color-status-warning)] bg-[var(--color-status-warning-bg)]', label: 'Needs Review', labelColor: 'bg-[var(--color-status-warning-bg)] text-[var(--color-status-warning)]' };
    }
    // Fallback to validation_passed for backwards compatibility
    if (step.validation_passed === true) {
      return { icon: <CheckCircle className="w-4 h-4 text-[var(--color-status-success)]" />, color: 'border-[var(--color-status-success)] bg-[var(--color-status-success-bg)]', label: 'Passed', labelColor: 'bg-[var(--color-status-success-bg)] text-[var(--color-status-success)]' };
    }
    if (step.validation_passed === false) {
      return { icon: <XCircle className="w-4 h-4 text-[var(--color-status-danger)]" />, color: 'border-[var(--color-status-danger)] bg-[var(--color-status-danger-bg)]', label: 'Failed', labelColor: 'bg-[var(--color-status-danger-bg)] text-[var(--color-status-danger)]' };
    }
    return { icon: <Clock className="w-4 h-4 text-[var(--color-content-muted)]" />, color: 'border-[var(--color-border-strong)] bg-[var(--color-surface-inset)]', label: 'Pending', labelColor: 'bg-[var(--color-surface-inset)] text-[var(--color-content-secondary)]' };
  };

  const validationStyle = getValidationStyle();

  // Parse validation details
  const validationDetails = step.validation_details || {};
  const houndifyResult = validationDetails.houndify_result || validationDetails.houndifyResult;
  const llmResult = validationDetails.ensemble_result || validationDetails.ensembleResult || validationDetails.llm_result;
  const perLangResults = validationDetails.per_language_results || validationDetails.perLanguageResults;

  return (
    <div className="relative flex gap-4">
      {/* Timeline connector */}
      <div className="flex flex-col items-center">
        <div className={`w-10 h-10 rounded-full border-2 flex items-center justify-center ${validationStyle.color}`}>
          {validationStyle.icon}
        </div>
        {!isLast && (
          <div className="w-0.5 h-full bg-[var(--color-interactive-active)] my-1" />
        )}
      </div>

      {/* Step content */}
      <div className="flex-1 pb-6">
        <div
          className="bg-[var(--color-surface-raised)] rounded-xl border border-[var(--color-border-default)] shadow-sm hover:shadow-md transition-shadow cursor-pointer"
          onClick={() => setExpanded(!expanded)}
        >
          {/* Step header */}
          <div className="p-4">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-3">
                <span className="text-sm font-semibold text-[var(--color-content-secondary)]">Step {step.step_order}</span>
                {step.command_kind && (
                  <span className="px-2 py-0.5 rounded-full text-xs bg-[var(--color-status-info-bg)] text-[var(--color-status-info)] font-mono">
                    {step.command_kind}
                  </span>
                )}
                <span className={`px-2 py-0.5 rounded-full text-xs ${validationStyle.labelColor}`}>
                  {validationStyle.label}
                </span>
              </div>
              <div className="flex items-center gap-3 text-xs text-[var(--color-content-muted)]">
                {step.response_time_ms && (
                  <span className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {step.response_time_ms}ms
                  </span>
                )}
                {step.confidence_score !== undefined && step.confidence_score !== null && (
                  <span className="flex items-center gap-1">
                    <Activity className="w-3 h-3" />
                    {(step.confidence_score * 100).toFixed(0)}%
                  </span>
                )}
                {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </div>
            </div>

            {/* User utterance and AI response - Language-specific */}
            <div className="flex items-start gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <Mic className="w-3 h-3 text-[var(--color-status-info)]" />
                  <span className="text-xs font-medium text-[var(--color-content-muted)]">User</span>
                </div>
                <p className="text-sm text-[var(--color-content-primary)]">
                  {selectedLanguage ? getUtteranceForLanguage(selectedLanguage) : step.user_utterance}
                </p>
              </div>
              <ArrowRight className="w-4 h-4 text-[var(--color-content-muted)] mt-4 flex-shrink-0" />
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <Volume2 className="w-3 h-3 text-[var(--color-status-success)]" />
                  <span className="text-xs font-medium text-[var(--color-content-muted)]">AI Response</span>
                </div>
                <p className="text-sm text-[var(--color-content-primary)] line-clamp-2">
                  {selectedLanguage ? getAIResponseForLanguage(selectedLanguage) : (step.ai_response || step.transcription || '—')}
                </p>
              </div>
            </div>
          </div>

          {/* Expanded content */}
          {expanded && (
            <div
              className="border-t border-[var(--color-border-subtle)] p-4 bg-[var(--color-surface-base)]/30 space-y-4"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Transcription */}
              {step.transcription && step.transcription !== step.ai_response && (
                <div>
                  <p className="text-xs font-medium text-[var(--color-content-muted)] mb-1">Transcription</p>
                  <p className="text-sm text-[var(--color-content-secondary)] bg-[var(--color-surface-raised)] p-3 rounded-lg border border-[var(--color-border-subtle)]">
                    {step.transcription}
                  </p>
                </div>
              )}

              {/* User Input Audio - Filtered by selected language */}
              {step.audio_data_urls && selectedLanguage && step.audio_data_urls[selectedLanguage] && (
                <div>
                  <p className="text-xs font-medium text-[var(--color-content-muted)] mb-2 flex items-center gap-2">
                    <Mic className="w-3 h-3" />
                    User Input Audio
                  </p>
                  <div className="bg-[var(--color-surface-raised)] rounded-lg border border-[var(--color-border-default)] overflow-hidden">
                    <div className="px-3 py-2 bg-[var(--color-surface-inset)]/50 border-b border-[var(--color-border-subtle)]">
                      <span className="text-xs font-medium text-[var(--color-content-secondary)]">{selectedLanguage.toUpperCase()} - User Input</span>
                    </div>
                    <AudioPlayer audioUrl={step.audio_data_urls[selectedLanguage]} />
                  </div>
                </div>
              )}

              {/* Response Audio - Filtered by selected language */}
              {step.response_audio_urls && selectedLanguage && step.response_audio_urls[selectedLanguage] && (
                <div>
                  <p className="text-xs font-medium text-[var(--color-content-muted)] mb-2 flex items-center gap-2">
                    <Volume2 className="w-3 h-3" />
                    AI Response Audio
                  </p>
                  <div className="bg-[var(--color-surface-raised)] rounded-lg border border-[var(--color-border-default)] overflow-hidden">
                    <div className="px-3 py-2 bg-[var(--color-status-success-bg)] border-b border-[var(--color-status-success-bg)]">
                      <span className="text-xs font-medium text-[var(--color-status-success)]">{selectedLanguage.toUpperCase()} - AI Response</span>
                    </div>
                    <AudioPlayer audioUrl={step.response_audio_urls[selectedLanguage]} />
                  </div>
                </div>
              )}

              {/* Comprehensive Validation Details - Language-specific */}
              <ValidationDetailsCard
                houndifyResult={selectedLanguage && perLangResults?.[selectedLanguage]?.houndify_result || houndifyResult}
                llmResult={selectedLanguage && perLangResults?.[selectedLanguage]?.ensemble_result || llmResult}
                finalDecision={selectedLanguage && perLangResults?.[selectedLanguage]?.final_decision || validationDetails.final_decision}
                reviewStatus={selectedLanguage && perLangResults?.[selectedLanguage]?.review_status || validationDetails.review_status}
              />

              {/* Error Message */}
              {step.error_message && (
                <div className="p-3 bg-[var(--color-status-danger-bg)] rounded-lg border border-[var(--color-status-danger)]">
                  <div className="flex items-center gap-2 text-[var(--color-status-danger)] mb-1">
                    <AlertCircle className="w-4 h-4" />
                    <span className="font-semibold text-sm">Error</span>
                  </div>
                  <p className="text-sm text-[var(--color-status-danger)]">{step.error_message}</p>
                </div>
              )}

              {/* Metadata */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
                {step.executed_at && (
                  <div className="bg-[var(--color-surface-raised)] p-2 rounded-lg border border-[var(--color-border-subtle)]">
                    <p className="text-[var(--color-content-muted)] mb-0.5">Executed At</p>
                    <p className="font-medium text-[var(--color-content-secondary)]">
                      {new Date(step.executed_at).toLocaleTimeString()}
                    </p>
                  </div>
                )}
                {step.request_id && (
                  <div className="bg-[var(--color-surface-raised)] p-2 rounded-lg border border-[var(--color-border-subtle)]">
                    <p className="text-[var(--color-content-muted)] mb-0.5">Request ID</p>
                    <p className="font-mono text-[var(--color-content-secondary)] truncate">{step.request_id}</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ScenarioExecution;

