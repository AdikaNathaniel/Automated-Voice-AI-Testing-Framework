/**
 * LoadingSpinner Component
 *
 * Standardized loading state display with spinner animation and message.
 * Supports full-page and inline variants.
 */

import React from 'react';
import { RefreshCw, Loader2 } from 'lucide-react';

type SpinnerVariant = 'page' | 'card' | 'inline';
type SpinnerSize = 'sm' | 'md' | 'lg';

interface LoadingSpinnerProps {
  /** Message to display below the spinner */
  message?: string;
  /** Display variant: 'page' for full-page, 'card' for card container, 'inline' for inline */
  variant?: SpinnerVariant;
  /** Spinner size */
  size?: SpinnerSize;
  /** Additional CSS classes */
  className?: string;
}

const sizeClasses: Record<SpinnerSize, { spinner: string; text: string }> = {
  sm: { spinner: 'w-6 h-6', text: 'text-sm' },
  md: { spinner: 'w-8 h-8', text: 'text-base' },
  lg: { spinner: 'w-12 h-12', text: 'text-lg' },
};

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  message,
  variant = 'card',
  size = 'md',
  className = '',
}) => {
  const sizeConfig = sizeClasses[size];

  const spinner = (
    <RefreshCw
      className={`${sizeConfig.spinner} text-primary animate-spin`}
      aria-hidden="true"
    />
  );

  if (variant === 'inline') {
    return (
      <div
        className={`inline-flex items-center gap-2 ${className}`}
        role="status"
        aria-live="polite"
      >
        <Loader2
          className={`${sizeClasses.sm.spinner} text-primary animate-spin`}
          aria-hidden="true"
        />
        {message && (
          <span className={`text-[var(--color-content-secondary)] ${sizeClasses.sm.text}`}>
            {message}
          </span>
        )}
        <span className="sr-only">{message || 'Loading...'}</span>
      </div>
    );
  }

  const content = (
    <div className="flex flex-col items-center gap-4" role="status" aria-live="polite">
      {spinner}
      {message && (
        <p className={`font-medium text-[var(--color-content-primary)] ${sizeConfig.text}`}>
          {message}
        </p>
      )}
      <span className="sr-only">{message || 'Loading...'}</span>
    </div>
  );

  if (variant === 'page') {
    return (
      <div
        className={`min-h-screen bg-[var(--color-surface-inset)] flex items-center justify-center ${className}`}
      >
        {content}
      </div>
    );
  }

  // variant === 'card'
  return (
    <div
      className={`bg-[var(--color-surface-raised)] rounded-xl p-6 shadow-sm ${className}`}
    >
      <div className="flex flex-col items-center justify-center p-16">
        {content}
      </div>
    </div>
  );
};

export default LoadingSpinner;
