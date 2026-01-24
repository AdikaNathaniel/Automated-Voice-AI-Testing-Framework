
/**
 * SuiteRunDetail Page
 *
 * Detailed view of a single suite run with:
 * - Overview: Suite run metadata and summary
 * - Execution list: Individual test case executions with expandable details
 * - Statistics: Aggregated metrics and charts
 * - Real-time updates via WebSocket
 *
 * Features:
 * - Tailwind CSS layout
 * - URL parameter handling for suite run ID
 * - Data fetching via suite run service
 * - Expandable execution cards with validation details
 */

import React, { useEffect, useMemo, useState, useCallback } from 'react';
import { useParams, Link as RouterLink, useNavigate } from 'react-router-dom';
import {
  Loader2,
  ArrowLeft,
  RefreshCw,
  CheckCircle,
  XCircle,
  AlertCircle,
  Clock,
  Play,
  Filter,
  BarChart2,
  Eye,
  Globe,
  PlayCircle,
} from 'lucide-react';
import {
  getSuiteRunDetail,
  getSuiteRunExecutions,
} from '../../services/suiteRun.service';
import type {
  SuiteRunDetail as SuiteRunDetailType,
  SuiteRunExecution,
} from '../../types/suiteRun';
import { useSocket } from '../../hooks/useSocket';
import { Dropdown } from '../../components/common';

/**
 * Suite run status type
 */
type SuiteRunStatus =
  | 'pending'
  | 'running'
  | 'passed'
  | 'failed'
  | 'needs_review'
  | 'completed'
  | 'cancelled';

/**
 * Test execution status type
 */
type ExecutionStatus =
  | 'passed'
  | 'failed'
  | 'running'
  | 'pending'
  | 'completed'
  | 'skipped';

/**
 * Get status color based on suite run status
 */
const getStatusColor = (
  status: SuiteRunStatus | ExecutionStatus
): string => {
  switch (status) {
    case 'passed':
    case 'completed':
      return 'bg-[var(--color-status-success-bg)] text-[var(--color-status-success)]';
    case 'failed':
      return 'bg-[var(--color-status-danger-bg)] text-[var(--color-status-danger)]';
    case 'running':
      return 'bg-[var(--color-status-info-bg)] text-[var(--color-status-info)]';
    case 'needs_review':
      return 'bg-[var(--color-status-warning-bg)] text-[var(--color-status-warning)]';
    default:
      return 'bg-[var(--color-surface-inset)] text-[var(--color-content-secondary)]';
  }
};


const formatTimestamp = (value: string | null | undefined) => {
  if (!value) return '—';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return '—';
  }
  return date.toLocaleString();
};

const formatDuration = (seconds?: number | null) => {
  if (seconds === null || seconds === undefined) {
    return '—';
  }
  if (seconds < 1) {
    return `${(seconds * 1000).toFixed(0)} ms`;
  }
  return `${seconds.toFixed(2)}s`;
};

/**
 * Get execution status styling for table
 */
const getExecutionStatusStyle = (status: string): {
  icon: React.ReactNode;
  bgClass: string;
  textClass: string;
  label: string;
} => {
  switch (status) {
    case 'passed':
    case 'completed':
      return {
        icon: <CheckCircle className="w-3.5 h-3.5" />,
        bgClass: 'bg-[var(--color-status-success-bg)]',
        textClass: 'text-[var(--color-status-success)]',
        label: status === 'passed' ? 'Passed' : 'Completed',
      };
    case 'failed':
      return {
        icon: <XCircle className="w-3.5 h-3.5" />,
        bgClass: 'bg-[var(--color-status-danger-bg)]',
        textClass: 'text-[var(--color-status-danger)]',
        label: 'Failed',
      };
    case 'running':
    case 'in_progress':
      return {
        icon: <PlayCircle className="w-3.5 h-3.5" />,
        bgClass: 'bg-[var(--color-status-info-bg)]',
        textClass: 'text-[var(--color-status-info)]',
        label: 'Running',
      };
    case 'pending':
      return {
        icon: <Clock className="w-3.5 h-3.5" />,
        bgClass: 'bg-[var(--color-surface-inset)]',
        textClass: 'text-[var(--color-content-secondary)]',
        label: 'Pending',
      };
    default:
      return {
        icon: <AlertCircle className="w-3.5 h-3.5" />,
        bgClass: 'bg-[var(--color-status-warning-bg)]',
        textClass: 'text-[var(--color-status-warning)]',
        label: status,
      };
  }
};

/**
 * Get validation review status styling
 */
const getValidationStatusStyle = (status?: string | null): {
  icon: React.ReactNode;
  bgClass: string;
  textClass: string;
  label: string;
} | null => {
  if (!status) return null;

  switch (status) {
    case 'auto_pass':
      return {
        icon: <CheckCircle className="w-3 h-3" />,
        bgClass: 'bg-[var(--color-status-success-bg)]',
        textClass: 'text-[var(--color-status-success)]',
        label: 'Auto Pass',
      };
    case 'auto_fail':
      return {
        icon: <XCircle className="w-3 h-3" />,
        bgClass: 'bg-[var(--color-status-danger-bg)]',
        textClass: 'text-[var(--color-status-danger)]',
        label: 'Auto Fail',
      };
    case 'needs_review':
      return {
        icon: <AlertCircle className="w-3 h-3" />,
        bgClass: 'bg-[var(--color-status-warning-bg)]',
        textClass: 'text-[var(--color-status-warning)]',
        label: 'Needs Review',
      };
    default:
      return null;
  }
};

const SuiteRunDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [suiteRun, setSuiteRun] = useState<SuiteRunDetailType | null>(null);
  const [executions, setExecutions] = useState<SuiteRunExecution[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [refreshing, setRefreshing] = useState(false);
  const { isConnected, on, off, subscribeToSuiteRun } = useSocket();

  // Fetch function for reuse
  const fetchData = useCallback(async (showLoading = true) => {
    if (!id) {
      setError('Suite run ID is missing.');
      setLoading(false);
      return;
    }

    try {
      if (showLoading) setLoading(true);
      setRefreshing(true);
      setError(null);
      const [runDetail, executionList] = await Promise.all([
        getSuiteRunDetail(id),
        getSuiteRunExecutions(id),
      ]);
      setSuiteRun(runDetail);
      setExecutions(executionList);
    } catch {
      setError('Unable to load suite run. Please try again.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [id]);

  // Fetch initial data
  useEffect(() => {
    let cancelled = false;

    if (!cancelled) {
      fetchData();
    }

    return () => {
      cancelled = true;
    };
  }, [fetchData]);

  // Filter executions by status
  const filteredExecutions = useMemo(() => {
    if (statusFilter === 'all') return executions;
    return executions.filter(exec => {
      if (statusFilter === 'passed') return exec.status === 'passed' || exec.status === 'completed';
      if (statusFilter === 'failed') return exec.status === 'failed';
      if (statusFilter === 'pending') return exec.status === 'pending' || exec.status === 'running';
      if (statusFilter === 'needs_review') return exec.validationReviewStatus === 'needs_review';
      return true;
    });
  }, [executions, statusFilter]);

  // Execution statistics
  const executionStats = useMemo(() => {
    const passed = executions.filter(e => e.status === 'passed' || e.status === 'completed').length;
    const failed = executions.filter(e => e.status === 'failed').length;
    const pending = executions.filter(e => e.status === 'pending' || e.status === 'running').length;
    const needsReview = executions.filter(e => e.validationReviewStatus === 'needs_review').length;
    return { passed, failed, pending, needsReview };
  }, [executions]);

  // Handler for suite run updates (defined outside useEffect)
  const handleSuiteRunUpdate = useCallback((data: any) => {
    console.log('[SuiteRunDetail] Received suite_run_update:', data);

    setSuiteRun((prev) => {
      if (!prev) return prev;
      return {
        ...prev,
        status: data.status || prev.status,
        passedTests: data.passed_tests ?? prev.passedTests,
        failedTests: data.failed_tests ?? prev.failedTests,
        skippedTests: data.skipped_tests ?? prev.skippedTests,
        totalTests: data.total_tests ?? prev.totalTests,
      };
    });
  }, []);

  // Handler for individual test completion (defined outside useEffect)
  const handleTestCompleted = useCallback((data: any) => {
    console.log('[SuiteRunDetail] Received test_completed:', data);

    // Update or add execution in the list
    setExecutions((prev) => {
      const existingIndex = prev.findIndex(
        (exec) => exec.id === data.test_execution_id
      );

      if (existingIndex >= 0) {
        // Update existing execution
        const updated = [...prev];
        updated[existingIndex] = {
          ...updated[existingIndex],
          status: data.status,
          completedAt: data.completed_at,
          audioDuration: data.audio_duration,
          processingTime: data.processing_time,
        };
        return updated;
      } else {
        // Add new execution (if it wasn't in the initial list)
        return [
          ...prev,
          {
            id: data.test_execution_id,
            scriptId: data.script_id,
            suiteRunId: data.suite_run_id,
            languageCode: data.language_code,
            status: data.status,
            completedAt: data.completed_at,
            audioDuration: data.audio_duration,
            processingTime: data.processing_time,
          } as SuiteRunExecution,
        ];
      }
    });
  }, []);

  // Subscribe to real-time updates
  useEffect(() => {
    if (!id || !isConnected) return;

    // Subscribe to suite run updates
    subscribeToSuiteRun(id);
    console.log(`[SuiteRunDetail] Subscribed to suite run updates: ${id}`);

    // Subscribe to events
    on('suite_run_update', handleSuiteRunUpdate);
    on('test_completed', handleTestCompleted);

    return () => {
      off('suite_run_update', handleSuiteRunUpdate);
      off('test_completed', handleTestCompleted);
    };
  }, [id, isConnected, subscribeToSuiteRun, on, off, handleSuiteRunUpdate, handleTestCompleted]);

  const progress = useMemo(() => {
    if (!suiteRun || suiteRun.totalTests === 0) return 0;
    const completed = (suiteRun.passedTests || 0) + (suiteRun.failedTests || 0) + (suiteRun.skippedTests || 0);
    return Math.round((completed / suiteRun.totalTests) * 100);
  }, [suiteRun]);

  const isRunning = suiteRun?.status === 'running' || suiteRun?.status === 'pending';

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 mt-8 flex justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-[var(--color-status-info)]" />
      </div>
    );
  }

  if (error || !suiteRun) {
    return (
      <div className="max-w-7xl mx-auto px-4 mt-8">
        <div className="bg-[var(--color-status-danger-bg)] border border-[var(--color-status-danger)] rounded-lg p-4" role="alert">
          <p className="text-[var(--color-status-danger)]">{error ?? 'Unable to load suite run.'}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Page Header */}
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
            <h1 className="text-2xl font-bold text-[var(--color-content-primary)]">Suite Run Details</h1>
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(suiteRun.status)}`}>
              {suiteRun.status}
            </span>
            {isConnected && (
              <span className="text-xs text-[var(--color-status-success)] flex items-center gap-1">
                <span className="w-2 h-2 bg-[var(--color-status-success)] rounded-full animate-pulse"></span>
                Live
              </span>
            )}
          </div>

          <button
            onClick={() => fetchData(false)}
            disabled={refreshing}
            className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-[var(--color-content-secondary)] bg-[var(--color-surface-raised)] border border-[var(--color-border-strong)] rounded-lg hover:bg-[var(--color-interactive-hover)] disabled:opacity-50 transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      {/* Progress Bar for Running */}
      {isRunning && (
        <div className="mb-6 bg-[var(--color-surface-raised)] rounded-xl p-5 shadow-sm border border-[var(--color-border-default)]">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Play className="w-5 h-5 text-[var(--color-status-info)]" />
              <h3 className="text-sm font-semibold text-[var(--color-content-primary)]">Test Execution Progress</h3>
            </div>
            <span className="text-sm font-medium text-[var(--color-content-secondary)]">
              {(suiteRun.passedTests || 0) + (suiteRun.failedTests || 0) + (suiteRun.skippedTests || 0)} / {suiteRun.totalTests} tests
            </span>
          </div>

          <div className="w-full bg-[var(--color-surface-inset)] rounded-full h-3 overflow-hidden">
            <div
              className="h-full rounded-full transition-all duration-500 ease-out"
              style={{
                width: `${progress}%`,
                background: 'linear-gradient(135deg, #2A6B6E 0%, #11484D 100%)',
              }}
            />
          </div>

          <div className="mt-3 flex gap-6 text-xs text-[var(--color-content-secondary)]">
            <span className="flex items-center gap-1.5">
              <CheckCircle className="w-3.5 h-3.5 text-[var(--color-status-success)]" />
              Passed: {suiteRun.passedTests || 0}
            </span>
            <span className="flex items-center gap-1.5">
              <XCircle className="w-3.5 h-3.5 text-[var(--color-status-danger)]" />
              Failed: {suiteRun.failedTests || 0}
            </span>
            <span className="flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5 text-[var(--color-content-muted)]" />
              Pending: {suiteRun.totalTests - (suiteRun.passedTests || 0) - (suiteRun.failedTests || 0) - (suiteRun.skippedTests || 0)}
            </span>
          </div>
        </div>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-[var(--color-surface-raised)] rounded-xl p-5 shadow-sm border border-[var(--color-border-default)]">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-lg bg-[var(--color-surface-inset)] flex items-center justify-center">
              <BarChart2 className="w-5 h-5 text-[var(--color-content-secondary)]" />
            </div>
            <div>
              <p className="text-2xl font-bold text-[var(--color-content-primary)]">{suiteRun.totalTests}</p>
              <p className="text-xs text-[var(--color-content-muted)]">Total Tests</p>
            </div>
          </div>
        </div>

        <div className="bg-[var(--color-surface-raised)] rounded-xl p-5 shadow-sm border border-[var(--color-border-default)]">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-lg bg-[var(--color-status-success-bg)] flex items-center justify-center">
              <CheckCircle className="w-5 h-5 text-[var(--color-status-success)]" />
            </div>
            <div>
              <p className="text-2xl font-bold text-[var(--color-status-success)]">{executionStats.passed}</p>
              <p className="text-xs text-[var(--color-content-muted)]">Completed</p>
            </div>
          </div>
        </div>

        <div className="bg-[var(--color-surface-raised)] rounded-xl p-5 shadow-sm border border-[var(--color-border-default)]">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-lg bg-[var(--color-status-danger-bg)] flex items-center justify-center">
              <XCircle className="w-5 h-5 text-[var(--color-status-danger)]" />
            </div>
            <div>
              <p className="text-2xl font-bold text-[var(--color-status-danger)]">{executionStats.failed}</p>
              <p className="text-xs text-[var(--color-content-muted)]">Incomplete</p>
            </div>
          </div>
        </div>
      </div>

      {/* Run Details */}
      <div className="bg-[var(--color-surface-raised)] rounded-xl p-5 shadow-sm border border-[var(--color-border-default)] mb-6">
        <h2 className="text-lg font-semibold text-[var(--color-content-primary)] mb-4">Run Details</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <p className="text-[var(--color-content-muted)] mb-1">Run ID</p>
            <p className="font-mono text-xs text-[var(--color-content-secondary)]">{suiteRun.id}</p>
          </div>
          <div>
            <p className="text-[var(--color-content-muted)] mb-1">Suite ID</p>
            <p className="font-mono text-xs text-[var(--color-content-secondary)]">{suiteRun.testSuiteId || '—'}</p>
          </div>
          <div>
            <p className="text-[var(--color-content-muted)] mb-1">Trigger</p>
            <p className="text-[var(--color-content-secondary)] capitalize">{suiteRun.triggerType || 'manual'}</p>
          </div>
          <div>
            <p className="text-[var(--color-content-muted)] mb-1">Started</p>
            <p className="text-[var(--color-content-secondary)]">{formatTimestamp(suiteRun.startedAt)}</p>
          </div>
          <div>
            <p className="text-[var(--color-content-muted)] mb-1">Completed</p>
            <p className="text-[var(--color-content-secondary)]">{formatTimestamp(suiteRun.completedAt)}</p>
          </div>
          <div>
            <p className="text-[var(--color-content-muted)] mb-1">Created</p>
            <p className="text-[var(--color-content-secondary)]">{formatTimestamp(suiteRun.createdAt)}</p>
          </div>
        </div>
      </div>

      {/* Execution List Section */}
      <div className="bg-[var(--color-surface-raised)] rounded-xl shadow-sm border border-[var(--color-border-default)]">
        {/* Header with filters */}
        <div className="p-5 border-b border-[var(--color-border-subtle)]">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-[var(--color-content-primary)]">
              Test Executions
              <span className="ml-2 text-sm font-normal text-[var(--color-content-muted)]">
                ({filteredExecutions.length} of {executions.length})
              </span>
            </h2>

            <div className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-[var(--color-content-muted)]" />
              <Dropdown
                value={statusFilter}
                onChange={setStatusFilter}
                options={[
                  { value: 'all', label: 'All Statuses' },
                  { value: 'passed', label: `Passed (${executionStats.passed})` },
                  { value: 'failed', label: `Failed (${executionStats.failed})` },
                  { value: 'pending', label: `Pending (${executionStats.pending})` },
                  { value: 'needs_review', label: `Needs Review (${executionStats.needsReview})` },
                ]}
              />
            </div>
          </div>
        </div>

        {/* Executions Table */}
        {filteredExecutions.length === 0 ? (
          <div className="p-12 text-center">
            <Clock className="w-12 h-12 text-[var(--color-content-muted)] mx-auto mb-4" />
            <p className="text-[var(--color-content-muted)]">
              {executions.length === 0
                ? 'No executions recorded for this run yet.'
                : 'No executions match the selected filter.'}
            </p>
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
                    Validation
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-[var(--color-content-muted)] uppercase tracking-wider">
                    Steps
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
                {filteredExecutions.map((execution) => {
                  const statusStyle = getExecutionStatusStyle(execution.status);
                  const validationStyle = getValidationStatusStyle(execution.validationReviewStatus);

                  return (
                    <tr
                      key={execution.id}
                      className="hover:bg-[var(--color-interactive-hover)] transition-colors cursor-pointer"
                      onClick={() => navigate(`/scenarios/executions/${execution.id}`)}
                    >
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div>
                          <div className="text-sm font-medium text-[var(--color-content-primary)]">
                            {execution.scriptName || 'Unknown Scenario'}
                          </div>
                          <div className="flex items-center gap-2 text-xs text-[var(--color-content-muted)]">
                            <span className="font-mono">{execution.id.substring(0, 8)}...</span>
                            {execution.languageCode && (
                              <>
                                <span className="text-[var(--color-content-muted)]">|</span>
                                <span className="flex items-center gap-1">
                                  <Globe className="w-3 h-3" />
                                  {execution.languageCode}
                                </span>
                              </>
                            )}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${statusStyle.bgClass} ${statusStyle.textClass}`}>
                          {statusStyle.icon}
                          {statusStyle.label}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {validationStyle ? (
                          <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${validationStyle.bgClass} ${validationStyle.textClass}`}>
                            {validationStyle.icon}
                            {validationStyle.label}
                          </span>
                        ) : (
                          <span className="text-xs text-[var(--color-content-muted)]">—</span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-[var(--color-content-primary)]">
                        {execution.totalSteps !== undefined && execution.totalSteps !== null ? (
                          <span>
                            {execution.completedSteps || 0}/{execution.totalSteps}
                          </span>
                        ) : (
                          <span className="text-[var(--color-content-muted)]">—</span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-[var(--color-content-secondary)]">
                        {formatDuration(execution.responseTimeSeconds)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            navigate(`/scenarios/executions/${execution.id}`);
                          }}
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
