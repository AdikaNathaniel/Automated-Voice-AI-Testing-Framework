import React, { useCallback, useEffect, useMemo, useState, useRef } from 'react';
import { RefreshCw, Plus, Network, AlertTriangle, TrendingUp, Play, Loader2, CheckCircle2, Clock, BarChart3 } from 'lucide-react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { listEdgeCases, searchEdgeCases } from '../../services/edgeCase.service';
import { listPatternGroups, getTrendingPatterns, triggerPatternAnalysis, checkAnalysisStatus } from '../../services/patternGroup.service';
import type { EdgeCase } from '../../types/edgeCase';
import type { PatternGroup } from '../../types/patternGroup';
import { LoadingSpinner, ErrorState, EmptyState, SearchInput, Dropdown } from '../../components/common';
import type { DropdownOption } from '../../components/common';

const DEFAULT_QUERY = { skip: 0, limit: 50 } as const

type TabType = 'edge-cases' | 'pattern-groups';

const formatCategory = (value: string) =>
  value
    .split('_')
    .map((segment) => segment.charAt(0).toUpperCase() + segment.slice(1))
    .join(' ')

const resolveSeverityColor = (severity: string) => {
  switch (severity.toLowerCase()) {
    case 'critical':
      return 'bg-[var(--color-status-danger-bg)] text-[var(--color-status-danger)]';
    case 'high':
      return 'bg-[var(--color-status-amber-bg)] text-[var(--color-status-amber)]';
    case 'medium':
      return 'bg-[var(--color-status-warning-bg)] text-[var(--color-status-warning)]';
    case 'low':
      return 'bg-[var(--color-status-success-bg)] text-[var(--color-status-success)]';
    default:
      return 'bg-[var(--color-interactive-hover)] text-[var(--color-content-secondary)]';
  }
};

const resolveStatusIcon = (status: string) => {
  switch (status.toLowerCase()) {
    case 'active':
      return <AlertTriangle className="w-4 h-4 text-[var(--color-status-warning)]" />;
    case 'resolved':
      return <CheckCircle2 className="w-4 h-4 text-[var(--color-status-success)]" />;
    case 'monitoring':
      return <Clock className="w-4 h-4 text-[var(--color-status-info)]" />;
    default:
      return null;
  }
};

const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
};

const EdgeCaseLibrary: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();

  // Tab state from URL
  const activeTab = (searchParams.get('tab') as TabType) || 'edge-cases';

  // Edge Cases state
  const [edgeCases, setEdgeCases] = useState<EdgeCase[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  // Pattern Groups state
  const [patterns, setPatterns] = useState<PatternGroup[]>([]);
  const [trendingPatterns, setTrendingPatterns] = useState<PatternGroup[]>([]);
  const [patternsLoading, setPatternsLoading] = useState(false);
  const [patternsError, setPatternsError] = useState<string | null>(null);
  const [patternStatusFilter, setPatternStatusFilter] = useState<string>('active');

  // Pattern analysis state
  const [analysisRunning, setAnalysisRunning] = useState(false);
  const [analysisMessage, setAnalysisMessage] = useState<string>('');
  const [analysisError, setAnalysisError] = useState<string | null>(null);

  // Pattern group filter for edge cases
  const [patternGroupFilter, setPatternGroupFilter] = useState<string>('');
  const [allPatterns, setAllPatterns] = useState<PatternGroup[]>([]);

  const setActiveTab = (tab: TabType) => {
    setSearchParams({ tab });
  };

  // Fetch edge cases
  const fetchEdgeCases = useCallback(
    async (options?: { query?: string; patternGroupId?: string }) => {
      setLoading(true);
      setError(null);

      const filters = options?.patternGroupId
        ? { patternGroupId: options.patternGroupId }
        : {};

      try {
        if (options?.query) {
          const response = await searchEdgeCases({
            query: options.query,
            skip: DEFAULT_QUERY.skip,
            limit: DEFAULT_QUERY.limit,
            ...filters,
          });
          setEdgeCases(response.items);
        } else {
          const response = await listEdgeCases({
            ...DEFAULT_QUERY,
            filters,
          });
          setEdgeCases(response.items);
        }
      } catch (err: unknown) {
        const message = err instanceof Error ? err.message : 'Failed to load edge cases';
        setError(message);
        setEdgeCases([]);
      } finally {
        setLoading(false);
      }
    },
    []
  );

  // Fetch pattern groups
  const fetchPatterns = useCallback(async () => {
    setPatternsLoading(true);
    setPatternsError(null);

    try {
      const [patternsResponse, trendingResponse] = await Promise.all([
        listPatternGroups({
          status: patternStatusFilter,
          skip: 0,
          limit: 50,
        }),
        getTrendingPatterns({ days: 7, limit: 5 }),
      ]);

      setPatterns(patternsResponse.items);
      setTrendingPatterns(trendingResponse);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to load pattern groups';
      setPatternsError(message);
      setPatterns([]);
      setTrendingPatterns([]);
    } finally {
      setPatternsLoading(false);
    }
  }, [patternStatusFilter]);

  // Fetch all patterns for filter dropdown
  const fetchAllPatterns = useCallback(async () => {
    try {
      const response = await listPatternGroups({ limit: 100 });
      setAllPatterns(response.items);
    } catch (err) {
      console.error('Failed to fetch patterns for filter:', err);
    }
  }, []);

  // Fetch patterns list for filter dropdown on mount
  useEffect(() => {
    fetchAllPatterns();
  }, [fetchAllPatterns]);

  // Fetch patterns on mount for tab count, and refetch when tab becomes active or filter changes
  useEffect(() => {
    fetchPatterns();
  }, [fetchPatterns]);

  // Debounce timer ref
  const searchTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Debounced search effect - triggers search as user types
  useEffect(() => {
    // Clear any existing timeout
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }

    // Set up debounced search (300ms delay)
    searchTimeoutRef.current = setTimeout(() => {
      const trimmed = searchTerm.trim();
      fetchEdgeCases({
        query: trimmed || undefined,
        patternGroupId: patternGroupFilter || undefined,
      });
    }, 300);

    // Cleanup on unmount or when dependencies change
    return () => {
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current);
      }
    };
  }, [searchTerm, patternGroupFilter, fetchEdgeCases]);

  const handleSearchSubmit = useCallback(
    async (event: React.FormEvent<HTMLFormElement>) => {
      event.preventDefault();
      // Clear debounce timer and search immediately
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current);
      }
      const trimmed = searchTerm.trim();
      await fetchEdgeCases({
        query: trimmed || undefined,
        patternGroupId: patternGroupFilter || undefined,
      });
    },
    [fetchEdgeCases, searchTerm, patternGroupFilter]
  );

  const handleTriggerAnalysis = async () => {
    setAnalysisRunning(true);
    setAnalysisError(null);
    setAnalysisMessage('Starting pattern analysis...');

    try {
      const response = await triggerPatternAnalysis({
        lookback_days: 7,
        min_pattern_size: 3,
        similarity_threshold: 0.85,
      });

      setAnalysisMessage(response.message);

      const pollInterval = setInterval(async () => {
        try {
          const statusResponse = await checkAnalysisStatus(response.task_id);

          if (statusResponse.status === 'SUCCESS') {
            clearInterval(pollInterval);
            setAnalysisRunning(false);

            if (statusResponse.result) {
              const result = statusResponse.result;
              setAnalysisMessage(`Analysis complete! Found ${result.patterns_discovered || 0} patterns.`);
            } else {
              setAnalysisMessage('Analysis completed successfully!');
            }

            setTimeout(() => {
              fetchPatterns();
              setAnalysisMessage('');
            }, 2000);
          } else if (statusResponse.status === 'FAILURE') {
            clearInterval(pollInterval);
            setAnalysisRunning(false);
            setAnalysisError(statusResponse.error || 'Analysis failed');
          } else {
            setAnalysisMessage(statusResponse.message || 'Analysis in progress...');
          }
        } catch (err) {
          console.error('Error checking analysis status:', err);
        }
      }, 2000);

      setTimeout(() => {
        clearInterval(pollInterval);
        if (analysisRunning) {
          setAnalysisRunning(false);
          setAnalysisError('Analysis timeout');
        }
      }, 300000);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to trigger analysis';
      setAnalysisError(message);
      setAnalysisRunning(false);
    }
  };

  // Edge cases are now filtered server-side via pattern_group_id parameter
  const filteredEdgeCases = edgeCases;

  const groupedByCategory = useMemo(() => {
    const groups = new Map<string, EdgeCase[]>()

    filteredEdgeCases.forEach((edgeCase) => {
      const category = edgeCase.category ?? 'uncategorized'
      if (!groups.has(category)) {
        groups.set(category, [])
      }
      groups.get(category)?.push(edgeCase)
    })

    return Array.from(groups.entries()).sort(([a], [b]) => a.localeCompare(b))
  }, [filteredEdgeCases])

  const handleRefresh = () => {
    if (activeTab === 'edge-cases') {
      fetchEdgeCases({
        patternGroupId: patternGroupFilter || undefined,
      });
    } else {
      fetchPatterns();
    }
  };

  const handlePatternClick = (patternId: string) => {
    navigate(`/pattern-groups/${patternId}`);
  };

  return (
    <>
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-bold text-[var(--color-content-primary)] flex items-center gap-3">
            <AlertTriangle className="w-6 h-6" style={{ color: '#2A6B6E' }} />
            Edge Case Library
          </h1>
          <p className="text-sm text-[var(--color-content-muted)] mt-1">
            {activeTab === 'edge-cases'
              ? 'Browse known conversational edge cases grouped by category.'
              : 'LLM-generated patterns from edge case analysis.'}
          </p>
        </div>
        <div className="flex gap-3 items-center">
          <button
            className="px-4 py-2.5 rounded-lg text-sm font-semibold transition-all inline-flex items-center gap-2 bg-[var(--color-status-purple-bg)] text-[var(--color-status-purple)] border border-[var(--color-status-purple)] hover:bg-[var(--color-status-purple-bg)]"
            onClick={() => navigate('/edge-cases/analytics')}
          >
            <BarChart3 size={14} /> Analytics
          </button>
          {activeTab === 'edge-cases' && (
            <button
              className="px-4 py-2.5 rounded-lg text-sm font-semibold transition-all inline-flex items-center gap-2 text-white hover:shadow-lg hover:-translate-y-0.5"
              style={{ background: 'linear-gradient(135deg, #2A6B6E 0%, #11484D 100%)' }}
              onClick={() => navigate('/edge-cases/new')}
            >
              <Plus size={14} /> New Edge Case
            </button>
          )}
          {activeTab === 'pattern-groups' && (
            <button
              onClick={handleTriggerAnalysis}
              disabled={analysisRunning}
              className="px-4 py-2.5 rounded-lg text-sm font-semibold transition-all inline-flex items-center gap-2 text-white hover:shadow-lg hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed"
              style={{ background: 'linear-gradient(135deg, #2A6B6E 0%, #11484D 100%)' }}
            >
              {analysisRunning ? (
                <>
                  <Loader2 size={14} className="animate-spin" />
                  Running...
                </>
              ) : (
                <>
                  <Play size={14} />
                  Run Analysis
                </>
              )}
            </button>
          )}
          <button
            className="p-2.5 rounded-lg text-sm font-semibold transition-all inline-flex items-center gap-2 bg-[var(--color-surface-inset)] text-[var(--color-content-secondary)] border border-[var(--color-border-default)] hover:bg-[var(--color-interactive-active)]"
            onClick={handleRefresh}
          >
            <RefreshCw size={18} />
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-[var(--color-surface-raised)] rounded-xl shadow-sm border border-[var(--color-border-default)] mb-6">
        <div className="px-6 border-b border-[var(--color-border-default)]">
          <nav className="-mb-px flex space-x-8 overflow-x-auto">
            <button
              onClick={() => setActiveTab('edge-cases')}
              className={`py-3 px-1 border-b-2 font-medium text-sm flex items-center gap-2 transition-colors ${
                activeTab === 'edge-cases'
                  ? 'border-primary text-primary'
                  : 'border-transparent text-[var(--color-content-muted)] hover:text-[var(--color-content-secondary)] hover:border-[var(--color-border-default)]'
              }`}
            >
              <AlertTriangle size={16} />
              Edge Cases
              <span className="ml-1 px-2 py-0.5 text-xs rounded-full bg-[var(--color-surface-inset)] text-[var(--color-content-secondary)]">
                {edgeCases.length}
              </span>
            </button>
            <button
              onClick={() => setActiveTab('pattern-groups')}
              className={`py-3 px-1 border-b-2 font-medium text-sm flex items-center gap-2 transition-colors ${
                activeTab === 'pattern-groups'
                  ? 'border-primary text-primary'
                  : 'border-transparent text-[var(--color-content-muted)] hover:text-[var(--color-content-secondary)] hover:border-[var(--color-border-default)]'
              }`}
            >
              <Network size={16} />
              Pattern Groups
              <span className="ml-1 px-2 py-0.5 text-xs rounded-full bg-[var(--color-surface-inset)] text-[var(--color-content-secondary)]">
                {patterns.length}
              </span>
            </button>
          </nav>
        </div>
      </div>

      {/* Analysis Status Banner */}
      {activeTab === 'pattern-groups' && (analysisMessage || analysisError) && (
        <div className={`rounded-lg p-4 mb-5 ${
          analysisError
            ? 'bg-[var(--color-status-danger-bg)] border border-[var(--color-status-danger)]'
            : 'bg-[var(--color-status-info-bg)] border border-[var(--color-status-info)]'
        }`}>
          <div className="flex items-center">
            {analysisRunning && !analysisError && (
              <Loader2 className="w-5 h-5 mr-3 animate-spin text-[var(--color-status-info)]" />
            )}
            {analysisError && (
              <AlertTriangle className="w-5 h-5 mr-3 text-[var(--color-status-danger)]" />
            )}
            {!analysisRunning && !analysisError && analysisMessage && (
              <CheckCircle2 className="w-5 h-5 mr-3 text-[var(--color-status-success)]" />
            )}
            <p className={analysisError ? 'text-[var(--color-status-danger)]' : 'text-[var(--color-status-info)]'}>
              {analysisError || analysisMessage}
            </p>
          </div>
        </div>
      )}

      {/* Edge Cases Tab Content */}
      {activeTab === 'edge-cases' && (
        <>
          {/* Search and Filters */}
          <div className="bg-[var(--color-surface-raised)] p-4 rounded-xl mb-5 shadow-sm">
            <div className="flex flex-col sm:flex-row gap-3 sm:items-center">
              <form onSubmit={handleSearchSubmit}>
                <SearchInput
                  id="edge-case-search"
                  value={searchTerm}
                  onChange={(event) => setSearchTerm(event.target.value)}
                  placeholder="Search by keyword, tags, or description"
                />
              </form>

              {/* Pattern Group Filter */}
              <Dropdown
                value={patternGroupFilter}
                onChange={setPatternGroupFilter}
                placeholder="All Patterns"
                options={[
                  { value: '', label: 'All Patterns' },
                  ...allPatterns.map((pattern): DropdownOption => ({
                    value: pattern.id,
                    label: `${pattern.name} (${pattern.occurrence_count})`,
                  })),
                ]}
              />
            </div>
          </div>

          {loading ? (
            <LoadingSpinner message="Loading Edge Cases..." />
          ) : error ? (
            <ErrorState
              title="Unable to load edge cases"
              message={error}
              variant="alert"
            />
          ) : groupedByCategory.length === 0 ? (
            <EmptyState
              title="No Edge Cases Found"
              description="Try adjusting your search criteria."
              icon="search"
            />
          ) : (
            <div className="flex flex-col gap-6">
              {groupedByCategory.map(([category, items]) => (
                <div
                  key={category}
                  className="bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-sm"
                >
                  <h2 className="text-xl font-bold text-[var(--color-content-primary)] mb-4">
                    {formatCategory(category)} <span className="text-[var(--color-content-muted)] text-base">({items.length})</span>
                  </h2>

                  <div className="flex flex-col gap-4">
                    {items.map((edgeCase) => (
                      <div
                        key={edgeCase.id}
                        className="p-4 bg-[var(--color-surface-inset)] rounded-lg hover:shadow-md transition-all cursor-pointer"
                        onClick={() => navigate(`/edge-cases/${edgeCase.id}`)}
                      >
                        <div className="flex items-center justify-between mb-2">
                          <h3 className="text-base font-semibold text-[var(--color-content-primary)]">{edgeCase.title}</h3>
                          {edgeCase.severity && (
                            <span className={`px-2.5 py-1 rounded-md text-xs font-semibold ${resolveSeverityColor(edgeCase.severity)} capitalize`}>
                              {edgeCase.severity}
                            </span>
                          )}
                        </div>
                        {edgeCase.description && <p className="text-sm text-[var(--color-content-secondary)] mb-2">{edgeCase.description}</p>}
                        {edgeCase.tags.length > 0 && (
                          <div className="flex gap-2 flex-wrap mt-2">
                            {edgeCase.tags.map((tag) => (
                              <span key={tag} className="px-2 py-1 bg-[var(--color-interactive-active)] rounded-md text-xs text-[var(--color-content-secondary)]">
                                {tag}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {/* Pattern Groups Tab Content */}
      {activeTab === 'pattern-groups' && (
        <>
          {/* Pattern Status Filter */}
          <div className="bg-[var(--color-surface-raised)] p-4 rounded-xl mb-5 shadow-sm">
            <div className="flex gap-4">
              {['active', 'resolved', 'monitoring'].map((status) => (
                <button
                  key={status}
                  onClick={() => setPatternStatusFilter(status)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    patternStatusFilter === status
                      ? 'bg-primary/10 text-primary border border-primary/30'
                      : 'bg-[var(--color-surface-inset)] text-[var(--color-content-secondary)] hover:bg-[var(--color-interactive-active)]'
                  }`}
                >
                  {status.charAt(0).toUpperCase() + status.slice(1)}
                </button>
              ))}
            </div>
          </div>

          {patternsLoading ? (
            <LoadingSpinner message="Loading Pattern Groups..." />
          ) : patternsError ? (
            <ErrorState
              title="Unable to load pattern groups"
              message={patternsError}
              variant="alert"
            />
          ) : (
            <>
              {/* Trending Patterns */}
              {trendingPatterns.length > 0 && (
                <div className="bg-gradient-to-r from-[var(--color-status-info-bg)] to-[var(--color-status-indigo-bg)] border border-[var(--color-status-info)] rounded-xl p-5 mb-5">
                  <div className="flex items-center mb-4">
                    <TrendingUp className="w-5 h-5 text-[var(--color-status-info)] mr-2" />
                    <h2 className="text-lg font-semibold text-[var(--color-content-primary)]">
                      Trending Patterns (Last 7 Days)
                    </h2>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-3">
                    {trendingPatterns.map((pattern) => (
                      <div
                        key={pattern.id}
                        onClick={() => handlePatternClick(pattern.id)}
                        className="bg-[var(--color-surface-raised)] rounded-lg p-3 cursor-pointer hover:shadow-md transition-shadow"
                      >
                        <div className="flex items-start justify-between mb-2">
                          <h3 className="font-medium text-[var(--color-content-primary)] text-sm line-clamp-1">
                            {pattern.name}
                          </h3>
                          <span className={`px-2 py-0.5 rounded text-xs font-medium ${resolveSeverityColor(pattern.severity)}`}>
                            {pattern.severity}
                          </span>
                        </div>
                        <p className="text-xs text-[var(--color-content-secondary)]">
                          {pattern.occurrence_count} occurrences
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Pattern List */}
              {patterns.length === 0 ? (
                <EmptyState
                  title={`No ${patternStatusFilter} patterns found`}
                  description='Click "Run Analysis" to detect patterns from edge cases.'
                  icon={<Network size={48} className="text-[var(--color-content-muted)]" />}
                />
              ) : (
                <div className="bg-[var(--color-surface-raised)] shadow-sm overflow-hidden rounded-xl">
                  <div className="divide-y divide-[var(--color-border-subtle)]">
                    {patterns.map((pattern) => (
                      <div
                        key={pattern.id}
                        onClick={() => handlePatternClick(pattern.id)}
                        className="p-5 hover:bg-[var(--color-interactive-hover)]/50 cursor-pointer transition-colors"
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center flex-wrap gap-2 mb-2">
                              {resolveStatusIcon(pattern.status)}
                              <h3 className="text-lg font-semibold text-[var(--color-content-primary)]">
                                {pattern.name}
                              </h3>
                              <span className={`px-2 py-1 rounded text-xs font-medium ${resolveSeverityColor(pattern.severity)}`}>
                                {pattern.severity}
                              </span>
                              {pattern.pattern_type && (
                                <span className="px-2 py-1 rounded text-xs font-medium bg-[var(--color-status-info-bg)] text-[var(--color-status-info)]">
                                  {pattern.pattern_type}
                                </span>
                              )}
                            </div>

                            {pattern.description && (
                              <p className="text-sm text-[var(--color-content-secondary)] mb-3 line-clamp-2">
                                {pattern.description}
                              </p>
                            )}

                            <div className="flex items-center flex-wrap gap-4 text-sm text-[var(--color-content-muted)]">
                              <span>
                                <strong>{pattern.occurrence_count}</strong> occurrences
                              </span>
                              <span>First: {formatDate(pattern.first_seen)}</span>
                              <span>Last: {formatDate(pattern.last_seen)}</span>
                            </div>

                            {pattern.suggested_actions && pattern.suggested_actions.length > 0 && (
                              <div className="mt-3">
                                <p className="text-xs font-medium text-[var(--color-content-secondary)] mb-1">
                                  Suggested Actions:
                                </p>
                                <ul className="list-disc list-inside text-xs text-[var(--color-content-secondary)] space-y-0.5">
                                  {pattern.suggested_actions.slice(0, 2).map((action, idx) => (
                                    <li key={idx}>{action}</li>
                                  ))}
                                </ul>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </>
      )}
    </>
  );
};

export default EdgeCaseLibrary
