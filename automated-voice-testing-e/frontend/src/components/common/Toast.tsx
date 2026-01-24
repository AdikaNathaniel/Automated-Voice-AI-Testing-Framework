/**
 * Toast Notification Component
 *
 * A lightweight toast notification system for showing success, error,
 * and info messages that auto-dismiss.
 */

import React, { useEffect, useState, useCallback, createContext, useContext } from 'react';
import { CheckCircle, XCircle, AlertCircle, Info, X } from 'lucide-react';

type ToastType = 'success' | 'error' | 'warning' | 'info';

interface Toast {
  id: string;
  type: ToastType;
  title: string;
  message?: string;
  duration?: number;
}

interface ToastContextType {
  showToast: (toast: Omit<Toast, 'id'>) => void;
  dismissToast: (id: string) => void;
}

const ToastContext = createContext<ToastContextType | null>(null);

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
};

const toastIcons: Record<ToastType, React.ReactNode> = {
  success: <CheckCircle className="w-5 h-5 text-[var(--color-status-success)]" />,
  error: <XCircle className="w-5 h-5 text-[var(--color-status-danger)]" />,
  warning: <AlertCircle className="w-5 h-5 text-[var(--color-status-warning)]" />,
  info: <Info className="w-5 h-5 text-[var(--color-status-info)]" />,
};

const toastStyles: Record<ToastType, string> = {
  success: 'bg-[var(--color-status-success-bg)] border-[var(--color-status-success)]',
  error: 'bg-[var(--color-status-danger-bg)] border-[var(--color-status-danger)]',
  warning: 'bg-[var(--color-status-warning-bg)] border-[var(--color-status-warning)]',
  info: 'bg-[var(--color-status-info-bg)] border-[var(--color-status-info)]',
};

const ToastItem: React.FC<{ toast: Toast; onDismiss: (id: string) => void }> = ({
  toast,
  onDismiss,
}) => {
  const [isExiting, setIsExiting] = useState(false);

  useEffect(() => {
    const duration = toast.duration ?? 4000;
    const exitTimer = setTimeout(() => setIsExiting(true), duration - 300);
    const removeTimer = setTimeout(() => onDismiss(toast.id), duration);

    return () => {
      clearTimeout(exitTimer);
      clearTimeout(removeTimer);
    };
  }, [toast.id, toast.duration, onDismiss]);

  return (
    <div
      className={`
        flex items-start gap-3 p-4 rounded-lg border shadow-lg
        transform transition-all duration-300 ease-out
        ${toastStyles[toast.type]}
        ${isExiting ? 'opacity-0 translate-x-4' : 'opacity-100 translate-x-0'}
      `}
    >
      <div className="flex-shrink-0 mt-0.5">{toastIcons[toast.type]}</div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-semibold text-[var(--color-content-primary)]">{toast.title}</p>
        {toast.message && (
          <p className="mt-1 text-sm text-[var(--color-content-secondary)]">{toast.message}</p>
        )}
      </div>
      <button
        onClick={() => onDismiss(toast.id)}
        className="flex-shrink-0 p-1 rounded-md hover:bg-black/5 transition-colors"
      >
        <X className="w-4 h-4 text-[var(--color-content-muted)]" />
      </button>
    </div>
  );
};

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const showToast = useCallback((toast: Omit<Toast, 'id'>) => {
    const id = `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    setToasts((prev) => [...prev, { ...toast, id }]);
  }, []);

  const dismissToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  return (
    <ToastContext.Provider value={{ showToast, dismissToast }}>
      {children}
      {/* Toast Container */}
      <div className="fixed top-4 right-4 z-50 flex flex-col gap-2 max-w-sm w-full pointer-events-none">
        {toasts.map((toast) => (
          <div key={toast.id} className="pointer-events-auto">
            <ToastItem toast={toast} onDismiss={dismissToast} />
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
};

export default ToastProvider;
