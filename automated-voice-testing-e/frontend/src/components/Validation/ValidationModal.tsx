/**
 * ValidationModal - Professional validation work interface
 *
 * A sleek, modern modal for reviewing and validating test execution results.
 * Features a split-panel layout with audio/input on the left and validation
 * analysis on the right.
 */

import React, { useCallback, useEffect, useState, useRef } from 'react';
import ReactDOM from 'react-dom';
import { useSelector, useDispatch } from 'react-redux';
import {
  X,
  Play,
  Pause,
  Volume2,
  Clock,
  Globe,
  Zap,
  Brain,
  CheckCircle,
  XCircle,
  AlertTriangle,
  ChevronDown,
  ChevronRight,
  Sparkles,
  Target,
  MessageSquare,
  SkipForward,
  Send,
  Keyboard,
  Info,
  Bug,
  List,
} from 'lucide-react';
import {
  submitValidation,
  releaseValidation,
  setCurrentValidation,
  updateValidationTimer,
} from '../../store/slices/validationSlice';
import type { RootState, AppDispatch } from '../../store';
import { useToast } from '../../components/common/Toast';

interface ValidationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmitSuccess?: () => void;
}

type DecisionOption = 'pass' | 'fail' | 'edge_case' | 'create_defect' | '';

const formatTime = (seconds: number): string => {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};

// Waveform Audio Player Component with Visual Waveform
const AudioPlayerSlim: React.FC<{ url: string; label: string }> = ({ url, label }) => {
  const audioRef = useRef<HTMLAudioElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationFrameRef = useRef<number>();
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const [duration, setDuration] = useState(0);
  const [waveformData, setWaveformData] = useState<number[]>([]);

  // Generate waveform data from audio
  useEffect(() => {
    const generateWaveform = async () => {
      try {
        const response = await fetch(url);
        const arrayBuffer = await response.arrayBuffer();
        const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
        const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);

        const rawData = audioBuffer.getChannelData(0);
        const samples = 100; // Number of bars in waveform
        const blockSize = Math.floor(rawData.length / samples);
        const filteredData: number[] = [];

        for (let i = 0; i < samples; i++) {
          let sum = 0;
          for (let j = 0; j < blockSize; j++) {
            sum += Math.abs(rawData[i * blockSize + j]);
          }
          filteredData.push(sum / blockSize);
        }

        // Normalize the data
        const max = Math.max(...filteredData);
        const normalized = filteredData.map(n => n / max);
        setWaveformData(normalized);
      } catch (error) {
        console.error('Error generating waveform:', error);
        // Fallback to simple bars
        setWaveformData(Array(100).fill(0).map(() => Math.random() * 0.8 + 0.2));
      }
    };

    generateWaveform();
  }, [url]);

  // Smooth animation loop for progress
  useEffect(() => {
    const updateProgress = () => {
      if (audioRef.current && isPlaying) {
        const currentProgress = (audioRef.current.currentTime / audioRef.current.duration) * 100;
        setProgress(currentProgress);
        animationFrameRef.current = requestAnimationFrame(updateProgress);
      }
    };

    if (isPlaying) {
      animationFrameRef.current = requestAnimationFrame(updateProgress);
    } else {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    }

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [isPlaying]);

  // Draw waveform on canvas with smooth progress
  useEffect(() => {
    if (!canvasRef.current || waveformData.length === 0) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const { width, height } = canvas;
    ctx.clearRect(0, 0, width, height);

    const barWidth = width / waveformData.length;
    const exactProgress = (progress / 100) * waveformData.length;
    const playedIndex = Math.floor(exactProgress);
    const partialProgress = exactProgress - playedIndex; // Fractional part for smooth transition

    waveformData.forEach((value, index) => {
      const barHeight = value * height * 0.9;
      const x = index * barWidth;
      const y = (height - barHeight) / 2;

      // Determine color based on playback position
      // Use CSS variable fallback colors for canvas
      const playedColor = getComputedStyle(document.documentElement).getPropertyValue('--color-brand-primary').trim() || '#2A6B6E';
      const unplayedColor = 'rgba(148, 163, 184, 0.3)';

      if (index < playedIndex) {
        // Fully played bars
        ctx.fillStyle = playedColor;
      } else if (index === playedIndex && partialProgress > 0) {
        // Currently playing bar - create gradient for smooth transition
        const gradient = ctx.createLinearGradient(x, 0, x + barWidth, 0);
        gradient.addColorStop(0, playedColor);
        gradient.addColorStop(partialProgress, playedColor);
        gradient.addColorStop(partialProgress, unplayedColor);
        gradient.addColorStop(1, unplayedColor);
        ctx.fillStyle = gradient;
      } else {
        // Unplayed bars
        ctx.fillStyle = unplayedColor;
      }

      ctx.fillRect(x, y, Math.max(barWidth - 1, 1), barHeight);
    });
  }, [waveformData, progress]);

  const togglePlay = () => {
    if (!audioRef.current) return;
    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play();
    }
    setIsPlaying(!isPlaying);
  };

  const handleTimeUpdate = () => {
    if (!audioRef.current) return;
    setProgress((audioRef.current.currentTime / audioRef.current.duration) * 100);
  };

  const handleLoadedMetadata = () => {
    if (audioRef.current) {
      setDuration(audioRef.current.duration);
    }
  };

  const handleEnded = () => setIsPlaying(false);

  const handleSeek = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!audioRef.current) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const percent = (e.clientX - rect.left) / rect.width;
    audioRef.current.currentTime = percent * audioRef.current.duration;
  };

  return (
    <div className="flex items-center gap-3 p-3 bg-[var(--color-surface-inset)] rounded-xl border border-[var(--color-border-default)]">
      <audio
        ref={audioRef}
        src={url}
        onTimeUpdate={handleTimeUpdate}
        onLoadedMetadata={handleLoadedMetadata}
        onEnded={handleEnded}
      />
      <button
        onClick={togglePlay}
        className="w-10 h-10 rounded-full bg-[var(--color-brand-primary)] flex items-center justify-center text-white shadow-lg hover:bg-[var(--color-brand-hover)] transition-all hover:scale-105 flex-shrink-0"
      >
        {isPlaying ? <Pause size={18} /> : <Play size={18} className="ml-0.5" />}
      </button>
      <div className="flex-1">
        <div className="flex items-center justify-between mb-1.5">
          <span className="text-xs font-medium text-[var(--color-content-muted)] uppercase tracking-wide">{label}</span>
          <span className="text-xs text-[var(--color-content-muted)]">{formatTime(Math.floor(duration))}</span>
        </div>
        <canvas
          ref={canvasRef}
          width={400}
          height={32}
          className="w-full h-8 cursor-pointer rounded"
          onClick={handleSeek}
        />
      </div>
      <Volume2 size={16} className="text-[var(--color-content-muted)] flex-shrink-0" />
    </div>
  );
};

// Validation Status Badge
const StatusBadge: React.FC<{ status: string; size?: 'sm' | 'md' }> = ({ status, size = 'md' }) => {
  const config: Record<string, { bg: string; text: string; icon: React.ReactNode }> = {
    pass: { bg: 'bg-[var(--color-status-success-bg)]', text: 'text-[var(--color-status-success)]', icon: <CheckCircle size={14} /> },
    fail: { bg: 'bg-[var(--color-status-danger-bg)]', text: 'text-[var(--color-status-danger)]', icon: <XCircle size={14} /> },
    uncertain: { bg: 'bg-[var(--color-status-warning-bg)]', text: 'text-[var(--color-status-warning)]', icon: <AlertTriangle size={14} /> },
    PASSED: { bg: 'bg-[var(--color-status-success-bg)]', text: 'text-[var(--color-status-success)]', icon: <CheckCircle size={14} /> },
    FAILED: { bg: 'bg-[var(--color-status-danger-bg)]', text: 'text-[var(--color-status-danger)]', icon: <XCircle size={14} /> },
  };
  const c = config[status] || config.uncertain;
  const sizeClasses = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-3 py-1 text-sm';

  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full font-medium ${c.bg} ${c.text} ${sizeClasses}`}>
      {c.icon}
      {status.toUpperCase()}
    </span>
  );
};

// Score Ring Component
const ScoreRing: React.FC<{ score: number; size?: number; label?: string; tooltip?: string }> = ({ score, size = 64, label, tooltip }) => {
  const percentage = Math.round(score * 100);
  const strokeWidth = 4;
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (score * circumference);

  const getColor = () => {
    const computedStyle = getComputedStyle(document.documentElement);
    if (score >= 0.7) return {
      stroke: computedStyle.getPropertyValue('--color-status-success').trim() || '#10b981',
      bg: computedStyle.getPropertyValue('--color-status-success-bg').trim() || 'rgba(16, 185, 129, 0.1)'
    };
    if (score >= 0.4) return {
      stroke: computedStyle.getPropertyValue('--color-status-warning').trim() || '#f59e0b',
      bg: computedStyle.getPropertyValue('--color-status-warning-bg').trim() || 'rgba(245, 158, 11, 0.1)'
    };
    return {
      stroke: computedStyle.getPropertyValue('--color-status-danger').trim() || '#ef4444',
      bg: computedStyle.getPropertyValue('--color-status-danger-bg').trim() || 'rgba(239, 68, 68, 0.1)'
    };
  };

  const colors = getColor();

  return (
    <div className="flex flex-col items-center gap-1">
      <div className="relative inline-flex items-center justify-center">
        <svg width={size} height={size} className="transform -rotate-90">
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill={colors.bg}
            stroke="var(--color-border-default)"
            strokeWidth={strokeWidth}
          />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={colors.stroke}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            className="transition-all duration-500"
          />
        </svg>
        <span className="absolute inset-0 flex items-center justify-center text-lg font-bold text-[var(--color-content-primary)]">
          {percentage}%
        </span>
      </div>
      {label && (
        <div className="flex items-center gap-1">
          <span className="text-xs text-[var(--color-content-muted)]">{label}</span>
          {tooltip && <InfoTooltip text={tooltip} />}
        </div>
      )}
    </div>
  );
};

// Info Tooltip Component
const InfoTooltip: React.FC<{ text: string }> = ({ text }) => {
  const [show, setShow] = useState(false);
  const buttonRef = useRef<HTMLButtonElement>(null);
  const [position, setPosition] = useState({ top: 0, left: 0 });

  useEffect(() => {
    if (show && buttonRef.current) {
      const rect = buttonRef.current.getBoundingClientRect();
      setPosition({
        top: rect.top - 8, // 8px above button
        left: rect.left + rect.width / 2, // Center horizontally
      });
    }
  }, [show]);

  const tooltipContent = show ? (
    <div
      className="fixed px-3 py-2 bg-[var(--color-surface-overlay)] text-[var(--color-content-primary)] text-xs rounded-lg shadow-xl border border-[var(--color-border-default)] pointer-events-none"
      style={{
        top: `${position.top}px`,
        left: `${position.left}px`,
        transform: 'translate(-50%, -100%)',
        zIndex: 999999,
        maxWidth: '256px',
      }}
    >
      {text}
      <div
        className="absolute bg-[var(--color-surface-overlay)] border-r border-b border-[var(--color-border-default)]"
        style={{
          left: '50%',
          bottom: '-4px',
          transform: 'translateX(-50%) rotate(45deg)',
          width: '8px',
          height: '8px',
        }}
      />
    </div>
  ) : null;

  return (
    <>
      <button
        ref={buttonRef}
        type="button"
        className="inline-flex items-center justify-center w-4 h-4 rounded-full text-[var(--color-content-muted)] hover:text-[var(--color-content-primary)] hover:bg-[var(--color-interactive-active)] transition-colors"
        onMouseEnter={() => setShow(true)}
        onMouseLeave={() => setShow(false)}
        onClick={(e) => e.stopPropagation()}
      >
        <Info size={12} />
      </button>
      {tooltipContent && ReactDOM.createPortal(tooltipContent, document.body)}
    </>
  );
};

// Criterion Score Bar Component
const CriterionScoreBar: React.FC<{
  label: string;
  score: number;
  maxScore?: number;
  weight?: number;
  tooltip?: string;
}> = ({ label, score, maxScore = 10, weight, tooltip }) => {
  const percentage = (score / maxScore) * 100;
  const getColorClass = () => {
    if (percentage >= 70) return 'bg-[var(--color-status-success)]';
    if (percentage >= 40) return 'bg-[var(--color-status-warning)]';
    return 'bg-[var(--color-status-danger)]';
  };

  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between text-sm">
        <div className="flex items-center gap-1.5">
          <span className="text-[var(--color-content-secondary)]">{label}</span>
          {tooltip && <InfoTooltip text={tooltip} />}
          {weight !== undefined && (
            <span className="text-xs text-[var(--color-content-muted)]">(Weight: {(weight * 100).toFixed(0)}%)</span>
          )}
        </div>
        <span className="font-mono font-semibold text-[var(--color-content-primary)]">
          {score.toFixed(1)}/{maxScore}
        </span>
      </div>
      <div className="h-2 bg-[var(--color-interactive-active)] rounded-full overflow-hidden">
        <div
          className={`h-full ${getColorClass()} rounded-full transition-all duration-500`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};

// Collapsible Section
const CollapsibleSection: React.FC<{
  title: string | React.ReactNode;
  icon: React.ReactNode;
  badge?: React.ReactNode;
  defaultOpen?: boolean;
  children: React.ReactNode;
}> = ({ title, icon, badge, defaultOpen = false, children }) => {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div className="border border-[var(--color-border-default)] rounded-xl overflow-hidden bg-[var(--color-surface-inset)]">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-4 py-3 flex items-center justify-between hover:bg-[var(--color-interactive-hover)] transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-[var(--color-interactive-active)] flex items-center justify-center">
            {icon}
          </div>
          <div className="font-medium text-[var(--color-content-primary)]">{title}</div>
          {badge}
        </div>
        <ChevronDown
          size={18}
          className={`text-[var(--color-content-muted)] transition-transform ${isOpen ? 'rotate-180' : ''}`}
        />
      </button>
      {isOpen && <div className="px-4 pb-4 pt-2">{children}</div>}
    </div>
  );
};

const ValidationModal: React.FC<ValidationModalProps> = ({ isOpen, onClose, onSubmitSuccess }) => {
  const dispatch = useDispatch<AppDispatch>();
  const { showToast } = useToast();
  const { current, loading, timeSpent } = useSelector((state: RootState) => state.validation);

  const [decision, setDecision] = useState<DecisionOption>('');
  const [feedback, setFeedback] = useState('');
  const [activeTab, setActiveTab] = useState<'houndify' | 'llm'>('houndify');
  const [showShortcuts, setShowShortcuts] = useState(false);

  const isCompleted = current?.status === 'completed';

  // Timer update
  useEffect(() => {
    if (!isOpen || !current || isCompleted) return;

    dispatch(updateValidationTimer());
    const interval = setInterval(() => dispatch(updateValidationTimer()), 1000);
    return () => clearInterval(interval);
  }, [isOpen, current, isCompleted, dispatch]);

  // Keyboard shortcuts
  useEffect(() => {
    if (!isOpen || !current || isCompleted) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement;
      if (target.tagName === 'TEXTAREA' || target.tagName === 'INPUT') return;

      switch (e.key.toLowerCase()) {
        case 'p':
          e.preventDefault();
          setDecision('pass');
          break;
        case 'f':
          e.preventDefault();
          setDecision('fail');
          break;
        case 'e':
          e.preventDefault();
          setDecision('edge_case');
          break;
        case 'd':
          e.preventDefault();
          setDecision('create_defect');
          break;
        case 'enter':
          if (decision) {
            e.preventDefault();
            handleSubmit();
          }
          break;
        case 's':
          e.preventDefault();
          handleSkip();
          break;
        case 'escape':
          onClose();
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, current, decision, isCompleted]);

  const handleSubmit = useCallback(async () => {
    if (!current || !decision) return;

    try {
      await dispatch(
        submitValidation({
          queueId: current.id,
          validation: {
            validationResultId: current.validationResultId,
            decision,
            feedback: feedback || undefined,
            timeSpent,
          },
        })
      ).unwrap();

      // Show different toast based on decision type
      if (decision === 'edge_case') {
        showToast({
          type: 'info',
          title: 'Edge Case Recorded',
          message: 'This edge case has been added to the library for analysis and will help improve AI validation accuracy.',
          duration: 5000,
        });
      } else if (decision === 'create_defect') {
        showToast({
          type: 'warning',
          title: 'Defect Created',
          message: 'A defect has been created for this validation failure. The issue will be tracked and can be assigned for resolution.',
          duration: 5000,
        });
      } else {
        showToast({
          type: 'success',
          title: 'Validation Submitted',
          message: `Marked as ${decision.replace('_', ' ')}`,
          duration: 3000,
        });
      }

      setDecision('');
      setFeedback('');
      dispatch(setCurrentValidation(null));
      onSubmitSuccess?.();
      onClose();
    } catch {
      showToast({
        type: 'error',
        title: 'Submission Failed',
        message: 'Could not submit validation. Please try again.',
      });
    }
  }, [current, decision, feedback, timeSpent, dispatch, showToast, onClose, onSubmitSuccess]);

  const handleSkip = useCallback(async () => {
    if (!current) return;

    try {
      await dispatch(releaseValidation(current.id)).unwrap();
      dispatch(setCurrentValidation(null));
      setDecision('');
      setFeedback('');
      onClose();
    } catch {
      console.error('Error releasing validation');
    }
  }, [current, dispatch, onClose]);

  if (!isOpen) return null;

  const houndifyResult = current?.aiScores?.houndifyResult;
  const llmResult = current?.aiScores?.ensembleResult;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-[var(--color-surface-base)]/80 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative w-full max-w-6xl max-h-[90vh] mx-4 bg-[var(--color-surface-raised)] rounded-2xl border border-[var(--color-border-default)] shadow-2xl shadow-black/30 flex flex-col overflow-hidden">
        {/* Header */}
        <div className="flex-shrink-0 px-6 py-4 border-b border-[var(--color-border-default)] bg-[var(--color-surface-inset)]">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-xl bg-[var(--color-brand-primary)] flex items-center justify-center">
                <Sparkles size={20} className="text-white" />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-[var(--color-content-primary)]">
                  {current?.testCaseName || 'Validation Review'}
                </h2>
                <div className="flex items-center gap-3 mt-0.5 text-sm text-[var(--color-content-muted)]">
                  <span className="flex items-center gap-1">
                    <Globe size={14} />
                    {current?.languageCode || 'en-US'}
                  </span>
                  <span className="text-[var(--color-content-muted)]">|</span>
                  <span className="flex items-center gap-1">
                    <Clock size={14} />
                    {formatTime(timeSpent)}
                  </span>
                  {current?.confidenceScore && (
                    <>
                      <span className="text-[var(--color-content-muted)]">|</span>
                      <span>Validation Score: {(current.confidenceScore * 100).toFixed(1)}%</span>
                    </>
                  )}
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowShortcuts(!showShortcuts)}
                className="p-2 rounded-lg text-[var(--color-content-muted)] hover:text-[var(--color-content-primary)] hover:bg-[var(--color-interactive-hover)] transition-colors"
                title="Keyboard shortcuts"
              >
                <Keyboard size={18} />
              </button>
              <button
                onClick={onClose}
                className="p-2 rounded-lg text-[var(--color-content-muted)] hover:text-[var(--color-content-primary)] hover:bg-[var(--color-interactive-hover)] transition-colors"
              >
                <X size={20} />
              </button>
            </div>
          </div>

          {/* Keyboard shortcuts tooltip */}
          {showShortcuts && (
            <div className="absolute right-6 top-16 z-10 p-4 bg-[var(--color-surface-raised)] rounded-xl border border-[var(--color-border-default)] shadow-xl text-sm">
              <p className="font-medium text-[var(--color-content-primary)] mb-2">Keyboard Shortcuts</p>
              <div className="space-y-1.5 text-[var(--color-content-secondary)]">
                <div><kbd className="px-1.5 py-0.5 bg-[var(--color-surface-inset)] rounded text-xs">P</kbd> Pass</div>
                <div><kbd className="px-1.5 py-0.5 bg-[var(--color-surface-inset)] rounded text-xs">F</kbd> Fail</div>
                <div><kbd className="px-1.5 py-0.5 bg-[var(--color-surface-inset)] rounded text-xs">E</kbd> Edge Case</div>
                <div><kbd className="px-1.5 py-0.5 bg-[var(--color-surface-inset)] rounded text-xs">D</kbd> Create Defect</div>
                <div><kbd className="px-1.5 py-0.5 bg-[var(--color-surface-inset)] rounded text-xs">Enter</kbd> Submit</div>
                <div><kbd className="px-1.5 py-0.5 bg-[var(--color-surface-inset)] rounded text-xs">S</kbd> Skip</div>
                <div><kbd className="px-1.5 py-0.5 bg-[var(--color-surface-inset)] rounded text-xs">Esc</kbd> Close</div>
              </div>
            </div>
          )}
        </div>

        {/* Content */}
        <div className="flex-1 overflow-hidden flex">
          {/* Left Panel - Input & Audio */}
          <div className="w-2/5 p-6 border-r border-[var(--color-border-default)] overflow-y-auto">
            <div className="space-y-6">
              {/* User Utterance */}
              <div>
                <h3 className="text-sm font-medium text-[var(--color-content-muted)] uppercase tracking-wide mb-3">
                  User Input
                </h3>
                <div className="p-4 bg-[var(--color-surface-inset)] rounded-xl border border-[var(--color-border-default)]">
                  <p className="text-[var(--color-content-primary)] text-lg leading-relaxed">
                    "{current?.inputText || 'No input text available'}"
                  </p>
                </div>
              </div>

              {/* Audio Players */}
              <div className="space-y-3">
                <h3 className="text-sm font-medium text-[var(--color-content-muted)] uppercase tracking-wide">
                  Audio
                </h3>
                {current?.inputAudioUrl && (
                  <AudioPlayerSlim url={current.inputAudioUrl} label="Input Audio" />
                )}
                {current?.responseAudioUrl && (
                  <AudioPlayerSlim url={current.responseAudioUrl} label="Response Audio" />
                )}
                {!current?.inputAudioUrl && !current?.responseAudioUrl && (
                  <div className="p-4 bg-[var(--color-surface-inset)] rounded-xl text-[var(--color-content-muted)] text-center text-sm">
                    No audio available
                  </div>
                )}
              </div>

              {/* AI Response */}
              {current?.aiScores?.houndifyResult?.actual_command_kind && (
                <div>
                  <h3 className="text-sm font-medium text-[var(--color-content-muted)] uppercase tracking-wide mb-3">
                    AI Response
                  </h3>
                  <div className="p-4 bg-[var(--color-surface-inset)] rounded-xl border border-[var(--color-border-default)] space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-[var(--color-content-muted)]">Command Type</span>
                      <span className="px-2.5 py-1 bg-[var(--color-interactive-active)] rounded-lg text-sm font-mono text-[var(--color-content-primary)]">
                        {current.aiScores.houndifyResult.actual_command_kind}
                      </span>
                    </div>
                    {current.aiScores.houndifyResult.asr_confidence !== undefined && (
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-[var(--color-content-muted)]">ASR Confidence</span>
                        <span className="text-[var(--color-content-primary)] font-medium">
                          {(current.aiScores.houndifyResult.asr_confidence * 100).toFixed(1)}%
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Right Panel - Validation Analysis */}
          <div className="flex-1 p-6 overflow-y-auto">
            {/* Tab Navigation */}
            <div className="flex items-center gap-1 mb-6 p-1 bg-[var(--color-surface-inset)] rounded-xl">
              <button
                onClick={() => setActiveTab('houndify')}
                className={`flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  activeTab === 'houndify'
                    ? 'bg-[var(--color-status-info)] text-white shadow-lg'
                    : 'text-[var(--color-content-muted)] hover:text-[var(--color-content-primary)] hover:bg-[var(--color-interactive-active)]'
                }`}
              >
                <Zap size={16} />
                Deterministic
                {houndifyResult && (
                  <StatusBadge status={houndifyResult.passed ? 'pass' : 'fail'} size="sm" />
                )}
              </button>
              <button
                onClick={() => setActiveTab('llm')}
                className={`flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  activeTab === 'llm'
                    ? 'bg-[var(--color-status-purple)] text-white shadow-lg'
                    : 'text-[var(--color-content-muted)] hover:text-[var(--color-content-primary)] hover:bg-[var(--color-interactive-active)]'
                }`}
              >
                <Brain size={16} />
                LLM Ensemble
                {llmResult && (
                  <StatusBadge status={llmResult.final_decision || 'uncertain'} size="sm" />
                )}
              </button>
            </div>

            {/* Houndify Tab Content */}
            {activeTab === 'houndify' && houndifyResult && (
              <div className="space-y-4">
                {/* Overall Status */}
                <div className={`p-4 rounded-xl border ${
                  houndifyResult.passed
                    ? 'bg-[var(--color-status-emerald-bg)] border-[var(--color-status-emerald-bg)]'
                    : 'bg-[var(--color-status-rose-bg)] border-[var(--color-status-rose-bg)]'
                }`}>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      {houndifyResult.passed ? (
                        <CheckCircle className="w-6 h-6 text-[var(--color-status-emerald)]" />
                      ) : (
                        <XCircle className="w-6 h-6 text-[var(--color-status-rose)]" />
                      )}
                      <div>
                        <p className="font-semibold text-[var(--color-content-primary)]">
                          {houndifyResult.passed ? 'All Checks Passed' : 'Validation Failed'}
                        </p>
                        <p className="text-sm text-[var(--color-content-muted)]">
                          Deterministic validation using Houndify rules
                        </p>
                      </div>
                    </div>
                    {houndifyResult.validation_score !== undefined && (
                      <ScoreRing
                        score={houndifyResult.validation_score}
                        label="Validation Score"
                        tooltip="Weighted composite of all Houndify deterministic checks: validation pass/fail (50%), ASR confidence (30%), CommandKind match (20%)."
                      />
                    )}
                  </div>
                </div>

                {/* Command Kind Check */}
                <CollapsibleSection
                  title={
                    <div className="flex items-center gap-2">
                      <span>Command Kind</span>
                      <InfoTooltip text="CommandKind represents the intent category detected by Houndify (e.g., WeatherCommand, MusicCommand). This validates that the correct type of command was understood." />
                    </div>
                  }
                  icon={<Target size={16} className="text-[var(--color-status-info)]" />}
                  badge={
                    houndifyResult.command_kind_match !== undefined && (
                      <StatusBadge status={houndifyResult.command_kind_match ? 'pass' : 'fail'} size="sm" />
                    )
                  }
                  defaultOpen
                >
                  <div className="grid grid-cols-2 gap-3">
                    <div className="p-3 bg-[var(--color-surface-inset)] rounded-lg">
                      <p className="text-xs text-[var(--color-content-muted)] mb-1">Expected</p>
                      <p className="font-mono text-[var(--color-content-primary)]">
                        {houndifyResult.expected_command_kind || '—'}
                      </p>
                    </div>
                    <div className={`p-3 rounded-lg ${
                      houndifyResult.command_kind_match ? 'bg-[var(--color-status-emerald-bg)]' : 'bg-[var(--color-status-rose-bg)]'
                    }`}>
                      <p className="text-xs text-[var(--color-content-muted)] mb-1">Actual</p>
                      <p className={`font-mono ${
                        houndifyResult.command_kind_match ? 'text-[var(--color-status-emerald)]' : 'text-[var(--color-status-rose)]'
                      }`}>
                        {houndifyResult.actual_command_kind || '—'}
                      </p>
                    </div>
                  </div>
                </CollapsibleSection>

                {/* ASR Confidence (actual confidence - how sure the ASR is) */}
                {houndifyResult.asr_confidence !== undefined && (
                  <CollapsibleSection
                    title={
                      <div className="flex items-center gap-2">
                        <span>Speech Recognition Confidence</span>
                        <InfoTooltip text="ASR (Automatic Speech Recognition) confidence indicates how certain the speech recognition system is about what was said. This is actual confidence, not a validation score." />
                      </div>
                    }
                    icon={<MessageSquare size={16} className="text-[var(--color-brand-primary)]" />}
                    badge={
                      houndifyResult.expected_asr_confidence_min !== undefined && (
                        <StatusBadge
                          status={houndifyResult.asr_confidence >= houndifyResult.expected_asr_confidence_min ? 'pass' : 'fail'}
                          size="sm"
                        />
                      )
                    }
                  >
                    <div className="space-y-3">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-[var(--color-content-muted)]">Minimum Required</span>
                        <span className="font-mono text-[var(--color-content-primary)]">
                          {houndifyResult.expected_asr_confidence_min !== undefined
                            ? `${(houndifyResult.expected_asr_confidence_min * 100).toFixed(0)}%`
                            : '—'}
                        </span>
                      </div>
                      <div className="relative h-3 bg-[var(--color-interactive-active)] rounded-full overflow-hidden">
                        {houndifyResult.expected_asr_confidence_min !== undefined && (
                          <div
                            className="absolute top-0 bottom-0 w-0.5 bg-[var(--color-content-muted)] z-10"
                            style={{ left: `${houndifyResult.expected_asr_confidence_min * 100}%` }}
                          />
                        )}
                        <div
                          className={`h-full rounded-full transition-all ${
                            houndifyResult.expected_asr_confidence_min === undefined ||
                            houndifyResult.asr_confidence >= houndifyResult.expected_asr_confidence_min
                              ? 'bg-[var(--color-status-success)]'
                              : 'bg-[var(--color-status-danger)]'
                          }`}
                          style={{ width: `${houndifyResult.asr_confidence * 100}%` }}
                        />
                      </div>
                      <div className="text-right">
                        <span className="text-2xl font-bold text-[var(--color-content-primary)]">
                          {(houndifyResult.asr_confidence * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  </CollapsibleSection>
                )}

                {/* Response Content Validation */}
                {(() => {
                  const contentValidation = houndifyResult.response_content_validation || houndifyResult.response_content_result;
                  if (!contentValidation) return null;

                  return (
                    <CollapsibleSection
                      title="Response Content"
                      icon={<MessageSquare size={16} className="text-[var(--color-status-warning)]" />}
                      badge={<StatusBadge status={contentValidation.passed ? 'pass' : 'fail'} size="sm" />}
                    >
                      {contentValidation.details ? (
                        <div className="space-y-2">
                          {contentValidation.details.contains && (
                            <div className="p-3 bg-[var(--color-surface-inset)] rounded-lg">
                              <div className="flex items-center justify-between mb-2">
                                <span className="text-sm text-[var(--color-content-secondary)]">Required Phrases</span>
                                <StatusBadge status={contentValidation.details.contains.passed ? 'pass' : 'fail'} size="sm" />
                              </div>
                              {contentValidation.details.contains.matched?.length > 0 && (
                                <p className="text-xs text-[var(--color-status-emerald)]">
                                  Matched: {contentValidation.details.contains.matched.join(', ')}
                                </p>
                              )}
                              {contentValidation.details.contains.missing?.length > 0 && (
                                <p className="text-xs text-[var(--color-status-rose)]">
                                  Missing: {contentValidation.details.contains.missing.join(', ')}
                                </p>
                              )}
                            </div>
                          )}
                        </div>
                      ) : (
                        <p className="text-sm text-[var(--color-content-muted)]">No detailed content validation</p>
                      )}
                    </CollapsibleSection>
                  );
                })()}

                {/* Entity Validation */}
                {(current?.expectedEntities || current?.actualEntities || current?.entityValidation) && (
                  <CollapsibleSection
                    title="Entity Validation"
                    icon={<List size={16} className="text-[var(--color-status-info)]" />}
                    badge={
                      current?.entityValidation ? (
                        <StatusBadge
                          status={current.entityValidation.passed ? 'pass' : 'fail'}
                          size="sm"
                        />
                      ) : undefined
                    }
                  >
                    <div className="space-y-3">
                      {/* Show entity validation score if available */}
                      {current?.entityValidation && (
                        <div className="flex items-center justify-between p-2 bg-[var(--color-surface-inset)] rounded-lg">
                          <span className="text-xs text-[var(--color-content-muted)]">Match Score</span>
                          <span className={`text-sm font-mono font-medium ${
                            current.entityValidation.passed
                              ? 'text-[var(--color-status-success)]'
                              : 'text-[var(--color-status-danger)]'
                          }`}>
                            {(current.entityValidation.score * 100).toFixed(0)}%
                          </span>
                        </div>
                      )}
                      {current?.expectedEntities && (
                        <div className="p-3 bg-[var(--color-surface-inset)] rounded-lg">
                          <p className="text-xs text-[var(--color-content-muted)] mb-2 font-medium">Expected Entities</p>
                          <pre className="text-xs font-mono text-[var(--color-content-secondary)] whitespace-pre-wrap overflow-auto max-h-40">
                            {typeof current.expectedEntities === 'string'
                              ? current.expectedEntities
                              : JSON.stringify(current.expectedEntities, null, 2)}
                          </pre>
                        </div>
                      )}
                      {current?.actualEntities && (
                        <div className={`p-3 rounded-lg ${
                          current?.entityValidation?.passed
                            ? 'bg-[var(--color-status-success-bg)]'
                            : 'bg-[var(--color-status-danger-bg)]'
                        }`}>
                          <p className="text-xs text-[var(--color-content-muted)] mb-2 font-medium">Actual Entities</p>
                          <pre className={`text-xs font-mono whitespace-pre-wrap overflow-auto max-h-40 ${
                            current?.entityValidation?.passed
                              ? 'text-[var(--color-status-success)]'
                              : 'text-[var(--color-status-danger)]'
                          }`}>
                            {typeof current.actualEntities === 'string'
                              ? current.actualEntities
                              : JSON.stringify(current.actualEntities, null, 2)}
                          </pre>
                        </div>
                      )}
                      {/* Show entity validation errors if any */}
                      {current?.entityValidation?.errors && current.entityValidation.errors.length > 0 && (
                        <div className="p-2 bg-[var(--color-status-danger-bg)] rounded-lg">
                          <p className="text-xs text-[var(--color-status-danger)] font-medium mb-1">Validation Errors:</p>
                          <ul className="text-xs text-[var(--color-status-danger)] list-disc list-inside">
                            {current.entityValidation.errors.map((error, idx) => (
                              <li key={idx}>{error}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </CollapsibleSection>
                )}
              </div>
            )}

            {/* LLM Tab Content */}
            {activeTab === 'llm' && llmResult && (
              <div className="space-y-4">
                {/* Overall Score */}
                <div className="p-5 rounded-xl bg-[var(--color-status-purple-bg)] border border-[var(--color-status-purple-bg)]">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-[var(--color-content-muted)] mb-1">Final Decision</p>
                      <StatusBadge status={llmResult.final_decision || 'uncertain'} />
                      <p className="text-sm text-[var(--color-content-muted)] mt-2">
                        Consensus: <span className="text-[var(--color-content-primary)]">{llmResult.consensus_type?.replace(/_/g, ' ')}</span>
                      </p>
                    </div>
                    <ScoreRing
                      score={llmResult.final_score}
                      size={80}
                      label="Ensemble Score"
                      tooltip="Final weighted score from LLM ensemble validation. Based on consensus between Evaluator A (Gemini) and Evaluator B (GPT), with Curator (Claude) tie-breaking when needed."
                    />
                  </div>
                </div>

                {/* Evaluator Scores */}
                <CollapsibleSection
                  title="Evaluator Comparison"
                  icon={<Brain size={16} className="text-[var(--color-status-purple)]" />}
                  defaultOpen
                >
                  <div className="grid grid-cols-2 gap-4">
                    {/* Evaluator A */}
                    <div className="p-4 bg-[var(--color-status-info-bg)] rounded-xl border border-[var(--color-status-info-bg)]">
                      <div className="flex items-center justify-between mb-3">
                        <div>
                          <p className="text-sm font-medium text-[var(--color-content-primary)]">Evaluator A</p>
                          <p className="text-xs text-[var(--color-content-muted)]">Gemini 2.5 Flash</p>
                        </div>
                        <span className="text-2xl font-bold text-[var(--color-status-info)]">
                          {(llmResult.evaluator_a_score * 100).toFixed(0)}%
                        </span>
                      </div>
                      <div className="h-2 bg-[var(--color-interactive-active)] rounded-full overflow-hidden">
                        <div
                          className="h-full bg-[var(--color-status-info)] rounded-full"
                          style={{ width: `${llmResult.evaluator_a_score * 100}%` }}
                        />
                      </div>

                      {/* Detailed Criterion Scores for Evaluator A */}
                      {(llmResult as any).evaluator_a_scores && (
                        <div className="mt-4 pt-3 border-t border-[var(--color-status-info-bg)] space-y-2.5">
                          <p className="text-xs font-medium text-[var(--color-content-secondary)] mb-2">Criterion Breakdown</p>
                          {(llmResult as any).evaluator_a_scores.relevance !== undefined && (
                            <CriterionScoreBar
                              label="Relevance"
                              score={(llmResult as any).evaluator_a_scores.relevance}
                              weight={(llmResult as any).evaluator_a_scores.relevance_weight || 0.2}
                              tooltip="How well the response addresses the user's query and stays on topic"
                            />
                          )}
                          {(llmResult as any).evaluator_a_scores.correctness !== undefined && (
                            <CriterionScoreBar
                              label="Correctness"
                              score={(llmResult as any).evaluator_a_scores.correctness}
                              weight={(llmResult as any).evaluator_a_scores.correctness_weight || 0.25}
                              tooltip="Factual accuracy and whether the response provides correct information"
                            />
                          )}
                          {(llmResult as any).evaluator_a_scores.completeness !== undefined && (
                            <CriterionScoreBar
                              label="Completeness"
                              score={(llmResult as any).evaluator_a_scores.completeness}
                              weight={(llmResult as any).evaluator_a_scores.completeness_weight || 0.2}
                              tooltip="Whether the response fully addresses all aspects of the query"
                            />
                          )}
                          {(llmResult as any).evaluator_a_scores.tone !== undefined && (
                            <CriterionScoreBar
                              label="Tone"
                              score={(llmResult as any).evaluator_a_scores.tone}
                              weight={(llmResult as any).evaluator_a_scores.tone_weight || 0.15}
                              tooltip="Appropriateness of the response tone and conversational style"
                            />
                          )}
                          {(llmResult as any).evaluator_a_scores.entity_accuracy !== undefined && (
                            <CriterionScoreBar
                              label="Entity Accuracy"
                              score={(llmResult as any).evaluator_a_scores.entity_accuracy}
                              weight={(llmResult as any).evaluator_a_scores.entity_accuracy_weight || 0.2}
                              tooltip="Accuracy of extracted entities (dates, locations, names, numbers)"
                            />
                          )}
                        </div>
                      )}

                      {llmResult.evaluator_a_latency_ms > 0 && (
                        <p className="text-xs text-[var(--color-content-muted)] mt-2 flex items-center gap-1">
                          <Clock size={12} /> {llmResult.evaluator_a_latency_ms}ms
                        </p>
                      )}
                    </div>

                    {/* Evaluator B */}
                    <div className="p-4 bg-[var(--color-status-emerald-bg)] rounded-xl border border-[var(--color-status-emerald-bg)]">
                      <div className="flex items-center justify-between mb-3">
                        <div>
                          <p className="text-sm font-medium text-[var(--color-content-primary)]">Evaluator B</p>
                          <p className="text-xs text-[var(--color-content-muted)]">GPT-4.1 Mini</p>
                        </div>
                        <span className="text-2xl font-bold text-[var(--color-status-emerald)]">
                          {(llmResult.evaluator_b_score * 100).toFixed(0)}%
                        </span>
                      </div>
                      <div className="h-2 bg-[var(--color-interactive-active)] rounded-full overflow-hidden">
                        <div
                          className="h-full bg-[var(--color-status-success)] rounded-full"
                          style={{ width: `${llmResult.evaluator_b_score * 100}%` }}
                        />
                      </div>

                      {/* Detailed Criterion Scores for Evaluator B */}
                      {(llmResult as any).evaluator_b_scores && (
                        <div className="mt-4 pt-3 border-t border-[var(--color-status-emerald-bg)] space-y-2.5">
                          <p className="text-xs font-medium text-[var(--color-content-secondary)] mb-2">Criterion Breakdown</p>
                          {(llmResult as any).evaluator_b_scores.relevance !== undefined && (
                            <CriterionScoreBar
                              label="Relevance"
                              score={(llmResult as any).evaluator_b_scores.relevance}
                              weight={(llmResult as any).evaluator_b_scores.relevance_weight || 0.2}
                              tooltip="How well the response addresses the user's query and stays on topic"
                            />
                          )}
                          {(llmResult as any).evaluator_b_scores.correctness !== undefined && (
                            <CriterionScoreBar
                              label="Correctness"
                              score={(llmResult as any).evaluator_b_scores.correctness}
                              weight={(llmResult as any).evaluator_b_scores.correctness_weight || 0.25}
                              tooltip="Factual accuracy and whether the response provides correct information"
                            />
                          )}
                          {(llmResult as any).evaluator_b_scores.completeness !== undefined && (
                            <CriterionScoreBar
                              label="Completeness"
                              score={(llmResult as any).evaluator_b_scores.completeness}
                              weight={(llmResult as any).evaluator_b_scores.completeness_weight || 0.2}
                              tooltip="Whether the response fully addresses all aspects of the query"
                            />
                          )}
                          {(llmResult as any).evaluator_b_scores.tone !== undefined && (
                            <CriterionScoreBar
                              label="Tone"
                              score={(llmResult as any).evaluator_b_scores.tone}
                              weight={(llmResult as any).evaluator_b_scores.tone_weight || 0.15}
                              tooltip="Appropriateness of the response tone and conversational style"
                            />
                          )}
                          {(llmResult as any).evaluator_b_scores.entity_accuracy !== undefined && (
                            <CriterionScoreBar
                              label="Entity Accuracy"
                              score={(llmResult as any).evaluator_b_scores.entity_accuracy}
                              weight={(llmResult as any).evaluator_b_scores.entity_accuracy_weight || 0.2}
                              tooltip="Accuracy of extracted entities (dates, locations, names, numbers)"
                            />
                          )}
                        </div>
                      )}

                      {llmResult.evaluator_b_latency_ms > 0 && (
                        <p className="text-xs text-[var(--color-content-muted)] mt-2 flex items-center gap-1">
                          <Clock size={12} /> {llmResult.evaluator_b_latency_ms}ms
                        </p>
                      )}
                    </div>
                  </div>

                  {/* Score Difference */}
                  <div className="mt-4 p-3 bg-[var(--color-surface-inset)] rounded-lg flex items-center justify-between">
                    <span className="text-sm text-[var(--color-content-muted)]">Score Difference</span>
                    <span className={`font-medium ${
                      llmResult.score_difference <= 0.15 ? 'text-[var(--color-status-emerald)]' :
                      llmResult.score_difference < 0.40 ? 'text-[var(--color-status-amber)]' : 'text-[var(--color-status-rose)]'
                    }`}>
                      {(llmResult.score_difference * 100).toFixed(1)}%
                      {llmResult.score_difference <= 0.15 ? ' (High Consensus)' :
                       llmResult.score_difference < 0.40 ? ' (Curator Needed)' : ' (Disagreement)'}
                    </span>
                  </div>
                </CollapsibleSection>

                {/* Curator Decision */}
                {llmResult.curator_decision && (
                  <CollapsibleSection
                    title="Curator Decision"
                    icon={<Sparkles size={16} className="text-[var(--color-status-warning)]" />}
                    badge={<StatusBadge status={llmResult.curator_decision} size="sm" />}
                    defaultOpen
                  >
                    <div className="space-y-3">
                      <div className="p-3 bg-[var(--color-status-amber-bg)] rounded-lg border border-[var(--color-status-amber-bg)]">
                        <p className="text-xs text-[var(--color-content-muted)] mb-1">Claude Sonnet 4.5</p>
                        <p className="text-sm text-[var(--color-content-secondary)]">{llmResult.curator_reasoning}</p>
                      </div>
                      {llmResult.curator_latency_ms && (
                        <p className="text-xs text-[var(--color-content-muted)] flex items-center gap-1">
                          <Clock size={12} /> {llmResult.curator_latency_ms}ms
                        </p>
                      )}
                    </div>
                  </CollapsibleSection>
                )}

                {/* Evaluator Reasoning */}
                <CollapsibleSection
                  title="Evaluator Reasoning"
                  icon={<MessageSquare size={16} className="text-[var(--color-status-info)]" />}
                >
                  <div className="space-y-3">
                    {llmResult.evaluator_a_reasoning && (
                      <div className="p-3 bg-[var(--color-status-info-bg)] rounded-lg border border-[var(--color-status-info-bg)]">
                        <p className="text-xs text-[var(--color-status-info)] mb-1">Evaluator A (Gemini)</p>
                        <p className="text-sm text-[var(--color-content-secondary)]">{llmResult.evaluator_a_reasoning}</p>
                      </div>
                    )}
                    {llmResult.evaluator_b_reasoning && (
                      <div className="p-3 bg-[var(--color-status-emerald-bg)] rounded-lg border border-[var(--color-status-emerald-bg)]">
                        <p className="text-xs text-[var(--color-status-emerald)] mb-1">Evaluator B (GPT)</p>
                        <p className="text-sm text-[var(--color-content-secondary)]">{llmResult.evaluator_b_reasoning}</p>
                      </div>
                    )}
                  </div>
                </CollapsibleSection>

                {/* Total Latency */}
                {llmResult.latency_ms > 0 && (
                  <div className="p-3 bg-[var(--color-surface-inset)] rounded-xl flex items-center justify-between">
                    <span className="text-sm text-[var(--color-content-muted)]">Total Pipeline Latency</span>
                    <span className="font-mono text-[var(--color-content-primary)]">{llmResult.latency_ms}ms</span>
                  </div>
                )}
              </div>
            )}

            {/* No validation data */}
            {!houndifyResult && !llmResult && (
              <div className="flex flex-col items-center justify-center py-12 text-[var(--color-content-muted)]">
                <AlertTriangle size={48} className="mb-4 opacity-50" />
                <p>No validation details available</p>
              </div>
            )}
          </div>
        </div>

        {/* Footer - Decision Panel */}
        {!isCompleted && (
          <div className="flex-shrink-0 px-6 py-4 border-t border-[var(--color-border-default)] bg-[var(--color-surface-inset)]">
            {/* Decision Guide */}
            <div className="mb-4 p-4 bg-[var(--color-status-info-bg)] rounded-xl border border-[var(--color-status-info-bg)]">
              <div className="flex items-start gap-2 mb-2">
                <Info size={16} className="text-[var(--color-status-info)] mt-0.5 flex-shrink-0" />
                <div className="text-sm text-[var(--color-content-secondary)]">
                  <p className="font-medium text-[var(--color-status-info)] mb-1">Decision Guide</p>
                  <p className="text-xs leading-relaxed">
                    Your decision affects how we track AI validation accuracy and system improvements:
                  </p>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3 mt-3 text-xs">
                <div className="flex gap-2">
                  <CheckCircle size={14} className="text-[var(--color-status-emerald)] mt-0.5 flex-shrink-0" />
                  <div>
                    <span className="font-medium text-[var(--color-content-primary)]">Pass:</span>
                    <span className="text-[var(--color-content-secondary)]"> Test succeeded. Counts toward AI agreement metrics.</span>
                  </div>
                </div>
                <div className="flex gap-2">
                  <XCircle size={14} className="text-[var(--color-status-rose)] mt-0.5 flex-shrink-0" />
                  <div>
                    <span className="font-medium text-[var(--color-content-primary)]">Fail:</span>
                    <span className="text-[var(--color-content-secondary)]"> Test failed. Counts toward AI agreement metrics.</span>
                  </div>
                </div>
                <div className="flex gap-2">
                  <AlertTriangle size={14} className="text-[var(--color-status-amber)] mt-0.5 flex-shrink-0" />
                  <div>
                    <span className="font-medium text-[var(--color-content-primary)]">Edge Case:</span>
                    <span className="text-[var(--color-content-secondary)]"> Challenging scenario. Tracked separately, added to knowledge base for AI improvement.</span>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Bug size={14} className="text-[var(--color-status-danger)] mt-0.5 flex-shrink-0" />
                  <div>
                    <span className="font-medium text-[var(--color-content-primary)]">Create Defect:</span>
                    <span className="text-[var(--color-content-secondary)]"> Test failed AND creates trackable defect for investigation/resolution. Counts as "fail" in metrics.</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="flex items-center justify-between gap-6">
              {/* Decision Buttons */}
              <div className="flex items-center gap-2">
                <span className="text-sm text-[var(--color-content-muted)] mr-2">Decision:</span>
                <button
                  onClick={() => setDecision('pass')}
                  className={`px-5 py-2.5 rounded-xl font-medium transition-all ${
                    decision === 'pass'
                      ? 'bg-[var(--color-status-success)] text-white shadow-lg'
                      : 'bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] hover:bg-[var(--color-status-success-bg)] hover:text-[var(--color-status-success)] border border-[var(--color-border-default)]'
                  }`}
                >
                  <span className="flex items-center gap-2">
                    <CheckCircle size={16} />
                    Pass
                    <kbd className="text-xs opacity-60 bg-[var(--color-surface-inset)] px-1.5 rounded">P</kbd>
                  </span>
                </button>
                <button
                  onClick={() => setDecision('fail')}
                  className={`px-5 py-2.5 rounded-xl font-medium transition-all ${
                    decision === 'fail'
                      ? 'bg-[var(--color-status-danger)] text-white shadow-lg'
                      : 'bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] hover:bg-[var(--color-status-danger-bg)] hover:text-[var(--color-status-danger)] border border-[var(--color-border-default)]'
                  }`}
                >
                  <span className="flex items-center gap-2">
                    <XCircle size={16} />
                    Fail
                    <kbd className="text-xs opacity-60 bg-[var(--color-surface-inset)] px-1.5 rounded">F</kbd>
                  </span>
                </button>
                <button
                  onClick={() => setDecision('edge_case')}
                  className={`px-5 py-2.5 rounded-xl font-medium transition-all ${
                    decision === 'edge_case'
                      ? 'bg-[var(--color-status-warning)] text-white shadow-lg'
                      : 'bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] hover:bg-[var(--color-status-warning-bg)] hover:text-[var(--color-status-warning)] border border-[var(--color-border-default)]'
                  }`}
                >
                  <span className="flex items-center gap-2 whitespace-nowrap">
                    <AlertTriangle size={16} />
                    Edge
                    <kbd className="text-xs opacity-60 bg-[var(--color-surface-inset)] px-1.5 rounded">E</kbd>
                  </span>
                </button>
                <button
                  onClick={() => setDecision('create_defect')}
                  className={`px-5 py-2.5 rounded-xl font-medium transition-all ${
                    decision === 'create_defect'
                      ? 'bg-[var(--color-status-danger)] text-white shadow-lg'
                      : 'bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] hover:bg-[var(--color-status-danger-bg)] hover:text-[var(--color-status-danger)] border border-[var(--color-border-default)]'
                  }`}
                >
                  <span className="flex items-center gap-2 whitespace-nowrap">
                    <Bug size={16} />
                    Defect
                    <kbd className="text-xs opacity-60 bg-[var(--color-surface-inset)] px-1.5 rounded">D</kbd>
                  </span>
                </button>
              </div>

              {/* Feedback & Actions */}
              <div className="flex items-center gap-3">
                <input
                  type="text"
                  value={feedback}
                  onChange={(e) => setFeedback(e.target.value)}
                  placeholder="Add notes (optional)..."
                  className="w-48 px-4 py-2 bg-[var(--color-surface-raised)] border border-[var(--color-border-default)] rounded-xl text-[var(--color-content-primary)] placeholder-[var(--color-content-muted)] focus:outline-none focus:ring-2 focus:ring-[var(--color-brand-primary)]/50 focus:border-[var(--color-brand-primary)]"
                />
                <button
                  onClick={handleSkip}
                  disabled={loading}
                  className="px-4 py-2.5 rounded-xl font-medium bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] hover:bg-[var(--color-interactive-hover)] border border-[var(--color-border-default)] transition-all flex items-center gap-2 disabled:opacity-50"
                >
                  <SkipForward size={16} />
                  Skip
                </button>
                <button
                  onClick={handleSubmit}
                  disabled={loading || !decision}
                  className="px-6 py-2.5 rounded-xl font-medium bg-[var(--color-brand-primary)] text-white shadow-lg hover:bg-[var(--color-brand-hover)] transition-all flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Send size={16} />
                  Submit
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Completed State - Validation History */}
        {isCompleted && current && (
          <div className="flex-shrink-0 border-t border-[var(--color-border-default)] bg-[var(--color-surface-inset)]">
            <CollapsibleSection
              title="Validation History"
              icon={<CheckCircle size={16} className="text-[var(--color-status-success)]" />}
              badge={
                <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-medium bg-[var(--color-status-emerald-bg)] text-[var(--color-status-emerald)]">
                  <CheckCircle size={14} />
                  Completed
                </span>
              }
              defaultOpen
            >
              <div className="space-y-3">
                {/* Most Recent Decision */}
                {current.humanValidationDecision && (
                  <div className="p-4 bg-[var(--color-surface-raised)] rounded-xl border border-[var(--color-border-default)]">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-3">
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                          current.humanValidationDecision === 'pass'
                            ? 'bg-[var(--color-status-emerald-bg)]'
                            : current.humanValidationDecision === 'fail'
                            ? 'bg-[var(--color-status-rose-bg)]'
                            : 'bg-[var(--color-status-amber-bg)]'
                        }`}>
                          {current.humanValidationDecision === 'pass' && <CheckCircle size={20} className="text-[var(--color-status-emerald)]" />}
                          {current.humanValidationDecision === 'fail' && <XCircle size={20} className="text-[var(--color-status-rose)]" />}
                          {current.humanValidationDecision === 'edge_case' && <AlertTriangle size={20} className="text-[var(--color-status-amber)]" />}
                        </div>
                        <div>
                          <p className="font-medium text-[var(--color-content-primary)] capitalize">
                            {current.humanValidationDecision.replace('_', ' ')}
                          </p>
                          <p className="text-xs text-[var(--color-content-muted)]">
                            {current.humanValidationValidatorName || 'Unknown Validator'}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-xs text-[var(--color-content-muted)]">
                          {current.humanValidationSubmittedAt
                            ? new Date(current.humanValidationSubmittedAt).toLocaleString()
                            : 'Unknown time'
                          }
                        </p>
                      </div>
                    </div>
                    {current.humanValidationFeedback && (
                      <div className="mt-3 p-3 bg-[var(--color-surface-inset)] rounded-lg">
                        <p className="text-xs text-[var(--color-content-muted)] mb-1">Feedback</p>
                        <p className="text-sm text-[var(--color-content-secondary)]">{current.humanValidationFeedback}</p>
                      </div>
                    )}
                  </div>
                )}

                {/* Full Validation History */}
                {current.validationHistory && current.validationHistory.length > 0 && (
                  <div className="space-y-2">
                    <p className="text-xs font-medium text-[var(--color-content-muted)] uppercase tracking-wide">
                      All Decisions ({current.validationHistory.length})
                    </p>
                    {current.validationHistory.map((entry, index) => (
                      <div key={entry.id} className="p-3 bg-[var(--color-surface-raised)] rounded-lg border border-[var(--color-border-default)]">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <StatusBadge status={entry.decision} size="sm" />
                            <span className="text-sm text-[var(--color-content-secondary)]">
                              {entry.validatorName || 'Unknown'}
                            </span>
                            {entry.isSecondOpinion && (
                              <span className="px-2 py-0.5 bg-[var(--color-status-amber-bg)] text-[var(--color-status-amber)] text-xs rounded-full">
                                2nd Opinion
                              </span>
                            )}
                          </div>
                          <div className="flex items-center gap-3 text-xs text-[var(--color-content-muted)]">
                            {entry.timeSpentSeconds !== null && (
                              <span className="flex items-center gap-1">
                                <Clock size={12} />
                                {formatTime(entry.timeSpentSeconds)}
                              </span>
                            )}
                            <span>{new Date(entry.submittedAt || entry.createdAt || '').toLocaleString()}</span>
                          </div>
                        </div>
                        {entry.feedback && (
                          <p className="mt-2 text-xs text-[var(--color-content-secondary)] italic">"{entry.feedback}"</p>
                        )}
                      </div>
                    ))}
                  </div>
                )}

                {/* No history available */}
                {!current.humanValidationDecision && (!current.validationHistory || current.validationHistory.length === 0) && (
                  <div className="p-4 text-center text-[var(--color-content-muted)] text-sm">
                    No validation history available
                  </div>
                )}
              </div>
            </CollapsibleSection>
          </div>
        )}
      </div>
    </div>
  );
};

export default ValidationModal;
