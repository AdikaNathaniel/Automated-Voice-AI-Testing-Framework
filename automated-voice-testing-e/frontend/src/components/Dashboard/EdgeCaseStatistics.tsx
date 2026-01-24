import React from 'react';
import { AlertCircle } from 'lucide-react';

export type EdgeCaseCategory = {
  category: string;
  count: number;
};

export type EdgeCaseStatisticsData = {
  totalEdgeCases: number;
  resolvedCount: number;
  byCategory: EdgeCaseCategory[];
  resolutionRatePct?: number;
};

export type EdgeCaseStatisticsProps = {
  data: EdgeCaseStatisticsData;
  loading?: boolean;
  error?: string | null;
  onRetry?: () => void;
};

const integerFormatter = new Intl.NumberFormat();
const percentFormatter = new Intl.NumberFormat(undefined, {
  minimumFractionDigits: 0,
  maximumFractionDigits: 1,
});

const makeSlug = (value: string) =>
  value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)+/g, '');

const EdgeCaseStatistics: React.FC<EdgeCaseStatisticsProps> = ({
  data,
  loading = false,
  error = null,
  onRetry,
}) => {
  if (loading) {
    return (
      <div className="card">
        <div
          className="flex items-center justify-center py-4"
          data-testid="edge-case-stats-loading"
        >
          <div className="spinner"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <div className="flex items-start gap-3 p-4 bg-[var(--color-status-danger-bg)] text-[var(--color-status-danger)] rounded-lg border border-[var(--color-status-danger)]">
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="text-sm">{error}</p>
          </div>
          {onRetry && (
            <button
              onClick={onRetry}
              className="text-sm font-medium text-[var(--color-status-danger)] hover:opacity-80"
            >
              Retry
            </button>
          )}
        </div>
      </div>
    );
  }

  const { totalEdgeCases, resolvedCount, byCategory, resolutionRatePct } = data;
  const safeTotal = Math.max(totalEdgeCases, 0);
  const safeResolved = Math.max(Math.min(resolvedCount, safeTotal), 0);
  const openCount = Math.max(safeTotal - safeResolved, 0);
  const computedResolutionRate =
    typeof resolutionRatePct === 'number'
      ? Math.max(Math.min(resolutionRatePct, 100), 0)
      : safeTotal > 0
        ? (safeResolved / safeTotal) * 100
        : 0;

  const resolutionDisplay = `${percentFormatter.format(computedResolutionRate)}%`;

  return (
    <div className="card h-full">
      <div className="flex flex-col gap-4">
        <h2 className="card-title">
          Edge Case Statistics
        </h2>

        <div className="flex gap-6">
          <StatisticBlock
            label="Total"
            value={integerFormatter.format(safeTotal)}
            testId="edge-case-total"
          />
          <StatisticBlock
            label="Resolved"
            value={integerFormatter.format(safeResolved)}
            testId="edge-case-resolved"
          />
          <StatisticBlock
            label="Open"
            value={integerFormatter.format(openCount)}
            testId="edge-case-open"
          />
        </div>

        <div className="flex flex-col gap-2">
          <div className="flex items-center justify-between">
            <span className="text-sm font-semibold text-[var(--color-content-secondary)]">
              Resolution Rate
            </span>
            <span className="text-sm font-semibold" data-testid="edge-case-resolution-rate">
              {resolutionDisplay}
            </span>
          </div>
          <div className="progress-bar h-2">
            <div
              className="progress-fill h-full"
              style={{ width: `${Math.min(Math.max(computedResolutionRate, 0), 100)}%` }}
            ></div>
          </div>
        </div>

        <div className="border-t border-[var(--color-border-default)]"></div>

        <div className="flex flex-col gap-3">
          <h3 className="text-sm font-semibold text-[var(--color-content-secondary)]">
            By Category
          </h3>
          {byCategory.length > 0 ? (
            <div className="flex flex-col gap-2.5">
              {byCategory.map(({ category, count }) => (
                <CategoryRow
                  key={category}
                  category={category}
                  count={count}
                  testId={`edge-case-category-${makeSlug(category)}`}
                />
              ))}
            </div>
          ) : (
            <p className="text-sm text-[var(--color-content-secondary)]" data-testid="edge-case-category-empty">
              No categorized edge cases yet — start tagging failures to see insights.
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

type StatisticBlockProps = {
  label: string;
  value: string | number;
  testId: string;
};

const StatisticBlock: React.FC<StatisticBlockProps> = ({ label, value, testId }) => (
  <div className="flex flex-col gap-1">
    <span className="text-xs text-[var(--color-content-muted)]">
      {label}
    </span>
    <span className="text-2xl font-bold" data-testid={testId}>
      {value}
    </span>
  </div>
);

type CategoryRowProps = {
  category: string;
  count: number;
  testId: string;
};

const CategoryRow: React.FC<CategoryRowProps> = ({ category, count, testId }) => (
  <div
    className="flex items-center justify-between"
    data-testid={testId}
  >
    <span className="text-sm text-[var(--color-content-primary)]">{category}</span>
    <span className="text-sm text-[var(--color-content-secondary)]">
      {integerFormatter.format(count)}
    </span>
  </div>
);

export default EdgeCaseStatistics;
