/**
 * DefectDetail Page
 *
 * Displays comprehensive information for a specific defect, including metadata,
 * related executions, and review comments.
 */

import React, { useEffect, useState } from 'react';
import { ArrowLeft, RefreshCw, ExternalLink, Plus } from 'lucide-react';
import { useParams, useNavigate } from 'react-router-dom';

import { getDefectDetail, createJiraTicket } from '../../services/defect.service';
import type { DefectDetail as DefectDetailType } from '../../types/defect';

const resolveSeverityColor = (severity: string) => {
  switch (severity.toLowerCase()) {
    case 'critical':
    case 'high':
      return 'bg-[var(--color-status-danger-bg)] text-[var(--color-status-danger)]';
    case 'medium':
      return 'bg-[var(--color-status-warning-bg)] text-[var(--color-status-warning)]';
    case 'low':
      return 'bg-[var(--color-status-success-bg)] text-[var(--color-status-success)]';
    default:
      return 'bg-[var(--color-interactive-hover)] text-[var(--color-content-secondary)]';
  }
};

const formatDateTime = (value: string | null | undefined) => {
  if (!value) {
    return '—';
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return '—';
  }
  return date.toLocaleString();
};

const DefectDetail: React.FC = () => {
  const { id: defectId } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [defect, setDefect] = useState<DefectDetailType | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [jiraLoading, setJiraLoading] = useState(false);
  const [jiraError, setJiraError] = useState<string | null>(null);

  useEffect(() => {
    if (!defectId) {
      setError('Missing defect identifier.');
      return;
    }

    let cancelled = false;

    const fetchDetail = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await getDefectDetail(defectId);
        if (!cancelled) {
          setDefect(response);
        }
      } catch (err: unknown) {
        if (!cancelled) {
          setError(err?.message ?? 'Failed to load defect details.');
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    fetchDetail();

    return () => {
      cancelled = true;
    };
  }, [defectId]);

  const renderExecutions = (executions: DefectDetailType['relatedExecutions']) => {
    if (!executions.length) {
      return <p className="text-[var(--color-content-muted)]">No related executions recorded.</p>;
    }

    return (
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b-2 border-[var(--color-border-default)] bg-[var(--color-surface-inset)]">
              <th className="p-4 text-left text-xs font-semibold text-[var(--color-content-muted)] uppercase tracking-wide">
                Execution ID
              </th>
              <th className="p-4 text-left text-xs font-semibold text-[var(--color-content-muted)] uppercase tracking-wide">
                Status
              </th>
              <th className="p-4 text-left text-xs font-semibold text-[var(--color-content-muted)] uppercase tracking-wide">
                Test Run
              </th>
              <th className="p-4 text-left text-xs font-semibold text-[var(--color-content-muted)] uppercase tracking-wide">
                Executed
              </th>
            </tr>
          </thead>
          <tbody>
            {executions.map((execution) => (
              <tr
                key={execution.id}
                className="border-b border-[var(--color-border-default)] hover:bg-[var(--color-interactive-hover)] transition-colors"
              >
                <td className="p-4 text-sm font-semibold text-[var(--color-content-primary)]">
                  {execution.id}
                </td>
                <td className="p-4 text-sm text-[var(--color-content-secondary)] capitalize">
                  {execution.status}
                </td>
                <td className="p-4 text-sm text-[var(--color-content-secondary)]">
                  {execution.suiteRunId ?? '—'}
                </td>
                <td className="p-4 text-sm text-[var(--color-content-secondary)]">
                  {formatDateTime(execution.executedAt)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  const renderComments = (comments: DefectDetailType['comments']) => {
    if (!comments.length) {
      return <p className="text-[var(--color-content-muted)]">No reviewer comments yet.</p>;
    }

    return (
      <div className="flex flex-col gap-4">
        {comments.map((comment) => (
          <div key={comment.id}>
            <div className="pb-4">
              <p className="font-semibold text-[var(--color-content-primary)]">{comment.author}</p>
              <p className="text-sm text-[var(--color-content-muted)] mb-2">
                {formatDateTime(comment.createdAt)}
              </p>
              <p className="text-sm text-[var(--color-content-secondary)]">
                {comment.message}
              </p>
            </div>
            <div className="border-t border-[var(--color-border-default)]"></div>
          </div>
        ))}
      </div>
    );
  };

  const handleBack = () => {
    navigate('/defects');
  };

  const handleRefresh = () => {
    if (defectId) {
      setLoading(true);
      setError(null);
      getDefectDetail(defectId)
        .then((response) => setDefect(response))
        .catch((err) => setError(err?.message ?? 'Failed to load defect details.'))
        .finally(() => setLoading(false));
    }
  };

  const handleCreateJiraTicket = async () => {
    if (!defectId) return;

    setJiraLoading(true);
    setJiraError(null);

    try {
      const updatedDefect = await createJiraTicket(defectId);
      // Update the defect state with Jira fields
      setDefect((prev) =>
        prev
          ? {
              ...prev,
              jiraIssueKey: updatedDefect.jiraIssueKey,
              jiraIssueUrl: updatedDefect.jiraIssueUrl,
              jiraStatus: updatedDefect.jiraStatus,
            }
          : prev
      );
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to create Jira ticket';
      setJiraError(message);
    } finally {
      setJiraLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-sm">
        <div className="flex flex-col items-center justify-center p-20">
          <div className="w-12 h-12 border-4 border-[var(--color-border-default)] rounded-full animate-spin mb-4" style={{ borderTopColor: '#2A6B6E' }}></div>
          <div className="text-lg font-semibold text-[var(--color-content-primary)] mb-2">Loading Defect Details...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 rounded-lg mb-5 flex items-center gap-3 bg-danger-light  text-[var(--color-status-danger)] border-l-4 border-danger ">
        <div className="text-xl">⚠️</div>
        <div className="flex-1">
          <div className="font-semibold">Failed to load defect details: {error}</div>
        </div>
      </div>
    );
  }

  if (!defect) {
    return null;
  }

  return (
    <>
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-4 mb-6">
          <button
            onClick={handleBack}
            className="p-2 hover:bg-[var(--color-interactive-hover)] rounded-lg transition-colors"
            aria-label="Back to defects"
          >
            <ArrowLeft className="h-5 w-5 text-[var(--color-content-primary)]" />
          </button>
          <h1 className="text-4xl font-bold text-[var(--color-content-primary)]">{defect.title}</h1>
        </div>
        <div className="flex gap-3 flex-wrap">
          <span
            className={`px-2.5 py-1 rounded-md text-xs font-semibold ${resolveSeverityColor(defect.severity)} capitalize`}
            data-testid="defect-detail-severity"
          >
            {defect.severity}
          </span>
          <span className="px-2.5 py-1 rounded-md text-xs font-semibold bg-[var(--color-interactive-hover)] text-[var(--color-content-secondary)] capitalize">
            {defect.status}
          </span>
          <button
            className="px-4 py-2.5 rounded-lg text-sm font-semibold transition-all inline-flex items-center gap-2 bg-[var(--color-surface-inset)] text-[var(--color-content-secondary)] border border-[var(--color-border-default)] hover:bg-[var(--color-interactive-active)]"
            onClick={handleRefresh}
          >
            <RefreshCw size={14} /> Refresh
          </button>
        </div>
      </div>

      {/* Defect Details */}
      <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-sm mb-6">
        <div className="flex flex-col gap-2">
          <p className="text-sm text-[var(--color-content-secondary)]">
            Category: <strong className="text-[var(--color-content-primary)]">{defect.category}</strong>
          </p>
          <p className="text-sm text-[var(--color-content-secondary)]">
            Script: <strong className="text-[var(--color-content-primary)]">{defect.scriptId ?? '—'}</strong>
          </p>
          <p className="text-sm text-[var(--color-content-secondary)]">
            Language: <strong className="text-[var(--color-content-primary)]">{defect.languageCode ?? '—'}</strong>
          </p>
          <p className="text-sm text-[var(--color-content-secondary)]">
            Detected: <strong className="text-[var(--color-content-primary)]">{formatDateTime(defect.detectedAt)}</strong>
          </p>
          <p className="text-sm text-[var(--color-content-secondary)]">
            Assigned to: <strong className="text-[var(--color-content-primary)]">{defect.assignedTo ?? 'Unassigned'}</strong>
          </p>
        </div>

        {/* Jira Integration Section */}
        <div className="mt-6 pt-6 border-t border-[var(--color-border-default)]">
          <h3 className="text-base font-semibold mb-3 text-[var(--color-content-primary)]">Jira Integration</h3>

          {jiraError && (
            <div className="p-3 rounded-lg mb-3 flex items-center gap-2 bg-[var(--color-status-danger-bg)] text-[var(--color-status-danger)] text-sm">
              <span>Failed to create Jira ticket: {jiraError}</span>
            </div>
          )}

          {defect.jiraIssueKey && defect.jiraIssueUrl ? (
            <div className="flex items-center gap-3">
              <a
                href={defect.jiraIssueUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold bg-[#0052CC] text-white hover:bg-[#0747A6] transition-colors"
              >
                <ExternalLink size={16} />
                {defect.jiraIssueKey}
              </a>
              {defect.jiraStatus && (
                <span className="px-2.5 py-1 rounded-md text-xs font-semibold bg-[var(--color-interactive-hover)] text-[var(--color-content-secondary)]">
                  {defect.jiraStatus}
                </span>
              )}
            </div>
          ) : (
            <button
              onClick={handleCreateJiraTicket}
              disabled={jiraLoading}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold bg-[#0052CC] text-white hover:bg-[#0747A6] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {jiraLoading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 rounded-full animate-spin" style={{ borderTopColor: 'white' }}></div>
                  Creating...
                </>
              ) : (
                <>
                  <Plus size={16} />
                  Create Jira Ticket
                </>
              )}
            </button>
          )}
        </div>

        {defect.description && (
          <div className="mt-6">
            <h3 className="text-base font-semibold mb-2 text-[var(--color-content-primary)]">Description</h3>
            <p className="text-sm text-[var(--color-content-secondary)] whitespace-pre-line">
              {defect.description}
            </p>
          </div>
        )}
      </div>

      {/* Related Executions */}
      <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-sm mb-6">
        <h2 className="text-lg font-bold text-[var(--color-content-primary)] mb-4">Related Executions</h2>
        {renderExecutions(defect.relatedExecutions)}
      </div>

      {/* Reviewer Comments */}
      <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-sm">
        <h2 className="text-lg font-bold text-[var(--color-content-primary)] mb-4">Reviewer Comments</h2>
        {renderComments(defect.comments)}
      </div>
    </>
  );
};

export default DefectDetail;
