import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import TestCoverage, { TestCoverageProps } from '../TestCoverage';

const baseProps: TestCoverageProps = {
  coverage: [
    { area: 'Voice Commands', coveragePct: 85, automatedPct: 70 },
    { area: 'Smart Home', coveragePct: 72, automatedPct: 61 },
    { area: 'Search', coveragePct: 40, automatedPct: 22 },
  ],
  loading: false,
  error: null,
};

describe('TestCoverage component', () => {
  it('renders coverage cards with progress bars and automation data', () => {
    render(<TestCoverage {...baseProps} />);

    expect(screen.getByRole('heading', { name: /Test Coverage Analysis/i })).toBeInTheDocument();

    const voiceCard = screen.getByTestId('coverage-card-Voice Commands');
    expect(voiceCard).toHaveTextContent('Voice Commands');
    expect(voiceCard).toHaveTextContent('85% coverage');
    expect(voiceCard).toHaveTextContent('70% automated');

    const smartHomeCard = screen.getByTestId('coverage-card-Smart Home');
    expect(smartHomeCard).toHaveTextContent('72% coverage');
    expect(smartHomeCard).toHaveTextContent('61% automated');

    const progressBars = screen.getAllByRole('progressbar');
    expect(progressBars).toHaveLength(6);
  });

  it('shows info fallback when no coverage data is available', () => {
    render(<TestCoverage {...baseProps} coverage={[]} />);

    expect(
      screen.getByText(/Test coverage analytics will appear once automated coverage data is ingested/i)
    ).toBeInTheDocument();
  });

  it('renders loading state and error state with retry support', () => {
    const onRetry = vi.fn();
    const { rerender } = render(
      <TestCoverage {...baseProps} loading error={null} onRetry={onRetry} />
    );

    expect(screen.getByTestId('test-coverage-loading')).toBeInTheDocument();

    rerender(
      <TestCoverage
        {...baseProps}
        loading={false}
        error="Unable to load coverage"
        onRetry={onRetry}
      />
    );

    expect(screen.getByText(/Unable to load coverage/i)).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /Retry/i }));
    expect(onRetry).toHaveBeenCalledTimes(1);
  });
});
