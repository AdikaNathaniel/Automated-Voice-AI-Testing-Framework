/**
 * Validation Result Detail Page
 *
 * Displays validation results from the two-stage validation pipeline:
 * 1. Houndify Deterministic: CommandKind match, ASR confidence, response content
 * 2. LLM Ensemble: Semantic understanding with multiple models
 *
 * @module pages/Validation/ValidationResultDetail
 */

import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Loader2, ArrowLeft, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import {
  fetchValidationResult,
  type ValidationResultDetail,
} from '../../services/validation.service';
import LLMPipelineResultCard from '../../components/Validation/LLMPipelineResultCard';
import type { LLMEnsembleResult } from '../../types/validation';

/**
 * Format score as percentage
 */
const formatPercent = (score: number | null): string => {
  if (score === null || score === undefined) return 'N/A';
  return `${(score * 100).toFixed(1)}%`;
};

/**
 * Get color class based on score value
 */
const getScoreColor = (score: number | null): string => {
  if (score === null || score === undefined) return 'text-[var(--color-content-secondary)]';
  if (score >= 0.75) return 'text-[var(--color-status-success)]';
  if (score >= 0.5) return 'text-[var(--color-status-warning)]';
  return 'text-[var(--color-status-danger)]';
};

/**
 * Get review status badge styling
 */
const getReviewStatusBadge = (status: string | null): {
  icon: React.ReactNode;
  text: string;
  className: string;
} => {
  switch (status) {
    case 'auto_pass':
      return {
        icon: <CheckCircle className="w-5 h-5" />,
        text: 'Auto Pass',
        className: 'bg-[var(--color-status-success-bg)] text-[var(--color-status-success)]',
      };
    case 'auto_fail':
      return {
        icon: <XCircle className="w-5 h-5" />,
        text: 'Auto Fail',
        className: 'bg-[var(--color-status-danger-bg)] text-[var(--color-status-danger)]',
      };
    case 'needs_review':
      return {
        icon: <AlertCircle className="w-5 h-5" />,
        text: 'Needs Review',
        className: 'bg-[var(--color-status-warning-bg)] text-[var(--color-status-warning)]',
      };
    default:
      return {
        icon: <AlertCircle className="w-5 h-5" />,
        text: 'Unknown',
        className: 'bg-[var(--color-surface-inset)] text-[var(--color-content-primary)]',
      };
  }
};

/**
 * Score Card Component
 */
const ScoreCard: React.FC<{
  title: string;
  score: number | null;
  description: string;
  formatter?: (score: number | null) => string;
}> = ({ title, score, description, formatter = formatPercent }) => {
  const scoreColor = getScoreColor(score);

  return (
    <div className="bg-[var(--color-surface-raised)] border border-[var(--color-border-default)] rounded-lg p-4">
      <h3 className="text-sm font-medium text-[var(--color-content-secondary)] mb-2">{title}</h3>
      <p className={`text-3xl font-bold ${scoreColor} mb-2`}>
        {formatter(score)}
      </p>
      <p className="text-xs text-[var(--color-content-muted)]">{description}</p>
    </div>
  );
};

/**
 * Pass/Fail Badge Component
 */
const PassFailBadge: React.FC<{ passed: boolean | null; label: string }> = ({ passed, label }) => {
  if (passed === null) {
    return (
      <div className="flex items-center gap-2 px-3 py-2 bg-[var(--color-surface-inset)] rounded-lg">
        <AlertCircle className="w-5 h-5 text-[var(--color-content-muted)]" />
        <span className="text-[var(--color-content-secondary)]">{label}: N/A</span>
      </div>
    );
  }

  return (
    <div className={`flex items-center gap-2 px-3 py-2 rounded-lg ${
      passed
        ? 'bg-[var(--color-status-success-bg)]'
        : 'bg-[var(--color-status-danger-bg)]'
    }`}>
      {passed ? (
        <CheckCircle className="w-5 h-5 text-[var(--color-status-success)]" />
      ) : (
        <XCircle className="w-5 h-5 text-[var(--color-status-danger)]" />
      )}
      <span className={passed
        ? 'text-[var(--color-status-success)]'
        : 'text-[var(--color-status-danger)]'
      }>
        {label}: {passed ? 'Passed' : 'Failed'}
      </span>
    </div>
  );
};

/**
 * ValidationResultDetail Component
 */
const ValidationResultDetailPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ValidationResultDetail | null>(null);

  const resultId = searchParams.get('resultId');

  useEffect(() => {
    const loadValidationResult = async () => {
      if (!resultId) {
        setError('No validation result ID provided');
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);
        const data = await fetchValidationResult(resultId);
        setResult(data);
      } catch (err) {
        console.error('Failed to load validation result:', err);
        setError('Failed to load validation result. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    void loadValidationResult();
  }, [resultId]);

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 mt-8 flex justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-[var(--color-status-info)]" />
      </div>
    );
  }

  if (error || !result) {
    return (
      <div className="max-w-7xl mx-auto px-4 mt-8">
        <div className="bg-[var(--color-status-danger-bg)] border border-[var(--color-status-danger)] rounded-lg p-4" role="alert">
          <p className="text-[var(--color-status-danger)]">{error || 'Validation result not found'}</p>
        </div>
      </div>
    );
  }

  const reviewStatus = getReviewStatusBadge(result.review_status);

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => navigate(-1)}
          className="btn mb-4 flex items-center gap-2"
        >
          <ArrowLeft className="w-4 h-4" />
          Back
        </button>

        <div className="flex items-center justify-between">
          <h1 className="header">Validation Results</h1>
          <div className={`badge flex items-center gap-2 ${reviewStatus.className}`}>
            {reviewStatus.icon}
            {reviewStatus.text}
          </div>
        </div>
      </div>

      {/* Validation Summary */}
      <div className="card mb-6">
        <h2 className="text-lg font-semibold mb-4 text-[var(--color-content-primary)]">Validation Summary</h2>
        <div className="flex flex-wrap gap-4 mb-4">
          <PassFailBadge passed={result.houndify_passed} label="Houndify" />
          <PassFailBadge passed={result.llm_passed} label="LLM Ensemble" />
        </div>
        {result.final_decision && (
          <p className="text-sm text-[var(--color-content-secondary)]">
            Final Decision: <span className="font-medium">{result.final_decision}</span>
          </p>
        )}
      </div>

      {/* Houndify Validation Scores */}
      <div className="card mb-6">
        <h2 className="text-lg font-semibold mb-4 text-[var(--color-content-primary)]">
          Houndify Deterministic Validation
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <ScoreCard
            title="CommandKind Match"
            score={result.command_kind_match_score}
            description="1.0 if Houndify CommandKind matches expected, 0.0 otherwise"
          />
          <ScoreCard
            title="ASR Confidence"
            score={result.asr_confidence_score}
            description="Houndify's speech recognition confidence level"
          />
        </div>
      </div>

      {/* LLM Pipeline Result (if available) */}
      {result.ensemble_result && (
        <div className="mb-6">
          <LLMPipelineResultCard result={result.ensemble_result as LLMEnsembleResult} />
        </div>
      )}

      {/* Metadata */}
      <div className="card">
        <h2 className="text-lg font-semibold mb-4 text-[var(--color-content-primary)]">Metadata</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-[var(--color-content-muted)]">Validation ID</p>
            <p className="font-mono text-xs text-[var(--color-content-primary)]">{result.id}</p>
          </div>
          {result.multi_turn_execution_id && (
            <div>
              <p className="text-[var(--color-content-muted)]">Execution ID</p>
              <p className="font-mono text-xs text-[var(--color-content-primary)]">{result.multi_turn_execution_id}</p>
            </div>
          )}
          {result.created_at && (
            <div>
              <p className="text-[var(--color-content-muted)]">Created At</p>
              <p className="text-[var(--color-content-primary)]">{new Date(result.created_at).toLocaleString()}</p>
            </div>
          )}
          {result.updated_at && (
            <div>
              <p className="text-[var(--color-content-muted)]">Updated At</p>
              <p className="text-[var(--color-content-primary)]">{new Date(result.updated_at).toLocaleString()}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ValidationResultDetailPage;
