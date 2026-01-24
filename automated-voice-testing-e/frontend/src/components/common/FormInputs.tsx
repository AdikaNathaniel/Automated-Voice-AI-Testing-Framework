/**
 * Form Input Components
 *
 * Reusable, consistently styled form inputs for the application.
 * Uses semantic tokens for consistent theming across light/dark/oled.
 */

import React, { forwardRef, useState, useRef, useEffect, useCallback } from 'react';
import { Search, ChevronDown, Check } from 'lucide-react';

// ============================================
// Shared Styles (using semantic tokens)
// ============================================

const baseInputStyles = `
  px-4 py-3 text-sm rounded-xl
  bg-[var(--color-surface-raised)]
  border-2 border-[var(--color-border-default)]
  text-[var(--color-content-primary)]
  placeholder:text-[var(--color-content-muted)]
  shadow-sm
  transition-all duration-200 ease-out
  hover:border-[var(--color-border-strong)]
  focus:outline-none focus:border-[var(--color-brand-primary)] focus:ring-3 focus:ring-[var(--color-brand-primary)]/15 focus:shadow-md
  disabled:bg-[var(--color-surface-inset)] disabled:text-[var(--color-content-muted)] disabled:cursor-not-allowed disabled:opacity-60
`.trim().replace(/\s+/g, ' ');

const selectStyles = `
  pl-3 pr-8 py-2.5 text-sm rounded-xl
  bg-[var(--color-surface-raised)]
  border-2 border-[var(--color-border-default)]
  text-[var(--color-content-primary)]
  shadow-sm cursor-pointer
  transition-all duration-200 ease-out
  appearance-none
  hover:border-[var(--color-border-strong)]
  focus:outline-none focus:border-[var(--color-brand-primary)] focus:ring-2 focus:ring-[var(--color-brand-primary)]/15 focus:shadow-md
  disabled:bg-[var(--color-surface-inset)] disabled:text-[var(--color-content-muted)] disabled:cursor-not-allowed disabled:opacity-60
`.trim().replace(/\s+/g, ' ');

// ============================================
// Input Component
// ============================================

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: boolean;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className = '', error, ...props }, ref) => {
    const errorStyles = error ? 'border-[var(--color-status-danger)] focus:border-[var(--color-status-danger)] focus:ring-[var(--color-status-danger)]/15' : '';

    return (
      <input
        ref={ref}
        className={`${baseInputStyles} ${errorStyles} ${className}`}
        {...props}
      />
    );
  }
);

Input.displayName = 'Input';

// ============================================
// Select Component
// ============================================

export interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  error?: boolean;
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ className = '', error, style, ...props }, ref) => {
    const errorStyles = error ? 'border-[var(--color-status-danger)] focus:border-[var(--color-status-danger)] focus:ring-[var(--color-status-danger)]/15' : '';

    return (
      <select
        ref={ref}
        className={`${selectStyles} select ${errorStyles} ${className}`}
        style={style}
        {...props}
      />
    );
  }
);

Select.displayName = 'Select';

// ============================================
// Dropdown Component (Custom styled select)
// ============================================

export interface DropdownOption {
  value: string;
  label: string;
  icon?: React.ReactNode;
}

export interface DropdownProps {
  options: DropdownOption[];
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
  error?: boolean;
  className?: string;
  menuClassName?: string;
  id?: string;
}

export const Dropdown: React.FC<DropdownProps> = ({
  options,
  value,
  onChange,
  placeholder = 'Select...',
  disabled = false,
  error = false,
  className = '',
  menuClassName = '',
  id,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState(-1);
  const [minWidth, setMinWidth] = useState<number | undefined>(undefined);
  const containerRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);
  const listRef = useRef<HTMLUListElement>(null);
  const measureRef = useRef<HTMLDivElement>(null);

  const selectedOption = options.find((opt) => opt.value === value);

  // Measure the width of all options to set minimum width
  useEffect(() => {
    if (measureRef.current) {
      const width = measureRef.current.offsetWidth;
      // Add padding for the chevron icon and some extra space
      setMinWidth(width + 32);
    }
  }, [options, placeholder]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Reset highlighted index when options change or dropdown opens
  useEffect(() => {
    if (isOpen) {
      const currentIndex = options.findIndex((opt) => opt.value === value);
      setHighlightedIndex(currentIndex >= 0 ? currentIndex : 0);
    }
  }, [isOpen, options, value]);

  // Scroll highlighted option into view
  useEffect(() => {
    if (isOpen && highlightedIndex >= 0 && listRef.current) {
      const highlightedEl = listRef.current.children[highlightedIndex] as HTMLElement;
      if (highlightedEl) {
        highlightedEl.scrollIntoView({ block: 'nearest' });
      }
    }
  }, [highlightedIndex, isOpen]);

  const handleKeyDown = useCallback(
    (event: React.KeyboardEvent) => {
      if (disabled) return;

      switch (event.key) {
        case 'Enter':
        case ' ':
          event.preventDefault();
          if (isOpen && highlightedIndex >= 0) {
            onChange(options[highlightedIndex].value);
            setIsOpen(false);
          } else {
            setIsOpen(true);
          }
          break;
        case 'Escape':
          event.preventDefault();
          setIsOpen(false);
          buttonRef.current?.focus();
          break;
        case 'ArrowDown':
          event.preventDefault();
          if (!isOpen) {
            setIsOpen(true);
          } else {
            setHighlightedIndex((prev) =>
              prev < options.length - 1 ? prev + 1 : prev
            );
          }
          break;
        case 'ArrowUp':
          event.preventDefault();
          if (isOpen) {
            setHighlightedIndex((prev) => (prev > 0 ? prev - 1 : prev));
          }
          break;
        case 'Home':
          event.preventDefault();
          if (isOpen) setHighlightedIndex(0);
          break;
        case 'End':
          event.preventDefault();
          if (isOpen) setHighlightedIndex(options.length - 1);
          break;
      }
    },
    [disabled, isOpen, highlightedIndex, options, onChange]
  );

  const handleOptionClick = (optionValue: string) => {
    onChange(optionValue);
    setIsOpen(false);
    buttonRef.current?.focus();
  };

  const errorStyles = error
    ? 'border-[var(--color-status-danger)] focus:border-[var(--color-status-danger)] focus:ring-[var(--color-status-danger)]/15'
    : '';

  return (
    <div ref={containerRef} className={`relative inline-block ${className}`} id={id}>
      {/* Hidden element to measure the width of the longest option */}
      <div
        ref={measureRef}
        aria-hidden="true"
        className="absolute invisible whitespace-nowrap text-sm px-3 py-2"
        style={{ pointerEvents: 'none' }}
      >
        {/* Measure placeholder */}
        <span>{placeholder}</span>
        {/* Measure all options and find the longest */}
        {options.map((opt) => (
          <div key={opt.value} className="flex items-center gap-2">
            {opt.icon}
            {opt.label}
          </div>
        ))}
      </div>

      <button
        ref={buttonRef}
        type="button"
        onClick={() => !disabled && setIsOpen(!isOpen)}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
        aria-labelledby={id ? `${id}-label` : undefined}
        style={{ minWidth: minWidth ? `${minWidth}px` : undefined }}
        className={`
          flex items-center justify-between gap-2
          pl-3 pr-2 py-2.5 text-sm rounded-xl
          bg-[var(--color-surface-raised)]
          border-2 border-[var(--color-border-default)]
          text-[var(--color-content-primary)]
          shadow-sm cursor-pointer
          transition-all duration-200 ease-out
          hover:border-[var(--color-border-strong)]
          focus:outline-none focus:border-[var(--color-brand-primary)] focus:ring-2 focus:ring-[var(--color-brand-primary)]/15 focus:shadow-md
          disabled:bg-[var(--color-surface-inset)] disabled:text-[var(--color-content-muted)] disabled:cursor-not-allowed disabled:opacity-60
          ${errorStyles}
        `.trim().replace(/\s+/g, ' ')}
      >
        <span className={`truncate ${!selectedOption ? 'text-[var(--color-content-muted)]' : ''}`}>
          {selectedOption ? (
            <span className="flex items-center gap-2">
              {selectedOption.icon}
              {selectedOption.label}
            </span>
          ) : (
            placeholder
          )}
        </span>
        <ChevronDown
          className={`w-4 h-4 text-[var(--color-content-muted)] transition-transform duration-200 flex-shrink-0 ${
            isOpen ? 'rotate-180' : ''
          }`}
        />
      </button>

      {isOpen && (
        <ul
          ref={listRef}
          role="listbox"
          aria-activedescendant={highlightedIndex >= 0 ? `option-${highlightedIndex}` : undefined}
          style={{ minWidth: minWidth ? `${minWidth}px` : undefined }}
          className={`
            absolute z-50 mt-1 w-full min-w-[160px]
            bg-[var(--color-surface-raised)]
            border border-[var(--color-border-default)]
            rounded-xl shadow-lg
            py-1 max-h-60 overflow-auto
            animate-in fade-in-0 zoom-in-95 duration-100
            ${menuClassName}
          `.trim().replace(/\s+/g, ' ')}
        >
          {options.map((option, index) => {
            const isSelected = option.value === value;
            const isHighlighted = index === highlightedIndex;

            return (
              <li
                key={option.value}
                id={`option-${index}`}
                role="option"
                aria-selected={isSelected}
                onClick={() => handleOptionClick(option.value)}
                onMouseEnter={() => setHighlightedIndex(index)}
                className={`
                  flex items-center justify-between gap-2 px-3 py-2 text-sm cursor-pointer
                  transition-colors duration-75
                  ${isHighlighted ? 'bg-[var(--color-interactive-hover)]' : ''}
                  ${isSelected ? 'text-[var(--color-brand-primary)] font-medium' : 'text-[var(--color-content-secondary)]'}
                `.trim().replace(/\s+/g, ' ')}
              >
                <span className="flex items-center gap-2 truncate">
                  {option.icon}
                  {option.label}
                </span>
                {isSelected && (
                  <Check className="w-4 h-4 flex-shrink-0 text-[var(--color-brand-primary)]" />
                )}
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
};

Dropdown.displayName = 'Dropdown';

// ============================================
// Textarea Component
// ============================================

export interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  error?: boolean;
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className = '', error, ...props }, ref) => {
    const errorStyles = error ? 'border-[var(--color-status-danger)] focus:border-[var(--color-status-danger)] focus:ring-[var(--color-status-danger)]/15' : '';

    return (
      <textarea
        ref={ref}
        className={`${baseInputStyles} resize-y min-h-[100px] ${errorStyles} ${className}`}
        {...props}
      />
    );
  }
);

Textarea.displayName = 'Textarea';

// ============================================
// SearchInput Component
// ============================================

export interface SearchInputProps extends Omit<InputProps, 'type'> {
  onSearch?: (value: string) => void;
  iconClassName?: string;
  maxWidth?: string | number;
}

export const SearchInput = forwardRef<HTMLInputElement, SearchInputProps>(
  ({ className = '', iconClassName = '', onSearch, onChange, maxWidth = '320px', ...props }, ref) => {
    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      onChange?.(e);
      onSearch?.(e.target.value);
    };

    const maxWidthStyle = typeof maxWidth === 'number' ? `${maxWidth}px` : maxWidth;

    return (
      <div className="relative w-full" style={{ maxWidth: maxWidthStyle }}>
        <Search
          className={`absolute left-4 top-1/2 transform -translate-y-1/2 w-4.5 h-4.5 text-[var(--color-content-muted)] pointer-events-none transition-colors ${iconClassName}`}
        />
        <input
          ref={ref}
          type="text"
          className={`${baseInputStyles} w-full pl-11 ${className}`}
          onChange={handleChange}
          {...props}
        />
      </div>
    );
  }
);

SearchInput.displayName = 'SearchInput';

// ============================================
// FormLabel Component
// ============================================

export interface FormLabelProps extends React.LabelHTMLAttributes<HTMLLabelElement> {
  required?: boolean;
}

export const FormLabel: React.FC<FormLabelProps> = ({
  children,
  required,
  className = '',
  ...props
}) => {
  return (
    <label
      className={`block text-sm font-semibold text-[var(--color-content-secondary)] mb-2 ${className}`}
      {...props}
    >
      {children}
      {required && <span className="text-[var(--color-status-danger)] ml-0.5">*</span>}
    </label>
  );
};

// ============================================
// FormHelper Component
// ============================================

export interface FormHelperProps {
  children: React.ReactNode;
  error?: boolean;
  className?: string;
}

export const FormHelper: React.FC<FormHelperProps> = ({
  children,
  error,
  className = ''
}) => {
  const colorClass = error
    ? 'text-[var(--color-status-danger)]'
    : 'text-[var(--color-content-muted)]';

  return (
    <p className={`text-xs mt-1.5 ${colorClass} ${className}`}>
      {children}
    </p>
  );
};

// ============================================
// FormGroup Component (wrapper for form fields)
// ============================================

export interface FormGroupProps {
  children: React.ReactNode;
  className?: string;
}

export const FormGroup: React.FC<FormGroupProps> = ({ children, className = '' }) => {
  return (
    <div className={`space-y-1 ${className}`}>
      {children}
    </div>
  );
};

// ============================================
// Checkbox Component
// ============================================

export interface CheckboxProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
}

export const Checkbox = forwardRef<HTMLInputElement, CheckboxProps>(
  ({ label, className = '', id, ...props }, ref) => {
    const inputId = id || `checkbox-${Math.random().toString(36).substr(2, 9)}`;

    return (
      <label htmlFor={inputId} className="flex items-center gap-2.5 cursor-pointer">
        <input
          ref={ref}
          id={inputId}
          type="checkbox"
          className={`w-4.5 h-4.5 rounded border-[var(--color-border-default)] text-[var(--color-brand-primary)] focus:ring-2 focus:ring-[var(--color-brand-primary)]/20 focus:ring-offset-0 transition-all duration-150 cursor-pointer ${className}`}
          {...props}
        />
        {label && (
          <span className="text-sm text-[var(--color-content-secondary)]">{label}</span>
        )}
      </label>
    );
  }
);

Checkbox.displayName = 'Checkbox';

// ============================================
// Radio Component
// ============================================

export interface RadioProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
}

export const Radio = forwardRef<HTMLInputElement, RadioProps>(
  ({ label, className = '', id, ...props }, ref) => {
    const inputId = id || `radio-${Math.random().toString(36).substr(2, 9)}`;

    return (
      <label htmlFor={inputId} className="flex items-center gap-2.5 cursor-pointer">
        <input
          ref={ref}
          id={inputId}
          type="radio"
          className={`w-4.5 h-4.5 rounded-full border-[var(--color-border-default)] text-[var(--color-brand-primary)] focus:ring-2 focus:ring-[var(--color-brand-primary)]/20 focus:ring-offset-0 transition-all duration-150 cursor-pointer ${className}`}
          {...props}
        />
        {label && (
          <span className="text-sm text-[var(--color-content-secondary)]">{label}</span>
        )}
      </label>
    );
  }
);

Radio.displayName = 'Radio';

export default {
  Input,
  Select,
  Dropdown,
  Textarea,
  SearchInput,
  FormLabel,
  FormHelper,
  FormGroup,
  Checkbox,
  Radio,
};
