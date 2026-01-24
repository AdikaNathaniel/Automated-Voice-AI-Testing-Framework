import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import EdgeCaseStatistics, {
  EdgeCaseStatisticsProps,
} from '../EdgeCaseStatistics';

const baseProps: EdgeCaseStatisticsProps = {
  data: {
    totalEdgeCases: 128,
    resolvedCount: 96,
    byCategory: [
      { category: 'Voice Recognition', count: 48 },
      { category: 'Smart Home', count: 32 },
      { category: 'Navigation', count: 16 },
    ],
  },
  loading: false,
  error: null,
};

describe('EdgeCaseStatistics', () => {
  it('renders totals, resolution rate, and category breakdown', () => {
    render(<EdgeCaseStatistics {...baseProps} />);

    expect(
      screen.getByRole('heading', { name: /Edge Case Statistics/i })
    ).toBeInTheDocument();

    expect(screen.getByTestId('edge-case-total').textContent).toContain('128');
    expect(screen.getByTestId('edge-case-resolved').textContent).toContain('96');
    expect(screen.getByTestId('edge-case-open').textContent).toContain('32');

    const resolutionRate = screen.getByTestId('edge-case-resolution-rate');
    expect(resolutionRate.textContent).toMatch(/75(\.0)?%/);

    expect(screen.getByTestId('edge-case-category-voice-recognition')).toHaveTextContent(
      'Voice Recognition'
    );
    expect(screen.getByTestId('edge-case-category-voice-recognition')).toHaveTextContent('48');
    expect(screen.getByTestId('edge-case-category-smart-home')).toHaveTextContent('32');
    expect(screen.getByTestId('edge-case-category-navigation')).toHaveTextContent('16');
  });

  it('supports empty category states gracefully', () => {
    const emptyProps: EdgeCaseStatisticsProps = {
      ...baseProps,
      data: {
        totalEdgeCases: 0,
        resolvedCount: 0,
        byCategory: [],
      },
    };

    render(<EdgeCaseStatistics {...emptyProps} />);

    expect(screen.getByTestId('edge-case-category-empty')).toHaveTextContent(
      /No categorized edge cases yet/i
    );
    expect(screen.getByTestId('edge-case-resolution-rate').textContent).toContain('0%');
  });

  it('renders loading and error states with retry support', () => {
    const onRetry = vi.fn();
    const { rerender } = render(
      <EdgeCaseStatistics {...baseProps} loading error={null} onRetry={onRetry} />
    );

    expect(screen.getByTestId('edge-case-stats-loading')).toBeInTheDocument();

    rerender(
      <EdgeCaseStatistics
        {...baseProps}
        loading={false}
        error="Unable to load edge case statistics"
        onRetry={onRetry}
      />
    );

    expect(screen.getByText(/Unable to load edge case statistics/i)).toBeInTheDocument();

    const retryButton = screen.getByRole('button', { name: /Retry/i });
    fireEvent.click(retryButton);

    expect(onRetry).toHaveBeenCalledTimes(1);
  });
});
