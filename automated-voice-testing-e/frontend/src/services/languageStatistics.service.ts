/**
 * Language statistics service helpers.
 *
 * Wraps requests to the `/v1/languages/stats` endpoint and normalises
 * the response into camelCased fields.
 */

import apiClient from './api';
import type {
  LanguageStatisticsEntry,
  LanguageStatisticsResponse,
} from '../types/languageStatistics';

type ApiLanguageCoverage = {
  test_cases?: number;
};

type ApiLanguageStatistics = {
  language_code: string;
  language_name: string;
  native_name: string;
  coverage?: ApiLanguageCoverage;
  pass_rate: number | null;
  executions: number;
  common_issues?: string[];
};

type ApiLanguageStatisticsResponse = {
  total_languages: number;
  languages: ApiLanguageStatistics[];
};

const toLanguageStatisticsEntry = (
  payload: ApiLanguageStatistics
): LanguageStatisticsEntry => ({
  languageCode: payload.language_code,
  languageName: payload.language_name,
  nativeName: payload.native_name,
  coverage: {
    testCases: payload.coverage?.test_cases ?? 0,
  },
  passRate: payload.pass_rate,
  executions: payload.executions,
  commonIssues: payload.common_issues ?? [],
});

/**
 * Fetch aggregated language coverage statistics.
 */
export const getLanguageStatistics = async (): Promise<LanguageStatisticsResponse> => {
  const response = await apiClient.get<ApiLanguageStatisticsResponse>(
    '/languages/stats'
  );

  return {
    totalLanguages: response.data.total_languages,
    languages: response.data.languages.map(toLanguageStatisticsEntry),
  };
};

export default {
  getLanguageStatistics,
};
