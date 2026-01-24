/**
 * LLM Pipeline Result Card Component
 *
 * Displays the results from the 3-stage LLM validation pipeline:
 * - Stage 1: Dual Evaluators (Gemini + GPT) running in parallel
 * - Stage 2: Curator (Claude) for tie-breaking when needed
 * - Stage 3: Final consensus decision
 *
 * Features:
 * - Visual score comparison between evaluators
 * - Consensus type indicator
 * - Reasoning display with expandable sections
 * - Latency breakdown
 *
 * @module components/Validation/LLMPipelineResultCard
 */

import React, { useState } from 'react';
import {
  CheckCircle,
  XCircle,
  AlertCircle,
  Clock,
  ChevronDown,
  ChevronUp,
  Zap,
  Scale,
  Brain,
  Sparkles,
} from 'lucide-react';
import type { LLMEnsembleResult } from '../../types/validation';

interface LLMPipelineResultCardProps {
  /** The LLM pipeline result data */
  result: LLMEnsembleResult;
}

/**
 * Format score as percentage
 */
const formatScore = (score: number): string => {
  return `${(score * 100).toFixed(0)}%`;
};

/**
 * Format latency in human-readable form
 */
const formatLatency = (ms: number): string => {
  if (ms < 1000) return `${ms}ms`;
  return `${(ms / 1000).toFixed(1)}s`;
};

/**
 * Get decision styling based on decision value
 */
const getDecisionStyle = (decision: string): {
  icon: React.ReactNode;
  bgClass: string;
  textClass: string;
  label: string;
} => {
  switch (decision) {
    case 'pass':
      return {
        icon: <CheckCircle className="w-6 h-6" />,
        bgClass: 'bg-[var(--color-status-success-bg)] border-[var(--color-status-success)]',
        textClass: 'text-[var(--color-status-success)]',
        label: 'PASS',
      };
    case 'fail':
      return {
        icon: <XCircle className="w-6 h-6" />,
        bgClass: 'bg-[var(--color-status-danger-bg)] border-[var(--color-status-danger)]',
        textClass: 'text-[var(--color-status-danger)]',
        label: 'FAIL',
      };
    default:
      return {
        icon: <AlertCircle className="w-6 h-6" />,
        bgClass: 'bg-[var(--color-status-warning-bg)] border-[var(--color-status-warning)]',
        textClass: 'text-[var(--color-status-warning)]',
        label: 'NEEDS REVIEW',
      };
  }
};

/**
 * Get confidence badge styling
 */
const getConfidenceBadge = (confidence: string): {
  bgClass: string;
  textClass: string;
} => {
  switch (confidence) {
    case 'high':
      return { bgClass: 'bg-[var(--color-status-success-bg)]', textClass: 'text-[var(--color-status-success)]' };
    case 'medium':
      return { bgClass: 'bg-[var(--color-status-warning-bg)]', textClass: 'text-[var(--color-status-warning)]' };
    default:
      return { bgClass: 'bg-[var(--color-status-danger-bg)]', textClass: 'text-[var(--color-status-danger)]' };
  }
};

/**
 * Get consensus type description
 */
const getConsensusDescription = (type: string): {
  label: string;
  description: string;
  icon: React.ReactNode;
} => {
  switch (type) {
    case 'high_consensus':
      return {
        label: 'High Consensus',
        description: 'Both evaluators strongly agreed',
        icon: <Sparkles className="w-4 h-4 text-[var(--color-status-success)]" />,
      };
    case 'curator_resolved':
      return {
        label: 'Curator Resolved',
        description: 'Curator broke the tie between evaluators',
        icon: <Scale className="w-4 h-4 text-[var(--color-status-warning)]" />,
      };
    case 'human_review':
      return {
        label: 'Human Review',
        description: 'Extreme disagreement requires human review',
        icon: <AlertCircle className="w-4 h-4 text-[var(--color-status-danger)]" />,
      };
    default:
      return {
        label: type,
        description: 'Unknown consensus type',
        icon: <Brain className="w-4 h-4 text-[var(--color-content-secondary)]" />,
      };
  }
};

/**
 * Score bar component for visual representation
 */
const ScoreBar: React.FC<{ score: number; label: string }> = ({ score, label }) => {
  const percentage = score * 100;
  const getBarColor = () => {
    if (percentage >= 80) return 'bg-[var(--color-status-success)]';
    if (percentage >= 60) return 'bg-[var(--color-status-warning)]';
    return 'bg-[var(--color-status-danger)]';
  };

  return (
    <div className="flex items-center gap-3">
      <span className="text-xs text-[var(--color-content-muted)] w-20">{label}</span>
      <div className="flex-1 h-2 bg-[var(--color-surface-inset)] rounded-full overflow-hidden">
        <div
          className={`h-full ${getBarColor()} transition-all duration-500`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      <span className="text-sm font-semibold text-[var(--color-content-secondary)] w-12 text-right">
        {formatScore(score)}
      </span>
    </div>
  );
};

/**
 * Evaluator card component
 */
const EvaluatorCard: React.FC<{
  name: string;
  model: string;
  score: number;
  reasoning: string | null;
  latencyMs: number;
  icon: React.ReactNode;
}> = ({ name, model, score, reasoning, latencyMs, icon }) => {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="bg-[var(--color-surface-inset)] rounded-lg p-4 border border-[var(--color-border-subtle)]">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="text-[var(--color-brand-primary)]">{icon}</div>
          <div>
            <p className="text-sm font-semibold text-[var(--color-content-primary)]">{name}</p>
            <p className="text-xs text-[var(--color-content-muted)]">{model}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1 text-xs text-[var(--color-content-muted)]">
            <Clock className="w-3 h-3" />
            {formatLatency(latencyMs)}
          </div>
        </div>
      </div>

      {/* Score */}
      <div className="mb-3">
        <ScoreBar score={score} label="Score" />
      </div>

      {/* Reasoning (Expandable) */}
      {reasoning && (
        <div>
          <button
            onClick={() => setExpanded(!expanded)}
            className="flex items-center gap-1 text-xs text-[#2A6B6E] hover:text-[#11484D] transition-colors"
          >
            {expanded ? (
              <>
                <ChevronUp className="w-3 h-3" />
                Hide reasoning
              </>
            ) : (
              <>
                <ChevronDown className="w-3 h-3" />
                Show reasoning
              </>
            )}
          </button>
          {expanded && (
            <div className="mt-2 p-3 bg-[var(--color-surface-raised)] rounded-md border border-[var(--color-border-subtle)]">
              <p className="text-xs text-[var(--color-content-secondary)] leading-relaxed">{reasoning}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

/**
 * LLMPipelineResultCard Component
 */
const LLMPipelineResultCard: React.FC<LLMPipelineResultCardProps> = ({ result }) => {
  const decision = getDecisionStyle(result.final_decision);
  const confidence = getConfidenceBadge(result.confidence);
  const consensus = getConsensusDescription(result.consensus_type);

  const showCurator = result.consensus_type === 'curator_resolved' && result.curator_decision;

  return (
    <div className="card">
      {/* Header with Final Decision */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-lg font-semibold text-[var(--color-content-primary)] flex items-center gap-2">
            <Brain className="w-5 h-5 text-[var(--color-brand-primary)]" />
            LLM Pipeline Validation
          </h2>
          <p className="text-xs text-[var(--color-content-muted)] mt-1">
            3-stage evaluation: Dual Evaluators + Curator
          </p>
        </div>
        <div className="flex items-center gap-3">
          {/* Confidence Badge */}
          <span className={`badge ${confidence.bgClass} ${confidence.textClass}`}>
            {result.confidence.toUpperCase()} CONFIDENCE
          </span>
          {/* Final Decision */}
          <div
            className={`flex items-center gap-2 px-4 py-2 rounded-lg border ${decision.bgClass} ${decision.textClass}`}
          >
            {decision.icon}
            <span className="font-bold">{decision.label}</span>
          </div>
        </div>
      </div>

      {/* Final Score & Consensus */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        {/* Final Score */}
        <div className="bg-gradient-to-br from-[#2A6B6E]/10 to-[#11484D]/10 rounded-lg p-4 border border-[#2A6B6E]/20">
          <p className="text-sm text-[var(--color-content-secondary)] mb-1">Final Score</p>
          <p className="text-4xl font-bold text-[var(--color-content-primary)]">
            {formatScore(result.final_score)}
          </p>
          <div className="mt-2">
            <div className="h-2 bg-[var(--color-surface-base)]/50 rounded-full overflow-hidden">
              <div
                className="h-full rounded-full"
                style={{
                  width: `${result.final_score * 100}%`,
                  background: 'linear-gradient(135deg, #2A6B6E 0%, #11484D 100%)',
                }}
              />
            </div>
          </div>
        </div>

        {/* Consensus Info */}
        <div className="bg-[var(--color-surface-inset)] rounded-lg p-4 border border-[var(--color-border-subtle)]">
          <div className="flex items-center gap-2 mb-2">
            {consensus.icon}
            <p className="text-sm font-semibold text-[var(--color-content-primary)]">{consensus.label}</p>
          </div>
          <p className="text-xs text-[var(--color-content-muted)] mb-3">{consensus.description}</p>
          <div className="flex items-center justify-between text-xs">
            <span className="text-[var(--color-content-muted)]">Score Difference</span>
            <span className="font-mono font-semibold text-[var(--color-content-secondary)]">
              {(result.score_difference * 100).toFixed(1)}%
            </span>
          </div>
        </div>
      </div>

      {/* Evaluators Section */}
      <div className="mb-6">
        <h3 className="text-sm font-semibold text-[var(--color-content-secondary)] mb-3 flex items-center gap-2">
          <Zap className="w-4 h-4 text-[var(--color-brand-primary)]" />
          Stage 1: Dual Evaluators
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <EvaluatorCard
            name="Evaluator A"
            model="Gemini Pro"
            score={result.evaluator_a_score}
            reasoning={result.evaluator_a_reasoning}
            latencyMs={result.evaluator_a_latency_ms}
            icon={<Sparkles className="w-5 h-5" />}
          />
          <EvaluatorCard
            name="Evaluator B"
            model="GPT-4"
            score={result.evaluator_b_score}
            reasoning={result.evaluator_b_reasoning}
            latencyMs={result.evaluator_b_latency_ms}
            icon={<Brain className="w-5 h-5" />}
          />
        </div>
      </div>

      {/* Curator Section (if called) */}
      {showCurator && (
        <div className="mb-6">
          <h3 className="text-sm font-semibold text-[var(--color-content-secondary)] mb-3 flex items-center gap-2">
            <Scale className="w-4 h-4 text-[var(--color-brand-primary)]" />
            Stage 2: Curator Tie-Breaking
          </h3>
          <div className="bg-[var(--color-status-purple-bg)] rounded-lg p-4 border border-[var(--color-status-purple)]/20">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 bg-[var(--color-status-purple-bg)] rounded-full flex items-center justify-center">
                  <Scale className="w-4 h-4 text-[var(--color-status-purple)]" />
                </div>
                <div>
                  <p className="text-sm font-semibold text-[var(--color-content-primary)]">Curator</p>
                  <p className="text-xs text-[var(--color-content-muted)]">Claude 3.5 Sonnet</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <div className="flex items-center gap-1 text-xs text-[var(--color-content-muted)]">
                  <Clock className="w-3 h-3" />
                  {formatLatency(result.curator_latency_ms)}
                </div>
                <span
                  className={`badge ${
                    result.curator_decision === 'pass'
                      ? 'badge-success'
                      : result.curator_decision === 'fail'
                        ? 'badge-danger'
                        : 'badge-warning'
                  }`}
                >
                  {result.curator_decision?.toUpperCase()}
                </span>
              </div>
            </div>
            {result.curator_reasoning && (
              <div className="bg-[var(--color-surface-raised)]/70 rounded-md p-3 border border-[var(--color-status-purple)]/20">
                <p className="text-xs text-[var(--color-content-secondary)] leading-relaxed">
                  {result.curator_reasoning}
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Latency Breakdown */}
      <div className="border-t border-[var(--color-border-subtle)] pt-4">
        <div className="flex items-center justify-between text-xs text-[var(--color-content-muted)]">
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1">
              <Clock className="w-3 h-3" />
              Total: <strong className="text-[var(--color-content-secondary)]">{formatLatency(result.latency_ms)}</strong>
            </span>
            <span className="text-[var(--color-content-muted)]">|</span>
            <span>
              Eval A: {formatLatency(result.evaluator_a_latency_ms)}
            </span>
            <span>
              Eval B: {formatLatency(result.evaluator_b_latency_ms)}
            </span>
            {result.curator_latency_ms > 0 && (
              <span>
                Curator: {formatLatency(result.curator_latency_ms)}
              </span>
            )}
          </div>
          <span className="text-[var(--color-content-muted)]">
            Pipeline completed successfully
          </span>
        </div>
      </div>
    </div>
  );
};

export default LLMPipelineResultCard;
