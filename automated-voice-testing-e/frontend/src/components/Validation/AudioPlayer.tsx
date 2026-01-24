/**
 * Audio Player Component
 *
 * A comprehensive audio player component for validation workflow.
 * Provides play/pause, seek, volume, playback speed controls,
 * and waveform visualization using WaveSurfer.js.
 *
 * Features:
 * - Play/Pause controls
 * - Seek functionality with progress slider
 * - Volume control
 * - Playback speed adjustment (0.5x, 1x, 1.5x, 2x)
 * - Waveform visualization using WaveSurfer.js
 * - Current time and duration display
 *
 * @module components/Validation/AudioPlayer
 */

import React, { useState, useRef, useEffect } from 'react';
import { Play, Pause, Volume2, VolumeX, Loader2 } from 'lucide-react';
import WaveSurfer from 'wavesurfer.js';

/**
 * AudioPlayer component props interface
 */
interface AudioPlayerProps {
  /**
   * URL of the audio file to play
   */
  audioUrl: string;

  /**
   * Optional callback when playback state changes
   */
  onPlaybackChange?: (isPlaying: boolean) => void;

  /**
   * Optional callback when time updates
   */
  onTimeUpdate?: (currentTime: number, duration: number) => void;

  /**
   * Render compact version for tables (no waveform, minimal controls)
   */
  compact?: boolean;
}

/**
 * AudioPlayer Component
 *
 * Displays audio playback controls with waveform visualization.
 *
 * @param {AudioPlayerProps} props - Component props
 * @returns {React.FC} AudioPlayer component
 */
const AudioPlayer: React.FC<AudioPlayerProps> = ({
  audioUrl,
  onPlaybackChange,
  onTimeUpdate,
  compact = false,
}) => {
  // Audio element reference
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const audioRef = useRef<HTMLAudioElement>(null);

  // Waveform container reference
  const waveformRef = useRef<HTMLDivElement>(null);

  // WaveSurfer instance reference
  const wavesurferRef = useRef<WaveSurfer | null>(null);

  // Playback state
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [currentTime, setCurrentTime] = useState<number>(0);
  const [duration, setDuration] = useState<number>(0);
  const [volume, setVolume] = useState<number>(1);
  const [playbackRate, setPlaybackRate] = useState<number>(1);
  const [isMuted, setIsMuted] = useState<boolean>(false);

  /**
   * Initialize WaveSurfer for full mode or audio element for compact mode
   */
  useEffect(() => {
    if (compact) {
      // For compact mode, create a hidden WaveSurfer instance
      const container = document.createElement('div');
      container.style.display = 'none';
      document.body.appendChild(container);

      const wavesurfer = WaveSurfer.create({
        container,
        url: audioUrl,
      });

      wavesurferRef.current = wavesurfer;

      // Set up event listeners
      wavesurfer.on('ready', () => {
        setDuration(wavesurfer.getDuration());
        setIsLoading(false);
      });

      wavesurfer.on('loading', () => {
        setIsLoading(true);
      });

      wavesurfer.on('audioprocess', () => {
        setCurrentTime(wavesurfer.getCurrentTime());
        onTimeUpdate?.(wavesurfer.getCurrentTime(), wavesurfer.getDuration());
      });

      wavesurfer.on('finish', () => {
        setIsPlaying(false);
        onPlaybackChange?.(false);
      });

      wavesurfer.on('play', () => {
        setIsPlaying(true);
        onPlaybackChange?.(true);
      });

      wavesurfer.on('pause', () => {
        setIsPlaying(false);
        onPlaybackChange?.(false);
      });

      return () => {
        wavesurfer.destroy();
        document.body.removeChild(container);
      };
    } else {
      // For full mode, create WaveSurfer with waveform visualization
      if (!waveformRef.current) return;

      const wavesurfer = WaveSurfer.create({
        container: waveformRef.current,
        waveColor: '#9DD4D6',
        progressColor: '#2A6B6E',
        cursorColor: '#11484D',
        barWidth: 2,
        barRadius: 3,
        cursorWidth: 1,
        height: 80,
        barGap: 2,
        normalize: true,
        url: audioUrl,
      });

      wavesurferRef.current = wavesurfer;

      // Set up WaveSurfer event listeners
      wavesurfer.on('ready', () => {
        setDuration(wavesurfer.getDuration());
        setIsLoading(false);
      });

      wavesurfer.on('loading', () => {
        setIsLoading(true);
      });

      wavesurfer.on('audioprocess', () => {
        setCurrentTime(wavesurfer.getCurrentTime());
        onTimeUpdate?.(wavesurfer.getCurrentTime(), wavesurfer.getDuration());
      });

      wavesurfer.on('seeking', () => {
        setCurrentTime(wavesurfer.getCurrentTime());
      });

      wavesurfer.on('finish', () => {
        setIsPlaying(false);
        onPlaybackChange?.(false);
      });

      wavesurfer.on('play', () => {
        setIsPlaying(true);
        onPlaybackChange?.(true);
      });

      wavesurfer.on('pause', () => {
        setIsPlaying(false);
        onPlaybackChange?.(false);
      });

      // Cleanup
      return () => {
        wavesurfer.destroy();
      };
    }
  }, [audioUrl, compact, onPlaybackChange, onTimeUpdate]);

  /**
   * Toggle play/pause
   */
  const handlePlayPause = () => {
    const wavesurfer = wavesurferRef.current;
    if (!wavesurfer) return;

    wavesurfer.playPause();
  };

  /**
   * Handle seek slider change
   */
  const handleSeek = (event: React.ChangeEvent<HTMLInputElement>) => {
    const wavesurfer = wavesurferRef.current;
    if (!wavesurfer) return;

    const newTime = parseFloat(event.target.value);
    wavesurfer.setTime(newTime);
    setCurrentTime(newTime);
  };

  /**
   * Handle volume slider change
   */
  const handleVolumeChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const wavesurfer = wavesurferRef.current;
    if (!wavesurfer) return;

    const newVolume = parseFloat(event.target.value);
    wavesurfer.setVolume(newVolume);
    setVolume(newVolume);
    setIsMuted(newVolume === 0);
  };

  /**
   * Toggle mute
   */
  const handleToggleMute = () => {
    const wavesurfer = wavesurferRef.current;
    if (!wavesurfer) return;

    if (isMuted) {
      const newVolume = volume > 0 ? volume : 0.5;
      wavesurfer.setVolume(newVolume);
      setVolume(newVolume);
      setIsMuted(false);
    } else {
      wavesurfer.setVolume(0);
      setIsMuted(true);
    }
  };

  /**
   * Handle playback speed change
   */
  const handleSpeedChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const wavesurfer = wavesurferRef.current;
    if (!wavesurfer) return;

    const newRate = Number(event.target.value);
    wavesurfer.setPlaybackRate(newRate);
    setPlaybackRate(newRate);
  };

  /**
   * Format time in MM:SS format
   */
  const formatTime = (time: number): string => {
    if (!isFinite(time)) return '0:00';
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  // Render compact version for tables
  if (compact) {
    return (
      <div className="flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
        {/* Play/Pause button */}
        <button
          onClick={(e) => { e.stopPropagation(); handlePlayPause(); }}
          className="p-1 rounded hover:bg-[var(--color-interactive-hover)] disabled:opacity-50 disabled:cursor-not-allowed text-[var(--color-brand-primary)] flex-shrink-0"
          aria-label={isPlaying ? 'Pause' : 'Play'}
          disabled={isLoading}
        >
          {isLoading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : isPlaying ? (
            <Pause className="w-4 h-4" />
          ) : (
            <Play className="w-4 h-4" />
          )}
        </button>

        {/* Time display */}
        <span className="text-xs text-[var(--color-content-secondary)] whitespace-nowrap">
          {formatTime(currentTime)} / {formatTime(duration)}
        </span>
      </div>
    );
  }

  return (
    <div className="w-full p-4" onClick={(e) => e.stopPropagation()}>
      {/* Waveform visualization */}
      <div className="w-full mb-4 relative">
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-[var(--color-surface-inset)] rounded">
            <Loader2 className="w-6 h-6 animate-spin text-[var(--color-brand-primary)]" />
          </div>
        )}
        <div ref={waveformRef} className="w-full" />
      </div>

      {/* Main controls */}
      <div className="space-y-4">
        {/* Play/Pause and Seek controls */}
        <div className="flex items-center gap-2">
          {/* Play/Pause button */}
          <button
            onClick={(e) => { e.stopPropagation(); handlePlayPause(); }}
            className="p-2 rounded-full hover:bg-[var(--color-interactive-hover)] disabled:opacity-50 disabled:cursor-not-allowed text-[var(--color-brand-primary)]"
            aria-label={isPlaying ? 'Pause' : 'Play'}
            disabled={isLoading}
          >
            {isLoading ? (
              <Loader2 className="w-6 h-6 animate-spin" />
            ) : isPlaying ? (
              <Pause className="w-6 h-6" />
            ) : (
              <Play className="w-6 h-6" />
            )}
          </button>

          {/* Current time */}
          <span className="text-sm min-w-[45px]">
            {formatTime(currentTime)}
          </span>

          {/* Seek slider */}
          <input
            type="range"
            value={currentTime}
            max={duration || 100}
            onChange={handleSeek}
            onClick={(e) => e.stopPropagation()}
            aria-label="Seek"
            className="flex-1 h-2 bg-[var(--color-interactive-hover)] rounded-lg appearance-none cursor-pointer"
          />

          {/* Duration */}
          <span className="text-sm min-w-[45px]">
            {formatTime(duration)}
          </span>
        </div>

        {/* Volume and Speed controls */}
        <div className="flex items-center gap-4">
          {/* Volume controls */}
          <div className="flex items-center gap-2 flex-1">
            <button
              onClick={(e) => { e.stopPropagation(); handleToggleMute(); }}
              className="p-1 rounded hover:bg-[var(--color-interactive-hover)]"
              aria-label={isMuted ? 'Unmute' : 'Mute'}
            >
              {isMuted || volume === 0 ? (
                <VolumeX className="w-5 h-5" />
              ) : (
                <Volume2 className="w-5 h-5" />
              )}
            </button>

            <input
              type="range"
              value={isMuted ? 0 : volume}
              max={1}
              step={0.1}
              onChange={handleVolumeChange}
              onClick={(e) => e.stopPropagation()}
              aria-label="Volume"
              className="max-w-[120px] h-2 bg-[var(--color-interactive-hover)] rounded-lg appearance-none cursor-pointer"
            />
          </div>

          {/* Playback speed control */}
          <div className="min-w-[100px]">
            <select
              value={playbackRate}
              onChange={handleSpeedChange}
              onClick={(e) => e.stopPropagation()}
              className="filter-select w-full"
              aria-label="Playback speed"
            >
              <option value={0.5}>0.5x</option>
              <option value={1}>1x</option>
              <option value={1.5}>1.5x</option>
              <option value={2}>2x</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AudioPlayer;
