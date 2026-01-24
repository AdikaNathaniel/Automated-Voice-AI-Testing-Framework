import React, { useEffect, useState, useMemo } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import {
  CheckCircle,
  Clock,
  Users,
  PlayCircle,
  RefreshCw,
  Award,
  LayoutGrid,
  List,
  ChevronRight,
  AlertCircle,
  Loader2,
} from 'lucide-react';
import {
  fetchValidationStats,
  claimValidation,
  fetchValidationQueue,
  fetchGroupedValidationQueue,
  fetchValidationById,
} from '../../store/slices/validationSlice';
import type { RootState, AppDispatch } from '../../store';
import { useSocket } from '../../hooks/useSocket';
import { StatCard } from '../../components/common';
import ValidationModal from '../../components/Validation/ValidationModal';

type StatusFilter = 'pending' | 'claimed' | 'completed';
type ViewMode = 'cards' | 'table';

/**
 * Get country flag emoji from language code
 * Converts language codes like "en-US", "fr-FR", "es-ES" to flag emojis
 */
const getCountryFlag = (languageCode: string): string => {
  if (!languageCode) return '🌐';

  // Extract country code (e.g., "US" from "en-US")
  const parts = languageCode.split('-');
  const countryCode = parts.length > 1 ? parts[1].toUpperCase() : parts[0].toUpperCase();

  // Convert country code to flag emoji
  // Flag emojis use regional indicator symbols (🇦-🇿)
  // Each letter is offset by 127397 from its ASCII code
  try {
    const codePoints = [...countryCode].map(char => 127397 + char.charCodeAt(0));
    return String.fromCodePoint(...codePoints);
  } catch {
    return '🌐'; // Fallback to globe if conversion fails
  }
};

/**
 * Get status dot color for human validation decision
 */
const getDecisionDotColor = (decision: string | null | undefined): string | null => {
  if (!decision) return null;
  switch (decision) {
    case 'pass':
      return 'bg-[var(--color-status-success)]';
    case 'edge_case':
      return 'bg-[var(--color-status-warning)]';
    case 'fail':
      return 'bg-[var(--color-status-danger)]';
    default:
      return null;
  }
};

const ValidationDashboardNew: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { on, off, emit } = useSocket();
  const [claiming, setClaiming] = useState(false);
  const [claimingId, setClaimingId] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('pending');
  const [viewMode, setViewMode] = useState<ViewMode>('cards');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [page, setPage] = useState(1);
  const pageSize = 20;

  const { stats, groupedQueue, groupedQueuePagination, loading, error } = useSelector(
    (state: RootState) => state.validation
  );

  // Initial data fetch
  useEffect(() => {
    dispatch(fetchValidationStats());
  }, [dispatch]);

  useEffect(() => {
    dispatch(fetchGroupedValidationQueue({ status: statusFilter, page, pageSize }));
  }, [dispatch, statusFilter, page]);

  // Reset page when status filter changes
  useEffect(() => {
    setPage(1);
  }, [statusFilter]);

  // WebSocket: Subscribe to validation queue updates
  useEffect(() => {
    const handleQueueUpdate = () => {
      // Refresh the queue when someone claims/completes a validation
      dispatch(fetchValidationStats());
      dispatch(fetchGroupedValidationQueue({ status: statusFilter, page, pageSize }));
    };

    // Subscribe to validation events
    emit('subscribe_validation_queue', {});
    on('validation_claimed', handleQueueUpdate);
    on('validation_completed', handleQueueUpdate);

    return () => {
      off('validation_claimed', handleQueueUpdate);
      off('validation_completed', handleQueueUpdate);
    };
  }, [on, off, emit, dispatch, statusFilter, page]);

  const handleClaimNext = async () => {
    try {
      setClaiming(true);
      const queueResult = await dispatch(
        fetchValidationQueue({ status: 'pending' })
      ).unwrap();

      if (Array.isArray(queueResult) && queueResult.length > 0) {
        await dispatch(claimValidation(queueResult[0].id)).unwrap();
        setIsModalOpen(true);
      } else {
        console.warn('No validation tasks available in queue');
      }
    } catch (err) {
      console.error('Failed to claim validation:', err);
    } finally {
      setClaiming(false);
    }
  };

  const handleStepClick = async (queueId: string, status: string) => {
    try {
      setClaimingId(queueId);
      if (status === 'pending') {
        await dispatch(claimValidation(queueId)).unwrap();
      } else {
        // For claimed/completed items, fetch the specific validation
        await dispatch(fetchValidationById(queueId)).unwrap();
      }
      setIsModalOpen(true);
    } catch (err) {
      console.error('Failed to open validation item:', err);
    } finally {
      setClaimingId(null);
    }
  };

  const handleExecutionClick = async (group: any) => {
    try {
      const firstStep = group.stepValidations?.[0];
      if (firstStep) {
        setClaimingId(group.executionId);
        if (firstStep.queueStatus === 'pending') {
          await dispatch(claimValidation(firstStep.queueId)).unwrap();
          // Emit event so other users' dashboards update
          emit('validation_claimed', { queueId: firstStep.queueId });
        } else {
          await dispatch(fetchValidationById(firstStep.queueId)).unwrap();
        }
        setIsModalOpen(true);
      }
    } catch (err) {
      console.error('Failed to open validation item:', err);
      setClaimingId(null);
    }
  };

  const handleModalClose = () => {
    setIsModalOpen(false);
    // Refresh the queue after closing modal
    handleRefresh();
  };

  const handleSubmitSuccess = () => {
    // Refresh stats and queue after successful submission
    handleRefresh();
  };

  const handleRefresh = () => {
    dispatch(fetchValidationStats());
    dispatch(fetchGroupedValidationQueue({ status: statusFilter, page, pageSize }));
  };

  const pendingCount = stats?.pendingCount || 0;
  const claimedByUser = statusFilter === 'claimed'
    ? (groupedQueue?.reduce((sum, group) => sum + (group.stepValidations?.length || 0), 0) || 0)
    : (stats?.claimedCount || 0);
  const completedCount = stats?.completedCount || 0;
  const accuracyRate = stats?.accuracyRate || 0;

  // Flatten grouped queue into individual validation items
  const flattenedQueue = useMemo(() => {
    if (!groupedQueue) return [];

    return groupedQueue.flatMap((group) =>
      (group.stepValidations || []).map((step: any) => ({
        ...step,
        scenarioName: group.scenarioName,
        scenarioId: group.scenarioId,
        executionId: group.executionId,
      }))
    );
  }, [groupedQueue]);

  if (loading && !stats) {
    return (
      <div className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-sm">
        <div className="flex flex-col items-center justify-center p-20">
          <div className="w-12 h-12 border-4 border-[var(--color-border-default)] rounded-full animate-spin mb-4 border-t-primary" />
          <div className="text-lg font-semibold text-[var(--color-content-primary)] mb-2">Loading Validation Dashboard...</div>
        </div>
      </div>
    );
  }

  const statusTabs = [
    {
      key: 'pending' as StatusFilter,
      label: 'Pending',
      count: pendingCount,
      icon: Clock,
      activeClass: 'bg-warning/10 text-warning border-warning',
      iconColor: 'text-warning',
    },
    {
      key: 'claimed' as StatusFilter,
      label: 'My Claimed',
      count: claimedByUser,
      icon: Users,
      activeClass: 'bg-info/10 text-info border-info',
      iconColor: 'text-info',
    },
    {
      key: 'completed' as StatusFilter,
      label: 'Completed',
      count: completedCount,
      icon: CheckCircle,
      activeClass: 'bg-success/10 text-success border-success',
      iconColor: 'text-success',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-[var(--color-content-primary)] flex items-center gap-3">
            <CheckCircle className="w-6 h-6" style={{ color: '#2A6B6E' }} />
            Validation Dashboard
          </h1>
          <p className="text-sm text-[var(--color-content-muted)] mt-1">AI-Assisted Validation Workflow</p>
        </div>
        <div className="flex gap-3 items-center">
          <button
            className="px-4 py-2.5 rounded-lg text-sm font-semibold transition-all inline-flex items-center gap-2 text-white hover:shadow-lg hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:translate-y-0 disabled:hover:shadow-none"
            style={{ background: 'linear-gradient(135deg, #2A6B6E 0%, #11484D 100%)' }}
            onClick={handleClaimNext}
            disabled={claiming || pendingCount === 0}
          >
            <PlayCircle size={16} />
            {claiming ? 'Claiming...' : 'Claim Next'}
          </button>
          <button
            className="p-2.5 rounded-lg text-sm font-semibold transition-all inline-flex items-center justify-center bg-[var(--color-surface-inset)] text-[var(--color-content-secondary)] border border-[var(--color-border-default)] hover:bg-[var(--color-interactive-hover)]"
            onClick={handleRefresh}
          >
            <RefreshCw size={18} className={loading ? 'animate-spin' : ''} />
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-lg flex items-center gap-3 bg-[var(--color-status-danger-bg)] text-[var(--color-status-danger)] border border-[var(--color-status-danger)]">
          <AlertCircle size={20} className="text-[var(--color-status-danger)] flex-shrink-0" />
          <span className="font-medium">{error}</span>
        </div>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Pending"
          value={pendingCount}
          icon={<Clock className="w-6 h-6" />}
          iconColor="text-warning"
          iconBg="bg-warning/10"
          valueColor="text-warning"
        />
        <StatCard
          title="Claimed"
          value={claimedByUser}
          icon={<Users className="w-6 h-6" />}
          iconColor="text-info"
          iconBg="bg-info/10"
          valueColor="text-info"
        />
        <StatCard
          title="Completed"
          value={completedCount}
          icon={<CheckCircle className="w-6 h-6" />}
          iconColor="text-success"
          iconBg="bg-success/10"
          valueColor="text-success"
        />
        <StatCard
          title="Accuracy"
          value={`${accuracyRate.toFixed(1)}%`}
          icon={<Award className="w-6 h-6" />}
          iconColor="text-white"
          iconBg="bg-gradient-to-br from-[#2A6B6E] to-[#11484D]"
          valueColor="text-primary"
        />
      </div>

      {/* Filters and Controls Bar */}
      <div className="bg-[var(--color-surface-raised)] rounded-xl shadow-sm border border-[var(--color-border-default)]">
        <div className="p-4 flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          {/* Status Tabs */}
          <div className="flex bg-[var(--color-surface-inset)] rounded-lg p-1 gap-1">
            {statusTabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = statusFilter === tab.key;
              return (
                <button
                  key={tab.key}
                  onClick={() => setStatusFilter(tab.key)}
                  className={`
                    flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all
                    ${isActive
                      ? `${tab.activeClass} border shadow-sm`
                      : 'text-[var(--color-content-muted)] hover:text-[var(--color-content-primary)] hover:bg-[var(--color-interactive-hover)] border border-transparent'
                    }
                  `}
                >
                  <Icon size={16} />
                  <span>{tab.label}</span>
                  <span className={`
                    px-2 py-0.5 rounded-full text-xs font-semibold
                    ${isActive ? 'bg-[var(--color-surface-raised)]/50' : 'bg-[var(--color-interactive-active)] text-[var(--color-content-secondary)]'}
                  `}>
                    {tab.count}
                  </span>
                </button>
              );
            })}
          </div>

          {/* Right side controls */}
          <div className="flex items-center gap-3">
            {/* View Toggle */}
            <div className="flex bg-[var(--color-surface-inset)] rounded-lg p-1 gap-1">
              <button
                onClick={() => setViewMode('cards')}
                className={`
                  p-2 rounded-md transition-all
                  ${viewMode === 'cards'
                    ? 'bg-[var(--color-surface-raised)] text-primary shadow-sm'
                    : 'text-[var(--color-content-muted)] hover:text-[var(--color-content-primary)]'
                  }
                `}
                title="Card view"
              >
                <LayoutGrid size={18} />
              </button>
              <button
                onClick={() => setViewMode('table')}
                className={`
                  p-2 rounded-md transition-all
                  ${viewMode === 'table'
                    ? 'bg-[var(--color-surface-raised)] text-primary shadow-sm'
                    : 'text-[var(--color-content-muted)] hover:text-[var(--color-content-primary)]'
                  }
                `}
                title="Table view"
              >
                <List size={18} />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Queue Content */}
      <div className="bg-[var(--color-surface-raised)] rounded-xl shadow-sm border border-[var(--color-border-default)]">
        <div className="p-4 border-b border-[var(--color-border-default)]">
          <h2 className="text-lg font-semibold text-[var(--color-content-primary)]">
            {statusFilter === 'pending' && 'Validation Queue'}
            {statusFilter === 'claimed' && 'My Claimed Items'}
            {statusFilter === 'completed' && 'Completed Items'}
          </h2>
          <p className="text-sm text-[var(--color-content-muted)] mt-0.5">
            {flattenedQueue.length} validation{flattenedQueue.length !== 1 ? 's' : ''} to review
          </p>
        </div>

        {flattenedQueue.length > 0 ? (
          viewMode === 'cards' ? (
            /* Card View - Individual validation items */
            <div className="p-4 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {flattenedQueue.map((item) => {
                const isClaimingThis = claimingId === item.queueId;
                const itemStatus = item.queueStatus || 'pending';
                const statusConfig: Record<string, { bg: string; text: string; label: string }> = {
                  pending: { bg: 'bg-warning/10', text: 'text-warning', label: 'Pending' },
                  claimed: { bg: 'bg-info/10', text: 'text-info', label: 'Claimed' },
                  completed: { bg: 'bg-success/10', text: 'text-success', label: 'Completed' },
                };
                const config = statusConfig[itemStatus] || statusConfig.pending;

                return (
                  <div
                    key={item.queueId}
                    className={`
                      relative p-4 rounded-xl border border-[var(--color-border-default)] bg-[var(--color-surface-raised)] shadow-sm
                      hover:shadow-md hover:border-primary/30 transition-all duration-200 cursor-pointer
                      ${isClaimingThis ? 'opacity-70 pointer-events-none' : ''}
                    `}
                    onClick={() => handleStepClick(item.queueId, item.queueStatus)}
                  >
                    {/* Loading Overlay */}
                    {isClaimingThis && (
                      <div className="absolute inset-0 bg-[var(--color-surface-raised)]/50 rounded-xl flex items-center justify-center z-10">
                        <Loader2 className="w-6 h-6 animate-spin text-primary" />
                      </div>
                    )}

                    {/* Header with Language Badge */}
                    <div className="flex items-start justify-between gap-3 mb-3">
                      <div className="flex items-center gap-2">
                        <div className="w-9 h-9 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0 text-2xl">
                          {getCountryFlag(item.languageCode || 'en-US')}
                        </div>
                        <div>
                          <span className="text-sm font-bold text-primary uppercase tracking-wide">
                            {item.languageCode || 'en-US'}
                          </span>
                          <p className="text-xs text-[var(--color-content-muted)]">Step {item.stepOrder}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {/* Human validation decision dot for completed items */}
                        {itemStatus === 'completed' && getDecisionDotColor((item as any).humanValidationDecision) && (
                          <div
                            className={`w-3 h-3 rounded-full ${getDecisionDotColor((item as any).humanValidationDecision)} ring-2 ring-[var(--color-surface-raised)]`}
                            title={`Decision: ${(item as any).humanValidationDecision?.replace('_', ' ')}`}
                          />
                        )}
                        <span className={`px-2.5 py-1 rounded-full text-xs font-semibold flex-shrink-0 ${config.bg} ${config.text}`}>
                          {config.label}
                        </span>
                      </div>
                    </div>

                    {/* Scenario Name */}
                    <h3 className="font-semibold text-[var(--color-content-primary)] truncate mb-2">
                      {item.scenarioName}
                    </h3>

                    {/* User Utterance */}
                    <div className="py-2 px-3 bg-[var(--color-surface-raised)] rounded-lg mb-3">
                      <p className="text-sm text-[var(--color-content-secondary)] italic line-clamp-2">
                        "{item.userUtterance}"
                      </p>
                    </div>

                    {/* AI Validation Status */}
                    <div className="space-y-2 mb-3">
                      {/* AI Review Status Badge */}
                      {item.reviewStatus && (
                        <div className="flex items-center justify-between text-xs">
                          <span className="text-[var(--color-content-muted)]">AI Review Status</span>
                          <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                            item.reviewStatus === 'auto_pass'
                              ? 'bg-[var(--color-status-emerald-bg)] text-[var(--color-status-emerald)]'
                              : item.reviewStatus === 'auto_fail'
                              ? 'bg-[var(--color-status-rose-bg)] text-[var(--color-status-rose)]'
                              : 'bg-[var(--color-status-amber-bg)] text-[var(--color-status-amber)]'
                          }`}>
                            {item.reviewStatus.replace(/_/g, ' ').replace(/auto /g, '')}
                          </span>
                        </div>
                      )}
                      {/* AI Decision Badge */}
                      {(item as any).finalDecision && (
                        <div className="flex items-center justify-between text-xs">
                          <span className="text-[var(--color-content-muted)]">AI Decision</span>
                          <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                            (item as any).finalDecision === 'pass'
                              ? 'bg-[var(--color-status-emerald-bg)] text-[var(--color-status-emerald)]'
                              : (item as any).finalDecision === 'fail'
                              ? 'bg-[var(--color-status-rose-bg)] text-[var(--color-status-rose)]'
                              : 'bg-[var(--color-surface-inset)] text-[var(--color-content-secondary)]'
                          }`}>
                            {(item as any).finalDecision}
                          </span>
                        </div>
                      )}
                    </div>

                    {/* Action */}
                    <div className="pt-3 border-t border-[var(--color-border-default)] flex items-center justify-end">
                      <span className="inline-flex items-center gap-1 text-xs text-primary font-medium">
                        {statusFilter === 'pending' ? 'Claim & Review' :
                         itemStatus === 'completed' ? 'View Details' : 'Continue'}
                        <ChevronRight size={14} />
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            /* Table View - Individual validation items */
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="bg-[var(--color-surface-inset)] border-b border-[var(--color-border-default)]">
                    <th className="text-left py-3 px-4 text-xs font-semibold text-[var(--color-content-muted)] uppercase tracking-wide">Language</th>
                    <th className="text-left py-3 px-4 text-xs font-semibold text-[var(--color-content-muted)] uppercase tracking-wide">Scenario</th>
                    <th className="text-left py-3 px-4 text-xs font-semibold text-[var(--color-content-muted)] uppercase tracking-wide">Utterance</th>
                    <th className="text-center py-3 px-4 text-xs font-semibold text-[var(--color-content-muted)] uppercase tracking-wide">AI Review</th>
                    <th className="text-center py-3 px-4 text-xs font-semibold text-[var(--color-content-muted)] uppercase tracking-wide">Status</th>
                    <th className="text-right py-3 px-4 text-xs font-semibold text-[var(--color-content-muted)] uppercase tracking-wide">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[var(--color-border-subtle)]">
                  {flattenedQueue.map((item) => {
                    const isClaimingThis = claimingId === item.queueId;
                    const itemStatus = item.queueStatus || 'pending';
                    const statusConfig: Record<string, { bg: string; text: string; label: string }> = {
                      pending: { bg: 'bg-warning/10', text: 'text-warning', label: 'Pending' },
                      claimed: { bg: 'bg-info/10', text: 'text-info', label: 'Claimed' },
                      completed: { bg: 'bg-success/10', text: 'text-success', label: 'Completed' },
                    };
                    const config = statusConfig[itemStatus] || statusConfig.pending;

                    return (
                      <tr
                        key={item.queueId}
                        className={`
                          hover:bg-[var(--color-interactive-hover)] transition-colors cursor-pointer
                          ${isClaimingThis ? 'opacity-50' : ''}
                        `}
                        onClick={() => handleStepClick(item.queueId, item.queueStatus)}
                      >
                        <td className="py-3 px-4">
                          <div className="flex items-center gap-2">
                            <span className="text-lg">
                              {getCountryFlag(item.languageCode || 'en-US')}
                            </span>
                            <span className="text-sm font-bold text-primary uppercase">
                              {item.languageCode || 'en-US'}
                            </span>
                          </div>
                        </td>
                        <td className="py-3 px-4">
                          <div className="font-medium text-[var(--color-content-primary)] flex items-center gap-2">
                            {isClaimingThis && <Loader2 size={14} className="animate-spin text-primary" />}
                            {item.scenarioName}
                          </div>
                          <div className="text-xs text-[var(--color-content-muted)]">Step {item.stepOrder}</div>
                        </td>
                        <td className="py-3 px-4 max-w-xs">
                          <span className="text-sm text-[var(--color-content-secondary)] italic truncate block">
                            "{item.userUtterance}"
                          </span>
                        </td>
                        <td className="py-3 px-4">
                          <div className="flex flex-col gap-1.5 items-center">
                            {/* Review Status Badge */}
                            {item.reviewStatus && (
                              <span className={`px-2 py-0.5 rounded-full text-xs font-medium whitespace-nowrap ${
                                item.reviewStatus === 'auto_pass'
                                  ? 'bg-[var(--color-status-emerald-bg)] text-[var(--color-status-emerald)]'
                                  : item.reviewStatus === 'auto_fail'
                                  ? 'bg-[var(--color-status-rose-bg)] text-[var(--color-status-rose)]'
                                  : 'bg-[var(--color-status-amber-bg)] text-[var(--color-status-amber)]'
                              }`}>
                                {item.reviewStatus.replace(/_/g, ' ').replace(/auto /g, '')}
                              </span>
                            )}
                            {/* AI Decision Badge */}
                            {(item as any).finalDecision && (
                              <span className={`px-2 py-0.5 rounded-full text-xs font-medium whitespace-nowrap ${
                                (item as any).finalDecision === 'pass'
                                  ? 'bg-[var(--color-status-emerald-bg)] text-[var(--color-status-emerald)]'
                                  : (item as any).finalDecision === 'fail'
                                  ? 'bg-[var(--color-status-rose-bg)] text-[var(--color-status-rose)]'
                                  : 'bg-[var(--color-surface-inset)] text-[var(--color-content-secondary)]'
                              }`}>
                                AI: {(item as any).finalDecision}
                              </span>
                            )}
                            {/* Show dash if neither is available */}
                            {!item.reviewStatus && !(item as any).finalDecision && (
                              <span className="text-[var(--color-content-muted)]">—</span>
                            )}
                          </div>
                        </td>
                        <td className="py-3 px-4 text-center">
                          <div className="flex items-center justify-center gap-2">
                            {/* Human validation decision dot for completed items */}
                            {itemStatus === 'completed' && getDecisionDotColor((item as any).humanValidationDecision) && (
                              <div
                                className={`w-2.5 h-2.5 rounded-full ${getDecisionDotColor((item as any).humanValidationDecision)} ring-2 ring-[var(--color-surface-raised)]`}
                                title={`Decision: ${(item as any).humanValidationDecision?.replace('_', ' ')}`}
                              />
                            )}
                            <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${config.bg} ${config.text}`}>
                              {config.label}
                            </span>
                          </div>
                        </td>
                        <td className="py-3 px-4 text-right">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleStepClick(item.queueId, item.queueStatus);
                            }}
                            disabled={isClaimingThis}
                            className="text-sm text-primary font-medium hover:underline inline-flex items-center gap-1 disabled:opacity-50"
                          >
                            {statusFilter === 'pending' ? 'Claim' :
                             itemStatus === 'completed' ? 'View' : 'Continue'}
                            <ChevronRight size={14} />
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )
        ) : (
          /* Empty State */
          <div className="py-16 px-4 text-center">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-[var(--color-surface-inset)] flex items-center justify-center">
              {statusFilter === 'pending' ? (
                <CheckCircle size={32} className="text-success" />
              ) : statusFilter === 'claimed' ? (
                <Users size={32} className="text-info" />
              ) : (
                <Clock size={32} className="text-[var(--color-content-muted)]" />
              )}
            </div>
            <h3 className="text-lg font-semibold text-[var(--color-content-primary)] mb-1">
              {statusFilter === 'pending' && 'All Caught Up!'}
              {statusFilter === 'claimed' && 'No Claimed Items'}
              {statusFilter === 'completed' && 'No Completed Items'}
            </h3>
            <p className="text-sm text-[var(--color-content-muted)] max-w-sm mx-auto">
              {statusFilter === 'pending' && 'There are no pending validations at the moment. Great job!'}
              {statusFilter === 'claimed' && 'You haven\'t claimed any validation items yet.'}
              {statusFilter === 'completed' && 'No validations have been completed yet.'}
            </p>
            {statusFilter === 'claimed' && pendingCount > 0 && (
              <button
                className="mt-4 px-4 py-2 text-sm font-medium text-primary hover:text-primary-dark transition-colors"
                onClick={() => setStatusFilter('pending')}
              >
                View {pendingCount} pending →
              </button>
            )}
          </div>
        )}
      </div>

      {/* Pagination Controls */}
      {groupedQueuePagination.totalPages > 1 && !loading && flattenedQueue.length > 0 && (
        <div className="bg-[var(--color-surface-raised)] rounded-xl p-4 shadow-sm border border-[var(--color-border-default)]">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="text-sm text-[var(--color-content-secondary)]">
              Showing {((page - 1) * pageSize) + 1} to {Math.min(page * pageSize, groupedQueuePagination.total)} of {groupedQueuePagination.total} items
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setPage(page - 1)}
                disabled={page === 1}
                className="px-4 py-2 border border-[var(--color-border-strong)] rounded-lg text-[var(--color-content-secondary)] bg-[var(--color-surface-raised)] hover:bg-[var(--color-interactive-hover)] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Previous
              </button>
              <span className="px-3 py-2 text-sm text-[var(--color-content-secondary)]">
                Page {page} of {groupedQueuePagination.totalPages}
              </span>
              <button
                onClick={() => setPage(page + 1)}
                disabled={page === groupedQueuePagination.totalPages}
                className="px-4 py-2 border border-[var(--color-border-strong)] rounded-lg text-[var(--color-content-secondary)] bg-[var(--color-surface-raised)] hover:bg-[var(--color-interactive-hover)] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Next
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Call to Action */}
      {pendingCount > 0 && statusFilter !== 'pending' && (
        <div
          className="rounded-xl p-8 text-center text-white"
          style={{ background: 'linear-gradient(135deg, #2A6B6E 0%, #11484D 100%)' }}
        >
          <h2 className="text-2xl font-bold mb-2">Ready to Validate?</h2>
          <p className="text-white/90 mb-6">
            {pendingCount} validation{pendingCount !== 1 ? 's' : ''} waiting for review
          </p>
          <button
            className="inline-flex items-center gap-2 px-6 py-3 bg-[var(--color-surface-overlay)] text-primary font-semibold rounded-lg hover:shadow-lg hover:-translate-y-0.5 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            onClick={handleClaimNext}
            disabled={claiming}
          >
            <PlayCircle size={18} />
            {claiming ? 'Claiming...' : 'Start Validating'}
          </button>
        </div>
      )}

      {/* Validation Modal */}
      <ValidationModal
        isOpen={isModalOpen}
        onClose={handleModalClose}
        onSubmitSuccess={handleSubmitSuccess}
      />
    </div>
  );
};

export default ValidationDashboardNew;
