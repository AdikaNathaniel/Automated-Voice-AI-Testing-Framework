/**
 * WebSocket Service (TASK-138)
 *
 * Manages WebSocket connections for real-time updates:
 * - Connect on user login
 * - Subscribe to suite run updates
 * - Emit events to Redux store
 * - Handle connection lifecycle
 *
 * Features:
 * - Socket.io-client integration
 * - Automatic reconnection
 * - Event subscription management
 * - Redux store integration
 * - TypeScript type safety
 */

import { io, Socket } from 'socket.io-client';
import { store } from '../store';

/**
 * WebSocket message types
 */
export interface SuiteRunUpdateMessage {
  /**
   * Suite run ID
   */
  suiteRunId: number;

  /**
   * Update type
   */
  type: 'status' | 'progress' | 'result';

  /**
   * Update data
   */
  data: unknown;
}

/**
 * WebSocket connection options
 */
interface ConnectionOptions {
  /**
   * Authentication token
   */
  token?: string;

  /**
   * Auto-reconnect on disconnect
   */
  autoReconnect?: boolean;
}

/**
 * WebSocket service class
 */
class WebSocketService {
  /**
   * Socket.io client instance
   */
  private socket: Socket | null = null;

  /**
   * Connection status
   */
  private connected = false;

  /**
   * WebSocket server URL
   */
  private readonly serverUrl: string;

  /**
   * Initialize WebSocket service
   */
  constructor() {
    // Use environment variable or default to localhost
    this.serverUrl = import.meta.env.VITE_WS_URL || 'http://localhost:8000';
  }

  /**
   * Connect to WebSocket server
   *
   * Called on user login to establish real-time connection.
   *
   * @param options - Connection options
   * @returns Promise that resolves when connected
   *
   * @example
   * ```typescript
   * await websocketService.connect({ token: userToken });
   * ```
   */
  async connect(options: ConnectionOptions = {}): Promise<void> {
    try {
      // Disconnect existing connection
      if (this.socket) {
        this.disconnect();
      }

      // Create new socket connection
      this.socket = io(this.serverUrl, {
        auth: {
          token: options.token,
        },
        autoConnect: true,
        reconnection: options.autoReconnect ?? true,
        reconnectionDelay: 1000,
        reconnectionAttempts: 5,
      });

      // Set up connection event handlers
      this.setupEventHandlers();

      // Wait for connection
      return new Promise((resolve, reject) => {
        if (!this.socket) {
          reject(new Error('Socket not initialized'));
          return;
        }

        this.socket.on('connect', () => {
          this.connected = true;
          console.log('WebSocket connected');
          resolve();
        });

        this.socket.on('connect_error', (error) => {
          console.error('WebSocket connection error:', error);
          reject(error);
        });
      });
    } catch (error) {
      console.error('Failed to connect to WebSocket:', error);
      throw error;
    }
  }

  /**
   * Disconnect from WebSocket server
   *
   * Clean up connection and remove event listeners.
   *
   * @example
   * ```typescript
   * websocketService.disconnect();
   * ```
   */
  disconnect(): void {
    try {
      if (this.socket) {
        this.socket.removeAllListeners();
        this.socket.disconnect();
        this.socket = null;
        this.connected = false;
        console.log('WebSocket disconnected');
      }
    } catch (error) {
      console.error('Error disconnecting WebSocket:', error);
    }
  }

  /**
   * Set up WebSocket event handlers
   *
   * Handles connection lifecycle and incoming messages.
   */
  private setupEventHandlers(): void {
    if (!this.socket) return;

    // Connection events
    this.socket.on('disconnect', () => {
      this.connected = false;
      console.log('WebSocket disconnected');
    });

    this.socket.on('error', (error) => {
      console.error('WebSocket error:', error);
    });

    // Subscribe to suite run updates
    this.subscribeToSuiteRunUpdates();
  }

  /**
   * Subscribe to suite run updates
   *
   * Listen for real-time suite run status, progress, and results.
   * Dispatches updates to Redux store.
   */
  private subscribeToSuiteRunUpdates(): void {
    if (!this.socket) return;

    // Subscribe to suite run update events
    this.socket.on('suite_run:update', (message: SuiteRunUpdateMessage) => {
      try {
        console.log('Suite run update received:', message);

        // Dispatch to Redux store
        store.dispatch({
          type: 'suiteRuns/updateReceived',
          payload: message,
        });
      } catch (error) {
        console.error('Error handling suite run update:', error);
      }
    });

    // Subscribe to test execution updates
    this.socket.on('test_execution:update', (message: unknown) => {
      try {
        console.log('Test execution update received:', message);

        // Dispatch to Redux store
        store.dispatch({
          type: 'testExecutions/updateReceived',
          payload: message,
        });
      } catch (error) {
        console.error('Error handling test execution update:', error);
      }
    });
  }

  /**
   * Subscribe to custom event
   *
   * @param event - Event name
   * @param callback - Event handler
   *
   * @example
   * ```typescript
   * websocketService.on('custom_event', (data) => {
   *   console.log('Custom event:', data);
   * });
   * ```
   */
  on(event: string, callback: (data: unknown) => void): void {
    if (!this.socket) {
      console.warn('Cannot subscribe: WebSocket not connected');
      return;
    }

    this.socket.on(event, callback);
  }

  /**
   * Unsubscribe from event
   *
   * @param event - Event name
   * @param callback - Event handler to remove (optional)
   */
  off(event: string, callback?: (data: unknown) => void): void {
    if (!this.socket) return;

    if (callback) {
      this.socket.off(event, callback);
    } else {
      this.socket.off(event);
    }
  }

  /**
   * Emit event to server
   *
   * @param event - Event name
   * @param data - Event data
   *
   * @example
   * ```typescript
   * websocketService.emit('suite_run:start', { suiteRunId: 123 });
   * ```
   */
  emit(event: string, data: unknown): void {
    if (!this.socket || !this.connected) {
      console.warn('Cannot emit: WebSocket not connected');
      return;
    }

    this.socket.emit(event, data);
  }

  /**
   * Check if connected
   *
   * @returns True if connected to WebSocket server
   */
  isConnected(): boolean {
    return this.connected;
  }
}

/**
 * WebSocket service singleton instance
 */
export const websocketService = new WebSocketService();

/**
 * Default export
 */
export default websocketService;
