import React, { useState, useEffect } from 'react';
import apiClient from '../services/api';

interface Language {
  code: string;
  name: string;
  native_name: string;
  soundhound_model: string;
}

interface LanguageSelectorProps {
  selectedLanguages: string[];
  onChange: (languages: string[]) => void;
  disabled?: boolean;
  maxSelections?: number;
  availableLanguageCodes?: string[]; // Filter to only show these language codes
}

export const LanguageSelector: React.FC<LanguageSelectorProps> = ({
  selectedLanguages,
  onChange,
  disabled = false,
  maxSelections,
  availableLanguageCodes,
}) => {
  const [languages, setLanguages] = useState<Language[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchLanguages();
  }, []);

  const fetchLanguages = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.get('/languages');
      setLanguages(response.data.data || []);
    } catch (err) {
      console.error('Failed to fetch languages:', err);
      setError('Failed to load languages');
    } finally {
      setLoading(false);
    }
  };

  const handleToggle = (languageCode: string) => {
    if (disabled) return;

    const isSelected = selectedLanguages.includes(languageCode);

    if (isSelected) {
      // Don't allow deselecting if it's the last one
      if (selectedLanguages.length === 1) {
        return;
      }
      onChange(selectedLanguages.filter((code) => code !== languageCode));
    } else {
      // Check max selections limit
      if (maxSelections && selectedLanguages.length >= maxSelections) {
        return;
      }
      onChange([...selectedLanguages, languageCode]);
    }
  };

  if (loading) {
    return (
      <div className="my-3">
        <div className="p-4 rounded-lg text-center text-sm bg-[var(--color-surface-inset)] text-[var(--color-content-secondary)]">
          Loading languages...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="my-3">
        <div className="p-4 rounded-lg text-center text-sm bg-[var(--color-status-danger-bg)] text-[var(--color-status-danger)]">
          {error}
          <button
            onClick={fetchLanguages}
            className="ml-3 px-3 py-1 bg-[var(--color-status-danger)] text-white border-none rounded cursor-pointer text-sm hover:opacity-90 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  // Filter languages if availableLanguageCodes is provided
  const filteredLanguages = availableLanguageCodes
    ? languages.filter((lang) => availableLanguageCodes.includes(lang.code))
    : languages;

  // Show message if no languages are available
  const hasNoLanguages = filteredLanguages.length === 0;

  return (
    <div className="my-3">
      <label className="block font-semibold text-sm text-[var(--color-content-secondary)] mb-2">
        Languages to test:
        <span className="font-normal text-sm text-[var(--color-content-muted)] ml-2">
          {availableLanguageCodes && availableLanguageCodes.length > 0
            ? `(${availableLanguageCodes.length} available)`
            : '(Select at least one)'}
        </span>
      </label>
      {hasNoLanguages ? (
        <div className="p-4 rounded-lg text-center text-sm bg-[var(--color-status-warning-bg)] border border-[var(--color-status-warning)] text-[var(--color-status-warning)]">
          <p>
            No languages available for this test case. Please add language queries to the scenario definition.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
          {filteredLanguages.map((language) => {
          const isSelected = selectedLanguages.includes(language.code);
          const isDisabled =
            disabled ||
            (maxSelections &&
              !isSelected &&
              selectedLanguages.length >= maxSelections) ||
            (isSelected && selectedLanguages.length === 1);

          return (
            <label
              key={language.code}
              className={`flex items-center p-2 px-3 border rounded-md cursor-pointer transition-all ${
                isSelected
                  ? 'border-[var(--color-status-info)] bg-[var(--color-status-info-bg)]'
                  : 'border-[var(--color-border-default)] bg-[var(--color-surface-raised)] hover:border-[var(--color-status-info)] hover:bg-[var(--color-status-info-bg)]'
              } ${isDisabled ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              <input
                type="checkbox"
                checked={isSelected}
                onChange={() => handleToggle(language.code)}
                disabled={isDisabled}
                className="mr-3 w-4 h-4 cursor-pointer"
              />
              <div className="flex flex-col gap-1">
                <span className="text-sm font-medium text-[var(--color-content-primary)]">
                  {language.name}
                </span>
                <span className="text-xs text-[var(--color-content-muted)]">
                  {language.native_name}
                </span>
              </div>
            </label>
          );
        })}
        </div>
      )}
      {!hasNoLanguages && (
        <div className="mt-2 flex justify-between items-center text-xs text-[var(--color-content-muted)]">
          <span className="font-medium">
            {selectedLanguages.length} language{selectedLanguages.length !== 1 ? 's' : ''} selected
          </span>
          {maxSelections && (
            <span className="italic">
              (max: {maxSelections})
            </span>
          )}
        </div>
      )}
    </div>
  );
};

