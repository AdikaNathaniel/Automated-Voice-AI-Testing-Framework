import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import Heatmap from '../Heatmap';

const responsiveProps: { current?: unknown } = {};
const scatterChartProps: { current?: unknown } = {};
const scatterProps: { current?: unknown } = {};
const xAxisProps: { current?: unknown } = {};
const yAxisProps: { current?: unknown } = {};
const tooltipProps: { current?: unknown } = {};
const cellsRendered: unknown[] = [];

const mockResponsiveContainer = vi.fn((props: unknown) => {
  const { children, ...rest } = props;
  responsiveProps.current = rest;
  return (
    <div data-testid="responsive-container">
      {children}
    </div>
  );
});

const mockScatterChart = vi.fn((props: unknown) => {
  const { children, ...rest } = props;
  scatterChartProps.current = rest;
  return <div data-testid="scatter-chart">{children}</div>;
});

const mockXAxis = vi.fn((props: unknown) => {
  xAxisProps.current = props;
  return <div data-testid="x-axis" />;
});

const mockYAxis = vi.fn((props: unknown) => {
  yAxisProps.current = props;
  return <div data-testid="y-axis" />;
});

const mockZAxis = vi.fn((props: unknown) => <div data-testid="z-axis" data-props={JSON.stringify(props)} />);

const mockTooltip = vi.fn((props: unknown) => {
  tooltipProps.current = props;
  return <div data-testid="tooltip" />;
});

const mockScatter = vi.fn((props: unknown) => {
  scatterProps.current = props;
  return (
    <div data-testid="scatter">
      {props.children}
    </div>
  );
});

const mockCell = vi.fn((props: unknown) => {
  cellsRendered.push(props);
  return <div data-testid="cell" />;
});

const mockCartesianGrid = vi.fn(() => <div data-testid="grid" />);

vi.mock('recharts', () => ({
  ResponsiveContainer: (props: unknown) => mockResponsiveContainer(props),
  ScatterChart: (props: unknown) => mockScatterChart(props),
  CartesianGrid: (props: unknown) => mockCartesianGrid(props),
  XAxis: (props: unknown) => mockXAxis(props),
  YAxis: (props: unknown) => mockYAxis(props),
  ZAxis: (props: unknown) => mockZAxis(props),
  Tooltip: (props: unknown) => mockTooltip(props),
  Scatter: (props: unknown) => mockScatter(props),
  Cell: (props: unknown) => mockCell(props),
}));

describe('Heatmap', () => {
  const sampleData = [
    { feature: 'Login', suite: 'Smoke', coverage: 92 },
    { feature: 'Login', suite: 'Regression', coverage: 75 },
    { feature: 'Billing', suite: 'Smoke', coverage: 60 },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
    responsiveProps.current = undefined;
    scatterChartProps.current = undefined;
    scatterProps.current = undefined;
    xAxisProps.current = undefined;
    yAxisProps.current = undefined;
    tooltipProps.current = undefined;
    cellsRendered.splice(0, cellsRendered.length);
  });

  it('renders an empty state when no data is provided', () => {
    render(
      <Heatmap
        title="Coverage by Feature"
        data={[]}
        xKey="suite"
        yKey="feature"
        valueKey="coverage"
      />
    );

    expect(screen.getAllByText(/no data available/i).length).toBeGreaterThan(0);
    expect(mockScatterChart).not.toHaveBeenCalled();
  });

  it('renders a heatmap with categorical axes and mapped cells', () => {
    render(
      <Heatmap
        title="Coverage by Feature"
        data={sampleData}
        xKey="suite"
        yKey="feature"
        valueKey="coverage"
      />
    );

    expect(mockScatterChart).toHaveBeenCalledTimes(1);
    expect(scatterProps.current?.data).toHaveLength(sampleData.length);

    const xFormatter = xAxisProps.current?.tickFormatter;
    const yFormatter = yAxisProps.current?.tickFormatter;
    expect(typeof xFormatter).toBe('function');
    expect(typeof yFormatter).toBe('function');

    expect(xFormatter?.(0)).toBe('Smoke');
    expect(xFormatter?.(1)).toBe('Regression');
    expect(yFormatter?.(0)).toBe('Login');
    expect(yFormatter?.(1)).toBe('Billing');

    expect(cellsRendered).toHaveLength(sampleData.length);
  });

  it('applies custom color scale and tooltip formatter for intensity values', () => {
    const formatter = vi.fn((value: number, name: string) => `${name}: ${value}%`);

    render(
      <Heatmap
        title="Coverage by Feature"
        data={[
          { feature: 'Auth', suite: 'Smoke', coverage: 40 },
          { feature: 'Auth', suite: 'Regression', coverage: 80 },
        ]}
        xKey="suite"
        yKey="feature"
        valueKey="coverage"
        colorScale={['#e0f7fa', '#006064']}
        tooltipFormatter={formatter}
      />
    );

    expect(tooltipProps.current?.formatter).toBe(formatter);
    expect(cellsRendered[0]?.fill).toBe('#e0f7fa');
    expect(cellsRendered[1]?.fill).toBe('#006064');
  });
});
