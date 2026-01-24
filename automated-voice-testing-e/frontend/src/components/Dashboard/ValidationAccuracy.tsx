import React from 'react';
import { AlertCircle } from 'lucide-react';

export type ValidationAccuracyData = {
  overallAccuracyPct: number;
  totalValidations: number;
  humanReviews: number;
  agreements: number;
  disagreements: number;
  aiOverturned: number;
  timeSavedHours?: number;
};

export type ValidationAccuracyProps = {
  data: ValidationAccuracyData;
  loading?: boolean;
  error?: string | null;
  onRetry?: () => void;
};

const percentFormatter = new Intl.NumberFormat(undefined, {
  minimumFractionDigits: 1,
  maximumFractionDigits: 1,
});

const integerFormatter = new Intl.NumberFormat();

const timeSavedFormatter = new Intl.NumberFormat(undefined, {
  minimumFractionDigits: 0,
  maximumFractionDigits: 1,
});

const ValidationAccuracy: React.FC<ValidationAccuracyProps> = ({
  data,
  loading = false,
  error = null,
  onRetry,
}) => {
  if (loading) {
    return (
      <div className="card">
        <div
          className="flex items-center justify-center py-4"
          data-testid="validation-accuracy-loading"
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

  const {
    overallAccuracyPct,
    totalValidations,
    humanReviews,
    agreements,
    disagreements,
    aiOverturned,
    timeSavedHours
  } = data;
  const accuracyDisplay = `${percentFormatter.format(overallAccuracyPct)}%`;
  const validationsDisplay = integerFormatter.format(totalValidations);
  const humanReviewsDisplay = integerFormatter.format(humanReviews);
  const agreementsDisplay = integerFormatter.format(agreements);
  const disagreementsDisplay = integerFormatter.format(disagreements);
  const timeSavedDisplay =
    typeof timeSavedHours === 'number'
      ? `${timeSavedFormatter.format(timeSavedHours)} hrs`
      : null;

  return (
    <div className="card h-full">
      <div className="flex flex-col gap-4">
        <h2 className="card-title">
          Validation Accuracy Metrics
        </h2>

        <div className="flex flex-col gap-2">
          <p className="text-xs text-[var(--color-content-muted)]">
            Last 7 days rolling average
          </p>
          <p className="text-3xl font-bold text-[var(--color-content-primary)]" data-testid="validation-accuracy-value">
            {accuracyDisplay}
          </p>
          <p className="text-sm text-[var(--color-content-secondary)]">
            AI decisions align with human validators at a high confidence level.
          </p>
        </div>

        <div className="border-t border-[var(--color-border-subtle)]"></div>

        <div className="flex flex-col gap-3">
          <MetricRow label="Total validations" value={validationsDisplay} />
          <MetricRow label="Human reviews" value={humanReviewsDisplay} />
          <MetricRow label="Agreements" value={agreementsDisplay} />
          <MetricRow label="Disagreements" value={disagreementsDisplay} />
          {timeSavedDisplay ? (
            <MetricRow label="Time saved" value={timeSavedDisplay} />
          ) : null}
        </div>
      </div>
    </div>
  );
};

type MetricRowProps = {
  label: string;
  value: React.ReactNode;
};

const MetricRow: React.FC<MetricRowProps> = ({ label, value }) => (
  <div className="flex justify-between items-center">
    <span className="text-sm text-[var(--color-content-secondary)]">
      {label}
    </span>
    <span className="text-sm text-[var(--color-content-primary)]">{value}</span>
  </div>
);

export default ValidationAccuracy;
