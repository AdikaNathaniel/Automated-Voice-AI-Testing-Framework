import React from 'react';
import TrendChart from '../Charts/TrendChart';
import type { DefectTrendPoint } from '../../types/analytics';

type DefectTrendCardProps = {
  data: DefectTrendPoint[];
  isLoading?: boolean;
};

const formatChange = (value: number | null | undefined): string => {
  if (value == null || Number.isNaN(value)) {
    return 'Change vs previous: —';
  }
  const rounded = Math.round(value);
  const sign = rounded > 0 ? '+' : '';
  return `Change vs previous: ${sign}${rounded}`;
};

const DefectTrendCard: React.FC<DefectTrendCardProps> = ({ data, isLoading = false }) => {
  const latest = data.length > 0 ? data[data.length - 1] : null;

  const openDefectsLabel = latest ? `Open Defects: ${latest.netOpen}` : 'Open Defects: —';
  const changeLabel = formatChange(latest?.changeOpen);
  const detectedResolvedLabel = latest
    ? `Detected vs resolved (latest): ${latest.detected} / ${latest.resolved}`
    : 'Detected vs resolved (latest): —';

  return (
    <div className="card p-4 h-full flex flex-col gap-4">
      <div className="space-y-2">
        <h3 className="text-lg font-semibold">Defect Backlog Trend</h3>
        <p className="text-sm">{openDefectsLabel}</p>
        <p className="text-sm">{changeLabel}</p>
        <p className="text-sm">{detectedResolvedLabel}</p>
      </div>

      <hr className="border-[var(--color-border-default)] my-2" />

      {latest ? (
        <TrendChart
          title="Defect Backlog Trend"
          data={data}
          xKey="periodStart"
          yKey="netOpen"
          variant="line"
          tooltipFormatter={(value) => value.toString()}
          emptyMessage="No defect trend data available"
        />
      ) : !isLoading ? (
        <p className="text-sm text-[var(--color-content-muted)]">
          No defect trend data available
        </p>
      ) : (
        <p className="text-sm text-[var(--color-content-muted)]">
          Loading defect trend...
        </p>
      )}
    </div>
  );
};

export default DefectTrendCard;
