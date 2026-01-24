import { beforeEach, describe, expect, it, vi } from 'vitest';
import Analytics from '../Analytics/Analytics';
import { renderWithProviders, screen, waitFor, userEvent } from '../../test/utils';

const mockGetTrendAnalytics = vi.fn();

vi.mock('../../services/analytics.service', () => ({
  getTrendAnalytics: (...args: unknown[]) => mockGetTrendAnalytics(...args),
}));

const createSampleTrendData = ({
  passRatePct = 94.12,
  changePct = 1.72,
  direction = 'up',
  netOpen = 40,
  changeOpen = -2,
  totalExecutions = 138,
  detected = 10,
  resolved = 12,
  performanceMs = 1184.91,
  changeMs = -135.67,
  sampleSize = 298,
}: {
  passRatePct?: number;
  changePct?: number;
  direction?: 'up' | 'down' | 'flat';
  netOpen?: number;
  changeOpen?: number;
  totalExecutions?: number;
  detected?: number;
  resolved?: number;
  performanceMs?: number;
  changeMs?: number;
  sampleSize?: number;
} = {}) => ({
  passRate: [
    {
      periodStart: '2024-01-01T00:00:00.000Z',
      passRatePct: 92.4,
      changePct: -1.2,
      direction: 'down',
      totalExecutions: 120,
    },
    {
      periodStart: '2024-01-02T00:00:00.000Z',
      passRatePct,
      changePct,
      direction,
      totalExecutions,
    },
  ],
  defects: [
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
      detected,
      resolved,
      netOpen,
      changeOpen,
      direction: changeOpen > 0 ? 'up' : changeOpen < 0 ? 'down' : 'flat',
    },
  ],
  performance: [
    {
      periodStart: '2024-01-01T00:00:00.000Z',
      avgResponseTimeMs: 1320.58,
      changeMs: 45.1,
      direction: 'up',
      sampleSize: 312,
    },
    {
      periodStart: '2024-01-02T00:00:00.000Z',
      avgResponseTimeMs: performanceMs,
      changeMs,
      direction: changeMs < 0 ? 'down' : changeMs > 0 ? 'up' : 'flat',
      sampleSize,
    },
  ],
});

describe('Analytics page', () => {
  beforeEach(() => {
    mockGetTrendAnalytics.mockReset();
  });

  it('fetches analytics trends and renders overview with stat cards and charts', async () => {
    const initialData = createSampleTrendData();
    mockGetTrendAnalytics.mockResolvedValue(initialData);

    renderWithProviders(<Analytics />);

    expect(screen.getByText(/loading analytics/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(mockGetTrendAnalytics).toHaveBeenCalledTimes(1);
    });

    expect(mockGetTrendAnalytics).toHaveBeenCalledWith({
      range: '30d',
      granularity: 'day',
    });

    expect(await screen.findByRole('heading', { name: /analytics overview/i })).toBeInTheDocument();

    // Check stat cards are rendered with values
    expect(await screen.findByText('94.1%')).toBeInTheDocument();
    expect(screen.getByText('Pass Rate')).toBeInTheDocument();
    expect(screen.getByText('Open Defects')).toBeInTheDocument();
    expect(screen.getByText('Avg Response Time')).toBeInTheDocument();
    expect(screen.getByText('Total Executions')).toBeInTheDocument();

    // Check chart cards are rendered
    expect(screen.getByText('Pass Rate Trend')).toBeInTheDocument();
    expect(screen.getByText('Response Time Trend')).toBeInTheDocument();
    expect(screen.getByText('Defect Trend')).toBeInTheDocument();
    expect(screen.getByText('Open Defect Backlog')).toBeInTheDocument();

    // Check quick links are rendered
    expect(screen.getByText('Edge Case Analytics')).toBeInTheDocument();
    expect(screen.getByText('Validation Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Suite Runs')).toBeInTheDocument();
  });

  it('allows adjusting time range filter', async () => {
    const initialData = createSampleTrendData();
    const fourteenDayData = createSampleTrendData({
      passRatePct: 96.52,
      changePct: 2.4,
      direction: 'up',
      netOpen: 36,
      changeOpen: -4,
      totalExecutions: 162,
      detected: 12,
      resolved: 15,
      performanceMs: 1024.3,
      changeMs: -160.2,
      sampleSize: 320,
    });

    mockGetTrendAnalytics
      .mockResolvedValueOnce(initialData)
      .mockResolvedValueOnce(fourteenDayData);

    const user = userEvent.setup();
    renderWithProviders(<Analytics />);

    await screen.findByText('94.1%');

    await user.click(screen.getByRole('button', { name: /14 days/i }));

    await waitFor(() => {
      expect(mockGetTrendAnalytics).toHaveBeenCalledTimes(2);
    });

    expect(mockGetTrendAnalytics).toHaveBeenNthCalledWith(2, {
      range: '14d',
      granularity: 'day',
    });

    expect(await screen.findByText('96.5%')).toBeInTheDocument();
  });

  it('displays error state and allows retry', async () => {
    mockGetTrendAnalytics.mockRejectedValueOnce(new Error('Network error'));

    renderWithProviders(<Analytics />);

    expect(await screen.findByText('Failed to Load Analytics')).toBeInTheDocument();
    expect(screen.getByText('Network error')).toBeInTheDocument();

    const successData = createSampleTrendData();
    mockGetTrendAnalytics.mockResolvedValueOnce(successData);

    const user = userEvent.setup();
    await user.click(screen.getByRole('button', { name: /retry/i }));

    await waitFor(() => {
      expect(mockGetTrendAnalytics).toHaveBeenCalledTimes(2);
    });

    expect(await screen.findByText('94.1%')).toBeInTheDocument();
  });

  it('shows loading spinner while fetching data', async () => {
    mockGetTrendAnalytics.mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve(createSampleTrendData()), 100))
    );

    renderWithProviders(<Analytics />);

    expect(screen.getByText(/loading analytics/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.queryByText(/loading analytics/i)).not.toBeInTheDocument();
    });

    expect(await screen.findByText('94.1%')).toBeInTheDocument();
  });

  it('shows trend indicators correctly', async () => {
    const dataWithTrends = createSampleTrendData({
      passRatePct: 95.0,
      changePct: 2.5,
      direction: 'up',
      netOpen: 35,
      changeOpen: -5,
      performanceMs: 1000,
      changeMs: -200,
    });
    mockGetTrendAnalytics.mockResolvedValue(dataWithTrends);

    renderWithProviders(<Analytics />);

    await screen.findByText('95.0%');

    // Trend values should be displayed
    expect(screen.getByText('2.5%')).toBeInTheDocument(); // Pass rate trend
    expect(screen.getByText('5')).toBeInTheDocument(); // Defect change
    expect(screen.getByText('200 ms')).toBeInTheDocument(); // Performance change
  });
});
