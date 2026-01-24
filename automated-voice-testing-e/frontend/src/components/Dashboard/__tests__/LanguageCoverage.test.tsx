import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import LanguageCoverage, { LanguageCoverageProps } from '../LanguageCoverage';

const baseProps: LanguageCoverageProps = {
  languages: [
    { languageCode: 'en-US', testCases: 420, passRatePct: 99.1 },
    { languageCode: 'es-ES', testCases: 210, passRatePct: 78.4 },
    { languageCode: 'ja-JP', testCases: 120, passRatePct: 62.5 },
  ],
  loading: false,
  error: null,
};

describe('LanguageCoverage component', () => {
  it('renders language cards with test counts and pass rate status', () => {
    render(<LanguageCoverage {...baseProps} />);

    expect(screen.getByRole('heading', { name: /Multi-Language Coverage/i })).toBeInTheDocument();

    const englishCard = screen.getByTestId('language-card-en-US');
    expect(englishCard).toHaveTextContent('en-US');
    expect(englishCard).toHaveTextContent('420 test cases');
    expect(englishCard).toHaveTextContent('99.1%');
    expect(englishCard).toHaveTextContent('On Track');

    const spanishCard = screen.getByTestId('language-card-es-ES');
    expect(spanishCard).toHaveTextContent('es-ES');
    expect(spanishCard).toHaveTextContent('210 test cases');
    expect(spanishCard).toHaveTextContent('78.4%');
    expect(spanishCard).toHaveTextContent('At Risk');

    const japaneseCard = screen.getByTestId('language-card-ja-JP');
    expect(japaneseCard).toHaveTextContent('ja-JP');
    expect(japaneseCard).toHaveTextContent('120 test cases');
    expect(japaneseCard).toHaveTextContent('62.5%');
    expect(japaneseCard).toHaveTextContent('Needs Attention');
  });

  it('renders informative empty state when no languages provided', () => {
    render(<LanguageCoverage {...baseProps} languages={[]} />);

    expect(
      screen.getByText(/No language coverage data available yet/i)
    ).toBeInTheDocument();
  });

  it('renders loading indicator while fetching', () => {
    render(<LanguageCoverage {...baseProps} loading languages={[]} />);

    expect(screen.getByTestId('language-coverage-loading')).toBeInTheDocument();
  });

  it('renders error state with retry support', () => {
    const onRetry = vi.fn();
    render(
      <LanguageCoverage
        {...baseProps}
        error="Unable to load language coverage"
        onRetry={onRetry}
      />
    );

    expect(screen.getByText(/Unable to load language coverage/i)).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /Retry/i }));
    expect(onRetry).toHaveBeenCalledTimes(1);
  });
});
