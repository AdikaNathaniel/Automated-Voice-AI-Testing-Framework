import React, { useEffect, useState, useMemo, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Bug,
  Zap,
  Activity,
  CheckCircle2,
  XCircle,
  RefreshCw,
  ArrowRight,
  BarChart3,
  Clock,
  Target,
} from 'lucide-react';
import { getTrendAnalytics } from '../../services/analytics.service';
import { StatCard } from '../../components/common';
import type {
  TrendAnalytics,
  TrendAnalyticsFilters,
  PassRateTrendPoint,
  DefectTrendPoint,
  PerformanceTrendPoint,
  TrendDirection,
} from '../../types/analytics';

type TimeRange = '7d' | '14d' | '30d' | '90d';

// Chart color mapping to semantic tokens
const chartColorMap: Record<string, string> = {
  green: 'var(--color-status-success)',
  yellow: 'var(--color-status-warning)',
  red: 'var(--color-status-danger)',
  blue: 'var(--color-status-info)',
};

const TIME_RANGES: Array<{ value: TimeRange; label: string }> = [
  { value: '7d', label: '7 Days' },
  { value: '14d', label: '14 Days' },
  { value: '30d', label: '30 Days' },
  { value: '90d', label: '90 Days' },
];

const formatPercentage = (value: number): string => `${value.toFixed(1)}%`;
const formatMilliseconds = (value: number): string => `${Math.round(value)} ms`;
const formatInteger = (value: number): string =>
  new Intl.NumberFormat().format(Math.round(value));

const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
  });
};

interface TrendChartProps<T> {
  data: T[];
  getValue: (item: T) => number;
  getLabel: (item: T) => string;
  formatValue: (value: number) => string;
  color: string;
  height?: number;
}

function TrendLineChart<T>({
  data,
  getValue,
  getLabel,
  formatValue,
  color,
  height = 200,
}: TrendChartProps<T>) {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

  // Memoize expensive chart calculations
  const chartData = useMemo(() => {
    if (data.length === 0) return null;

    const values = data.map(getValue);
    const minValue = Math.min(...values);
    const maxValue = Math.max(...values);
    const range = maxValue - minValue || 1;

    const displayData = data.length > 20
      ? data.filter((_, i, arr) => i % Math.ceil(arr.length / 20) === 0 || i === arr.length - 1)
      : data;

    const points = displayData.map((item, index) => {
      const x = (index / (displayData.length - 1 || 1)) * 100;
      const y = ((getValue(item) - minValue) / range) * 100;
      return { x, y: 100 - y, item, value: getValue(item), label: getLabel(item) };
    });

    const pathD = points
      .map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`)
      .join(' ');

    const areaD = `${pathD} L 100 100 L 0 100 Z`;

    const xLabels = displayData
      .filter((_, i) => i % Math.ceil(displayData.length / 5) === 0)
      .map((item) => formatDate(getLabel(item)));

    return { points, pathD, areaD, xLabels, minValue, maxValue };
  }, [data, getValue, getLabel]);

  if (!chartData) {
    return (
      <div
        className="flex items-center justify-center text-[var(--color-content-muted)]"
        style={{ height }}
      >
        No data available
      </div>
    );
  }

  const { points, pathD, areaD, xLabels, minValue, maxValue } = chartData;

  return (
    <div className="relative" style={{ height }}>
      {/* Y-axis labels */}
      <div className="absolute left-0 top-0 bottom-6 w-12 flex flex-col justify-between text-xs text-[var(--color-content-muted)] pr-2">
        <span className="text-right">{formatValue(maxValue)}</span>
        <span className="text-right">{formatValue((maxValue + minValue) / 2)}</span>
        <span className="text-right">{formatValue(minValue)}</span>
      </div>

      {/* Chart area */}
      <div className="ml-14 relative h-full">
        <svg
          viewBox="0 0 100 100"
          preserveAspectRatio="none"
          className="w-full h-full"
          style={{ height: height - 24 }}
        >
          <defs>
            <linearGradient id={`gradient-${color}`} x1="0" x2="0" y1="0" y2="1">
              <stop offset="0%" stopColor={chartColorMap[color]} stopOpacity="0.3" />
              <stop offset="100%" stopColor={chartColorMap[color]} stopOpacity="0.05" />
            </linearGradient>
          </defs>
          {/* Grid lines */}
          <line x1="0" y1="50" x2="100" y2="50" stroke="currentColor" strokeOpacity="0.1" strokeWidth="0.2" vectorEffect="non-scaling-stroke" />
          <path
            d={areaD}
            fill={`url(#gradient-${color})`}
          />
          <path
            d={pathD}
            fill="none"
            stroke={chartColorMap[color] || 'currentColor'}
            strokeWidth="0.5"
            vectorEffect="non-scaling-stroke"
          />
        </svg>

        {/* Interactive overlay with hover points */}
        <div className="absolute inset-0" style={{ height: height - 24 }}>
          {points.map((point, index) => (
            <div
              key={index}
              className="absolute transform -translate-x-1/2 -translate-y-1/2 group cursor-pointer"
              style={{
                left: `${point.x}%`,
                top: `${point.y}%`,
              }}
              onMouseEnter={() => setHoveredIndex(index)}
              onMouseLeave={() => setHoveredIndex(null)}
            >
              {/* Hover target area */}
              <div className="w-6 h-6 rounded-full" />
              {/* Visible point */}
              <div
                className={`absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-2 h-2 rounded-full transition-transform ${hoveredIndex === index ? 'scale-150' : ''}`}
                style={{ backgroundColor: chartColorMap[color] }}
              />
              {/* Tooltip */}
              {hoveredIndex === index && (
                <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 bg-[var(--color-surface-overlay)] text-[var(--color-content-primary)] text-xs px-2 py-1 rounded whitespace-nowrap z-20 shadow-lg border border-[var(--color-border-default)]">
                  <div className="font-medium">{formatValue(point.value)}</div>
                  <div className="text-[var(--color-content-muted)] text-[10px]">{formatDate(point.label)}</div>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* X-axis labels */}
        <div className="flex justify-between text-xs text-[var(--color-content-muted)] pt-1">
          {xLabels.map((label, i) => (
            <span key={i}>{label}</span>
          ))}
        </div>
      </div>
    </div>
  );
}

interface BarChartProps {
  data: Array<{ label: string; value: number; secondaryValue?: number }>;
  formatValue: (value: number) => string;
  primaryColor: string;
  secondaryColor?: string;
  height?: number;
}

const SimpleBarChart: React.FC<BarChartProps> = ({
  data,
  formatValue,
  primaryColor,
  secondaryColor,
  height = 200,
}) => {
  // Memoize expensive bar chart calculations
  const chartData = useMemo(() => {
    if (data.length === 0) return null;

    const maxValue = Math.max(
      ...data.flatMap((d) => [d.value, d.secondaryValue ?? 0]),
      1 // Ensure at least 1 for the y-axis
    );

    const displayData = data.length > 15
      ? data.filter((_, i, arr) => i % Math.ceil(arr.length / 15) === 0 || i === arr.length - 1)
      : data;

    const labelInterval = Math.ceil(displayData.length / 7);

    return { maxValue, displayData, labelInterval };
  }, [data]);

  if (!chartData) {
    return (
      <div
        className="flex items-center justify-center text-[var(--color-content-muted)]"
        style={{ height }}
      >
        No data available
      </div>
    );
  }

  const { maxValue, displayData, labelInterval } = chartData;

  const barAreaHeight = height - 24; // Reserve 24px for x-axis labels

  return (
    <div className="relative" style={{ height }}>
      {/* Y-axis labels */}
      <div className="absolute left-0 top-0 w-8 flex flex-col justify-between text-xs text-[var(--color-content-muted)] pr-1" style={{ height: barAreaHeight }}>
        <span className="text-right">{formatValue(maxValue)}</span>
        <span className="text-right">{formatValue(maxValue / 2)}</span>
        <span className="text-right">0</span>
      </div>

      {/* Chart area - separate bar area and label area for consistent positioning */}
      <div className="ml-10">
        {/* Bar area with fixed height */}
        <div className="flex items-end gap-1" style={{ height: barAreaHeight }}>
          {displayData.map((item, index) => (
            <div key={index} className="flex-1 flex gap-0.5 items-end h-full group relative">
              {/* Tooltip */}
              <div className="absolute -top-2 left-1/2 -translate-x-1/2 bg-[var(--color-surface-overlay)] text-[var(--color-content-primary)] text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-20 shadow-lg pointer-events-none border border-[var(--color-border-default)]">
                <div className="text-[var(--color-content-muted)] text-[10px] mb-0.5">{item.label}</div>
                <div className="flex gap-2">
                  <span className="text-[var(--color-status-danger)]">Detected: {formatValue(item.value)}</span>
                  {item.secondaryValue !== undefined && (
                    <span className="text-[var(--color-status-success)]">Resolved: {formatValue(item.secondaryValue)}</span>
                  )}
                </div>
              </div>
              <div
                className={`flex-1 ${primaryColor} rounded-t transition-colors relative cursor-pointer`}
                style={{
                  height: `${Math.max((item.value / maxValue) * 100, 2)}%`,
                  minHeight: item.value > 0 ? '4px' : '2px',
                }}
              />
              {secondaryColor && item.secondaryValue !== undefined && (
                <div
                  className={`flex-1 ${secondaryColor} rounded-t transition-colors cursor-pointer`}
                  style={{
                    height: `${Math.max((item.secondaryValue / maxValue) * 100, 2)}%`,
                    minHeight: item.secondaryValue > 0 ? '4px' : '2px',
                  }}
                />
              )}
            </div>
          ))}
        </div>

        {/* X-axis labels area with fixed height */}
        <div className="flex gap-1 h-6">
          {displayData.map((item, index) => (
            <div key={index} className="flex-1 flex justify-center">
              {index % labelInterval === 0 && (
                <span className="text-[10px] text-[var(--color-content-muted)] mt-1 whitespace-nowrap">
                  {item.label}
                </span>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

interface ChartCardProps {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  legend?: React.ReactNode;
}

const ChartCard: React.FC<ChartCardProps> = ({ title, subtitle, children, legend }) => (
  <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-sm border border-[var(--color-border-default)]">
    <div className="flex items-center justify-between mb-4">
      <div>
        <h3 className="text-lg font-semibold text-[var(--color-content-primary)]">
          {title}
        </h3>
        {subtitle && (
          <p className="text-sm text-[var(--color-content-muted)]">{subtitle}</p>
        )}
      </div>
      {legend}
    </div>
    {children}
  </div>
);

const Analytics: React.FC = () => {
  const navigate = useNavigate();
  const [analytics, setAnalytics] = useState<TrendAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeRange, setTimeRange] = useState<TimeRange>('30d');

  const fetchAnalytics = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const filters: TrendAnalyticsFilters = {
        range: timeRange,
        granularity: 'day',
      };
      const data = await getTrendAnalytics(filters);
      setAnalytics(data);
      setLoading(false);
    } catch (err) {
      console.error('[Analytics] Error fetching analytics:', err);
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch analytics';
      setError(errorMessage);
      setLoading(false);
    }
  }, [timeRange]);

  useEffect(() => {
    fetchAnalytics();
  }, [fetchAnalytics]);

  const latestMetrics = useMemo(() => {
    if (!analytics) return null;

    const passRate = analytics.passRate[analytics.passRate.length - 1] ?? null;
    const defects = analytics.defects[analytics.defects.length - 1] ?? null;
    const performance = analytics.performance[analytics.performance.length - 1] ?? null;

    // Use summary for accurate counts (totalExecutions counts MultiTurnExecution records)
    const totalExecutions = analytics.summary?.totalExecutions ?? 0;
    const totalValidations = analytics.summary?.totalValidations ?? 0;

    const totalDetected = analytics.defects.reduce(
      (sum, d) => sum + d.detected,
      0
    );
    const totalResolved = analytics.defects.reduce(
      (sum, d) => sum + d.resolved,
      0
    );

    return { passRate, defects, performance, totalExecutions, totalValidations, totalDetected, totalResolved };
  }, [analytics]);

  const defectChartData = useMemo(() => {
    if (!analytics) return [];
    return analytics.defects.map((d) => ({
      label: formatDate(d.periodStart),
      value: d.detected,
      secondaryValue: d.resolved,
    }));
  }, [analytics]);

  const passRateChartData = useMemo(() => {
    if (!analytics) return [];
    return analytics.passRate;
  }, [analytics]);

  const performanceChartData = useMemo(() => {
    if (!analytics) return [];
    return analytics.performance;
  }, [analytics]);

  if (loading && !analytics) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="flex flex-col items-center gap-4">
          <RefreshCw className="w-8 h-8 text-[var(--color-status-info)] animate-spin" />
          <p className="text-[var(--color-content-secondary)]">Loading analytics...</p>
        </div>
      </div>
    );
  }

  if (error && !analytics) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="text-center">
          <XCircle className="w-12 h-12 text-[var(--color-status-danger)] mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-[var(--color-content-primary)] mb-2">
            Failed to Load Analytics
          </h2>
          <p className="text-[var(--color-content-secondary)] mb-4">{error}</p>
          <button
            onClick={fetchAnalytics}
            className="px-4 py-2 bg-[var(--color-brand-primary)] text-white rounded-lg hover:bg-[var(--color-brand-hover)] transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
          <div>
            <h1 className="text-2xl font-bold text-[var(--color-content-primary)] flex items-center gap-3">
              <BarChart3 className="w-6 h-6" style={{ color: '#2A6B6E' }} />
              Analytics Overview
            </h1>
            <p className="text-sm text-[var(--color-content-secondary)] mt-1">
              Monitor test pass rates, defect trends, and performance metrics
            </p>
          </div>

          <div className="flex items-center gap-4">
            {/* Time Range Selector */}
            <div className="flex items-center gap-2 bg-[var(--color-surface-raised)] rounded-lg border border-[var(--color-border-default)] p-1">
              {TIME_RANGES.map((range) => (
                <button
                  key={range.value}
                  onClick={() => setTimeRange(range.value)}
                  className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
                    timeRange === range.value
                      ? 'bg-[var(--color-brand-primary)] text-white'
                      : 'text-[var(--color-content-secondary)] hover:bg-[var(--color-interactive-hover)]'
                  }`}
                >
                  {range.label}
                </button>
              ))}
            </div>

            <button
              onClick={fetchAnalytics}
              disabled={loading}
              className="p-2 text-[var(--color-content-secondary)] hover:text-[var(--color-content-primary)] bg-[var(--color-surface-raised)] rounded-lg border border-[var(--color-border-default)] disabled:opacity-50"
              title="Refresh"
            >
              <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <StatCard
            variant="vertical"
            title="Pass Rate"
            value={analytics?.summary ? formatPercentage(analytics.summary.avgPassRatePct) : '—'}
            subtitle={analytics?.summary ? `${formatInteger(analytics.summary.totalValidations)} validations over ${timeRange === '7d' ? '7' : timeRange === '14d' ? '14' : timeRange === '30d' ? '30' : '90'} days` : undefined}
            icon={<Target className="w-5 h-5" />}
            iconColor="text-[var(--color-status-success)]"
            iconBg="bg-[var(--color-status-success-bg)]"
            trend={
              latestMetrics?.passRate?.changePct != null && latestMetrics.passRate.direction !== 'flat'
                ? {
                    value: `${Math.abs(latestMetrics.passRate.changePct).toFixed(1)}%`,
                    direction: latestMetrics.passRate.direction,
                    isPositive: latestMetrics.passRate.direction === 'up',
                  }
                : undefined
            }
          />
          <StatCard
            variant="vertical"
            title="Open Defects"
            value={latestMetrics?.defects ? formatInteger(latestMetrics.defects.netOpen) : '—'}
            subtitle={`${latestMetrics?.totalDetected ?? 0} detected / ${latestMetrics?.totalResolved ?? 0} resolved`}
            icon={<Bug className="w-5 h-5" />}
            iconColor="text-[var(--color-status-danger)]"
            iconBg="bg-[var(--color-status-danger-bg)]"
            trend={
              latestMetrics?.defects?.changeOpen != null && latestMetrics.defects.direction !== 'flat'
                ? {
                    value: formatInteger(Math.abs(latestMetrics.defects.changeOpen)),
                    direction: latestMetrics.defects.direction,
                    isPositive: latestMetrics.defects.direction === 'down',
                  }
                : undefined
            }
          />
          <StatCard
            variant="vertical"
            title="Avg Response Time"
            value={analytics?.summary ? formatMilliseconds(analytics.summary.avgResponseTimeMs) : '—'}
            subtitle={analytics?.summary ? `${formatInteger(analytics.summary.responseTimeSamples)} samples over ${timeRange === '7d' ? '7' : timeRange === '14d' ? '14' : timeRange === '30d' ? '30' : '90'} days` : undefined}
            icon={<Zap className="w-5 h-5" />}
            iconColor="text-[var(--color-status-warning)]"
            iconBg="bg-[var(--color-status-warning-bg)]"
            trend={
              latestMetrics?.performance?.changeMs != null && latestMetrics.performance.direction !== 'flat'
                ? {
                    value: `${Math.abs(latestMetrics.performance.changeMs).toFixed(0)} ms`,
                    direction: latestMetrics.performance.direction,
                    isPositive: latestMetrics.performance.direction === 'down',
                  }
                : undefined
            }
          />
          <StatCard
            variant="vertical"
            title="Total Executions"
            value={formatInteger(latestMetrics?.totalExecutions ?? 0)}
            subtitle={`Over ${timeRange === '7d' ? '7' : timeRange === '14d' ? '14' : timeRange === '30d' ? '30' : '90'} days`}
            icon={<Activity className="w-5 h-5" />}
            iconColor="text-[var(--color-status-info)]"
            iconBg="bg-[var(--color-status-info-bg)]"
          />
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Pass Rate Trend */}
          <ChartCard
            title="Pass Rate Trend"
            subtitle="Test pass rate over time"
          >
            <TrendLineChart
              data={passRateChartData}
              getValue={(p: PassRateTrendPoint) => p.passRatePct}
              getLabel={(p: PassRateTrendPoint) => p.periodStart}
              formatValue={formatPercentage}
              color="green"
              height={200}
            />
          </ChartCard>

          {/* Response Time Trend */}
          <ChartCard
            title="Response Time Trend"
            subtitle="Average response time over time"
          >
            <TrendLineChart
              data={performanceChartData}
              getValue={(p: PerformanceTrendPoint) => p.avgResponseTimeMs}
              getLabel={(p: PerformanceTrendPoint) => p.periodStart}
              formatValue={formatMilliseconds}
              color="yellow"
              height={200}
            />
          </ChartCard>
        </div>

        {/* Defect Trend - Full Width */}
        <div className="mb-8">
          <ChartCard
            title="Defect Trend"
            subtitle="Defects detected and resolved over time"
            legend={
              <div className="flex items-center gap-4 text-sm">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-[var(--color-status-danger)]" />
                  <span className="text-[var(--color-content-secondary)]">Detected</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-[var(--color-status-success)]" />
                  <span className="text-[var(--color-content-secondary)]">Resolved</span>
                </div>
              </div>
            }
          >
            <SimpleBarChart
              data={defectChartData}
              formatValue={formatInteger}
              primaryColor="bg-[var(--color-status-danger)] hover:opacity-80"
              secondaryColor="bg-[var(--color-status-success)] hover:opacity-80"
              height={200}
            />
          </ChartCard>
        </div>

        {/* Defect Backlog */}
        <div className="mb-8">
          <ChartCard
            title="Open Defect Backlog"
            subtitle="Net open defects over time"
          >
            <TrendLineChart
              data={analytics?.defects ?? []}
              getValue={(d: DefectTrendPoint) => d.netOpen}
              getLabel={(d: DefectTrendPoint) => d.periodStart}
              formatValue={formatInteger}
              color="red"
              height={180}
            />
          </ChartCard>
        </div>

        {/* Quick Links */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={() => navigate('/edge-cases/analytics')}
            className="flex items-center justify-between p-4 bg-[var(--color-surface-raised)] rounded-xl border border-[var(--color-border-default)] hover:border-[var(--color-status-info)] transition-colors group"
          >
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-[var(--color-status-purple-bg)]">
                <BarChart3 className="w-5 h-5 text-[var(--color-status-purple)]" />
              </div>
              <div className="text-left">
                <p className="font-medium text-[var(--color-content-primary)]">Edge Case Analytics</p>
                <p className="text-sm text-[var(--color-content-muted)]">View detailed edge case metrics</p>
              </div>
            </div>
            <ArrowRight className="w-5 h-5 text-[var(--color-content-muted)] group-hover:text-[var(--color-status-info)] transition-colors" />
          </button>

          <button
            onClick={() => navigate('/validation')}
            className="flex items-center justify-between p-4 bg-[var(--color-surface-raised)] rounded-xl border border-[var(--color-border-default)] hover:border-[var(--color-status-info)] transition-colors group"
          >
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-[var(--color-status-success-bg)]">
                <CheckCircle2 className="w-5 h-5 text-[var(--color-status-success)]" />
              </div>
              <div className="text-left">
                <p className="font-medium text-[var(--color-content-primary)]">Validation Dashboard</p>
                <p className="text-sm text-[var(--color-content-muted)]">Review pending validations</p>
              </div>
            </div>
            <ArrowRight className="w-5 h-5 text-[var(--color-content-muted)] group-hover:text-[var(--color-status-info)] transition-colors" />
          </button>

          <button
            onClick={() => navigate('/suite-runs')}
            className="flex items-center justify-between p-4 bg-[var(--color-surface-raised)] rounded-xl border border-[var(--color-border-default)] hover:border-[var(--color-status-info)] transition-colors group"
          >
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-[var(--color-status-info-bg)]">
                <Clock className="w-5 h-5 text-[var(--color-status-info)]" />
              </div>
              <div className="text-left">
                <p className="font-medium text-[var(--color-content-primary)]">Suite Runs</p>
                <p className="text-sm text-[var(--color-content-muted)]">View recent test suite runs</p>
              </div>
            </div>
            <ArrowRight className="w-5 h-5 text-[var(--color-content-muted)] group-hover:text-[var(--color-status-info)] transition-colors" />
          </button>
        </div>
    </div>
  );
};

export default Analytics;
