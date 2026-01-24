import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  RefreshCw,
  Edit,
  Play,
  CheckCircle,
  XCircle,
  Loader2,
  AlertTriangle,
  Calendar,
  User,
  FileText,
  Tag,
  ExternalLink,
  MessageSquare,
  TrendingUp,
  Clock,
  Sparkles,
} from 'lucide-react';

import { getEdgeCase, rerunEdgeCaseScenario, updateEdgeCase, type RerunResult } from '../../services/edgeCase.service';
import type { EdgeCase } from '../../types/edgeCase';

const getSeverityConfig = (severity: string) => {
  switch (severity.toLowerCase()) {
    case 'critical':
      return {
        bg: 'bg-[var(--color-status-danger-bg)]',
        text: 'text-[var(--color-status-danger)]',
        border: 'border-[var(--color-status-danger)]',
        icon: 'text-[var(--color-status-danger)]',
        label: 'Critical',
      };
    case 'high':
      return {
        bg: 'bg-[var(--color-status-amber-bg)]',
        text: 'text-[var(--color-status-amber)]',
        border: 'border-[var(--color-status-amber-bg)]',
        icon: 'text-[var(--color-status-amber)]',
        label: 'High',
      };
    case 'medium':
      return {
        bg: 'bg-[var(--color-status-warning-bg)]',
        text: 'text-[var(--color-status-warning)]',
        border: 'border-[var(--color-status-warning)]',
        icon: 'text-[var(--color-status-warning)]',
        label: 'Medium',
      };
    case 'low':
      return {
        bg: 'bg-[var(--color-status-success-bg)]',
        text: 'text-[var(--color-status-success)]',
        border: 'border-[var(--color-status-success)]',
        icon: 'text-[var(--color-status-success)]',
        label: 'Low',
      };
    default:
      return {
        bg: 'bg-[var(--color-surface-inset)]',
        text: 'text-[var(--color-content-secondary)]',
        border: 'border-[var(--color-border-default)]',
        icon: 'text-[var(--color-content-secondary)]',
        label: severity || 'Unknown',
      };
  }
};

const getStatusConfig = (status: string) => {
  switch (status.toLowerCase()) {
    case 'resolved':
      return {
        bg: 'bg-[var(--color-status-success-bg)]',
        text: 'text-[var(--color-status-success)]',
        icon: CheckCircle,
        label: 'Resolved',
      };
    case 'active':
    case 'new':
      return {
        bg: 'bg-[var(--color-status-info-bg)]',
        text: 'text-[var(--color-status-info)]',
        icon: AlertTriangle,
        label: status === 'new' ? 'New' : 'Active',
      };
    case 'wont_fix':
      return {
        bg: 'bg-[var(--color-surface-inset)]',
        text: 'text-[var(--color-content-secondary)]',
        icon: XCircle,
        label: "Won't Fix",
      };
    default:
      return {
        bg: 'bg-[var(--color-surface-inset)]',
        text: 'text-[var(--color-content-secondary)]',
        icon: AlertTriangle,
        label: 'Unknown',
      };
  }
};

const formatDate = (dateString: string | undefined) => {
  if (!dateString) return 'Unknown';
  try {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return 'Invalid date';
  }
};

const EdgeCaseDetail: React.FC = () => {
  const { edgeCaseId } = useParams<{ edgeCaseId: string }>();
  const navigate = useNavigate();

  const [edgeCase, setEdgeCase] = useState<EdgeCase | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Re-run state
  const [rerunning, setRerunning] = useState(false);
  const [rerunResult, setRerunResult] = useState<RerunResult | null>(null);
  const [rerunError, setRerunError] = useState<string | null>(null);

  // Status update state
  const [updatingStatus, setUpdatingStatus] = useState(false);

  useEffect(() => {
    let cancelled = false;

    const loadEdgeCase = async () => {
      if (!edgeCaseId) {
        setError('Edge case identifier is missing from the URL.');
        setLoading(false);
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const record = await getEdgeCase(edgeCaseId);
        if (!cancelled) {
          setEdgeCase(record);
        }
      } catch (err: unknown) {
        if (!cancelled) {
          const message = err instanceof Error ? err.message : 'Failed to load edge case';
          setError(message);
          setEdgeCase(null);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    loadEdgeCase();

    return () => {
      cancelled = true;
    };
  }, [edgeCaseId]);

  const handleBack = () => {
    navigate('/edge-cases');
  };

  const handleRefresh = () => {
    if (edgeCaseId) {
      setLoading(true);
      setError(null);
      setRerunResult(null);
      setRerunError(null);
      getEdgeCase(edgeCaseId)
        .then((record) => {
          setEdgeCase(record);
        })
        .catch((err) => setError(err instanceof Error ? err.message : 'Failed to load edge case'))
        .finally(() => setLoading(false));
    }
  };

  const handleRerunScenario = async () => {
    if (!edgeCaseId) return;

    setRerunning(true);
    setRerunResult(null);
    setRerunError(null);

    try {
      const result = await rerunEdgeCaseScenario(edgeCaseId);
      setRerunResult(result);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to re-run scenario';
      setRerunError(message);
    } finally {
      setRerunning(false);
    }
  };

  const handleMarkAsResolved = async () => {
    if (!edgeCaseId) return;

    setUpdatingStatus(true);
    try {
      const updated = await updateEdgeCase(edgeCaseId, { status: 'resolved' });
      setEdgeCase(updated);
      setRerunResult(null);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to update status';
      setError(message);
    } finally {
      setUpdatingStatus(false);
    }
  };

  const handleMarkAsActive = async () => {
    if (!edgeCaseId) return;

    setUpdatingStatus(true);
    try {
      const updated = await updateEdgeCase(edgeCaseId, { status: 'active' });
      setEdgeCase(updated);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to update status';
      setError(message);
    } finally {
      setUpdatingStatus(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-sm border border-[var(--color-border-default)]">
        <div className="flex flex-col items-center justify-center p-20">
          <div
            className="w-12 h-12 border-4 border-[var(--color-border-default)] rounded-full animate-spin mb-4"
            style={{ borderTopColor: '#2A6B6E' }}
          />
          <div className="text-lg font-semibold text-[var(--color-content-primary)] mb-2">Loading Edge Case...</div>
        </div>
      </div>
    );
  }

  if (error || !edgeCase) {
    return (
      <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-sm border border-[var(--color-border-default)]">
        <div className="flex items-center gap-4 p-6 bg-[var(--color-status-danger-bg)] rounded-lg border border-[var(--color-status-danger)]">
          <XCircle className="w-12 h-12 text-[var(--color-status-danger)] flex-shrink-0" />
          <div className="flex-1">
            <div className="text-lg font-semibold text-[var(--color-status-danger)]">Unable to load edge case</div>
            <div className="text-sm text-[var(--color-status-danger)] mt-1">{error ?? 'Edge case not found.'}</div>
          </div>
          <button
            onClick={handleBack}
            className="px-4 py-2 rounded-lg text-sm font-medium bg-[var(--color-status-danger-bg)] text-[var(--color-status-danger)] hover:bg-[var(--color-status-danger-bg)]"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  const { title, description, tags, severity, status, scenarioDefinition, category, createdAt, discoveredDate, autoCreated } = edgeCase;
  const isResolved = status?.toLowerCase() === 'resolved';
  const statusConfig = getStatusConfig(status ?? 'unknown');
  const severityConfig = getSeverityConfig(severity ?? '');
  const StatusIcon = statusConfig.icon;

  const scenarioSteps =
    Array.isArray(scenarioDefinition?.steps) && scenarioDefinition.steps.length > 0 ? scenarioDefinition.steps : null;

  return (
    <div className="space-y-6">
      {/* Header with Back Button */}
      <div className="flex items-center gap-4">
        <button
          onClick={handleBack}
          className="p-2.5 hover:bg-[var(--color-interactive-hover)] rounded-lg transition-colors text-[var(--color-content-secondary)] hover:text-[var(--color-content-primary)]"
          aria-label="Back to edge cases"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-[var(--color-content-primary)] flex items-center gap-3">
            <AlertTriangle className="w-6 h-6" style={{ color: '#2A6B6E' }} />
            {title}
          </h1>
          <p className="text-sm text-[var(--color-content-muted)] mt-1">
            {autoCreated ? 'Auto-detected edge case' : 'Manually created edge case'}
          </p>
        </div>
      </div>

      {/* Status & Severity Banner */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Status Card */}
        <div className={`${statusConfig.bg} rounded-xl p-5 border ${statusConfig.text}`}>
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-[var(--color-surface-raised)]/50 flex items-center justify-center">
              <StatusIcon className="w-6 h-6" />
            </div>
            <div className="flex-1">
              <div className="text-xs font-medium opacity-75 uppercase tracking-wide">Status</div>
              <div className="text-xl font-bold">{statusConfig.label}</div>
            </div>
          </div>
        </div>

        {/* Severity Card */}
        <div className={`${severityConfig.bg} rounded-xl p-5 border ${severityConfig.border}`}>
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-[var(--color-surface-raised)]/50 flex items-center justify-center">
              <AlertTriangle className={`w-6 h-6 ${severityConfig.icon}`} />
            </div>
            <div className="flex-1">
              <div className={`text-xs font-medium opacity-75 uppercase tracking-wide ${severityConfig.text}`}>
                Severity
              </div>
              <div className={`text-xl font-bold ${severityConfig.text}`}>{severityConfig.label}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="bg-[var(--color-surface-raised)] rounded-xl p-4 shadow-sm border border-[var(--color-border-default)]">
        <div className="flex flex-wrap gap-3">
          <button
            className="px-4 py-2.5 rounded-lg text-sm font-semibold transition-all inline-flex items-center gap-2 bg-[var(--color-surface-inset)] text-[var(--color-content-secondary)] border border-[var(--color-border-default)] hover:bg-[var(--color-interactive-active)]"
            onClick={handleRefresh}
          >
            <RefreshCw size={16} /> Refresh
          </button>

          {edgeCase.scriptId && (
            <button
              className="px-4 py-2.5 rounded-lg text-sm font-semibold transition-all inline-flex items-center gap-2 bg-[var(--color-status-purple)] hover:opacity-90 text-white disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
              onClick={handleRerunScenario}
              disabled={rerunning}
            >
              {rerunning ? (
                <>
                  <Loader2 size={16} className="animate-spin" /> Running Test...
                </>
              ) : (
                <>
                  <Play size={16} /> Re-run Test
                </>
              )}
            </button>
          )}

          {isResolved ? (
            <button
              className="px-4 py-2.5 rounded-lg text-sm font-semibold transition-all inline-flex items-center gap-2 bg-[var(--color-status-warning)] hover:opacity-90 text-white disabled:opacity-50 shadow-sm"
              onClick={handleMarkAsActive}
              disabled={updatingStatus}
            >
              <TrendingUp size={16} /> Reopen
            </button>
          ) : (
            <button
              className="px-4 py-2.5 rounded-lg text-sm font-semibold transition-all inline-flex items-center gap-2 bg-[var(--color-status-success)] hover:opacity-90 text-white disabled:opacity-50 shadow-sm"
              onClick={handleMarkAsResolved}
              disabled={updatingStatus}
            >
              <CheckCircle size={16} /> Mark Resolved
            </button>
          )}

          <button
            className="px-4 py-2.5 rounded-lg text-sm font-semibold transition-all inline-flex items-center gap-2 text-white hover:shadow-lg hover:-translate-y-0.5 ml-auto shadow-sm"
            style={{ background: 'linear-gradient(135deg, #2A6B6E 0%, #11484D 100%)' }}
            onClick={() => navigate(`/edge-cases/${edgeCaseId}/edit`)}
          >
            <Edit size={16} /> Edit Details
          </button>
        </div>
      </div>

      {/* Re-run Result Banner */}
      {rerunResult && (
        <div
          className={`rounded-xl p-5 border ${
            rerunResult.passed
              ? 'bg-[var(--color-status-success-bg)] border-[var(--color-status-success)]'
              : 'bg-[var(--color-status-danger-bg)] border-[var(--color-status-danger)]'
          }`}
        >
          <div className="flex items-start gap-4">
            <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
              rerunResult.passed ? 'bg-[var(--color-status-success-bg)]' : 'bg-[var(--color-status-danger-bg)]'
            }`}>
              {rerunResult.passed ? (
                <CheckCircle className="w-6 h-6 text-[var(--color-status-success)]" />
              ) : (
                <XCircle className="w-6 h-6 text-[var(--color-status-danger)]" />
              )}
            </div>
            <div className="flex-1">
              <div className={`font-semibold text-lg ${
                rerunResult.passed ? 'text-[var(--color-status-success)]' : 'text-[var(--color-status-danger)]'
              }`}>
                {rerunResult.message}
              </div>
              <div className={`text-sm mt-2 ${
                rerunResult.passed ? 'text-[var(--color-status-success)]' : 'text-[var(--color-status-danger)]'
              }`}>
                <div className="flex items-center gap-4 flex-wrap">
                  <span><strong>Scenario:</strong> {rerunResult.scriptName}</span>
                  <span><strong>Result:</strong> {rerunResult.result}</span>
                  <span><strong>Status:</strong> {rerunResult.status}</span>
                </div>
              </div>
            </div>
            {rerunResult.passed && !isResolved && (
              <button
                className="px-4 py-2 rounded-lg text-sm font-semibold bg-[var(--color-status-success)] hover:opacity-90 text-white shadow-sm"
                onClick={handleMarkAsResolved}
                disabled={updatingStatus}
              >
                Mark as Resolved
              </button>
            )}
          </div>
        </div>
      )}

      {/* Re-run Error Banner */}
      {rerunError && (
        <div className="rounded-xl p-5 border bg-[var(--color-status-danger-bg)] border-[var(--color-status-danger)]">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-xl bg-[var(--color-status-danger-bg)] flex items-center justify-center">
              <XCircle className="w-6 h-6 text-[var(--color-status-danger)]" />
            </div>
            <div className="flex-1">
              <div className="font-semibold text-lg text-[var(--color-status-danger)]">Test execution failed</div>
              <div className="text-sm text-[var(--color-status-danger)] mt-1">{rerunError}</div>
            </div>
          </div>
        </div>
      )}

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Description Card */}
          <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-sm border border-[var(--color-border-default)]">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-[#2A6B6E] to-[#11484D] flex items-center justify-center">
                <FileText className="w-5 h-5 text-white" />
              </div>
              <h2 className="text-lg font-semibold text-[var(--color-content-primary)]">Description</h2>
            </div>
            {description ? (
              <p className="text-[var(--color-content-secondary)] leading-relaxed">{description}</p>
            ) : (
              <p className="text-[var(--color-content-muted)] italic">No description provided.</p>
            )}
          </div>

          {/* Scenario Steps Card */}
          <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-sm border border-[var(--color-border-default)]">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-purple-500 to-purple-700 flex items-center justify-center">
                <MessageSquare className="w-5 h-5 text-white" />
              </div>
              <h2 className="text-lg font-semibold text-[var(--color-content-primary)]">Scenario Steps</h2>
            </div>
            {scenarioSteps ? (
              <div className="space-y-3">
                {scenarioSteps.map((step: string, index: number) => (
                  <div
                    key={`${index}-${step}`}
                    className="flex gap-3 p-3 bg-[var(--color-surface-inset)]/50 rounded-lg border border-[var(--color-border-default)]"
                  >
                    <div className="w-7 h-7 rounded-full bg-gradient-to-br from-[#2A6B6E] to-[#11484D] flex items-center justify-center flex-shrink-0 text-white text-sm font-semibold">
                      {index + 1}
                    </div>
                    <p className="text-[var(--color-content-secondary)] flex-1 pt-0.5">{step}</p>
                  </div>
                ))}
              </div>
            ) : scenarioDefinition && Object.keys(scenarioDefinition).length > 0 ? (
              <div className="bg-[var(--color-surface-inset)]/50 p-4 rounded-lg border border-[var(--color-border-default)]">
                <p className="text-sm text-[var(--color-content-secondary)] mb-2">Scenario data available (raw format):</p>
                <div className="max-h-64 overflow-auto">
                  <pre className="text-xs text-[var(--color-content-secondary)] font-mono">
                    {JSON.stringify(scenarioDefinition, null, 2)}
                  </pre>
                </div>
              </div>
            ) : (
              <p className="text-[var(--color-content-muted)] italic">No scenario steps defined.</p>
            )}
          </div>

          {/* Related Scenario Card */}
          {edgeCase.scriptId && (
            <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-sm border border-[var(--color-border-default)]">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center">
                  <ExternalLink className="w-5 h-5 text-white" />
                </div>
                <h2 className="text-lg font-semibold text-[var(--color-content-primary)]">Related Test Scenario</h2>
              </div>
              <div className="flex items-center justify-between p-4 bg-gradient-to-r from-[var(--color-status-info-bg)] to-[var(--color-status-purple-bg)] rounded-lg border border-[var(--color-status-info)]">
                <div className="flex items-center gap-3">
                  <Sparkles className="w-5 h-5 text-[var(--color-status-info)]" />
                  <div>
                    <p className="text-sm font-medium text-[var(--color-content-primary)]">
                      Test scenario linked to this edge case
                    </p>
                    <p className="text-xs text-[var(--color-content-secondary)] mt-0.5">
                      Re-run to verify if the issue still occurs
                    </p>
                  </div>
                </div>
                <button
                  className="px-4 py-2 rounded-lg text-sm font-semibold bg-[var(--color-status-info)] hover:opacity-90 text-white shadow-sm flex items-center gap-2"
                  onClick={() => navigate(`/scenarios/${edgeCase.scriptId}`)}
                >
                  View Scenario <ExternalLink size={14} />
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Right Column - Metadata & Tags */}
        <div className="space-y-6">
          {/* Category & Tags Card */}
          <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-sm border border-[var(--color-border-default)]">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-amber-500 to-amber-700 flex items-center justify-center">
                <Tag className="w-5 h-5 text-white" />
              </div>
              <h2 className="text-lg font-semibold text-[var(--color-content-primary)]">Classification</h2>
            </div>

            {/* Category */}
            {category && (
              <div className="mb-4">
                <div className="text-xs font-medium text-[var(--color-content-muted)] uppercase tracking-wide mb-2">
                  Category
                </div>
                <div className="inline-flex items-center gap-2 px-3 py-2 rounded-lg bg-[var(--color-status-info-bg)] border border-[var(--color-status-info)]">
                  <div className="w-2 h-2 rounded-full bg-[var(--color-status-info)]" />
                  <span className="text-sm font-medium text-[var(--color-status-info)] capitalize">{category}</span>
                </div>
              </div>
            )}

            {/* Tags */}
            {tags && tags.length > 0 && (
              <div>
                <div className="text-xs font-medium text-[var(--color-content-muted)] uppercase tracking-wide mb-2">
                  Tags
                </div>
                <div className="flex flex-wrap gap-2">
                  {tags.map((tag) => (
                    <span
                      key={tag}
                      className="px-3 py-1.5 bg-[var(--color-surface-inset)] rounded-lg text-xs font-medium text-[var(--color-content-secondary)] border border-[var(--color-border-default)]"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {!category && (!tags || tags.length === 0) && (
              <p className="text-sm text-[var(--color-content-muted)] italic">No classification data available.</p>
            )}
          </div>

          {/* Metadata Card */}
          <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-sm border border-[var(--color-border-default)]">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-lg bg-[var(--color-content-muted)] flex items-center justify-center">
                <Clock className="w-5 h-5 text-[var(--color-content-inverse)]" />
              </div>
              <h2 className="text-lg font-semibold text-[var(--color-content-primary)]">Metadata</h2>
            </div>

            <div className="space-y-3">
              {/* Created Date */}
              <div className="flex items-center gap-3 p-3 bg-[var(--color-surface-inset)]/50 rounded-lg">
                <Calendar className="w-5 h-5 text-[var(--color-content-muted)] flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <div className="text-xs text-[var(--color-content-muted)]">Created</div>
                  <div className="text-sm font-medium text-[var(--color-content-primary)] truncate">
                    {formatDate(createdAt)}
                  </div>
                </div>
              </div>

              {/* Discovered Date */}
              {discoveredDate && (
                <div className="flex items-center gap-3 p-3 bg-[var(--color-surface-inset)]/50 rounded-lg">
                  <AlertTriangle className="w-5 h-5 text-[var(--color-content-muted)] flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <div className="text-xs text-[var(--color-content-muted)]">Discovered</div>
                    <div className="text-sm font-medium text-[var(--color-content-primary)] truncate">
                      {formatDate(discoveredDate)}
                    </div>
                  </div>
                </div>
              )}

              {/* Auto-created badge */}
              <div className="flex items-center gap-3 p-3 bg-[var(--color-surface-inset)]/50 rounded-lg">
                <User className="w-5 h-5 text-[var(--color-content-muted)] flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <div className="text-xs text-[var(--color-content-muted)]">Source</div>
                  <div className="text-sm font-medium text-[var(--color-content-primary)]">
                    {autoCreated ? 'Auto-detected' : 'Manual entry'}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EdgeCaseDetail;
