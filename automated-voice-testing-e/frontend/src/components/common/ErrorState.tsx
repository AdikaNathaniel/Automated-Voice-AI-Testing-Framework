/**
 * ErrorState Component
 *
 * Standardized error display with icon, message, and optional retry button.
 * Uses semantic tokens for consistent theming across light/dark/oled.
 * Supports full-page, card, and alert variants.
 */

import React from 'react';
import { XCircle, AlertTriangle, RefreshCw } from 'lucide-react';

type ErrorVariant = 'page' | 'card' | 'alert';

interface ErrorStateProps {
  title?: string;
  message: string;
  onRetry?: () => void;
  retryLoading?: boolean;
  variant?: ErrorVariant;
  className?: string;
}

const ErrorState: React.FC<ErrorStateProps> = ({
  title = 'Something went wrong',
  message,
  onRetry,
  retryLoading = false,
  variant = 'card',
  className = '',
}) => {
  if (variant === 'alert') {
    return (
      <div
        className={`p-4 rounded-xl flex items-center gap-3 border-l-4 ${className}`}
        style={{
          background: 'var(--color-status-danger-bg)',
          borderLeftColor: 'var(--color-status-danger)',
        }}
        role="alert"
      >
        <AlertTriangle
          className="w-5 h-5 flex-shrink-0 text-[var(--color-status-danger)]"
          aria-hidden="true"
        />
        <div className="flex-1">
          <p className="font-semibold text-[var(--color-status-danger)]">{message}</p>
        </div>
        {onRetry && (
          <button
            onClick={onRetry}
            disabled={retryLoading}
            className="p-2 rounded-lg transition-colors disabled:opacity-50 hover:bg-[var(--color-interactive-hover)]"
            aria-label="Retry"
          >
            <RefreshCw
              className={`w-4 h-4 text-[var(--color-status-danger)] ${retryLoading ? 'animate-spin' : ''}`}
              aria-hidden="true"
            />
          </button>
        )}
      </div>
    );
  }

  const content = (
    <div className="text-center">
      <div
        className="w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-6"
        style={{ background: 'var(--color-status-danger-bg)' }}
      >
        <XCircle
          className="w-8 h-8 text-[var(--color-status-danger)]"
          aria-hidden="true"
        />
      </div>
      <h2 className="text-xl font-semibold text-[var(--color-content-primary)] mb-2">
        {title}
      </h2>
      <p className="text-[var(--color-content-secondary)] mb-6 max-w-md mx-auto">
        {message}
      </p>
      {onRetry && (
        <button
          onClick={onRetry}
          disabled={retryLoading}
          className="btn-primary inline-flex items-center gap-2 disabled:opacity-50"
        >
          <RefreshCw
            className={`w-4 h-4 ${retryLoading ? 'animate-spin' : ''}`}
            aria-hidden="true"
          />
          <span>Retry</span>
        </button>
      )}
    </div>
  );

  if (variant === 'page') {
    return (
      <div
        className={`min-h-screen flex items-center justify-center ${className}`}
        style={{ background: 'var(--color-surface-base)' }}
        role="alert"
      >
        {content}
      </div>
    );
  }

  // variant === 'card'
  return (
    <div className={`card-static ${className}`} role="alert">
      <div className="flex flex-col items-center justify-center py-12">
        {content}
      </div>
    </div>
  );
};

export default ErrorState;
