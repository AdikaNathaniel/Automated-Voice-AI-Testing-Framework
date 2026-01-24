/**
 * Language Variant Manager Component
 *
 * Manages multi-language variants for scenario steps:
 * - Add/remove language variants
 * - Primary language selection
 * - Language-specific utterances and responses
 * - Visual language selector with flags
 */

import React, { useState } from 'react';
import { Plus, Trash2, Globe, Check, Languages, Loader2 } from 'lucide-react';
import apiClient from '../../services/api';
import Modal from '../../components/Modal/Modal';
import { useModal } from '../../hooks/useModal';

export interface LanguageVariant {
  language_code: string;
  user_utterance: string;
}

interface LanguageVariantManagerProps {
  variants: LanguageVariant[];
  primaryLanguage: string;
  onChange: (variants: LanguageVariant[], primaryLanguage: string) => void;
}

// Supported languages with display names and flags
const SUPPORTED_LANGUAGES = [
  { code: 'en-US', name: 'English (US)', flag: '🇺🇸' },
  { code: 'es-ES', name: 'Spanish (Spain)', flag: '🇪🇸' },
  { code: 'fr-FR', name: 'French (France)', flag: '🇫🇷' },
  { code: 'de-DE', name: 'German (Germany)', flag: '🇩🇪' },
  { code: 'it-IT', name: 'Italian (Italy)', flag: '🇮🇹' },
  { code: 'pt-BR', name: 'Portuguese (Brazil)', flag: '🇧🇷' },
  { code: 'ja-JP', name: 'Japanese (Japan)', flag: '🇯🇵' },
  { code: 'zh-CN', name: 'Chinese (Simplified)', flag: '🇨🇳' },
  { code: 'ko-KR', name: 'Korean (Korea)', flag: '🇰🇷' },
  { code: 'ar-SA', name: 'Arabic (Saudi Arabia)', flag: '🇸🇦' },
];

export const LanguageVariantManager: React.FC<LanguageVariantManagerProps> = ({
  variants,
  primaryLanguage,
  onChange,
}) => {
  const { modalState, showWarning, showSuccess, showError, closeModal } = useModal();
  const [showAddLanguage, setShowAddLanguage] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState('');
  const [isTranslating, setIsTranslating] = useState(false);
  const [showTranslateSelector, setShowTranslateSelector] = useState(false);
  const [selectedTranslateLanguages, setSelectedTranslateLanguages] = useState<string[]>([]);

  const addLanguageVariant = () => {
    if (!selectedLanguage) return;

    // Check if language already exists
    if (variants.some((v) => v.language_code === selectedLanguage)) {
      showWarning('This language variant already exists');
      return;
    }

    const newVariant: LanguageVariant = {
      language_code: selectedLanguage,
      user_utterance: '',
    };

    onChange([...variants, newVariant], primaryLanguage);
    setShowAddLanguage(false);
    setSelectedLanguage('');
  };

  const removeLanguageVariant = (languageCode: string) => {
    // Don't allow removing the primary language
    if (languageCode === primaryLanguage) {
      showWarning('Cannot remove the primary language. Set another language as primary first.');
      return;
    }

    const newVariants = variants.filter((v) => v.language_code !== languageCode);
    onChange(newVariants, primaryLanguage);
  };

  const updateVariant = (languageCode: string, field: 'user_utterance', value: string) => {
    const newVariants = variants.map((v) =>
      v.language_code === languageCode ? { ...v, [field]: value } : v
    );
    onChange(newVariants, primaryLanguage);
  };

  const setPrimaryLanguage = (languageCode: string) => {
    onChange(variants, languageCode);
  };

  // Get available languages for translation (not already added)
  const getAvailableLanguages = () => {
    return SUPPORTED_LANGUAGES
      .map((lang) => lang.code)
      .filter((code) => !variants.some((v) => v.language_code === code));
  };

  // Open translate selector and pre-select all available languages
  const openTranslateSelector = () => {
    const primaryVariant = variants.find((v) => v.language_code === primaryLanguage);
    if (!primaryVariant) {
      showWarning('Please set a primary language with content first');
      return;
    }

    if (!primaryVariant.user_utterance) {
      showWarning('Please fill in the utterance for the primary language first');
      return;
    }
    // expected_response is now optional - only show warning if trying to translate it later
    // but allow proceeding since validation can use ExpectedOutcome instead

    const available = getAvailableLanguages();
    if (available.length === 0) {
      showWarning('All languages already have variants');
      return;
    }

    setSelectedTranslateLanguages(available); // Pre-select all
    setShowTranslateSelector(true);
  };

  // Toggle language selection
  const toggleLanguageSelection = (languageCode: string) => {
    setSelectedTranslateLanguages((prev) =>
      prev.includes(languageCode)
        ? prev.filter((code) => code !== languageCode)
        : [...prev, languageCode]
    );
  };

  // Select all available languages
  const selectAllLanguages = () => {
    setSelectedTranslateLanguages(getAvailableLanguages());
  };

  // Deselect all languages
  const deselectAllLanguages = () => {
    setSelectedTranslateLanguages([]);
  };

  // Perform translation with selected languages
  const performTranslation = async () => {
    if (selectedTranslateLanguages.length === 0) {
      showWarning('Please select at least one language to translate to');
      return;
    }

    const primaryVariant = variants.find((v) => v.language_code === primaryLanguage);
    if (!primaryVariant) {
      showError('Primary language variant not found');
      return;
    }

    setIsTranslating(true);

    try {
      const response = await apiClient.post('/auto-translation/auto-translate-step', {
        user_utterance: primaryVariant.user_utterance,
        source_lang: primaryLanguage,
        target_languages: selectedTranslateLanguages,
      });

      const translations = response.data.data.translations;

      // Convert translations to variants
      const newVariants = Object.entries(translations).map(([lang, trans]: [string, any]) => ({
        language_code: lang,
        user_utterance: trans.user_utterance,
      }));

      // Merge with existing variants (keep existing, add new)
      const mergedVariants = [...variants];
      newVariants.forEach((newVariant) => {
        if (!mergedVariants.some((v) => v.language_code === newVariant.language_code)) {
          mergedVariants.push(newVariant);
        }
      });

      onChange(mergedVariants, primaryLanguage);
      setShowTranslateSelector(false);
      setSelectedTranslateLanguages([]);
      showSuccess(`Successfully translated to ${selectedTranslateLanguages.length} language(s)!`);
    } catch (error: any) {
      console.error('Auto-translate error:', error);
      showError(`Translation failed: ${error.response?.data?.detail || error.message}`);
    } finally {
      setIsTranslating(false);
    }
  };

  const getLanguageInfo = (code: string) => {
    return SUPPORTED_LANGUAGES.find((l) => l.code === code) || { code, name: code, flag: '🌐' };
  };

  const availableLanguages = SUPPORTED_LANGUAGES.filter(
    (lang) => !variants.some((v) => v.language_code === lang.code)
  );

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <div className="flex items-center gap-2">
          <Globe className="w-5 h-5 text-[var(--color-content-secondary)]" />
          <h4 className="text-sm font-semibold text-[var(--color-content-primary)]">Language Variants</h4>
          <span className="text-xs text-[var(--color-content-muted)]">({variants.length} language{variants.length !== 1 ? 's' : ''})</span>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={openTranslateSelector}
            disabled={isTranslating || getAvailableLanguages().length === 0}
            className="flex items-center gap-1 px-3 py-1.5 text-sm text-white bg-gradient-to-r from-[#2A6B6E] to-[#11484D] rounded-md hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Languages className="w-4 h-4" />
            Auto-Translate
          </button>
          <button
            type="button"
            onClick={() => setShowAddLanguage(!showAddLanguage)}
            className="flex items-center gap-1 px-3 py-1.5 text-sm text-[var(--color-status-info)] hover:text-[var(--color-status-info)] border border-[var(--color-status-info-bg)] rounded-md hover:bg-[var(--color-status-info-bg)]"
          >
            <Plus className="w-4 h-4" />
            Add Language
          </button>
        </div>
      </div>

      {/* Add Language Dropdown */}
      {showAddLanguage && (
        <div className="p-4 bg-[var(--color-status-info-bg)] border border-[var(--color-status-info-bg)] rounded-lg">
          <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-2">Select Language</label>
          <div className="flex gap-2">
            <select
              value={selectedLanguage}
              onChange={(e) => setSelectedLanguage(e.target.value)}
              className="flex-1 px-3 py-2 border border-[var(--color-border-strong)] rounded-md bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-border-focus)]"
            >
              <option value="">-- Select a language --</option>
              {availableLanguages.map((lang) => (
                <option key={lang.code} value={lang.code}>
                  {lang.flag} {lang.name}
                </option>
              ))}
            </select>
            <button
              type="button"
              onClick={addLanguageVariant}
              disabled={!selectedLanguage}
              className="px-4 py-2 bg-[var(--color-status-info)] text-white rounded-md hover:opacity-90 disabled:bg-[var(--color-interactive-disabled)] disabled:cursor-not-allowed"
            >
              Add
            </button>
          </div>
        </div>
      )}

      {/* Auto-Translate Language Selector */}
      {showTranslateSelector && (
        <div className="p-4 bg-gradient-to-br from-[var(--color-status-teal-bg)] to-[var(--color-status-teal-bg)] border-2 border-[#2A6B6E] rounded-lg shadow-md">
          <div className="flex justify-between items-center mb-3">
            <h5 className="text-sm font-semibold text-[var(--color-content-primary)]">Select Languages to Translate</h5>
            <button
              type="button"
              onClick={() => {
                setShowTranslateSelector(false);
                setSelectedTranslateLanguages([]);
              }}
              className="text-[var(--color-content-muted)] hover:text-[var(--color-content-primary)]"
            >
              ✕
            </button>
          </div>

          {/* Quick Select Buttons */}
          <div className="flex gap-2 mb-3">
            <button
              type="button"
              onClick={selectAllLanguages}
              className="px-3 py-1.5 text-xs font-medium text-[var(--color-brand-primary)] bg-[var(--color-surface-raised)] border border-[#2A6B6E] rounded-md hover:bg-[var(--color-status-teal-bg)]"
            >
              Select All
            </button>
            <button
              type="button"
              onClick={deselectAllLanguages}
              className="px-3 py-1.5 text-xs font-medium text-[var(--color-content-secondary)] bg-[var(--color-surface-raised)] border border-[var(--color-border-strong)] rounded-md hover:bg-[var(--color-interactive-hover)]"
            >
              Deselect All
            </button>
            <span className="ml-auto text-xs text-[var(--color-content-secondary)] self-center">
              {selectedTranslateLanguages.length} selected
            </span>
          </div>

          {/* Language Checkboxes */}
          <div className="grid grid-cols-2 gap-2 mb-4 max-h-64 overflow-y-auto">
            {getAvailableLanguages().map((langCode) => {
              const langInfo = getLanguageInfo(langCode);
              const isSelected = selectedTranslateLanguages.includes(langCode);

              return (
                <label
                  key={langCode}
                  className={`flex items-center gap-2 p-2 rounded-md cursor-pointer transition-colors ${
                    isSelected
                      ? 'bg-[var(--color-brand-muted)] border border-[#2A6B6E]'
                      : 'bg-[var(--color-surface-raised)] border border-[var(--color-border-default)] hover:bg-[var(--color-interactive-hover)]'
                  }`}
                >
                  <input
                    type="checkbox"
                    checked={isSelected}
                    onChange={() => toggleLanguageSelection(langCode)}
                    className="w-4 h-4 text-[#2A6B6E] border-[var(--color-border-strong)] rounded focus:ring-[#2A6B6E]"
                  />
                  <span className="text-lg">{langInfo.flag}</span>
                  <span className="text-sm font-medium text-[var(--color-content-secondary)]">{langInfo.name}</span>
                </label>
              );
            })}
          </div>

          {/* Action Buttons */}
          <div className="flex gap-2">
            <button
              type="button"
              onClick={performTranslation}
              disabled={isTranslating || selectedTranslateLanguages.length === 0}
              className="flex-1 flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-[#2A6B6E] to-[#11484D] rounded-md hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isTranslating ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Translating...
                </>
              ) : (
                <>
                  <Languages className="w-4 h-4" />
                  Translate to {selectedTranslateLanguages.length} Language{selectedTranslateLanguages.length !== 1 ? 's' : ''}
                </>
              )}
            </button>
            <button
              type="button"
              onClick={() => {
                setShowTranslateSelector(false);
                setSelectedTranslateLanguages([]);
              }}
              disabled={isTranslating}
              className="px-4 py-2 text-sm font-medium text-[var(--color-content-secondary)] bg-[var(--color-surface-raised)] border border-[var(--color-border-strong)] rounded-md hover:bg-[var(--color-interactive-hover)] disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Language Variants List */}
      {variants.length === 0 ? (
        <div className="text-center py-8 bg-[var(--color-surface-inset)]/50 rounded-lg border-2 border-dashed border-[var(--color-border-strong)]">
          <Globe className="w-12 h-12 text-[var(--color-content-muted)] mx-auto mb-2" />
          <p className="text-sm text-[var(--color-content-muted)]">No language variants added yet</p>
          <p className="text-xs text-[var(--color-content-muted)] mt-1">Add at least one language to get started</p>
        </div>
      ) : (
        <div className="space-y-3">
          {variants.map((variant) => {
            const langInfo = getLanguageInfo(variant.language_code);
            const isPrimary = variant.language_code === primaryLanguage;

            return (
              <div
                key={variant.language_code}
                className={`border rounded-lg p-4 ${
                  isPrimary
                    ? 'border-[var(--color-status-info)] bg-[var(--color-status-info-bg)]'
                    : 'border-[var(--color-border-strong)] bg-[var(--color-surface-raised)]'
                }`}
              >
                {/* Language Header */}
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <span className="text-2xl">{langInfo.flag}</span>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-[var(--color-content-primary)]">{langInfo.name}</span>
                        {isPrimary && (
                          <span className="px-2 py-0.5 text-xs font-semibold bg-[var(--color-status-info)] text-white rounded">
                            PRIMARY
                          </span>
                        )}
                      </div>
                      <span className="text-xs text-[var(--color-content-muted)]">{variant.language_code}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {!isPrimary && (
                      <button
                        type="button"
                        onClick={() => setPrimaryLanguage(variant.language_code)}
                        className="flex items-center gap-1 px-2 py-1 text-xs text-[var(--color-status-info)] hover:text-[var(--color-status-info)] border border-[var(--color-status-info-bg)] rounded hover:bg-[var(--color-status-info-bg)]"
                        title="Set as primary language"
                      >
                        <Check className="w-3 h-3" />
                        Set Primary
                      </button>
                    )}
                    <button
                      type="button"
                      onClick={() => removeLanguageVariant(variant.language_code)}
                      className="text-[var(--color-status-danger)] hover:text-[var(--color-status-danger)] disabled:opacity-50"
                      title="Remove language"
                      disabled={isPrimary}
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                {/* User Utterance */}
                <div>
                  <label className="block text-xs font-medium text-[var(--color-content-secondary)] mb-1">
                    User Utterance <span className="text-[var(--color-status-danger)]">*</span>
                  </label>
                  <input
                    type="text"
                    value={variant.user_utterance}
                    onChange={(e) => updateVariant(variant.language_code, 'user_utterance', e.target.value)}
                    className="w-full px-3 py-2 text-sm border border-[var(--color-border-strong)] rounded-md bg-[var(--color-surface-raised)] text-[var(--color-content-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-border-focus)]"
                    placeholder={`What the user says in ${langInfo.name}...`}
                    required
                  />
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Info Banner */}
      <div className="p-3 bg-[var(--color-surface-inset)]/50 border border-[var(--color-border-default)] rounded-lg">
        <p className="text-xs text-[var(--color-content-secondary)]">
          <strong>Tip:</strong> The primary language is used as the default when executing this scenario.
          You can switch languages during test execution.
        </p>
      </div>

      {/* Modal for alerts */}
      <Modal
        isOpen={modalState.isOpen}
        onClose={closeModal}
        onConfirm={modalState.onConfirm}
        title={modalState.title}
        message={modalState.message}
        type={modalState.type}
        confirmText={modalState.confirmText}
        cancelText={modalState.cancelText}
        showCancel={modalState.showCancel}
      />
    </div>
  );
};

export default LanguageVariantManager;
