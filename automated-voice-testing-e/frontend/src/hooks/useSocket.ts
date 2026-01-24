/**
 * useSocket Hook
 *
 * React hook for managing Socket.IO connections and subscriptions.
 * Provides a clean interface for components to subscribe to real-time events.
 *
 * Features:
 * - Auto-connect on mount (if not already connected)
 * - Auto-cleanup on unmount
 * - Subscribe/unsubscribe to events with React lifecycle
 * - Connection status tracking
 * - Emit events to server
 *
 * @example
 * ```tsx
 * function SuiteRunDetail() {
 *   const { isConnected, on, off, emit } = useSocket();
 *
 *   useEffect(() => {
 *     const handler = (data) => {
 *       console.log('Suite run update:', data);
 *     };
 *
 *     on('suite_run_update', handler);
 *     return () => off('suite_run_update', handler);
 *   }, [on, off]);
 *
 *   return <div>Connected: {isConnected ? 'Yes' : 'No'}</div>;
 * }
 * ```
 */

import { useEffect, useState, useCallback } from 'react';
import websocketService from '../services/websocket.service';

/**
 * Event handler function type
 */
type EventHandler = (data: unknown) => void;

/**
 * useSocket hook return type
 */
interface UseSocketReturn {
  /**
   * Whether the socket is currently connected
   */
  isConnected: boolean;

  /**
   * Subscribe to a socket event
   * @param event - Event name
   * @param handler - Event handler function
   */
  on: (event: string, handler: EventHandler) => void;

  /**
   * Unsubscribe from a socket event
   * @param event - Event name
   * @param handler - Event handler function (optional)
   */
  off: (event: string, handler?: EventHandler) => void;

  /**
   * Emit an event to the server
   * @param event - Event name
   * @param data - Event data
   */
  emit: (event: string, data: unknown) => void;

  /**
   * Subscribe to a specific suite run's updates
   * @param suiteRunId - Suite run ID to subscribe to
   */
  subscribeToSuiteRun: (suiteRunId: string) => void;
}

/**
 * useSocket hook
 *
 * Manages Socket.IO connection and provides event subscription interface.
 *
 * @returns Socket connection interface
 */
export function useSocket(): UseSocketReturn {
  const [isConnected, setIsConnected] = useState(websocketService.isConnected());

  // Connect on mount if not already connected
  useEffect(() => {
    if (!websocketService.isConnected()) {
      websocketService.connect().catch((error) => {
        console.error('[useSocket] Failed to connect:', error);
      });
    }

    // Set up connection status listener
    const handleConnect = () => {
      setIsConnected(true);
      console.log('[useSocket] Socket connected');
    };

    const handleDisconnect = () => {
      setIsConnected(false);
      console.log('[useSocket] Socket disconnected');
    };

    websocketService.on('connect', handleConnect);
    websocketService.on('disconnect', handleDisconnect);

    // Update initial state
    setIsConnected(websocketService.isConnected());

    return () => {
      websocketService.off('connect', handleConnect);
      websocketService.off('disconnect', handleDisconnect);
    };
  }, []);

  // Subscribe to event
  const on = useCallback((event: string, handler: EventHandler) => {
    websocketService.on(event, handler);
  }, []);

  // Unsubscribe from event
  const off = useCallback((event: string, handler?: EventHandler) => {
    websocketService.off(event, handler);
  }, []);

  // Emit event
  const emit = useCallback((event: string, data: unknown) => {
    websocketService.emit(event, data);
  }, []);

  // Subscribe to suite run updates
  const subscribeToSuiteRun = useCallback((suiteRunId: string) => {
    websocketService.emit('subscribe_suite_run', { suite_run_id: suiteRunId });
    console.log(`[useSocket] Subscribed to suite run: ${suiteRunId}`);
  }, []);

  return {
    isConnected,
    on,
    off,
    emit,
    subscribeToSuiteRun,
  };
}

export default useSocket;

