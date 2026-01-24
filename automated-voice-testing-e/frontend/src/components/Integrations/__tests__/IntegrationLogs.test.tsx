import { beforeEach, describe, expect, it, vi } from 'vitest';
import axios from 'axios';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import IntegrationLogs from '../IntegrationLogs';

vi.mock('axios', () => {
  const get = vi.fn();
  return {
    default: { get },
    get,
  };
});

const mockedAxios = axios as unknown as { get: ReturnType<typeof vi.fn> };

describe('IntegrationLogs', () => {
  beforeEach(() => {
    mockedAxios.get.mockReset();
  });

  it('loads logs for default filters and displays entries', async () => {
    mockedAxios.get.mockResolvedValue({
      data: {
        items: [
          {
            id: 'log-1',
            integration: 'slack',
            level: 'info',
            message: 'Notification delivered',
            timestamp: '2024-02-01T12:00:00Z',
            metadata: { channel: '#qa-alerts', status: 200 },
          },
          {
            id: 'log-2',
            integration: 'jira',
            level: 'error',
            message: 'Failed to sync defect',
            timestamp: '2024-02-01T12:05:00Z',
            metadata: { status: 500, detail: 'Internal error' },
          },
        ],
      },
    });

    render(<IntegrationLogs />);

    await waitFor(() => {
      expect(mockedAxios.get).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/integrations/logs',
        expect.objectContaining({
          params: expect.objectContaining({
            integration: 'all',
            level: 'all',
            limit: 20,
          }),
        })
      );
    });

    expect(await screen.findByText(/Notification delivered/i)).toBeInTheDocument();
    expect(screen.getByText(/Failed to sync defect/i)).toBeInTheDocument();
    expect(screen.getByText(/slack/i)).toBeInTheDocument();
    expect(screen.getByText(/jira/i)).toBeInTheDocument();
  });

  it('surfaces error when log retrieval fails', async () => {
    mockedAxios.get.mockRejectedValue({
      response: { data: { detail: 'Logs unavailable' } },
    });

    render(<IntegrationLogs />);

    const alert = await screen.findByRole('alert');
    expect(alert).toHaveTextContent('Logs unavailable');
  });

  it('supports refreshing with updated filters', async () => {
    mockedAxios.get
      .mockResolvedValueOnce({ data: { items: [] } })
      .mockResolvedValueOnce({
        data: {
          items: [
            {
              id: 'log-3',
              integration: 'github',
              level: 'warning',
              message: 'Commit status update delayed',
              timestamp: '2024-02-01T12:10:00Z',
              metadata: { retryCount: 2 },
            },
          ],
        },
      });

    render(<IntegrationLogs />);

    const integrationSelect = await screen.findByLabelText(/Integration/i);
    await userEvent.click(integrationSelect);
    await userEvent.click(screen.getByRole('option', { name: /GitHub/i }));

    const levelSelect = screen.getByLabelText(/Level/i);
    await userEvent.click(levelSelect);
    await userEvent.click(screen.getByRole('option', { name: /Warnings/i }));

    await userEvent.click(screen.getByRole('button', { name: /Refresh/i }));

    await waitFor(() => {
      expect(mockedAxios.get).toHaveBeenLastCalledWith(
        'http://localhost:8000/api/v1/integrations/logs',
        expect.objectContaining({
          params: expect.objectContaining({
            integration: 'github',
            level: 'warning',
            limit: 20,
          }),
        })
      );
    });

    expect(await screen.findByText(/Commit status update delayed/i)).toBeInTheDocument();
  });
});
