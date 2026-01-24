/**
 * Language Coverage Widget
 *
 * Displays translation and validation coverage per language, including
 * test case counts, derived coverage percentage, and completion status.
 */

import React, { useEffect, useMemo, useState } from 'react';
import { AlertCircle, Info } from 'lucide-react';
import { getLanguageStatistics } from '../../services/languageStatistics.service';
import type {
  LanguageStatisticsEntry,
  LanguageStatisticsResponse,
} from '../../types/languageStatistics';

type StatusVariant = 'success' | 'warning' | 'error' | 'default';

interface StatusDescriptor {
  label: string;
  color: StatusVariant;
}

const determineStatus = (passRate: number | null): StatusDescriptor => {
  if (passRate === null || Number.isNaN(passRate)) {
    return { label: 'No Data', color: 'default' };
  }

  if (passRate >= 0.85) {
    return { label: 'On Track', color: 'success' };
  }

  if (passRate >= 0.7) {
    return { label: 'At Risk', color: 'warning' };
  }

  return { label: 'Needs Attention', color: 'error' };
};

const formatCoveragePercent = (value: number) => `${value}%`;

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

const LanguageCoverageWidget: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [languages, setLanguages] = useState<LanguageStatisticsEntry[]>([]);

  useEffect(() => {
    let isMounted = true;

    const fetchCoverage = async () => {
      try {
        setLoading(true);
        setError(null);

        const response: LanguageStatisticsResponse = await getLanguageStatistics();
        if (!isMounted) {
          return;
        }
        setLanguages(response.languages);
      } catch (err: unknown) {
        if (!isMounted) {
          return;
        }
        setError(err?.message ?? 'Failed to load language coverage data.');
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    fetchCoverage();

    return () => {
      isMounted = false;
    };
  }, []);

  const maxTestCases = useMemo(() => {
    return languages.reduce(
      (max, language) => Math.max(max, language.coverage.testCases || 0),
      0
    );
  }, [languages]);

  const rows = useMemo(() => {
    return languages.map((language) => {
      const testCases = language.coverage.testCases || 0;
      const coveragePercent =
        maxTestCases > 0 ? Math.round((testCases / maxTestCases) * 100) : 0;
      const status = determineStatus(language.passRate);

      return {
        ...language,
        testCases,
        coveragePercent,
        status,
      };
    });
  }, [languages, maxTestCases]);

  return (
    <div className="card h-full flex flex-col">
      <h2 className="card-title mb-4">
        Language Coverage
      </h2>

      {loading ? (
        <div
          data-testid="language-coverage-loading"
          className="flex-1 flex items-center justify-center"
        >
          <div className="spinner"></div>
        </div>
      ) : error ? (
        <div className="flex items-start gap-3 p-4 bg-[var(--color-status-danger-bg)] text-[var(--color-status-danger)] rounded-lg border border-[var(--color-status-danger)]">
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <p className="text-sm">{error}</p>
        </div>
      ) : rows.length === 0 ? (
        <div className="flex items-start gap-3 p-4 bg-[var(--color-status-info-bg)] text-[var(--color-status-info)] rounded-lg border border-[var(--color-status-info)]">
          <Info className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <p className="text-sm">
            No language coverage data available yet. Once translations are added,
            progress will appear here automatically.
          </p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full" aria-label="Language coverage table">
            <thead>
              <tr className="border-b border-[var(--color-border-default)]">
                <th className="text-left py-2 px-3 text-sm font-semibold text-[var(--color-content-primary)]">Language</th>
                <th className="text-right py-2 px-3 text-sm font-semibold text-[var(--color-content-primary)]">Test Cases</th>
                <th className="text-right py-2 px-3 text-sm font-semibold text-[var(--color-content-primary)]">Coverage</th>
                <th className="text-right py-2 px-3 text-sm font-semibold text-[var(--color-content-primary)]">Status</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((language) => (
                <tr
                  key={language.languageCode}
                  className="border-b border-[var(--color-border-subtle)] hover:bg-[var(--color-interactive-hover)] transition-colors"
                >
                  <td className="py-3 px-3">
                    <span className="text-sm font-medium text-[var(--color-content-primary)] block">
                      {language.languageName}
                    </span>
                    <span className="text-xs text-[var(--color-content-muted)] block">
                      {language.languageCode}
                    </span>
                  </td>
                  <td className="text-right py-3 px-3 text-sm text-[var(--color-content-primary)]">{language.testCases}</td>
                  <td className="text-right py-3 px-3 text-sm text-[var(--color-content-primary)]">
                    {formatCoveragePercent(language.coveragePercent)}
                  </td>
                  <td className="text-right py-3 px-3">
                    <span className={getBadgeClass(language.status.color)}>
                      {language.status.label}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default LanguageCoverageWidget;
