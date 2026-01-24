/**
 * Scenario Detail Page
 *
 * Displays scenario details with approval workflow:
 * - Scenario metadata and steps
 * - Approval status badge
 * - Submit for Review button
 * - Approve/Reject buttons (for reviewers)
 * - Review notes and reviewer information
 */

import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useSelector } from 'react-redux';
import {
  ArrowLeft,
  Edit,
  Play,
  CheckCircle,
  XCircle,
  Send,
  AlertCircle,
  Clock,
  User,
  Target,
  History,
  TrendingUp,
  FileText,
} from 'lucide-react';
import { multiTurnService } from '../../services/multiTurn.service';
import type { ScenarioScript } from '../../types/multiTurn';
import Modal from '../../components/Modal/Modal';
import { useModal } from '../../hooks/useModal';
import type { RootState } from '../../store';
import { LanguageSelector } from '../../components/Scenarios/LanguageSelector';
import { getBaselineHistory, approveBaseline } from '../../services/regression.service';
import type { BaselineHistoryResponse } from '../../types/regression';
import { useToast } from '../../components/common/Toast';

// Roles that can approve/reject scenarios
const APPROVAL_ROLES = ['org_admin', 'qa_lead'];

export const ScenarioDetail: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const { modalState, showError, showWarning, showSuccess, closeModal } = useModal();
  const { showToast } = useToast();
  const currentUser = useSelector((state: RootState) => state.auth.user);
  const [scenario, setScenario] = useState<ScenarioScript | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState(false);
  const [showReviewModal, setShowReviewModal] = useState<'approve' | 'reject' | null>(null);
  const [reviewNotes, setReviewNotes] = useState('');
  const [selectedLanguages, setSelectedLanguages] = useState<string[]>([]);
  const [baselineHistory, setBaselineHistory] = useState<BaselineHistoryResponse | null>(null);
  const [baselineLoading, setBaselineLoading] = useState(false);
  const [showBaselineModal, setShowBaselineModal] = useState(false);
  const [baselineNote, setBaselineNote] = useState('');

  // Check if current user can approve/reject this scenario
  const canReviewScenario = useMemo(() => {
    if (!currentUser || !scenario) return false;

    // Must have ADMIN or QA_LEAD role
    const hasApprovalRole = APPROVAL_ROLES.includes(currentUser.role?.toLowerCase() || '');
    if (!hasApprovalRole) return false;

    // Org admins can always approve (including self-approval)
    if (currentUser.role?.toLowerCase() === 'org_admin') return true;

    // QA_LEAD cannot approve their own scenarios
    const isCreator = scenario.created_by === currentUser.id;
    return !isCreator;
  }, [currentUser, scenario]);

  useEffect(() => {
    if (id) {
      loadScenario();
      loadBaselineHistory();
    }
  }, [id]);

  const loadScenario = async () => {
    if (!id) return;

    try {
      setLoading(true);
      setError(null);
      const data = await multiTurnService.getScenario(id);
      setScenario(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load scenario');
    } finally {
      setLoading(false);
    }
  };

  const loadBaselineHistory = async () => {
    if (!id) return;

    try {
      setBaselineLoading(true);
      const data = await getBaselineHistory(id);
      setBaselineHistory(data);
    } catch (err: any) {
      // Baseline history is optional - don't show error if not found
      console.log('No baseline history available:', err.message);
    } finally {
      setBaselineLoading(false);
    }
  };

  const handleSubmitForReview = async () => {
    if (!id) return;

    try {
      setActionLoading(true);
      await multiTurnService.submitForReview(id);
      showSuccess('Scenario submitted for review successfully');
      // Reload full scenario data after submission
      await loadScenario();
    } catch (err: any) {
      showError(`Failed to submit for review: ${err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  const handleApprove = async () => {
    if (!id) return;

    try {
      setActionLoading(true);
      await multiTurnService.approveScenario(id, reviewNotes);
      setShowReviewModal(null);
      setReviewNotes('');
      showSuccess('Scenario approved successfully');
      // Reload full scenario data after approval
      await loadScenario();
    } catch (err: any) {
      showError(`Failed to approve scenario: ${err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async () => {
    if (!id) return;

    if (!reviewNotes.trim()) {
      showWarning('Review notes are required when rejecting a scenario');
      return;
    }

    try {
      setActionLoading(true);
      await multiTurnService.rejectScenario(id, reviewNotes);
      setShowReviewModal(null);
      setReviewNotes('');
      showSuccess('Scenario rejected');
      // Reload full scenario data after rejection
      await loadScenario();
    } catch (err: any) {
      showError(`Failed to reject scenario: ${err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  const handleExecute = async () => {
    if (!id) return;

    try {
      const result = await multiTurnService.executeScenario(id, {
        script_id: id,
        language_codes: selectedLanguages.length > 0 ? selectedLanguages : undefined,
      });
      navigate(`/scenarios/executions/${result.execution_id}`);
    } catch (err: any) {
      showError(`Failed to execute scenario: ${err.message}`);
    }
  };

  const handleApproveBaseline = async () => {
    if (!id || !baselineHistory?.pending) return;

    try {
      setActionLoading(true);
      await approveBaseline(id, {
        status: baselineHistory.pending.status || 'pass',
        metrics: baselineHistory.pending.metrics || {},
        note: baselineNote || undefined,
      });

      showToast({
        type: 'success',
        title: 'Baseline Approved',
        message: 'The baseline has been successfully approved and set as the new reference.',
      });

      setShowBaselineModal(false);
      setBaselineNote('');

      // Reload baseline history
      await loadBaselineHistory();
    } catch (err: any) {
      showToast({
        type: 'error',
        title: 'Baseline Approval Failed',
        message: err.message || 'Failed to approve baseline',
      });
    } finally {
      setActionLoading(false);
    }
  };

  const getStatusBadge = () => {
    if (!scenario) return null;

    if (!scenario.is_active) {
      return (
        <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[var(--color-interactive-active)] text-[var(--color-content-secondary)]">
          <Clock className="w-4 h-4" />
          Inactive
        </span>
      );
    }

    switch (scenario.approval_status) {
      case 'approved':
        return (
          <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[var(--color-status-success-bg)] text-[var(--color-status-success)]">
            <CheckCircle className="w-4 h-4" />
            Approved
          </span>
        );
      case 'pending_review':
        return (
          <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[var(--color-status-warning-bg)] text-[var(--color-status-warning)]">
            <Clock className="w-4 h-4" />
            Pending Review
          </span>
        );
      case 'draft':
        return (
          <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[var(--color-surface-inset)] text-[var(--color-content-secondary)]">
            <Edit className="w-4 h-4" />
            Draft
          </span>
        );
      case 'rejected':
        return (
          <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[var(--color-status-danger-bg)] text-[var(--color-status-danger)]">
            <XCircle className="w-4 h-4" />
            Rejected
          </span>
        );
      default:
        return null;
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

  if (error || !scenario) {
    return (
      <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-sm">
        <div className="bg-[var(--color-status-danger-bg)] border border-[var(--color-status-danger-bg)] rounded-lg p-4">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-[var(--color-status-danger)] mt-0.5" />
            <div>
              <h3 className="font-semibold text-[var(--color-status-danger)]">Error</h3>
              <p className="text-[var(--color-status-danger)]">{error || 'Scenario not found'}</p>
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
          onClick={() => navigate('/scenarios')}
          className="flex items-center gap-2 text-[var(--color-content-secondary)] hover:text-[var(--color-content-primary)] mb-4"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Scenarios
        </button>

        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-4 mb-2">
              <h1 className="text-2xl font-bold text-[var(--color-content-primary)] flex items-center gap-3">
                <FileText className="w-6 h-6" style={{ color: '#2A6B6E' }} />
                {scenario.name}
              </h1>
              {getStatusBadge()}
            </div>
            <p className="text-[var(--color-content-muted)]">Version {scenario.version}</p>
            {scenario.description && (
              <p className="text-[var(--color-content-secondary)] mt-2">{scenario.description}</p>
            )}
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3">
            <button
              onClick={() => navigate(`/scenarios/${id}/edit`)}
              className="flex items-center gap-2 px-4 py-2.5 border border-[var(--color-border-strong)] text-[var(--color-content-secondary)] rounded-lg hover:bg-[var(--color-interactive-hover)] transition-all"
            >
              <Edit className="w-4 h-4" />
              Edit
            </button>
            <button
              onClick={handleExecute}
              disabled={!scenario.is_active}
              className="flex items-center gap-2 px-4 py-2.5 text-white rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg hover:-translate-y-0.5"
              style={scenario.is_active ? { background: 'linear-gradient(135deg, #2A6B6E 0%, #11484D 100%)' } : { background: '#9CA3AF' }}
            >
              <Play className="w-4 h-4" />
              Execute
            </button>
          </div>
        </div>

        {/* Language Selection - Only show if scenario has multiple languages */}
        {scenario.languages && scenario.languages.length > 1 && (
          <div className="mt-6 pt-6 border-t border-[var(--color-border-default)]">
            <LanguageSelector
              availableLanguages={scenario.languages}
              selectedLanguages={selectedLanguages}
              onChange={setSelectedLanguages}
            />
          </div>
        )}
      </div>

      {/* Regression Baseline Section */}
      {scenario.is_active && (
        <div className="bg-[var(--color-surface-raised)] rounded-xl shadow-md p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Target className="w-5 h-5 text-[var(--color-status-info)]" />
              <h2 className="text-xl font-semibold text-[var(--color-content-primary)]">Regression Baseline</h2>
            </div>
            {baselineHistory?.history && baselineHistory.history.length > 0 && (
              <button
                onClick={() => navigate(`/regressions/${id}/baselines`)}
                className="flex items-center gap-2 px-3 py-1.5 text-sm text-[var(--color-content-secondary)] hover:text-[var(--color-content-primary)] transition-colors"
              >
                <History className="w-4 h-4" />
                View History
              </button>
            )}
          </div>

          {baselineLoading ? (
            <div className="flex items-center justify-center p-8">
              <div className="w-8 h-8 border-4 border-[var(--color-border-default)] rounded-full animate-spin" style={{ borderTopColor: '#2A6B6E' }}></div>
            </div>
          ) : (
            <>
              {/* Current Baseline */}
              {baselineHistory?.history && baselineHistory.history.length > 0 ? (
                <div className="bg-[var(--color-status-emerald-bg)] border border-[var(--color-status-emerald-bg)] rounded-lg p-4 mb-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <CheckCircle className="w-5 h-5 text-[var(--color-status-emerald)]" />
                        <span className="font-semibold text-[var(--color-status-emerald)]">
                          Active Baseline (v{baselineHistory.history[0].version})
                        </span>
                      </div>
                      <div className="text-sm text-[var(--color-status-emerald)] space-y-1">
                        <p>
                          Status: <span className="font-medium">{baselineHistory.history[0].status}</span>
                        </p>
                        {baselineHistory.history[0].approvedAt && (
                          <p>
                            Approved: {new Date(baselineHistory.history[0].approvedAt).toLocaleDateString()} by {baselineHistory.history[0].approvedBy || 'Unknown'}
                          </p>
                        )}
                        {baselineHistory.history[0].note && (
                          <p className="mt-2 text-xs italic">"{baselineHistory.history[0].note}"</p>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="bg-[var(--color-status-amber-bg)] border border-[var(--color-status-amber-bg)] rounded-lg p-4 mb-4">
                  <div className="flex items-start gap-3">
                    <AlertCircle className="w-5 h-5 text-[var(--color-status-amber)] mt-0.5" />
                    <div>
                      <p className="font-medium text-[var(--color-status-amber)]">No Baseline Set</p>
                      <p className="text-sm text-[var(--color-status-amber)] mt-1">
                        Execute this scenario and approve the results as a baseline to enable regression detection.
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Pending Baseline */}
              {baselineHistory?.pending && (
                <div className="bg-[var(--color-status-info-bg)] border border-[var(--color-status-info-bg)] rounded-lg p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-3">
                        <TrendingUp className="w-5 h-5 text-[var(--color-status-info)]" />
                        <span className="font-semibold text-[var(--color-status-info)]">
                          Pending Baseline Approval
                        </span>
                      </div>

                      {/* Summary Row */}
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                        <div className="bg-[var(--color-surface-raised)] rounded-lg p-2 text-center">
                          <p className="text-xs text-[var(--color-content-muted)]">Status</p>
                          <p className={`font-semibold ${
                            baselineHistory.pending.status === 'completed' ? 'text-[var(--color-status-success)]' :
                            baselineHistory.pending.status === 'failed' ? 'text-[var(--color-status-danger)]' : 'text-[var(--color-content-secondary)]'
                          }`}>
                            {baselineHistory.pending.status || 'N/A'}
                          </p>
                        </div>
                        {baselineHistory.pending.validationSummary && (
                          <>
                            <div className="bg-[var(--color-surface-raised)] rounded-lg p-2 text-center">
                              <p className="text-xs text-[var(--color-content-muted)]">Steps Passed</p>
                              <p className="font-semibold text-[var(--color-status-success)]">
                                {baselineHistory.pending.validationSummary.passedSteps}/{baselineHistory.pending.validationSummary.totalSteps}
                              </p>
                            </div>
                            <div className="bg-[var(--color-surface-raised)] rounded-lg p-2 text-center">
                              <p className="text-xs text-[var(--color-content-muted)]">Steps Failed</p>
                              <p className={`font-semibold ${baselineHistory.pending.validationSummary.failedSteps > 0 ? 'text-[var(--color-status-danger)]' : 'text-[var(--color-content-secondary)]'}`}>
                                {baselineHistory.pending.validationSummary.failedSteps}
                              </p>
                            </div>
                            <div className="bg-[var(--color-surface-raised)] rounded-lg p-2 text-center">
                              <p className="text-xs text-[var(--color-content-muted)]">All Passed</p>
                              <p className={`font-semibold ${baselineHistory.pending.validationSummary.allPassed ? 'text-[var(--color-status-success)]' : 'text-[var(--color-status-warning)]'}`}>
                                {baselineHistory.pending.validationSummary.allPassed ? 'Yes' : 'No'}
                              </p>
                            </div>
                          </>
                        )}
                      </div>

                      {/* Metrics */}
                      {baselineHistory.pending.metrics && Object.keys(baselineHistory.pending.metrics).length > 0 && (
                        <div className="mb-4">
                          <p className="text-sm font-medium text-[var(--color-status-info)] mb-2">Validation Metrics</p>
                          <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                            {Object.entries(baselineHistory.pending.metrics).map(([key, value]) => (
                              <div key={key} className="bg-[var(--color-surface-raised)] rounded px-2 py-1 text-xs flex justify-between">
                                <span className="text-[var(--color-content-secondary)]">{key}:</span>
                                <span className="font-medium">
                                  {typeof value === 'number' ? value.toFixed(3) : String(value ?? 'N/A')}
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Step Details */}
                      {baselineHistory.pending.stepDetails && baselineHistory.pending.stepDetails.length > 0 && (
                        <div className="mb-4">
                          <p className="text-sm font-medium text-[var(--color-status-info)] mb-2">Step Results</p>
                          <div className="space-y-2 max-h-64 overflow-y-auto">
                            {baselineHistory.pending.stepDetails.map((step) => (
                              <div
                                key={step.stepOrder}
                                className={`bg-[var(--color-surface-raised)] rounded-lg p-3 border-l-4 ${
                                  step.validationPassed === true ? 'border-[var(--color-status-success)]' :
                                  step.validationPassed === false ? 'border-[var(--color-status-danger)]' : 'border-[var(--color-border-default)]'
                                }`}
                              >
                                <div className="flex items-center justify-between mb-1">
                                  <span className="text-xs font-semibold text-[var(--color-content-secondary)]">
                                    Step {step.stepOrder}
                                  </span>
                                  <span className={`text-xs px-2 py-0.5 rounded ${
                                    step.validationPassed === true ? 'bg-[var(--color-status-success-bg)] text-[var(--color-status-success)]' :
                                    step.validationPassed === false ? 'bg-[var(--color-status-danger-bg)] text-[var(--color-status-danger)]' : 'bg-[var(--color-surface-inset)] text-[var(--color-content-secondary)]'
                                  }`}>
                                    {step.validationPassed === true ? 'Passed' : step.validationPassed === false ? 'Failed' : 'Pending'}
                                  </span>
                                </div>
                                {step.userUtterance && (
                                  <p className="text-xs text-[var(--color-content-secondary)] mb-1">
                                    <span className="font-medium">User:</span> {step.userUtterance}
                                  </p>
                                )}
                                {step.aiResponse && (
                                  <p className="text-xs text-[var(--color-content-secondary)]">
                                    <span className="font-medium">AI:</span> {step.aiResponse}
                                  </p>
                                )}
                                {step.confidenceScore !== null && (
                                  <p className="text-xs text-[var(--color-content-muted)] mt-1">
                                    Confidence: {(step.confidenceScore * 100).toFixed(1)}%
                                  </p>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Detected At */}
                      {baselineHistory.pending.detectedAt && (
                        <p className="text-xs text-[var(--color-status-info)]">
                          Detected: {new Date(baselineHistory.pending.detectedAt).toLocaleString()}
                        </p>
                      )}
                    </div>
                  </div>

                  {/* Approve Button - Only for users with appropriate permissions */}
                  {canReviewScenario && (
                    <div className="mt-4 pt-4 border-t border-[var(--color-status-info-bg)]">
                      <button
                        onClick={() => setShowBaselineModal(true)}
                        disabled={actionLoading}
                        className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-[var(--color-status-info)] text-white rounded-lg hover:opacity-90 transition-all disabled:opacity-50"
                      >
                        <CheckCircle className="w-4 h-4" />
                        Approve as Baseline
                      </button>
                    </div>
                  )}

                  {!canReviewScenario && (
                    <p className="mt-4 pt-4 border-t border-[var(--color-status-info-bg)] text-xs text-[var(--color-status-info)]">
                      Only admins or QA leads can approve baselines
                    </p>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      )}

      {/* Approval Workflow Section */}
      {scenario.approval_status !== 'approved' && (
        <div className="bg-[var(--color-surface-raised)] rounded-xl shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold text-[var(--color-content-primary)] mb-4">Approval Workflow</h2>

          {/* Draft Status */}
          {scenario.approval_status === 'draft' && (
            <div className="space-y-4">
              <p className="text-[var(--color-content-secondary)]">
                This scenario is in draft status. Submit it for review when ready.
              </p>
              <button
                onClick={handleSubmitForReview}
                disabled={actionLoading}
                className="flex items-center gap-2 px-4 py-2.5 text-white rounded-lg transition-all disabled:opacity-50 hover:shadow-lg hover:-translate-y-0.5"
                style={{ background: 'linear-gradient(135deg, #2A6B6E 0%, #11484D 100%)' }}
              >
                <Send className="w-4 h-4" />
                {actionLoading ? 'Submitting...' : 'Submit for Review'}
              </button>
            </div>
          )}

          {/* Pending Review Status */}
          {scenario.approval_status === 'pending_review' && (
            <div className="space-y-4">
              <p className="text-[var(--color-content-secondary)]">
                This scenario is pending review.
                {canReviewScenario
                  ? ' You can approve or reject it.'
                  : ' Only admins or QA leads can approve/reject scenarios.'}
              </p>
              {canReviewScenario ? (
                <div className="flex gap-3">
                  <button
                    onClick={() => setShowReviewModal('approve')}
                    className="flex items-center gap-2 px-4 py-2.5 bg-[var(--color-status-success)] text-white rounded-lg hover:opacity-90 transition-all"
                  >
                    <CheckCircle className="w-4 h-4" />
                    Approve
                  </button>
                  <button
                    onClick={() => setShowReviewModal('reject')}
                    className="flex items-center gap-2 px-4 py-2.5 bg-[var(--color-status-danger)] text-white rounded-lg hover:opacity-90 transition-all"
                  >
                    <XCircle className="w-4 h-4" />
                    Reject
                  </button>
                </div>
              ) : (
                <p className="text-sm text-[var(--color-status-warning)] bg-[var(--color-status-warning-bg)] border border-[var(--color-status-warning-bg)] rounded-lg p-3">
                  {!APPROVAL_ROLES.includes(currentUser?.role?.toLowerCase() || '')
                    ? 'You need Org Admin or QA Lead role to review scenarios.'
                    : 'You cannot review your own scenario. Another reviewer must approve it.'}
                </p>
              )}
            </div>
          )}

          {/* Rejected Status */}
          {scenario.approval_status === 'rejected' && (
            <div className="space-y-4">
              <div className="bg-[var(--color-status-danger-bg)] border border-[var(--color-status-danger-bg)] rounded-lg p-4">
                <p className="text-[var(--color-status-danger)] font-medium mb-2">This scenario was rejected</p>
                {scenario.review_notes && (
                  <p className="text-[var(--color-status-danger)] text-sm">{scenario.review_notes}</p>
                )}
              </div>
              <button
                onClick={handleSubmitForReview}
                disabled={actionLoading}
                className="flex items-center gap-2 px-4 py-2.5 text-white rounded-lg transition-all disabled:opacity-50 hover:shadow-lg hover:-translate-y-0.5"
                style={{ background: 'linear-gradient(135deg, #2A6B6E 0%, #11484D 100%)' }}
              >
                <Send className="w-4 h-4" />
                {actionLoading ? 'Resubmitting...' : 'Resubmit for Review'}
              </button>
            </div>
          )}

          {/* Reviewer Information */}
          {scenario.reviewed_by && scenario.reviewed_at && (
            <div className="mt-4 pt-4 border-t border-[var(--color-border-default)]">
              <div className="flex items-center gap-2 text-sm text-[var(--color-content-secondary)]">
                <User className="w-4 h-4" />
                <span>
                  Reviewed by {scenario.reviewed_by} on{' '}
                  {new Date(scenario.reviewed_at).toLocaleDateString()}
                </span>
              </div>
              {scenario.review_notes && (
                <div className="mt-2 p-3 bg-[var(--color-surface-inset)] rounded-lg">
                  <p className="text-sm text-[var(--color-content-secondary)]">{scenario.review_notes}</p>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Scenario Details */}
      <div className="bg-[var(--color-surface-raised)] rounded-xl shadow-md p-6 mb-6">
        <h2 className="text-xl font-semibold text-[var(--color-content-primary)] mb-4">Scenario Details</h2>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-[var(--color-content-muted)]">Category</p>
            <p className="font-medium text-[var(--color-content-primary)]">
              {scenario.script_metadata?.category || 'N/A'}
            </p>
          </div>
          <div>
            <p className="text-sm text-[var(--color-content-muted)]">Steps</p>
            <p className="font-medium text-[var(--color-content-primary)]">{scenario.steps?.length || 0}</p>
          </div>
          <div>
            <p className="text-sm text-[var(--color-content-muted)]">Active</p>
            <p className="font-medium text-[var(--color-content-primary)]">{scenario.is_active ? 'Yes' : 'No'}</p>
          </div>
          <div>
            <p className="text-sm text-[var(--color-content-muted)]">Created</p>
            <p className="font-medium text-[var(--color-content-primary)]">
              {new Date(scenario.created_at).toLocaleDateString()}
            </p>
          </div>
        </div>

        {/* Tags */}
        {scenario.script_metadata?.tags && scenario.script_metadata.tags.length > 0 && (
          <div className="mt-4">
            <p className="text-sm text-[var(--color-content-muted)] mb-2">Tags</p>
            <div className="flex flex-wrap gap-2">
              {scenario.script_metadata.tags.map((tag: string) => (
                <span
                  key={tag}
                  className="px-3 py-1 bg-[var(--color-status-info-bg)] text-[var(--color-status-info)] rounded-full text-sm"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Steps */}
      <div className="bg-[var(--color-surface-raised)] rounded-xl shadow-md p-6">
        <h2 className="text-xl font-semibold text-[var(--color-content-primary)] mb-4">Steps</h2>
        {scenario.steps && scenario.steps.length > 0 ? (
          <div className="space-y-4">
            {scenario.steps.map((step: any, index: number) => (
              <div key={step.id || index} className="border border-[var(--color-border-default)] rounded-lg p-4">
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center font-semibold text-white" style={{ background: 'linear-gradient(135deg, #2A6B6E 0%, #11484D 100%)' }}>
                    {step.step_order}
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-[var(--color-content-primary)] mb-1">
                      User: "{step.user_utterance}"
                    </p>
                    {step.expected_outcomes && step.expected_outcomes.length > 0 ? (
                      <div className="text-sm text-[var(--color-content-secondary)]">
                        <span className="text-[var(--color-status-success)]">{step.expected_outcomes.length} expected outcome(s)</span> configured
                        {step.expected_outcomes[0]?.expected_command_kind && (
                          <span className="ml-2 text-xs bg-[var(--color-status-info-bg)] text-[var(--color-status-info)] px-2 py-0.5 rounded">
                            {step.expected_outcomes[0].expected_command_kind}
                          </span>
                        )}
                      </div>
                    ) : (
                      <p className="text-sm text-[var(--color-status-warning)]">No validation configured (auto-pass)</p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-[var(--color-content-muted)]">No steps configured</p>
        )}
      </div>

      {/* Review Modal */}
      {showReviewModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 max-w-md w-full mx-4 shadow-xl">
            <h3 className="text-lg font-semibold text-[var(--color-content-primary)] mb-4">
              {showReviewModal === 'approve' ? 'Approve Scenario' : 'Reject Scenario'}
            </h3>
            <div className="mb-4">
              <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-2">
                Review Notes {showReviewModal === 'reject' && <span className="text-[var(--color-status-danger)]">*</span>}
              </label>
              <textarea
                value={reviewNotes}
                onChange={(e) => setReviewNotes(e.target.value)}
                rows={4}
                className="w-full px-3 py-2 bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] border border-[var(--color-border-default)] rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/10"
                placeholder={
                  showReviewModal === 'approve'
                    ? 'Optional notes about the approval...'
                    : 'Required: Explain why this scenario is being rejected...'
                }
              />
            </div>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => {
                  setShowReviewModal(null);
                  setReviewNotes('');
                }}
                disabled={actionLoading}
                className="px-4 py-2.5 border border-[var(--color-border-strong)] text-[var(--color-content-secondary)] rounded-lg hover:bg-[var(--color-interactive-hover)] transition-all"
              >
                Cancel
              </button>
              <button
                onClick={showReviewModal === 'approve' ? handleApprove : handleReject}
                disabled={actionLoading}
                className={`px-4 py-2.5 text-white rounded-lg transition-all disabled:opacity-50 ${
                  showReviewModal === 'approve'
                    ? 'bg-[var(--color-status-success)] hover:opacity-90'
                    : 'bg-[var(--color-status-danger)] hover:opacity-90'
                }`}
              >
                {actionLoading
                  ? 'Processing...'
                  : showReviewModal === 'approve'
                  ? 'Approve'
                  : 'Reject'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Baseline Approval Modal */}
      {showBaselineModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 max-w-md w-full mx-4 shadow-xl">
            <h3 className="text-lg font-semibold text-[var(--color-content-primary)] mb-4">
              Approve Regression Baseline
            </h3>
            <div className="mb-4">
              <div className="bg-[var(--color-status-info-bg)] border border-[var(--color-status-info-bg)] rounded-lg p-3 mb-4">
                <p className="text-sm text-[var(--color-status-info)]">
                  This will set the current test execution as the new baseline for regression detection.
                  Future executions will be compared against this baseline to identify regressions.
                </p>
              </div>
              <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-2">
                Approval Notes (Optional)
              </label>
              <textarea
                value={baselineNote}
                onChange={(e) => setBaselineNote(e.target.value)}
                rows={3}
                className="w-full px-3 py-2 bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] border border-[var(--color-border-default)] rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/10"
                placeholder="Optional notes about this baseline approval..."
              />
            </div>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => {
                  setShowBaselineModal(false);
                  setBaselineNote('');
                }}
                disabled={actionLoading}
                className="px-4 py-2.5 border border-[var(--color-border-strong)] text-[var(--color-content-secondary)] rounded-lg hover:bg-[var(--color-interactive-hover)] transition-all"
              >
                Cancel
              </button>
              <button
                onClick={handleApproveBaseline}
                disabled={actionLoading}
                className="px-4 py-2.5 bg-[var(--color-status-info)] text-white rounded-lg hover:opacity-90 transition-all disabled:opacity-50"
              >
                {actionLoading ? 'Approving...' : 'Approve Baseline'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal for alerts */}
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

export default ScenarioDetail;

