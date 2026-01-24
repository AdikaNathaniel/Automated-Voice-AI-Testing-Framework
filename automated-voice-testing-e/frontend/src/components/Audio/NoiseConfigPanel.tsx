/**
 * NoiseConfigPanel Component
 *
 * A reusable component for configuring noise injection settings.
 * Features:
 * - Enable/disable toggle with visual feedback
 * - Category-based profile selection (Vehicle, Environmental, Industrial)
 * - Visual profile cards with difficulty badges
 * - SNR gauge with threshold markers
 * - SNR slider and custom input
 * - Randomize SNR option with variance control
 */

import React, { useState, useEffect } from 'react';
import {
  Volume2,
  ChevronDown,
  Car,
  Building2,
  Factory,
  Wind,
  Users,
  Plane,
  Train,
  Waves,
  Thermometer,
  AudioWaveform,
  Shuffle,
  Info,
  AlertCircle,
} from 'lucide-react';
import { multiTurnService } from '../../services/multiTurn.service';
import type { NoiseProfile, NoiseConfig } from '../../types/multiTurn';

export interface NoiseConfigPanelProps {
  /** Current noise configuration */
  config: NoiseConfig;
  /** Callback when configuration changes */
  onChange: (config: NoiseConfig) => void;
  /** Whether the panel is disabled */
  disabled?: boolean;
  /** Whether to start expanded */
  defaultExpanded?: boolean;
  /** Optional custom title */
  title?: string;
  /** Optional custom description */
  description?: string;
}

// Difficulty badge component with gradient styling
const DifficultyBadge: React.FC<{ difficulty: string; size?: 'sm' | 'md' }> = ({
  difficulty,
  size = 'md',
}) => {
  const config: Record<string, { bg: string; text: string; border: string }> = {
    easy: {
      bg: 'bg-gradient-to-r from-emerald-500/10 to-green-500/10',
      text: 'text-[var(--color-status-emerald)]',
      border: 'border-[var(--color-status-emerald-bg)]',
    },
    medium: {
      bg: 'bg-gradient-to-r from-amber-500/10 to-yellow-500/10',
      text: 'text-[var(--color-status-amber)]',
      border: 'border-[var(--color-status-amber-bg)]',
    },
    hard: {
      bg: 'bg-gradient-to-r from-orange-500/10 to-red-500/10',
      text: 'text-[var(--color-status-amber)]',
      border: 'border-[var(--color-status-amber-bg)]',
    },
    very_hard: {
      bg: 'bg-gradient-to-r from-red-500/10 to-rose-500/10',
      text: 'text-[var(--color-status-danger)]',
      border: 'border-[var(--color-status-danger-bg)]',
    },
    extreme: {
      bg: 'bg-gradient-to-r from-purple-500/10 to-fuchsia-500/10',
      text: 'text-[var(--color-status-purple)]',
      border: 'border-[var(--color-status-purple-bg)]',
    },
  };
  const c = config[difficulty] || config.medium;
  const sizeClasses = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-sm';

  return (
    <span
      className={`inline-flex items-center rounded-full font-medium border ${c.bg} ${c.text} ${c.border} ${sizeClasses} capitalize`}
    >
      {difficulty.replace('_', ' ')}
    </span>
  );
};

// Get icon for noise profile category
const getCategoryIcon = (category: string, profileName: string) => {
  // Check specific profile names first
  if (profileName.includes('hvac') || profileName.includes('ac')) return Thermometer;
  if (profileName.includes('wind')) return Wind;
  if (profileName.includes('train') || profileName.includes('subway')) return Train;
  if (profileName.includes('airport') || profileName.includes('airplane')) return Plane;
  if (profileName.includes('crowd') || profileName.includes('restaurant') || profileName.includes('cafe'))
    return Users;
  if (profileName.includes('highway') || profileName.includes('car') || profileName.includes('idle'))
    return Car;
  if (profileName.includes('office') || profileName.includes('quiet')) return Building2;
  if (profileName.includes('factory') || profileName.includes('construction')) return Factory;
  if (profileName.includes('rain') || profileName.includes('water')) return Waves;

  // Fallback to category
  switch (category) {
    case 'vehicle':
      return Car;
    case 'environmental':
      return Building2;
    case 'industrial':
      return Factory;
    default:
      return AudioWaveform;
  }
};

// SNR Gauge Component
const SNRGauge: React.FC<{ snr: number; min?: number; max?: number }> = ({
  snr,
  min = -10,
  max = 50,
}) => {
  const percentage = ((snr - min) / (max - min)) * 100;

  const getGradient = () => {
    if (snr >= 30) return 'from-emerald-500 to-green-400';
    if (snr >= 15) return 'from-teal-400 to-cyan-400';
    if (snr >= 5) return 'from-amber-500 to-yellow-400';
    if (snr >= 0) return 'from-orange-500 to-amber-400';
    return 'from-red-500 to-orange-400';
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-sm">
        <span className="text-[var(--color-content-muted)]">Signal-to-Noise Ratio</span>
        <span className="font-mono font-bold text-[var(--color-content-primary)]">{snr.toFixed(1)} dB</span>
      </div>
      <div className="relative h-3 bg-[var(--color-surface-inset)] rounded-full overflow-hidden">
        {/* Threshold markers */}
        <div
          className="absolute top-0 bottom-0 w-px bg-[var(--color-border-strong)] z-10"
          style={{ left: '25%' }}
          title="Hard threshold (5 dB)"
        />
        <div
          className="absolute top-0 bottom-0 w-px bg-[var(--color-border-strong)] z-10"
          style={{ left: '50%' }}
          title="Medium threshold (15 dB)"
        />
        <div
          className="absolute top-0 bottom-0 w-px bg-[var(--color-border-strong)] z-10"
          style={{ left: '75%' }}
          title="Easy threshold (30 dB)"
        />
        {/* Progress bar */}
        <div
          className={`h-full rounded-full bg-gradient-to-r ${getGradient()} transition-all duration-300`}
          style={{ width: `${Math.max(0, Math.min(100, percentage))}%` }}
        />
      </div>
      <div className="flex justify-between text-xs text-[var(--color-content-muted)]">
        <span>Noisy</span>
        <span>Clean</span>
      </div>
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
        <div className="absolute left-1/2 bottom-full mb-2 px-3 py-2 bg-[var(--color-surface-overlay)] text-white text-xs rounded-lg shadow-xl border border-[var(--color-border-strong)] pointer-events-none z-50 w-64 -translate-x-1/2">
          {text}
          <div className="absolute left-1/2 top-full -translate-x-1/2 border-4 border-transparent border-t-[var(--color-surface-overlay)]" />
        </div>
      )}
    </div>
  );
};

// Category labels and icons
const categoryLabels: Record<string, { label: string; icon: React.ReactNode }> = {
  vehicle: { label: 'Vehicle', icon: <Car size={16} /> },
  environmental: { label: 'Environmental', icon: <Building2 size={16} /> },
  industrial: { label: 'Industrial', icon: <Factory size={16} /> },
};

export const NoiseConfigPanel: React.FC<NoiseConfigPanelProps> = ({
  config,
  onChange,
  disabled = false,
  defaultExpanded = false,
  title = 'Audio Environment Simulation',
  description = 'Test voice AI robustness with realistic background noise',
}) => {
  const [expanded, setExpanded] = useState(defaultExpanded || config.enabled);
  const [noiseProfiles, setNoiseProfiles] = useState<NoiseProfile[]>([]);
  const [loadingProfiles, setLoadingProfiles] = useState(true);
  const [profilesError, setProfilesError] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('vehicle');

  // Fetch noise profiles on mount
  useEffect(() => {
    const fetchNoiseProfiles = async () => {
      try {
        setLoadingProfiles(true);
        setProfilesError(null);
        const profiles = await multiTurnService.getNoiseProfiles();
        setNoiseProfiles(profiles);
      } catch (error) {
        console.error('Failed to fetch noise profiles:', error);
        setProfilesError('Failed to load noise profiles. Please try again.');
        setNoiseProfiles([]);
      } finally {
        setLoadingProfiles(false);
      }
    };

    fetchNoiseProfiles();
  }, []);

  // Update config helper
  const updateConfig = (updates: Partial<NoiseConfig>) => {
    onChange({
      ...config,
      ...updates,
    });
  };

  // Get selected noise profile info
  const selectedNoiseProfile = noiseProfiles.find((p) => p.name === config.profile);

  // Get effective SNR for display
  const effectiveSnr = config.snr_db ?? selectedNoiseProfile?.default_snr_db ?? 15;

  // Group profiles by category
  const profilesByCategory = noiseProfiles.reduce(
    (acc, profile) => {
      if (!acc[profile.category]) {
        acc[profile.category] = [];
      }
      acc[profile.category].push(profile);
      return acc;
    },
    {} as Record<string, NoiseProfile[]>
  );

  return (
    <div className="border border-[var(--color-border-default)] rounded-xl overflow-hidden bg-[var(--color-surface-inset)]">
      <button
        type="button"
        onClick={() => setExpanded(!expanded)}
        disabled={disabled}
        className="w-full flex items-center justify-between p-4 text-left hover:bg-[var(--color-interactive-hover)] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[var(--color-status-teal-bg)] to-[var(--color-status-teal-bg)] flex items-center justify-center border border-[var(--color-status-teal-bg)]">
            <Volume2 className="w-5 h-5 text-[var(--color-status-teal)]" />
          </div>
          <div>
            <span className="font-semibold text-[var(--color-content-primary)]">{title}</span>
            <p className="text-xs text-[var(--color-content-muted)] mt-0.5">{description}</p>
          </div>
          {config.enabled && (
            <span className="px-2.5 py-1 text-xs font-medium bg-gradient-to-r from-[var(--color-status-teal-bg)] to-[var(--color-status-teal-bg)] text-[var(--color-status-teal)] rounded-full border border-[var(--color-status-teal-bg)]">
              Active
            </span>
          )}
        </div>
        <ChevronDown
          className={`w-5 h-5 text-[var(--color-content-muted)] transition-transform duration-200 ${
            expanded ? 'rotate-180' : ''
          }`}
        />
      </button>

      {expanded && (
        <div className="px-4 pb-5 space-y-5 border-t border-[var(--color-border-default)] pt-4">
          {/* Enable Toggle with Enhanced Design */}
          <div className="flex items-center justify-between p-4 bg-[var(--color-surface-raised)] rounded-xl border border-[var(--color-border-default)]">
            <div className="flex items-center gap-3">
              <div
                className={`w-12 h-6 rounded-full relative cursor-pointer transition-colors ${
                  config.enabled
                    ? 'bg-gradient-to-r from-teal-400 to-cyan-500'
                    : 'bg-[var(--color-border-default)]'
                } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
                onClick={() => !disabled && updateConfig({ enabled: !config.enabled })}
              >
                <div
                  className={`absolute top-0.5 w-5 h-5 bg-[var(--color-surface-overlay)] rounded-full shadow-lg transition-all duration-200 ${
                    config.enabled ? 'left-6' : 'left-0.5'
                  }`}
                />
              </div>
              <div>
                <span className="text-sm font-medium text-[var(--color-content-primary)]">
                  Enable Noise Injection
                </span>
                <p className="text-xs text-[var(--color-content-muted)]">
                  Add background noise to test audio inputs
                </p>
              </div>
            </div>
            <InfoTooltip text="Noise injection helps test how well your voice AI handles real-world audio conditions like car noise, crowds, or office environments." />
          </div>

          {config.enabled && (
            <>
              {/* Error state for profile loading */}
              {profilesError && (
                <div className="flex items-center gap-2 p-3 bg-[var(--color-status-danger-bg)] border border-[var(--color-status-danger)] rounded-lg">
                  <AlertCircle className="w-4 h-4 text-[var(--color-status-danger)]" />
                  <span className="text-sm text-[var(--color-status-danger)]">{profilesError}</span>
                </div>
              )}

              {/* Category Tabs */}
              <div className="flex items-center gap-1 p-1 bg-[var(--color-surface-inset)] rounded-xl">
                {Object.entries(categoryLabels).map(([key, { label, icon }]) => (
                  <button
                    key={key}
                    type="button"
                    onClick={() => setSelectedCategory(key)}
                    disabled={disabled}
                    className={`flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all disabled:opacity-50 ${
                      selectedCategory === key
                        ? 'bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] shadow-sm'
                        : 'text-[var(--color-content-muted)] hover:text-[var(--color-content-primary)]'
                    }`}
                  >
                    {icon}
                    {label}
                  </button>
                ))}
              </div>

              {/* Profile Cards Grid */}
              <div className="grid grid-cols-2 gap-3">
                {loadingProfiles ? (
                  <div className="col-span-2 flex items-center justify-center py-8">
                    <div className="w-6 h-6 border-2 border-[var(--color-status-teal)] border-t-transparent rounded-full animate-spin" />
                  </div>
                ) : (
                  profilesByCategory[selectedCategory]?.map((profile) => {
                    const IconComponent = getCategoryIcon(profile.category, profile.name);
                    const isSelected = config.profile === profile.name;

                    return (
                      <button
                        key={profile.name}
                        type="button"
                        onClick={() => updateConfig({ profile: profile.name, snr_db: undefined })}
                        disabled={disabled}
                        className={`group p-4 rounded-xl border-2 text-left transition-all disabled:opacity-50 ${
                          isSelected
                            ? 'border-[var(--color-status-teal)] bg-gradient-to-br from-[var(--color-status-teal-bg)] to-[var(--color-status-teal-bg)] shadow-lg shadow-teal-500/10'
                            : 'border-[var(--color-border-default)] bg-[var(--color-surface-raised)] hover:border-[var(--color-status-teal-bg)] hover:shadow-md'
                        }`}
                      >
                        <div className="flex items-start justify-between mb-3">
                          <div
                            className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                              isSelected
                                ? 'bg-gradient-to-br from-teal-400 to-cyan-500 text-white'
                                : 'bg-[var(--color-surface-inset)] text-[var(--color-content-muted)] group-hover:bg-[var(--color-status-teal-bg)] group-hover:text-[var(--color-status-teal)]'
                            }`}
                          >
                            <IconComponent size={20} />
                          </div>
                          <DifficultyBadge difficulty={profile.difficulty} size="sm" />
                        </div>

                        <h4
                          className={`font-medium mb-1 ${
                            isSelected
                              ? 'text-[var(--color-status-teal)]'
                              : 'text-[var(--color-content-primary)]'
                          }`}
                        >
                          {profile.name
                            .replace(/_/g, ' ')
                            .replace(/\b\w/g, (c) => c.toUpperCase())}
                        </h4>

                        {profile.description && (
                          <p className="text-xs text-[var(--color-content-muted)] mb-3 line-clamp-2">
                            {profile.description}
                          </p>
                        )}

                        <div className="flex items-center justify-between text-xs">
                          <span className="text-[var(--color-content-muted)]">
                            Default: {profile.default_snr_db} dB
                          </span>
                          {profile.estimated_wer_increase && (
                            <span className="text-[var(--color-status-amber)] font-medium">
                              +{profile.estimated_wer_increase}% WER
                            </span>
                          )}
                        </div>
                      </button>
                    );
                  })
                )}
              </div>

              {/* SNR Configuration */}
              {selectedNoiseProfile && (
                <div className="p-4 bg-[var(--color-surface-raised)] rounded-xl border border-[var(--color-border-default)] space-y-4">
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium text-[var(--color-content-primary)]">SNR Configuration</h4>
                    <InfoTooltip text="Signal-to-Noise Ratio (SNR) controls how much noise is added. Lower values = more noise = harder test conditions." />
                  </div>

                  <SNRGauge snr={effectiveSnr} />

                  {/* SNR Slider */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-[var(--color-content-muted)]">Custom SNR Override</span>
                      <div className="flex items-center gap-2">
                        <input
                          type="number"
                          value={config.snr_db ?? ''}
                          onChange={(e) =>
                            updateConfig({
                              snr_db: e.target.value ? parseFloat(e.target.value) : undefined,
                            })
                          }
                          placeholder={`${selectedNoiseProfile?.default_snr_db ?? 15}`}
                          className="w-20 px-2 py-1.5 border border-[var(--color-border-strong)] rounded-lg bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] text-sm text-center focus:outline-none focus:ring-2 focus:ring-[var(--color-border-focus)] focus:border-transparent"
                          disabled={disabled}
                        />
                        <span className="text-[var(--color-content-muted)]">dB</span>
                      </div>
                    </div>

                    <input
                      type="range"
                      min="-10"
                      max="50"
                      step="1"
                      value={effectiveSnr}
                      onChange={(e) => updateConfig({ snr_db: parseFloat(e.target.value) })}
                      className="w-full h-2 bg-[var(--color-surface-inset)] rounded-full appearance-none cursor-pointer accent-teal-500"
                      style={{
                        background: `linear-gradient(to right, rgb(20 184 166) 0%, rgb(20 184 166) ${
                          ((effectiveSnr + 10) / 60) * 100
                        }%, rgb(229 231 235) ${((effectiveSnr + 10) / 60) * 100}%, rgb(229 231 235) 100%)`,
                      }}
                      disabled={disabled}
                    />

                    <p className="text-xs text-[var(--color-content-muted)]">
                      Leave empty to use profile default ({selectedNoiseProfile?.default_snr_db} dB)
                    </p>
                  </div>

                  {/* Randomize SNR Toggle */}
                  <div className="flex items-center justify-between pt-3 border-t border-[var(--color-border-subtle)]">
                    <div className="flex items-center gap-3">
                      <div
                        className={`w-10 h-5 rounded-full relative cursor-pointer transition-colors ${
                          config.randomize_snr
                            ? 'bg-gradient-to-r from-purple-500 to-indigo-500'
                            : 'bg-[var(--color-border-default)]'
                        } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
                        onClick={() => !disabled && updateConfig({ randomize_snr: !config.randomize_snr })}
                      >
                        <div
                          className={`absolute top-0.5 w-4 h-4 bg-[var(--color-surface-overlay)] rounded-full shadow transition-all duration-200 ${
                            config.randomize_snr ? 'left-5' : 'left-0.5'
                          }`}
                        />
                      </div>
                      <div className="flex items-center gap-2">
                        <Shuffle size={16} className="text-[var(--color-status-purple)]" />
                        <span className="text-sm font-medium text-[var(--color-content-primary)]">
                          Randomize SNR
                        </span>
                      </div>
                    </div>

                    {config.randomize_snr && (
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-[var(--color-content-muted)]">±</span>
                        <input
                          type="number"
                          min="0"
                          max="10"
                          step="0.5"
                          value={config.snr_variance || 3}
                          onChange={(e) => updateConfig({ snr_variance: parseFloat(e.target.value) })}
                          className="w-14 px-2 py-1 border border-[var(--color-border-strong)] rounded-lg bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] text-sm text-center"
                          disabled={disabled}
                        />
                        <span className="text-xs text-[var(--color-content-muted)]">dB</span>
                      </div>
                    )}
                  </div>

                  {config.randomize_snr && (
                    <p className="text-xs text-[var(--color-status-purple)] bg-[var(--color-status-purple-bg)] px-3 py-2 rounded-lg">
                      SNR will vary between {effectiveSnr - (config.snr_variance || 3)} and{' '}
                      {effectiveSnr + (config.snr_variance || 3)} dB for each execution
                    </p>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default NoiseConfigPanel;
