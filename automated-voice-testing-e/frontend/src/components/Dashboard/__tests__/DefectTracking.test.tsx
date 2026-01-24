import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import DefectTracking, { DefectTrackingProps } from '../DefectTracking';

const baseProps: DefectTrackingProps = {
  summary: {
    open: 24,
    critical: 6,
    high: 8,
    medium: 7,
    low: 3,
  },
  trend: [
    { date: '2024-01-01', open: 18 },
    { date: '2024-01-02', open: 21 },
    { date: '2024-01-03', open: 24 },
  ],
  loading: false,
  error: null,
};

describe('DefectTracking component', () => {
  it('renders severity summary and trend bars', () => {
    render(<DefectTracking {...baseProps} />);

    expect(
      screen.getByRole('heading', { name: /Defect Detection & Tracking/i })
    ).toBeInTheDocument();

    expect(screen.getByText(/Open Issues/i).nextSibling?.textContent).toContain('24');
    expect(screen.getByText(/Critical/i).nextSibling?.textContent).toContain('6');
    expect(screen.getByText(/High/i).nextSibling?.textContent).toContain('8');
    expect(screen.getByText(/Medium/i).nextSibling?.textContent).toContain('7');
    expect(screen.getByText(/Low/i).nextSibling?.textContent).toContain('3');

    const chart = screen.getByTestId('defect-trend-chart');
    expect(chart).toBeInTheDocument();
    expect(screen.getAllByTestId('defect-trend-bar')).toHaveLength(3);
  });

  it('shows informative fallback when no trend data exists', () => {
    render(<DefectTracking {...baseProps} trend={[]} />);

    expect(
      screen.getByText(/No historical defect trend data available yet/i)
    ).toBeInTheDocument();
  });

  it('renders loading placeholder and error state with retry', () => {
    const onRetry = vi.fn();
    const { rerender } = render(
      <DefectTracking {...baseProps} loading error={null} onRetry={onRetry} />
    );

    expect(screen.getByTestId('defect-tracking-loading')).toBeInTheDocument();

    rerender(
      <DefectTracking
        {...baseProps}
        loading={false}
        error="Unable to load defects"
        onRetry={onRetry}
      />
    );

    expect(screen.getByText(/Unable to load defects/i)).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /Retry/i }));
    expect(onRetry).toHaveBeenCalledTimes(1);
  });
});
