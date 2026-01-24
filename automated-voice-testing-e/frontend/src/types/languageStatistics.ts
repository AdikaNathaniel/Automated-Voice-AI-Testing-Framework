/**
 * Language statistics domain types.
 *
 * Mirrors the backend `/v1/languages/stats` response while exposing
 * camelCased properties for frontend consumption.
 */

export interface LanguageCoverageSummary {
  /** Number of test case variations available for the language. */
  testCases: number;
}

export interface LanguageStatisticsEntry {
  /** Language code (e.g., en-US). */
  languageCode: string;

  /** Display name of the language. */
  languageName: string;

  /** Native name of the language (if available). */
  nativeName: string;

  /** Summary of coverage metrics for the language. */
  coverage: LanguageCoverageSummary;

  /** Average validation pass rate expressed as 0-1 float, null when unavailable. */
  passRate: number | null;

  /** Number of automated executions recorded for the language. */
  executions: number;

  /** Common validation issues flagged for the language. */
  commonIssues: string[];
}

export interface LanguageStatisticsResponse {
  /** Total number of languages returned by the API. */
  totalLanguages: number;

  /** Detailed statistics per language. */
  languages: LanguageStatisticsEntry[];
}
