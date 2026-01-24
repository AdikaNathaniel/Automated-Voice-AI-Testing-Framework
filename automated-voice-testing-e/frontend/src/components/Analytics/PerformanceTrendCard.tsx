import React from 'react';
import TrendChart from '../Charts/TrendChart';
import type { PerformanceTrendPoint } from '../../types/analytics';

type PerformanceTrendCardProps = {
  data: PerformanceTrendPoint[];
  isLoading?: boolean;
};

const numberFormatter = new Intl.NumberFormat(undefined, {
  maximumFractionDigits: 0,
});

const formatResponseTime = (value: number): string => `${numberFormatter.format(Math.round(value))} ms`;

const formatChange = (value: number | null | undefined): string => {
  if (value == null || Number.isNaN(value)) {
    return 'Change vs previous: —';
  }
  const rounded = Math.round(value);
  const sign = rounded > 0 ? '+' : '';
  return `Change vs previous: ${sign}${rounded} ms`;
};

const PerformanceTrendCard: React.FC<PerformanceTrendCardProps> = ({ data, isLoading = false }) => {
  const latest = data.length > 0 ? data[data.length - 1] : null;

  const responseTimeLabel = latest ? formatResponseTime(latest.avgResponseTimeMs) : '—';
  const changeLabel = formatChange(latest?.changeMs);
  const sampleLabel = latest ? `Sample size (latest): ${latest.sampleSize}` : 'Sample size (latest): —';

  return (
    <div className="card p-4 h-full flex flex-col gap-4">
      <div className="space-y-2">
        <h3 className="text-lg font-semibold">Response Time Trend</h3>
        <p className="text-sm">Average Response Time: {responseTimeLabel}</p>
        <p className="text-sm">{changeLabel}</p>
        <p className="text-sm">{sampleLabel}</p>
      </div>

      <hr className="border-[var(--color-border-default)] my-2" />

      {latest ? (
        <TrendChart
          title="Response Time Trend"
          data={data}
          xKey="periodStart"
          yKey="avgResponseTimeMs"
          variant="area"
          tooltipFormatter={(value) => `${Math.round(value)} ms`}
          emptyMessage="No performance data available"
        />
      ) : !isLoading ? (
        <p className="text-sm text-[var(--color-content-muted)]">
          No performance data available
        </p>
      ) : (
        <p className="text-sm text-[var(--color-content-muted)]">
          Loading performance trend...
        </p>
      )}
    </div>
  );
};

export default PerformanceTrendCard;
