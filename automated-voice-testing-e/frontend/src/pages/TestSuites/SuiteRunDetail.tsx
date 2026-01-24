/**
 * Suite Run Detail Page
 *
 * Displays details of a specific suite run including:
 * - Suite/category information
 * - Overall run status and progress
 * - List of all scenario executions with their status
 * - Links to individual scenario execution details
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  CheckCircle,
  XCircle,
  Clock,
  PlayCircle,
  Layers,
  Tag,
  Eye,
  RefreshCw,
  AlertTriangle,
} from 'lucide-react';
import {
  getSuiteRunDetail,
  type SuiteRunDetail as SuiteRunDetailType,
  type SuiteRunScenarioExecution,
} from '../../services/testSuite.service';

const SuiteRunDetail: React.FC = () => {
  const { runId } = useParams<{ runId: string }>();
  const navigate = useNavigate();

  const [run, setRun] = useState<SuiteRunDetailType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadRunDetail = async () => {
    if (!runId) return;

    try {
      setLoading(true);
      setError(null);
      const data = await getSuiteRunDetail(runId);
      setRun(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load suite run details');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRunDetail();
  }, [runId]);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'completed':
        return { icon: CheckCircle, color: 'text-[var(--color-status-success)]', bg: 'bg-[var(--color-status-success-bg)]', label: 'Completed' };
      case 'failed':
        return { icon: XCircle, color: 'text-[var(--color-status-danger)]', bg: 'bg-[var(--color-status-danger-bg)]', label: 'Failed' };
      case 'in_progress':
        return { icon: PlayCircle, color: 'text-[var(--color-status-info)]', bg: 'bg-[var(--color-status-info-bg)]', label: 'In Progress' };
      case 'pending':
        return { icon: Clock, color: 'text-[var(--color-status-warning)]', bg: 'bg-[var(--color-status-warning-bg)]', label: 'Pending' };
      default:
        return { icon: Clock, color: 'text-[var(--color-content-secondary)]', bg: 'bg-[var(--color-surface-inset)]', label: status };
    }
  };

  const formatDate = (dateString: string | null | undefined) => {
    if (!dateString) return '—';
    return new Date(dateString).toLocaleString();
  };

  const formatDuration = (started: string | null | undefined, completed: string | null | undefined) => {
    if (!started) return '—';
    const end = completed ? new Date(completed) : new Date();
    const duration = end.getTime() - new Date(started).getTime();
    if (duration < 1000) return `${duration}ms`;
    if (duration < 60000) return `${(duration / 1000).toFixed(1)}s`;
    const minutes = Math.floor(duration / 60000);
    const seconds = Math.floor((duration % 60000) / 1000);
    return `${minutes}m ${seconds}s`;
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-sm border border-[var(--color-border-default)]">
          <div className="flex flex-col items-center justify-center p-20">
            <div className="w-12 h-12 border-4 border-[var(--color-border-default)] rounded-full animate-spin mb-4" style={{ borderTopColor: '#2A6B6E' }}></div>
            <div className="text-lg font-semibold text-[var(--color-content-primary)] mb-2">Loading Suite Run...</div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !run) {
    return (
      <div className="space-y-6">
        <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-sm border border-[var(--color-border-default)]">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center gap-2 text-[var(--color-content-secondary)] hover:text-[var(--color-content-primary)] mb-6 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            Back
          </button>
          <div className="flex flex-col items-center justify-center p-16">
            <AlertTriangle className="w-16 h-16 text-[var(--color-status-danger)] mb-4" />
            <div className="text-lg font-semibold text-[var(--color-content-primary)] mb-2">Error Loading Suite Run</div>
            <div className="text-[var(--color-content-muted)] mb-4">{error || 'Suite run not found'}</div>
            <button
              onClick={loadRunDetail}
              className="px-4 py-2 bg-[#2A6B6E] text-white rounded-lg hover:bg-[#4a9a9d] transition-colors"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  const statusBadge = getStatusBadge(run.status);
  const StatusIcon = statusBadge.icon;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-md border border-[var(--color-border-default)]">
        <button
          onClick={() => navigate(-1)}
          className="flex items-center gap-2 text-[var(--color-content-secondary)] hover:text-[var(--color-content-primary)] mb-4 transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
          Back
        </button>

        <div className="flex justify-between items-start">
          <div className="flex items-start gap-4">
            <div className={`p-3 rounded-xl ${run.is_categorical ? 'bg-[var(--color-brand-muted)]' : 'bg-[var(--color-surface-inset)]'}`}>
              {run.is_categorical ? (
                <Tag className="w-8 h-8 text-[#2A6B6E]" />
              ) : (
                <Layers className="w-8 h-8 text-[var(--color-content-secondary)]" />
              )}
            </div>
            <div>
              <h1 className="text-2xl font-bold text-[var(--color-content-primary)]">
                {run.name || run.suite_name || run.category_name || 'Suite Run'}
              </h1>
              <div className="flex items-center gap-3 mt-2">
                <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-medium ${statusBadge.bg} ${statusBadge.color}`}>
                  <StatusIcon className="w-4 h-4" />
                  {statusBadge.label}
                </span>
                {run.is_categorical ? (
                  <span className="px-2.5 py-1 text-xs font-medium rounded-full bg-[var(--color-brand-muted)] text-[#2A6B6E]">
                    Category Run
                  </span>
                ) : (
                  <span className="px-2.5 py-1 text-xs font-medium rounded-full bg-[var(--color-surface-inset)] text-[var(--color-content-secondary)]">
                    Custom Suite
                  </span>
                )}
              </div>
              {run.description && (
                <p className="text-[var(--color-content-secondary)] mt-2">{run.description}</p>
              )}
            </div>
          </div>

          <button
            onClick={loadRunDetail}
            className="p-2.5 rounded-lg text-sm font-semibold transition-all inline-flex items-center gap-2 bg-[var(--color-surface-inset)] text-[var(--color-content-secondary)] border border-[var(--color-border-strong)] hover:bg-[var(--color-interactive-active)]"
          >
            <RefreshCw size={18} />
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-4 gap-4 mt-6 pt-6 border-t border-[var(--color-border-default)]">
          <div>
            <div className="text-sm text-[var(--color-content-muted)]">Total Scenarios</div>
            <div className="text-2xl font-bold text-[var(--color-content-primary)]">{run.total_scenarios || 0}</div>
          </div>
          <div>
            <div className="text-sm text-[var(--color-content-muted)]">Completed</div>
            <div className="text-2xl font-bold text-[var(--color-status-success)]">{run.completed_scenarios || 0}</div>
          </div>
          <div>
            <div className="text-sm text-[var(--color-content-muted)]">Failed</div>
            <div className="text-2xl font-bold text-[var(--color-status-danger)]">{run.failed_scenarios || 0}</div>
          </div>
          <div>
            <div className="text-sm text-[var(--color-content-muted)]">Progress</div>
            <div className="text-2xl font-bold text-[#2A6B6E]">{run.progress_percentage || 0}%</div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mt-4">
          <div className="w-full h-2 bg-[var(--color-interactive-active)] rounded-full overflow-hidden">
            <div
              className="h-full transition-all duration-300"
              style={{
                width: `${run.progress_percentage || 0}%`,
                background: 'linear-gradient(135deg, #2A6B6E 0%, #11484D 100%)',
              }}
            />
          </div>
        </div>

        {/* Timing Info */}
        <div className="flex gap-8 mt-4 text-sm text-[var(--color-content-secondary)]">
          <div>
            <span className="text-[var(--color-content-muted)]">Started:</span>{' '}
            {formatDate(run.started_at || run.created_at)}
          </div>
          {run.completed_at && (
            <div>
              <span className="text-[var(--color-content-muted)]">Completed:</span>{' '}
              {formatDate(run.completed_at)}
            </div>
          )}
          <div>
            <span className="text-[var(--color-content-muted)]">Duration:</span>{' '}
            {formatDuration(run.started_at || run.created_at, run.completed_at)}
          </div>
        </div>
      </div>

      {/* Scenario Executions */}
      <div className="bg-[var(--color-surface-raised)] rounded-xl shadow-sm overflow-hidden border border-[var(--color-border-default)]">
        <div className="px-6 py-4 border-b border-[var(--color-border-default)]">
          <h2 className="text-lg font-semibold text-[var(--color-content-primary)]">Scenario Executions</h2>
          <p className="text-sm text-[var(--color-content-muted)] mt-1">
            All scenarios that were executed as part of this suite run
          </p>
        </div>

        {(!run.scenario_executions || run.scenario_executions.length === 0) ? (
          <div className="p-12 text-center text-[var(--color-content-muted)]">
            <PlayCircle className="w-12 h-12 mx-auto mb-3 text-[var(--color-content-muted)]" />
            <div className="font-medium">No scenario executions yet</div>
            <div className="text-sm mt-1">Executions will appear here as they start</div>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-[var(--color-surface-inset)] border-b border-[var(--color-border-default)]">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-[var(--color-content-muted)] uppercase tracking-wider">
                    Scenario
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-[var(--color-content-muted)] uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-[var(--color-content-muted)] uppercase tracking-wider">
                    Progress
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-[var(--color-content-muted)] uppercase tracking-wider">
                    Started At
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-[var(--color-content-muted)] uppercase tracking-wider">
                    Duration
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-[var(--color-content-muted)] uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-[var(--color-surface-raised)] divide-y divide-[var(--color-border-subtle)]">
                {run.scenario_executions.map((execution: SuiteRunScenarioExecution) => {
                  const execStatus = getStatusBadge(execution.status);
                  const ExecStatusIcon = execStatus.icon;

                  return (
                    <tr key={execution.id} className="hover:bg-[var(--color-interactive-hover)] transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-[var(--color-content-primary)]">
                          {execution.scenario_name || 'Unknown Scenario'}
                        </div>
                        <div className="text-xs text-[var(--color-content-muted)] font-mono">
                          {execution.id.substring(0, 8)}...
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${execStatus.bg} ${execStatus.color}`}>
                          <ExecStatusIcon className="w-3.5 h-3.5" />
                          {execStatus.label}
                        </span>
                        {execution.error_message && (
                          <div className="text-xs text-[var(--color-status-danger)] mt-1 max-w-xs truncate" title={execution.error_message}>
                            {execution.error_message}
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center gap-3">
                          <div className="w-24 h-2 bg-[var(--color-interactive-active)] rounded-full overflow-hidden">
                            <div
                              className="h-full transition-all duration-300"
                              style={{
                                width: `${execution.progress_percentage || 0}%`,
                                background: execution.status === 'failed'
                                  ? '#ef4444'
                                  : 'linear-gradient(135deg, #2A6B6E 0%, #11484D 100%)',
                              }}
                            />
                          </div>
                          <span className="text-sm text-[var(--color-content-secondary)]">
                            {execution.current_step}/{execution.total_steps}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-[var(--color-content-secondary)]">
                        {formatDate(execution.started_at)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-[var(--color-content-secondary)]">
                        {formatDuration(execution.started_at, execution.completed_at)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <button
                          onClick={() => navigate(`/scenarios/executions/${execution.id}`)}
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 border border-[var(--color-border-strong)] rounded-lg text-[var(--color-content-secondary)] bg-[var(--color-surface-raised)] hover:bg-[var(--color-interactive-hover)] transition-colors"
                        >
                          <Eye className="w-4 h-4" />
                          View
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default SuiteRunDetail;
