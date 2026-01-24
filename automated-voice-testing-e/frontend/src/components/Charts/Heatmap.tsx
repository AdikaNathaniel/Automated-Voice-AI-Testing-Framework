import React from 'react';
import {
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  CartesianGrid,
  XAxis,
  YAxis,
  ZAxis,
  Tooltip,
  Cell,
} from 'recharts';

type HeatmapProps<T extends Record<string, unknown>> = {
  title: string;
  data: T[];
  xKey: keyof T;
  yKey: keyof T;
  valueKey: keyof T;
  height?: number;
  colorScale?: string[];
  emptyMessage?: string;
  tooltipFormatter?: (value: number, name: string, entry: T) => string;
};

type ChartPoint<T> = {
  xIndex: number;
  yIndex: number;
  value: number;
  original: T;
};

const DEFAULT_COLORS = ['#e0f2f1', '#b2dfdb', '#80cbc4', '#26a69a', '#00897b', '#00695c'];
const DEFAULT_EMPTY_MESSAGE = 'No data available';

const defaultTooltipFormatter = <T extends Record<string, unknown>>(
  value: number,
  name: string,
  entry: T
): string => (Number.isFinite(value) ? value.toString() : `${name}: ${String(entry)}`);

const Heatmap = <T extends Record<string, unknown>>({
  title,
  data,
  xKey,
  yKey,
  valueKey,
  height = 320,
  colorScale,
  emptyMessage = DEFAULT_EMPTY_MESSAGE,
  tooltipFormatter = defaultTooltipFormatter,
}: HeatmapProps<T>) => {
  const hasData = data.length > 0;

  const xLabels = React.useMemo(
    () =>
      Array.from(
        new Set(
          data.map((item) => {
            const value = item[xKey];
            return value != null ? String(value) : '';
          })
        )
      ),
    [data, xKey]
  );

  const yLabels = React.useMemo(
    () =>
      Array.from(
        new Set(
          data.map((item) => {
            const value = item[yKey];
            return value != null ? String(value) : '';
          })
        )
      ),
    [data, yKey]
  );

  const resolvedColors = React.useMemo(() => {
    if (colorScale && colorScale.length > 0) {
      return colorScale;
    }
    return DEFAULT_COLORS;
  }, [colorScale]);

  const chartData = React.useMemo<ChartPoint<T>[]>(() => {
    return data.map((item) => {
      const xValue = item[xKey];
      const yValue = item[yKey];
      const value = item[valueKey];

      const xIndex = xLabels.indexOf(xValue != null ? String(xValue) : '');
      const yIndex = yLabels.indexOf(yValue != null ? String(yValue) : '');

      return {
        xIndex,
        yIndex,
        value: Number(value),
        original: item,
      };
    });
  }, [data, xKey, yKey, valueKey, xLabels, yLabels]);

  const [minValue, maxValue] = React.useMemo(() => {
    if (!hasData) {
      return [0, 0];
    }

    let min = Infinity;
    let max = -Infinity;

    chartData.forEach((point) => {
      if (Number.isFinite(point.value)) {
        min = Math.min(min, point.value);
        max = Math.max(max, point.value);
      }
    });

    if (min === Infinity || max === -Infinity) {
      return [0, 0];
    }

    return [min, max];
  }, [chartData, hasData]);

  const getColorForValue = React.useCallback(
    (value: number) => {
      if (!Number.isFinite(value)) {
        return resolvedColors[resolvedColors.length - 1];
      }

      if (minValue === maxValue) {
        return resolvedColors[resolvedColors.length - 1];
      }

      const ratio = (value - minValue) / (maxValue - minValue);
      const index = Math.min(
        resolvedColors.length - 1,
        Math.max(0, Math.round(ratio * (resolvedColors.length - 1)))
      );

      return resolvedColors[index];
    },
    [minValue, maxValue, resolvedColors]
  );

  const scatterData = React.useMemo(
    () =>
      chartData.map((point) => ({
        xIndex: point.xIndex,
        yIndex: point.yIndex,
        value: point.value,
        original: point.original,
      })),
    [chartData]
  );

  const xFormatter = React.useCallback(
    (index: number) => xLabels[index] ?? '',
    [xLabels]
  );

  const yFormatter = React.useCallback(
    (index: number) => yLabels[index] ?? '',
    [yLabels]
  );

  return (
    <div
      className="card flex flex-col gap-4 h-full"
      data-testid="heatmap-container"
    >
      <div className="flex flex-col gap-1">
        <h3 className="text-lg font-semibold text-[var(--color-content-primary)]">{title}</h3>
        <p className="text-sm text-[var(--color-content-muted)]">
          {hasData ? 'Coverage distribution' : emptyMessage}
        </p>
      </div>

      {hasData ? (
        <div className="flex-1" style={{ minHeight: height }}>
          <ResponsiveContainer width="100%" height={height}>
            <ScatterChart margin={{ top: 16, right: 24, bottom: 32, left: 24 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                type="number"
                dataKey="xIndex"
                domain={[-0.5, xLabels.length - 0.5]}
                tickFormatter={xFormatter}
                tickLine={false}
                axisLine={false}
              />
              <YAxis
                type="number"
                dataKey="yIndex"
                domain={[-0.5, yLabels.length - 0.5]}
                tickFormatter={yFormatter}
                tickLine={false}
                axisLine={false}
                width={120}
              />
              <ZAxis type="number" dataKey="value" range={[0, 1]} />
              <Tooltip cursor={{ strokeDasharray: '3 3' }} formatter={tooltipFormatter} />
              <Scatter data={scatterData} shape="square">
                {scatterData.map((point, index) => (
                  <Cell
                    key={`${point.xIndex}-${point.yIndex}-${index}`}
                    fill={getColorForValue(point.value)}
                  />
                ))}
              </Scatter>
            </ScatterChart>
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

export default React.memo(Heatmap) as typeof Heatmap;
