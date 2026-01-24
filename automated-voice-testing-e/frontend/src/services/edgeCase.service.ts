import apiClient from './api'
import type {
  EdgeCase,
  EdgeCaseListParams,
  EdgeCaseListResponse,
  EdgeCaseSearchParams,
  EdgeCaseCreateInput,
  EdgeCaseAnalytics,
  EdgeCaseAnalyticsParams,
} from '../types/edgeCase'

interface EdgeCaseApiResponse {
  id: string
  title: string
  description?: string | null
  scenario_definition: Record<string, unknown>
  tags: string[]
  severity?: string | null
  category?: string | null
  status: string
  script_id?: string | null
  discovered_date?: string | null
  discovered_by?: string | null
  auto_created: boolean
  created_at: string
  updated_at: string
}

interface EdgeCaseListResponseApi {
  total: number
  items: EdgeCaseApiResponse[]
}

interface EdgeCaseCreateRequest {
  title: string
  description?: string | null
  scenario_definition: Record<string, unknown>
  tags: string[]
  severity?: string | null
  category?: string | null
  status?: string | null
  script_id?: string | null
  discovered_date?: string | null
  discovered_by?: string | null
}

const toEdgeCase = (payload: EdgeCaseApiResponse): EdgeCase => ({
  id: payload.id,
  title: payload.title,
  description: payload.description ?? null,
  scenarioDefinition: payload.scenario_definition ?? {},
  tags: payload.tags ?? [],
  severity: payload.severity ?? null,
  category: payload.category ?? null,
  status: payload.status,
  scriptId: payload.script_id ?? null,
  discoveredDate: payload.discovered_date ?? null,
  discoveredBy: payload.discovered_by ?? null,
  autoCreated: payload.auto_created,
  createdAt: payload.created_at,
  updatedAt: payload.updated_at,
})

const buildQueryParams = (params: Record<string, string | string[] | undefined>) => {
  const searchParams = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => {
    if (value === undefined || value === null) {
      return
    }

    if (Array.isArray(value)) {
      value.forEach((entry) => searchParams.append(key, entry))
    } else {
      searchParams.append(key, value)
    }
  })

  return searchParams
}

export const listEdgeCases = async (
  params: EdgeCaseListParams = {}
): Promise<EdgeCaseListResponse> => {
  const { skip = 0, limit = 50, filters = {} } = params

  const query = buildQueryParams({
    skip: String(skip),
    limit: String(limit),
    status: filters.status,
    category: filters.category,
    severity: filters.severity,
    script_id: filters.scriptId,
    discovered_by: filters.discoveredBy,
    pattern_group_id: filters.patternGroupId,
  })

  if (filters.tags && filters.tags.length > 0) {
    filters.tags.forEach((tag) => query.append('tags', tag))
  }

  const response = await apiClient.get<EdgeCaseListResponseApi>(`/edge-cases?${query.toString()}`)
  const items = response.data.items.map(toEdgeCase)
  return {
    total: response.data.total,
    items,
  }
}

export const searchEdgeCases = async (
  params: EdgeCaseSearchParams
): Promise<EdgeCaseListResponse> => {
  const { query: searchTerm, skip = 0, limit = 50, ...filters } = params

  const query = buildQueryParams({
    query: searchTerm,
    skip: String(skip),
    limit: String(limit),
    status: filters.status,
    category: filters.category,
    severity: filters.severity,
    script_id: filters.scriptId,
    discovered_by: filters.discoveredBy,
  })

  if (filters.tags && filters.tags.length > 0) {
    filters.tags.forEach((tag) => query.append('tags', tag))
  }

  const response = await apiClient.get<EdgeCaseListResponseApi>(`/edge-cases/search?${query}`)
  const items = response.data.items.map(toEdgeCase)
  return {
    total: response.data.total,
    items,
  }
}

export const getEdgeCase = async (id: string): Promise<EdgeCase> => {
  const response = await apiClient.get<EdgeCaseApiResponse>(`/edge-cases/${id}`)
  return toEdgeCase(response.data)
}

const toCreateRequest = (input: EdgeCaseCreateInput): EdgeCaseCreateRequest => ({
  title: input.title,
  description: input.description ?? null,
  scenario_definition: input.scenarioDefinition ?? {},
  tags: input.tags ?? [],
  severity: input.severity ?? null,
  category: input.category ?? null,
  status: input.status ?? null,
  script_id: input.scriptId ?? null,
  discovered_date: input.discoveredDate ?? null,
  discovered_by: input.discoveredBy ?? null,
})

export const createEdgeCase = async (input: EdgeCaseCreateInput): Promise<EdgeCase> => {
  const response = await apiClient.post<EdgeCaseApiResponse>(
    '/edge-cases',
    toCreateRequest(input)
  )
  return toEdgeCase(response.data)
}

export interface EdgeCaseUpdateInput {
  title?: string
  description?: string | null
  scenarioDefinition?: Record<string, unknown>
  tags?: string[]
  severity?: string | null
  category?: string | null
  status?: string | null
  scriptId?: string | null
}

export const updateEdgeCase = async (
  id: string,
  input: EdgeCaseUpdateInput
): Promise<EdgeCase> => {
  const payload: Record<string, unknown> = {}

  if (input.title !== undefined) payload.title = input.title
  if (input.description !== undefined) payload.description = input.description
  if (input.scenarioDefinition !== undefined) payload.scenario_definition = input.scenarioDefinition
  if (input.tags !== undefined) payload.tags = input.tags
  if (input.severity !== undefined) payload.severity = input.severity
  if (input.category !== undefined) payload.category = input.category
  if (input.status !== undefined) payload.status = input.status
  if (input.scriptId !== undefined) payload.script_id = input.scriptId

  const response = await apiClient.patch<EdgeCaseApiResponse>(
    `/edge-cases/${id}`,
    payload
  )
  return toEdgeCase(response.data)
}

export interface RerunResult {
  edgeCaseId: string
  executionId: string
  scriptId: string
  scriptName: string
  status: string
  result: string
  passed: boolean
  message: string
}

interface RerunApiResponse {
  edge_case_id: string
  execution_id: string
  script_id: string
  script_name: string
  status: string
  result: string
  passed: boolean
  message: string
}

export const rerunEdgeCaseScenario = async (id: string): Promise<RerunResult> => {
  const response = await apiClient.post<RerunApiResponse>(`/edge-cases/${id}/rerun`)
  return {
    edgeCaseId: response.data.edge_case_id,
    executionId: response.data.execution_id,
    scriptId: response.data.script_id,
    scriptName: response.data.script_name,
    status: response.data.status,
    result: response.data.result,
    passed: response.data.passed,
    message: response.data.message,
  }
}

// ---------------------------------------------------------------------
// Analytics (Phase 5)
// ---------------------------------------------------------------------

interface AnalyticsApiResponse {
  date_range: {
    from: string
    to: string
  }
  summary: {
    total_in_range: number
    total_all_time: number
    active_count: number
    resolved_in_range: number
    critical_active: number
  }
  count_over_time: Array<{
    date: string
    count: number
    cumulative: number
  }>
  category_distribution: Array<{
    category?: string
    count: number
    percentage: number
  }>
  severity_distribution: Array<{
    severity?: string
    count: number
    percentage: number
  }>
  status_distribution: Array<{
    status?: string
    count: number
    percentage: number
  }>
  resolution_metrics: {
    total_created: number
    resolved: number
    active: number
    wont_fix: number
    resolution_rate_percent: number
  }
  top_patterns: Array<{
    id: string
    name: string
    pattern_type?: string
    severity: string
    occurrence_count: number
    linked_edge_cases: number
  }>
  auto_vs_manual: {
    auto_created: number
    manually_created: number
    auto_created_percent: number
    manually_created_percent: number
  }
  trend_comparison?: {
    current_period: {
      from: string
      to: string
      count: number
    }
    previous_period: {
      from: string
      to: string
      count: number
    }
    change: number
    change_percent: number
    trend: string
  }
}

const toAnalytics = (api: AnalyticsApiResponse): EdgeCaseAnalytics => ({
  dateRange: {
    from: api.date_range.from,
    to: api.date_range.to,
  },
  summary: {
    totalInRange: api.summary.total_in_range,
    totalAllTime: api.summary.total_all_time,
    activeCount: api.summary.active_count,
    resolvedInRange: api.summary.resolved_in_range,
    criticalActive: api.summary.critical_active,
  },
  countOverTime: api.count_over_time,
  categoryDistribution: api.category_distribution.map(item => ({
    category: item.category,
    count: item.count,
    percentage: item.percentage,
  })),
  severityDistribution: api.severity_distribution.map(item => ({
    severity: item.severity,
    count: item.count,
    percentage: item.percentage,
  })),
  statusDistribution: api.status_distribution.map(item => ({
    status: item.status,
    count: item.count,
    percentage: item.percentage,
  })),
  resolutionMetrics: {
    totalCreated: api.resolution_metrics.total_created,
    resolved: api.resolution_metrics.resolved,
    active: api.resolution_metrics.active,
    wontFix: api.resolution_metrics.wont_fix,
    resolutionRatePercent: api.resolution_metrics.resolution_rate_percent,
  },
  topPatterns: api.top_patterns.map(pattern => ({
    id: pattern.id,
    name: pattern.name,
    patternType: pattern.pattern_type,
    severity: pattern.severity,
    occurrenceCount: pattern.occurrence_count,
    linkedEdgeCases: pattern.linked_edge_cases,
  })),
  autoVsManual: {
    autoCreated: api.auto_vs_manual.auto_created,
    manuallyCreated: api.auto_vs_manual.manually_created,
    autoCreatedPercent: api.auto_vs_manual.auto_created_percent,
    manuallyCreatedPercent: api.auto_vs_manual.manually_created_percent,
  },
  trendComparison: api.trend_comparison
    ? {
        currentPeriod: {
          from: api.trend_comparison.current_period.from,
          to: api.trend_comparison.current_period.to,
          count: api.trend_comparison.current_period.count,
        },
        previousPeriod: {
          from: api.trend_comparison.previous_period.from,
          to: api.trend_comparison.previous_period.to,
          count: api.trend_comparison.previous_period.count,
        },
        change: api.trend_comparison.change,
        changePercent: api.trend_comparison.change_percent,
        trend: api.trend_comparison.trend as 'up' | 'down' | 'stable',
      }
    : undefined,
})

export const getEdgeCaseAnalytics = async (
  params: EdgeCaseAnalyticsParams = {}
): Promise<EdgeCaseAnalytics> => {
  const query = buildQueryParams({
    date_from: params.dateFrom,
    date_to: params.dateTo,
    include_trend: params.includeTrend !== false ? 'true' : 'false',
  })

  const response = await apiClient.get<AnalyticsApiResponse>(
    `/edge-cases/analytics?${query.toString()}`
  )
  return toAnalytics(response.data)
}
