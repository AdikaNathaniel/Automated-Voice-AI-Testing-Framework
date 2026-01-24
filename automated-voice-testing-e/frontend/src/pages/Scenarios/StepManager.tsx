/**
 * Step Manager Component
 *
 * Manages scenario steps with SOTA design featuring:
 * - Drag-and-drop reordering with visual feedback
 * - Audio upload with waveform visualization
 * - Multi-language support with elegant variant management
 * - Real-time transcription display with confidence scores
 */

import React, { useState, useRef, useEffect, useCallback } from 'react';
import {
  Plus,
  Trash2,
  GripVertical,
  ChevronDown,
  ChevronUp,
  Upload,
  Mic,
  Play,
  Pause,
  X,
  Volume2,
  FileAudio,
  CheckCircle,
  AlertCircle,
  Loader2,
  Clock,
  CloudUpload,
  Info,
  AudioWaveform,
  Globe,
  Waves,
  Car,
  Building2,
  Factory,
  Shuffle,
  Eye,
  Square,
} from 'lucide-react';
import LanguageVariantManager, { type LanguageVariant } from './LanguageVariantManager';
import apiClient from '../../services/api';

export interface NoiseAppliedInfo {
  profile: string;
  profile_name: string;
  snr_db: number;
  category?: string;
}

export interface NoiseProfile {
  name: string;
  category: string;
  description?: string;
  default_snr_db: number;
  difficulty: string;
}

export interface UploadedAudioInfo {
  s3_key: string;
  transcription: string;
  duration_ms: number;
  original_format: string;
  stt_confidence: number;
  language_code: string;
  noise_applied?: NoiseAppliedInfo;
}

export interface ScenarioStepData {
  id?: string;
  step_order: number;
  user_utterance: string;
  step_metadata?: {
    audio_source?: 'tts' | 'uploaded';
    uploaded_audio?: Record<string, UploadedAudioInfo>;
    primary_language?: string;
    language_variants?: LanguageVariant[];
    [key: string]: any;
  };
  follow_up_action?: string;
  expected_outcomes?: any[];
}

interface StepManagerProps {
  steps: ScenarioStepData[];
  onChange: (steps: ScenarioStepData[]) => void;
  onStepSelect?: (stepIndex: number) => void;
  selectedStepIndex?: number;
  scenarioId?: string;
}

// Confidence Ring Component with animated SVG
const ConfidenceRing: React.FC<{ score: number; size?: number }> = ({ score, size = 44 }) => {
  const percentage = Math.round(score * 100);
  const strokeWidth = 3;
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - score * circumference;

  const getColor = () => {
    if (score >= 0.9) return { stroke: '#10b981', bg: 'rgba(16, 185, 129, 0.1)' };
    if (score >= 0.7) return { stroke: '#14b8a6', bg: 'rgba(20, 184, 166, 0.1)' };
    if (score >= 0.5) return { stroke: '#f59e0b', bg: 'rgba(245, 158, 11, 0.1)' };
    return { stroke: '#ef4444', bg: 'rgba(239, 68, 68, 0.1)' };
  };

  const colors = getColor();

  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="transform -rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill={colors.bg}
          stroke="rgba(148, 163, 184, 0.2)"
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
          className="transition-all duration-700"
        />
      </svg>
      <span className="absolute inset-0 flex items-center justify-center text-xs font-bold text-[var(--color-content-primary)]">
        {percentage}%
      </span>
    </div>
  );
};

// Audio Player with waveform visualization
const AudioPlayerCard: React.FC<{
  audioInfo: UploadedAudioInfo;
  onRemove: () => void;
}> = ({ audioInfo, onRemove }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const audioRef = useRef<HTMLAudioElement>(null);
  const animationRef = useRef<number>();

  const formatDuration = (ms: number) => {
    const seconds = Math.floor(ms / 1000);
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const togglePlay = useCallback(() => {
    if (!audioRef.current) return;
    if (isPlaying) {
      audioRef.current.pause();
      if (animationRef.current) cancelAnimationFrame(animationRef.current);
    } else {
      audioRef.current.play().catch(console.error);
    }
    setIsPlaying(!isPlaying);
  }, [isPlaying]);

  const updateProgress = useCallback(() => {
    if (audioRef.current && !audioRef.current.paused) {
      const current = audioRef.current.currentTime;
      const duration = audioRef.current.duration || audioInfo.duration_ms / 1000;
      setProgress((current / duration) * 100);
      animationRef.current = requestAnimationFrame(updateProgress);
    }
  }, [audioInfo.duration_ms]);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const handlePlay = () => {
      setIsPlaying(true);
      updateProgress();
    };
    const handlePause = () => {
      setIsPlaying(false);
      if (animationRef.current) cancelAnimationFrame(animationRef.current);
    };
    const handleEnded = () => {
      setIsPlaying(false);
      setProgress(0);
      if (animationRef.current) cancelAnimationFrame(animationRef.current);
    };

    audio.addEventListener('play', handlePlay);
    audio.addEventListener('pause', handlePause);
    audio.addEventListener('ended', handleEnded);

    return () => {
      audio.removeEventListener('play', handlePlay);
      audio.removeEventListener('pause', handlePause);
      audio.removeEventListener('ended', handleEnded);
      if (animationRef.current) cancelAnimationFrame(animationRef.current);
    };
  }, [updateProgress]);

  // Generate waveform bars
  const waveformBars = Array.from({ length: 35 }, () => Math.random() * 0.6 + 0.4);

  return (
    <div className="space-y-3">
      {/* Audio Player */}
      <div className="flex items-center gap-3 p-3 bg-gradient-to-r from-[var(--color-status-teal-bg)] to-[var(--color-status-teal-bg)] rounded-xl border border-[var(--color-status-teal-bg)]">
        <audio ref={audioRef} src={audioInfo.s3_key} />

        {/* Play Button */}
        <button
          onClick={togglePlay}
          className="w-10 h-10 rounded-full bg-gradient-to-br from-teal-400 to-teal-600 flex items-center justify-center text-white shadow-lg shadow-teal-500/20 hover:shadow-teal-500/40 transition-all hover:scale-105 flex-shrink-0"
        >
          {isPlaying ? <Pause size={16} /> : <Play size={16} className="ml-0.5" />}
        </button>

        {/* Waveform Visualization */}
        <div className="flex-1 flex items-center gap-0.5 h-8">
          {waveformBars.map((height, i) => {
            const barProgress = (i / waveformBars.length) * 100;
            return (
              <div
                key={i}
                className="flex-1 rounded-full transition-colors duration-100"
                style={{
                  height: `${height * 100}%`,
                  backgroundColor:
                    barProgress <= progress ? 'rgb(20 184 166)' : 'rgba(148, 163, 184, 0.3)',
                }}
              />
            );
          })}
        </div>

        {/* Info & Controls */}
        <div className="flex items-center gap-3 flex-shrink-0">
          <div className="text-right">
            <div className="flex items-center gap-1 text-xs text-[var(--color-content-muted)]">
              <Clock size={12} />
              {formatDuration(audioInfo.duration_ms)}
            </div>
            <div className="text-xs font-medium text-[var(--color-content-secondary)]">
              {audioInfo.original_format.toUpperCase()}
            </div>
          </div>
          <ConfidenceRing score={audioInfo.stt_confidence} size={40} />
          <button
            onClick={onRemove}
            className="p-1.5 text-[var(--color-content-muted)] hover:text-[var(--color-status-danger)] hover:bg-[var(--color-status-danger-bg)] rounded-lg transition-colors"
          >
            <X size={16} />
          </button>
        </div>
      </div>

      {/* Transcription Card */}
      <div className="p-3 bg-[var(--color-surface-raised)]/50 rounded-lg border border-[var(--color-border-default)]">
        <div className="flex items-center gap-2 mb-1.5">
          <CheckCircle size={14} className="text-[var(--color-status-success)]" />
          <span className="text-xs font-medium text-[var(--color-content-muted)] uppercase tracking-wide">
            Transcription
          </span>
        </div>
        <p className="text-sm text-[var(--color-content-secondary)] leading-relaxed">
          "{audioInfo.transcription}"
        </p>
      </div>

      {/* Noise Applied Indicator */}
      {audioInfo.noise_applied && (
        <div className="p-3 bg-gradient-to-r from-amber-500/10 to-orange-500/10 rounded-lg border border-amber-500/20">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Waves size={14} className="text-amber-500" />
              <span className="text-xs font-medium text-amber-600 uppercase tracking-wide">
                Noise Applied
              </span>
            </div>
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-1.5">
                {audioInfo.noise_applied.category === 'vehicle' && <Car size={12} className="text-amber-500" />}
                {audioInfo.noise_applied.category === 'environmental' && <Building2 size={12} className="text-amber-500" />}
                {audioInfo.noise_applied.category === 'industrial' && <Factory size={12} className="text-amber-500" />}
                <span className="text-xs text-[var(--color-content-secondary)]">
                  {audioInfo.noise_applied.profile_name}
                </span>
              </div>
              <span className="text-xs font-mono px-2 py-0.5 bg-amber-500/20 text-amber-600 rounded">
                {audioInfo.noise_applied.snr_db.toFixed(1)} dB SNR
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Drag and Drop Upload Zone
const AudioUploadZone: React.FC<{
  onUpload: (file: File) => void;
  isUploading: boolean;
  uploadProgress: number;
  disabled?: boolean;
  disabledMessage?: string;
}> = ({ onUpload, isUploading, uploadProgress, disabled, disabledMessage }) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    if (!disabled) setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (disabled) return;
    const files = e.dataTransfer.files;
    if (files.length > 0 && files[0].type.startsWith('audio/')) {
      onUpload(files[0]);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      onUpload(files[0]);
      e.target.value = '';
    }
  };

  if (disabled) {
    return (
      <div className="border-2 border-dashed border-[var(--color-border-default)] rounded-xl p-4 text-center bg-[var(--color-surface-inset)]/30">
        <div className="w-10 h-10 mx-auto rounded-full bg-[var(--color-surface-inset)] flex items-center justify-center mb-2">
          <AlertCircle size={18} className="text-[var(--color-status-warning)]" />
        </div>
        <p className="text-sm text-[var(--color-status-amber)]">{disabledMessage}</p>
      </div>
    );
  }

  return (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onClick={() => !isUploading && fileInputRef.current?.click()}
      className={`relative border-2 border-dashed rounded-xl p-4 text-center cursor-pointer transition-all ${
        isDragOver
          ? 'border-[var(--color-status-teal)] bg-[var(--color-status-teal-bg)] scale-[1.02]'
          : isUploading
            ? 'border-[var(--color-border-strong)] bg-[var(--color-surface-inset)]/50 cursor-wait'
            : 'border-[var(--color-border-strong)] hover:border-[var(--color-status-teal)] hover:bg-[var(--color-interactive-hover)]/30'
      }`}
    >
      <input
        ref={fileInputRef}
        type="file"
        accept="audio/*"
        onChange={handleFileSelect}
        className="hidden"
        disabled={isUploading}
      />

      {isUploading ? (
        <div className="space-y-3">
          <div className="w-10 h-10 mx-auto rounded-full bg-[var(--color-status-teal-bg)] flex items-center justify-center">
            <Loader2 size={20} className="text-[var(--color-status-teal)] animate-spin" />
          </div>
          <div>
            <p className="text-sm font-medium text-[var(--color-content-secondary)]">
              Uploading & Transcribing...
            </p>
            <p className="text-xs text-[var(--color-content-muted)] mt-1">
              Processing audio with Whisper AI
            </p>
          </div>
          <div className="w-full h-2 bg-[var(--color-surface-inset)] rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-teal-400 to-cyan-500 rounded-full transition-all duration-300 ease-out"
              style={{ width: `${uploadProgress}%` }}
            />
          </div>
        </div>
      ) : isDragOver ? (
        <div className="space-y-2">
          <div className="w-12 h-12 mx-auto rounded-full bg-[var(--color-status-teal-bg)] flex items-center justify-center">
            <CloudUpload size={24} className="text-[var(--color-status-teal)]" />
          </div>
          <p className="text-sm font-medium text-[var(--color-status-teal)]">Drop audio file here</p>
        </div>
      ) : (
        <div className="space-y-2">
          <div className="w-10 h-10 mx-auto rounded-full bg-[var(--color-surface-inset)] flex items-center justify-center">
            <Upload size={18} className="text-[var(--color-content-muted)]" />
          </div>
          <div>
            <p className="text-sm text-[var(--color-content-secondary)]">
              <span className="font-medium text-[var(--color-status-teal)]">Click to upload</span> or drag and drop
            </p>
            <p className="text-xs text-[var(--color-content-muted)] mt-1">
              WAV, MP3, OGG, or FLAC (max 25MB)
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

// Info Tooltip Component
const InfoTooltip: React.FC<{ text: string }> = ({ text }) => {
  const [show, setShow] = useState(false);

  return (
    <div className="relative inline-flex">
      <button
        type="button"
        className="inline-flex items-center justify-center w-4 h-4 rounded-full text-[var(--color-content-muted)] hover:text-[var(--color-content-secondary)] hover:bg-[var(--color-interactive-active)] transition-colors"
        onMouseEnter={() => setShow(true)}
        onMouseLeave={() => setShow(false)}
        onClick={(e) => e.stopPropagation()}
      >
        <Info size={12} />
      </button>
      {show && (
        <div className="absolute left-1/2 bottom-full mb-2 px-3 py-2 bg-[var(--color-surface-overlay)] text-white text-xs rounded-lg shadow-xl border border-[var(--color-border-strong)] pointer-events-none z-50 w-56 -translate-x-1/2">
          {text}
          <div className="absolute left-1/2 top-full -translate-x-1/2 border-4 border-transparent border-t-[var(--color-surface-overlay)]" />
        </div>
      )}
    </div>
  );
};

// Main StepManager Component
export const StepManager: React.FC<StepManagerProps> = ({
  steps,
  onChange,
  onStepSelect,
  selectedStepIndex,
  scenarioId,
}) => {
  const [expandedSteps, setExpandedSteps] = useState<Set<number>>(new Set([0]));
  const [draggedIndex, setDraggedIndex] = useState<number | null>(null);
  const [uploadingAudio, setUploadingAudio] = useState<Record<string, boolean>>({});
  const [uploadProgress, setUploadProgress] = useState<Record<string, number>>({});
  const [uploadErrors, setUploadErrors] = useState<Record<string, string>>({});
  const [noiseProfiles, setNoiseProfiles] = useState<NoiseProfile[]>([]);
  const [noiseConfig, setNoiseConfig] = useState<Record<string, { profile: string; snr_db: number; randomize: boolean }>>({});
  const [applyingNoise, setApplyingNoise] = useState<Record<string, boolean>>({});
  const [previewLoading, setPreviewLoading] = useState<Record<string, boolean>>({});
  const [previewPlaying, setPreviewPlaying] = useState<Record<string, boolean>>({});
  const previewAudioRef = useRef<Record<string, HTMLAudioElement | null>>({});

  // Fetch noise profiles on mount
  useEffect(() => {
    const fetchNoiseProfiles = async () => {
      try {
        const response = await apiClient.get<{ success: boolean; data: NoiseProfile[] }>('/scenarios/noise-profiles');
        if (response.data.data) {
          setNoiseProfiles(response.data.data);
        }
      } catch (error) {
        console.error('Failed to fetch noise profiles:', error);
      }
    };
    fetchNoiseProfiles();
  }, []);

  // Helper function to ensure step has language_variants
  const ensureLanguageVariants = (step: ScenarioStepData): ScenarioStepData => {
    if (!step.step_metadata?.language_variants || step.step_metadata.language_variants.length === 0) {
      const primaryLanguage = step.step_metadata?.primary_language || 'en-US';
      return {
        ...step,
        step_metadata: {
          ...step.step_metadata,
          primary_language: primaryLanguage,
          language_variants: [{ language_code: primaryLanguage, user_utterance: step.user_utterance || '' }],
        },
      };
    }
    return step;
  };

  const addStep = () => {
    const newStep: ScenarioStepData = {
      step_order: steps.length + 1,
      user_utterance: '',
      step_metadata: {
        primary_language: 'en-US',
        language_variants: [{ language_code: 'en-US', user_utterance: '' }],
      },
      expected_outcomes: [],
    };
    onChange([...steps, newStep]);
    setExpandedSteps(new Set([...expandedSteps, steps.length]));
  };

  const removeStep = (index: number) => {
    const newSteps = steps.filter((_, i) => i !== index);
    const reorderedSteps = newSteps.map((step, i) => ({ ...step, step_order: i + 1 }));
    onChange(reorderedSteps);
    setExpandedSteps(new Set([...expandedSteps].filter((i) => i < newSteps.length)));
  };

  const updateStep = (index: number, updates: Partial<ScenarioStepData>) => {
    const newSteps = [...steps];
    newSteps[index] = { ...newSteps[index], ...updates };
    onChange(newSteps);
  };

  const toggleExpanded = (index: number) => {
    const newExpanded = new Set(expandedSteps);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedSteps(newExpanded);
  };

  // Drag and Drop handlers
  const handleDragStart = (index: number) => setDraggedIndex(index);

  const handleDragOver = (e: React.DragEvent, index: number) => {
    e.preventDefault();
    if (draggedIndex === null || draggedIndex === index) return;

    const newSteps = [...steps];
    const draggedStep = newSteps[draggedIndex];
    newSteps.splice(draggedIndex, 1);
    newSteps.splice(index, 0, draggedStep);

    const reorderedSteps = newSteps.map((step, i) => ({ ...step, step_order: i + 1 }));
    onChange(reorderedSteps);
    setDraggedIndex(index);
  };

  const handleDragEnd = () => setDraggedIndex(null);

  // Audio upload handlers
  const getUploadKey = (stepIndex: number, langCode: string) => `${stepIndex}-${langCode}`;

  const handleAudioUpload = async (stepIndex: number, langCode: string, file: File) => {
    const step = steps[stepIndex];
    const uploadKey = getUploadKey(stepIndex, langCode);

    if (!scenarioId || !step.id) {
      setUploadErrors({
        ...uploadErrors,
        [uploadKey]: 'Please save the scenario first before uploading audio',
      });
      return;
    }

    setUploadingAudio({ ...uploadingAudio, [uploadKey]: true });
    setUploadProgress({ ...uploadProgress, [uploadKey]: 0 });
    setUploadErrors({ ...uploadErrors, [uploadKey]: '' });

    // Simulate progress
    const progressInterval = setInterval(() => {
      setUploadProgress((prev) => {
        const current = prev[uploadKey] || 0;
        if (current >= 90) {
          clearInterval(progressInterval);
          return prev;
        }
        return { ...prev, [uploadKey]: current + 10 };
      });
    }, 200);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await apiClient.post<{ success: boolean; data: UploadedAudioInfo }>(
        `/scenarios/${scenarioId}/steps/${step.id}/audio?language_code=${langCode}`,
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );

      clearInterval(progressInterval);
      setUploadProgress({ ...uploadProgress, [uploadKey]: 100 });

      const audioInfo = response.data.data;
      const updatedMetadata = {
        ...step.step_metadata,
        audio_source: 'uploaded' as const,
        uploaded_audio: { ...step.step_metadata?.uploaded_audio, [langCode]: audioInfo },
      };

      updateStep(stepIndex, { step_metadata: updatedMetadata });
    } catch (error: any) {
      console.error('Audio upload failed:', error);
      clearInterval(progressInterval);
      setUploadErrors({
        ...uploadErrors,
        [uploadKey]: error.response?.data?.detail || 'Failed to upload audio',
      });
    } finally {
      setUploadingAudio({ ...uploadingAudio, [uploadKey]: false });
      setTimeout(() => setUploadProgress({ ...uploadProgress, [uploadKey]: 0 }), 500);
    }
  };

  const handleRemoveAudio = async (stepIndex: number, langCode: string) => {
    const step = steps[stepIndex];
    if (!scenarioId || !step.id) return;

    try {
      await apiClient.delete(`/scenarios/${scenarioId}/steps/${step.id}/audio/${langCode}`);

      const uploadedAudio = { ...step.step_metadata?.uploaded_audio };
      delete uploadedAudio[langCode];

      const updatedMetadata = {
        ...step.step_metadata,
        uploaded_audio: Object.keys(uploadedAudio).length > 0 ? uploadedAudio : undefined,
        audio_source: Object.keys(uploadedAudio).length > 0 ? 'uploaded' : 'tts',
      };

      updateStep(stepIndex, { step_metadata: updatedMetadata });
    } catch (error) {
      console.error('Failed to remove audio:', error);
    }
  };

  // Apply noise to existing audio
  const handleApplyNoise = async (stepIndex: number, langCode: string) => {
    const step = steps[stepIndex];
    if (!scenarioId || !step.id) return;

    const configKey = `${stepIndex}-${langCode}`;
    const config = noiseConfig[configKey];
    if (!config) return;

    setApplyingNoise({ ...applyingNoise, [configKey]: true });

    try {
      const response = await apiClient.post<{ success: boolean; data: UploadedAudioInfo }>(
        `/scenarios/${scenarioId}/steps/${step.id}/audio/${langCode}/apply-noise`,
        {
          enabled: true,
          profile: config.profile,
          snr_db: config.snr_db,
          randomize_snr: config.randomize,
          snr_variance: 3.0,
        }
      );

      const audioInfo = response.data.data;
      const updatedMetadata = {
        ...step.step_metadata,
        uploaded_audio: { ...step.step_metadata?.uploaded_audio, [langCode]: audioInfo },
      };

      updateStep(stepIndex, { step_metadata: updatedMetadata });
    } catch (error: any) {
      console.error('Failed to apply noise:', error);
      setUploadErrors({
        ...uploadErrors,
        [configKey]: error.response?.data?.detail || 'Failed to apply noise',
      });
    } finally {
      setApplyingNoise({ ...applyingNoise, [configKey]: false });
    }
  };

  // Preview noise on existing audio
  const handlePreviewNoise = async (stepIndex: number, langCode: string) => {
    const step = steps[stepIndex];
    if (!scenarioId || !step.id) return;

    const configKey = `${stepIndex}-${langCode}`;
    const config = noiseConfig[configKey];
    if (!config) return;

    // Stop any currently playing preview
    const existingAudio = previewAudioRef.current[configKey];
    if (existingAudio) {
      existingAudio.pause();
      existingAudio.src = '';
      setPreviewPlaying({ ...previewPlaying, [configKey]: false });
    }

    setPreviewLoading({ ...previewLoading, [configKey]: true });

    try {
      const response = await apiClient.post<{
        success: boolean;
        data: {
          audio_base64: string;
          content_type: string;
          format: string;
          snr_db: number;
          profile: string;
          profile_name: string;
        };
      }>(
        `/scenarios/${scenarioId}/steps/${step.id}/audio/${langCode}/preview-noise`,
        {
          enabled: true,
          profile: config.profile,
          snr_db: config.snr_db,
          randomize_snr: config.randomize,
          snr_variance: 3.0,
        }
      );

      const { audio_base64, content_type } = response.data.data;

      // Create audio element and play
      const audio = new Audio(`data:${content_type};base64,${audio_base64}`);
      previewAudioRef.current[configKey] = audio;

      audio.onended = () => {
        setPreviewPlaying({ ...previewPlaying, [configKey]: false });
      };

      audio.onerror = () => {
        console.error('Preview audio playback failed');
        setPreviewPlaying({ ...previewPlaying, [configKey]: false });
      };

      await audio.play();
      setPreviewPlaying({ ...previewPlaying, [configKey]: true });
    } catch (error: any) {
      console.error('Failed to preview noise:', error);
      setUploadErrors({
        ...uploadErrors,
        [configKey]: error.response?.data?.detail || 'Failed to preview noise',
      });
    } finally {
      setPreviewLoading({ ...previewLoading, [configKey]: false });
    }
  };

  // Stop preview playback
  const handleStopPreview = (stepIndex: number, langCode: string) => {
    const configKey = `${stepIndex}-${langCode}`;
    const audio = previewAudioRef.current[configKey];
    if (audio) {
      audio.pause();
      audio.currentTime = 0;
    }
    setPreviewPlaying({ ...previewPlaying, [configKey]: false });
  };

  // Noise Config Panel Component
  const NoiseConfigPanel: React.FC<{
    stepIndex: number;
    langCode: string;
    audioInfo: UploadedAudioInfo;
  }> = ({ stepIndex, langCode, audioInfo }) => {
    const configKey = `${stepIndex}-${langCode}`;
    const config = noiseConfig[configKey] || {
      profile: 'car_cabin_city',
      snr_db: 15,
      randomize: false,
    };
    const isApplying = applyingNoise[configKey];
    const isPreviewLoading = previewLoading[configKey];
    const isPreviewPlaying = previewPlaying[configKey];

    const updateConfig = (updates: Partial<typeof config>) => {
      setNoiseConfig({
        ...noiseConfig,
        [configKey]: { ...config, ...updates },
      });
    };

    // Group profiles by category
    const profilesByCategory = noiseProfiles.reduce((acc, profile) => {
      if (!acc[profile.category]) acc[profile.category] = [];
      acc[profile.category].push(profile);
      return acc;
    }, {} as Record<string, NoiseProfile[]>);

    // Already has noise applied
    if (audioInfo.noise_applied) {
      return null;
    }

    return (
      <div className="p-3 bg-[var(--color-surface-inset)]/50 rounded-lg border border-[var(--color-border-default)]">
        <div className="flex items-center gap-2 mb-3">
          <Waves size={14} className="text-amber-500" />
          <span className="text-xs font-medium text-[var(--color-content-muted)] uppercase tracking-wide">
            Add Noise
          </span>
        </div>

        <div className="space-y-3">
          {/* Profile Selector */}
          <div>
            <label className="text-xs text-[var(--color-content-muted)] mb-1 block">
              Noise Profile
            </label>
            <select
              value={config.profile}
              onChange={(e) => {
                const profile = noiseProfiles.find((p) => p.name === e.target.value);
                updateConfig({
                  profile: e.target.value,
                  snr_db: profile?.default_snr_db || 15,
                });
              }}
              className="w-full px-3 py-2 text-sm bg-[var(--color-surface-raised)] border border-[var(--color-border-default)] rounded-lg text-[var(--color-content-primary)]"
            >
              {Object.entries(profilesByCategory).map(([category, profiles]) => (
                <optgroup key={category} label={category.charAt(0).toUpperCase() + category.slice(1)}>
                  {profiles.map((profile) => (
                    <option key={profile.name} value={profile.name}>
                      {profile.description || profile.name} ({profile.difficulty})
                    </option>
                  ))}
                </optgroup>
              ))}
            </select>
          </div>

          {/* SNR Slider */}
          <div>
            <div className="flex items-center justify-between mb-1">
              <label className="text-xs text-[var(--color-content-muted)]">
                SNR (Signal-to-Noise Ratio)
              </label>
              <span className="text-xs font-mono text-[var(--color-content-secondary)]">
                {config.snr_db} dB
              </span>
            </div>
            <input
              type="range"
              min="-10"
              max="50"
              step="1"
              value={config.snr_db}
              onChange={(e) => updateConfig({ snr_db: parseInt(e.target.value) })}
              className="w-full h-2 bg-[var(--color-surface-inset)] rounded-lg appearance-none cursor-pointer accent-amber-500"
            />
            <div className="flex justify-between text-xs text-[var(--color-content-muted)] mt-1">
              <span>Noisy (-10 dB)</span>
              <span>Clean (50 dB)</span>
            </div>
          </div>

          {/* Randomize Toggle */}
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={config.randomize}
              onChange={(e) => updateConfig({ randomize: e.target.checked })}
              className="w-4 h-4 rounded border-[var(--color-border-default)] accent-amber-500"
            />
            <span className="text-xs text-[var(--color-content-secondary)] flex items-center gap-1">
              <Shuffle size={12} />
              Randomize SNR (±3 dB)
            </span>
          </label>

          {/* Preview and Apply Buttons */}
          <div className="flex gap-2">
            {/* Preview Button */}
            <button
              onClick={() => isPreviewPlaying ? handleStopPreview(stepIndex, langCode) : handlePreviewNoise(stepIndex, langCode)}
              disabled={isPreviewLoading || isApplying}
              className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-[var(--color-surface-raised)] border border-[var(--color-border-strong)] text-[var(--color-content-primary)] text-sm font-medium rounded-lg hover:bg-[var(--color-interactive-hover)] disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              {isPreviewLoading ? (
                <>
                  <Loader2 size={14} className="animate-spin" />
                  Loading...
                </>
              ) : isPreviewPlaying ? (
                <>
                  <Square size={14} />
                  Stop
                </>
              ) : (
                <>
                  <Eye size={14} />
                  Preview
                </>
              )}
            </button>

            {/* Apply Button */}
            <button
              onClick={() => handleApplyNoise(stepIndex, langCode)}
              disabled={isApplying || isPreviewLoading}
              className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-gradient-to-r from-amber-400 to-orange-500 text-white text-sm font-medium rounded-lg hover:from-amber-500 hover:to-orange-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              {isApplying ? (
                <>
                  <Loader2 size={14} className="animate-spin" />
                  Applying...
                </>
              ) : (
                <>
                  <Waves size={14} />
                  Apply
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    );
  };

  // Audio Upload Section Component
  const AudioUploadSection: React.FC<{ stepIndex: number; step: ScenarioStepData }> = ({ stepIndex, step }) => {
    const variants = step.step_metadata?.language_variants || [];
    const uploadedAudio = step.step_metadata?.uploaded_audio || {};

    if (variants.length === 0) return null;

    const canUpload = scenarioId && step.id;

    return (
      <div className="border border-[var(--color-border-default)] rounded-xl overflow-hidden bg-[var(--color-surface-inset)]">
        <div className="flex items-center gap-3 px-4 py-3 bg-[var(--color-surface-raised)] border-b border-[var(--color-border-default)]">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[var(--color-status-teal-bg)] to-[var(--color-status-teal-bg)] flex items-center justify-center border border-[var(--color-status-teal-bg)]">
            <Volume2 size={16} className="text-[var(--color-status-teal)]" />
          </div>
          <div>
            <span className="font-medium text-[var(--color-content-primary)] text-sm">Audio Source</span>
            <p className="text-xs text-[var(--color-content-muted)]">
              Upload audio files or use auto-generated TTS
            </p>
          </div>
          <InfoTooltip text="Upload custom audio recordings for each language variant. Audio will be transcribed using Whisper AI." />
        </div>

        <div className="p-4 space-y-4">
          {variants.map((variant) => {
            const langCode = variant.language_code;
            const uploadKey = getUploadKey(stepIndex, langCode);
            const isUploading = uploadingAudio[uploadKey];
            const progress = uploadProgress[uploadKey] || 0;
            const error = uploadErrors[uploadKey];
            const audioInfo = uploadedAudio[langCode];

            return (
              <div key={langCode} className="space-y-2">
                <div className="flex items-center gap-2">
                  <Globe size={14} className="text-[var(--color-status-info)]" />
                  <span className="text-sm font-medium text-[var(--color-content-secondary)]">
                    {langCode}
                  </span>
                  <span
                    className={`text-xs px-2 py-0.5 rounded-full ${
                      audioInfo
                        ? 'bg-gradient-to-r from-teal-400/10 to-cyan-500/10 text-[var(--color-status-teal)] border border-[var(--color-status-teal-bg)]'
                        : 'bg-[var(--color-surface-inset)] text-[var(--color-content-muted)]'
                    }`}
                  >
                    {audioInfo ? (
                      <span className="flex items-center gap-1">
                        <FileAudio size={10} />
                        Uploaded
                      </span>
                    ) : (
                      <span className="flex items-center gap-1">
                        <Mic size={10} />
                        TTS
                      </span>
                    )}
                  </span>
                </div>

                {audioInfo ? (
                  <>
                    <AudioPlayerCard
                      audioInfo={audioInfo}
                      onRemove={() => handleRemoveAudio(stepIndex, langCode)}
                    />
                    {/* Noise Config Panel - only show if no noise applied yet */}
                    {noiseProfiles.length > 0 && !audioInfo.noise_applied && (
                      <NoiseConfigPanel
                        stepIndex={stepIndex}
                        langCode={langCode}
                        audioInfo={audioInfo}
                      />
                    )}
                  </>
                ) : (
                  <AudioUploadZone
                    onUpload={(file) => handleAudioUpload(stepIndex, langCode, file)}
                    isUploading={isUploading}
                    uploadProgress={progress}
                    disabled={!canUpload}
                    disabledMessage="Save scenario first to enable audio upload"
                  />
                )}

                {error && (
                  <div className="flex items-center gap-2 text-sm text-[var(--color-status-danger)]">
                    <AlertCircle size={14} />
                    {error}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div className="flex items-center gap-2">
          <h3 className="text-lg font-semibold text-[var(--color-content-primary)]">Scenario Steps</h3>
          <span className="px-2 py-0.5 text-xs font-medium bg-[var(--color-surface-inset)] text-[var(--color-content-secondary)] rounded-full">
            {steps.length} {steps.length === 1 ? 'step' : 'steps'}
          </span>
        </div>
        <button
          type="button"
          onClick={addStep}
          className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-teal-400 to-teal-600 text-white rounded-lg hover:from-teal-600 hover:to-teal-700 shadow-lg shadow-teal-500/20 hover:shadow-teal-500/30 transition-all"
        >
          <Plus size={16} />
          Add Step
        </button>
      </div>

      {/* Empty State */}
      {steps.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-12 border-2 border-dashed border-[var(--color-border-strong)] rounded-xl bg-[var(--color-surface-inset)]/30">
          <div className="w-16 h-16 mb-4 rounded-full bg-[var(--color-surface-inset)] flex items-center justify-center">
            <AudioWaveform size={28} className="text-[var(--color-content-muted)]" />
          </div>
          <p className="text-[var(--color-content-muted)] mb-2">No steps added yet</p>
          <p className="text-sm text-[var(--color-content-muted)] mb-4">
            Add steps to define your scenario's conversation flow
          </p>
          <button
            type="button"
            onClick={addStep}
            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-teal-400 to-teal-600 text-white rounded-lg hover:from-teal-600 hover:to-teal-700 shadow-lg shadow-teal-500/20 transition-all"
          >
            <Plus size={16} />
            Add First Step
          </button>
        </div>
      ) : (
        <div className="space-y-3">
          {steps.map((step, index) => {
            const isExpanded = expandedSteps.has(index);
            const variants = step.step_metadata?.language_variants || [];
            const uploadedAudio = step.step_metadata?.uploaded_audio || {};
            const hasUploadedAudio = Object.keys(uploadedAudio).length > 0;

            return (
              <div
                key={step.id || index}
                draggable
                onDragStart={() => handleDragStart(index)}
                onDragOver={(e) => handleDragOver(e, index)}
                onDragEnd={handleDragEnd}
                className={`border rounded-xl bg-[var(--color-surface-raised)] shadow-sm hover:shadow-md transition-all ${
                  draggedIndex === index ? 'opacity-50 scale-[0.98]' : ''
                } ${
                  selectedStepIndex === index
                    ? 'ring-2 ring-[var(--color-status-teal)] border-[var(--color-status-teal)]'
                    : 'border-[var(--color-border-default)]'
                }`}
              >
                {/* Step Header */}
                <div
                  className="flex items-center gap-3 px-4 py-3 bg-[var(--color-surface-inset)]/50 border-b border-[var(--color-border-default)] cursor-pointer"
                  onClick={() => toggleExpanded(index)}
                >
                  <button
                    type="button"
                    className="cursor-move text-[var(--color-content-muted)] hover:text-[var(--color-content-secondary)]"
                    title="Drag to reorder"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <GripVertical size={18} />
                  </button>

                  <span className="w-8 h-8 flex items-center justify-center bg-gradient-to-br from-teal-400 to-teal-600 text-white rounded-lg text-sm font-bold shadow-sm flex-shrink-0">
                    {step.step_order}
                  </span>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-medium text-[var(--color-content-primary)]">
                        Step {step.step_order}
                      </span>
                      {step.step_metadata?.primary_language && (
                        <span className="text-xs px-2 py-0.5 bg-[var(--color-status-info-bg)] text-[var(--color-status-info)] rounded-full">
                          {step.step_metadata.primary_language}
                        </span>
                      )}
                      {variants.length > 1 && (
                        <span className="flex items-center gap-1 text-xs text-[var(--color-content-muted)]">
                          <Globe size={12} />
                          +{variants.length - 1} variant{variants.length > 2 ? 's' : ''}
                        </span>
                      )}
                      {hasUploadedAudio && (
                        <span className="flex items-center gap-1 text-xs px-2 py-0.5 bg-[var(--color-status-teal-bg)] text-[var(--color-status-teal)] rounded-full">
                          <FileAudio size={10} />
                          Audio
                        </span>
                      )}
                    </div>
                    {step.user_utterance && (
                      <p className="text-sm text-[var(--color-content-muted)] truncate mt-0.5">
                        "{step.user_utterance}"
                      </p>
                    )}
                  </div>

                  <div className="flex items-center gap-1">
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        removeStep(index);
                      }}
                      className="p-1.5 text-[var(--color-content-muted)] hover:text-[var(--color-status-danger)] hover:bg-[var(--color-status-danger-bg)] rounded-lg transition-colors"
                      title="Remove step"
                    >
                      <Trash2 size={16} />
                    </button>
                    {isExpanded ? (
                      <ChevronUp size={18} className="text-[var(--color-content-muted)]" />
                    ) : (
                      <ChevronDown size={18} className="text-[var(--color-content-muted)]" />
                    )}
                  </div>
                </div>

                {/* Expanded Content */}
                {isExpanded && (
                  <div className="p-4 space-y-5">
                    {/* Language Variants */}
                    <LanguageVariantManager
                      variants={ensureLanguageVariants(step).step_metadata?.language_variants || []}
                      primaryLanguage={ensureLanguageVariants(step).step_metadata?.primary_language || 'en-US'}
                      onChange={(variants, primaryLanguage) => {
                        const updatedMetadata = {
                          ...step.step_metadata,
                          language_variants: variants,
                          primary_language: primaryLanguage,
                        };

                        const primaryVariant = variants.find((v) => v.language_code === primaryLanguage);
                        const updates: Partial<ScenarioStepData> = {
                          step_metadata: updatedMetadata,
                        };

                        if (primaryVariant) {
                          updates.user_utterance = primaryVariant.user_utterance;
                        }

                        updateStep(index, updates);
                      }}
                    />

                    {/* Audio Upload Section */}
                    <AudioUploadSection stepIndex={index} step={step} />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default StepManager;
