import React, { useEffect, useMemo, useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { RefreshCw, AlertTriangle, ArrowRightLeft, TrendingDown } from 'lucide-react';

import { getRegressions } from '../../services/regression.service';
import type { RegressionFinding, RegressionSummary } from '../../types/regression';
import { LoadingSpinner, ErrorState, EmptyState, StatCard } from '../../components/common';

const INITIAL_SUMMARY: RegressionSummary = {
  totalRegressions: 0,
  statusRegressions: 0,
  metricRegressions: 0,
};

const resolveImpact = (finding: RegressionFinding): string => {
  const { detail } = finding;

  if (finding.category === 'status') {
    const baseline = (detail.baseline_status ?? detail.baselineStatus) as string | undefined;
    const current = (detail.current_status ?? detail.currentStatus) as string | undefined;

    if (baseline && current) {
      return `${baseline} → ${current}`;
    }
  }

  if (finding.category === 'metric') {
    const metricName = (detail.metric ?? detail.metric_name) as string | undefined;
    const changeValue = detail.change as number | undefined;
    const changePct = detail.change_pct as number | undefined;

    if (metricName && typeof changeValue === 'number') {
      const pctText = typeof changePct === 'number' ? ` (${changePct.toFixed(1)}%)` : '';
      return `${metricName}: ${changeValue.toFixed(2)}${pctText}`;
    }
  }

  if (detail.message && typeof detail.message === 'string') {
    return detail.message;
  }

  return 'Review details';
};

const formatDetectedAt = (value?: string | null): string => {
  if (!value) {
    return '—';
  }

  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return '—';
  }

  return parsed.toLocaleString();
};

const RegressionList: React.FC = () => {
  const [summary, setSummary] = useState<RegressionSummary>(INITIAL_SUMMARY);
  const [regressions, setRegressions] = useState<RegressionFinding[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    const fetchRegressions = async () => {
      try {
        setLoading(true);
        setError(null);

        const response = await getRegressions();
        if (!cancelled) {
          setSummary(response.summary);
          setRegressions(response.items);
        }
      } catch (err: unknown) {
        if (!cancelled) {
          setError(err?.message ?? 'Failed to load regressions.');
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    fetchRegressions();

    return () => {
      cancelled = true;
    };
  }, []);

  const content = useMemo(() => {
    if (loading) {
      return <LoadingSpinner message="Loading Regressions..." />;
    }

    if (error) {
      return <ErrorState message={error} variant="alert" />;
    }

    if (regressions.length === 0) {
      return (
        <EmptyState
          title="No Regressions Found"
          description="No regressions detected for the selected context."
          icon="search"
        />
      );
    }

    return (
      <div className="bg-[var(--color-surface-raised)] rounded-xl shadow-sm" style={{ padding: 0, overflow: 'hidden' }}>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr className="border-b-2 border-[var(--color-border-default)] bg-[var(--color-surface-inset)]/50">
                <th className="px-4 py-4 text-left text-xs font-semibold text-[var(--color-content-secondary)] uppercase tracking-wider">
                  Test Case
                </th>
                <th className="px-4 py-4 text-left text-xs font-semibold text-[var(--color-content-secondary)] uppercase tracking-wider">
                  Category
                </th>
                <th className="px-4 py-4 text-left text-xs font-semibold text-[var(--color-content-secondary)] uppercase tracking-wider">
                  Impact
                </th>
                <th className="px-4 py-4 text-left text-xs font-semibold text-[var(--color-content-secondary)] uppercase tracking-wider">
                  Detected
                </th>
                <th className="px-4 py-4 text-right text-xs font-semibold text-[var(--color-content-secondary)] uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody>
              {regressions.map((finding) => (
                <tr
                  key={`${finding.scriptId}-${finding.detectedAt ?? 'unknown'}`}
                  className="border-b border-[var(--color-border-default)] transition-colors hover:bg-[var(--color-interactive-hover)]/50"
                >
                  <td className="px-4 py-4 text-sm font-semibold text-[var(--color-content-primary)]">
                    {finding.scriptId}
                  </td>
                  <td className="px-4 py-4">
                    <span
                      className={`px-2.5 py-1 rounded-md text-xs font-semibold capitalize ${
                        finding.category === 'status'
                          ? 'bg-[var(--color-status-warning-bg)] text-[var(--color-status-warning)]'
                          : 'bg-[var(--color-status-info-bg)] text-[var(--color-status-info)]'
                      }`}
                    >
                      {finding.category}
                    </span>
                  </td>
                  <td className="px-4 py-4 text-sm text-[var(--color-content-secondary)]">
                    {resolveImpact(finding)}
                  </td>
                  <td className="px-4 py-4 text-sm text-[var(--color-content-secondary)]">
                    {formatDetectedAt(finding.detectedAt)}
                  </td>
                  <td className="px-4 py-4 text-right">
                    <div className="flex justify-end gap-2">
                      <Link
                        to={`/regressions/${finding.scriptId}/comparison`}
                        className="px-3 py-1.5 rounded-lg text-sm font-semibold transition-all inline-flex items-center gap-2 bg-[var(--color-surface-inset)] text-[var(--color-content-secondary)] border border-[var(--color-border-strong)] hover:bg-[var(--color-interactive-active)]"
                      >
                        View comparison
                      </Link>
                      <Link
                        to={`/regressions/${finding.scriptId}/baselines`}
                        className="px-3 py-1.5 text-sm font-semibold transition-all text-[var(--color-content-secondary)] hover:text-[var(--color-content-primary)]"
                      >
                        Manage baseline
                      </Link>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  }, [error, loading, regressions]);

  const handleRefresh = useCallback(() => {
    setLoading(true);
    setError(null);
    getRegressions()
      .then((response) => {
        setSummary(response.summary);
        setRegressions(response.items);
      })
      .catch((err: unknown) => {
        setError(err?.message ?? 'Failed to load regressions.');
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <>
      {/* Header */}
      <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 mb-6 shadow-md">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-[var(--color-content-primary)] flex items-center gap-3">
              <TrendingDown className="w-6 h-6" style={{ color: '#2A6B6E' }} />
              Regression Insights
            </h1>
            <div className="text-sm text-[var(--color-content-muted)] mt-1">
              Track and analyze regressions detected in test executions.
            </div>
          </div>
          <button
            className="p-2.5 rounded-lg text-sm font-semibold transition-all inline-flex items-center gap-2 bg-[var(--color-surface-inset)] text-[var(--color-content-secondary)] border border-[var(--color-border-strong)] hover:bg-[var(--color-interactive-active)]"
            onClick={handleRefresh}
          >
            <RefreshCw size={18} />
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mb-5">
        <StatCard
          title="Total Regressions"
          value={String(summary.totalRegressions)}
          icon={<AlertTriangle className="w-6 h-6" />}
          iconColor="text-[var(--color-status-danger)]"
          iconBg="bg-[var(--color-status-danger-bg)]"
        />
        <StatCard
          title="Status Changes"
          value={String(summary.statusRegressions)}
          icon={<ArrowRightLeft className="w-6 h-6" />}
          iconColor="text-[var(--color-status-warning)]"
          iconBg="bg-[var(--color-status-warning-bg)]"
        />
        <StatCard
          title="Metric Degradations"
          value={String(summary.metricRegressions)}
          icon={<TrendingDown className="w-6 h-6" />}
          iconColor="text-[var(--color-status-info)]"
          iconBg="bg-[var(--color-status-info-bg)]"
        />
      </div>

      {/* Regressions Table */}
      {content}
    </>
  );
};

export default RegressionList;
