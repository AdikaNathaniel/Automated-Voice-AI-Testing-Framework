/**
 * ErrorFallback Component
 *
 * Default fallback UI displayed when ErrorBoundary catches an error.
 * Provides a user-friendly error message and retry functionality.
 *
 * Features:
 * - Clean, centered error display
 * - Shows error message
 * - Retry button to reset error boundary
 * - Responsive design
 *
 * @example
 * ```tsx
 * <ErrorFallback
 *   error={new Error('Something went wrong')}
 *   resetErrorBoundary={() => window.location.reload()}
 * />
 * ```
 */

import React from 'react'
import { AlertCircle, RefreshCw } from 'lucide-react'

/**
 * Props for ErrorFallback component
 */
export interface ErrorFallbackProps {
  /** The error that was caught */
  error: Error
  /** Function to reset the error boundary */
  resetErrorBoundary: () => void
}

/**
 * Default fallback UI for error boundaries
 */
const ErrorFallback: React.FC<ErrorFallbackProps> = ({
  error,
  resetErrorBoundary,
}) => {
  return (
    <div className="max-w-2xl mx-auto">
      <div className="flex flex-col items-center justify-center min-h-[50vh] py-8">
        <div className="card text-center w-full">
          <AlertCircle
            className="w-16 h-16 text-[var(--color-status-danger)] mx-auto mb-4"
            aria-hidden="true"
          />

          <h1 className="text-2xl font-bold text-[var(--color-status-danger)] mb-3">
            Something went wrong
          </h1>

          <p className="text-base text-[var(--color-content-secondary)] mb-6">
            {error.message || 'An unexpected error occurred'}
          </p>

          <div className="bg-[var(--color-surface-inset)] p-4 rounded-lg mb-6 font-mono text-sm break-words text-left max-h-[150px] overflow-auto">
            <p className="text-xs text-[var(--color-content-muted)] mb-2">
              Error details:
            </p>
            <pre className="m-0 whitespace-pre-wrap text-[var(--color-content-primary)]">
              {error.message}
            </pre>
          </div>

          <button
            className="btn btn-primary"
            onClick={resetErrorBoundary}
            aria-label="Try again"
          >
            <RefreshCw className="w-4 h-4" aria-hidden="true" />
            Try again
          </button>

          <p className="text-xs text-[var(--color-content-muted)] mt-4 block">
            If the problem persists, please contact support.
          </p>
        </div>
      </div>
    </div>
  )
}

export default ErrorFallback
