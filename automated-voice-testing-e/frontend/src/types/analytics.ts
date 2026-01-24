export type TrendDirection = 'up' | 'down' | 'flat';

export type PassRateTrendPoint = {
  periodStart: string;
  passRatePct: number;
  changePct: number | null;
  direction: TrendDirection;
  totalExecutions: number;
};

export type DefectTrendPoint = {
  periodStart: string;
  detected: number;
  resolved: number;
  netOpen: number;
  changeOpen: number | null;
  direction: TrendDirection;
};

export type PerformanceTrendPoint = {
  periodStart: string;
  avgResponseTimeMs: number;
  changeMs: number | null;
  direction: TrendDirection;
  sampleSize: number;
};

export type TrendSummary = {
  totalExecutions: number;
  totalValidations: number;
  avgPassRatePct: number;
  avgResponseTimeMs: number;
  responseTimeSamples: number;
};

export type TrendAnalytics = {
  passRate: PassRateTrendPoint[];
  defects: DefectTrendPoint[];
  performance: PerformanceTrendPoint[];
  summary?: TrendSummary;
};

export type TrendRange = '7d' | '14d' | '30d' | '90d';
export type TrendGranularity = 'raw' | 'hour' | 'day';

export type TrendAnalyticsFilters = {
  range?: TrendRange;
  startDate?: string;
  endDate?: string;
  granularity?: TrendGranularity;
};
