/**
 * Pattern Group View - Displays LLM-generated pattern groups
 *
 * Shows patterns identified by the automated pattern recognition system,
 * with details about occurrence count, severity, and suggested actions.
 */

import React, { useCallback, useEffect, useState } from 'react';
import { TrendingUp, RefreshCw, AlertTriangle, CheckCircle2, Clock, Play, Loader2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { listPatternGroups, getTrendingPatterns, triggerPatternAnalysis, checkAnalysisStatus } from '../../services/patternGroup.service';
import type { PatternGroup } from '../../types/patternGroup';

const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
};

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

const PatternGroupView: React.FC = () => {
  const navigate = useNavigate();
  const [patterns, setPatterns] = useState<PatternGroup[]>([]);
  const [trendingPatterns, setTrendingPatterns] = useState<PatternGroup[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('active');

  // Pattern analysis state
  const [analysisRunning, setAnalysisRunning] = useState(false);
  const [analysisTaskId, setAnalysisTaskId] = useState<string | null>(null);
  const [analysisMessage, setAnalysisMessage] = useState<string>('');
  const [analysisError, setAnalysisError] = useState<string | null>(null);

  const fetchPatterns = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const [patternsResponse, trendingResponse] = await Promise.all([
        listPatternGroups({
          status: statusFilter,
          skip: 0,
          limit: 50,
        }),
        getTrendingPatterns({ days: 7, limit: 5 }),
      ]);

      setPatterns(patternsResponse.items);
      setTrendingPatterns(trendingResponse);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to load pattern groups';
      setError(message);
      setPatterns([]);
      setTrendingPatterns([]);
    } finally {
      setLoading(false);
    }
  }, [statusFilter]);

  useEffect(() => {
    let isMounted = true;

    const loadPatterns = async () => {
      try {
        if (!isMounted) return;
        await fetchPatterns();
      } finally {
        setLoading(false);
      }
    };

    loadPatterns();

    return () => {
      isMounted = false;
    };
  }, [fetchPatterns]);

  const handlePatternClick = (patternId: string) => {
    navigate(`/pattern-groups/${patternId}`);
  };

  const handleTriggerAnalysis = async () => {
    setAnalysisRunning(true);
    setAnalysisError(null);
    setAnalysisMessage('Starting pattern analysis...');

    try {
      // Trigger the analysis
      const response = await triggerPatternAnalysis({
        lookback_days: 7,
        min_pattern_size: 3,
        similarity_threshold: 0.85,
      });

      setAnalysisTaskId(response.task_id);
      setAnalysisMessage(response.message);

      // Poll for status
      const pollInterval = setInterval(async () => {
        try {
          const statusResponse = await checkAnalysisStatus(response.task_id);

          if (statusResponse.status === 'SUCCESS') {
            clearInterval(pollInterval);
            setAnalysisRunning(false);
            setAnalysisMessage('Analysis completed successfully!');
            setAnalysisTaskId(null);

            // Show results if available
            if (statusResponse.result) {
              const result = statusResponse.result;
              const message = `Analysis complete! Found ${result.patterns_discovered || 0} patterns. ${result.new_patterns || 0} new, ${result.updated_patterns || 0} updated.`;
              setAnalysisMessage(message);
            }

            // Refresh the pattern list after 2 seconds
            setTimeout(() => {
              fetchPatterns();
              setAnalysisMessage('');
            }, 2000);
          } else if (statusResponse.status === 'FAILURE') {
            clearInterval(pollInterval);
            setAnalysisRunning(false);
            setAnalysisError(statusResponse.error || 'Analysis failed');
            setAnalysisTaskId(null);
          } else {
            setAnalysisMessage(statusResponse.message || 'Analysis in progress...');
          }
        } catch (err) {
          // Continue polling on error
          console.error('Error checking analysis status:', err);
        }
      }, 2000); // Poll every 2 seconds

      // Set timeout to stop polling after 15 minutes
      setTimeout(() => {
        clearInterval(pollInterval);
        if (analysisRunning) {
          setAnalysisRunning(false);
          setAnalysisError('Analysis timeout - check logs for details');
          setAnalysisTaskId(null);
        }
      }, 900000); // 15 minutes timeout (allows for large datasets)
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to trigger analysis';
      setAnalysisError(message);
      setAnalysisRunning(false);
      setAnalysisTaskId(null);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-8 h-8 animate-spin text-[var(--color-status-info)]" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-[var(--color-status-danger-bg)] border border-[var(--color-status-danger)] rounded-lg p-4">
          <p className="text-[var(--color-status-danger)]">
            {error}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[var(--color-content-primary)]">
            Pattern Groups
          </h1>
          <p className="mt-1 text-sm text-[var(--color-content-muted)]">
            LLM-generated patterns from edge case analysis
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={handleTriggerAnalysis}
            disabled={analysisRunning}
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-[var(--color-status-info)] hover:bg-[var(--color-status-info-hover)] disabled:bg-[var(--color-content-muted)] disabled:cursor-not-allowed"
          >
            {analysisRunning ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Running...
              </>
            ) : (
              <>
                <Play className="w-4 h-4 mr-2" />
                Run Analysis
              </>
            )}
          </button>
          <button
            onClick={fetchPatterns}
            className="inline-flex items-center px-4 py-2 border border-[var(--color-border-strong)] rounded-md shadow-sm text-sm font-medium text-[var(--color-content-secondary)] bg-[var(--color-surface-raised)] hover:bg-[var(--color-interactive-hover)]"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </button>
        </div>
      </div>

      {/* Analysis Status Banner */}
      {(analysisMessage || analysisError) && (
        <div className={`rounded-lg p-4 ${
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
            {!analysisRunning && !analysisError && (
              <CheckCircle2 className="w-5 h-5 mr-3 text-[var(--color-status-success)]" />
            )}
            <p className={analysisError
              ? 'text-[var(--color-status-danger)]'
              : 'text-[var(--color-status-info)]'
            }>
              {analysisError || analysisMessage}
            </p>
          </div>
          {analysisTaskId && (
            <p className="mt-1 text-xs text-[var(--color-content-secondary)] ml-8">
              Task ID: {analysisTaskId}
            </p>
          )}
        </div>
      )}

      {/* Filter Tabs */}
      <div className="border-b border-[var(--color-border-default)]">
        <nav className="-mb-px flex space-x-8">
          {['active', 'resolved', 'monitoring'].map((status) => (
            <button
              key={status}
              onClick={() => setStatusFilter(status)}
              className={`
                py-2 px-1 border-b-2 font-medium text-sm
                ${
                  statusFilter === status
                    ? 'border-[var(--color-status-info)] text-[var(--color-status-info)]'
                    : 'border-transparent text-[var(--color-content-muted)] hover:text-[var(--color-content-secondary)] hover:border-[var(--color-border-default)]'
                }
              `}
            >
              {status.charAt(0).toUpperCase() + status.slice(1)}
            </button>
          ))}
        </nav>
      </div>

      {/* Trending Patterns */}
      {trendingPatterns.length > 0 && (
        <div className="bg-gradient-to-r from-[var(--color-status-info-bg)] to-[var(--color-status-indigo-bg)] border border-[var(--color-status-info)] rounded-lg p-4">
          <div className="flex items-center mb-3">
            <TrendingUp className="w-5 h-5 text-[var(--color-status-info)] mr-2" />
            <h2 className="text-lg font-semibold text-[var(--color-content-primary)]">
              Trending Patterns (Last 7 Days)
            </h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {trendingPatterns.map((pattern) => (
              <div
                key={pattern.id}
                onClick={() => handlePatternClick(pattern.id)}
                className="bg-[var(--color-surface-raised)] rounded-lg p-3 cursor-pointer hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between mb-2">
                  <h3 className="font-medium text-[var(--color-content-primary)] text-sm">
                    {pattern.name}
                  </h3>
                  <span
                    className={`px-2 py-0.5 rounded text-xs font-medium ${resolveSeverityColor(pattern.severity)}`}
                  >
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
        <div className="text-center py-12">
          <p className="text-[var(--color-content-muted)]">
            No {statusFilter} patterns found
          </p>
        </div>
      ) : (
        <div className="bg-[var(--color-surface-raised)] shadow overflow-hidden rounded-lg">
          <div className="divide-y divide-[var(--color-border-subtle)]">
            {patterns.map((pattern) => (
              <div
                key={pattern.id}
                onClick={() => handlePatternClick(pattern.id)}
                className="p-6 hover:bg-[var(--color-interactive-hover)]/50 cursor-pointer transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      {resolveStatusIcon(pattern.status)}
                      <h3 className="text-lg font-semibold text-[var(--color-content-primary)]">
                        {pattern.name}
                      </h3>
                      <span
                        className={`px-2 py-1 rounded text-xs font-medium ${resolveSeverityColor(pattern.severity)}`}
                      >
                        {pattern.severity}
                      </span>
                      {pattern.pattern_type && (
                        <span className="px-2 py-1 rounded text-xs font-medium bg-[var(--color-status-info-bg)] text-[var(--color-status-info)]">
                          {pattern.pattern_type}
                        </span>
                      )}
                    </div>

                    {pattern.description && (
                      <p className="text-sm text-[var(--color-content-secondary)] mb-3">
                        {pattern.description}
                      </p>
                    )}

                    <div className="flex items-center space-x-6 text-sm text-[var(--color-content-muted)]">
                      <span>
                        <strong>{pattern.occurrence_count}</strong> occurrences
                      </span>
                      <span>
                        First seen: {formatDate(pattern.first_seen)}
                      </span>
                      <span>
                        Last seen: {formatDate(pattern.last_seen)}
                      </span>
                    </div>

                    {pattern.suggested_actions.length > 0 && (
                      <div className="mt-3">
                        <p className="text-xs font-medium text-[var(--color-content-secondary)] mb-1">
                          Suggested Actions:
                        </p>
                        <ul className="list-disc list-inside text-xs text-[var(--color-content-secondary)] space-y-0.5">
                          {pattern.suggested_actions.slice(0, 3).map((action, idx) => (
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
    </div>
  );
};

export default PatternGroupView;
