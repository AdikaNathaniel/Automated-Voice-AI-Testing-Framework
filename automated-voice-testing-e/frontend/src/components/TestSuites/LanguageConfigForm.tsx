/**
 * Language Configuration Form Component
 *
 * Provides UI for configuring suite-level language execution settings:
 * - Mode selection (Primary, Specific, All)
 * - Language selection with flags
 * - Fallback behavior configuration
 * - Real-time execution preview
 */

import React, { useState, useEffect } from 'react';
import {
  Globe,
  Zap,
  Target,
  CheckCircle,
  AlertTriangle,
  XCircle,
  Info,
  ChevronRight
} from 'lucide-react';
import type { LanguageConfig } from '../../services/testSuite.service';

interface LanguageConfigFormProps {
  value: LanguageConfig | null;
  onChange: (config: LanguageConfig | null) => void;
  scenarioCount?: number;
  scenarioLanguages?: { [scenarioId: string]: string[] };
}

interface LanguageOption {
  code: string;
  flag: string;
  name: string;
}

const AVAILABLE_LANGUAGES: LanguageOption[] = [
  { code: 'en-US', flag: '🇺🇸', name: 'English (United States)' },
  { code: 'es-ES', flag: '🇪🇸', name: 'Spanish (Spain)' },
  { code: 'fr-FR', flag: '🇫🇷', name: 'French (France)' },
];

const LanguageConfigForm: React.FC<LanguageConfigFormProps> = ({
  value,
  onChange,
  scenarioCount = 0,
  scenarioLanguages = {},
}) => {
  const [mode, setMode] = useState<'primary' | 'specific' | 'all'>(value?.mode || 'primary');
  const [selectedLanguages, setSelectedLanguages] = useState<string[]>(value?.languages || []);
  const [fallbackBehavior, setFallbackBehavior] = useState<'smart' | 'skip' | 'fail'>(
    value?.fallback_behavior || 'smart'
  );

  // Update parent when local state changes
  useEffect(() => {
    const config: LanguageConfig = {
      mode,
      languages: mode === 'specific' ? selectedLanguages : undefined,
      fallback_behavior: fallbackBehavior,
    };
    onChange(config);
  }, [mode, selectedLanguages, fallbackBehavior, onChange]);

  const handleLanguageToggle = (langCode: string) => {
    setSelectedLanguages((prev) =>
      prev.includes(langCode)
        ? prev.filter((l) => l !== langCode)
        : [...prev, langCode]
    );
  };

  const getModeIcon = (modeType: string) => {
    switch (modeType) {
      case 'primary':
        return <Zap className="w-5 h-5" />;
      case 'specific':
        return <Target className="w-5 h-5" />;
      case 'all':
        return <Globe className="w-5 h-5" />;
      default:
        return null;
    }
  };

  const getFallbackIcon = (behavior: string) => {
    switch (behavior) {
      case 'smart':
        return <CheckCircle className="w-4 h-4" />;
      case 'skip':
        return <AlertTriangle className="w-4 h-4" />;
      case 'fail':
        return <XCircle className="w-4 h-4" />;
      default:
        return null;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header with description */}
      <div className="bg-gradient-to-r from-[var(--color-status-info-bg)] to-[var(--color-status-indigo-bg)] p-4 rounded-lg border border-[var(--color-status-info-bg)]">
        <div className="flex items-start gap-3">
          <Info className="w-5 h-5 text-[var(--color-status-info)] mt-0.5 flex-shrink-0" />
          <div>
            <h4 className="text-sm font-semibold text-[var(--color-status-info)] mb-1">
              Language Execution Configuration
            </h4>
            <p className="text-xs text-[var(--color-status-info)]">
              Control which languages are executed when running this suite. Configure fallback behavior
              for scenarios that don't support all requested languages.
            </p>
          </div>
        </div>
      </div>

      {/* Mode Selection */}
      <div>
        <label className="block text-sm font-semibold text-[var(--color-content-secondary)] mb-3">
          Execution Mode
        </label>
        <div className="grid grid-cols-1 gap-3">
          {/* Primary Mode */}
          <button
            type="button"
            onClick={() => setMode('primary')}
            className={`relative p-4 rounded-lg border-2 transition-all text-left ${
              mode === 'primary'
                ? 'border-[#2A6B6E] bg-gradient-to-r from-[#2A6B6E]/10 to-[#11484D]/10 shadow-md'
                : 'border-[var(--color-border-default)] hover:border-[#2A6B6E]/50 bg-[var(--color-surface-raised)]'
            }`}
          >
            <div className="flex items-start gap-3">
              <div
                className={`p-2 rounded-lg ${
                  mode === 'primary'
                    ? 'bg-gradient-to-r from-[#2A6B6E] to-[#11484D] text-white'
                    : 'bg-[var(--color-surface-inset)] text-[var(--color-content-secondary)]'
                }`}
              >
                {getModeIcon('primary')}
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <h4 className="text-sm font-semibold text-[var(--color-content-primary)]">
                    Primary Language Only
                  </h4>
                  <span className="px-2 py-0.5 text-xs font-medium bg-[var(--color-status-success-bg)] text-[var(--color-status-success)] rounded-full">
                    Fastest
                  </span>
                </div>
                <p className="text-xs text-[var(--color-content-secondary)]">
                  Execute scenarios in their primary language only (typically en-US). Best for quick
                  regression testing and CI/CD pipelines.
                </p>
              </div>
              {mode === 'primary' && (
                <CheckCircle className="w-5 h-5 text-[#2A6B6E] flex-shrink-0" />
              )}
            </div>
          </button>

          {/* Specific Languages Mode */}
          <button
            type="button"
            onClick={() => setMode('specific')}
            className={`relative p-4 rounded-lg border-2 transition-all text-left ${
              mode === 'specific'
                ? 'border-[#2A6B6E] bg-gradient-to-r from-[#2A6B6E]/10 to-[#11484D]/10 shadow-md'
                : 'border-[var(--color-border-default)] hover:border-[#2A6B6E]/50 bg-[var(--color-surface-raised)]'
            }`}
          >
            <div className="flex items-start gap-3">
              <div
                className={`p-2 rounded-lg ${
                  mode === 'specific'
                    ? 'bg-gradient-to-r from-[#2A6B6E] to-[#11484D] text-white'
                    : 'bg-[var(--color-surface-inset)] text-[var(--color-content-secondary)]'
                }`}
              >
                {getModeIcon('specific')}
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <h4 className="text-sm font-semibold text-[var(--color-content-primary)]">
                    Specific Languages
                  </h4>
                  <span className="px-2 py-0.5 text-xs font-medium bg-[var(--color-status-info-bg)] text-[var(--color-status-info)] rounded-full">
                    Recommended
                  </span>
                </div>
                <p className="text-xs text-[var(--color-content-secondary)]">
                  Select which languages to test. Ideal for regional releases or targeting specific
                  markets. Configure fallback behavior below.
                </p>
              </div>
              {mode === 'specific' && (
                <CheckCircle className="w-5 h-5 text-[#2A6B6E] flex-shrink-0" />
              )}
            </div>
          </button>

          {/* All Languages Mode */}
          <button
            type="button"
            onClick={() => setMode('all')}
            className={`relative p-4 rounded-lg border-2 transition-all text-left ${
              mode === 'all'
                ? 'border-[#2A6B6E] bg-gradient-to-r from-[#2A6B6E]/10 to-[#11484D]/10 shadow-md'
                : 'border-[var(--color-border-default)] hover:border-[#2A6B6E]/50 bg-[var(--color-surface-raised)]'
            }`}
          >
            <div className="flex items-start gap-3">
              <div
                className={`p-2 rounded-lg ${
                  mode === 'all'
                    ? 'bg-gradient-to-r from-[#2A6B6E] to-[#11484D] text-white'
                    : 'bg-[var(--color-surface-inset)] text-[var(--color-content-secondary)]'
                }`}
              >
                {getModeIcon('all')}
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <h4 className="text-sm font-semibold text-[var(--color-content-primary)]">
                    All Available Languages
                  </h4>
                  <span className="px-2 py-0.5 text-xs font-medium bg-[var(--color-status-purple-bg)] text-[var(--color-status-purple)] rounded-full">
                    Comprehensive
                  </span>
                </div>
                <p className="text-xs text-[var(--color-content-secondary)]">
                  Test all language variants available in each scenario. Most thorough coverage but
                  takes longer to execute.
                </p>
              </div>
              {mode === 'all' && (
                <CheckCircle className="w-5 h-5 text-[#2A6B6E] flex-shrink-0" />
              )}
            </div>
          </button>
        </div>
      </div>

      {/* Language Selection (only show when mode is 'specific') */}
      {mode === 'specific' && (
        <div className="space-y-3">
          <label className="block text-sm font-semibold text-[var(--color-content-secondary)]">
            Select Languages to Test
          </label>
          <div className="grid grid-cols-1 gap-2">
            {AVAILABLE_LANGUAGES.map((lang) => (
              <button
                key={lang.code}
                type="button"
                onClick={() => handleLanguageToggle(lang.code)}
                className={`flex items-center gap-3 p-3 rounded-lg border-2 transition-all ${
                  selectedLanguages.includes(lang.code)
                    ? 'border-[#2A6B6E] bg-gradient-to-r from-[#2A6B6E]/10 to-[#11484D]/10'
                    : 'border-[var(--color-border-default)] hover:border-[#2A6B6E]/50 bg-[var(--color-surface-raised)]'
                }`}
              >
                <div className="flex items-center gap-3 flex-1">
                  <span className="text-2xl">{lang.flag}</span>
                  <div className="text-left">
                    <div className="text-sm font-medium text-[var(--color-content-primary)]">
                      {lang.code}
                    </div>
                    <div className="text-xs text-[var(--color-content-muted)]">{lang.name}</div>
                  </div>
                </div>
                {selectedLanguages.includes(lang.code) && (
                  <CheckCircle className="w-5 h-5 text-[#2A6B6E]" />
                )}
              </button>
            ))}
          </div>
          {selectedLanguages.length === 0 && (
            <p className="text-xs text-[var(--color-status-amber)] flex items-center gap-2">
              <AlertTriangle className="w-4 h-4" />
              Select at least one language to test
            </p>
          )}
        </div>
      )}

      {/* Fallback Behavior (only show when mode is 'specific') */}
      {mode === 'specific' && (
        <div className="space-y-3">
          <label className="block text-sm font-semibold text-[var(--color-content-secondary)]">
            Fallback Behavior
            <span className="ml-2 text-xs font-normal text-[var(--color-content-muted)]">
              When a scenario doesn't support a selected language
            </span>
          </label>
          <div className="grid grid-cols-1 gap-2">
            {/* Smart Fallback */}
            <button
              type="button"
              onClick={() => setFallbackBehavior('smart')}
              className={`flex items-start gap-3 p-3 rounded-lg border-2 transition-all text-left ${
                fallbackBehavior === 'smart'
                  ? 'border-[var(--color-status-success)] bg-[var(--color-status-success-bg)]'
                  : 'border-[var(--color-border-default)] hover:border-[var(--color-status-success)]/50 bg-[var(--color-surface-raised)]'
              }`}
            >
              <div
                className={`p-1.5 rounded ${
                  fallbackBehavior === 'smart'
                    ? 'bg-[var(--color-status-success)] text-white'
                    : 'bg-[var(--color-surface-inset)] text-[var(--color-content-muted)]'
                }`}
              >
                {getFallbackIcon('smart')}
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-0.5">
                  <h5 className="text-sm font-medium text-[var(--color-content-primary)]">
                    Smart Fallback
                  </h5>
                  <span className="px-1.5 py-0.5 text-xs font-medium bg-[var(--color-status-success-bg)] text-[var(--color-status-success)] rounded">
                    Recommended
                  </span>
                </div>
                <p className="text-xs text-[var(--color-content-secondary)]">
                  Use primary language if requested language unavailable. Adds warning but scenario
                  still runs.
                </p>
              </div>
            </button>

            {/* Skip Scenario */}
            <button
              type="button"
              onClick={() => setFallbackBehavior('skip')}
              className={`flex items-start gap-3 p-3 rounded-lg border-2 transition-all text-left ${
                fallbackBehavior === 'skip'
                  ? 'border-[var(--color-status-amber)] bg-[var(--color-status-amber-bg)]'
                  : 'border-[var(--color-border-default)] hover:border-[var(--color-status-amber)]/50 bg-[var(--color-surface-raised)]'
              }`}
            >
              <div
                className={`p-1.5 rounded ${
                  fallbackBehavior === 'skip'
                    ? 'bg-[var(--color-status-amber)] text-white'
                    : 'bg-[var(--color-surface-inset)] text-[var(--color-content-muted)]'
                }`}
              >
                {getFallbackIcon('skip')}
              </div>
              <div className="flex-1">
                <h5 className="text-sm font-medium text-[var(--color-content-primary)] mb-0.5">
                  Skip Scenario
                </h5>
                <p className="text-xs text-[var(--color-content-secondary)]">
                  Don't run scenario if requested language unavailable. Marks scenario as skipped.
                </p>
              </div>
            </button>

            {/* Fail Scenario */}
            <button
              type="button"
              onClick={() => setFallbackBehavior('fail')}
              className={`flex items-start gap-3 p-3 rounded-lg border-2 transition-all text-left ${
                fallbackBehavior === 'fail'
                  ? 'border-[var(--color-status-danger)] bg-[var(--color-status-danger-bg)]'
                  : 'border-[var(--color-border-default)] hover:border-[var(--color-status-danger)]/50 bg-[var(--color-surface-raised)]'
              }`}
            >
              <div
                className={`p-1.5 rounded ${
                  fallbackBehavior === 'fail'
                    ? 'bg-[var(--color-status-danger)] text-white'
                    : 'bg-[var(--color-surface-inset)] text-[var(--color-content-muted)]'
                }`}
              >
                {getFallbackIcon('fail')}
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-0.5">
                  <h5 className="text-sm font-medium text-[var(--color-content-primary)]">
                    Fail Scenario
                  </h5>
                  <span className="px-1.5 py-0.5 text-xs font-medium bg-[var(--color-status-danger-bg)] text-[var(--color-status-danger)] rounded">
                    Strict
                  </span>
                </div>
                <p className="text-xs text-[var(--color-content-secondary)]">
                  Mark scenario as failed if requested language unavailable. Use for critical
                  requirements.
                </p>
              </div>
            </button>
          </div>
        </div>
      )}

      {/* Summary Preview */}
      <div className="bg-[var(--color-surface-inset)]/50 rounded-lg p-4 border border-[var(--color-border-default)]">
        <div className="flex items-start gap-3">
          <ChevronRight className="w-5 h-5 text-[#2A6B6E] mt-0.5" />
          <div className="flex-1">
            <h4 className="text-sm font-semibold text-[var(--color-content-primary)] mb-2">
              Configuration Summary
            </h4>
            <div className="space-y-1.5 text-xs text-[var(--color-content-secondary)]">
              <div className="flex items-center gap-2">
                <span className="font-medium text-[var(--color-content-secondary)]">Mode:</span>
                <span className="capitalize">{mode}</span>
              </div>
              {mode === 'specific' && (
                <>
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-[var(--color-content-secondary)]">Languages:</span>
                    {selectedLanguages.length > 0 ? (
                      <div className="flex items-center gap-1 flex-wrap">
                        {selectedLanguages.map((lang) => {
                          const langOption = AVAILABLE_LANGUAGES.find((l) => l.code === lang);
                          return (
                            <span
                              key={lang}
                              className="inline-flex items-center gap-1 px-2 py-0.5 bg-[var(--color-surface-raised)] border border-[var(--color-border-default)] rounded"
                            >
                              <span>{langOption?.flag}</span>
                              <span>{lang}</span>
                            </span>
                          );
                        })}
                      </div>
                    ) : (
                      <span className="text-[var(--color-status-amber)]">None selected</span>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-[var(--color-content-secondary)]">Fallback:</span>
                    <span className="capitalize">{fallbackBehavior}</span>
                  </div>
                </>
              )}
              {mode === 'all' && (
                <div className="flex items-center gap-2">
                  <span className="font-medium text-[var(--color-content-secondary)]">Coverage:</span>
                  <span>All available languages in each scenario</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LanguageConfigForm;
