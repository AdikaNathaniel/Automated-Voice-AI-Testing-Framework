/**
 * ErrorBoundary Component
 *
 * A React error boundary that catches JavaScript errors in child components,
 * logs them, and displays a fallback UI instead of crashing the whole app.
 *
 * Features:
 * - Catches render errors in child components
 * - Displays customizable fallback UI
 * - Supports error logging callbacks
 * - Provides reset functionality
 *
 * @example
 * ```tsx
 * <ErrorBoundary
 *   onError={(error, info) => logError(error, info)}
 *   onReset={() => clearCache()}
 * >
 *   <MyComponent />
 * </ErrorBoundary>
 * ```
 */

import React, { Component, ErrorInfo, ReactNode } from 'react'
import ErrorFallback from './ErrorFallback'

/**
 * Props for the fallback render function
 */
export interface FallbackProps {
  /** The error that was caught */
  error: Error
  /** Function to reset the error boundary */
  resetErrorBoundary: () => void
}

/**
 * Props for ErrorBoundary component
 */
export interface ErrorBoundaryProps {
  /** Child components to render */
  children: ReactNode
  /** Static fallback component to render on error */
  fallback?: ReactNode
  /** Render function for custom fallback with error info */
  fallbackRender?: (props: FallbackProps) => ReactNode
  /** Callback when error is caught */
  onError?: (error: Error, errorInfo: ErrorInfo) => void
  /** Callback when error boundary is reset */
  onReset?: () => void
}

/**
 * State for ErrorBoundary component
 */
interface ErrorBoundaryState {
  hasError: boolean
  error: Error | null
}

/**
 * Error boundary component for catching and handling React errors
 */
class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
    }
  }

  /**
   * Update state when an error is thrown
   */
  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return {
      hasError: true,
      error,
    }
  }

  /**
   * Log error information when caught
   */
  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    const { onError } = this.props

    // Call onError callback if provided
    if (onError) {
      onError(error, errorInfo)
    }

    // Log to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error('ErrorBoundary caught an error:', error, errorInfo)
    }
  }

  /**
   * Reset the error boundary state
   */
  resetErrorBoundary = (): void => {
    const { onReset } = this.props

    // Call onReset callback if provided
    if (onReset) {
      onReset()
    }

    // Reset state
    this.setState({
      hasError: false,
      error: null,
    })
  }

  render(): ReactNode {
    const { hasError, error } = this.state
    const { children, fallback, fallbackRender } = this.props

    // If there's an error, render fallback UI
    if (hasError && error) {
      // Use custom fallback render function if provided
      if (fallbackRender) {
        return fallbackRender({
          error,
          resetErrorBoundary: this.resetErrorBoundary,
        })
      }

      // Use static fallback component if provided
      if (fallback) {
        return fallback
      }

      // Use default ErrorFallback component
      return (
        <ErrorFallback
          error={error}
          resetErrorBoundary={this.resetErrorBoundary}
        />
      )
    }

    // No error, render children normally
    return children
  }
}

export default ErrorBoundary
