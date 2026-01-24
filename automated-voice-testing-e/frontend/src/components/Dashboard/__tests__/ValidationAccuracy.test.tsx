import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import ValidationAccuracy, { ValidationAccuracyProps } from '../ValidationAccuracy';

const baseProps: ValidationAccuracyProps = {
  data: {
    overallAccuracyPct: 99.6,
    totalValidations: 9340,
    humanReviews: 384,
    agreements: 382,
    disagreements: 2,
    aiOverturned: 2,
    timeSavedHours: 812.5,
  },
  loading: false,
  error: null,
};

describe('ValidationAccuracy component', () => {
  it('renders overall accuracy with breakdown metrics', () => {
    render(<ValidationAccuracy {...baseProps} />);

    expect(
      screen.getByRole('heading', { name: /Validation Accuracy Metrics/i })
    ).toBeInTheDocument();

    expect(screen.getByTestId('validation-accuracy-value').textContent).toContain('99.6%');
    expect(screen.getByText(/Total validations/i).nextSibling?.textContent).toContain('9,340');
    expect(screen.getByText(/Human reviews/i).nextSibling?.textContent).toContain('384');
    expect(screen.getByText('Agreements').nextSibling?.textContent).toContain('382');
    expect(screen.getByText('Disagreements').nextSibling?.textContent).toContain('2');
    expect(screen.getByText(/Time saved/i).nextSibling?.textContent).toContain('812.5 hrs');
  });

  it('updates displayed metrics when new data is provided', () => {
    const { rerender } = render(<ValidationAccuracy {...baseProps} />);

    expect(screen.getByText(/Human reviews/i).nextSibling?.textContent).toContain('384');

    const updatedProps: ValidationAccuracyProps = {
      ...baseProps,
      data: {
        overallAccuracyPct: 98.2,
        totalValidations: 12040,
        humanReviews: 512,
        agreements: 502,
        disagreements: 10,
        aiOverturned: 10,
        timeSavedHours: 1024,
      },
    };

    rerender(<ValidationAccuracy {...updatedProps} />);

    expect(screen.getByText(/Human reviews/i).nextSibling?.textContent).toContain('512');
    expect(screen.getByTestId('validation-accuracy-value').textContent).toContain('98.2%');
    expect(screen.getByText('Agreements').nextSibling?.textContent).toContain('502');
    expect(screen.getByText(/Time saved/i).nextSibling?.textContent).toContain('1,024 hrs');
  });

  it('renders loading and error states with retry support', () => {
    const onRetry = vi.fn();
    const { rerender } = render(
      <ValidationAccuracy {...baseProps} loading error={null} onRetry={onRetry} />
    );

    expect(screen.getByTestId('validation-accuracy-loading')).toBeInTheDocument();

    rerender(
      <ValidationAccuracy
        {...baseProps}
        loading={false}
        error="Unable to load accuracy metrics"
        onRetry={onRetry}
      />
    );

    expect(screen.getByText(/Unable to load accuracy metrics/i)).toBeInTheDocument();

    const retryButton = screen.getByRole('button', { name: /Retry/i });
    fireEvent.click(retryButton);

    expect(onRetry).toHaveBeenCalledTimes(1);
  });
});
