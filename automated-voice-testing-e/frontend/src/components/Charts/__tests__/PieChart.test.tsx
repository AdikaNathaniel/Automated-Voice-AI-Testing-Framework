import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import PieChartComponent from '../PieChart';

const pieProps: { current?: unknown } = {};
const legendProps: { current?: unknown } = {};
const tooltipProps: { current?: unknown } = {};
const cellsRendered: unknown[] = [];

const mockPieChart = vi.fn(({ children, ...rest }: unknown) => {
  pieProps.current = { ...(pieProps.current ?? {}), chartProps: rest };
  return <div data-testid="pie-chart">{children}</div>;
});

const mockPie = vi.fn(({ children, ...rest }: unknown) => {
  pieProps.current = { ...(pieProps.current ?? {}), pieProps: rest };
  return <div data-testid="pie">{children}</div>;
});

const mockResponsiveContainer = vi.fn(({ children, ...rest }: unknown) => (
  <div data-testid="responsive-container" data-props={JSON.stringify(rest)}>
    {children}
  </div>
));

const mockCell = vi.fn((props: unknown) => {
  cellsRendered.push(props);
  return <div data-testid="cell" />;
});

const mockTooltip = vi.fn((props: unknown) => {
  tooltipProps.current = props;
  return <div data-testid="tooltip" />;
});

const mockLegend = vi.fn((props: unknown) => {
  legendProps.current = props;
  return <div data-testid="legend" />;
});

vi.mock('recharts', () => ({
  ResponsiveContainer: (props: unknown) => mockResponsiveContainer(props),
  PieChart: (props: unknown) => mockPieChart(props),
  Pie: (props: unknown) => mockPie(props),
  Cell: (props: unknown) => mockCell(props),
  Tooltip: (props: unknown) => mockTooltip(props),
  Legend: (props: unknown) => mockLegend(props),
}));

describe('PieChart', () => {
  const sampleData = [
    { name: 'Pass', value: 72 },
    { name: 'Fail', value: 18 },
    { name: 'Blocked', value: 10 },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
    pieProps.current = undefined;
    legendProps.current = undefined;
    tooltipProps.current = undefined;
    cellsRendered.splice(0, cellsRendered.length);
  });

  it('renders an empty state when no data is provided', () => {
    render(
      <PieChartComponent
        title="Pass/Fail"
        data={[]}
        dataKey="value"
        nameKey="name"
      />
    );

    expect(screen.getAllByText(/no data available/i).length).toBeGreaterThan(0);
    expect(mockPieChart).not.toHaveBeenCalled();
  });

  it('renders a standard pie chart with legend and tooltip', () => {
    render(
      <PieChartComponent
        title="Pass/Fail"
        data={sampleData}
        dataKey="value"
        nameKey="name"
      />
    );

    expect(mockPieChart).toHaveBeenCalledTimes(1);
    expect(pieProps.current?.pieProps?.outerRadius).toBe(120);
    expect(legendProps.current?.verticalAlign).toBe('bottom');
    expect(tooltipProps.current?.formatter?.(72, 'Pass', sampleData[0])).toBe('72');
    expect(cellsRendered).toHaveLength(sampleData.length);
  });

  it('renders a donut chart with formatted tooltip and custom colors', () => {
    const formatter = vi.fn((value: number, name: string) => `${name}: ${value}%`);
    render(
      <PieChartComponent
        title="Defect Categories"
        data={sampleData}
        dataKey="value"
        nameKey="name"
        variant="donut"
        colors={['#2e7d32', '#d32f2f', '#ff9800']}
        tooltipFormatter={formatter}
      />
    );

    expect(pieProps.current?.pieProps?.innerRadius).toBe(70);
    expect(pieProps.current?.pieProps?.outerRadius).toBe(120);
    expect(tooltipProps.current?.formatter).toBe(formatter);
    expect(tooltipProps.current?.formatter?.(18, 'Fail', sampleData[1])).toBe('Fail: 18%');
    expect(cellsRendered[0]?.fill).toBe('#2e7d32');
    expect(cellsRendered[1]?.fill).toBe('#d32f2f');
    expect(cellsRendered[2]?.fill).toBe('#ff9800');
  });
});
