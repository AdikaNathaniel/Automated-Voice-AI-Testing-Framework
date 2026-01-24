/**
 * LanguageSelector Component
 *
 * Provides a compact dropdown for filtering content by language, displaying
 * human-readable language names. Supports an optional "All languages"
 * entry for clearing the filter.
 */

import React, { useMemo, useId } from 'react';
import { Dropdown, type DropdownOption } from './FormInputs';

/** Special token used internally to represent the "All languages" option. */
const ALL_LANG_VALUE = '__ALL_LANGUAGES__';

export interface LanguageOption {
  code: string;
  name: string;
  nativeName?: string;
}

export interface LanguageSelectorProps {
  languages: LanguageOption[];
  value: string | null;
  onChange: (languageCode: string | null) => void;
  label?: string;
  helperText?: string;
  includeAllOption?: boolean;
  disabled?: boolean;
}

const LanguageSelector: React.FC<LanguageSelectorProps> = ({
  languages,
  value,
  onChange,
  label = 'Language',
  helperText,
  includeAllOption = false,
  disabled = false,
}) => {
  const labelId = useId();

  const dropdownOptions: DropdownOption[] = useMemo(() => {
    const opts: DropdownOption[] = languages.map((lang) => ({
      value: lang.code,
      label: lang.nativeName && lang.nativeName !== lang.name
        ? `${lang.name} (${lang.nativeName})`
        : lang.name,
    }));

    if (includeAllOption) {
      return [{ value: ALL_LANG_VALUE, label: 'All languages' }, ...opts];
    }

    return opts;
  }, [includeAllOption, languages]);

  const handleChange = (selectedValue: string) => {
    if (selectedValue === ALL_LANG_VALUE) {
      onChange(null);
      return;
    }
    onChange(selectedValue);
  };

  const resolvedValue =
    value === null && includeAllOption ? ALL_LANG_VALUE : value ?? '';

  return (
    <div className="min-w-[150px]">
      <label
        id={labelId}
        className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1"
      >
        {label}
      </label>
      <Dropdown
        options={dropdownOptions}
        value={resolvedValue}
        onChange={handleChange}
        disabled={disabled}
        placeholder="Select language..."
      />
      {helperText && (
        <p className="text-xs text-[var(--color-content-muted)] mt-1">
          {helperText}
        </p>
      )}
    </div>
  );
};

export default LanguageSelector;
