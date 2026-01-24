import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import DefectForm, { DefectFormValues } from '../DefectForm';

describe('DefectForm', () => {
  const fillCommonFields = async () => {
    await userEvent.type(screen.getByLabelText(/Title/i), '  API Regression  ');
    await userEvent.selectOptions(screen.getByLabelText(/Severity/i), 'critical');
    await userEvent.selectOptions(screen.getByLabelText(/Category/i), 'functional');
    await userEvent.selectOptions(screen.getByLabelText(/Status/i), 'open');
    await userEvent.type(screen.getByLabelText(/Script ID/i), '  case-123  ');
    await userEvent.type(screen.getByLabelText(/Execution ID/i), '  exec-456  ');
    await userEvent.type(screen.getByLabelText(/Language Code/i), '  en-US  ');
    await userEvent.type(screen.getByLabelText(/Assigned To/i), '  alice  ');
    await userEvent.type(screen.getByLabelText(/Description/i), '  Steps to reproduce  ');
  };

  it('submits trimmed values and normalises empty optional fields in create mode', async () => {
    const onSubmit = vi.fn();

    render(<DefectForm mode="create" onSubmit={onSubmit} />);

    await fillCommonFields();

    await userEvent.click(screen.getByRole('button', { name: /Create Defect/i }));

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledTimes(1);
    });

    const submitted: DefectFormValues = onSubmit.mock.calls[0][0];

    expect(submitted).toEqual({
      title: 'API Regression',
      severity: 'critical',
      category: 'functional',
      status: 'open',
      scriptId: 'case-123',
      executionId: 'exec-456',
      languageCode: 'en-US',
      assignedTo: 'alice',
      description: 'Steps to reproduce',
    });
  });

  it('prefills initial values in edit mode and uses save changes label', async () => {
    const initialValues: DefectFormValues = {
      title: 'Existing defect',
      severity: 'high',
      category: 'performance',
      status: 'in_progress',
      scriptId: 'case-789',
      executionId: 'exec-000',
      languageCode: 'fr-FR',
      assignedTo: 'bob',
      description: 'Investigate slow response',
    };

    const onSubmit = vi.fn();

    render(<DefectForm mode="edit" initialValues={initialValues} onSubmit={onSubmit} />);

    expect(screen.getByDisplayValue(initialValues.title)).toBeInTheDocument();
    expect(screen.getByDisplayValue(initialValues.scriptId)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Save Changes/i })).toBeInTheDocument();

    await userEvent.selectOptions(screen.getByLabelText(/Status/i), 'resolved');
    await userEvent.click(screen.getByRole('button', { name: /Save Changes/i }));

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledTimes(1);
    });

    const submitted: DefectFormValues = onSubmit.mock.calls[0][0];
    expect(submitted.status).toBe('resolved');
    expect(submitted.title).toBe(initialValues.title);
  });

  it('prevents submission when required fields contain only whitespace', async () => {
    const onSubmit = vi.fn();

    render(<DefectForm mode="create" onSubmit={onSubmit} />);

    await userEvent.type(screen.getByLabelText(/Title/i), '   ');
    await userEvent.selectOptions(screen.getByLabelText(/Severity/i), 'critical');
    await userEvent.selectOptions(screen.getByLabelText(/Category/i), 'functional');
    await userEvent.selectOptions(screen.getByLabelText(/Status/i), 'open');
    await userEvent.type(screen.getByLabelText(/Script ID/i), '   ');

    await userEvent.click(screen.getByRole('button', { name: /Create Defect/i }));

    expect(await screen.findByText(/Title is required/i)).toBeInTheDocument();
    expect(await screen.findByText(/Script ID is required/i)).toBeInTheDocument();
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it('renders cancel action when provided and triggers callback', async () => {
    const onCancel = vi.fn();

    render(<DefectForm onSubmit={vi.fn()} onCancel={onCancel} />);

    await userEvent.click(screen.getByRole('button', { name: /Cancel/i }));

    expect(onCancel).toHaveBeenCalledTimes(1);
  });

  it('surfaces external error messages for failed submissions', () => {
    const errorMessage = 'Failed to save defect';

    render(<DefectForm onSubmit={vi.fn()} error={errorMessage} />);

    const errorNode = screen.getByRole('alert');
    expect(errorNode).toHaveTextContent(errorMessage);
  });
});
