import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import DefectAssignmentModal, {
  DefectAssignmentFormValues,
} from '../DefectAssignmentModal';

describe('DefectAssignmentModal', () => {
  const baseProps = {
    open: true,
    defectTitle: 'Critical API regression',
    currentAssignee: 'alice',
    currentStatus: 'open',
    assignees: ['alice', 'bob', 'carol'],
    statuses: [
      { value: 'open', label: 'Open' },
      { value: 'in_progress', label: 'In Progress' },
      { value: 'resolved', label: 'Resolved' },
    ],
  };

  it('renders with initial values and submits trimmed selection via callback', async () => {
    const onSubmit = vi.fn();

    render(
      <DefectAssignmentModal
        {...baseProps}
        currentAssignee="  alice  "
        currentStatus="  open  "
        onSubmit={onSubmit}
        onClose={vi.fn()}
      />
    );

    expect(
      screen.getByRole('heading', { name: /Update assignment for Critical API regression/i })
    ).toBeInTheDocument();
    expect(screen.getByDisplayValue('alice')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Open')).toBeInTheDocument();

    await userEvent.selectOptions(screen.getByLabelText(/Assign To/i), 'bob');
    await userEvent.selectOptions(screen.getByLabelText(/Status/i), 'in_progress');

    await userEvent.click(screen.getByRole('button', { name: /Save Assignment/i }));

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledTimes(1);
    });

    const submission: DefectAssignmentFormValues = onSubmit.mock.calls[0][0];
    expect(submission).toEqual({ assignee: 'bob', status: 'in_progress', comment: null });
  });

  it('blocks submission when required fields are empty and surfaces validation messages', async () => {
    const onSubmit = vi.fn();

    render(
      <DefectAssignmentModal
        {...baseProps}
        currentAssignee=""
        currentStatus=""
        onSubmit={onSubmit}
        onClose={vi.fn()}
      />
    );

    await userEvent.selectOptions(screen.getByLabelText(/Assign To/i), '');
    await userEvent.selectOptions(screen.getByLabelText(/Status/i), '');

    await userEvent.click(screen.getByRole('button', { name: /Save Assignment/i }));

    expect(await screen.findByText(/Assignee is required/i)).toBeInTheDocument();
    expect(await screen.findByText(/Status is required/i)).toBeInTheDocument();
    expect(onSubmit).not.toHaveBeenCalled();
  });
  it('invokes onClose when cancel is clicked', async () => {
    const onClose = vi.fn();

    render(
      <DefectAssignmentModal
        {...baseProps}
        onSubmit={vi.fn()}
        onClose={onClose}
      />
    );

    await userEvent.click(screen.getByRole('button', { name: /Cancel/i }));
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('shows external error message and preserves comment input', async () => {
    const onSubmit = vi.fn();

    render(
      <DefectAssignmentModal
        {...baseProps}
        error="Unable to update assignment"
        onSubmit={onSubmit}
        onClose={vi.fn()}
      />
    );

    expect(screen.getByRole('alert')).toHaveTextContent(/Unable to update assignment/i);

    await userEvent.type(screen.getByLabelText(/Comment/i), 'Need backup');
    await userEvent.click(screen.getByRole('button', { name: /Save Assignment/i }));

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledTimes(1);
    });

    const submission: DefectAssignmentFormValues = onSubmit.mock.calls[0][0];
    expect(submission.comment).toBe('Need backup');
  });
});
