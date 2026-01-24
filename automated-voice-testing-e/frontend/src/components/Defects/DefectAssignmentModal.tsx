/**
 * DefectAssignmentModal
 *
 * Modal dialog used to adjust the assignee and status of a defect while
 * optionally leaving an operator comment. Designed to integrate with the
 * defects workflow pages.
 */

import React, { useEffect } from 'react';
import { X } from 'lucide-react';
import { useForm } from 'react-hook-form';

export interface DefectAssignmentFormValues {
  assignee: string;
  status: string;
  comment: string | null;
}

interface RawFormValues {
  assignee: string;
  status: string;
  comment: string;
}

export interface StatusOption {
  value: string;
  label: string;
}

export interface DefectAssignmentModalProps {
  open: boolean;
  defectTitle: string;
  assignees: string[];
  statuses: StatusOption[];
  currentAssignee?: string | null;
  currentStatus?: string | null;
  onClose: () => void;
  onSubmit: (values: DefectAssignmentFormValues) => void | Promise<void>;
  submitting?: boolean;
  error?: string | null;
}

const emptyToNull = (value: string): string | null => {
  const trimmed = value.trim();
  return trimmed.length ? trimmed : null;
};

const trimOrEmpty = (value?: string | null): string => (value ? value.trim() : '');

const normalize = (values: RawFormValues): DefectAssignmentFormValues => ({
  assignee: values.assignee.trim(),
  status: values.status.trim(),
  comment: emptyToNull(values.comment),
});

const DefectAssignmentModal: React.FC<DefectAssignmentModalProps> = ({
  open,
  defectTitle,
  assignees,
  statuses,
  currentAssignee,
  currentStatus,
  onClose,
  onSubmit,
  submitting = false,
  error = null,
}) => {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<RawFormValues>({
    defaultValues: {
      assignee: trimOrEmpty(currentAssignee),
      status: trimOrEmpty(currentStatus),
      comment: '',
    },
  });

  useEffect(() => {
    if (open) {
      reset({
        assignee: trimOrEmpty(currentAssignee),
        status: trimOrEmpty(currentStatus),
        comment: '',
      });
    }
  }, [open, currentAssignee, currentStatus, reset]);

  const onFormSubmit = async (values: RawFormValues) => {
    const normalized = normalize(values);
    await onSubmit(normalized);
  };

  const busy = submitting || isSubmitting;

  if (!open) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal max-w-lg" onClick={(e) => e.stopPropagation()} aria-labelledby="defect-assign-title">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <h3 id="defect-assign-title" className="text-lg font-semibold">
            Update assignment for {defectTitle}
          </h3>
          <button
            type="button"
            onClick={onClose}
            className="text-[var(--color-content-muted)] hover:text-[var(--color-content-secondary)] transition-colors"
            aria-label="Close modal"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <form id="defect-assignment-form" onSubmit={handleSubmit(onFormSubmit)} noValidate>
          <div className="space-y-4">
            <p className="text-sm text-[var(--color-content-secondary)]">
              Adjust assignment for <strong>{defectTitle}</strong>. Choose the teammate responsible and
              update the defect status.
            </p>

            {error && (
              <p role="alert" className="text-sm text-[var(--color-status-danger)]" data-testid="defect-assignment-error">
                {error}
              </p>
            )}

            <div>
              <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1">
                Assign To <span className="text-[var(--color-status-danger)]">*</span>
              </label>
              <select
                {...register('assignee', {
                  required: 'Assignee is required',
                  validate: (value) => value.trim().length > 0 || 'Assignee is required',
                })}
                className={`filter-select ${errors.assignee ? 'border-[var(--color-status-danger)]' : ''}`}
              >
                <option value="">Select team member</option>
                {assignees.map((member) => (
                  <option key={member} value={member}>
                    {member}
                  </option>
                ))}
              </select>
              {errors.assignee && (
                <p className="mt-1 text-sm text-[var(--color-status-danger)]">{errors.assignee.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1">
                Status <span className="text-[var(--color-status-danger)]">*</span>
              </label>
              <select
                {...register('status', {
                  required: 'Status is required',
                  validate: (value) => value.trim().length > 0 || 'Status is required',
                })}
                className={`filter-select ${errors.status ? 'border-[var(--color-status-danger)]' : ''}`}
              >
                <option value="">Select status</option>
                {statuses.map((status) => (
                  <option key={status.value} value={status.value}>
                    {status.label}
                  </option>
                ))}
              </select>
              {errors.status && (
                <p className="mt-1 text-sm text-[var(--color-status-danger)]">{errors.status.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1">
                Comment
              </label>
              <textarea
                rows={3}
                placeholder="Provide optional context for the new assignee."
                {...register('comment')}
                className="w-full px-3 py-2 border border-[var(--color-border-default)] rounded-md focus:border-[var(--color-status-info)] focus:ring-1 focus:ring-[var(--color-status-info)] resize-y bg-[var(--color-surface-raised)] text-[var(--color-content-primary)]"
              />
            </div>
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-3 mt-6 pt-4 border-t">
            <button
              type="button"
              onClick={onClose}
              disabled={busy}
              className="btn btn-secondary"
            >
              Cancel
            </button>
            <button type="submit" disabled={busy} className="btn">
              Save Assignment
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default DefectAssignmentModal;
