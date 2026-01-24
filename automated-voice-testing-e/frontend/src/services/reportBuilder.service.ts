import apiClient from './api';

export interface ReportSection {
  id: string;
  title: string;
  description: string;
  metrics: string[];
}

export interface CustomReportPayload {
  metrics: string[];
  startDate: string;
  endDate: string;
  format: 'pdf' | 'json';
  title?: string;
  description?: string;
}

export interface CustomReportResponse {
  filename: string;
  contentType: string;
  content?: string;
  data?: Record<string, unknown>;
}

export async function fetchReportSections(): Promise<ReportSection[]> {
  /**
   * Placeholder implementation until the backend exposes a dedicated
   * report section catalog endpoint. Returns a curated list of sections
   * aligned with analytics and quality signals already surfaced in the UI.
   */
  return [
    {
      id: 'analytics-overview',
      title: 'Analytics Overview',
      description: 'Key pass/fail metrics and KPI trends.',
      metrics: ['pass_rate', 'defect_density', 'execution_volume'],
    },
    {
      id: 'defect-summary',
      title: 'Defect Summary',
      description: 'Resolved vs open defects with severity breakdown.',
      metrics: ['defects_resolved', 'defects_open', 'critical_defects'],
    },
    {
      id: 'performance-insights',
      title: 'Performance Insights',
      description: 'Response time distribution and bottleneck detection.',
      metrics: ['avg_response_time_ms', 'p95_response_time_ms'],
    },
    {
      id: 'validation-insights',
      title: 'Validation Insights',
      description: 'Validation outcomes by language and validator accuracy.',
      metrics: ['validator_accuracy', 'validation_volume'],
    },
  ];
}

export async function createCustomReport(payload: CustomReportPayload): Promise<CustomReportResponse> {
  const response = await apiClient.post<CustomReportResponse>('/reports/custom', {
    metrics: payload.metrics,
    start_date: payload.startDate,
    end_date: payload.endDate,
    format: payload.format,
    title: payload.title,
    description: payload.description,
  });

  return {
    filename: response.data.filename,
    contentType: response.data.content_type,
    content: response.data.content,
    data: response.data.data,
  };
}
