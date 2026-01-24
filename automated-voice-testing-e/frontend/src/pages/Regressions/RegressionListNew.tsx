import React, { useEffect, useState, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  RefreshCw,
  AlertTriangle,
  ArrowRightLeft,
  TrendingDown,
  CheckCircle,
  Bug,
  Clock,
  Filter,
} from 'lucide-react';

import {
  getRegressionRecords,
  resolveRegression,
  createDefectFromRegression,
  type RegressionRecord,
  type RegressionRecordListResponse,
} from '../../services/regression.service';
import { LoadingSpinner, ErrorState, EmptyState, StatCard, Dropdown } from '../../components/common';
import { useToast } from '../../components/common/Toast';

const formatDate = (value: string | null): string => {
  if (!value) return '—';
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return '—';
  return parsed.toLocaleString();
};

const getSeverityColor = (severity: string): string => {
  switch (severity.toLowerCase()) {
    case 'critical':
      return 'bg-[var(--color-brand-muted)] text-[var(--color-brand-primary)]';
    case 'high':
      return 'bg-[var(--color-status-amber-bg)] text-[var(--color-status-amber)]';
    case 'medium':
      return 'bg-[var(--color-status-warning-bg)] text-[var(--color-status-warning)]';
    case 'low':
      return 'bg-[var(--color-status-info-bg)] text-[var(--color-status-info)]';
    default:
      return 'bg-[var(--color-surface-inset)] text-[var(--color-content-primary)]';
  }
};

const getStatusColor = (status: string): string => {
  switch (status.toLowerCase()) {
    case 'active':
      return 'bg-[var(--color-status-danger-bg)] text-[var(--color-status-danger)]';
    case 'investigating':
      return 'bg-[var(--color-status-amber-bg)] text-[var(--color-status-amber)]';
    case 'resolved':
      return 'bg-[var(--color-status-emerald-bg)] text-[var(--color-status-emerald)]';
    case 'ignored':
      return 'bg-[var(--color-surface-inset)] text-[var(--color-content-secondary)]';
    default:
      return 'bg-[var(--color-surface-inset)] text-[var(--color-content-primary)]';
  }
};

const getCategoryIcon = (category: string) => {
  switch (category.toLowerCase()) {
    case 'status':
      return <ArrowRightLeft size={16} />;
    case 'metric':
      return <TrendingDown size={16} />;
    case 'llm':
      return <AlertTriangle size={16} />;
    default:
      return <Bug size={16} />;
  }
};

const RegressionListNew: React.FC = () => {
  const navigate = useNavigate();
  const { showToast } = useToast();

  const [data, setData] = useState<RegressionRecordListResponse>({
    total: 0,
    active: 0,
    resolved: 0,
    items: [],
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('active');
  const [processingId, setProcessingId] = useState<string | null>(null);

  const fetchRegressions = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await getRegressionRecords({
        status: statusFilter === 'all' ? undefined : statusFilter,
      });
      setData(response);
    } catch (err: unknown) {
      const message = (err as Error)?.message ?? 'Failed to load regression records.';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [statusFilter]);

  useEffect(() => {
    fetchRegressions();
  }, [fetchRegressions]);

  const handleResolve = useCallback(async (regression: RegressionRecord) => {
    const note = prompt('Enter resolution note (optional):');
    if (note === null) return; // User cancelled

    try {
      setProcessingId(regression.id);
      await resolveRegression(regression.id, { note: note || undefined });

      showToast({
        type: 'success',
        title: 'Regression Resolved',
        message: 'The regression has been marked as resolved.',
      });

      // Refresh list
      await fetchRegressions();
    } catch (err) {
      showToast({
        type: 'error',
        title: 'Resolution Failed',
        message: (err as Error)?.message ?? 'Could not resolve regression.',
      });
    } finally {
      setProcessingId(null);
    }
  }, [fetchRegressions, showToast]);

  const handleCreateDefect = useCallback(async (regression: RegressionRecord) => {
    const confirmed = confirm(
      `Create a defect to track this regression?\n\nScenario: ${regression.scriptName || regression.scriptId}\nCategory: ${regression.category}\nSeverity: ${regression.severity}`
    );

    if (!confirmed) return;

    try {
      setProcessingId(regression.id);
      const result = await createDefectFromRegression(regression.id, {
        severity: regression.severity,
      });

      showToast({
        type: 'success',
        title: 'Defect Created',
        message: 'A defect has been created to track this regression.',
        duration: 5000,
      });

      // Navigate to defect detail
      navigate(`/defects/${result.defect_id}`);
    } catch (err) {
      showToast({
        type: 'error',
        title: 'Defect Creation Failed',
        message: (err as Error)?.message ?? 'Could not create defect.',
      });
      setProcessingId(null);
    }
  }, [navigate, showToast]);

  const renderContent = () => {
    if (loading) {
      return <LoadingSpinner message="Loading regressions..." />;
    }

    if (error) {
      return <ErrorState message={error} variant="alert" />;
    }

    if (data.items.length === 0) {
      return (
        <EmptyState
          title="No Regressions Found"
          description={
            statusFilter === 'active'
              ? 'No active regressions detected. Your tests are performing well!'
              : 'No regressions found for the selected filter.'
          }
          icon="check"
        />
      );
    }

    return (
      <div className="bg-[var(--color-surface-raised)] rounded-xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b-2 border-[var(--color-border-default)] bg-[var(--color-surface-inset)]/50">
                <th className="px-4 py-4 text-left text-xs font-semibold text-[var(--color-content-secondary)] uppercase tracking-wider">
                  Scenario
                </th>
                <th className="px-4 py-4 text-left text-xs font-semibold text-[var(--color-content-secondary)] uppercase tracking-wider">
                  Category
                </th>
                <th className="px-4 py-4 text-left text-xs font-semibold text-[var(--color-content-secondary)] uppercase tracking-wider">
                  Severity
                </th>
                <th className="px-4 py-4 text-left text-xs font-semibold text-[var(--color-content-secondary)] uppercase tracking-wider">
                  Status
                </th>
                <th className="px-4 py-4 text-left text-xs font-semibold text-[var(--color-content-secondary)] uppercase tracking-wider">
                  Detection
                </th>
                <th className="px-4 py-4 text-left text-xs font-semibold text-[var(--color-content-secondary)] uppercase tracking-wider">
                  Occurrences
                </th>
                <th className="px-4 py-4 text-right text-xs font-semibold text-[var(--color-content-secondary)] uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((regression) => (
                <tr
                  key={regression.id}
                  className="border-b border-[var(--color-border-default)] transition-colors hover:bg-[var(--color-interactive-hover)]/50"
                >
                  <td className="px-4 py-4">
                    <div className="flex flex-col">
                      <span className="text-sm font-semibold text-[var(--color-content-primary)]">
                        {regression.scriptName || regression.scriptId}
                      </span>
                      {regression.linkedDefectId && (
                        <Link
                          to={`/defects/${regression.linkedDefectId}`}
                          className="text-xs text-[var(--color-status-info)] hover:underline mt-0.5"
                        >
                          Linked to defect
                        </Link>
                      )}
                    </div>
                  </td>
                  <td className="px-4 py-4">
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold capitalize bg-[var(--color-surface-inset)] text-[var(--color-content-primary)]">
                      {getCategoryIcon(regression.category)}
                      {regression.category}
                    </span>
                  </td>
                  <td className="px-4 py-4">
                    <span className={`px-2.5 py-1 rounded-md text-xs font-semibold capitalize ${getSeverityColor(regression.severity)}`}>
                      {regression.severity}
                    </span>
                  </td>
                  <td className="px-4 py-4">
                    <span className={`px-2.5 py-1 rounded-md text-xs font-semibold capitalize ${getStatusColor(regression.status)}`}>
                      {regression.status}
                    </span>
                  </td>
                  <td className="px-4 py-4 text-sm text-[var(--color-content-secondary)]">
                    <div className="flex items-center gap-1.5">
                      <Clock size={14} className="text-[var(--color-content-muted)]" />
                      {formatDate(regression.detectionDate)}
                    </div>
                  </td>
                  <td className="px-4 py-4">
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold bg-[var(--color-status-amber-bg)] text-[var(--color-status-amber)]">
                      {regression.occurrenceCount}×
                    </span>
                  </td>
                  <td className="px-4 py-4 text-right">
                    <div className="flex justify-end gap-2">
                      <Link
                        to={`/regressions/${regression.scriptId}/comparison`}
                        className="px-3 py-1.5 rounded-lg text-sm font-semibold transition-all inline-flex items-center gap-2 bg-[var(--color-surface-inset)] text-[var(--color-content-secondary)] border border-[var(--color-border-strong)] hover:bg-[var(--color-interactive-active)]"
                      >
                        Compare
                      </Link>

                      {regression.status === 'active' && !regression.linkedDefectId && (
                        <button
                          onClick={() => handleCreateDefect(regression)}
                          disabled={processingId === regression.id}
                          className="btn btn-accent px-3 py-1.5 rounded-lg text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          <Bug size={14} />
                          Create Defect
                        </button>
                      )}

                      {regression.status === 'active' && (
                        <button
                          onClick={() => handleResolve(regression)}
                          disabled={processingId === regression.id}
                          className="px-3 py-1.5 rounded-lg text-sm font-semibold transition-all inline-flex items-center gap-2 bg-[var(--color-status-success)] text-white hover:bg-[var(--color-status-success-hover)] disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          <CheckCircle size={14} />
                          Resolve
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  return (
    <>
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-bold text-[var(--color-content-primary)] flex items-center gap-3">
            <TrendingDown className="w-6 h-6" style={{ color: '#2A6B6E' }} />
            Regression Tracking
          </h1>
          <p className="text-sm text-[var(--color-content-muted)] mt-1">
            Track, resolve, and create defects from detected regressions.
          </p>
        </div>
        <div className="flex items-center gap-3">
          {/* Status Filter */}
          <div className="flex items-center gap-2">
            <Filter size={16} className="text-[var(--color-content-muted)]" />
            <Dropdown
              value={statusFilter}
              onChange={setStatusFilter}
              options={[
                { value: 'all', label: 'All Status' },
                { value: 'active', label: 'Active' },
                { value: 'investigating', label: 'Investigating' },
                { value: 'resolved', label: 'Resolved' },
                { value: 'ignored', label: 'Ignored' },
              ]}
            />
          </div>

          <button
            className="p-2.5 rounded-lg text-sm font-semibold transition-all inline-flex items-center gap-2 bg-[var(--color-surface-inset)] text-[var(--color-content-secondary)] border border-[var(--color-border-strong)] hover:bg-[var(--color-interactive-active)]"
            onClick={fetchRegressions}
            disabled={loading}
          >
            <RefreshCw size={18} className={loading ? 'animate-spin' : ''} />
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mb-5">
        <StatCard
          title="Total Regressions"
          value={String(data.total)}
          icon={<AlertTriangle className="w-6 h-6" />}
          iconColor="text-[var(--color-status-danger)]"
          iconBg="bg-[var(--color-status-danger-bg)]"
        />
        <StatCard
          title="Active Regressions"
          value={String(data.active)}
          icon={<Clock className="w-6 h-6" />}
          iconColor="text-[var(--color-status-warning)]"
          iconBg="bg-[var(--color-status-amber-bg)]"
        />
        <StatCard
          title="Resolved"
          value={String(data.resolved)}
          icon={<CheckCircle className="w-6 h-6" />}
          iconColor="text-[var(--color-status-success)]"
          iconBg="bg-[var(--color-status-emerald-bg)]"
        />
      </div>

      {/* Regressions Table */}
      {renderContent()}
    </>
  );
};

export default RegressionListNew;
