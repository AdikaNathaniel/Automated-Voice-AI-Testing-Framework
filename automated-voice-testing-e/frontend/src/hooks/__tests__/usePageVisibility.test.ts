/**
 * usePageVisibility hook tests
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { usePageVisibility, useVisibilityPolling } from '../usePageVisibility';

describe('usePageVisibility', () => {
  let originalVisibilityState: PropertyDescriptor | undefined;
  let visibilityChangeListeners: Array<() => void> = [];

  beforeEach(() => {
    visibilityChangeListeners = [];
    originalVisibilityState = Object.getOwnPropertyDescriptor(
      document,
      'visibilityState'
    );

    // Mock addEventListener to capture listeners
    vi.spyOn(document, 'addEventListener').mockImplementation(
      (event, handler) => {
        if (event === 'visibilitychange') {
          visibilityChangeListeners.push(handler as () => void);
        }
      }
    );

    vi.spyOn(document, 'removeEventListener').mockImplementation(
      (event, handler) => {
        if (event === 'visibilitychange') {
          visibilityChangeListeners = visibilityChangeListeners.filter(
            (h) => h !== handler
          );
        }
      }
    );
  });

  afterEach(() => {
    vi.restoreAllMocks();
    if (originalVisibilityState) {
      Object.defineProperty(document, 'visibilityState', originalVisibilityState);
    }
  });

  const setVisibilityState = (state: 'visible' | 'hidden') => {
    Object.defineProperty(document, 'visibilityState', {
      value: state,
      configurable: true,
    });
    // Trigger all listeners
    visibilityChangeListeners.forEach((listener) => listener());
  };

  it('returns isVisible true when document is visible', () => {
    Object.defineProperty(document, 'visibilityState', {
      value: 'visible',
      configurable: true,
    });

    const { result } = renderHook(() => usePageVisibility());
    expect(result.current.isVisible).toBe(true);
    expect(result.current.isHidden).toBe(false);
  });

  it('returns isVisible false when document is hidden', () => {
    Object.defineProperty(document, 'visibilityState', {
      value: 'hidden',
      configurable: true,
    });

    const { result } = renderHook(() => usePageVisibility());
    expect(result.current.isVisible).toBe(false);
    expect(result.current.isHidden).toBe(true);
  });

  it('calls onVisible callback when page becomes visible', () => {
    Object.defineProperty(document, 'visibilityState', {
      value: 'hidden',
      configurable: true,
    });

    const onVisible = vi.fn();
    const onHidden = vi.fn();

    renderHook(() => usePageVisibility({ onVisible, onHidden }));

    act(() => {
      setVisibilityState('visible');
    });

    expect(onVisible).toHaveBeenCalledTimes(1);
    expect(onHidden).not.toHaveBeenCalled();
  });

  it('calls onHidden callback when page becomes hidden', () => {
    Object.defineProperty(document, 'visibilityState', {
      value: 'visible',
      configurable: true,
    });

    const onVisible = vi.fn();
    const onHidden = vi.fn();

    renderHook(() => usePageVisibility({ onVisible, onHidden }));

    act(() => {
      setVisibilityState('hidden');
    });

    expect(onHidden).toHaveBeenCalledTimes(1);
    expect(onVisible).not.toHaveBeenCalled();
  });

  it('updates isVisible when visibility changes', () => {
    Object.defineProperty(document, 'visibilityState', {
      value: 'visible',
      configurable: true,
    });

    const { result } = renderHook(() => usePageVisibility());
    expect(result.current.isVisible).toBe(true);

    act(() => {
      setVisibilityState('hidden');
    });

    expect(result.current.isVisible).toBe(false);

    act(() => {
      setVisibilityState('visible');
    });

    expect(result.current.isVisible).toBe(true);
  });

  it('cleans up event listener on unmount', () => {
    Object.defineProperty(document, 'visibilityState', {
      value: 'visible',
      configurable: true,
    });

    const { unmount } = renderHook(() => usePageVisibility());
    expect(visibilityChangeListeners.length).toBe(1);

    unmount();
    expect(visibilityChangeListeners.length).toBe(0);
  });
});

describe('useVisibilityPolling', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    Object.defineProperty(document, 'visibilityState', {
      value: 'visible',
      configurable: true,
    });
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.restoreAllMocks();
  });

  it('calls callback at specified interval when visible', () => {
    const callback = vi.fn();

    renderHook(() => useVisibilityPolling(callback, 1000));

    expect(callback).not.toHaveBeenCalled();

    vi.advanceTimersByTime(1000);
    expect(callback).toHaveBeenCalledTimes(1);

    vi.advanceTimersByTime(1000);
    expect(callback).toHaveBeenCalledTimes(2);
  });

  it('calls callback immediately when immediate option is true', () => {
    const callback = vi.fn();

    renderHook(() => useVisibilityPolling(callback, 1000, { immediate: true }));

    expect(callback).toHaveBeenCalledTimes(1);
  });

  it('does not call callback when enabled is false', () => {
    const callback = vi.fn();

    renderHook(() => useVisibilityPolling(callback, 1000, { enabled: false }));

    vi.advanceTimersByTime(5000);
    expect(callback).not.toHaveBeenCalled();
  });

  it('clears interval on unmount', () => {
    const callback = vi.fn();

    const { unmount } = renderHook(() => useVisibilityPolling(callback, 1000));

    vi.advanceTimersByTime(1000);
    expect(callback).toHaveBeenCalledTimes(1);

    unmount();

    vi.advanceTimersByTime(5000);
    expect(callback).toHaveBeenCalledTimes(1); // No additional calls after unmount
  });
});
