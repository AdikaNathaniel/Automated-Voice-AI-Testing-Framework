/**
 * Validator Statistics Page
 *
 * Presents the validator's personal performance metrics, leaderboard standings,
 * and accuracy trend data sourced from the validation Redux slice.
 */

import React, { useEffect, useMemo } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchValidatorStatistics } from '../../store/slices/validationSlice';
import type { RootState, AppDispatch } from '../../store';

/**
 * Format a floating-point accuracy value as a percentage string.
 *
 * @param value - Accuracy value between 0 and 1.
 * @returns Formatted percentage string (e.g., "92% accuracy").
 */
const formatAccuracy = (value: number | undefined | null) => {
  if (value === undefined || value === null || Number.isNaN(value)) {
    return 'N/A';
  }

  return `${Math.round(value * 100)}% accuracy`;
};

/**
 * Convert seconds to mm:ss display for average validation time.
 *
 * @param totalSeconds - Number of seconds.
 * @returns Formatted string (e.g., "00:45 per validation").
 */
const formatAverageTime = (totalSeconds: number | undefined | null) => {
  if (totalSeconds === undefined || totalSeconds === null) {
    return 'N/A';
  }

  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;

  return `${minutes.toString().padStart(2, '0')}:${seconds
    .toString()
    .padStart(2, '0')} per validation`;
};

/**
 * ValidatorStats page component.
 *
 * Renders validator metrics once fetched via Redux thunk.
 */
const ValidatorStats: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();

  const {
    loading,
    error,
    validatorSummary,
    validatorLeaderboard,
    validatorAccuracyTrend,
  } = useSelector((state: RootState) => state.validation);

  useEffect(() => {
    dispatch(fetchValidatorStatistics());
  }, [dispatch]);

  const hasLoadedSummary = !!validatorSummary;
  const personalStats = validatorSummary ?? null;
  const leaderboardEntries = validatorLeaderboard ?? [];
  const accuracyTrend = validatorAccuracyTrend ?? [];

  const approvalsVsRejections = useMemo(() => {
    if (!personalStats) return null;

    return `${personalStats.approvals} approvals · ${personalStats.rejections} rejections`;
  }, [personalStats]);

  if (loading && !hasLoadedSummary) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-8">
        <p className="text-xl text-[var(--color-content-primary)]" data-testid="stats-loading">
          Loading validator statistics...
        </p>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <h1 className="header mb-6">Validator Statistics</h1>

      {error && (
        <div className="bg-[var(--color-status-danger-bg)] border border-[var(--color-status-danger)] rounded-lg p-4 mb-6">
          <p className="text-[var(--color-status-danger)]">{error}</p>
        </div>
      )}

      {!personalStats && (
        <div className="card mb-8">
          <h2 className="text-lg font-semibold mb-2 text-[var(--color-content-primary)]">Statistics unavailable</h2>
          <p className="text-[var(--color-content-secondary)]">
            We were unable to load your validator statistics. Please try again
            shortly.
          </p>
        </div>
      )}

      {personalStats && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="card">
            <h2 className="text-lg font-semibold mb-4 text-[var(--color-content-primary)]">Personal Performance</h2>
            <p className="text-4xl font-bold mb-2 text-[var(--color-content-primary)]">
              {`${personalStats.completedValidations} validations`}
            </p>
            <p className="text-[var(--color-content-secondary)] mb-4">
              {formatAccuracy(personalStats.accuracy)}
            </p>
            <p className="text-base mb-1 text-[var(--color-content-primary)]">
              {formatAverageTime(personalStats.averageTimeSeconds)}
            </p>
            <p className="text-[var(--color-content-secondary)] mb-2">
              Current streak: {personalStats.currentStreakDays} days
            </p>
            <p className="text-[var(--color-content-secondary)]">
              {approvalsVsRejections}
            </p>
          </div>

          <div className="card">
            <h2 className="text-lg font-semibold mb-4 text-[var(--color-content-primary)]">Leaderboard</h2>
            {leaderboardEntries.length === 0 ? (
              <p className="text-[var(--color-content-secondary)]">
                No leaderboard data available
              </p>
            ) : (
              <div className="space-y-3">
                {leaderboardEntries.map((entry) => (
                  <div key={entry.validatorId}>
                    <div className="pb-3">
                      <p className="font-medium text-[var(--color-content-primary)]">
                        {entry.rank}. {entry.displayName}
                      </p>
                      <p className="text-sm text-[var(--color-content-secondary)]">
                        {entry.completedValidations} validations · {formatAccuracy(
                          entry.accuracy
                        )}
                      </p>
                    </div>
                    <hr className="border-[var(--color-border-default)]" />
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="card">
            <h2 className="text-lg font-semibold mb-4 text-[var(--color-content-primary)]">Accuracy Trend</h2>
            {accuracyTrend.length === 0 ? (
              <p className="text-[var(--color-content-secondary)]">
                Accuracy trend data not available
              </p>
            ) : (
              <div className="space-y-3">
                {accuracyTrend.map((point) => (
                  <div key={point.date}>
                    <div className="flex justify-between items-start pb-3">
                      <div>
                        <p className="font-medium text-[var(--color-content-primary)]">{point.date}</p>
                        <p className="text-sm text-[var(--color-content-secondary)]">
                          {formatAccuracy(point.accuracy)}
                        </p>
                      </div>
                      <p className="text-sm text-[var(--color-content-secondary)]">
                        {`${point.validations} validations`}
                      </p>
                    </div>
                    <hr className="border-[var(--color-border-default)]" />
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ValidatorStats;
