import React, { useState, useEffect } from 'react';
import { CheckCircle, Circle } from 'lucide-react';

interface LanguageSelectorProps {
  /**
   * Available languages for the scenario
   * Example: ["en-US", "fr-FR", "es-ES"]
   */
  availableLanguages: string[];

  /**
   * Currently selected language codes
   */
  selectedLanguages: string[];

  /**
   * Callback when selection changes
   */
  onChange: (languages: string[]) => void;

  /**
   * Whether to show the "All Languages" option
   * Default: true
   */
  showAllOption?: boolean;

  /**
   * Label for the component
   * Default: "Select Languages to Execute"
   */
  label?: string;
}

// Language display names
const LANGUAGE_NAMES: Record<string, string> = {
  'en-US': 'English (US)',
  'en-GB': 'English (UK)',
  'fr-FR': 'French',
  'es-ES': 'Spanish',
  'de-DE': 'German',
  'it-IT': 'Italian',
  'ja-JP': 'Japanese',
  'zh-CN': 'Chinese (Simplified)',
  'pt-BR': 'Portuguese (Brazil)',
};

/**
 * Language selector component for multi-language scenarios
 *
 * Allows users to select which language variants to execute
 */
export const LanguageSelector: React.FC<LanguageSelectorProps> = ({
  availableLanguages,
  selectedLanguages,
  onChange,
  showAllOption = true,
  label = 'Select Languages to Execute',
}) => {
  const [allSelected, setAllSelected] = useState(false);

  // Check if all languages are selected
  useEffect(() => {
    if (selectedLanguages.length === 0) {
      setAllSelected(true);
    } else if (selectedLanguages.length === availableLanguages.length) {
      const allMatch = availableLanguages.every(lang => selectedLanguages.includes(lang));
      setAllSelected(allMatch);
    } else {
      setAllSelected(false);
    }
  }, [selectedLanguages, availableLanguages]);

  const handleAllToggle = () => {
    if (allSelected) {
      // Was "all", switch to first language
      onChange([availableLanguages[0]]);
    } else {
      // Switch to "all"
      onChange([]);
    }
  };

  const handleLanguageToggle = (languageCode: string) => {
    console.log('handleLanguageToggle called:', { languageCode, allSelected, selectedLanguages });

    if (allSelected) {
      // If "all" was selected, deselect this language (all except this one)
      const newSelection = availableLanguages.filter(lang => lang !== languageCode);
      console.log('Deselecting from all languages:', { languageCode, newSelection });
      onChange(newSelection);
      return;
    }

    if (selectedLanguages.includes(languageCode)) {
      // Remove language
      const newSelection = selectedLanguages.filter(lang => lang !== languageCode);
      console.log('Removing language:', { languageCode, newSelection });
      // If removing the last language, switch to "all"
      onChange(newSelection.length === 0 ? [] : newSelection);
    } else {
      // Add language
      const newSelection = [...selectedLanguages, languageCode];
      console.log('Adding language:', { languageCode, newSelection });
      // If all languages are now selected, switch to "all"
      if (newSelection.length === availableLanguages.length) {
        onChange([]);
      } else {
        onChange(newSelection);
      }
    }
  };

  const getLanguageName = (code: string): string => {
    return LANGUAGE_NAMES[code] || code;
  };

  const isLanguageSelected = (languageCode: string): boolean => {
    return allSelected || selectedLanguages.includes(languageCode);
  };

  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium text-[var(--color-content-secondary)]">
        {label}
      </label>

      <div className="space-y-2">
        {/* All Languages Option */}
        {showAllOption && (
          <button
            type="button"
            onClick={handleAllToggle}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg border-2 transition-all ${
              allSelected
                ? 'border-[var(--color-status-info)] bg-[var(--color-status-info-bg)]'
                : 'border-[var(--color-border-default)] hover:border-[var(--color-border-strong)]'
            }`}
          >
            {allSelected ? (
              <CheckCircle className="w-5 h-5 text-[var(--color-status-info)]" />
            ) : (
              <Circle className="w-5 h-5 text-[var(--color-content-muted)]" />
            )}
            <span className={`font-medium ${allSelected ? 'text-[var(--color-status-info)]' : 'text-[var(--color-content-secondary)]'}`}>
              All Languages
            </span>
            <span className="ml-auto text-sm text-[var(--color-content-muted)]">
              ({availableLanguages.length} variants)
            </span>
          </button>
        )}

        {/* Individual Language Options */}
        <div className="space-y-2 pl-4">
          {availableLanguages.map((languageCode) => {
            const isSelected = isLanguageSelected(languageCode);

            return (
              <button
                key={languageCode}
                type="button"
                onClick={() => handleLanguageToggle(languageCode)}
                className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-lg border transition-all ${
                  isSelected && !allSelected
                    ? 'border-[var(--color-status-info)] bg-[var(--color-status-info-bg)]'
                    : 'border-[var(--color-border-default)] hover:border-[var(--color-border-strong)]'
                }`}
              >
                {isSelected ? (
                  <CheckCircle className={`w-4 h-4 ${allSelected ? 'text-[var(--color-content-muted)]' : 'text-[var(--color-status-info)]'}`} />
                ) : (
                  <Circle className="w-4 h-4 text-[var(--color-content-muted)]" />
                )}
                <span className={`text-sm ${
                  isSelected && !allSelected
                    ? 'text-[var(--color-status-info)] font-medium'
                    : 'text-[var(--color-content-secondary)]'
                }`}>
                  {getLanguageName(languageCode)}
                </span>
                <span className="ml-auto text-xs font-mono text-[var(--color-content-muted)]">
                  {languageCode}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Selection Summary */}
      <div className="text-sm text-[var(--color-content-secondary)]">
        {allSelected ? (
          <p>Executing all language variants</p>
        ) : selectedLanguages.length === 1 ? (
          <p>Executing 1 language variant</p>
        ) : (
          <p>Executing {selectedLanguages.length} language variants</p>
        )}
      </div>
    </div>
  );
};

export default LanguageSelector;
