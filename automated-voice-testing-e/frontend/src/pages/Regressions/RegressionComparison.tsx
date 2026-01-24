import React, { useEffect, useMemo, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, ExternalLink } from 'lucide-react';

import { getRegressionComparison } from '../../services/regression.service';
import type { RegressionComparison as RegressionComparisonData, RegressionDifference } from '../../types/regression';

const formatNumber = (value: number | null, { percent = false }: { percent?: boolean } = {}): string => {
  if (typeof value !== 'number' || Number.isNaN(value)) {
    return '—';
  }

  const formatted = value.toFixed(2);
  return percent ? `${formatted}%` : formatted;
};

const resolveDeltaColor = (difference: RegressionDifference): string => {
  if (typeof difference.delta !== 'number' || Number.isNaN(difference.delta) || difference.delta === 0) {
    return 'text-[var(--color-content-primary)]';
  }

  return difference.delta < 0 ? 'text-[var(--color-status-danger)]' : 'text-[var(--color-status-success)]';
};

const RegressionComparison: React.FC = () => {
  const { scriptId } = useParams<{ scriptId: string }>();
  const navigate = useNavigate();

  const [comparison, setComparison] = useState<RegressionComparisonData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!scriptId) {
      setError('Missing script identifier.');
      setLoading(false);
      return;
    }

    let cancelled = false;

    const fetchComparison = async () => {
      try {
        setLoading(true);
        setError(null);
        const result = await getRegressionComparison(scriptId);
        if (!cancelled) {
          setComparison(result);
        }
      } catch (err: unknown) {
        if (!cancelled) {
          setError(err?.message ?? 'Failed to load comparison data.');
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    fetchComparison();

    return () => {
      cancelled = true;
    };
  }, [scriptId]);

  const content = useMemo(() => {
    if (loading) {
      return (
        <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-sm">
          <div className="flex flex-col items-center justify-center p-20">
            <div className="w-12 h-12 border-4 border-[var(--color-border-default)] rounded-full animate-spin mb-4" style={{ borderTopColor: '#2A6B6E' }}></div>
            <div className="text-lg font-semibold text-[var(--color-content-primary)] mb-2">Loading Comparison...</div>
          </div>
        </div>
      );
    }

    if (error) {
      return (
        <div className="p-4 rounded-lg mb-5 flex items-center gap-3 bg-danger-light  text-[var(--color-status-danger)] border-l-4 border-danger " data-testid="comparison-error">
          <div className="text-xl">⚠️</div>
          <div className="flex-1">
            <div className="font-semibold">{error}</div>
          </div>
        </div>
      );
    }

    if (!comparison) {
      return (
        <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-sm">
          <div className="flex flex-col items-center justify-center p-20">
            <div className="text-6xl mb-4">📊</div>
            <div className="text-lg font-semibold text-[var(--color-content-primary)] mb-2">No Comparison Data</div>
            <div className="text-sm text-[var(--color-content-muted)]">No comparison data available for this test case yet.</div>
          </div>
        </div>
      );
    }

    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          <div className="bg-[var(--color-surface-raised)] rounded-xl shadow-sm p-6" data-testid="regression-baseline">
            <h2 className="text-xl font-bold text-[var(--color-content-primary)] mb-4">Baseline Snapshot</h2>
            <p className="text-sm font-semibold text-[var(--color-content-muted)] mb-1">Status</p>
            <p className="text-2xl font-bold text-[var(--color-content-primary)] capitalize mb-4">
              {comparison.baseline.status ?? 'Unknown'}
            </p>
            {comparison.baseline.mediaUri && (
              <a
                href={comparison.baseline.mediaUri}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center px-4 py-2.5 rounded-lg text-sm font-semibold transition-all gap-2 bg-[var(--color-surface-inset)] text-[var(--color-content-secondary)] border border-[var(--color-border-strong)] hover:bg-[var(--color-interactive-active)]"
              >
                <ExternalLink size={16} />
                Open baseline media
              </a>
            )}
          </div>

          <div className="bg-[var(--color-surface-raised)] rounded-xl shadow-sm p-6" data-testid="regression-current">
            <h2 className="text-xl font-bold text-[var(--color-content-primary)] mb-4">Current Snapshot</h2>
            <p className="text-sm font-semibold text-[var(--color-content-muted)] mb-1">Status</p>
            <p className="text-2xl font-bold text-[var(--color-content-primary)] capitalize mb-4">
              {comparison.current.status ?? 'Unknown'}
            </p>
            {comparison.current.mediaUri && (
              <a
                href={comparison.current.mediaUri}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center px-4 py-2.5 rounded-lg text-sm font-semibold transition-all gap-2 bg-[var(--color-surface-inset)] text-[var(--color-content-secondary)] border border-[var(--color-border-strong)] hover:bg-[var(--color-interactive-active)]"
              >
                <ExternalLink size={16} />
                Open current media
              </a>
            )}
          </div>
        </div>

        <div className="bg-[var(--color-surface-raised)] rounded-xl shadow-sm p-6">
          <h2 className="text-xl font-bold text-[var(--color-content-primary)] mb-4">Metric Comparison</h2>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }} aria-label="Metric comparison">
              <thead>
                <tr className="border-b-2 border-[var(--color-border-default)] bg-[var(--color-surface-inset)]/50">
                  <th className="px-4 py-4 text-left text-xs font-semibold text-[var(--color-content-secondary)] uppercase tracking-wider">
                    Metric
                  </th>
                  <th className="px-4 py-4 text-left text-xs font-semibold text-[var(--color-content-secondary)] uppercase tracking-wider">
                    Baseline
                  </th>
                  <th className="px-4 py-4 text-left text-xs font-semibold text-[var(--color-content-secondary)] uppercase tracking-wider">
                    Current
                  </th>
                  <th className="px-4 py-4 text-left text-xs font-semibold text-[var(--color-content-secondary)] uppercase tracking-wider">
                    Δ
                  </th>
                  <th className="px-4 py-4 text-left text-xs font-semibold text-[var(--color-content-secondary)] uppercase tracking-wider">
                    Δ%
                  </th>
                </tr>
              </thead>
              <tbody>
                {comparison.differences.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-8 py-8 text-center text-[var(--color-content-muted)]">
                      No metric differences detected.
                    </td>
                  </tr>
                ) : (
                  comparison.differences.map((difference) => (
                    <tr
                      key={difference.metric}
                      className="border-b border-[var(--color-border-default)] transition-colors hover:bg-[var(--color-interactive-hover)]/50"
                    >
                      <td className="px-4 py-4 text-sm text-[var(--color-content-primary)] capitalize">
                        {difference.metric}
                      </td>
                      <td className="px-4 py-4 text-sm text-[var(--color-content-secondary)]">
                        {formatNumber(difference.baselineValue)}
                      </td>
                      <td className="px-4 py-4 text-sm text-[var(--color-content-secondary)]">
                        {formatNumber(difference.currentValue)}
                      </td>
                      <td className={`px-4 py-4 text-sm font-semibold ${resolveDeltaColor(difference)}`}>
                        {formatNumber(difference.delta)}
                      </td>
                      <td className={`px-4 py-4 text-sm font-semibold ${resolveDeltaColor(difference)}`}>
                        {formatNumber(difference.deltaPercent, { percent: true })}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    );
  }, [comparison, error, loading]);

  return (
    <>
      {/* Header */}
      <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 mb-6 shadow-md">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-[var(--color-content-primary)] mb-2">Regression Comparison</h1>
            <div className="text-sm text-[var(--color-content-muted)]">
              {scriptId ? `Script: ${scriptId}` : 'No script selected'}
            </div>
          </div>
          <div className="flex gap-3 flex-wrap">
            <Link
              to={scriptId ? `/regressions/${scriptId}/baselines` : '#'}
              className={`inline-flex items-center px-4 py-2.5 rounded-lg text-sm font-semibold transition-all gap-2 ${
                scriptId
                  ? 'text-white hover:shadow-lg hover:-translate-y-0.5'
                  : 'bg-[var(--color-interactive-active)] text-[var(--color-content-muted)] cursor-not-allowed'
              }`}
              style={scriptId ? { background: 'linear-gradient(135deg, #2A6B6E 0%, #11484D 100%)' } : undefined}
              onClick={(e) => !scriptId && e.preventDefault()}
            >
              Manage baseline
            </Link>
            <button
              onClick={() => navigate('/regressions')}
              className="inline-flex items-center px-4 py-2.5 rounded-lg text-sm font-semibold transition-all gap-2 bg-[var(--color-surface-inset)] text-[var(--color-content-secondary)] border border-[var(--color-border-strong)] hover:bg-[var(--color-interactive-active)]"
            >
              <ArrowLeft size={16} />
              Back to regressions
            </button>
          </div>
        </div>
      </div>

      {/* Comparison Content */}
      {content}
    </>
  );
};

export default RegressionComparison;
