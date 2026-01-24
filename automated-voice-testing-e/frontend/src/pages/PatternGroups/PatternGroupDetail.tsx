/**
 * Pattern Group Detail View
 *
 * Shows detailed information about a single pattern group including:
 * - Pattern metadata and analysis
 * - Linked edge cases
 * - Suggested actions
 * - Related KB articles (Phase 3)
 * - Generate KB Article button (Phase 3)
 */

import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  RefreshCw,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Lightbulb,
  TrendingUp,
  BookOpen,
  Loader2,
  Sparkles,
  Link2,
} from 'lucide-react';
import { getPatternGroupDetails } from '../../services/patternGroup.service';
import {
  generateArticleFromPattern,
  getArticlesByPatternGroup,
} from '../../services/knowledgeBase.service';
import type { PatternGroupDetailResponse } from '../../types/patternGroup';
import type { KnowledgeBaseArticle } from '../../types/knowledgeBase';

const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
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
      return <AlertTriangle className="w-5 h-5 text-[var(--color-status-warning)]" />;
    case 'resolved':
      return <CheckCircle2 className="w-5 h-5 text-[var(--color-status-success)]" />;
    case 'monitoring':
      return <Clock className="w-5 h-5 text-[var(--color-status-info)]" />;
    default:
      return null;
  }
};

const PatternGroupDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [data, setData] = useState<PatternGroupDetailResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Phase 3: KB article state
  const [kbArticles, setKbArticles] = useState<KnowledgeBaseArticle[]>([]);
  const [kbLoading, setKbLoading] = useState(false);
  const [generatingKb, setGeneratingKb] = useState(false);
  const [kbError, setKbError] = useState<string | null>(null);
  const [kbSuccess, setKbSuccess] = useState<string | null>(null);

  const fetchPatternDetails = async () => {
    if (!id) return;

    setLoading(true);
    setError(null);

    try {
      const response = await getPatternGroupDetails(id, 50);
      setData(response);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to load pattern details';
      setError(message);
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  // Phase 3: Fetch linked KB articles
  const fetchKbArticles = async () => {
    if (!id) return;

    setKbLoading(true);
    try {
      const response = await getArticlesByPatternGroup(id);
      setKbArticles(response.items);
    } catch (err) {
      console.error('Failed to fetch KB articles:', err);
    } finally {
      setKbLoading(false);
    }
  };

  // Phase 3: Generate KB article from pattern
  const handleGenerateKbArticle = async () => {
    if (!id) return;

    setGeneratingKb(true);
    setKbError(null);
    setKbSuccess(null);

    try {
      const article = await generateArticleFromPattern(id, { autoPublish: false });
      setKbSuccess(`Article "${article.title}" created successfully!`);
      // Refresh KB articles list
      await fetchKbArticles();

      // Clear success message after 5 seconds
      setTimeout(() => setKbSuccess(null), 5000);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to generate article';
      setKbError(message);
    } finally {
      setGeneratingKb(false);
    }
  };

  useEffect(() => {
    fetchPatternDetails();
    fetchKbArticles();
  }, [id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-8 h-8 animate-spin text-[var(--color-status-info)]" />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-6">
        <button
          onClick={() => navigate('/pattern-groups')}
          className="mb-4 inline-flex items-center text-sm text-[var(--color-content-secondary)] hover:text-[var(--color-content-primary)]"
        >
          <ArrowLeft className="w-4 h-4 mr-1" />
          Back to Pattern Groups
        </button>
        <div className="bg-[var(--color-status-danger-bg)] border border-[var(--color-status-danger)] rounded-lg p-4">
          <p className="text-[var(--color-status-danger)]">
            {error || 'Pattern group not found'}
          </p>
        </div>
      </div>
    );
  }

  const { pattern, edge_cases, total_edge_cases } = data;

  return (
    <div className="p-6 space-y-6">
      {/* Header with Back Button */}
      <div>
        <button
          onClick={() => navigate('/pattern-groups')}
          className="mb-4 inline-flex items-center text-sm text-[var(--color-content-secondary)] hover:text-[var(--color-content-primary)]"
        >
          <ArrowLeft className="w-4 h-4 mr-1" />
          Back to Pattern Groups
        </button>

        <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-3 mb-2">
              {resolveStatusIcon(pattern.status)}
              <h1 className="text-3xl font-bold text-[var(--color-content-primary)] truncate">
                {pattern.name}
              </h1>
            </div>
            {pattern.description && (
              <p className="text-[var(--color-content-secondary)] mt-2">
                {pattern.description}
              </p>
            )}
          </div>
          <div className="flex items-center gap-3 shrink-0">
            {/* Phase 3: Generate KB Article Button */}
            <button
              onClick={handleGenerateKbArticle}
              disabled={generatingKb}
              className="inline-flex items-center px-4 py-2.5 rounded-lg text-sm font-semibold text-white whitespace-nowrap hover:shadow-lg hover:-translate-y-0.5 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:transform-none"
              style={{ background: 'linear-gradient(135deg, #2A6B6E 0%, #11484D 100%)' }}
            >
              {generatingKb ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 mr-2" />
                  Generate KB Article
                </>
              )}
            </button>
            <button
              onClick={fetchPatternDetails}
              className="inline-flex items-center px-4 py-2.5 border border-[var(--color-border-strong)] rounded-lg text-sm font-medium text-[var(--color-content-secondary)] bg-[var(--color-surface-raised)] hover:bg-[var(--color-interactive-hover)] whitespace-nowrap"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh
            </button>
          </div>
        </div>
      </div>

      {/* Phase 3: KB Generation Status Messages */}
      {kbSuccess && (
        <div className="bg-[var(--color-status-success-bg)] border border-[var(--color-status-success)] rounded-lg p-4">
          <div className="flex items-center">
            <CheckCircle2 className="w-5 h-5 mr-3 text-[var(--color-status-success)]" />
            <p className="text-[var(--color-status-success)]">{kbSuccess}</p>
          </div>
        </div>
      )}
      {kbError && (
        <div className="bg-[var(--color-status-danger-bg)] border border-[var(--color-status-danger)] rounded-lg p-4">
          <div className="flex items-center">
            <AlertTriangle className="w-5 h-5 mr-3 text-[var(--color-status-danger)]" />
            <p className="text-[var(--color-status-danger)]">{kbError}</p>
          </div>
        </div>
      )}

      {/* Pattern Metadata */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-[var(--color-surface-raised)] rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <span className="text-sm text-[var(--color-content-muted)]">Severity</span>
            <span
              className={`px-2 py-1 rounded text-xs font-medium ${resolveSeverityColor(pattern.severity)}`}
            >
              {pattern.severity}
            </span>
          </div>
        </div>

        <div className="bg-[var(--color-surface-raised)] rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <span className="text-sm text-[var(--color-content-muted)]">Occurrences</span>
            <div className="flex items-center">
              <TrendingUp className="w-4 h-4 text-[var(--color-status-info)] mr-1" />
              <span className="text-lg font-bold text-[var(--color-content-primary)]">
                {pattern.occurrence_count}
              </span>
            </div>
          </div>
        </div>

        <div className="bg-[var(--color-surface-raised)] rounded-lg shadow p-4">
          <span className="text-sm text-[var(--color-content-muted)] block mb-1">
            First Seen
          </span>
          <span className="text-sm font-medium text-[var(--color-content-primary)]">
            {formatDate(pattern.first_seen)}
          </span>
        </div>

        <div className="bg-[var(--color-surface-raised)] rounded-lg shadow p-4">
          <span className="text-sm text-[var(--color-content-muted)] block mb-1">
            Last Seen
          </span>
          <span className="text-sm font-medium text-[var(--color-content-primary)]">
            {formatDate(pattern.last_seen)}
          </span>
        </div>
      </div>

      {/* Suggested Actions */}
      {pattern.suggested_actions.length > 0 && (
        <div className="bg-[var(--color-status-info-bg)] border border-[var(--color-status-info)] rounded-lg p-6">
          <div className="flex items-center mb-4">
            <Lightbulb className="w-5 h-5 text-[var(--color-status-info)] mr-2" />
            <h2 className="text-lg font-semibold text-[var(--color-content-primary)]">
              Suggested Actions
            </h2>
          </div>
          <ul className="space-y-2">
            {pattern.suggested_actions.map((action, idx) => (
              <li
                key={idx}
                className="flex items-start text-sm text-[var(--color-content-secondary)]"
              >
                <span className="inline-block w-6 h-6 rounded-full bg-[var(--color-status-info-bg)] text-[var(--color-status-info)] text-center mr-3 flex-shrink-0">
                  {idx + 1}
                </span>
                <span className="flex-1">{action}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Phase 3: Related KB Articles */}
      <div className="bg-gradient-to-r from-[var(--color-status-purple-bg)] to-[var(--color-status-indigo-bg)] border border-[var(--color-status-purple)] rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            <BookOpen className="w-5 h-5 text-[var(--color-status-purple)] mr-2" />
            <h2 className="text-lg font-semibold text-[var(--color-content-primary)]">
              Related Documentation
            </h2>
            <span className="ml-2 px-2 py-0.5 text-xs rounded-full bg-[var(--color-status-purple-bg)] text-[var(--color-status-purple)]">
              {kbArticles.length}
            </span>
          </div>
          <button
            onClick={handleGenerateKbArticle}
            disabled={generatingKb}
            className="text-sm text-[var(--color-status-purple)] hover:text-[var(--color-status-purple)] inline-flex items-center"
          >
            <Sparkles className="w-4 h-4 mr-1" />
            Generate New
          </button>
        </div>

        {kbLoading ? (
          <div className="text-center py-4">
            <Loader2 className="w-5 h-5 animate-spin text-[var(--color-status-purple)] mx-auto" />
          </div>
        ) : kbArticles.length === 0 ? (
          <div className="text-center py-4 text-[var(--color-content-muted)]">
            <BookOpen className="w-8 h-8 mx-auto mb-2 text-[var(--color-content-muted)]" />
            <p className="text-sm">No KB articles linked yet.</p>
            <p className="text-xs mt-1">Click "Generate KB Article" to create one.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {kbArticles.map((article) => (
              <div
                key={article.id}
                onClick={() => navigate(`/knowledge-base/${article.id}`)}
                className="bg-[var(--color-surface-raised)] rounded-lg p-4 cursor-pointer hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="font-medium text-[var(--color-content-primary)] mb-1">
                      {article.title}
                    </h3>
                    <div className="flex items-center space-x-3 text-xs text-[var(--color-content-muted)]">
                      <span className="inline-flex items-center">
                        <Link2 className="w-3 h-3 mr-1" />
                        {article.sourceType === 'auto_generated' ? 'Auto-generated' : article.sourceType}
                      </span>
                      {article.category && <span>{article.category}</span>}
                      <span>{article.views} views</span>
                    </div>
                  </div>
                  <span
                    className={`px-2 py-1 rounded text-xs font-medium ${
                      article.isPublished
                        ? 'bg-[var(--color-status-success-bg)] text-[var(--color-status-success)]'
                        : 'bg-[var(--color-status-warning-bg)] text-[var(--color-status-warning)]'
                    }`}
                  >
                    {article.isPublished ? 'Published' : 'Draft'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Linked Edge Cases */}
      <div>
        <h2 className="text-xl font-semibold text-[var(--color-content-primary)] mb-4">
          Linked Edge Cases ({total_edge_cases})
        </h2>

        {edge_cases.length === 0 ? (
          <div className="text-center py-12 bg-[var(--color-surface-raised)] rounded-lg">
            <p className="text-[var(--color-content-muted)]">
              No edge cases linked to this pattern
            </p>
          </div>
        ) : (
          <div className="bg-[var(--color-surface-raised)] shadow overflow-hidden rounded-lg">
            <div className="divide-y divide-[var(--color-border-subtle)]">
              {edge_cases.map((edgeCase: any) => (
                <div
                  key={edgeCase.id}
                  onClick={() => navigate(`/edge-cases/${edgeCase.id}`)}
                  className="p-4 hover:bg-[var(--color-interactive-hover)]/50 cursor-pointer transition-colors"
                >
                  <h3 className="font-medium text-[var(--color-content-primary)] mb-1">
                    {edgeCase.title}
                  </h3>
                  {edgeCase.description && (
                    <p className="text-sm text-[var(--color-content-secondary)]">
                      {edgeCase.description}
                    </p>
                  )}
                  <div className="flex items-center space-x-4 mt-2 text-xs text-[var(--color-content-muted)]">
                    {edgeCase.category && (
                      <span className="px-2 py-0.5 bg-[var(--color-surface-inset)] rounded">
                        {edgeCase.category}
                      </span>
                    )}
                    {edgeCase.severity && (
                      <span
                        className={`px-2 py-0.5 rounded ${resolveSeverityColor(edgeCase.severity)}`}
                      >
                        {edgeCase.severity}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PatternGroupDetail;
