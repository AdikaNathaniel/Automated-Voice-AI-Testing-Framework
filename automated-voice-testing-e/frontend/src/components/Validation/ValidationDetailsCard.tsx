/**
 * Comprehensive Validation Details Card
 *
 * Displays full validation results including:
 * - Houndify validation: expected vs actual, thresholds, individual checks
 * - LLM Ensemble validation: individual evaluator scores, models, consensus, reasoning
 */

import React, { useState } from 'react';
import {
  Zap,
  Brain,
  CheckCircle,
  XCircle,
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  Clock,
  Target,
  MessageSquare,
  Scale,
  Users,
  List,
} from 'lucide-react';

interface ResponseContentValidation {
  passed: boolean;
  errors?: string[];
  details?: {
    contains?: {
      passed: boolean;
      matched?: string[];
      missing?: string[];
    };
    not_contains?: {
      passed: boolean;
      found?: string[];
    };
    regex?: {
      passed: boolean;
      matched?: string[];
      failed?: string[];
    };
    regex_not_match?: {
      passed: boolean;
      found?: string[];
    };
    forbidden_phrases?: {
      passed: boolean;
      found?: string[];
    };
  };
}

interface EntityValidationResult {
  passed: boolean;
  score: number;
  errors: string[];
  details: {
    expected: Record<string, unknown> | null;
    actual: Record<string, unknown> | null;
    matched: string[];
    missing: string[];
    mismatched: Array<{
      key: string;
      expected: unknown;
      actual: unknown;
    }>;
  };
}

interface HoundifyResult {
  passed: boolean;
  method?: string;
  command_kind_match?: boolean;
  expected_command_kind?: string;
  actual_command_kind?: string;
  asr_confidence?: number;
  expected_asr_confidence_min?: number;
  validation_score?: number;
  response_content_validation?: ResponseContentValidation;
  response_content_result?: ResponseContentValidation;
  entity_validation?: EntityValidationResult | null;
  expected_entities?: Record<string, unknown> | null;
  actual_entities?: Record<string, unknown> | null;
  errors?: string[];
  expected_outcome_id?: string;
  latency_ms?: number;
  total_validation_latency_ms?: number;
}

interface CriterionScores {
  relevance?: number;
  correctness?: number;
  completeness?: number;
  tone?: number;
  entity_accuracy?: number;
}

interface LLMResult {
  final_score: number;
  final_decision: string;
  confidence: string;
  consensus_type: string;
  evaluator_a_score: number;
  evaluator_b_score: number;
  evaluator_a_scores?: CriterionScores;
  evaluator_b_scores?: CriterionScores;
  evaluator_a_reasoning: string;
  evaluator_b_reasoning: string;
  curator_decision?: string;
  curator_reasoning?: string;
  score_difference: number;
  latency_ms: number;
  evaluator_a_latency_ms: number;
  evaluator_b_latency_ms: number;
  curator_latency_ms?: number;
  total_validation_latency_ms?: number;
}

interface ValidationDetailsCardProps {
  houndifyResult?: HoundifyResult | null;
  llmResult?: LLMResult | null;
  finalDecision?: string;
  reviewStatus?: string;
  compact?: boolean;
  expectedEntities?: unknown;
  actualEntities?: unknown;
}

/**
 * Helper component for displaying individual criterion score comparison
 */
interface CriterionScoreRowProps {
  label: string;
  description: string;
  scoreA?: number;
  scoreB?: number;
}

const CriterionScoreRow: React.FC<CriterionScoreRowProps> = ({
  label,
  description,
  scoreA,
  scoreB,
}) => {
  const getScoreColor = (score: number) => {
    if (score >= 7) return 'text-[var(--color-status-success)]';
    if (score >= 4) return 'text-[var(--color-status-warning)]';
    return 'text-[var(--color-status-danger)]';
  };

  const getBarColor = (score: number) => {
    if (score >= 7) return 'bg-[var(--color-status-success)]';
    if (score >= 4) return 'bg-[var(--color-status-warning)]';
    return 'bg-[var(--color-status-danger)]';
  };

  return (
    <div className="flex items-center gap-3 p-2 bg-[var(--color-surface-inset)] rounded-lg">
      <div className="flex-shrink-0 w-32">
        <p className="text-sm font-medium text-[var(--color-content-secondary)]">{label}</p>
        <p className="text-xs text-[var(--color-content-muted)]">{description}</p>
      </div>
      <div className="flex-1 flex items-center gap-2">
        {/* Evaluator A score */}
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <div className="flex-1 bg-[var(--color-interactive-active)] rounded-full h-2 overflow-hidden">
              <div
                className={`h-full ${scoreA !== undefined ? getBarColor(scoreA) : 'bg-[var(--color-interactive-active)]'} opacity-70`}
                style={{ width: `${(scoreA ?? 0) * 10}%` }}
              />
            </div>
            <span className={`text-xs font-medium w-6 text-right ${scoreA !== undefined ? getScoreColor(scoreA) : 'text-[var(--color-content-muted)]'}`}>
              {scoreA !== undefined ? scoreA.toFixed(1) : '—'}
            </span>
          </div>
        </div>
        {/* Evaluator B score */}
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <div className="flex-1 bg-[var(--color-interactive-active)] rounded-full h-2 overflow-hidden">
              <div
                className={`h-full ${scoreB !== undefined ? getBarColor(scoreB) : 'bg-[var(--color-interactive-active)]'} opacity-70`}
                style={{ width: `${(scoreB ?? 0) * 10}%` }}
              />
            </div>
            <span className={`text-xs font-medium w-6 text-right ${scoreB !== undefined ? getScoreColor(scoreB) : 'text-[var(--color-content-muted)]'}`}>
              {scoreB !== undefined ? scoreB.toFixed(1) : '—'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * Validation Score Breakdown Component
 *
 * Displays the Houndify validation score formula in an elegant, interactive way.
 * Shows the weighted contributions of each component:
 * - Pass/Fail Check (50%)
 * - ASR Confidence (30%)
 * - CommandKind Match (20%)
 */
interface ValidationScoreBreakdownProps {
  validationScore: number;
  passed: boolean;
  asrConfidence?: number;
  commandKindMatch?: boolean;
  expectedCommandKind?: string | null;
}

const ValidationScoreBreakdown: React.FC<ValidationScoreBreakdownProps> = ({
  validationScore,
  passed,
  asrConfidence,
  commandKindMatch,
  expectedCommandKind,
}) => {
  const [expanded, setExpanded] = useState(false);

  // Calculate individual scores
  const passScore = passed ? 1.0 : 0.0;
  const asrScore = asrConfidence ?? 0.5;
  // If no expected command kind, it counts as passed (1.0)
  const commandKindScore = expectedCommandKind ? (commandKindMatch ? 1.0 : 0.0) : 1.0;

  // Weighted contributions
  const passContribution = passScore * 0.5;
  const asrContribution = asrScore * 0.3;
  const commandKindContribution = commandKindScore * 0.2;

  // Get color based on score
  const getScoreColor = (score: number) => {
    if (score >= 0.7) return 'var(--color-status-success)';
    if (score >= 0.4) return 'var(--color-status-warning)';
    return 'var(--color-status-danger)';
  };

  const getBgColor = (score: number) => {
    if (score >= 0.7) return 'var(--color-status-success-bg)';
    if (score >= 0.4) return 'var(--color-status-warning-bg)';
    return 'var(--color-status-danger-bg)';
  };

  const scoreColor = getScoreColor(validationScore);
  const scoreBgColor = getBgColor(validationScore);

  return (
    <div className="bg-[var(--color-surface-inset)] rounded-lg overflow-hidden">
      {/* Header - Always visible */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full p-3 flex items-center justify-between hover:bg-[var(--color-interactive-hover)] transition-colors"
      >
        <div className="flex items-center gap-3">
          <div
            className="w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg"
            style={{ backgroundColor: scoreBgColor, color: scoreColor }}
          >
            {(validationScore * 100).toFixed(0)}%
          </div>
          <div className="text-left">
            <p className="font-medium text-[var(--color-content-primary)]">Houndify Validation Score</p>
            <p className="text-xs text-[var(--color-content-muted)]">
              Weighted composite of deterministic checks
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-[var(--color-content-muted)]">
            {expanded ? 'Hide' : 'Show'} breakdown
          </span>
          {expanded ? (
            <ChevronUp className="w-4 h-4 text-[var(--color-content-muted)]" />
          ) : (
            <ChevronDown className="w-4 h-4 text-[var(--color-content-muted)]" />
          )}
        </div>
      </button>

      {/* Expanded breakdown */}
      {expanded && (
        <div className="px-3 pb-3 space-y-4">
          {/* Visual Formula */}
          <div className="bg-[var(--color-surface-raised)] rounded-lg p-3 border border-[var(--color-border-subtle)]">
            <p className="text-xs font-medium text-[var(--color-content-muted)] mb-2 text-center">
              Score Formula
            </p>
            <div className="flex items-center justify-center gap-1 text-sm font-mono flex-wrap">
              <span className="px-2 py-1 rounded bg-emerald-500/10 text-emerald-600 dark:text-emerald-400">
                Pass × 50%
              </span>
              <span className="text-[var(--color-content-muted)]">+</span>
              <span className="px-2 py-1 rounded bg-blue-500/10 text-blue-600 dark:text-blue-400">
                ASR × 30%
              </span>
              <span className="text-[var(--color-content-muted)]">+</span>
              <span className="px-2 py-1 rounded bg-purple-500/10 text-purple-600 dark:text-purple-400">
                Cmd × 20%
              </span>
              <span className="text-[var(--color-content-muted)]">=</span>
              <span
                className="px-2 py-1 rounded font-bold"
                style={{ backgroundColor: scoreBgColor, color: scoreColor }}
              >
                {(validationScore * 100).toFixed(1)}%
              </span>
            </div>
          </div>

          {/* Stacked Contribution Bar */}
          <div>
            <p className="text-xs font-medium text-[var(--color-content-muted)] mb-2">
              Weighted Contributions
            </p>
            <div className="h-6 rounded-full overflow-hidden flex bg-[var(--color-surface-raised)]">
              <div
                className="h-full flex items-center justify-center text-[10px] font-medium text-white transition-all"
                style={{
                  width: `${passContribution * 100}%`,
                  backgroundColor: passed ? '#10b981' : '#ef4444',
                  minWidth: passContribution > 0 ? '20px' : '0',
                }}
                title={`Pass/Fail: ${(passContribution * 100).toFixed(1)}%`}
              >
                {passContribution >= 0.1 && `${(passContribution * 100).toFixed(0)}%`}
              </div>
              <div
                className="h-full flex items-center justify-center text-[10px] font-medium text-white transition-all"
                style={{
                  width: `${asrContribution * 100}%`,
                  backgroundColor: '#3b82f6',
                  minWidth: asrContribution > 0 ? '20px' : '0',
                }}
                title={`ASR Confidence: ${(asrContribution * 100).toFixed(1)}%`}
              >
                {asrContribution >= 0.05 && `${(asrContribution * 100).toFixed(0)}%`}
              </div>
              <div
                className="h-full flex items-center justify-center text-[10px] font-medium text-white transition-all"
                style={{
                  width: `${commandKindContribution * 100}%`,
                  backgroundColor: commandKindScore === 1.0 ? '#8b5cf6' : '#ef4444',
                  minWidth: commandKindContribution > 0 ? '20px' : '0',
                }}
                title={`CommandKind: ${(commandKindContribution * 100).toFixed(1)}%`}
              >
                {commandKindContribution >= 0.05 && `${(commandKindContribution * 100).toFixed(0)}%`}
              </div>
            </div>
          </div>

          {/* Individual Components */}
          <div className="space-y-2">
            <p className="text-xs font-medium text-[var(--color-content-muted)]">
              Component Details
            </p>

            {/* Pass/Fail Check */}
            <div className="flex items-center gap-3 p-2 rounded-lg bg-[var(--color-surface-raised)] border border-[var(--color-border-subtle)]">
              <div
                className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0"
                style={{ backgroundColor: passed ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)' }}
              >
                {passed ? (
                  <CheckCircle className="w-4 h-4 text-emerald-500" />
                ) : (
                  <XCircle className="w-4 h-4 text-red-500" />
                )}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-[var(--color-content-primary)]">
                    Validation Check
                  </span>
                  <span className="text-xs font-mono text-[var(--color-content-muted)]">
                    50% weight
                  </span>
                </div>
                <div className="flex items-center justify-between mt-0.5">
                  <span className="text-xs text-[var(--color-content-muted)]">
                    {passed ? 'All checks passed' : 'One or more checks failed'}
                  </span>
                  <span
                    className="text-xs font-bold"
                    style={{ color: passed ? '#10b981' : '#ef4444' }}
                  >
                    {(passScore * 100).toFixed(0)}% → +{(passContribution * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
            </div>

            {/* ASR Confidence */}
            <div className="flex items-center gap-3 p-2 rounded-lg bg-[var(--color-surface-raised)] border border-[var(--color-border-subtle)]">
              <div
                className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0"
                style={{ backgroundColor: 'rgba(59, 130, 246, 0.1)' }}
              >
                <Target className="w-4 h-4 text-blue-500" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-[var(--color-content-primary)]">
                    ASR Confidence
                  </span>
                  <span className="text-xs font-mono text-[var(--color-content-muted)]">
                    30% weight
                  </span>
                </div>
                <div className="flex items-center justify-between mt-0.5">
                  <div className="flex items-center gap-2">
                    <div className="w-16 h-1.5 rounded-full bg-[var(--color-surface-inset)] overflow-hidden">
                      <div
                        className="h-full rounded-full bg-blue-500"
                        style={{ width: `${asrScore * 100}%` }}
                      />
                    </div>
                    <span className="text-xs text-[var(--color-content-muted)]">
                      {asrConfidence !== undefined ? `${(asrConfidence * 100).toFixed(1)}%` : 'Default 50%'}
                    </span>
                  </div>
                  <span className="text-xs font-bold text-blue-500">
                    {(asrScore * 100).toFixed(0)}% → +{(asrContribution * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
            </div>

            {/* CommandKind Match */}
            <div className="flex items-center gap-3 p-2 rounded-lg bg-[var(--color-surface-raised)] border border-[var(--color-border-subtle)]">
              <div
                className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0"
                style={{
                  backgroundColor: commandKindScore === 1.0
                    ? 'rgba(139, 92, 246, 0.1)'
                    : 'rgba(239, 68, 68, 0.1)'
                }}
              >
                <Zap
                  className="w-4 h-4"
                  style={{ color: commandKindScore === 1.0 ? '#8b5cf6' : '#ef4444' }}
                />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-[var(--color-content-primary)]">
                    CommandKind Match
                  </span>
                  <span className="text-xs font-mono text-[var(--color-content-muted)]">
                    20% weight
                  </span>
                </div>
                <div className="flex items-center justify-between mt-0.5">
                  <span className="text-xs text-[var(--color-content-muted)]">
                    {!expectedCommandKind
                      ? 'No requirement (auto-pass)'
                      : commandKindMatch
                        ? 'Matched expected type'
                        : 'Did not match expected type'
                    }
                  </span>
                  <span
                    className="text-xs font-bold"
                    style={{ color: commandKindScore === 1.0 ? '#8b5cf6' : '#ef4444' }}
                  >
                    {(commandKindScore * 100).toFixed(0)}% → +{(commandKindContribution * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Summary */}
          <div className="pt-2 border-t border-[var(--color-border-subtle)]">
            <div className="flex items-center justify-between text-sm">
              <span className="text-[var(--color-content-muted)]">Total Score</span>
              <span
                className="font-bold"
                style={{ color: scoreColor }}
              >
                {(passContribution * 100).toFixed(1)}% + {(asrContribution * 100).toFixed(1)}% + {(commandKindContribution * 100).toFixed(1)}% = {(validationScore * 100).toFixed(1)}%
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

/**
 * LLM Ensemble Score Breakdown Component
 *
 * Displays the LLM ensemble validation score breakdown showing:
 * - How the final score is calculated from evaluator scores
 * - Individual criterion contributions (relevance, correctness, completeness, tone, entity_accuracy)
 * - Consensus type and confidence
 */
interface LLMScoreBreakdownProps {
  finalScore: number;
  finalDecision: string;
  confidence: string;
  consensusType: string;
  evaluatorAScore: number;
  evaluatorBScore: number;
  evaluatorAScores?: CriterionScores;
  evaluatorBScores?: CriterionScores;
  scoreDifference: number;
  evaluatorAModel?: string;
  evaluatorBModel?: string;
  curatorModel?: string;
}

const LLMScoreBreakdown: React.FC<LLMScoreBreakdownProps> = ({
  finalScore,
  finalDecision,
  confidence,
  consensusType,
  evaluatorAScore,
  evaluatorBScore,
  evaluatorAScores,
  evaluatorBScores,
  scoreDifference,
  evaluatorAModel = 'Gemini 2.5 Flash',
  evaluatorBModel = 'GPT-4.1 Mini',
  curatorModel = 'Claude Sonnet 4.5',
}) => {
  const [expanded, setExpanded] = useState(false);

  // Calculate average criterion scores for display
  const getCriterionAverage = (criterion: keyof CriterionScores): number | null => {
    const scoreA = evaluatorAScores?.[criterion];
    const scoreB = evaluatorBScores?.[criterion];
    if (scoreA === undefined && scoreB === undefined) return null;
    if (scoreA === undefined) return scoreB! / 10;
    if (scoreB === undefined) return scoreA / 10;
    return (scoreA + scoreB) / 20; // Average of both, normalized to 0-1
  };

  const criterionAverages = {
    relevance: getCriterionAverage('relevance'),
    correctness: getCriterionAverage('correctness'),
    completeness: getCriterionAverage('completeness'),
    tone: getCriterionAverage('tone'),
    entity_accuracy: getCriterionAverage('entity_accuracy'),
  };

  // Get color based on score
  const getScoreColor = (score: number) => {
    if (score >= 0.7) return 'var(--color-status-success)';
    if (score >= 0.4) return 'var(--color-status-warning)';
    return 'var(--color-status-danger)';
  };

  const getBgColor = (score: number) => {
    if (score >= 0.7) return 'var(--color-status-success-bg)';
    if (score >= 0.4) return 'var(--color-status-warning-bg)';
    return 'var(--color-status-danger-bg)';
  };

  const getConfidenceColor = () => {
    if (confidence === 'high') return { text: '#10b981', bg: 'rgba(16, 185, 129, 0.1)' };
    if (confidence === 'medium') return { text: '#f59e0b', bg: 'rgba(245, 158, 11, 0.1)' };
    return { text: '#ef4444', bg: 'rgba(239, 68, 68, 0.1)' };
  };

  const scoreColor = getScoreColor(finalScore);
  const scoreBgColor = getBgColor(finalScore);
  const confidenceColors = getConfidenceColor();

  // Criterion labels and icons
  const criterionInfo: Array<{ key: keyof CriterionScores; label: string; description: string; color: string }> = [
    { key: 'relevance', label: 'Relevance', description: 'Addresses user request', color: '#3b82f6' },
    { key: 'correctness', label: 'Correctness', description: 'Accurate information', color: '#10b981' },
    { key: 'completeness', label: 'Completeness', description: 'Fully answered', color: '#8b5cf6' },
    { key: 'tone', label: 'Tone', description: 'Appropriate style', color: '#f59e0b' },
    { key: 'entity_accuracy', label: 'Entities', description: 'Correct details', color: '#ec4899' },
  ];

  return (
    <div className="bg-[var(--color-surface-inset)] rounded-lg overflow-hidden">
      {/* Header - Always visible */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full p-3 flex items-center justify-between hover:bg-[var(--color-interactive-hover)] transition-colors"
      >
        <div className="flex items-center gap-3">
          <div
            className="w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg"
            style={{ backgroundColor: scoreBgColor, color: scoreColor }}
          >
            {(finalScore * 100).toFixed(0)}%
          </div>
          <div className="text-left">
            <p className="font-medium text-[var(--color-content-primary)]">LLM Ensemble Score</p>
            <p className="text-xs text-[var(--color-content-muted)]">
              {consensusType === 'high_consensus' && 'High agreement between AI judges'}
              {consensusType === 'curator_resolved' && 'Tie-broken by curator'}
              {consensusType === 'human_review' && 'Human review needed'}
              {consensusType === 'error' && 'Evaluation error'}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-[var(--color-content-muted)]">
            {expanded ? 'Hide' : 'Show'} breakdown
          </span>
          {expanded ? (
            <ChevronUp className="w-4 h-4 text-[var(--color-content-muted)]" />
          ) : (
            <ChevronDown className="w-4 h-4 text-[var(--color-content-muted)]" />
          )}
        </div>
      </button>

      {/* Expanded breakdown */}
      {expanded && (
        <div className="px-3 pb-3 space-y-4">
          {/* How Score is Calculated */}
          <div className="bg-[var(--color-surface-raised)] rounded-lg p-3 border border-[var(--color-border-subtle)]">
            <p className="text-xs font-medium text-[var(--color-content-muted)] mb-2 text-center">
              Ensemble Calculation
            </p>
            <div className="flex items-center justify-center gap-2 text-sm font-mono flex-wrap">
              <div className="flex flex-col items-center px-2 py-1 rounded bg-blue-500/10">
                <span className="text-blue-600 dark:text-blue-400 text-xs">Eval A</span>
                <span className="text-blue-600 dark:text-blue-400 font-bold">{(evaluatorAScore * 100).toFixed(0)}%</span>
              </div>
              {consensusType === 'curator_resolved' ? (
                <>
                  <span className="text-[var(--color-content-muted)]">→</span>
                  <div className="flex flex-col items-center px-2 py-1 rounded bg-purple-500/10">
                    <span className="text-purple-600 dark:text-purple-400 text-xs">Curator</span>
                    <span className="text-purple-600 dark:text-purple-400 font-bold">Resolved</span>
                  </div>
                  <span className="text-[var(--color-content-muted)]">←</span>
                </>
              ) : (
                <span className="text-[var(--color-content-muted)]">+</span>
              )}
              <div className="flex flex-col items-center px-2 py-1 rounded bg-emerald-500/10">
                <span className="text-emerald-600 dark:text-emerald-400 text-xs">Eval B</span>
                <span className="text-emerald-600 dark:text-emerald-400 font-bold">{(evaluatorBScore * 100).toFixed(0)}%</span>
              </div>
              <span className="text-[var(--color-content-muted)]">=</span>
              <div
                className="flex flex-col items-center px-2 py-1 rounded"
                style={{ backgroundColor: scoreBgColor }}
              >
                <span className="text-xs" style={{ color: scoreColor }}>Final</span>
                <span className="font-bold" style={{ color: scoreColor }}>{(finalScore * 100).toFixed(0)}%</span>
              </div>
            </div>
            {consensusType !== 'curator_resolved' && (
              <p className="text-xs text-[var(--color-content-muted)] text-center mt-2">
                Score = Average of both evaluators
              </p>
            )}
            {consensusType === 'curator_resolved' && (
              <p className="text-xs text-[var(--color-content-muted)] text-center mt-2">
                Score = Curator ({curatorModel}) resolved disagreement
              </p>
            )}
          </div>

          {/* Agreement Visual */}
          <div>
            <p className="text-xs font-medium text-[var(--color-content-muted)] mb-2">
              Evaluator Agreement
            </p>
            <div className="relative h-8 rounded-full overflow-hidden bg-[var(--color-surface-raised)]">
              {/* Evaluator A bar */}
              <div
                className="absolute h-full flex items-center justify-end pr-2 text-[10px] font-medium text-white"
                style={{
                  width: `${evaluatorAScore * 100}%`,
                  backgroundColor: '#3b82f6',
                }}
              >
                {evaluatorAScore >= 0.15 && `A: ${(evaluatorAScore * 100).toFixed(0)}%`}
              </div>
              {/* Evaluator B bar (from right) */}
              <div
                className="absolute h-full right-0 flex items-center justify-start pl-2 text-[10px] font-medium text-white"
                style={{
                  width: `${evaluatorBScore * 100}%`,
                  backgroundColor: '#10b981',
                  opacity: 0.8,
                }}
              >
                {evaluatorBScore >= 0.15 && `B: ${(evaluatorBScore * 100).toFixed(0)}%`}
              </div>
              {/* Difference indicator */}
              <div className="absolute inset-0 flex items-center justify-center">
                <span
                  className="px-2 py-0.5 rounded text-[10px] font-bold bg-[var(--color-surface-overlay)] text-[var(--color-content-primary)]"
                >
                  Δ {(scoreDifference * 100).toFixed(0)}%
                </span>
              </div>
            </div>
            <div className="flex justify-between text-xs mt-1">
              <span className="text-blue-500">{evaluatorAModel}</span>
              <span className="text-emerald-500">{evaluatorBModel}</span>
            </div>
          </div>

          {/* Criterion Breakdown */}
          {(evaluatorAScores || evaluatorBScores) && (
            <div>
              <p className="text-xs font-medium text-[var(--color-content-muted)] mb-2">
                Criterion Contributions
              </p>
              <div className="space-y-2">
                {criterionInfo.map(({ key, label, description, color }) => {
                  const avg = criterionAverages[key];
                  const scoreA = evaluatorAScores?.[key];
                  const scoreB = evaluatorBScores?.[key];

                  if (avg === null) return null;

                  return (
                    <div
                      key={key}
                      className="flex items-center gap-3 p-2 rounded-lg bg-[var(--color-surface-raised)] border border-[var(--color-border-subtle)]"
                    >
                      <div
                        className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 text-white font-bold text-xs"
                        style={{ backgroundColor: color }}
                      >
                        {((avg ?? 0) * 10).toFixed(0)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-medium text-[var(--color-content-primary)]">
                            {label}
                          </span>
                          <div className="flex items-center gap-2 text-xs font-mono">
                            {scoreA !== undefined && (
                              <span className="text-blue-500">A:{scoreA.toFixed(1)}</span>
                            )}
                            {scoreB !== undefined && (
                              <span className="text-emerald-500">B:{scoreB.toFixed(1)}</span>
                            )}
                          </div>
                        </div>
                        <div className="flex items-center gap-2 mt-0.5">
                          <div className="flex-1 h-1.5 rounded-full bg-[var(--color-surface-inset)] overflow-hidden">
                            <div
                              className="h-full rounded-full transition-all"
                              style={{
                                width: `${(avg ?? 0) * 100}%`,
                                backgroundColor: color,
                              }}
                            />
                          </div>
                          <span className="text-xs text-[var(--color-content-muted)] w-12 text-right">
                            {description}
                          </span>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Confidence & Consensus */}
          <div className="grid grid-cols-2 gap-2">
            <div
              className="p-3 rounded-lg text-center"
              style={{ backgroundColor: confidenceColors.bg }}
            >
              <p
                className="text-lg font-bold capitalize"
                style={{ color: confidenceColors.text }}
              >
                {confidence}
              </p>
              <p className="text-xs text-[var(--color-content-muted)]">Confidence</p>
            </div>
            <div className="p-3 rounded-lg bg-[var(--color-surface-raised)] text-center">
              <p className="text-lg font-bold text-[var(--color-content-secondary)]">
                {finalDecision === 'pass' ? '✓ Pass' : finalDecision === 'fail' ? '✗ Fail' : '? Review'}
              </p>
              <p className="text-xs text-[var(--color-content-muted)]">Decision</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

/**
 * Determine the reason for an uncertain/needs_review decision.
 * Analyzes the validation results to provide a user-friendly explanation.
 */
const getUncertainReason = (
  houndifyResult?: HoundifyResult | null,
  llmResult?: LLMResult | null,
  finalDecision?: string,
): { reason: string; detail?: string } | null => {
  // Only show reason for uncertain decisions
  if (finalDecision !== 'uncertain') return null;

  // Check for LLM pipeline error
  if (llmResult?.consensus_type === 'error') {
    const errorDetail = llmResult.evaluator_a_reasoning?.includes('Pipeline error')
      ? llmResult.evaluator_a_reasoning
      : undefined;
    return {
      reason: 'Validation pipeline error',
      detail: errorDetail,
    };
  }

  // Check for extreme evaluator disagreement (human_review consensus)
  if (llmResult?.consensus_type === 'human_review') {
    const diffPercent = Math.round((llmResult.score_difference || 0) * 100);
    return {
      reason: 'AI judges significantly disagreed',
      detail: `Score difference: ${diffPercent}% (threshold: 40%)`,
    };
  }

  // Check for Houndify/LLM disagreement in hybrid mode
  if (houndifyResult && llmResult) {
    const houndifyPassed = houndifyResult.passed;
    const llmPassed = llmResult.final_decision === 'pass';

    if (houndifyPassed !== llmPassed) {
      return {
        reason: 'Deterministic and AI validation conflict',
        detail: `Houndify: ${houndifyPassed ? 'PASS' : 'FAIL'}, LLM: ${llmPassed ? 'PASS' : 'FAIL'}`,
      };
    }
  }

  // Check for low LLM confidence
  if (llmResult?.confidence === 'low') {
    return {
      reason: 'Low confidence in AI assessment',
      detail: `Final score: ${Math.round((llmResult.final_score || 0) * 100)}%`,
    };
  }

  // Check for medium confidence with curator involvement
  if (llmResult?.confidence === 'medium' && llmResult?.consensus_type === 'curator_resolved') {
    return {
      reason: 'Resolved by curator with medium confidence',
      detail: `Curator decision: ${llmResult.curator_decision?.toUpperCase()}`,
    };
  }

  // Default fallback
  return {
    reason: 'Human review recommended',
  };
};

const ValidationDetailsCard: React.FC<ValidationDetailsCardProps> = ({
  houndifyResult,
  llmResult,
  finalDecision,
  reviewStatus,
  compact = false,
  expectedEntities,
  actualEntities,
}) => {
  const [expandedSection, setExpandedSection] = useState<'houndify' | 'llm' | null>(
    compact ? null : 'houndify'
  );

  const toggleSection = (section: 'houndify' | 'llm') => {
    setExpandedSection(expandedSection === section ? null : section);
  };

  // Get LLM model names from environment or use defaults
  const evaluatorAModel = 'Gemini 2.5 Flash';
  const evaluatorBModel = 'GPT-4.1 Mini';
  const curatorModel = 'Claude Sonnet 4.5';

  // Get reason for uncertain decision
  const uncertainReason = getUncertainReason(houndifyResult, llmResult, finalDecision);

  return (
    <div className="space-y-4">
      {/* Overall Decision Banner */}
      {finalDecision && (
        <div className={`rounded-lg border overflow-hidden ${
          finalDecision === 'pass' ? 'bg-[var(--color-status-success-bg)] border-[var(--color-status-success)]' :
          finalDecision === 'fail' ? 'bg-[var(--color-status-danger-bg)] border-[var(--color-status-danger)]' :
          'bg-[var(--color-status-warning-bg)] border-[var(--color-status-warning)]'
        }`}>
          {/* Main decision row */}
          <div className="p-3 flex items-center justify-between">
            <div className="flex items-center gap-2">
              {finalDecision === 'pass' && <CheckCircle className="w-5 h-5 text-[var(--color-status-success)]" />}
              {finalDecision === 'fail' && <XCircle className="w-5 h-5 text-[var(--color-status-danger)]" />}
              {finalDecision === 'uncertain' && <AlertTriangle className="w-5 h-5 text-[var(--color-status-warning)]" />}
              <span className="font-semibold text-[var(--color-content-primary)]">
                Final Decision: <span className="uppercase">{finalDecision}</span>
              </span>
            </div>
            {reviewStatus && (
              <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                reviewStatus === 'auto_pass' ? 'bg-[var(--color-status-success-bg)] text-[var(--color-status-success)]' :
                reviewStatus === 'auto_fail' ? 'bg-[var(--color-status-danger-bg)] text-[var(--color-status-danger)]' :
                'bg-[var(--color-status-warning-bg)] text-[var(--color-status-warning)]'
              }`}>
                {reviewStatus.replace('_', ' ')}
              </span>
            )}
          </div>
          {/* Reason row for uncertain decisions */}
          {uncertainReason && (
            <div className="px-3 pb-3 pt-0">
              <div className="p-2 bg-[var(--color-surface-overlay)] rounded border border-[var(--color-status-warning)]/30">
                <p className="text-sm text-[var(--color-content-secondary)]">
                  <span className="font-medium">Reason:</span> {uncertainReason.reason}
                </p>
                {uncertainReason.detail && (
                  <p className="text-xs text-[var(--color-content-muted)] mt-0.5">
                    {uncertainReason.detail}
                  </p>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Validation Latency Summary - Shows parallel execution time */}
      {((houndifyResult?.total_validation_latency_ms ?? 0) > 0 || (llmResult?.total_validation_latency_ms ?? 0) > 0) && (
        <div className="p-3 bg-[var(--color-surface-inset)] rounded-lg border border-[var(--color-border-default)]">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-[var(--color-content-muted)]" />
              <span className="text-sm font-medium text-[var(--color-content-secondary)]">Validation Latency</span>
              <span className="text-xs text-[var(--color-content-muted)]">(parallel execution)</span>
            </div>
            <span className="text-sm font-bold text-[var(--color-brand-primary)]">
              {houndifyResult?.total_validation_latency_ms || llmResult?.total_validation_latency_ms}ms
            </span>
          </div>
          {/* Breakdown */}
          <div className="flex items-center gap-4 mt-2 text-xs text-[var(--color-content-muted)]">
            {houndifyResult?.latency_ms !== undefined && (
              <span className="flex items-center gap-1">
                <Zap className="w-3 h-3 text-[var(--color-status-info)]" />
                Houndify: {houndifyResult.latency_ms}ms
              </span>
            )}
            {llmResult?.latency_ms !== undefined && llmResult.latency_ms > 0 && (
              <span className="flex items-center gap-1">
                <Brain className="w-3 h-3 text-[var(--color-status-purple)]" />
                LLM: {llmResult.latency_ms}ms
              </span>
            )}
          </div>
        </div>
      )}

      {/* Houndify Validation Section */}
      {houndifyResult && (
        <div className="border border-[var(--color-status-info)] rounded-lg overflow-hidden">
          <button
            onClick={() => toggleSection('houndify')}
            className="w-full p-4 bg-[var(--color-status-info-bg)] flex items-center justify-between hover:bg-[var(--color-status-info-bg)] transition-colors"
          >
            <div className="flex items-center gap-3">
              <Zap className="w-5 h-5 text-[var(--color-status-info)]" />
              <span className="font-semibold text-[var(--color-content-primary)]">Houndify Validation (Deterministic)</span>
              <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                houndifyResult.passed ? 'bg-[var(--color-status-success-bg)] text-[var(--color-status-success)]' : 'bg-[var(--color-status-danger-bg)] text-[var(--color-status-danger)]'
              }`}>
                {houndifyResult.passed ? 'PASSED' : 'FAILED'}
              </span>
            </div>
            {expandedSection === 'houndify' ? (
              <ChevronUp className="w-5 h-5 text-[var(--color-content-muted)]" />
            ) : (
              <ChevronDown className="w-5 h-5 text-[var(--color-content-muted)]" />
            )}
          </button>

          {expandedSection === 'houndify' && (
            <div className="p-4 space-y-4 bg-[var(--color-surface-raised)]">
              {/* CommandKind Check */}
              <div className="border border-[var(--color-border-default)] rounded-lg p-3">
                <div className="flex items-center gap-2 mb-2">
                  <Target className="w-4 h-4 text-[var(--color-content-muted)]" />
                  <span className="font-medium text-[var(--color-content-secondary)]">CommandKind Match</span>
                  {houndifyResult.command_kind_match !== undefined && (
                    houndifyResult.command_kind_match ? (
                      <CheckCircle className="w-4 h-4 text-[var(--color-status-success)] ml-auto" />
                    ) : (
                      <XCircle className="w-4 h-4 text-[var(--color-status-danger)] ml-auto" />
                    )
                  )}
                </div>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div className="bg-[var(--color-surface-inset)] p-2 rounded">
                    <p className="text-xs text-[var(--color-content-muted)] mb-1">Expected</p>
                    <p className="font-mono text-[var(--color-content-primary)]">
                      {houndifyResult.expected_command_kind || '—'}
                    </p>
                  </div>
                  <div className={`p-2 rounded ${
                    houndifyResult.command_kind_match ? 'bg-[var(--color-status-success-bg)]' : 'bg-[var(--color-status-danger-bg)]'
                  }`}>
                    <p className="text-xs text-[var(--color-content-muted)] mb-1">Actual</p>
                    <p className={`font-mono ${
                      houndifyResult.command_kind_match ? 'text-[var(--color-status-success)]' : 'text-[var(--color-status-danger)]'
                    }`}>
                      {houndifyResult.actual_command_kind || '—'}
                    </p>
                  </div>
                </div>
              </div>

              {/* ASR Confidence Check */}
              {houndifyResult.asr_confidence !== undefined && (
                <div className="border border-[var(--color-border-default)] rounded-lg p-3">
                  <div className="flex items-center gap-2 mb-2">
                    <MessageSquare className="w-4 h-4 text-[var(--color-content-muted)]" />
                    <span className="font-medium text-[var(--color-content-secondary)]">ASR Confidence</span>
                    {houndifyResult.expected_asr_confidence_min !== undefined && (
                      houndifyResult.asr_confidence >= houndifyResult.expected_asr_confidence_min ? (
                        <CheckCircle className="w-4 h-4 text-[var(--color-status-success)] ml-auto" />
                      ) : (
                        <XCircle className="w-4 h-4 text-[var(--color-status-danger)] ml-auto" />
                      )
                    )}
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="bg-[var(--color-surface-inset)] p-2 rounded">
                      <p className="text-xs text-[var(--color-content-muted)] mb-1">Minimum Required</p>
                      <p className="font-mono text-[var(--color-content-primary)]">
                        {houndifyResult.expected_asr_confidence_min !== undefined
                          ? `${(houndifyResult.expected_asr_confidence_min * 100).toFixed(0)}%`
                          : '—'}
                      </p>
                    </div>
                    <div className={`p-2 rounded ${
                      houndifyResult.expected_asr_confidence_min === undefined ||
                      houndifyResult.asr_confidence >= houndifyResult.expected_asr_confidence_min
                        ? 'bg-[var(--color-status-success-bg)]' : 'bg-[var(--color-status-danger-bg)]'
                    }`}>
                      <p className="text-xs text-[var(--color-content-muted)] mb-1">Actual</p>
                      <p className={`font-mono ${
                        houndifyResult.expected_asr_confidence_min === undefined ||
                        houndifyResult.asr_confidence >= houndifyResult.expected_asr_confidence_min
                          ? 'text-[var(--color-status-success)]' : 'text-[var(--color-status-danger)]'
                      }`}>
                        {(houndifyResult.asr_confidence * 100).toFixed(1)}%
                      </p>
                    </div>
                  </div>
                  {/* Confidence Bar */}
                  <div className="mt-2">
                    <div className="w-full bg-[var(--color-interactive-active)] rounded-full h-2 relative">
                      {houndifyResult.expected_asr_confidence_min !== undefined && (
                        <div
                          className="absolute h-full w-0.5 bg-[var(--color-content-muted)] z-10"
                          style={{ left: `${houndifyResult.expected_asr_confidence_min * 100}%` }}
                          title={`Threshold: ${(houndifyResult.expected_asr_confidence_min * 100).toFixed(0)}%`}
                        />
                      )}
                      <div
                        className={`h-full rounded-full transition-all ${
                          houndifyResult.expected_asr_confidence_min === undefined ||
                          houndifyResult.asr_confidence >= houndifyResult.expected_asr_confidence_min
                            ? 'bg-[var(--color-status-success)]' : 'bg-[var(--color-status-danger)]'
                        }`}
                        style={{ width: `${houndifyResult.asr_confidence * 100}%` }}
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* Response Content Validation */}
              {(() => {
                const contentValidation = houndifyResult.response_content_validation || houndifyResult.response_content_result;
                if (!contentValidation) return null;

                const details = contentValidation.details;
                const hasDetails = details && (
                  details.contains || details.not_contains || details.regex ||
                  details.regex_not_match || details.forbidden_phrases
                );

                return (
                  <div className="border border-[var(--color-border-default)] rounded-lg p-3">
                    <div className="flex items-center gap-2 mb-3">
                      <MessageSquare className="w-4 h-4 text-[var(--color-content-muted)]" />
                      <span className="font-medium text-[var(--color-content-secondary)]">Response Content Validation</span>
                      {contentValidation.passed ? (
                        <CheckCircle className="w-4 h-4 text-[var(--color-status-success)] ml-auto" />
                      ) : (
                        <XCircle className="w-4 h-4 text-[var(--color-status-danger)] ml-auto" />
                      )}
                    </div>

                    {hasDetails ? (
                      <div className="space-y-3 text-sm">
                        {/* Contains Check */}
                        {details.contains && (
                          <div className="p-2 bg-[var(--color-surface-inset)] rounded">
                            <div className="flex items-center justify-between mb-2">
                              <span className="text-[var(--color-content-secondary)] font-medium">Contains Required Phrases</span>
                              {details.contains.passed ? (
                                <span className="text-[var(--color-status-success)] flex items-center gap-1">
                                  <CheckCircle className="w-3 h-3" /> Pass
                                </span>
                              ) : (
                                <span className="text-[var(--color-status-danger)] flex items-center gap-1">
                                  <XCircle className="w-3 h-3" /> Fail
                                </span>
                              )}
                            </div>
                            {details.contains.matched && details.contains.matched.length > 0 && (
                              <div className="text-xs text-[var(--color-status-success)] mb-1">
                                Matched: {details.contains.matched.map(p => `"${p}"`).join(', ')}
                              </div>
                            )}
                            {details.contains.missing && details.contains.missing.length > 0 && (
                              <div className="text-xs text-[var(--color-status-danger)]">
                                Missing: {details.contains.missing.map(p => `"${p}"`).join(', ')}
                              </div>
                            )}
                          </div>
                        )}

                        {/* Not Contains Check */}
                        {details.not_contains && (
                          <div className="p-2 bg-[var(--color-surface-inset)] rounded">
                            <div className="flex items-center justify-between mb-2">
                              <span className="text-[var(--color-content-secondary)] font-medium">No Forbidden Phrases</span>
                              {details.not_contains.passed ? (
                                <span className="text-[var(--color-status-success)] flex items-center gap-1">
                                  <CheckCircle className="w-3 h-3" /> Pass
                                </span>
                              ) : (
                                <span className="text-[var(--color-status-danger)] flex items-center gap-1">
                                  <XCircle className="w-3 h-3" /> Fail
                                </span>
                              )}
                            </div>
                            {details.not_contains.found && details.not_contains.found.length > 0 && (
                              <div className="text-xs text-[var(--color-status-danger)]">
                                Found forbidden: {details.not_contains.found.map(p => `"${p}"`).join(', ')}
                              </div>
                            )}
                          </div>
                        )}

                        {/* Regex Check */}
                        {details.regex && (
                          <div className="p-2 bg-[var(--color-surface-inset)] rounded">
                            <div className="flex items-center justify-between mb-2">
                              <span className="text-[var(--color-content-secondary)] font-medium">Regex Patterns Match</span>
                              {details.regex.passed ? (
                                <span className="text-[var(--color-status-success)] flex items-center gap-1">
                                  <CheckCircle className="w-3 h-3" /> Pass
                                </span>
                              ) : (
                                <span className="text-[var(--color-status-danger)] flex items-center gap-1">
                                  <XCircle className="w-3 h-3" /> Fail
                                </span>
                              )}
                            </div>
                            {details.regex.matched && details.regex.matched.length > 0 && (
                              <div className="text-xs text-[var(--color-status-success)] font-mono mb-1">
                                Matched: {details.regex.matched.join(', ')}
                              </div>
                            )}
                            {details.regex.failed && details.regex.failed.length > 0 && (
                              <div className="text-xs text-[var(--color-status-danger)] font-mono">
                                Failed: {details.regex.failed.join(', ')}
                              </div>
                            )}
                          </div>
                        )}

                        {/* Regex Not Match Check */}
                        {details.regex_not_match && (
                          <div className="p-2 bg-[var(--color-surface-inset)] rounded">
                            <div className="flex items-center justify-between mb-2">
                              <span className="text-[var(--color-content-secondary)] font-medium">No Forbidden Regex Patterns</span>
                              {details.regex_not_match.passed ? (
                                <span className="text-[var(--color-status-success)] flex items-center gap-1">
                                  <CheckCircle className="w-3 h-3" /> Pass
                                </span>
                              ) : (
                                <span className="text-[var(--color-status-danger)] flex items-center gap-1">
                                  <XCircle className="w-3 h-3" /> Fail
                                </span>
                              )}
                            </div>
                            {details.regex_not_match.found && details.regex_not_match.found.length > 0 && (
                              <div className="text-xs text-[var(--color-status-danger)] font-mono">
                                Found forbidden: {details.regex_not_match.found.join(', ')}
                              </div>
                            )}
                          </div>
                        )}

                        {/* Forbidden Phrases Check */}
                        {details.forbidden_phrases && (
                          <div className="p-2 bg-[var(--color-surface-inset)] rounded">
                            <div className="flex items-center justify-between mb-2">
                              <span className="text-[var(--color-content-secondary)] font-medium">Forbidden Phrases Check</span>
                              {details.forbidden_phrases.passed ? (
                                <span className="text-[var(--color-status-success)] flex items-center gap-1">
                                  <CheckCircle className="w-3 h-3" /> Pass
                                </span>
                              ) : (
                                <span className="text-[var(--color-status-danger)] flex items-center gap-1">
                                  <XCircle className="w-3 h-3" /> Fail
                                </span>
                              )}
                            </div>
                            {details.forbidden_phrases.found && details.forbidden_phrases.found.length > 0 && (
                              <div className="text-xs text-[var(--color-status-danger)]">
                                Found: {details.forbidden_phrases.found.map(p => `"${p}"`).join(', ')}
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    ) : (
                      /* Fallback: Show errors if no detailed structure */
                      <div className="space-y-1">
                        {contentValidation.errors?.map((err, i) => (
                          <p key={i} className="text-xs text-[var(--color-status-danger)]">• {err}</p>
                        ))}
                        {(!contentValidation.errors || contentValidation.errors.length === 0) && (
                          <p className="text-xs text-[var(--color-content-muted)]">No content validation rules defined</p>
                        )}
                      </div>
                    )}
                  </div>
                );
              })()}

              {/* Entity Validation */}
              {(expectedEntities || actualEntities || houndifyResult.entity_validation) && (
                <div className="border border-[var(--color-border-default)] rounded-lg p-3">
                  <div className="flex items-center gap-2 mb-3">
                    <List className="w-4 h-4 text-[var(--color-status-info)]" />
                    <span className="font-medium text-[var(--color-content-secondary)]">Entity Validation</span>
                    {houndifyResult.entity_validation ? (
                      houndifyResult.entity_validation.passed ? (
                        <CheckCircle className="w-4 h-4 text-[var(--color-status-success)] ml-auto" />
                      ) : (
                        <XCircle className="w-4 h-4 text-[var(--color-status-danger)] ml-auto" />
                      )
                    ) : null}
                  </div>
                  {/* Show entity validation score if available */}
                  {houndifyResult.entity_validation && (
                    <div className="flex items-center justify-between p-2 bg-[var(--color-surface-inset)] rounded mb-3">
                      <span className="text-xs text-[var(--color-content-muted)]">Match Score</span>
                      <span className={`text-sm font-mono font-medium ${
                        houndifyResult.entity_validation.passed
                          ? 'text-[var(--color-status-success)]'
                          : 'text-[var(--color-status-danger)]'
                      }`}>
                        {(houndifyResult.entity_validation.score * 100).toFixed(0)}%
                      </span>
                    </div>
                  )}
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    {expectedEntities && (
                      <div className="bg-[var(--color-surface-inset)] p-2 rounded">
                        <p className="text-xs text-[var(--color-content-muted)] mb-1">Expected Entities</p>
                        <pre className="font-mono text-xs text-[var(--color-content-secondary)] whitespace-pre-wrap overflow-auto max-h-32">
                          {typeof expectedEntities === 'string'
                            ? expectedEntities
                            : JSON.stringify(expectedEntities, null, 2)}
                        </pre>
                      </div>
                    )}
                    {actualEntities && (
                      <div className={`p-2 rounded ${
                        houndifyResult.entity_validation?.passed
                          ? 'bg-[var(--color-status-success-bg)]'
                          : 'bg-[var(--color-status-danger-bg)]'
                      }`}>
                        <p className="text-xs text-[var(--color-content-muted)] mb-1">Actual Entities</p>
                        <pre className={`font-mono text-xs whitespace-pre-wrap overflow-auto max-h-32 ${
                          houndifyResult.entity_validation?.passed
                            ? 'text-[var(--color-status-success)]'
                            : 'text-[var(--color-status-danger)]'
                        }`}>
                          {typeof actualEntities === 'string'
                            ? actualEntities
                            : JSON.stringify(actualEntities, null, 2)}
                        </pre>
                      </div>
                    )}
                  </div>
                  {/* Show entity validation errors if any */}
                  {houndifyResult.entity_validation?.errors && houndifyResult.entity_validation.errors.length > 0 && (
                    <div className="mt-3 p-2 bg-[var(--color-status-danger-bg)] rounded">
                      <p className="text-xs text-[var(--color-status-danger)] font-medium mb-1">Validation Errors:</p>
                      <ul className="text-xs text-[var(--color-status-danger)] list-disc list-inside">
                        {houndifyResult.entity_validation.errors.map((error, idx) => (
                          <li key={idx}>{error}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              {/* Houndify Validation Score Breakdown */}
              {houndifyResult.validation_score !== undefined && (
                <ValidationScoreBreakdown
                  validationScore={houndifyResult.validation_score}
                  passed={houndifyResult.passed}
                  asrConfidence={houndifyResult.asr_confidence}
                  commandKindMatch={houndifyResult.command_kind_match}
                  expectedCommandKind={houndifyResult.expected_command_kind}
                />
              )}

              {/* Errors */}
              {houndifyResult.errors && houndifyResult.errors.length > 0 && (
                <div className="p-3 bg-[var(--color-status-danger-bg)] rounded-lg border border-[var(--color-status-danger)]">
                  <p className="font-medium text-[var(--color-status-danger)] mb-2">Validation Errors</p>
                  <ul className="list-disc list-inside text-sm text-[var(--color-status-danger)] space-y-1">
                    {houndifyResult.errors.map((err, i) => (
                      <li key={i}>{err}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* LLM Ensemble Validation Section */}
      {llmResult && (
        <div className="border border-[var(--color-status-purple)] rounded-lg overflow-hidden">
          <button
            onClick={() => toggleSection('llm')}
            className="w-full p-4 bg-[var(--color-status-purple-bg)] flex items-center justify-between hover:bg-[var(--color-status-purple-bg)] transition-colors"
          >
            <div className="flex items-center gap-3">
              <Brain className="w-5 h-5 text-[var(--color-status-purple)]" />
              <span className="font-semibold text-[var(--color-content-primary)]">LLM Ensemble Validation (AI Judges)</span>
              <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                llmResult.final_decision === 'pass' ? 'bg-[var(--color-status-success-bg)] text-[var(--color-status-success)]' :
                llmResult.final_decision === 'fail' ? 'bg-[var(--color-status-danger-bg)] text-[var(--color-status-danger)]' :
                'bg-[var(--color-status-warning-bg)] text-[var(--color-status-warning)]'
              }`}>
                {llmResult.final_decision?.toUpperCase() || 'PENDING'}
              </span>
            </div>
            {expandedSection === 'llm' ? (
              <ChevronUp className="w-5 h-5 text-[var(--color-content-muted)]" />
            ) : (
              <ChevronDown className="w-5 h-5 text-[var(--color-content-muted)]" />
            )}
          </button>

          {expandedSection === 'llm' && (
            <div className="p-4 space-y-4 bg-[var(--color-surface-raised)]">
              {/* LLM Score Breakdown - Interactive Formula Display */}
              <LLMScoreBreakdown
                finalScore={llmResult.final_score}
                finalDecision={llmResult.final_decision}
                confidence={llmResult.confidence}
                consensusType={llmResult.consensus_type}
                evaluatorAScore={llmResult.evaluator_a_score}
                evaluatorBScore={llmResult.evaluator_b_score}
                evaluatorAScores={llmResult.evaluator_a_scores}
                evaluatorBScores={llmResult.evaluator_b_scores}
                scoreDifference={llmResult.score_difference}
                evaluatorAModel={evaluatorAModel}
                evaluatorBModel={evaluatorBModel}
                curatorModel={curatorModel}
              />

              {/* Latency Details */}
              {(llmResult.latency_ms > 0 || llmResult.evaluator_a_latency_ms > 0 || llmResult.evaluator_b_latency_ms > 0) && (
                <div className="border border-[var(--color-border-default)] rounded-lg p-3">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <Clock className="w-4 h-4 text-[var(--color-content-muted)]" />
                      <span className="font-medium text-[var(--color-content-secondary)]">Evaluation Latency</span>
                    </div>
                    {llmResult.latency_ms > 0 && (
                      <span className="text-sm font-bold text-[var(--color-status-purple)]">
                        Total: {llmResult.latency_ms}ms
                      </span>
                    )}
                  </div>
                  <div className="grid grid-cols-3 gap-3 text-sm">
                    {llmResult.evaluator_a_latency_ms > 0 && (
                      <div className="text-center p-2 bg-[var(--color-status-info-bg)] rounded">
                        <p className="text-xs text-[var(--color-content-muted)]">Evaluator A</p>
                        <p className="font-mono text-[var(--color-status-info)]">{llmResult.evaluator_a_latency_ms}ms</p>
                      </div>
                    )}
                    {llmResult.evaluator_b_latency_ms > 0 && (
                      <div className="text-center p-2 bg-[var(--color-status-success-bg)] rounded">
                        <p className="text-xs text-[var(--color-content-muted)]">Evaluator B</p>
                        <p className="font-mono text-[var(--color-status-success)]">{llmResult.evaluator_b_latency_ms}ms</p>
                      </div>
                    )}
                    {(llmResult.curator_latency_ms ?? 0) > 0 && (
                      <div className="text-center p-2 bg-[var(--color-status-warning-bg)] rounded">
                        <p className="text-xs text-[var(--color-content-muted)]">Curator</p>
                        <p className="font-mono text-[var(--color-status-warning)]">{llmResult.curator_latency_ms}ms</p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Curator Decision (if involved) */}
              {llmResult.curator_decision && (
                <div className="border border-[var(--color-status-amber-bg)] rounded-lg p-4 bg-[var(--color-status-amber-bg)]">
                  <div className="flex items-center gap-2 mb-3">
                    <Scale className="w-4 h-4 text-[var(--color-status-amber)]" />
                    <span className="font-semibold text-[var(--color-content-secondary)]">Curator Decision (Tie-Breaker)</span>
                    <span className="text-xs text-[var(--color-content-muted)] ml-auto">{curatorModel}</span>
                  </div>
                  <div className="flex items-center gap-4 mb-3">
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                      llmResult.curator_decision === 'pass' ? 'bg-[var(--color-status-success-bg)] text-[var(--color-status-success)]' :
                      llmResult.curator_decision === 'fail' ? 'bg-[var(--color-status-danger-bg)] text-[var(--color-status-danger)]' :
                      'bg-[var(--color-status-warning-bg)] text-[var(--color-status-warning)]'
                    }`}>
                      {llmResult.curator_decision.toUpperCase()}
                    </span>
                    {(llmResult.curator_latency_ms ?? 0) > 0 && (
                      <span className="text-xs text-[var(--color-content-muted)] flex items-center gap-1">
                        <Clock className="w-3 h-3" /> {llmResult.curator_latency_ms}ms
                      </span>
                    )}
                  </div>
                  {llmResult.curator_reasoning && (
                    <div className="text-sm text-[var(--color-content-secondary)] bg-[var(--color-surface-raised)] p-3 rounded border border-[var(--color-status-amber-bg)]">
                      <p className="text-xs text-[var(--color-content-muted)] mb-1">Curator Reasoning</p>
                      <p>{llmResult.curator_reasoning}</p>
                    </div>
                  )}
                </div>
              )}

              {/* Evaluator Reasoning */}
              <div className="space-y-3">
                <p className="font-medium text-[var(--color-content-secondary)]">Evaluator Reasoning</p>

                {llmResult.evaluator_a_reasoning && (
                  <div className="p-3 bg-[var(--color-status-info-bg)] rounded-lg border border-[var(--color-status-info-bg)]">
                    <p className="text-xs font-medium text-[var(--color-status-info)] mb-1">
                      Evaluator A ({evaluatorAModel})
                    </p>
                    <p className="text-sm text-[var(--color-content-secondary)]">{llmResult.evaluator_a_reasoning}</p>
                  </div>
                )}

                {llmResult.evaluator_b_reasoning && (
                  <div className="p-3 bg-[var(--color-status-success-bg)] rounded-lg border border-[var(--color-status-success-bg)]">
                    <p className="text-xs font-medium text-[var(--color-status-success)] mb-1">
                      Evaluator B ({evaluatorBModel})
                    </p>
                    <p className="text-sm text-[var(--color-content-secondary)]">{llmResult.evaluator_b_reasoning}</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* No validation data */}
      {!houndifyResult && !llmResult && (
        <div className="text-center py-8 text-[var(--color-content-muted)]">
          <AlertTriangle className="w-8 h-8 mx-auto mb-2 text-[var(--color-content-muted)]" />
          <p>No validation details available</p>
        </div>
      )}
    </div>
  );
};

export default ValidationDetailsCard;
