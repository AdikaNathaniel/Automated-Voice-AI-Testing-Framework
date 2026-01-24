import React, { useEffect } from 'react';
import { X, AlertCircle, CheckCircle, Info, AlertTriangle } from 'lucide-react';

export type ModalType = 'info' | 'success' | 'warning' | 'error' | 'confirm';

export interface ModalState {
  isOpen: boolean;
  type: ModalType;
  title?: string;
  message: string;
  onConfirm?: () => void;
  confirmText?: string;
  cancelText?: string;
  showCancel?: boolean;
}

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm?: () => void;
  title?: string;
  message: string;
  type?: ModalType;
  confirmText?: string;
  cancelText?: string;
  showCancel?: boolean;
}

const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  type = 'info',
  confirmText = 'OK',
  cancelText = 'Cancel',
  showCancel = false,
}) => {
  // Close on Escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      // Prevent body scroll when modal is open
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const getIcon = () => {
    switch (type) {
      case 'success':
        return <CheckCircle className="w-12 h-12 text-[var(--color-status-success)]" />;
      case 'error':
        return <AlertCircle className="w-12 h-12 text-[var(--color-status-danger)]" />;
      case 'warning':
        return <AlertTriangle className="w-12 h-12 text-[var(--color-status-warning)]" />;
      case 'confirm':
        return <AlertCircle className="w-12 h-12 text-[var(--color-brand-primary)]" />;
      default:
        return <Info className="w-12 h-12 text-[var(--color-status-info)]" />;
    }
  };

  const getTitle = () => {
    if (title) return title;
    switch (type) {
      case 'success':
        return 'Success';
      case 'error':
        return 'Error';
      case 'warning':
        return 'Warning';
      case 'confirm':
        return 'Confirm Action';
      default:
        return 'Information';
    }
  };

  const handleConfirm = () => {
    if (onConfirm) {
      onConfirm();
    }
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50 transition-opacity"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative bg-[var(--color-surface-overlay)] rounded-xl shadow-2xl max-w-md w-full mx-4 transform transition-all">
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-[var(--color-content-muted)] hover:text-[var(--color-content-secondary)] transition-colors"
          aria-label="Close"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Content */}
        <div className="p-6">
          {/* Icon */}
          <div className="flex justify-center mb-4">{getIcon()}</div>

          {/* Title */}
          <h3 className="text-xl font-semibold text-[var(--color-content-primary)] text-center mb-3">
            {getTitle()}
          </h3>

          {/* Message */}
          <p className="text-[var(--color-content-secondary)] text-center mb-6 whitespace-pre-line">
            {message}
          </p>

          {/* Actions */}
          <div className="flex gap-3 justify-center">
            {showCancel && (
              <button
                onClick={onClose}
                className="px-6 py-2 bg-[var(--color-surface-inset)] text-[var(--color-content-secondary)] rounded-lg hover:bg-[var(--color-interactive-hover)] transition-colors font-medium"
              >
                {cancelText}
              </button>
            )}
            <button
              onClick={handleConfirm}
              className="px-6 py-2 rounded-lg font-medium transition-all"
              style={{
                background: type === 'error' ? '#EF4444' : 'linear-gradient(135deg, #2A6B6E 0%, #11484D 100%)',
                color: 'white',
              }}
            >
              {confirmText}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Modal;
export type { ModalType, ModalState, ModalProps };

