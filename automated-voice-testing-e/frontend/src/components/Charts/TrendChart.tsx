import React from 'react';
import {
  ResponsiveContainer,
  LineChart,
  AreaChart,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Line,
  Area,
} from 'recharts';

type TrendChartProps<T extends Record<string, unknown>> = {
  title: string;
  data: T[];
  xKey: keyof T;
  yKey: keyof T;
  variant?: 'line' | 'area';
  height?: number;
  strokeColor?: string;
  areaStrokeColor?: string;
  areaFillColor?: string;
  tickFormatter?: (value: unknown) => string;
  labelFormatter?: (label: unknown) => string;
  tooltipFormatter?: (value: number) => string;
  emptyMessage?: string;
  loading?: boolean;
};

const DEFAULT_STROKE = '#1976d2';
const DEFAULT_AREA_STROKE = '#1976d2';
const DEFAULT_AREA_FILL = 'rgba(25, 118, 210, 0.16)';
const DEFAULT_EMPTY_MESSAGE = 'No data available';

const dateTimeFormatter = new Intl.DateTimeFormat(undefined, {
  month: 'short',
  day: 'numeric',
});

const dateTimeWithTimeFormatter = new Intl.DateTimeFormat(undefined, {
  month: 'short',
  day: 'numeric',
  hour: 'numeric',
  minute: '2-digit',
});

const parseDate = (value: unknown): Date | null => {
  if (value instanceof Date) {
    return value;
  }

  if (typeof value === 'number' || typeof value === 'string') {
    const date = new Date(value);
    if (!Number.isNaN(date.getTime())) {
      return date;
    }
  }

  return null;
};

const formatDate = (value: unknown, withTime = false): string => {
  const parsed = parseDate(value);
  if (!parsed) {
    return value != null ? String(value) : '';
  }

  return withTime ? dateTimeWithTimeFormatter.format(parsed) : dateTimeFormatter.format(parsed);
};

const TrendChart = <T extends Record<string, unknown>>({
  title,
  data,
  xKey,
  yKey,
  variant = 'line',
  height = 320,
  strokeColor = DEFAULT_STROKE,
  areaStrokeColor = DEFAULT_AREA_STROKE,
  areaFillColor = DEFAULT_AREA_FILL,
  tickFormatter,
  labelFormatter,
  tooltipFormatter,
  emptyMessage = DEFAULT_EMPTY_MESSAGE,
  loading = false,
}: TrendChartProps<T>) => {
  const hasData = data.length > 0;
  const xDataKey = xKey as string;
  const yDataKey = yKey as string;

  const resolvedTickFormatter = React.useMemo<(value: unknown) => string>(
    () => tickFormatter ?? ((value: unknown) => formatDate(value)),
    [tickFormatter]
  );

  const resolvedLabelFormatter = React.useMemo<(label: unknown) => string>(
    () => labelFormatter ?? ((label: unknown) => formatDate(label, true)),
    [labelFormatter]
  );

  const resolvedTooltipFormatter = React.useMemo<(value: number) => string>(
    () => tooltipFormatter ?? ((value: number) => (Number.isFinite(value) ? value.toString() : String(value))),
    [tooltipFormatter]
  );

  if (loading) {
    return (
      <div
        className="card flex flex-col gap-4 h-full"
        data-testid="trend-chart"
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

  return (
    <div
      className="card flex flex-col gap-4 h-full"
      data-testid="trend-chart"
    >
      <div className="flex flex-col gap-1">
        <h3 className="text-lg font-semibold text-[var(--color-content-primary)]">{title}</h3>
        <p className="text-sm text-[var(--color-content-muted)]">
          {hasData ? 'Showing recent trend' : emptyMessage}
        </p>
      </div>

      {hasData ? (
        <div className="flex-1" style={{ minHeight: height }}>
          <ResponsiveContainer width="100%" height={height}>
            {variant === 'area' ? (
              <AreaChart data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey={xDataKey}
                  tickFormatter={resolvedTickFormatter}
                  minTickGap={16}
                  tickLine={false}
                  axisLine={false}
                />
                <YAxis
                  tickLine={false}
                  axisLine={false}
                  allowDecimals
                  tick={{ fontSize: 12, fill: '#637381' }}
                />
                <Tooltip
                  cursor={{ strokeDasharray: '3 3' }}
                  formatter={resolvedTooltipFormatter}
                  labelFormatter={resolvedLabelFormatter}
                />
                <Area
                  type="monotone"
                  dataKey={yDataKey}
                  stroke={areaStrokeColor}
                  fill={areaFillColor}
                  fillOpacity={0.4}
                  strokeWidth={2}
                  activeDot={{ r: 5 }}
                />
              </AreaChart>
            ) : (
              <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey={xDataKey}
                  tickFormatter={resolvedTickFormatter}
                  minTickGap={16}
                  tickLine={false}
                  axisLine={false}
                />
                <YAxis
                  tickLine={false}
                  axisLine={false}
                  allowDecimals
                  tick={{ fontSize: 12, fill: '#637381' }}
                />
                <Tooltip
                  cursor={{ strokeDasharray: '3 3' }}
                  formatter={resolvedTooltipFormatter}
                  labelFormatter={resolvedLabelFormatter}
                />
                <Line
                  type="monotone"
                  dataKey={yDataKey}
                  stroke={strokeColor}
                  strokeWidth={2}
                  dot={{ r: 3 }}
                  activeDot={{ r: 5 }}
                />
              </LineChart>
            )}
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

export default React.memo(TrendChart) as typeof TrendChart;
