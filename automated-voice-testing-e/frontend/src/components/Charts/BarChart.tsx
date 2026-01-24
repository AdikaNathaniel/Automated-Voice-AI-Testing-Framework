import React from 'react';
import {
  ResponsiveContainer,
  BarChart as RechartsBarChart,
  Bar,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
} from 'recharts';

type BarDefinition<T> = {
  dataKey: keyof T;
  name?: string;
  color?: string;
  radius?: number | [number, number, number, number];
};

type Orientation = 'vertical' | 'horizontal';

type BarChartProps<T extends Record<string, unknown>> = {
  title: string;
  data: T[];
  xKey: keyof T;
  bars: BarDefinition<T>[];
  orientation?: Orientation;
  stacked?: boolean;
  height?: number;
  showLegend?: boolean;
  valueFormatter?: (value: number, name?: string, entry?: T) => string;
  emptyMessage?: string;
  loading?: boolean;
};

const DEFAULT_EMPTY_MESSAGE = 'No data available';
const STACK_ID = 'stack';

const defaultValueFormatter = (value: number): string =>
  Number.isFinite(value) ? value.toString() : String(value);

const BarChart = <T extends Record<string, unknown>>({
  title,
  data,
  xKey,
  bars,
  orientation = 'vertical',
  stacked = false,
  height = 320,
  showLegend = true,
  valueFormatter = defaultValueFormatter,
  emptyMessage = DEFAULT_EMPTY_MESSAGE,
  loading = false,
}: BarChartProps<T>) => {
  const hasData = data.length > 0;

  if (loading) {
    return (
      <div
        className="card flex flex-col gap-4 h-full"
        data-testid="bar-chart-container"
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
  const isHorizontal = orientation === 'horizontal';
  const xAxisKey = xKey as string;

  const chartLayoutProps = isHorizontal
    ? {
        layout: 'vertical' as const,
      }
    : {};

  const renderBars = () =>
    bars.map((barDef) => (
      <Bar
        key={String(barDef.dataKey)}
        dataKey={barDef.dataKey as string}
        name={barDef.name}
        fill={barDef.color}
        radius={barDef.radius}
        stackId={stacked ? STACK_ID : undefined}
        barSize={24}
      />
    ));

  return (
    <div
      className="card flex flex-col gap-4 h-full"
      data-testid="bar-chart-container"
    >
      <div className="flex flex-col gap-1">
        <h3 className="text-lg font-semibold text-[var(--color-content-primary)]">{title}</h3>
        <p className="text-sm text-[var(--color-content-muted)]">
          {hasData ? 'Distribution overview' : emptyMessage}
        </p>
      </div>

      {hasData ? (
        <div className="flex-1" style={{ minHeight: height }}>
          <ResponsiveContainer width="100%" height={height}>
            <RechartsBarChart data={data} {...chartLayoutProps}>
              <CartesianGrid strokeDasharray="3 3" />
              {isHorizontal ? (
                <>
                  <XAxis
                    type="number"
                    tickFormatter={valueFormatter}
                    allowDecimals
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis
                    type="category"
                    dataKey={xAxisKey}
                    width={120}
                    axisLine={false}
                    tickLine={false}
                  />
                </>
              ) : (
                <>
                  <XAxis
                    dataKey={xAxisKey}
                    axisLine={false}
                    tickLine={false}
                    angle={0}
                  />
                  <YAxis
                    tickFormatter={valueFormatter}
                    allowDecimals
                    axisLine={false}
                    tickLine={false}
                  />
                </>
              )}
              <Tooltip formatter={valueFormatter} />
              {showLegend && <Legend iconType="circle" />}
              {renderBars()}
            </RechartsBarChart>
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

export default React.memo(BarChart) as typeof BarChart;
