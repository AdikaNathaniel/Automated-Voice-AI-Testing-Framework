/**
 * Tag Selector Component
 *
 * A reusable tag selector component with multi-select functionality.
 *
 * Features:
 * - Multi-select tag selection with custom input
 * - Chip display for selected tags with delete functionality
 * - Search and filter available tags
 * - Tag validation (prevent duplicates, trim whitespace)
 * - Tag count and limit display
 * - Read-only mode support
 * - Empty state handling
 * - Responsive design
 *
 * Props:
 * - value: Array of selected tag strings
 * - onChange: Callback function called when tags change
 * - availableTags: Optional array of predefined tags
 * - label: Optional label for the selector
 * - helperText: Optional helper text
 * - readOnly: Optional read-only mode
 * - maxTags: Optional maximum number of tags allowed
 * - placeholder: Optional placeholder text
 */

import React, { useState } from 'react';
import { X } from 'lucide-react';

/**
 * Props interface for TagSelector component
 */
interface TagSelectorProps {
  /** Array of selected tag strings */
  value: string[];

  /** Callback function called when tags change */
  onChange: (tags: string[]) => void;

  /** Optional array of predefined tags */
  availableTags?: string[];

  /** Optional label for the selector */
  label?: string;

  /** Optional helper text */
  helperText?: string;

  /** Read-only mode */
  readOnly?: boolean;

  /** Maximum number of tags allowed */
  maxTags?: number;

  /** Placeholder text */
  placeholder?: string;
}

/**
 * TagSelector Component
 *
 * Multi-select tag selector with autocomplete
 */
const TagSelector: React.FC<TagSelectorProps> = ({
  value,
  onChange,
  availableTags = [],
  label = 'Tags',
  helperText,
  readOnly = false,
  maxTags,
  placeholder = 'Select or create tags...',
}) => {
  // Local state for input value
  const [inputValue, setInputValue] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);

  /**
   * Handle tag removal
   */
  const handleRemoveTag = (tagToRemove: string) => {
    if (readOnly) return;
    const newTags = value.filter(tag => tag !== tagToRemove);
    onChange(newTags);
  };

  /**
   * Handle tag addition
   */
  const handleAddTag = (tagToAdd: string) => {
    const trimmedTag = tagToAdd.trim();
    if (!trimmedTag || readOnly) return;

    // Check if tag already exists (case-insensitive)
    const tagExists = value.some(
      tag => tag.toLowerCase() === trimmedTag.toLowerCase()
    );
    if (tagExists) return;

    // Check max limit
    if (maxTags && value.length >= maxTags) return;

    onChange([...value, trimmedTag]);
    setInputValue('');
    setShowSuggestions(false);
  };

  /**
   * Handle input key down
   */
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && inputValue.trim()) {
      e.preventDefault();
      handleAddTag(inputValue);
    } else if (e.key === 'Backspace' && !inputValue && value.length > 0) {
      // Remove last tag on backspace if input is empty
      handleRemoveTag(value[value.length - 1]);
    }
  };

  /**
   * Get filtered suggestions
   */
  const getSuggestions = (): string[] => {
    if (!inputValue.trim()) return [];

    return availableTags.filter(
      tag =>
        tag.toLowerCase().includes(inputValue.toLowerCase()) &&
        !value.some(v => v.toLowerCase() === tag.toLowerCase())
    );
  };

  const suggestions = getSuggestions();
  const tagCount = value.length;
  const isAtLimit = maxTags && tagCount >= maxTags;

  // Build helper text
  const buildHelperText = (): string => {
    const countText = maxTags
      ? `${tagCount} / ${maxTags} tags`
      : `${tagCount} tags`;

    if (helperText) {
      return `${helperText} (${countText})`;
    }

    return countText;
  };

  return (
    <div className="w-full">
      {/* Label */}
      {label && (
        <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1">
          {label}
        </label>
      )}

      {/* Tag Input Container */}
      <div
        className={`border border-[var(--color-border-default)] rounded-lg p-2 focus-within:border-[var(--color-brand-primary)] focus-within:ring-2 focus-within:ring-[var(--color-brand-primary)]/10 ${
          readOnly ? 'bg-[var(--color-surface-inset)]' : 'bg-[var(--color-surface-raised)]'
        }`}
      >
        {/* Selected Tags */}
        <div className="flex flex-wrap gap-2 mb-2">
          {value.map((tag) => (
            <span
              key={tag}
              className="badge bg-[var(--color-status-info-bg)] text-[var(--color-status-info)] inline-flex items-center gap-1"
            >
              {tag}
              {!readOnly && (
                <button
                  type="button"
                  onClick={() => handleRemoveTag(tag)}
                  className="hover:bg-[var(--color-interactive-hover)] rounded p-0.5 transition-colors"
                  aria-label={`Remove ${tag}`}
                >
                  <X className="w-3 h-3" />
                </button>
              )}
            </span>
          ))}
        </div>

        {/* Input Field */}
        {!readOnly && !isAtLimit && (
          <div className="relative">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              onFocus={() => setShowSuggestions(true)}
              onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
              placeholder={value.length === 0 ? placeholder : ''}
              disabled={readOnly}
              className="w-full px-2 py-1 text-sm border-none outline-none"
            />

            {/* Suggestions Dropdown */}
            {showSuggestions && suggestions.length > 0 && (
              <div className="absolute z-10 w-full mt-1 bg-[var(--color-surface-overlay)] border border-[var(--color-border-default)] rounded-lg shadow-lg max-h-48 overflow-y-auto">
                {suggestions.map((suggestion) => (
                  <button
                    key={suggestion}
                    type="button"
                    onClick={() => handleAddTag(suggestion)}
                    className="w-full text-left px-3 py-2 text-sm hover:bg-[var(--color-interactive-hover)] transition-colors"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Helper Text */}
      <p className="text-xs text-[var(--color-content-muted)] mt-1">
        {buildHelperText()}
      </p>

      {/* Max Limit Warning */}
      {isAtLimit && (
        <p className="text-xs text-[var(--color-status-warning)] mt-1">
          Maximum tag limit reached
        </p>
      )}
    </div>
  );
};

export default TagSelector;
