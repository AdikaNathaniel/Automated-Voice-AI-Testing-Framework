import React from 'react';
import TrendChart from '../Charts/TrendChart';
import type { PassRateTrendPoint } from '../../types/analytics';

type PassRateTrendCardProps = {
  data: PassRateTrendPoint[];
  isLoading?: boolean;
};

const formatPassRate = (value: number): string => `${value.toFixed(1)}%`;

const formatChange = (value: number | null | undefined): string => {
  if (value == null || Number.isNaN(value)) {
    return 'Change vs previous: —';
  }
  const rounded = Math.round(value * 10) / 10;
  const sign = rounded > 0 ? '+' : '';
  return `Change vs previous: ${sign}${rounded.toFixed(1)}%`;
};

const PassRateTrendCard: React.FC<PassRateTrendCardProps> = ({ data, isLoading = false }) => {
  const latest = data.length > 0 ? data[data.length - 1] : null;

  const latestPassRateLabel = latest ? formatPassRate(latest.passRatePct) : '—';
  const changeLabel = formatChange(latest?.changePct);
  const executionLabel = latest ? `Executions (latest): ${latest.totalExecutions}` : 'Executions (latest): —';

  return (
    <div className="card p-4 h-full flex flex-col gap-4">
      <div className="space-y-2">
        <h3 className="text-lg font-semibold">Pass Rate Trend</h3>
        <p className="text-sm">Latest Pass Rate: {latestPassRateLabel}</p>
        <p className="text-sm">{changeLabel}</p>
        <p className="text-sm">{executionLabel}</p>
      </div>

      <hr className="border-[var(--color-border-default)] my-2" />

      {latest ? (
        <TrendChart
          title="Pass Rate Trend"
          data={data}
          xKey="periodStart"
          yKey="passRatePct"
          variant="area"
          tooltipFormatter={(value) => `${value.toFixed(2)}%`}
          emptyMessage="No pass rate data available"
        />
      ) : !isLoading ? (
        <p className="text-sm text-[var(--color-content-muted)]">
          No pass rate data available
        </p>
      ) : (
        <p className="text-sm text-[var(--color-content-muted)]">
          Loading pass rate trend...
        </p>
      )}
    </div>
  );
};

export default PassRateTrendCard;
