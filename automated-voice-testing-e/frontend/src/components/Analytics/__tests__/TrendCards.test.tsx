import React from 'react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import PassRateTrendCard from '../PassRateTrendCard';
import DefectTrendCard from '../DefectTrendCard';
import PerformanceTrendCard from '../PerformanceTrendCard';
import type {
  PassRateTrendPoint,
  DefectTrendPoint,
  PerformanceTrendPoint,
} from '../../../types/analytics';

const mockTrendChart = vi.fn();

vi.mock('../../Charts/TrendChart', () => ({
  __esModule: true,
  default: (props: unknown) => {
    mockTrendChart(props);
    return <div data-testid="trend-chart-mock" />;
  },
}));

describe('Analytics trend cards', () => {
  beforeEach(() => {
    mockTrendChart.mockReset();
  });

  describe('PassRateTrendCard', () => {
    const sampleData: PassRateTrendPoint[] = [
      {
        periodStart: '2024-01-01T00:00:00.000Z',
        passRatePct: 92.4,
        changePct: -1.2,
        direction: 'down',
        totalExecutions: 120,
      },
      {
        periodStart: '2024-01-02T00:00:00.000Z',
        passRatePct: 94.12,
        changePct: 1.72,
        direction: 'up',
        totalExecutions: 138,
      },
    ];

    it('renders latest stats and forwards props to TrendChart', () => {
      render(<PassRateTrendCard data={sampleData} />);

      expect(screen.getByRole('heading', { name: /pass rate trend/i })).toBeInTheDocument();
      expect(screen.getByText('Latest Pass Rate: 94.1%')).toBeInTheDocument();
      expect(screen.getByText('Change vs previous: +1.7%')).toBeInTheDocument();
      expect(screen.getByText('Executions (latest): 138')).toBeInTheDocument();

      expect(mockTrendChart).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Pass Rate Trend',
          data: sampleData,
          xKey: 'periodStart',
          yKey: 'passRatePct',
          variant: 'area',
          tooltipFormatter: expect.any(Function),
        })
      );
    });

    it('shows empty state when no data', () => {
      render(<PassRateTrendCard data={[]} />);

      expect(screen.getByText(/no pass rate data available/i)).toBeInTheDocument();
    });
  });

  describe('DefectTrendCard', () => {
    const sampleData: DefectTrendPoint[] = [
      {
        periodStart: '2024-01-01T00:00:00.000Z',
        detected: 14,
        resolved: 8,
        netOpen: 42,
        changeOpen: 2,
        direction: 'up',
      },
      {
        periodStart: '2024-01-02T00:00:00.000Z',
        detected: 10,
        resolved: 12,
        netOpen: 40,
        changeOpen: -2,
        direction: 'down',
      },
    ];

    it('renders backlog summary and passes props to TrendChart', () => {
      render(<DefectTrendCard data={sampleData} />);

      expect(screen.getByRole('heading', { name: /defect backlog trend/i })).toBeInTheDocument();
      expect(screen.getByText('Open Defects: 40')).toBeInTheDocument();
      expect(screen.getByText('Change vs previous: -2')).toBeInTheDocument();
      expect(screen.getByText('Detected vs resolved (latest): 10 / 12')).toBeInTheDocument();

      expect(mockTrendChart).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Defect Backlog Trend',
          data: sampleData,
          xKey: 'periodStart',
          yKey: 'netOpen',
          variant: 'line',
          tooltipFormatter: expect.any(Function),
        })
      );
    });

    it('shows empty state when no data', () => {
      render(<DefectTrendCard data={[]} />);

      expect(screen.getByText(/no defect trend data available/i)).toBeInTheDocument();
    });
  });

  describe('PerformanceTrendCard', () => {
    const sampleData: PerformanceTrendPoint[] = [
      {
        periodStart: '2024-01-01T00:00:00.000Z',
        avgResponseTimeMs: 1320.58,
        changeMs: 45.1,
        direction: 'up',
        sampleSize: 312,
      },
      {
        periodStart: '2024-01-02T00:00:00.000Z',
        avgResponseTimeMs: 1184.91,
        changeMs: -135.67,
        direction: 'down',
        sampleSize: 298,
      },
    ];

    it('renders performance summary and sends props to TrendChart', () => {
      render(<PerformanceTrendCard data={sampleData} />);

      expect(screen.getByRole('heading', { name: /response time trend/i })).toBeInTheDocument();
      expect(screen.getByText('Average Response Time: 1,185 ms')).toBeInTheDocument();
      expect(screen.getByText('Change vs previous: -136 ms')).toBeInTheDocument();
      expect(screen.getByText('Sample size (latest): 298')).toBeInTheDocument();

      expect(mockTrendChart).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Response Time Trend',
          data: sampleData,
          xKey: 'periodStart',
          yKey: 'avgResponseTimeMs',
          variant: 'area',
          tooltipFormatter: expect.any(Function),
        })
      );
    });

    it('shows empty state when no data', () => {
      render(<PerformanceTrendCard data={[]} />);

      expect(screen.getByText(/no performance data available/i)).toBeInTheDocument();
    });
  });
});
