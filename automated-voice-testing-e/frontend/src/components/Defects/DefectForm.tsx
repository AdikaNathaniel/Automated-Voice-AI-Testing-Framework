/**
 * DefectForm component
 *
 * Provides a reusable form for creating and editing defects manually. The form
 * captures the key metadata required by downstream services (severity,
 * category, status, linkage to test artefacts, and optional ownership details).
 */

import React from 'react';
import { useForm } from 'react-hook-form';

/**
 * Normalised values returned to calling components when the form is submitted.
 */
export interface DefectFormValues {
  title: string;
  severity: string;
  category: string;
  status: string;
  scriptId: string | null;
  executionId: string | null;
  languageCode: string | null;
  assignedTo: string | null;
  description: string | null;
}

/**
 * Internal raw form state used by react-hook-form. Optional fields remain
 * string-based so they can bind to text inputs without coercing to null.
 */
interface RawDefectFormValues {
  title: string;
  severity: string;
  category: string;
  status: string;
  scriptId: string;
  executionId: string;
  languageCode: string;
  assignedTo: string;
  description: string;
}

export interface DefectFormProps {
  /**
   * Form mode to adjust copy and behaviour.
   */
  mode?: 'create' | 'edit';
  /**
   * Initial field values (typically when editing an existing defect).
   */
  initialValues?: Partial<DefectFormValues>;
  /**
   * Submit handler invoked with sanitised values.
   */
  onSubmit: (values: DefectFormValues) => void | Promise<void>;
  /**
   * Optional cancel callback rendered as a secondary action button.
   */
  onCancel?: () => void;
  /**
   * Flag for coordinating external submission state (e.g. API mutation).
   */
  submitting?: boolean;
  /**
   * Optional error string surfaced above controls.
   */
  error?: string | null;
}

const REQUIRED_FIELDS = ['title', 'severity', 'category', 'status'] as const;

const defaultRawValues: RawDefectFormValues = {
  title: '',
  severity: '',
  category: '',
  status: '',
  scriptId: '',
  executionId: '',
  languageCode: '',
  assignedTo: '',
  description: '',
};

const emptyToNull = (value: string): string | null => {
  const trimmed = value.trim();
  return trimmed.length ? trimmed : null;
};

const trimRequired = (value: string): string => value.trim();

/**
 * Convert raw string-based form data into the normalised structure used by the
 * wider application.
 */
export const normalizeDefectFormValues = (values: RawDefectFormValues): DefectFormValues => ({
  title: trimRequired(values.title),
  severity: trimRequired(values.severity),
  category: trimRequired(values.category),
  status: trimRequired(values.status),
  scriptId: emptyToNull(values.scriptId),
  executionId: emptyToNull(values.executionId),
  languageCode: emptyToNull(values.languageCode),
  assignedTo: emptyToNull(values.assignedTo),
  description: emptyToNull(values.description),
});

const toRawValues = (initial?: Partial<DefectFormValues>): RawDefectFormValues => ({
  ...defaultRawValues,
  title: initial?.title ?? defaultRawValues.title,
  severity: initial?.severity ?? defaultRawValues.severity,
  category: initial?.category ?? defaultRawValues.category,
  status: initial?.status ?? defaultRawValues.status,
  scriptId: initial?.scriptId ?? defaultRawValues.scriptId,
  executionId: initial?.executionId ?? defaultRawValues.executionId,
  languageCode: initial?.languageCode ?? defaultRawValues.languageCode,
  assignedTo: initial?.assignedTo ?? defaultRawValues.assignedTo,
  description: initial?.description ?? defaultRawValues.description,
});

const severityOptions = [
  { value: '', label: 'Select severity' },
  { value: 'critical', label: 'Critical' },
  { value: 'high', label: 'High' },
  { value: 'medium', label: 'Medium' },
  { value: 'low', label: 'Low' },
];

const categoryOptions = [
  { value: '', label: 'Select category' },
  { value: 'functional', label: 'Functional' },
  { value: 'performance', label: 'Performance' },
  { value: 'localisation', label: 'Localisation' },
  { value: 'accessibility', label: 'Accessibility' },
];

const statusOptions = [
  { value: '', label: 'Select status' },
  { value: 'open', label: 'Open' },
  { value: 'in_progress', label: 'In Progress' },
  { value: 'resolved', label: 'Resolved' },
];

const getSubmitLabel = (mode: 'create' | 'edit') =>
  mode === 'create' ? 'Create Defect' : 'Save Changes';

const DefectForm: React.FC<DefectFormProps> = ({
  mode = 'create',
  initialValues,
  onSubmit,
  onCancel,
  submitting = false,
  error = null,
}) => {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RawDefectFormValues>({
    defaultValues: toRawValues(initialValues),
  });

  const submitLabel = getSubmitLabel(mode);
  const isBusy = submitting || isSubmitting;

  const onFormSubmit = async (formValues: RawDefectFormValues) => {
    const normalized = normalizeDefectFormValues(formValues);
    await onSubmit(normalized);
  };

  return (
    <div className="card">
      <form onSubmit={handleSubmit(onFormSubmit)} noValidate>
        <div className="space-y-6">
          <div>
            <h3 className="text-lg font-semibold">
              {mode === 'create' ? 'Create Defect' : 'Edit Defect'}
            </h3>
            <p className="text-sm text-[var(--color-content-secondary)] mt-1">
              Capture defect metadata, link to associated test artefacts, and optionally assign an
              owner for follow-up.
            </p>
          </div>

          {error && (
            <p className="text-sm text-[var(--color-status-danger)]" data-testid="defect-form-error" role="alert">
              {error}
            </p>
          )}

          <div>
            <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1">
              Title <span className="text-[var(--color-status-danger)]">*</span>
            </label>
            <input
              type="text"
              {...register('title', {
                required: 'Title is required',
                validate: (value) => value.trim().length > 0 || 'Title is required',
              })}
              className={`w-full px-3 py-2 border rounded-md focus:ring-1 ${
                errors.title
                  ? 'border-[var(--color-status-danger)] focus:border-[var(--color-status-danger)] focus:ring-[var(--color-status-danger)]'
                  : 'border-[var(--color-border-default)] focus:border-[var(--color-brand-primary)] focus:ring-[var(--color-brand-primary)]'
              }`}
            />
            {errors.title && (
              <p className="mt-1 text-sm text-[var(--color-status-danger)]">{errors.title.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1">
              Severity <span className="text-[var(--color-status-danger)]">*</span>
            </label>
            <select
              {...register('severity', {
                required: 'Severity is required',
                validate: (value) => value.trim().length > 0 || 'Severity is required',
              })}
              className={`filter-select ${errors.severity ? 'border-[var(--color-status-danger)]' : ''}`}
            >
              {severityOptions.map((option) => (
                <option key={option.value || 'placeholder'} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            {errors.severity && (
              <p className="mt-1 text-sm text-[var(--color-status-danger)]">{errors.severity.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1">
              Category <span className="text-[var(--color-status-danger)]">*</span>
            </label>
            <select
              {...register('category', {
                required: 'Category is required',
                validate: (value) => value.trim().length > 0 || 'Category is required',
              })}
              className={`filter-select ${errors.category ? 'border-[var(--color-status-danger)]' : ''}`}
            >
              {categoryOptions.map((option) => (
                <option key={option.value || 'placeholder'} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            {errors.category && (
              <p className="mt-1 text-sm text-[var(--color-status-danger)]">{errors.category.message}</p>
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
              {statusOptions.map((option) => (
                <option key={option.value || 'placeholder'} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            {errors.status && (
              <p className="mt-1 text-sm text-[var(--color-status-danger)]">{errors.status.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1">
              Script ID
            </label>
            <input
              type="text"
              {...register('scriptId')}
              className="w-full px-3 py-2 border border-[var(--color-border-default)] rounded-md focus:border-[var(--color-brand-primary)] focus:ring-1 focus:ring-[var(--color-brand-primary)]"
            />
            <p className="mt-1 text-sm text-[var(--color-content-muted)]">
              Optional reference to the scenario script associated with this defect.
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1">
              Execution ID
            </label>
            <input
              type="text"
              {...register('executionId')}
              className="w-full px-3 py-2 border border-[var(--color-border-default)] rounded-md focus:border-[var(--color-brand-primary)] focus:ring-1 focus:ring-[var(--color-brand-primary)]"
            />
            <p className="mt-1 text-sm text-[var(--color-content-muted)]">
              Optional reference to the execution where the defect was observed.
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1">
              Language Code
            </label>
            <input
              type="text"
              {...register('languageCode')}
              className="w-full px-3 py-2 border border-[var(--color-border-default)] rounded-md focus:border-[var(--color-brand-primary)] focus:ring-1 focus:ring-[var(--color-brand-primary)]"
            />
            <p className="mt-1 text-sm text-[var(--color-content-muted)]">
              ISO language code if localisation-specific.
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1">
              Assigned To
            </label>
            <input
              type="text"
              {...register('assignedTo')}
              className="w-full px-3 py-2 border border-[var(--color-border-default)] rounded-md focus:border-[var(--color-brand-primary)] focus:ring-1 focus:ring-[var(--color-brand-primary)]"
            />
            <p className="mt-1 text-sm text-[var(--color-content-muted)]">
              Person responsible for triaging or resolving the defect.
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-[var(--color-content-secondary)] mb-1">
              Description
            </label>
            <textarea
              {...register('description')}
              rows={3}
              className="w-full px-3 py-2 border border-[var(--color-border-default)] rounded-md focus:border-[var(--color-brand-primary)] focus:ring-1 focus:ring-[var(--color-brand-primary)] resize-y"
            />
          </div>

          <div className="flex justify-end gap-3">
            {onCancel && (
              <button
                type="button"
                onClick={onCancel}
                disabled={isBusy}
                className="btn btn-secondary"
              >
                Cancel
              </button>
            )}
            <button type="submit" disabled={isBusy} className="btn">
              {submitLabel}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
};

export default DefectForm;

export { REQUIRED_FIELDS };
