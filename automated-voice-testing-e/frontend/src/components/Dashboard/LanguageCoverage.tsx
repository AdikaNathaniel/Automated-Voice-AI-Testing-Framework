import React from 'react';
import { AlertCircle, Info } from 'lucide-react';
import type { LanguageCoverageEntry } from '../../types/dashboard';

type StatusVariant = 'success' | 'warning' | 'error' | 'default';

type StatusDescriptor = {
  label: string;
  color: StatusVariant;
};

const determineStatus = (passRatePct: number): StatusDescriptor => {
  if (Number.isNaN(passRatePct)) {
    return { label: 'No Data', color: 'default' };
  }

  if (passRatePct >= 90) {
    return { label: 'On Track', color: 'success' };
  }

  if (passRatePct >= 70) {
    return { label: 'At Risk', color: 'warning' };
  }

  return { label: 'Needs Attention', color: 'error' };
};

const numberFormatter = new Intl.NumberFormat();

const percentFormatter = new Intl.NumberFormat(undefined, {
  minimumFractionDigits: 1,
  maximumFractionDigits: 1,
});

export type LanguageCoverageProps = {
  languages: LanguageCoverageEntry[];
  loading?: boolean;
  error?: string | null;
  onRetry?: () => void;
};

const getBadgeClass = (color: StatusVariant): string => {
  switch (color) {
    case 'success':
      return 'badge badge-success';
    case 'warning':
      return 'badge badge-warning';
    case 'error':
      return 'badge badge-danger';
    default:
      return 'badge bg-[var(--color-surface-inset)] text-[var(--color-content-secondary)]';
  }
};

const LanguageCoverage: React.FC<LanguageCoverageProps> = ({
  languages,
  loading = false,
  error = null,
  onRetry,
}) => {
  if (loading) {
    return (
      <div className="card">
        <div
          className="flex items-center justify-center py-4"
          data-testid="language-coverage-loading"
        >
          <div className="spinner"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <div className="flex items-start gap-3 p-4 bg-[var(--color-status-danger-bg)] text-[var(--color-status-danger)] rounded-lg border border-[var(--color-status-danger)]">
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

  if (!languages.length) {
    return (
      <div className="card">
        <h2 className="card-title mb-4">
          Multi-Language Coverage
        </h2>
        <div className="flex items-start gap-3 p-4 bg-[var(--color-status-info-bg)] text-[var(--color-status-info)] rounded-lg border border-[var(--color-status-info)]">
          <Info className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <p className="text-sm">
            No language coverage data available yet. Add new translations or validations to see
            coverage progress.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="card h-full">
      <div className="flex flex-col gap-4">
        <h2 className="card-title">
          Multi-Language Coverage
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
          {languages.map((language) => {
            const passRate = Math.max(0, Math.min(100, language.passRatePct));
            const status = determineStatus(passRate);

            return (
              <div
                key={language.languageCode}
                className="border border-[var(--color-border-default)] rounded-lg p-5 h-full"
                data-testid={`language-card-${language.languageCode}`}
              >
                <div className="flex flex-col gap-3">
                  <div className="flex justify-between items-center">
                    <h3 className="text-base font-semibold">{language.languageCode}</h3>
                    <span className={getBadgeClass(status.color)}>{status.label}</span>
                  </div>

                  <div className="flex flex-col gap-1">
                    <p className="text-sm text-[var(--color-content-secondary)]">
                      {numberFormatter.format(language.testCases)} test cases
                    </p>
                    <p className="text-xl font-semibold">
                      {percentFormatter.format(passRate)}%
                    </p>
                  </div>

                  <div className="flex flex-col gap-1">
                    <div className="progress-bar">
                      <div className="progress-fill" style={{ width: `${passRate}%` }}></div>
                    </div>
                    <p className="text-xs text-[var(--color-content-muted)]">
                      Quality score based on validation pass rate
                    </p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default LanguageCoverage;
