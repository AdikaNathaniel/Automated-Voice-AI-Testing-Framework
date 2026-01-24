import React, { useEffect, useState, useMemo } from 'react';
import {
  BarChart3,
  TrendingUp,
  TrendingDown,
  Minus,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Clock,
  RefreshCw,
  Calendar,
  PieChart,
  Activity,
  Zap,
  Users,
  ArrowRight,
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { getEdgeCaseAnalytics } from '../../services/edgeCase.service';
import type { EdgeCaseAnalytics, TimeSeriesPoint } from '../../types/edgeCase';

const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
  });
};

const formatFullDate = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
};

const severityColors: Record<string, string> = {
  critical: 'bg-[var(--color-status-danger)]',
  high: 'bg-[var(--color-status-amber)]',
  medium: 'bg-[var(--color-status-warning)]',
  low: 'bg-[var(--color-status-success)]',
  unassigned: 'bg-[var(--color-content-muted)]',
};

const categoryColors = [
  'bg-[var(--color-status-info)]',
  'bg-[var(--color-status-purple)]',
  'bg-[var(--color-status-pink)]',
  'bg-[var(--color-status-indigo)]',
  'bg-[var(--color-status-teal)]',
  'bg-[var(--color-status-cyan)]',
  'bg-[var(--color-status-success)]',
  'bg-[var(--color-status-amber)]',
];

const statusColors: Record<string, string> = {
  active: 'bg-[var(--color-status-warning)]',
  resolved: 'bg-[var(--color-status-success)]',
  wont_fix: 'bg-[var(--color-content-muted)]',
};

// Icon background color mapping to semantic tokens
const iconBgColorMap: Record<string, string> = {
  blue: 'var(--color-status-info-bg)',
  yellow: 'var(--color-status-warning-bg)',
  green: 'var(--color-status-success-bg)',
  red: 'var(--color-status-danger-bg)',
  purple: 'var(--color-status-purple-bg)',
};

interface StatCardProps {
  title: string;
  value: number | string;
  subtitle?: string;
  icon: React.ReactNode;
  trend?: {
    value: number;
    direction: 'up' | 'down' | 'stable';
  };
  color?: string;
}

const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  icon,
  trend,
  color = 'blue',
}) => {
  const getTrendIcon = () => {
    if (!trend) return null;
    if (trend.direction === 'up') return <TrendingUp className="w-4 h-4" />;
    if (trend.direction === 'down') return <TrendingDown className="w-4 h-4" />;
    return <Minus className="w-4 h-4" />;
  };

  const getTrendColor = () => {
    if (!trend) return '';
    // For edge cases, down is good (fewer issues), up is concerning
    if (trend.direction === 'down') return 'text-[var(--color-status-success)]';
    if (trend.direction === 'up') return 'text-[var(--color-brand-primary)]';
    return 'text-[var(--color-content-secondary)]';
  };

  return (
    <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-sm border border-[var(--color-border-default)]">
      <div className="flex items-center justify-between mb-4">
        <div className="p-3 rounded-lg" style={{ backgroundColor: iconBgColorMap[color] || 'var(--color-status-info-bg)' }}>
          {icon}
        </div>
        {trend && (
          <div className={`flex items-center gap-1 text-sm ${getTrendColor()}`}>
            {getTrendIcon()}
            <span>{Math.abs(trend.value)}%</span>
          </div>
        )}
      </div>
      <h3 className="text-3xl font-bold text-[var(--color-content-primary)] mb-1">
        {value}
      </h3>
      <p className="text-sm text-[var(--color-content-secondary)]">{title}</p>
      {subtitle && (
        <p className="text-xs text-[var(--color-content-muted)] mt-1">{subtitle}</p>
      )}
    </div>
  );
};

interface SimpleBarChartProps {
  data: TimeSeriesPoint[];
  height?: number;
}

const SimpleBarChart: React.FC<SimpleBarChartProps> = ({ data, height = 200 }) => {
  const maxCount = Math.max(...data.map(d => d.count), 1);

  // Show at most 15 bars for readability
  const displayData = data.length > 15
    ? data.filter((_, i) => i % Math.ceil(data.length / 15) === 0)
    : data;

  return (
    <div className="flex items-end gap-1" style={{ height }}>
      {displayData.map((point, index) => (
        <div
          key={point.date}
          className="flex-1 flex flex-col items-center group"
        >
          <div
            className="w-full bg-[var(--color-status-info)] rounded-t hover:opacity-90 transition-colors relative"
            style={{
              height: `${Math.max((point.count / maxCount) * 100, 2)}%`,
              minHeight: point.count > 0 ? '4px' : '2px',
            }}
          >
            <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-[var(--color-surface-overlay)] text-[var(--color-content-primary)] text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10 border border-[var(--color-border-default)]">
              {point.count} on {formatDate(point.date)}
            </div>
          </div>
          {index % Math.ceil(displayData.length / 7) === 0 && (
            <span className="text-[10px] text-[var(--color-content-muted)] mt-1 whitespace-nowrap">
              {formatDate(point.date)}
            </span>
          )}
        </div>
      ))}
    </div>
  );
};

interface DistributionBarProps {
  items: Array<{
    label: string;
    count: number;
    percentage: number;
    color: string;
  }>;
  title: string;
}

const DistributionBar: React.FC<DistributionBarProps> = ({ items, title }) => {
  return (
    <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-sm border border-[var(--color-border-default)]">
      <h3 className="text-lg font-semibold text-[var(--color-content-primary)] mb-4">
        {title}
      </h3>
      <div className="h-4 flex rounded-full overflow-hidden mb-4">
        {items.map((item, index) => (
          <div
            key={item.label}
            className={`${item.color} transition-all hover:opacity-80`}
            style={{ width: `${item.percentage}%` }}
            title={`${item.label}: ${item.count} (${item.percentage}%)`}
          />
        ))}
      </div>
      <div className="flex flex-wrap gap-4">
        {items.map((item) => (
          <div key={item.label} className="flex items-center gap-2">
            <div className={`w-3 h-3 rounded-full ${item.color}`} />
            <span className="text-sm text-[var(--color-content-secondary)]">
              {item.label}: {item.count} ({item.percentage}%)
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

const EdgeCaseAnalytics: React.FC = () => {
  const navigate = useNavigate();
  const [analytics, setAnalytics] = useState<EdgeCaseAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dateRange, setDateRange] = useState<'7d' | '30d' | '90d'>('30d');

  const fetchAnalytics = async () => {
    setLoading(true);
    setError(null);

    try {
      const today = new Date();
      const days = dateRange === '7d' ? 7 : dateRange === '30d' ? 30 : 90;
      const fromDate = new Date(today);
      fromDate.setDate(fromDate.getDate() - days);

      const data = await getEdgeCaseAnalytics({
        dateFrom: fromDate.toISOString().split('T')[0],
        dateTo: today.toISOString().split('T')[0],
        includeTrend: true,
      });
      setAnalytics(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch analytics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, [dateRange]);

  const severityDistributionItems = useMemo(() => {
    if (!analytics) return [];
    return analytics.severityDistribution.map((item) => ({
      label: (item.severity || 'unassigned').charAt(0).toUpperCase() +
        (item.severity || 'unassigned').slice(1),
      count: item.count,
      percentage: item.percentage,
      color: severityColors[item.severity || 'unassigned'] || 'bg-[var(--color-content-muted)]',
    }));
  }, [analytics]);

  const categoryDistributionItems = useMemo(() => {
    if (!analytics) return [];
    return analytics.categoryDistribution.map((item, index) => ({
      label: (item.category || 'uncategorized')
        .split('_')
        .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
        .join(' '),
      count: item.count,
      percentage: item.percentage,
      color: categoryColors[index % categoryColors.length],
    }));
  }, [analytics]);

  const statusDistributionItems = useMemo(() => {
    if (!analytics) return [];
    return analytics.statusDistribution.map((item) => ({
      label: (item.status || 'unknown').charAt(0).toUpperCase() +
        (item.status || 'unknown').slice(1).replace('_', ' '),
      count: item.count,
      percentage: item.percentage,
      color: statusColors[item.status || 'unknown'] || 'bg-[var(--color-content-muted)]',
    }));
  }, [analytics]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="flex flex-col items-center gap-4">
          <RefreshCw className="w-8 h-8 text-[var(--color-status-info)] animate-spin" />
          <p className="text-[var(--color-content-secondary)]">Loading analytics...</p>
        </div>
      </div>
    );
  }

  if (error) {
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
            className="px-4 py-2 bg-[var(--color-status-info)] text-white rounded-lg hover:opacity-90"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!analytics) return null;

  return (
    <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
          <div>
            <h1 className="text-2xl font-bold text-[var(--color-content-primary)] flex items-center gap-3">
              <BarChart3 className="w-6 h-6" style={{ color: '#2A6B6E' }} />
              Edge Case Analytics
            </h1>
            <p className="text-[var(--color-content-secondary)] mt-1">
              {formatFullDate(analytics.dateRange.from)} - {formatFullDate(analytics.dateRange.to)}
            </p>
          </div>

          <div className="flex items-center gap-4">
            {/* Date Range Selector */}
            <div className="flex items-center gap-2 bg-[var(--color-surface-raised)] rounded-lg border border-[var(--color-border-default)] p-1">
              {(['7d', '30d', '90d'] as const).map((range) => (
                <button
                  key={range}
                  onClick={() => setDateRange(range)}
                  className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
                    dateRange === range
                      ? 'bg-[var(--color-status-info)] text-white'
                      : 'text-[var(--color-content-secondary)] hover:bg-[var(--color-interactive-hover)]'
                  }`}
                >
                  {range === '7d' ? '7 Days' : range === '30d' ? '30 Days' : '90 Days'}
                </button>
              ))}
            </div>

            <button
              onClick={fetchAnalytics}
              className="p-2 text-[var(--color-content-secondary)] hover:text-[var(--color-content-primary)] bg-[var(--color-surface-raised)] rounded-lg border border-[var(--color-border-default)]"
              title="Refresh"
            >
              <RefreshCw className="w-5 h-5" />
            </button>

            <button
              onClick={() => navigate('/edge-cases')}
              className="btn btn-accent px-4 py-2 rounded-lg"
            >
              View Library
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
          <StatCard
            title="Total in Range"
            value={analytics.summary.totalInRange}
            subtitle={`${analytics.summary.totalAllTime} all time`}
            icon={<BarChart3 className="w-6 h-6 text-[var(--color-status-info)]" />}
            trend={
              analytics.trendComparison
                ? {
                    value: analytics.trendComparison.changePercent,
                    direction: analytics.trendComparison.trend,
                  }
                : undefined
            }
            color="blue"
          />
          <StatCard
            title="Active"
            value={analytics.summary.activeCount}
            icon={<AlertTriangle className="w-6 h-6 text-[var(--color-status-warning)]" />}
            color="yellow"
          />
          <StatCard
            title="Resolved"
            value={analytics.summary.resolvedInRange}
            subtitle="in this period"
            icon={<CheckCircle2 className="w-6 h-6 text-[var(--color-status-success)]" />}
            color="green"
          />
          <StatCard
            title="Critical Active"
            value={analytics.summary.criticalActive}
            icon={<Zap className="w-6 h-6 text-[var(--color-status-danger)]" />}
            color="red"
          />
          <StatCard
            title="Resolution Rate"
            value={`${analytics.resolutionMetrics.resolutionRatePercent}%`}
            icon={<Activity className="w-6 h-6 text-[var(--color-status-purple)]" />}
            color="purple"
          />
        </div>

        {/* Trend Chart */}
        <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-sm border border-[var(--color-border-default)] mb-8">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-[var(--color-content-primary)]">
              Edge Cases Over Time
            </h3>
            {analytics.trendComparison && (
              <div
                className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-sm ${
                  analytics.trendComparison.trend === 'down'
                    ? 'bg-[var(--color-status-success-bg)] text-[var(--color-status-success)]'
                    : analytics.trendComparison.trend === 'up'
                    ? 'bg-[var(--color-brand-muted)] text-[var(--color-brand-primary)]'
                    : 'bg-[var(--color-interactive-hover)] text-[var(--color-content-secondary)]'
                }`}
              >
                {analytics.trendComparison.trend === 'down' && (
                  <TrendingDown className="w-4 h-4" />
                )}
                {analytics.trendComparison.trend === 'up' && (
                  <TrendingUp className="w-4 h-4" />
                )}
                {analytics.trendComparison.trend === 'stable' && (
                  <Minus className="w-4 h-4" />
                )}
                <span>
                  {analytics.trendComparison.change > 0 ? '+' : ''}
                  {analytics.trendComparison.change} vs previous period
                </span>
              </div>
            )}
          </div>
          <SimpleBarChart data={analytics.countOverTime} height={200} />
        </div>

        {/* Distribution Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <DistributionBar
            title="By Severity"
            items={severityDistributionItems}
          />
          <DistributionBar
            title="By Status"
            items={statusDistributionItems}
          />
        </div>

        <DistributionBar
          title="By Category"
          items={categoryDistributionItems}
        />

        {/* Auto vs Manual & Top Patterns */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-8">
          {/* Auto vs Manual */}
          <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-sm border border-[var(--color-border-default)]">
            <div className="flex items-center gap-3 mb-6">
              <Users className="w-6 h-6 text-[var(--color-status-indigo)]" />
              <h3 className="text-lg font-semibold text-[var(--color-content-primary)]">
                Source Distribution
              </h3>
            </div>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-4 h-4 rounded-full bg-[var(--color-status-indigo)]" />
                  <span className="text-[var(--color-content-secondary)]">Auto-Created</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xl font-semibold text-[var(--color-content-primary)]">
                    {analytics.autoVsManual.autoCreated}
                  </span>
                  <span className="text-sm text-[var(--color-content-muted)]">
                    ({analytics.autoVsManual.autoCreatedPercent}%)
                  </span>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-4 h-4 rounded-full bg-[var(--color-content-muted)]" />
                  <span className="text-[var(--color-content-secondary)]">Manually Created</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xl font-semibold text-[var(--color-content-primary)]">
                    {analytics.autoVsManual.manuallyCreated}
                  </span>
                  <span className="text-sm text-[var(--color-content-muted)]">
                    ({analytics.autoVsManual.manuallyCreatedPercent}%)
                  </span>
                </div>
              </div>
              <div className="h-3 flex rounded-full overflow-hidden mt-4">
                <div
                  className="bg-[var(--color-status-indigo)]"
                  style={{ width: `${analytics.autoVsManual.autoCreatedPercent}%` }}
                />
                <div
                  className="bg-[var(--color-content-muted)]"
                  style={{ width: `${analytics.autoVsManual.manuallyCreatedPercent}%` }}
                />
              </div>
            </div>
          </div>

          {/* Top Patterns */}
          <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-sm border border-[var(--color-border-default)]">
            <div className="flex items-center gap-3 mb-6">
              <PieChart className="w-6 h-6 text-[var(--color-status-purple)]" />
              <h3 className="text-lg font-semibold text-[var(--color-content-primary)]">
                Top Patterns
              </h3>
            </div>
            {analytics.topPatterns.length === 0 ? (
              <p className="text-[var(--color-content-muted)] text-center py-8">
                No patterns detected yet. Run pattern analysis to identify trends.
              </p>
            ) : (
              <div className="space-y-3">
                {analytics.topPatterns.slice(0, 5).map((pattern, index) => (
                  <button
                    key={pattern.id}
                    onClick={() => navigate(`/pattern-groups/${pattern.id}`)}
                    className="w-full flex items-center justify-between p-3 rounded-lg bg-[var(--color-surface-inset)]/50 hover:bg-[var(--color-interactive-hover)] transition-colors text-left"
                  >
                    <div className="flex items-center gap-3">
                      <span className="w-6 h-6 flex items-center justify-center rounded-full bg-[var(--color-status-purple-bg)] text-[var(--color-status-purple)] text-sm font-medium">
                        {index + 1}
                      </span>
                      <div>
                        <p className="text-sm font-medium text-[var(--color-content-primary)]">
                          {pattern.name}
                        </p>
                        <p className="text-xs text-[var(--color-content-muted)]">
                          {pattern.patternType || 'general'}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-semibold text-[var(--color-content-primary)]">
                        {pattern.linkedEdgeCases}
                      </p>
                      <p className="text-xs text-[var(--color-content-muted)]">edge cases</p>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Resolution Metrics Detail */}
        <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-sm border border-[var(--color-border-default)] mt-8">
          <h3 className="text-lg font-semibold text-[var(--color-content-primary)] mb-6">
            Resolution Breakdown
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-3 rounded-full bg-[var(--color-status-info-bg)] flex items-center justify-center">
                <BarChart3 className="w-8 h-8 text-[var(--color-status-info)]" />
              </div>
              <p className="text-2xl font-bold text-[var(--color-content-primary)]">
                {analytics.resolutionMetrics.totalCreated}
              </p>
              <p className="text-sm text-[var(--color-content-muted)]">Created</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-3 rounded-full bg-[var(--color-status-success-bg)] flex items-center justify-center">
                <CheckCircle2 className="w-8 h-8 text-[var(--color-status-success)]" />
              </div>
              <p className="text-2xl font-bold text-[var(--color-content-primary)]">
                {analytics.resolutionMetrics.resolved}
              </p>
              <p className="text-sm text-[var(--color-content-muted)]">Resolved</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-3 rounded-full bg-[var(--color-status-warning-bg)] flex items-center justify-center">
                <Clock className="w-8 h-8 text-[var(--color-status-warning)]" />
              </div>
              <p className="text-2xl font-bold text-[var(--color-content-primary)]">
                {analytics.resolutionMetrics.active}
              </p>
              <p className="text-sm text-[var(--color-content-muted)]">Active</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-3 rounded-full bg-[var(--color-surface-inset)] flex items-center justify-center">
                <XCircle className="w-8 h-8 text-[var(--color-content-muted)]" />
              </div>
              <p className="text-2xl font-bold text-[var(--color-content-primary)]">
                {analytics.resolutionMetrics.wontFix}
              </p>
              <p className="text-sm text-[var(--color-content-muted)]">Won't Fix</p>
            </div>
          </div>
        </div>
    </div>
  );
};

export default EdgeCaseAnalytics;
