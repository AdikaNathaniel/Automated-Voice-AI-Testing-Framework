export interface EdgeCase {
  id: string
  title: string
  description?: string | null
  scenarioDefinition: Record<string, unknown>
  tags: string[]
  severity?: string | null
  category?: string | null
  status: string
  scriptId?: string | null
  discoveredDate?: string | null
  discoveredBy?: string | null
  autoCreated: boolean
  createdAt: string
  updatedAt: string
}

export interface EdgeCaseListResponse {
  total: number
  items: EdgeCase[]
}

export interface EdgeCaseListFilters {
  status?: string
  category?: string
  severity?: string
  tags?: string[]
  scriptId?: string
  discoveredBy?: string
  patternGroupId?: string
}

export interface EdgeCaseListParams {
  skip?: number
  limit?: number
  filters?: EdgeCaseListFilters
}

export interface EdgeCaseSearchParams extends EdgeCaseListFilters {
  query: string
  skip?: number
  limit?: number
}

export interface EdgeCaseCreateInput {
  title: string
  description?: string | null
  scenarioDefinition: Record<string, unknown>
  tags: string[]
  severity?: string | null
  category?: string | null
  status?: string | null
  scriptId?: string | null
  discoveredDate?: string | null
  discoveredBy?: string | null
}

// ---------------------------------------------------------------------
// Analytics types (Phase 5)
// ---------------------------------------------------------------------

export interface AnalyticsSummary {
  totalInRange: number
  totalAllTime: number
  activeCount: number
  resolvedInRange: number
  criticalActive: number
}

export interface TimeSeriesPoint {
  date: string
  count: number
  cumulative: number
}

export interface DistributionItem {
  category?: string
  severity?: string
  status?: string
  count: number
  percentage: number
}

export interface ResolutionMetrics {
  totalCreated: number
  resolved: number
  active: number
  wontFix: number
  resolutionRatePercent: number
}

export interface TopPattern {
  id: string
  name: string
  patternType?: string
  severity: string
  occurrenceCount: number
  linkedEdgeCases: number
}

export interface AutoVsManual {
  autoCreated: number
  manuallyCreated: number
  autoCreatedPercent: number
  manuallyCreatedPercent: number
}

export interface TrendPeriod {
  from: string
  to: string
  count: number
}

export interface TrendComparison {
  currentPeriod: TrendPeriod
  previousPeriod: TrendPeriod
  change: number
  changePercent: number
  trend: 'up' | 'down' | 'stable'
}

export interface EdgeCaseAnalytics {
  dateRange: {
    from: string
    to: string
  }
  summary: AnalyticsSummary
  countOverTime: TimeSeriesPoint[]
  categoryDistribution: DistributionItem[]
  severityDistribution: DistributionItem[]
  statusDistribution: DistributionItem[]
  resolutionMetrics: ResolutionMetrics
  topPatterns: TopPattern[]
  autoVsManual: AutoVsManual
  trendComparison?: TrendComparison
}

export interface EdgeCaseAnalyticsParams {
  dateFrom?: string
  dateTo?: string
  includeTrend?: boolean
}
