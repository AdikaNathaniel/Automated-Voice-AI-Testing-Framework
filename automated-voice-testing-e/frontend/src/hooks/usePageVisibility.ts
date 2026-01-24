/**
 * usePageVisibility Hook
 *
 * Tracks page visibility state to pause/resume polling when tab is hidden/visible.
 * Uses the Page Visibility API for efficient resource management.
 */

import { useState, useEffect, useCallback } from 'react';

interface UsePageVisibilityOptions {
  /** Callback when page becomes visible */
  onVisible?: () => void;
  /** Callback when page becomes hidden */
  onHidden?: () => void;
}

interface UsePageVisibilityReturn {
  /** Whether the page is currently visible */
  isVisible: boolean;
  /** Whether the document is in a hidden state */
  isHidden: boolean;
}

/**
 * Hook to track page visibility state
 *
 * @example
 * ```tsx
 * const { isVisible } = usePageVisibility({
 *   onVisible: () => refetch(),
 *   onHidden: () => pausePolling(),
 * });
 *
 * useEffect(() => {
 *   if (!isVisible) return;
 *   const interval = setInterval(fetchData, 30000);
 *   return () => clearInterval(interval);
 * }, [isVisible]);
 * ```
 */
export function usePageVisibility(
  options: UsePageVisibilityOptions = {}
): UsePageVisibilityReturn {
  const { onVisible, onHidden } = options;

  const [isVisible, setIsVisible] = useState(() => {
    // Handle SSR and test environments where document may not exist
    if (typeof document === 'undefined') return true;
    return document.visibilityState === 'visible';
  });

  const handleVisibilityChange = useCallback(() => {
    const visible = document.visibilityState === 'visible';
    setIsVisible(visible);

    if (visible) {
      onVisible?.();
    } else {
      onHidden?.();
    }
  }, [onVisible, onHidden]);

  useEffect(() => {
    // Handle environments without document (SSR, tests)
    if (typeof document === 'undefined') return;

    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [handleVisibilityChange]);

  return {
    isVisible,
    isHidden: !isVisible,
  };
}

/**
 * Hook that provides a polling interval that pauses when the page is hidden
 *
 * @example
 * ```tsx
 * useVisibilityPolling(fetchData, 30000); // Polls every 30s, pauses when hidden
 * ```
 */
export function useVisibilityPolling(
  callback: () => void,
  intervalMs: number,
  options: { enabled?: boolean; immediate?: boolean } = {}
): void {
  const { enabled = true, immediate = false } = options;
  const { isVisible } = usePageVisibility();

  useEffect(() => {
    if (!enabled || !isVisible) return;

    // Call immediately if requested
    if (immediate) {
      callback();
    }

    const interval = setInterval(callback, intervalMs);
    return () => clearInterval(interval);
  }, [callback, intervalMs, enabled, isVisible, immediate]);
}

export default usePageVisibility;
