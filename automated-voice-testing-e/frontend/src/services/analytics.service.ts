import apiClient from './api';
import type {
  TrendAnalytics,
  TrendAnalyticsFilters,
  TrendDirection,
  TrendGranularity,
  TrendRange,
} from '../types/analytics';

type ApiTrendDirection = TrendDirection;

type ApiPassRateTrendPoint = {
  period_start: string;
  pass_rate_pct: number;
  change_pct: number | null;
  direction: ApiTrendDirection;
  total_executions: number;
};

type ApiDefectTrendPoint = {
  period_start: string;
  detected: number;
  resolved: number;
  net_open: number;
  change_open: number | null;
  direction: ApiTrendDirection;
};

type ApiPerformanceTrendPoint = {
  period_start: string;
  avg_response_time_ms: number;
  change_ms: number | null;
  direction: ApiTrendDirection;
  sample_size: number;
};

type ApiTrendSummary = {
  total_executions: number;
  total_validations: number;
  avg_pass_rate_pct: number;
  avg_response_time_ms: number;
  response_time_samples: number;
};

type ApiTrendAnalyticsResponse = {
  pass_rate: ApiPassRateTrendPoint[];
  defects: ApiDefectTrendPoint[];
  performance: ApiPerformanceTrendPoint[];
  summary?: ApiTrendSummary;
};

const DEFAULT_RANGE: TrendRange = '30d';
const DEFAULT_GRANULARITY: TrendGranularity = 'day';

const RANGE_TO_DAYS: Record<TrendRange, number> = {
  '7d': 7,
  '14d': 14,
  '30d': 30,
  '90d': 90,
};

const toDateString = (value: Date): string => value.toISOString().slice(0, 10);

const calculateStartDate = (endDate: Date, range: TrendRange): Date => {
  const days = RANGE_TO_DAYS[range] ?? RANGE_TO_DAYS[DEFAULT_RANGE];
  const start = new Date(endDate);
  start.setDate(endDate.getDate() - Math.max(days - 1, 0));
  return start;
};

const mapPassRateTrend = (entry: ApiPassRateTrendPoint) => ({
  periodStart: entry.period_start,
  passRatePct: entry.pass_rate_pct,
  changePct: entry.change_pct,
  direction: entry.direction,
  totalExecutions: entry.total_executions,
});

const mapDefectTrend = (entry: ApiDefectTrendPoint) => ({
  periodStart: entry.period_start,
  detected: entry.detected,
  resolved: entry.resolved,
  netOpen: entry.net_open,
  changeOpen: entry.change_open,
  direction: entry.direction,
});

const mapPerformanceTrend = (entry: ApiPerformanceTrendPoint) => ({
  periodStart: entry.period_start,
  avgResponseTimeMs: entry.avg_response_time_ms,
  changeMs: entry.change_ms,
  direction: entry.direction,
  sampleSize: entry.sample_size,
});

export const getTrendAnalytics = async (
  filters: TrendAnalyticsFilters = {}
): Promise<TrendAnalytics> => {
  const now = new Date();
  const range = filters.range ?? DEFAULT_RANGE;
  const granularity = filters.granularity ?? DEFAULT_GRANULARITY;

  const resolvedEndDate = (() => {
    if (filters.endDate) {
      return filters.endDate;
    }
    return toDateString(now);
  })();

  const resolvedStartDate = (() => {
    if (filters.startDate) {
      return filters.startDate;
    }
    const end = filters.endDate ? new Date(filters.endDate) : now;
    return toDateString(calculateStartDate(end, range));
  })();

  try {
    const response = await apiClient.get<ApiTrendAnalyticsResponse>('/analytics/trends', {
      params: {
        start_date: resolvedStartDate,
        end_date: resolvedEndDate,
        granularity,
      },
      timeout: 30000,
    });

    const data = response.data;

    if (!data || typeof data !== 'object') {
      console.error('[Analytics] Invalid response data:', data);
      throw new Error('Invalid analytics response format');
    }

    return {
      passRate: Array.isArray(data.pass_rate) ? data.pass_rate.map(mapPassRateTrend) : [],
      defects: Array.isArray(data.defects) ? data.defects.map(mapDefectTrend) : [],
      performance: Array.isArray(data.performance) ? data.performance.map(mapPerformanceTrend) : [],
      summary: data.summary ? {
        totalExecutions: data.summary.total_executions ?? 0,
        totalValidations: data.summary.total_validations ?? 0,
        avgPassRatePct: data.summary.avg_pass_rate_pct ?? 0,
        avgResponseTimeMs: data.summary.avg_response_time_ms ?? 0,
        responseTimeSamples: data.summary.response_time_samples ?? 0,
      } : undefined,
    };
  } catch (error) {
    console.error('[Analytics] Failed to fetch trend analytics:', error);
    throw error;
  }
};

export default {
  getTrendAnalytics,
};
