import React from 'react';
import { AlertCircle, Info } from 'lucide-react';
import type { DefectSummary } from '../../types/dashboard';

export type DefectTrendPoint = {
  date: string;
  open: number;
};

export type DefectTrackingProps = {
  summary: DefectSummary;
  trend: DefectTrendPoint[];
  loading?: boolean;
  error?: string | null;
  onRetry?: () => void;
};

const numberFormatter = new Intl.NumberFormat();

const DefectTracking: React.FC<DefectTrackingProps> = ({
  summary,
  trend,
  loading = false,
  error = null,
  onRetry,
}) => {
  if (loading) {
    return (
      <div className="card">
        <div
          className="flex items-center justify-center py-4"
          data-testid="defect-tracking-loading"
        >
          <div className="spinner"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <div className="flex items-start gap-3 p-4 bg-[var(--color-status-danger-bg)] text-[var(--color-status-danger)] rounded-lg border border-[var(--color-status-danger)]/20">
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

  const severityRows: Array<{ label: string; value: number; color?: string }> = [
    { label: 'Open Issues', value: summary.open },
    { label: 'Critical', value: summary.critical, color: 'error' },
    { label: 'High', value: summary.high, color: 'warning' },
    { label: 'Medium', value: summary.medium },
    { label: 'Low', value: summary.low },
  ];

  const maxTrendValue = trend.reduce((max, point) => Math.max(max, point.open), 0);
  const firstTrend = trend[0]?.date ?? null;
  const lastTrend = trend[trend.length - 1]?.date ?? null;

  return (
    <div className="card h-full">
      <div className="flex flex-col gap-4 h-full">
        <div className="flex justify-between items-center">
          <h2 className="card-title">
            Defect Detection &amp; Tracking
          </h2>
          <span className={`badge ${summary.open > 0 ? 'badge-warning' : 'badge-success'}`}>
            {numberFormatter.format(summary.open)} open
          </span>
        </div>

        <div className="flex flex-col gap-3">
          {severityRows.map((row) => (
            <SeverityRow
              key={row.label}
              label={row.label}
              value={row.value}
              color={row.color}
            />
          ))}
        </div>

        <div className="border-t border-[var(--color-border-subtle)] my-2"></div>

        <div className="flex flex-col gap-2">
          <h3 className="text-base font-semibold text-[var(--color-content-primary)]">Defects over time</h3>
          {trend.length === 0 ? (
            <div className="flex items-start gap-3 p-4 bg-[var(--color-status-info-bg)] text-[var(--color-status-info)] rounded-lg border border-[var(--color-status-info)]/20">
              <Info className="w-5 h-5 flex-shrink-0 mt-0.5" />
              <p className="text-sm">
                No historical defect trend data available yet. Once regressions are tracked, you will
                see how open issues evolve over time.
              </p>
            </div>
          ) : (
            <div className="flex flex-col gap-2">
              <TrendChart trend={trend} maxValue={maxTrendValue} />
              <p className="text-xs text-[var(--color-content-muted)]">
                {firstTrend ? new Date(firstTrend).toLocaleDateString() : '—'} –{' '}
                {lastTrend ? new Date(lastTrend).toLocaleDateString() : '—'}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

type SeverityRowProps = {
  label: string;
  value: number;
  color?: string;
};

const getTextColorClass = (color?: string): string => {
  switch (color) {
    case 'error':
      return 'text-[var(--color-status-danger)]';
    case 'warning':
      return 'text-[var(--color-status-warning)]';
    default:
      return 'text-[var(--color-content-primary)]';
  }
};

const SeverityRow: React.FC<SeverityRowProps> = ({ label, value, color }) => (
  <div className="flex justify-between items-center">
    <span className="text-sm text-[var(--color-content-secondary)]">
      {label}
    </span>
    <span className={`text-sm ${getTextColorClass(color)}`}>
      {numberFormatter.format(value)}
    </span>
  </div>
);

type TrendChartProps = {
  trend: DefectTrendPoint[];
  maxValue: number;
};

const TrendChart: React.FC<TrendChartProps> = ({ trend, maxValue }) => {
  const safeMax = maxValue > 0 ? maxValue : 1;
  const [hoveredPoint, setHoveredPoint] = React.useState<DefectTrendPoint | null>(null);
  const [tooltipPosition, setTooltipPosition] = React.useState<{ x: number; y: number } | null>(null);

  return (
    <div className="relative">
      <div
        className="flex gap-2 items-end h-32"
        data-testid="defect-trend-chart"
      >
        {trend.map((point) => {
          const heightPercent = Math.round((point.open / safeMax) * 100);

          return (
            <div
              key={point.date}
              data-testid="defect-trend-bar"
              className="flex-1 min-w-[12px] rounded-sm transition-all duration-300 cursor-pointer"
              style={{
                background: 'linear-gradient(180deg, var(--color-accent-500) 0%, var(--color-accent-700) 100%)',
                height: `${Math.max(4, heightPercent)}%`,
              }}
              onMouseEnter={(e) => {
                setHoveredPoint(point);
                const rect = e.currentTarget.getBoundingClientRect();
                setTooltipPosition({ x: rect.left + rect.width / 2, y: rect.top });
              }}
              onMouseLeave={() => {
                setHoveredPoint(null);
                setTooltipPosition(null);
              }}
            />
          );
        })}
      </div>
      {hoveredPoint && tooltipPosition && (
        <div
          className="fixed z-50 bg-[var(--color-surface-overlay)] text-[var(--color-content-primary)] text-xs px-2 py-1 rounded shadow-lg border border-[var(--color-border-default)] -translate-x-1/2 -translate-y-full -mt-2"
          style={{ left: tooltipPosition.x, top: tooltipPosition.y }}
        >
          {numberFormatter.format(hoveredPoint.open)} open on {new Date(hoveredPoint.date).toLocaleDateString()}
        </div>
      )}
    </div>
  );
};

export default DefectTracking;
