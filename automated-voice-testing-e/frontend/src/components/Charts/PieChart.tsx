import React from 'react';
import {
  ResponsiveContainer,
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
} from 'recharts';

type PieChartVariant = 'pie' | 'donut';

type PieChartProps<T extends Record<string, unknown>> = {
  title: string;
  data: T[];
  dataKey: keyof T;
  nameKey: keyof T;
  variant?: PieChartVariant;
  height?: number;
  innerRadius?: number;
  outerRadius?: number;
  colors?: string[];
  showLegend?: boolean;
  tooltipFormatter?: (value: number, name: string, _entry: T) => string;
  emptyMessage?: string;
  loading?: boolean;
};

const DEFAULT_COLORS = ['#0D47A1', '#1976D2', '#42A5F5', '#64B5F6', '#90CAF9'];
const DEFAULT_EMPTY_MESSAGE = 'No data available';

const defaultTooltipFormatter = (
  value: number,
  name: string
): string => (Number.isFinite(value) ? value.toString() : `${name}: ${String(value)}`);

const PieChart = <T extends Record<string, unknown>>({
  title,
  data,
  dataKey,
  nameKey,
  variant = 'pie',
  height = 320,
  innerRadius,
  outerRadius = 120,
  colors = DEFAULT_COLORS,
  showLegend = true,
  tooltipFormatter = defaultTooltipFormatter,
  emptyMessage = DEFAULT_EMPTY_MESSAGE,
  loading = false,
}: PieChartProps<T>) => {
  const hasData = data.length > 0;

  if (loading) {
    return (
      <div
        className="card flex flex-col gap-4 h-full"
        data-testid="pie-chart-container"
        role="status"
        aria-live="polite"
      >
        <div className="flex flex-col gap-1">
          <h3 className="text-lg font-semibold text-[var(--color-content-primary)]">{title}</h3>
          <p className="text-sm text-[var(--color-content-muted)]">Loading...</p>
        </div>
        <div className="flex-1 flex items-center justify-center" style={{ minHeight: height }}>
          <div className="spinner" aria-label={`Loading ${title}`} />
        </div>
      </div>
    );
  }
  const resolvedInnerRadius = innerRadius ?? (variant === 'donut' ? 70 : 0);
  const pieDataKey = dataKey as string;
  const pieNameKey = nameKey as string;

  return (
    <div
      className="card flex flex-col gap-4 h-full"
      data-testid="pie-chart-container"
    >
      <div className="flex flex-col gap-1">
        <h3 className="text-lg font-semibold text-[var(--color-content-primary)]">{title}</h3>
        <p className="text-sm text-[var(--color-content-muted)]">
          {hasData ? 'Segment distribution' : emptyMessage}
        </p>
      </div>

      {hasData ? (
        <div className="flex-1" style={{ minHeight: height }}>
          <ResponsiveContainer width="100%" height={height}>
            <RechartsPieChart>
              <Pie
                data={data}
                dataKey={pieDataKey}
                nameKey={pieNameKey}
                innerRadius={resolvedInnerRadius}
                outerRadius={outerRadius}
                paddingAngle={4}
                cornerRadius={4}
              >
                {data.map((_entry, index) => (
                  <Cell
                    key={`${String(pieNameKey)}-${String(_entry[pieNameKey])}`}
                    fill={colors[index % colors.length]}
                  />
                ))}
              </Pie>
              <Tooltip formatter={tooltipFormatter} />
              {showLegend && <Legend verticalAlign="bottom" height={36} iconType="circle" />}
            </RechartsPieChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <p className="text-sm text-[var(--color-content-muted)] mt-4">
          {emptyMessage}
        </p>
      )}
    </div>
  );
};

export default React.memo(PieChart) as typeof PieChart;
