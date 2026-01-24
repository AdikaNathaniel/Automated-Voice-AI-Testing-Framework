/**
 * ErrorBoundary Component Tests
 *
 * Tests for ErrorBoundary component error catching and fallback rendering.
 * Tests cover:
 *  - Rendering children when no error
 *  - Catching errors from child components
 *  - Rendering fallback UI on error
 *  - Reset functionality
 *  - Error logging callback
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import ErrorBoundary from '../ErrorBoundary'

// Component that throws an error for testing
const ThrowError = ({ shouldThrow = true }: { shouldThrow?: boolean }) => {
  if (shouldThrow) {
    throw new Error('Test error message')
  }
  return <div>No error thrown</div>
}

// Suppress console.error for cleaner test output
const originalError = console.error
beforeEach(() => {
  console.error = vi.fn()
})

afterEach(() => {
  console.error = originalError
})

describe('ErrorBoundary Component', () => {
  // ========== Basic Rendering Tests ==========
  describe('Basic Rendering', () => {
    it('should render children when there is no error', () => {
      render(
        <ErrorBoundary>
          <div>Child content</div>
        </ErrorBoundary>
      )

      expect(screen.getByText('Child content')).toBeInTheDocument()
    })

    it('should render multiple children', () => {
      render(
        <ErrorBoundary>
          <div>First child</div>
          <div>Second child</div>
        </ErrorBoundary>
      )

      expect(screen.getByText('First child')).toBeInTheDocument()
      expect(screen.getByText('Second child')).toBeInTheDocument()
    })
  })

  // ========== Error Catching Tests ==========
  describe('Error Catching', () => {
    it('should catch errors from child components', () => {
      render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>
      )

      // Should not render the child that threw
      expect(screen.queryByText('No error thrown')).not.toBeInTheDocument()
    })

    it('should render fallback UI when error is caught', () => {
      render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>
      )

      // Should show error fallback
      expect(screen.getByText(/something went wrong/i)).toBeInTheDocument()
    })

    it('should display error message in fallback', () => {
      render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>
      )

      // Should show the error message (appears in multiple places)
      const errorMessages = screen.getAllByText(/test error message/i)
      expect(errorMessages.length).toBeGreaterThan(0)
    })
  })

  // ========== Custom Fallback Tests ==========
  describe('Custom Fallback', () => {
    it('should render custom fallback component when provided', () => {
      const CustomFallback = () => <div>Custom error UI</div>

      render(
        <ErrorBoundary fallback={<CustomFallback />}>
          <ThrowError />
        </ErrorBoundary>
      )

      expect(screen.getByText('Custom error UI')).toBeInTheDocument()
    })

    it('should pass error to custom fallback render prop', () => {
      render(
        <ErrorBoundary
          fallbackRender={({ error }) => (
            <div>Error: {error.message}</div>
          )}
        >
          <ThrowError />
        </ErrorBoundary>
      )

      expect(screen.getByText('Error: Test error message')).toBeInTheDocument()
    })
  })

  // ========== Reset Functionality Tests ==========
  describe('Reset Functionality', () => {
    it('should provide reset button in fallback UI', () => {
      render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>
      )

      expect(screen.getByRole('button', { name: /try again/i })).toBeInTheDocument()
    })

    it('should call onReset when reset button is clicked', () => {
      const onReset = vi.fn()

      render(
        <ErrorBoundary onReset={onReset}>
          <ThrowError />
        </ErrorBoundary>
      )

      fireEvent.click(screen.getByRole('button', { name: /try again/i }))
      expect(onReset).toHaveBeenCalledTimes(1)
    })

    it('should pass resetErrorBoundary to fallbackRender', () => {
      const onReset = vi.fn()

      render(
        <ErrorBoundary
          onReset={onReset}
          fallbackRender={({ resetErrorBoundary }) => (
            <button onClick={resetErrorBoundary}>Reset</button>
          )}
        >
          <ThrowError />
        </ErrorBoundary>
      )

      fireEvent.click(screen.getByRole('button', { name: /reset/i }))
      expect(onReset).toHaveBeenCalledTimes(1)
    })
  })

  // ========== Error Logging Tests ==========
  describe('Error Logging', () => {
    it('should call onError callback when error is caught', () => {
      const onError = vi.fn()

      render(
        <ErrorBoundary onError={onError}>
          <ThrowError />
        </ErrorBoundary>
      )

      expect(onError).toHaveBeenCalledTimes(1)
      expect(onError).toHaveBeenCalledWith(
        expect.any(Error),
        expect.objectContaining({
          componentStack: expect.any(String)
        })
      )
    })

    it('should pass error with correct message to onError', () => {
      const onError = vi.fn()

      render(
        <ErrorBoundary onError={onError}>
          <ThrowError />
        </ErrorBoundary>
      )

      const [error] = onError.mock.calls[0]
      expect(error.message).toBe('Test error message')
    })
  })
})
