import React from 'react';
import { Loader2 } from 'lucide-react';

export type ComparisonDimension = 'language' | 'testType' | 'timePeriod';

export type ComparisonDimensionOption = {
  id: ComparisonDimension;
  label: string;
};

export type AnalyticsComparisonEntry = {
  id: string;
  label: string;
  sampleSize: number;
  passRatePct: number;
  passRateDeltaPct: number | null;
  defectRatePct: number;
  defectDeltaPct: number | null;
  avgResponseTimeMs: number;
  responseDeltaMs: number | null;
};

export type AnalyticsComparisonData = {
  dimension: ComparisonDimension;
  entries: AnalyticsComparisonEntry[];
};

type AnalyticsComparisonViewProps = {
  title: string;
  options: ComparisonDimensionOption[];
  data: AnalyticsComparisonData;
  isLoading?: boolean;
  onDimensionChange: (dimension: ComparisonDimension) => void;
};

const percentFormatter = new Intl.NumberFormat(undefined, {
  minimumFractionDigits: 0,
  maximumFractionDigits: 1,
});

const integerFormatter = new Intl.NumberFormat(undefined, {
  maximumFractionDigits: 0,
});

const responseFormatter = new Intl.NumberFormat(undefined, {
  maximumFractionDigits: 0,
});

const formatPercent = (value: number) => `${percentFormatter.format(value)}%`;

const formatPercentDelta = (value: number | null) => {
  if (value == null || Number.isNaN(value)) {
    return '—';
  }
  const rounded = Math.round(value * 10) / 10;
  const sign = rounded > 0 ? '+' : rounded < 0 ? '-' : '';
  return `${sign}${Math.abs(rounded).toFixed(1)} pts`;
};

const formatResponse = (value: number) => `${responseFormatter.format(Math.round(value))} ms`;

const formatResponseDelta = (value: number | null) => {
  if (value == null || Number.isNaN(value)) {
    return '—';
  }
  const rounded = Math.round(value);
  const sign = rounded > 0 ? '+' : rounded < 0 ? '-' : '';
  return `${sign}${integerFormatter.format(Math.abs(rounded))} ms`;
};

const renderDeltaProgress = (
  value: number | null,
  isPositiveBetter: boolean,
  formatter: (value: number | null) => string
) => {
  if (value == null || Number.isNaN(value)) {
    return (
      <span className="text-xs text-[var(--color-content-muted)]">
        —
      </span>
    );
  }

  const positive = value >= 0;
  const isGood = positive === isPositiveBetter;
  const formatted = formatter(value);

  return (
    <span className={`text-sm ${isGood ? 'text-[var(--color-status-success)]' : 'text-[var(--color-status-danger)]'}`}>
      {formatted}
    </span>
  );
};

const AnalyticsComparisonView: React.FC<AnalyticsComparisonViewProps> = ({
  title,
  options,
  data,
  isLoading = false,
  onDimensionChange,
}) => {
  const handleDimensionChange = React.useCallback(
    (dimension: ComparisonDimension) => {
      if (dimension === data.dimension) {
        return;
      }
      onDimensionChange(dimension);
    },
    [data.dimension, onDimensionChange]
  );

  const hasEntries = data.entries.length > 0;

  return (
    <div className="card p-6 flex flex-col gap-6">
      <div className="flex flex-col sm:flex-row gap-4 sm:items-center">
        <div className="flex-1 space-y-1">
          <h2 className="text-2xl font-bold">{title}</h2>
          <p className="text-sm text-[var(--color-content-muted)]">
            Compare key quality metrics across dimensions to identify strengths and opportunities.
          </p>
        </div>

        <div className="inline-flex rounded-lg border border-[var(--color-border-default)] p-1">
          {options.map((option) => (
            <button
              key={option.id}
              className={`px-3 py-1 text-sm rounded ${data.dimension === option.id ? 'bg-[var(--color-status-info)] text-white' : 'text-[var(--color-content-secondary)] hover:bg-[var(--color-interactive-hover)]'}`}
              onClick={() => handleDimensionChange(option.id)}
              aria-label={option.label}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>

      {isLoading && (
        <div className="flex items-center justify-center py-4">
          <Loader2 className="w-6 h-6 animate-spin text-[var(--color-status-info)]" />
        </div>
      )}

      {hasEntries ? (
        <div className="overflow-x-auto">
          <table className="w-full text-sm" aria-label="Comparison metrics">
            <caption className="text-left sr-only">Comparison metrics</caption>
            <thead>
              <tr className="border-b border-[var(--color-border-default)]">
                <th className="text-left py-2 px-2">Segment</th>
                <th className="text-right py-2 px-2">Pass Rate</th>
                <th className="text-right py-2 px-2">Δ Pass Rate</th>
                <th className="text-right py-2 px-2">Defect Rate</th>
                <th className="text-right py-2 px-2">Δ Defect Rate</th>
                <th className="text-right py-2 px-2">Avg Response</th>
                <th className="text-right py-2 px-2">Δ Response</th>
                <th className="text-right py-2 px-2">Sample Size</th>
              </tr>
            </thead>
            <tbody>
              {data.entries.map((entry) => (
                <tr key={entry.id} className="border-b border-[var(--color-border-subtle)] hover:bg-[var(--color-interactive-hover)]">
                  <td className="py-2 px-2">
                    <div className="space-y-1">
                      <p className="text-sm font-semibold">
                        {entry.label}
                      </p>
                      <p className="text-xs text-[var(--color-content-muted)]">
                        ID: {entry.id}
                      </p>
                    </div>
                  </td>
                  <td className="text-right py-2 px-2">{formatPercent(entry.passRatePct)}</td>
                  <td className="text-right py-2 px-2">
                    {renderDeltaProgress(entry.passRateDeltaPct, true, formatPercentDelta)}
                  </td>
                  <td className="text-right py-2 px-2">{formatPercent(entry.defectRatePct)}</td>
                  <td className="text-right py-2 px-2">
                    {renderDeltaProgress(entry.defectDeltaPct, false, formatPercentDelta)}
                  </td>
                  <td className="text-right py-2 px-2">{formatResponse(entry.avgResponseTimeMs)}</td>
                  <td className="text-right py-2 px-2">
                    {renderDeltaProgress(entry.responseDeltaMs, false, formatResponseDelta)}
                  </td>
                  <td className="text-right py-2 px-2">{integerFormatter.format(entry.sampleSize)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="py-12 flex flex-col items-center justify-center gap-2">
          <p className="text-base text-[var(--color-content-muted)]">
            No comparison data available for the selected dimension.
          </p>
          <p className="text-sm text-[var(--color-content-muted)]">
            Adjust filters or try a different dimension to populate these metrics.
          </p>
        </div>
      )}
    </div>
  );
};

export default AnalyticsComparisonView;
