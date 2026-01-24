import React from 'react';
import { AlertCircle, Info } from 'lucide-react';
import type { TestCoverageEntry } from '../../types/dashboard';

export type TestCoverageProps = {
  coverage: TestCoverageEntry[];
  loading?: boolean;
  error?: string | null;
  onRetry?: () => void;
};

const percentFormatter = new Intl.NumberFormat(undefined, {
  minimumFractionDigits: 0,
  maximumFractionDigits: 1,
});

const TestCoverage: React.FC<TestCoverageProps> = ({
  coverage,
  loading = false,
  error = null,
  onRetry,
}) => {
  if (loading) {
    return (
      <div className="card">
        <div
          className="flex items-center justify-center py-4"
          data-testid="test-coverage-loading"
        >
          <div className="spinner"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <div className="flex items-start gap-3 p-4 bg-[var(--color-status-danger-bg)] text-[var(--color-status-danger)] rounded-lg border border-[var(--color-status-danger)]/20">
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="text-sm">{error}</p>
          </div>
          {onRetry && (
            <button
              onClick={onRetry}
              className="text-sm font-medium text-[var(--color-status-danger)] hover:opacity-80"
            >
              Retry
            </button>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="card h-full">
      <div className="flex flex-col gap-4">
        <h2 className="card-title">
          Test Coverage Analysis
        </h2>

        {coverage.length === 0 ? (
          <div className="flex items-start gap-3 p-4 bg-[var(--color-status-info-bg)] text-[var(--color-status-info)] rounded-lg border border-[var(--color-status-info)]/20">
            <Info className="w-5 h-5 flex-shrink-0 mt-0.5" />
            <p className="text-sm">
              Test coverage analytics will appear once automated coverage data is ingested.
            </p>
          </div>
        ) : (
          <div className="flex flex-col gap-4">
            {coverage.map((entry) => {
              const coverageValue = Math.min(100, Math.max(0, entry.coveragePct));
              const automationValue = Math.min(100, Math.max(0, entry.automatedPct));

              return (
                <div
                  key={entry.area}
                  className="border border-[var(--color-border-default)] rounded-lg p-4"
                  data-testid={`coverage-card-${entry.area}`}
                >
                  <div className="flex flex-col gap-2">
                    <div className="flex justify-between items-center">
                      <h3 className="text-base font-semibold text-[var(--color-content-primary)]">{entry.area}</h3>
                      <span className="text-sm text-[var(--color-content-secondary)]">
                        {percentFormatter.format(coverageValue)}% coverage
                      </span>
                    </div>
                    <div className="progress-bar">
                      <div className="progress-fill" style={{ width: `${coverageValue}%` }}></div>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-[var(--color-content-secondary)]">
                        Automated
                      </span>
                      <span className="text-sm text-[var(--color-content-secondary)]">
                        {percentFormatter.format(automationValue)}% automated
                      </span>
                    </div>
                    <div className="progress-bar">
                      <div
                        className="h-full transition-all duration-300 bg-[var(--color-status-success)] rounded-full"
                        style={{ width: `${automationValue}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default TestCoverage;
