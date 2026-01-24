import { beforeEach, describe, expect, it, vi } from 'vitest';
import axios from 'axios';
import SlackIntegrationPage from '../Integrations/Slack';
import { renderWithProviders, screen, waitFor, userEvent } from '../../test/utils';

vi.mock('axios', () => {
  const get = vi.fn();
  const put = vi.fn();
  const del = vi.fn();

  return {
    default: { get, put, delete: del },
    get,
    put,
    delete: del,
  };
});

const mockedAxios = axios as unknown as {
  get: ReturnType<typeof vi.fn>;
  put: ReturnType<typeof vi.fn>;
  delete: ReturnType<typeof vi.fn>;
};

describe('SlackIntegrationPage', () => {
  beforeEach(() => {
    mockedAxios.get.mockReset();
    mockedAxios.put.mockReset();
    mockedAxios.delete.mockReset();
  });

  it('loads Slack configuration, allows editing preferences, and saves updates', async () => {
    mockedAxios.get.mockResolvedValue({
      data: {
        isConnected: true,
        workspaceName: 'VoiceAI QA',
        workspaceIconUrl: 'https://slack.example.com/icon.png',
        connectUrl: 'https://slack.com/oauth/authorize?client_id=123',
        defaultChannel: '#qa-alerts',
        notificationPreferences: {
          suiteRun: { enabled: true, channel: '#qa-alerts' },
          criticalDefect: { enabled: true, channel: '#critical-alerts' },
          systemAlert: { enabled: false, channel: '#ops-alerts' },
        },
        botTokenSet: true,
        signingSecretSet: true,
      },
    });

    mockedAxios.put.mockResolvedValue({
      data: {
        isConnected: true,
        workspaceName: 'VoiceAI QA',
        workspaceIconUrl: 'https://slack.example.com/icon.png',
        connectUrl: 'https://slack.com/oauth/authorize?client_id=123',
        defaultChannel: '#voice-ai-quality',
        notificationPreferences: {
          suiteRun: { enabled: true, channel: '#voice-ai-quality' },
          criticalDefect: { enabled: true, channel: '#voice-ai-critical' },
          systemAlert: { enabled: true, channel: '#voice-ai-ops' },
        },
        botTokenSet: true,
        signingSecretSet: true,
      },
    });

    renderWithProviders(<SlackIntegrationPage />);

    await waitFor(() => expect(mockedAxios.get).toHaveBeenCalledTimes(1));

    expect(screen.getByRole('heading', { name: /Slack Integration/i })).toBeInTheDocument();
    expect(screen.getByText(/Connected to VoiceAI QA/i)).toBeInTheDocument();

    const defaultChannelInput = await screen.findByLabelText(/Default notification channel/i);
    await userEvent.clear(defaultChannelInput);
    await userEvent.type(defaultChannelInput, '#voice-ai-quality');

    const systemAlertToggle = screen.getByLabelText(/Enable system alert notifications/i);
    await userEvent.click(systemAlertToggle);

    const suiteRunChannelInput = screen.getByLabelText(/Suite run channel/i);
    await userEvent.clear(suiteRunChannelInput);
    await userEvent.type(suiteRunChannelInput, '#voice-ai-quality');

    const criticalChannelInput = screen.getByLabelText(/Critical defect channel/i);
    await userEvent.clear(criticalChannelInput);
    await userEvent.type(criticalChannelInput, '#voice-ai-critical');

    const systemChannelInput = screen.getByLabelText(/System alert channel/i);
    await userEvent.clear(systemChannelInput);
    await userEvent.type(systemChannelInput, '#voice-ai-ops');

    const saveButton = screen.getByRole('button', { name: /Save Slack settings/i });
    await userEvent.click(saveButton);

    await waitFor(() => {
      expect(mockedAxios.put).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/integrations/slack/config',
        {
          defaultChannel: '#voice-ai-quality',
          notificationPreferences: {
            suiteRun: { enabled: true, channel: '#voice-ai-quality' },
            criticalDefect: { enabled: true, channel: '#voice-ai-critical' },
            systemAlert: { enabled: true, channel: '#voice-ai-ops' },
          },
        },
        expect.any(Object)
      );
    });

    const successAlert = await screen.findByText(/Configuration saved successfully/i);
    expect(successAlert).toBeInTheDocument();
  });

  it('allows disconnecting the connected Slack workspace', async () => {
    mockedAxios.get.mockResolvedValue({
      data: {
        isConnected: true,
        workspaceName: 'VoiceAI QA',
        workspaceIconUrl: null,
        connectUrl: 'https://slack.com/oauth/authorize?client_id=123',
        defaultChannel: '#qa-alerts',
        notificationPreferences: {
          suiteRun: { enabled: true, channel: '#qa-alerts' },
          criticalDefect: { enabled: true, channel: '#critical-alerts' },
          systemAlert: { enabled: false, channel: '#ops-alerts' },
        },
        botTokenSet: true,
        signingSecretSet: true,
      },
    });

    mockedAxios.delete.mockResolvedValue({
      data: {
        isConnected: false,
        workspaceName: null,
        workspaceIconUrl: null,
        connectUrl: 'https://slack.com/oauth/authorize?client_id=123',
        defaultChannel: '',
        notificationPreferences: {
          suiteRun: { enabled: true, channel: '' },
          criticalDefect: { enabled: true, channel: '' },
          systemAlert: { enabled: true, channel: '' },
        },
        botTokenSet: false,
        signingSecretSet: false,
      },
    });

    renderWithProviders(<SlackIntegrationPage />);

    const disconnectButton = await screen.findByRole('button', { name: /Disconnect workspace/i });
    await userEvent.click(disconnectButton);

    await waitFor(() => {
      expect(mockedAxios.delete).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/integrations/slack/config',
        expect.any(Object)
      );
    });

    const successAlert = await screen.findByText(/Slack workspace disconnected/i);
    expect(successAlert).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Connect workspace/i })).toBeInTheDocument();
  });

  it('displays an error when configuration load fails and allows dismissing it', async () => {
    mockedAxios.get.mockRejectedValue({
      response: { data: { detail: 'Slack integration unavailable' } },
    });

    renderWithProviders(<SlackIntegrationPage />);

    const errorAlert = await screen.findByRole('alert');
    expect(errorAlert).toHaveTextContent('Slack integration unavailable');

    const dismissButton = screen.getByRole('button', { name: /Dismiss/i });
    await userEvent.click(dismissButton);

    await waitFor(() => {
      expect(screen.queryByRole('alert')).toBeNull();
    });
  });
});
