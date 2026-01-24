/**
 * CI/CD Runs Page
 *
 * Displays a list of test runs triggered by CI/CD pipelines.
 */

import React, { useEffect, useMemo, useState, useCallback } from 'react';
import { GitBranch } from 'lucide-react';

import type { CICDRunRecord, CICDRunStatus } from '../../types/cicd';
import { getCICDRuns } from '../../services/cicd.service';
import { LoadingSpinner, ErrorState, EmptyState, Dropdown, FormLabel } from '../../components/common';

const STATUS_OPTIONS: { value: CICDRunStatus | null; label: string }[] = [
  { value: null, label: 'All statuses' },
  { value: 'success', label: 'Success' },
  { value: 'failed', label: 'Failed' },
  { value: 'running', label: 'Running' },
  { value: 'pending', label: 'Pending' },
];

const resolveStatusColor = (status: CICDRunStatus) => {
  switch (status) {
    case 'success':
      return 'bg-[var(--color-status-success-bg)] text-[var(--color-status-success)]';
    case 'failed':
      return 'bg-[var(--color-status-danger-bg)] text-[var(--color-status-danger)]';
    case 'running':
      return 'bg-[var(--color-status-warning-bg)] text-[var(--color-status-warning)]';
    case 'pending':
    default:
      return 'bg-[var(--color-interactive-hover)] text-[var(--color-content-primary)]';
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

const CICDRuns: React.FC = () => {
  const [statusFilter, setStatusFilter] = useState<CICDRunStatus | null>(null);
  const [runs, setRuns] = useState<CICDRunRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    const fetchRuns = async () => {
      try {
        setLoading(true);
        setError(null);

        const response = await getCICDRuns({
          status: statusFilter,
        });

        if (!cancelled) {
          setRuns(response.runs || []);
        }
      } catch (err: unknown) {
        if (!cancelled) {
          setError(err?.message ?? 'Failed to load CI/CD runs.');
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    fetchRuns();

    return () => {
      cancelled = true;
    };
  }, [statusFilter]);

  const content = useMemo(() => {
    if (loading) {
      return <LoadingSpinner message="Loading CI/CD Runs..." />;
    }

    if (error) {
      return <ErrorState message={error} variant="alert" />;
    }

    if (runs.length === 0) {
      return (
        <EmptyState
          title="No CI/CD Runs Found"
          description="No CI/CD runs found for the selected filters."
          icon="calendar"
        />
      );
    }

    return (
      <div className="bg-[var(--color-surface-raised)] rounded-xl shadow-sm" style={{ padding: 0, overflow: 'hidden' }}>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }} aria-label="CI/CD Runs">
            <thead>
              <tr className="border-b-2 border-[var(--color-border-default)] bg-[var(--color-surface-inset)]/50">
                <th className="px-4 py-4 text-left text-xs font-semibold text-[var(--color-content-secondary)] uppercase tracking-wider">Pipeline</th>
                <th className="px-4 py-4 text-left text-xs font-semibold text-[var(--color-content-secondary)] uppercase tracking-wider">Status</th>
                <th className="px-4 py-4 text-left text-xs font-semibold text-[var(--color-content-secondary)] uppercase tracking-wider">Branch</th>
                <th className="px-4 py-4 text-left text-xs font-semibold text-[var(--color-content-secondary)] uppercase tracking-wider">Commit</th>
                <th className="px-4 py-4 text-left text-xs font-semibold text-[var(--color-content-secondary)] uppercase tracking-wider">Triggered By</th>
                <th className="px-4 py-4 text-left text-xs font-semibold text-[var(--color-content-secondary)] uppercase tracking-wider">Started</th>
                <th className="px-4 py-4 text-left text-xs font-semibold text-[var(--color-content-secondary)] uppercase tracking-wider">Completed</th>
                <th className="px-4 py-4 text-left text-xs font-semibold text-[var(--color-content-secondary)] uppercase tracking-wider">Summary</th>
              </tr>
            </thead>
            <tbody>
              {runs.map((run) => (
                <tr
                  key={run.id}
                  className="border-b border-[var(--color-border-default)] hover:bg-[var(--color-interactive-hover)] transition-colors"
                >
                  <td className="px-4 py-4 text-sm text-[var(--color-content-primary)]">{run.pipelineName}</td>
                  <td className="px-4 py-4 text-sm">
                    <span className={`px-2.5 py-1 rounded-md text-xs font-semibold capitalize ${resolveStatusColor(run.status)}`}>
                      {run.status}
                    </span>
                  </td>
                  <td className="px-4 py-4 text-sm text-[var(--color-content-primary)]">{run.branch}</td>
                  <td className="px-4 py-4 text-sm">
                    <a href={run.commitUrl} target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">
                      {run.commitSha}
                    </a>
                  </td>
                  <td className="px-4 py-4 text-sm text-[var(--color-content-secondary)]">{run.triggeredBy}</td>
                  <td className="px-4 py-4 text-sm text-[var(--color-content-secondary)]">{formatDateTime(run.startedAt)}</td>
                  <td className="px-4 py-4 text-sm text-[var(--color-content-secondary)]">{formatDateTime(run.completedAt ?? null)}</td>
                  <td className="px-4 py-4 text-sm text-[var(--color-content-secondary)]">
                    {run.passedTests} passed / {run.failedTests} failed ({run.totalTests} total)
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  }, [error, loading, runs]);

  const handleStatusChange = useCallback((value: string) => {
    setStatusFilter(value === '' ? null : value as CICDRunStatus);
  }, []);

  return (
    <>
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-bold text-[var(--color-content-primary)] flex items-center gap-3">
            <GitBranch className="w-6 h-6" style={{ color: '#2A6B6E' }} />
            CI/CD Runs
          </h1>
          <p className="text-sm text-[var(--color-content-muted)] mt-1">
            Review automated pipeline executions and link directly to commit details.
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-[var(--color-surface-raised)] p-4 rounded-xl mb-5 shadow-sm">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="min-w-[180px]">
            <FormLabel htmlFor="status-filter">Status</FormLabel>
            <Dropdown
              id="status-filter"
              value={statusFilter ?? ''}
              onChange={handleStatusChange}
              options={STATUS_OPTIONS.map((option) => ({
                value: option.value ?? '',
                label: option.label,
              }))}
            />
          </div>
        </div>
      </div>

      {/* Content */}
      {content}
    </>
  );
};

export default CICDRuns;
