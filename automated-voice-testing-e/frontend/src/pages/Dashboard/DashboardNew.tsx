/**
 * Dashboard Page - Executive Overview
 *
 * Modern dashboard with:
 * - Welcome header with time-based greeting
 * - System overview stats
 * - Quick action cards
 * - KPI overview with sparkline trends
 * - Recent suite runs
 * - Defect breakdown
 * - Validation accuracy metrics
 * - Real-time execution status
 */

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import {
  Play,
  CheckCircle,
  XCircle,
  Clock,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  Zap,
  BarChart3,
  ArrowRight,
  RefreshCw,
  FlaskConical,
  Layers,
  Eye,
  Activity,
  Target,
  Timer,
  ChevronRight,
  Bug,
  FolderOpen,
  PlayCircle,
  FileCheck,
} from 'lucide-react';
import { getDashboardSnapshot, getDashboardSettings, type DashboardSettings } from '../../services/dashboard.service';
import { getSuiteRuns } from '../../services/suiteRun.service';
import { StatCard } from '../../components/common';
import type { DashboardSnapshot } from '../../types/dashboard';
import type { SuiteRunListItem } from '../../types/suiteRun';
import type { RootState } from '../../store';

// Helper to get time-based greeting
const getGreeting = (): string => {
  const hour = new Date().getHours();
  if (hour < 12) return 'Good morning';
  if (hour < 17) return 'Good afternoon';
  return 'Good evening';
};

// Simple sparkline component
const Sparkline: React.FC<{ data: number[]; color?: string }> = ({
  data,
  color = '#2A6B6E',
}) => {
  if (!data || data.length < 2) return null;

  const max = Math.max(...data);
  const min = Math.min(...data);
  const range = max - min || 1;
  const width = 80;
  const height = 24;
  const points = data
    .map((value, i) => {
      const x = (i / (data.length - 1)) * width;
      const y = height - ((value - min) / range) * height;
      return `${x},${y}`;
    })
    .join(' ');

  return (
    <svg width={width} height={height} className="overflow-visible">
      <polyline
        points={points}
        fill="none"
        stroke={color}
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
};

// Status badge component - uses semantic tokens
const StatusBadge: React.FC<{ status: string }> = ({ status }) => {
  const config: Record<string, { bg: string; text: string; label: string }> = {
    completed: { bg: 'bg-[var(--color-status-success-bg)]', text: 'text-[var(--color-status-success)]', label: 'Completed' },
    running: { bg: 'bg-[var(--color-status-info-bg)]', text: 'text-[var(--color-status-info)]', label: 'Running' },
    pending: { bg: 'bg-[var(--color-status-warning-bg)]', text: 'text-[var(--color-status-warning)]', label: 'Pending' },
    failed: { bg: 'bg-[var(--color-status-danger-bg)]', text: 'text-[var(--color-status-danger)]', label: 'Failed' },
    cancelled: { bg: 'bg-[var(--color-surface-inset)]', text: 'text-[var(--color-content-secondary)]', label: 'Cancelled' },
  };
  const { bg, text, label } = config[status] || config.pending;

  return (
    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${bg} ${text}`}>
      {label}
    </span>
  );
};


const DashboardNew: React.FC = () => {
  const navigate = useNavigate();
  const user = useSelector((state: RootState) => state.auth.user);

  const [snapshot, setSnapshot] = useState<DashboardSnapshot | null>(null);
  const [recentRuns, setRecentRuns] = useState<SuiteRunListItem[]>([]);
  const [settings, setSettings] = useState<DashboardSettings>({ responseTimeSlaMs: 2000 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeRange, setTimeRange] = useState<'1h' | '24h' | '7d' | '30d'>('24h');
  const [refreshing, setRefreshing] = useState(false);

  const fetchData = async (showRefresh = false) => {
    if (showRefresh) setRefreshing(true);
    else setLoading(true);

    try {
      const [snapshotData, runsData, settingsData] = await Promise.all([
        getDashboardSnapshot({ timeRange }),
        getSuiteRuns({ limit: 5 }),
        getDashboardSettings(),
      ]);
      setSnapshot(snapshotData);
      setRecentRuns(runsData.items || []);
      setSettings(settingsData);
      setError(null);
    } catch (err) {
      console.error('Dashboard fetch error:', err);
      setError('Unable to load dashboard metrics');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [timeRange]);

  // Auto-refresh every 30 seconds
  useEffect(() => {
    const interval = setInterval(() => fetchData(true), 30000);
    return () => clearInterval(interval);
  }, [timeRange]);

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="h-24 bg-[var(--color-surface-raised)] rounded-2xl animate-pulse" />
        <div className="grid grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-24 bg-[var(--color-surface-raised)] rounded-xl animate-pulse" />
          ))}
        </div>
        <div className="grid grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-32 bg-[var(--color-surface-raised)] rounded-xl animate-pulse" />
          ))}
        </div>
        <div className="grid grid-cols-3 gap-6">
          <div className="col-span-2 h-80 bg-[var(--color-surface-raised)] rounded-xl animate-pulse" />
          <div className="h-80 bg-[var(--color-surface-raised)] rounded-xl animate-pulse" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-[var(--color-surface-raised)] rounded-xl p-8 text-center">
        <AlertTriangle className="w-12 h-12 text-[var(--color-status-danger)] mx-auto mb-4" />
        <h2 className="text-lg font-semibold text-[var(--color-content-primary)] mb-2">Failed to Load Dashboard</h2>
        <p className="text-[var(--color-content-muted)] mb-4">{error}</p>
        <button
          onClick={() => fetchData()}
          className="btn btn-primary"
        >
          Try Again
        </button>
      </div>
    );
  }

  const kpis = snapshot?.kpis || {};
  const realTime = snapshot?.realTimeExecution || {};
  const validation = snapshot?.validationAccuracy || {};
  const validationQueue = snapshot?.validationQueue || { pendingReviews: 0 };
  const passRateTrend = snapshot?.passRateTrend || [];
  const defects = snapshot?.defects || { open: 0, critical: 0, high: 0, medium: 0, low: 0 };
  const scenarios = snapshot?.scenarios || { total: 0 };
  const testSuites = snapshot?.testSuites || { total: 0 };
  const suiteRuns = snapshot?.suiteRuns || { total: 0, completed: 0, failed: 0, running: 0 };
  const edgeCases = snapshot?.edgeCases || { total: 0, resolved: 0 };

  // Calculate trend direction
  const trendData = passRateTrend.map((p) => p.pass_rate_pct || 0);
  const isPositiveTrend = trendData.length >= 2 && trendData[trendData.length - 1] >= trendData[0];

  return (
    <div className="space-y-6">
      {/* Welcome Header */}
      <div className="bg-gradient-to-r from-[#2A6B6E] to-[#11484D] rounded-2xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold mb-1">
              {getGreeting()}, {user?.email?.split('@')[0] || 'there'}!
            </h1>
            <p className="text-white/80 text-sm">
              Here's what's happening with your voice testing today.
            </p>
          </div>
          <div className="flex items-center gap-3">
            {/* Time Range Selector */}
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value as typeof timeRange)}
              className="bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-white/30"
            >
              <option value="1h" className="text-[var(--color-content-primary)]">Last Hour</option>
              <option value="24h" className="text-[var(--color-content-primary)]">Last 24 Hours</option>
              <option value="7d" className="text-[var(--color-content-primary)]">Last 7 Days</option>
              <option value="30d" className="text-[var(--color-content-primary)]">Last 30 Days</option>
            </select>
            <button
              onClick={() => fetchData(true)}
              disabled={refreshing}
              className="p-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors"
            >
              <RefreshCw className={`w-5 h-5 ${refreshing ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>
      </div>

      {/* System Overview - Stats Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          title="Scenarios"
          value={scenarios.total}
          icon={<FlaskConical className="w-6 h-6" />}
          iconColor="text-primary"
          iconBg="bg-primary/10"
          onClick={() => navigate('/scenarios')}
        />
        <StatCard
          title="Test Suites"
          value={testSuites.total}
          icon={<Layers className="w-6 h-6" />}
          iconColor="text-[var(--color-status-info)]"
          iconBg="bg-[var(--color-status-info-bg)]"
          onClick={() => navigate('/test-suites')}
        />
        <StatCard
          title="Suite Runs"
          value={suiteRuns.total}
          icon={<PlayCircle className="w-6 h-6" />}
          iconColor="text-[var(--color-status-success)]"
          iconBg="bg-[var(--color-status-success-bg)]"
          onClick={() => navigate('/suite-runs')}
          subtitle={suiteRuns.running > 0 ? `${suiteRuns.running} running` : undefined}
        />
        <StatCard
          title="Open Defects"
          value={defects.open}
          icon={<Bug className="w-6 h-6" />}
          iconColor="text-[var(--color-status-danger)]"
          iconBg="bg-[var(--color-status-danger-bg)]"
          onClick={() => navigate('/defects')}
          subtitle={defects.critical > 0 ? `${defects.critical} critical` : undefined}
        />
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <button
          onClick={() => navigate('/scenarios/new')}
          className="flex items-center gap-3 p-4 bg-[var(--color-surface-raised)] rounded-xl border border-[var(--color-border-subtle)] hover:border-primary/30 hover:shadow-md transition-all group"
        >
          <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
            <FlaskConical className="w-5 h-5 text-primary" />
          </div>
          <div className="text-left">
            <p className="font-medium text-[var(--color-content-primary)]">New Scenario</p>
            <p className="text-xs text-[var(--color-content-muted)]">Create test scenario</p>
          </div>
        </button>

        <button
          onClick={() => navigate('/test-suites')}
          className="flex items-center gap-3 p-4 bg-[var(--color-surface-raised)] rounded-xl border border-[var(--color-border-subtle)] hover:border-primary/30 hover:shadow-md transition-all group"
        >
          <div className="w-10 h-10 rounded-lg bg-[var(--color-status-info-bg)] flex items-center justify-center group-hover:opacity-80 transition-colors">
            <Play className="w-5 h-5 text-[var(--color-status-info)]" />
          </div>
          <div className="text-left">
            <p className="font-medium text-[var(--color-content-primary)]">Run Tests</p>
            <p className="text-xs text-[var(--color-content-muted)]">Execute test suite</p>
          </div>
        </button>

        <button
          onClick={() => navigate('/validation')}
          className="flex items-center gap-3 p-4 bg-[var(--color-surface-raised)] rounded-xl border border-[var(--color-border-subtle)] hover:border-primary/30 hover:shadow-md transition-all group"
        >
          <div className="w-10 h-10 rounded-lg bg-[var(--color-status-warning-bg)] flex items-center justify-center group-hover:opacity-80 transition-colors">
            <Eye className="w-5 h-5 text-[var(--color-status-warning)]" />
          </div>
          <div className="text-left">
            <p className="font-medium text-[var(--color-content-primary)]">Validation Queue</p>
            <p className="text-xs text-[var(--color-content-muted)]">{validationQueue.pendingReviews || 0} pending review</p>
          </div>
        </button>

        <button
          onClick={() => navigate('/reports')}
          className="flex items-center gap-3 p-4 bg-[var(--color-surface-raised)] rounded-xl border border-[var(--color-border-subtle)] hover:border-primary/30 hover:shadow-md transition-all group"
        >
          <div className="w-10 h-10 rounded-lg bg-[var(--color-accent-100)] flex items-center justify-center group-hover:opacity-80 transition-colors">
            <BarChart3 className="w-5 h-5 text-[var(--color-accent-600)]" />
          </div>
          <div className="text-left">
            <p className="font-medium text-[var(--color-content-primary)]">View Reports</p>
            <p className="text-xs text-[var(--color-content-muted)]">Analytics & insights</p>
          </div>
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Tests Executed */}
        <div className="bg-[var(--color-surface-raised)] rounded-xl p-5 border border-[var(--color-border-subtle)]">
          <div className="flex items-start justify-between mb-3">
            <div className="w-10 h-10 rounded-lg bg-[var(--color-status-info-bg)] flex items-center justify-center">
              <Activity className="w-5 h-5 text-[var(--color-status-info)]" />
            </div>
            <Sparkline data={trendData} color="#3B82F6" />
          </div>
          <p className="text-sm text-[var(--color-content-muted)] mb-1">Tests Executed</p>
          <p className="text-3xl font-bold text-[var(--color-content-primary)]">{kpis.testsExecuted || 0}</p>
          <div className="flex items-center gap-1 mt-2 text-xs">
            {isPositiveTrend ? (
              <>
                <TrendingUp className="w-3 h-3 text-[var(--color-status-success)]" />
                <span className="text-[var(--color-status-success)]">Trending up</span>
              </>
            ) : (
              <>
                <TrendingDown className="w-3 h-3 text-[var(--color-status-danger)]" />
                <span className="text-[var(--color-status-danger)]">Trending down</span>
              </>
            )}
          </div>
        </div>

        {/* Pass Rate */}
        <div className="bg-[var(--color-surface-raised)] rounded-xl p-5 border border-[var(--color-border-subtle)]">
          <div className="flex items-start justify-between mb-3">
            <div className="w-10 h-10 rounded-lg bg-[var(--color-status-success-bg)] flex items-center justify-center">
              <Target className="w-5 h-5 text-[var(--color-status-success)]" />
            </div>
            <div className="text-right">
              <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                (kpis.systemHealthPct || 0) >= 90 ? 'bg-[var(--color-status-success-bg)] text-[var(--color-status-success)]' :
                (kpis.systemHealthPct || 0) >= 70 ? 'bg-[var(--color-status-warning-bg)] text-[var(--color-status-warning)]' :
                'bg-[var(--color-status-danger-bg)] text-[var(--color-status-danger)]'
              }`}>
                {(kpis.systemHealthPct || 0) >= 90 ? 'Healthy' : (kpis.systemHealthPct || 0) >= 70 ? 'Warning' : 'Critical'}
              </span>
            </div>
          </div>
          <p className="text-sm text-[var(--color-content-muted)] mb-1">Pass Rate</p>
          <p className="text-3xl font-bold text-[var(--color-content-primary)]">{kpis.systemHealthPct || 0}%</p>
          <div className="mt-2 h-1.5 bg-[var(--color-surface-inset)] rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-[var(--color-status-success)] to-[var(--color-status-success-dark,var(--color-status-success))] transition-all duration-500"
              style={{ width: `${kpis.systemHealthPct || 0}%` }}
            />
          </div>
        </div>

        {/* Failed Validations */}
        <div className="bg-[var(--color-surface-raised)] rounded-xl p-5 border border-[var(--color-border-subtle)]">
          <div className="flex items-start justify-between mb-3">
            <div className="w-10 h-10 rounded-lg bg-[var(--color-status-danger-bg)] flex items-center justify-center">
              <AlertTriangle className="w-5 h-5 text-[var(--color-status-danger)]" />
            </div>
            {(kpis.issuesDetected || 0) > 0 && (
              <span className="flex items-center gap-1 text-xs text-[var(--color-status-danger)]">
                <span className="w-2 h-2 bg-[var(--color-status-danger)] rounded-full animate-pulse" />
                Active
              </span>
            )}
          </div>
          <p className="text-sm text-[var(--color-content-muted)] mb-1">Failed Validations</p>
          <p className="text-3xl font-bold text-[var(--color-content-primary)]">{kpis.issuesDetected || 0}</p>
          <button
            onClick={() => navigate('/validation?status=failed')}
            className="flex items-center gap-1 mt-2 text-xs text-primary hover:underline"
          >
            View failed tests <ArrowRight className="w-3 h-3" />
          </button>
        </div>

        {/* Response Time */}
        <div className="bg-[var(--color-surface-raised)] rounded-xl p-5 border border-[var(--color-border-subtle)]">
          <div className="flex items-start justify-between mb-3">
            <div className="w-10 h-10 rounded-lg bg-[var(--color-accent-100)] flex items-center justify-center">
              <Timer className="w-5 h-5 text-[var(--color-accent-600)]" />
            </div>
            <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${
              (kpis.avgResponseTimeMs || 0) <= settings.responseTimeSlaMs * 0.75 ? 'bg-[var(--color-status-success-bg)] text-[var(--color-status-success)]' :
              (kpis.avgResponseTimeMs || 0) <= settings.responseTimeSlaMs ? 'bg-[var(--color-status-warning-bg)] text-[var(--color-status-warning)]' :
              'bg-[var(--color-status-danger-bg)] text-[var(--color-status-danger)]'
            }`}>
              {(kpis.avgResponseTimeMs || 0) <= settings.responseTimeSlaMs ? 'Within SLA' : 'Over SLA'}
            </span>
          </div>
          <p className="text-sm text-[var(--color-content-muted)] mb-1">Avg Response Time</p>
          <p className="text-3xl font-bold text-[var(--color-content-primary)]">
            {kpis.avgResponseTimeMs || 0}
            <span className="text-lg font-normal text-[var(--color-content-muted)]">ms</span>
          </p>
          <p className="text-xs text-[var(--color-content-muted)] mt-2">Target: &lt;{settings.responseTimeSlaMs}ms</p>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Suite Runs - Takes 2 columns */}
        <div className="lg:col-span-2 bg-[var(--color-surface-raised)] rounded-xl border border-[var(--color-border-subtle)]">
          <div className="flex items-center justify-between p-5 border-b border-[var(--color-border-subtle)]">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-[var(--color-status-info-bg)] flex items-center justify-center">
                <Layers className="w-4 h-4 text-[var(--color-status-info)]" />
              </div>
              <h2 className="font-semibold text-[var(--color-content-primary)]">Recent Suite Runs</h2>
            </div>
            <button
              onClick={() => navigate('/suite-runs')}
              className="text-sm text-primary hover:underline flex items-center gap-1"
            >
              View all <ChevronRight className="w-4 h-4" />
            </button>
          </div>

          {recentRuns.length > 0 ? (
            <div className="divide-y divide-[var(--color-border-subtle)]">
              {recentRuns.slice(0, 5).map((run) => (
                <div
                  key={run.id}
                  onClick={() => navigate(`/suite-runs/${run.id}`)}
                  className="flex items-center justify-between p-4 hover:bg-[var(--color-interactive-hover)] cursor-pointer transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                      run.status === 'completed' ? 'bg-[var(--color-status-success-bg)]' :
                      run.status === 'running' ? 'bg-[var(--color-status-info-bg)]' :
                      run.status === 'failed' ? 'bg-[var(--color-status-danger-bg)]' : 'bg-[var(--color-surface-inset)]'
                    }`}>
                      {run.status === 'completed' ? <CheckCircle className="w-5 h-5 text-[var(--color-status-success)]" /> :
                       run.status === 'running' ? <Play className="w-5 h-5 text-[var(--color-status-info)]" /> :
                       run.status === 'failed' ? <XCircle className="w-5 h-5 text-[var(--color-status-danger)]" /> :
                       <Clock className="w-5 h-5 text-[var(--color-content-muted)]" />}
                    </div>
                    <div>
                      <p className="font-medium text-[var(--color-content-primary)]">{run.suiteName || 'Test Suite'}</p>
                      <p className="text-xs text-[var(--color-content-muted)]">
                        {run.totalTests || 0} tests • {run.languageCode || 'en-US'}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <StatusBadge status={run.status} />
                      <p className="text-xs text-[var(--color-content-muted)] mt-1">
                        {run.createdAt ? new Date(run.createdAt).toLocaleString() : '—'}
                      </p>
                    </div>
                    <ChevronRight className="w-4 h-4 text-[var(--color-border-default)]" />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-8 text-center">
              <Layers className="w-10 h-10 text-[var(--color-border-default)] mx-auto mb-3" />
              <p className="text-[var(--color-content-muted)] mb-2">No recent suite runs</p>
              <button
                onClick={() => navigate('/test-suites')}
                className="text-sm text-primary hover:underline"
              >
                Run your first test suite
              </button>
            </div>
          )}
        </div>

        {/* Right Column - Defects & Validation */}
        <div className="space-y-6">
          {/* Defect Breakdown */}
          <div className="bg-[var(--color-surface-raised)] rounded-xl border border-[var(--color-border-subtle)]">
            <div className="flex items-center gap-3 p-5 border-b border-[var(--color-border-subtle)]">
              <div className="w-8 h-8 rounded-lg bg-[var(--color-status-danger-bg)] flex items-center justify-center">
                <Bug className="w-4 h-4 text-[var(--color-status-danger)]" />
              </div>
              <h2 className="font-semibold text-[var(--color-content-primary)]">Defect Breakdown</h2>
            </div>

            <div className="p-5">
              {defects.open > 0 ? (
                <div className="space-y-3">
                  {defects.critical > 0 && (
                    <div className="flex items-center justify-between p-3 bg-[var(--color-status-danger-bg)] rounded-lg border border-[var(--color-status-danger)]/20">
                      <div className="flex items-center gap-2">
                        <span className="w-2 h-2 bg-[var(--color-status-danger)] rounded-full" />
                        <span className="text-sm font-medium text-[var(--color-status-danger)]">Critical</span>
                      </div>
                      <span className="text-lg font-bold text-[var(--color-status-danger)]">{defects.critical}</span>
                    </div>
                  )}
                  {defects.high > 0 && (
                    <div className="flex items-center justify-between p-3 bg-[var(--color-status-warning-bg)] rounded-lg border border-[var(--color-status-warning)]/20">
                      <div className="flex items-center gap-2">
                        <span className="w-2 h-2 bg-[var(--color-status-warning)] rounded-full" />
                        <span className="text-sm font-medium text-[var(--color-status-warning)]">High</span>
                      </div>
                      <span className="text-lg font-bold text-[var(--color-status-warning)]">{defects.high}</span>
                    </div>
                  )}
                  {defects.medium > 0 && (
                    <div className="flex items-center justify-between p-3 bg-[var(--color-status-warning-bg)] rounded-lg border border-[var(--color-status-warning)]/20">
                      <div className="flex items-center gap-2">
                        <span className="w-2 h-2 bg-[var(--color-status-warning)] rounded-full" />
                        <span className="text-sm font-medium text-[var(--color-status-warning)]">Medium</span>
                      </div>
                      <span className="text-lg font-bold text-[var(--color-status-warning)]">{defects.medium}</span>
                    </div>
                  )}
                  {defects.low > 0 && (
                    <div className="flex items-center justify-between p-3 bg-[var(--color-surface-inset)] rounded-lg border border-[var(--color-border-default)]">
                      <div className="flex items-center gap-2">
                        <span className="w-2 h-2 bg-[var(--color-content-muted)] rounded-full" />
                        <span className="text-sm font-medium text-[var(--color-content-secondary)]">Low</span>
                      </div>
                      <span className="text-lg font-bold text-[var(--color-content-secondary)]">{defects.low}</span>
                    </div>
                  )}
                  <button
                    onClick={() => navigate('/defects')}
                    className="w-full mt-2 text-sm text-primary hover:underline flex items-center justify-center gap-1"
                  >
                    View all defects <ArrowRight className="w-3 h-3" />
                  </button>
                </div>
              ) : (
                <div className="text-center py-4">
                  <CheckCircle className="w-8 h-8 text-[var(--color-status-success)] mx-auto mb-2" />
                  <p className="text-sm text-[var(--color-content-muted)]">No open defects</p>
                </div>
              )}
            </div>
          </div>

          {/* AI Validation */}
          <div className="bg-[var(--color-surface-raised)] rounded-xl border border-[var(--color-border-subtle)]">
            <div className="flex items-center gap-3 p-5 border-b border-[var(--color-border-subtle)]">
              <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
                <Zap className="w-4 h-4 text-primary" />
              </div>
              <h2 className="font-semibold text-[var(--color-content-primary)]">AI Validation</h2>
            </div>

            <div className="p-5">
              {/* Main accuracy metric */}
              <div className="text-center mb-4">
                <div className="relative inline-flex items-center justify-center">
                  <svg className="w-24 h-24 transform -rotate-90">
                    <circle
                      cx="48"
                      cy="48"
                      r="40"
                      className="stroke-[var(--color-border-default)]"
                      strokeWidth="8"
                      fill="none"
                    />
                    <circle
                      cx="48"
                      cy="48"
                      r="40"
                      stroke="url(#gradient)"
                      strokeWidth="8"
                      fill="none"
                      strokeLinecap="round"
                      strokeDasharray={`${(validation.overallAccuracyPct || 0) * 2.51} 251`}
                    />
                    <defs>
                      <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" stopColor="#2A6B6E" />
                        <stop offset="100%" stopColor="#11484D" />
                      </linearGradient>
                    </defs>
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-xl font-bold text-[var(--color-content-primary)]">
                      {validation.overallAccuracyPct || 0}%
                    </span>
                  </div>
                </div>
                <p className="text-xs text-[var(--color-content-muted)] mt-1">Human Agreement Rate</p>
              </div>

              {/* Stats grid */}
              <div className="grid grid-cols-2 gap-2">
                <div className="p-2 bg-[var(--color-surface-inset)] rounded-lg text-center">
                  <p className="text-lg font-semibold text-[var(--color-content-primary)]">
                    {validation.totalValidations || 0}
                  </p>
                  <p className="text-xs text-[var(--color-content-muted)]">Validations</p>
                </div>
                <div className="p-2 bg-[var(--color-surface-inset)] rounded-lg text-center">
                  <p className="text-lg font-semibold text-[var(--color-content-primary)]">
                    {validation.humanReviews || 0}
                  </p>
                  <p className="text-xs text-[var(--color-content-muted)]">Reviews</p>
                </div>
              </div>

              {/* Time saved */}
              {(validation.timeSavedHours || 0) > 0 && (
                <div className="mt-3 p-2 bg-primary/5 rounded-lg border border-primary/10">
                  <div className="flex items-center gap-2 justify-center">
                    <Clock className="w-3 h-3 text-primary" />
                    <span className="text-xs text-primary font-medium">
                      {validation.timeSavedHours?.toFixed(1)}h saved
                    </span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Real-time Execution Status */}
      <div className="bg-[var(--color-surface-raised)] rounded-xl border border-[var(--color-border-subtle)] p-5">
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-[var(--color-status-info-bg)] flex items-center justify-center">
              <Activity className="w-4 h-4 text-[var(--color-status-info)]" />
            </div>
            <h2 className="font-semibold text-[var(--color-content-primary)]">Execution Pipeline</h2>
          </div>
          <div className="flex items-center gap-2 text-sm text-[var(--color-content-muted)]">
            <span className="w-2 h-2 bg-[var(--color-status-success)] rounded-full animate-pulse" />
            Live
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="p-4 bg-[var(--color-status-success-bg)] rounded-xl border border-[var(--color-status-success)]/20">
            <div className="flex items-center gap-2 mb-2">
              <CheckCircle className="w-4 h-4 text-[var(--color-status-success)]" />
              <span className="text-sm text-[var(--color-status-success)] font-medium">Passed</span>
            </div>
            <p className="text-2xl font-bold text-[var(--color-status-success)]">{realTime.testsPassed || 0}</p>
          </div>

          <div className="p-4 bg-[var(--color-status-danger-bg)] rounded-xl border border-[var(--color-status-danger)]/20">
            <div className="flex items-center gap-2 mb-2">
              <XCircle className="w-4 h-4 text-[var(--color-status-danger)]" />
              <span className="text-sm text-[var(--color-status-danger)] font-medium">Failed</span>
            </div>
            <p className="text-2xl font-bold text-[var(--color-status-danger)]">{realTime.testsFailed || 0}</p>
          </div>

          <div className="p-4 bg-[var(--color-status-warning-bg)] rounded-xl border border-[var(--color-status-warning)]/20">
            <div className="flex items-center gap-2 mb-2">
              <Eye className="w-4 h-4 text-[var(--color-status-warning)]" />
              <span className="text-sm text-[var(--color-status-warning)] font-medium">Under Review</span>
            </div>
            <p className="text-2xl font-bold text-[var(--color-status-warning)]">{realTime.underReview || 0}</p>
          </div>

          <div className="p-4 bg-[var(--color-status-info-bg)] rounded-xl border border-[var(--color-status-info)]/20">
            <div className="flex items-center gap-2 mb-2">
              <Clock className="w-4 h-4 text-[var(--color-status-info)]" />
              <span className="text-sm text-[var(--color-status-info)] font-medium">Queued</span>
            </div>
            <p className="text-2xl font-bold text-[var(--color-status-info)]">{realTime.queued || 0}</p>
          </div>
        </div>

        {/* Progress bar */}
        <div className="mt-5">
          <div className="flex items-center justify-between text-sm mb-2">
            <span className="text-[var(--color-content-muted)]">Overall Progress</span>
            <span className="font-medium text-[var(--color-content-secondary)]">{realTime.progressPct || 0}%</span>
          </div>
          <div className="h-2 bg-[var(--color-surface-inset)] rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-[#2A6B6E] to-[#11484D] transition-all duration-500"
              style={{ width: `${realTime.progressPct || 0}%` }}
            />
          </div>
        </div>
      </div>

      {/* Edge Cases Section */}
      {(edgeCases.total > 0) && (
        <div className="bg-[var(--color-surface-raised)] rounded-xl border border-[var(--color-border-subtle)] p-5">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-[var(--color-status-warning-bg)] flex items-center justify-center">
                <AlertTriangle className="w-4 h-4 text-[var(--color-status-warning)]" />
              </div>
              <h2 className="font-semibold text-[var(--color-content-primary)]">Edge Cases</h2>
            </div>
            <button
              onClick={() => navigate('/edge-cases')}
              className="text-sm text-primary hover:underline flex items-center gap-1"
            >
              View all <ChevronRight className="w-4 h-4" />
            </button>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 bg-[var(--color-status-warning-bg)] rounded-xl">
              <p className="text-2xl font-bold text-[var(--color-status-warning)]">{edgeCases.total - edgeCases.resolved}</p>
              <p className="text-sm text-[var(--color-status-warning)]">Active</p>
            </div>
            <div className="p-4 bg-[var(--color-status-success-bg)] rounded-xl">
              <p className="text-2xl font-bold text-[var(--color-status-success)]">{edgeCases.resolved}</p>
              <p className="text-sm text-[var(--color-status-success)]">Resolved</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DashboardNew;
