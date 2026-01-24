import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import TrendChart from '../TrendChart';

const responsiveProps: { current?: unknown } = {};
const lineChartProps: { current?: unknown } = {};
const areaChartProps: { current?: unknown } = {};
const xAxisProps: { current?: unknown } = {};
const yAxisProps: { current?: unknown } = {};
const tooltipProps: { current?: unknown } = {};
const lineProps: { current?: unknown } = {};
const areaProps: { current?: unknown } = {};

const mockResponsiveContainer = vi.fn((props: unknown) => {
  const { children, ...rest } = props;
  responsiveProps.current = rest;
  return <div data-testid="responsive-container">{children}</div>;
});
const mockLineChart = vi.fn((props: unknown) => {
  const { children, ...rest } = props;
  lineChartProps.current = rest;
  return <div data-testid="line-chart">{children}</div>;
});
const mockAreaChart = vi.fn((props: unknown) => {
  const { children, ...rest } = props;
  areaChartProps.current = rest;
  return <div data-testid="area-chart">{children}</div>;
});
const mockXAxis = vi.fn((props: unknown) => {
  xAxisProps.current = props;
  return <div data-testid="x-axis" />;
});
const mockYAxis = vi.fn((props: unknown) => {
  yAxisProps.current = props;
  return <div data-testid="y-axis" />;
});
const mockTooltip = vi.fn((props: unknown) => {
  tooltipProps.current = props;
  return <div data-testid="tooltip" />;
});
const mockCartesianGrid = vi.fn(() => <div data-testid="cartesian-grid" />);
const mockLine = vi.fn((props: unknown) => {
  lineProps.current = props;
  return <div data-testid="line" />;
});
const mockArea = vi.fn((props: unknown) => {
  areaProps.current = props;
  return <div data-testid="area" />;
});

vi.mock('recharts', () => ({
  ResponsiveContainer: (props: unknown) => mockResponsiveContainer(props),
  LineChart: (props: unknown) => mockLineChart(props),
  AreaChart: (props: unknown) => mockAreaChart(props),
  CartesianGrid: (props: unknown) => mockCartesianGrid(props),
  XAxis: (props: unknown) => mockXAxis(props),
  YAxis: (props: unknown) => mockYAxis(props),
  Tooltip: (props: unknown) => mockTooltip(props),
  Line: (props: unknown) => mockLine(props),
  Area: (props: unknown) => mockArea(props),
}));

describe('TrendChart', () => {
  const sampleData = [
    { timestamp: '2024-01-01T00:00:00Z', value: 32 },
    { timestamp: '2024-01-02T00:00:00Z', value: 48 },
    { timestamp: '2024-01-03T00:00:00Z', value: 56 },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
    responsiveProps.current = undefined;
    lineChartProps.current = undefined;
    areaChartProps.current = undefined;
    xAxisProps.current = undefined;
    yAxisProps.current = undefined;
    tooltipProps.current = undefined;
    lineProps.current = undefined;
    areaProps.current = undefined;
  });

  it('renders an empty state when no data is provided', () => {
    render(
      <TrendChart
        title="Execution Trend"
        data={[]}
        xKey="timestamp"
        yKey="value"
      />
    );

    expect(screen.getAllByText(/no data available/i).length).toBeGreaterThan(0);
    expect(mockLineChart).not.toHaveBeenCalled();
    expect(mockAreaChart).not.toHaveBeenCalled();
  });

  it('renders a line chart with default formatters for time-series data', () => {
    render(
      <TrendChart
        title="Execution Trend"
        data={sampleData}
        xKey="timestamp"
        yKey="value"
      />
    );

    expect(mockResponsiveContainer).toHaveBeenCalledWith(
      expect.objectContaining({ width: '100%' }),
    );
    expect(mockLineChart).toHaveBeenCalledTimes(1);
    expect(lineProps.current?.dataKey).toBe('value');
    expect(xAxisProps.current?.dataKey).toBe('timestamp');

    const formattedTick = xAxisProps.current?.tickFormatter?.('2024-01-02T00:00:00Z');
    expect(formattedTick).toMatch(/Jan/i);

    const formattedTooltip = tooltipProps.current?.formatter?.(56);
    expect(formattedTooltip).toBe('56');
  });

  it('renders an area chart when variant is area and applies custom formatters', () => {
    const tickFormatter = vi.fn((value: string) => `Day ${value.slice(8, 10)}`);
    const tooltipFormatter = vi.fn((value: number) => `${value.toFixed(1)} ms`);

    render(
      <TrendChart
        title="Latency Trend"
        data={sampleData}
        xKey="timestamp"
        yKey="value"
        variant="area"
        tickFormatter={tickFormatter}
        tooltipFormatter={tooltipFormatter}
      />
    );

    expect(mockAreaChart).toHaveBeenCalledTimes(1);
    expect(mockLineChart).not.toHaveBeenCalled();

    expect(areaProps.current?.dataKey).toBe('value');
    expect(areaProps.current?.type).toBe('monotone');

    expect(xAxisProps.current?.tickFormatter).toBe(tickFormatter);
    expect(tooltipProps.current?.formatter).toBe(tooltipFormatter);
  });
});
