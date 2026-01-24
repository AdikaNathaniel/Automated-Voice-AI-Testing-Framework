/**
 * ActivationToggle component.
 *
 * Provides an activation/deactivation button with confirmation modal.
 */

import React, { useState } from 'react';
import { AlertCircle, X } from 'lucide-react';

type ActivationToggleProps = {
  isActive: boolean;
  onToggle: (nextState: boolean) => Promise<void> | void;
  configurationName?: string;
};

const ActivationToggle: React.FC<ActivationToggleProps> = ({
  isActive,
  onToggle,
  configurationName,
}) => {
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleOpen = () => {
    setError(null);
    setConfirmOpen(true);
  };

  const handleClose = () => {
    if (!loading) {
      setConfirmOpen(false);
    }
  };

  const handleConfirm = async () => {
    if (loading) {
      return;
    }
    try {
      setLoading(true);
      setError(null);
      await onToggle(!isActive);
      setConfirmOpen(false);
    } catch (err: unknown) {
      const detail = err?.message;
      setError(detail ? `Failed to update configuration status. ${detail}` : 'Failed to update configuration status.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <button
        className={isActive ? 'btn border border-[var(--color-status-warning)] text-[var(--color-status-warning)] hover:bg-[var(--color-status-warning-bg)]' : 'btn bg-[var(--color-status-success)] text-[var(--color-content-inverse)] hover:opacity-90'}
        onClick={handleOpen}
        data-testid="activation-toggle-button"
      >
        {isActive ? 'Deactivate' : 'Activate'}
      </button>

      {confirmOpen && (
        <div className="modal">
          <div className="modal-content max-w-md">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold" id="activation-dialog-title">
                {isActive ? 'Deactivate configuration?' : 'Activate configuration?'}
              </h2>
              <button
                onClick={handleClose}
                disabled={loading}
                className="p-1 hover:bg-[var(--color-interactive-hover)] rounded"
                aria-label="Close"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4 mb-6">
              <p className="text-[var(--color-content-secondary)]">
                Are you sure you want to {isActive ? 'deactivate' : 'activate'}{' '}
                {configurationName ?? 'this configuration'}?
              </p>
              {error && (
                <div className="bg-[var(--color-status-danger-bg)] border border-[var(--color-status-danger)] text-[var(--color-status-danger)] px-4 py-3 rounded flex items-start gap-2">
                  <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                  <span>{error}</span>
                </div>
              )}
            </div>

            <div className="flex justify-end gap-2">
              <button
                onClick={handleClose}
                disabled={loading}
                className="btn"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirm}
                className={isActive ? 'btn bg-[var(--color-status-warning)] text-[var(--color-content-inverse)] hover:opacity-90' : 'btn-primary'}
                disabled={loading}
                data-testid="activation-confirm-button"
              >
                {loading ? 'Saving…' : 'Confirm'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ActivationToggle;
