/**
 * ExecutiveSummary Component
 *
 * Displays high-level executive summary with key metrics.
 * Uses semantic tokens for consistent theming across light/dark/oled.
 */

import React from 'react';
import { RefreshCw } from 'lucide-react';

const numberFormatter = new Intl.NumberFormat();

export type ExecutiveSummaryData = {
  testsExecuted: number;
  systemHealthPct: number;
  issuesDetected: number;
  avgResponseTimeMs: number;
  updatedAt?: string;
};

export type ExecutiveSummaryProps = {
  data: ExecutiveSummaryData;
  loading?: boolean;
  error?: string | null;
  onRetry?: () => void;
};

const ExecutiveSummary: React.FC<ExecutiveSummaryProps> = ({
  data,
  loading = false,
  error = null,
  onRetry,
}) => {
  if (loading) {
    return (
      <div className="card">
        <div data-testid="executive-summary-loading" className="flex flex-col items-center justify-center py-6">
          <div
            className="w-12 h-12 rounded-full animate-spin mb-4"
            style={{
              border: '4px solid var(--color-border-default)',
              borderTopColor: 'var(--color-brand-primary)'
            }}
          />
          <span className="text-sm text-[var(--color-content-muted)]">Loading summary...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <div
          className="rounded-xl p-4 flex items-center justify-between"
          style={{
            background: 'var(--color-status-danger-bg)',
            border: '1px solid var(--color-status-danger)'
          }}
        >
          <p className="text-[var(--color-status-danger)]">{error}</p>
          {onRetry && (
            <button
              onClick={onRetry}
              className="btn-secondary flex items-center gap-2"
            >
              <RefreshCw size={16} />
              Retry
            </button>
          )}
        </div>
      </div>
    );
  }

  const { testsExecuted, systemHealthPct, issuesDetected, avgResponseTimeMs, updatedAt } = data;
  const formattedTests = numberFormatter.format(testsExecuted);
  const formattedIssues = numberFormatter.format(issuesDetected);
  const formattedHealth = `${systemHealthPct.toFixed(1)}%`;
  const formattedResponse = `${(avgResponseTimeMs / 1000).toFixed(2)}s`;
  const lastUpdated = updatedAt ? new Date(updatedAt).toLocaleString() : null;

  return (
    <div className="card-static">
      <div className="flex justify-between items-center mb-4 pb-3 border-b border-[var(--color-border-subtle)]">
        <h2 className="text-lg font-bold text-[var(--color-content-primary)]">Executive Summary</h2>
        {lastUpdated && (
          <span className="text-xs text-[var(--color-content-muted)]">
            Last updated {lastUpdated}
          </span>
        )}
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <SummaryCard label="Tests Executed" value={formattedTests} />
        <SummaryCard label="System Health" value={formattedHealth} />
        <SummaryCard label="Issues Detected" value={formattedIssues} />
        <SummaryCard label="Avg Response Time" value={formattedResponse} />
      </div>
    </div>
  );
};

type SummaryCardProps = {
  label: string;
  value: string;
};

const SummaryCard: React.FC<SummaryCardProps> = ({ label, value }) => (
  <div
    className="rounded-xl p-4 transition-all hover:scale-[1.02]"
    style={{
      background: 'var(--color-surface-inset)',
      border: '1px solid var(--color-border-subtle)'
    }}
  >
    <div className="text-sm text-[var(--color-content-secondary)] mb-1">{label}</div>
    <div className="text-3xl font-bold text-[var(--color-content-primary)]">{value}</div>
  </div>
);

export default ExecutiveSummary;
