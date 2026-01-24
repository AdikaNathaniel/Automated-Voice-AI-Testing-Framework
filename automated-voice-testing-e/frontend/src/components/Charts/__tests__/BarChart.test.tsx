import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import BarChartComponent from '../BarChart';
const chartProps: { current?: unknown } = {};
const barsRendered: unknown[] = [];
const xAxisProps: { current?: unknown } = {};
const yAxisProps: { current?: unknown } = {};
const tooltipProps: { current?: unknown } = {};
const legendProps: { current?: unknown } = {};
const mockResponsiveContainer = vi.fn((props: unknown) => {
  const { children, ...rest } = props;
  return (
    <div data-testid="responsive-container" data-props={JSON.stringify(rest)}>
      {children}
    </div>
  );
});
const mockBarChart = vi.fn((props: unknown) => {
  const { children, ...rest } = props;
  chartProps.current = rest;
  return <div data-testid="bar-chart">{children}</div>;
});
const mockBar = vi.fn((props: unknown) => {
  barsRendered.push(props);
  return <div data-testid="bar" />;
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
const mockLegend = vi.fn((props: unknown) => {
  legendProps.current = props;
  return <div data-testid="legend" />;
});
const mockCartesianGrid = vi.fn(() => <div data-testid="grid" />);
vi.mock('recharts', () => ({
  ResponsiveContainer: (props: unknown) => mockResponsiveContainer(props),
  BarChart: (props: unknown) => mockBarChart(props),
  CartesianGrid: (props: unknown) => mockCartesianGrid(props),
  XAxis: (props: unknown) => mockXAxis(props),
  YAxis: (props: unknown) => mockYAxis(props),
  Tooltip: (props: unknown) => mockTooltip(props),
  Legend: (props: unknown) => mockLegend(props),
  Bar: (props: unknown) => mockBar(props),
  Cell: vi.fn(),
}));
describe('BarChart', () => {
  const sampleData = [
    { label: 'Voice Commands', automated: 72, manual: 18 },
    { label: 'Smart Home', automated: 64, manual: 26 },
  ];
  beforeEach(() => {
    vi.clearAllMocks();
    chartProps.current = undefined;
    barsRendered.splice(0, barsRendered.length);
    xAxisProps.current = undefined;
    yAxisProps.current = undefined;
    tooltipProps.current = undefined;
    legendProps.current = undefined;
  });
  it('renders an empty state when data is empty', () => {
    render(
      <BarChartComponent
        title="Coverage"
        data={[]}
        xKey="label"
        bars={[{ dataKey: 'automated', name: 'Automated' }]}
      />
    );
    expect(screen.getAllByText(/no data available/i).length).toBeGreaterThan(0);
    expect(mockBarChart).not.toHaveBeenCalled();
  });
  it('renders vertical bars with default tooltip formatter', () => {
    render(
      <BarChartComponent
        title="Coverage"
        data={sampleData}
        xKey="label"
        bars={[
          { dataKey: 'automated', name: 'Automated' },
          { dataKey: 'manual', name: 'Manual' },
        ]}
      />
    );
    expect(mockBarChart).toHaveBeenCalledTimes(1);
    expect(chartProps.current?.layout).toBeUndefined();
    expect(xAxisProps.current?.dataKey).toBe('label');
    expect(typeof yAxisProps.current?.tickFormatter).toBe('function');
    expect(typeof tooltipProps.current?.formatter).toBe('function');
    expect(barsRendered).toHaveLength(2);
  });
  it('supports horizontal stacked bars with custom formatter', () => {
    const formatter = vi.fn((value: number) => `${value}%`);
    render(
      <BarChartComponent
        title="Automation Mix"
        data={sampleData}
        xKey="label"
        orientation="horizontal"
        stacked
        bars={[
          { dataKey: 'automated', name: 'Automated', color: '#1976d2' },
          { dataKey: 'manual', name: 'Manual', color: '#d32f2f' },
        ]}
        valueFormatter={formatter}
      />
    );
    expect(chartProps.current?.layout).toBe('vertical');
    expect(yAxisProps.current?.dataKey).toBe('label');
    expect(barsRendered).toHaveLength(2);
    barsRendered.forEach((bar) => {
      expect(bar.stackId).toBe('stack');
    });
    expect(tooltipProps.current?.formatter).toBe(formatter);
  });
});
