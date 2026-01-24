import { beforeEach, describe, expect, it, vi } from 'vitest';
import axios from 'axios';
import IntegrationsDashboard from '../Integrations/IntegrationsDashboard';
import { renderWithProviders, screen, waitFor } from '../../test/utils';

vi.mock('axios', () => {
  const get = vi.fn();
  const post = vi.fn();
  const put = vi.fn();
  const del = vi.fn();

  return {
    default: { get, post, put, delete: del },
    get,
    post,
    put,
    delete: del,
  };
});

const mockedAxios = axios as unknown as {
  get: ReturnType<typeof vi.fn>;
  post: ReturnType<typeof vi.fn>;
  put: ReturnType<typeof vi.fn>;
  delete: ReturnType<typeof vi.fn>;
};

const successMocks = () => {
  mockedAxios.get.mockImplementation((url: string) => {
    if (url.endsWith('/integrations/github/status')) {
      return Promise.resolve({
        data: {
          connected: true,
          account: {
            login: 'voiceai-bot',
            avatarUrl: 'https://github.example.com/avatar.png',
            htmlUrl: 'https://github.com/voiceai-bot',
          },
          authorizationUrl: null,
          syncSettings: {
            repository: 'voiceai/testing',
            syncDirection: 'both',
            autoSync: true,
            createIssues: true,
          },
          repositories: [
            {
              id: 1,
              name: 'testing',
              fullName: 'voiceai/testing',
              private: true,
              defaultBranch: 'main',
            },
          ],
          lastSyncedAt: '2024-02-01T12:00:00Z',
        },
      });
    }

    if (url.endsWith('/integrations/jira/config')) {
      return Promise.resolve({
        data: {
          baseUrl: 'https://example.atlassian.net/rest/api/3',
          browseUrl: 'https://example.atlassian.net',
          userEmail: 'qa@example.com',
          apiTokenSet: true,
          projectMapping: {
            voice: {
              projectKey: 'QA',
              issueType: 'Bug',
              browseUrl: 'https://example.atlassian.net/browse',
            },
            analytics: {
              projectKey: 'AN',
              issueType: 'Task',
            },
          },
        },
      });
    }

    if (url.endsWith('/integrations/slack/config')) {
      return Promise.resolve({
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
    }

    if (url.endsWith('/integrations/logs')) {
      return Promise.resolve({
        data: {
          items: [
            {
              id: 'log-1',
              integration: 'slack',
              level: 'info',
              message: 'Notification delivered to #qa-alerts',
              timestamp: '2024-02-01T12:00:00Z',
            },
            {
              id: 'log-2',
              integration: 'github',
              level: 'warning',
              message: 'Commit status update delayed',
              timestamp: '2024-02-01T12:05:00Z',
            },
          ],
        },
      });
    }

    return Promise.reject(new Error(`Unhandled GET ${url}`));
  });
};

describe('IntegrationsDashboard', () => {
  beforeEach(() => {
    mockedAxios.get.mockReset();
    mockedAxios.post.mockReset();
    mockedAxios.put.mockReset();
    mockedAxios.delete.mockReset();
  });

  it('loads integration summaries and displays connection statuses', async () => {
    successMocks();

    renderWithProviders(<IntegrationsDashboard />);

    await waitFor(() => {
      expect(mockedAxios.get).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/integrations/github/status',
        expect.any(Object)
      );
      expect(mockedAxios.get).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/integrations/jira/config',
        expect.any(Object)
      );
      expect(mockedAxios.get).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/integrations/slack/config',
        expect.any(Object)
      );
      expect(mockedAxios.get).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/integrations/logs',
        expect.any(Object)
      );
    });

    expect(await screen.findByText(/Integrations Dashboard/i)).toBeInTheDocument();

    expect(screen.getByText(/VoiceAI QA/i)).toBeInTheDocument();
    expect(screen.getAllByText(/Connected/i)).toHaveLength(3);
    expect(screen.getByText(/qa@example.com/i)).toBeInTheDocument();
    expect(screen.getByText(/voiceai\/testing/i)).toBeInTheDocument();

    expect(screen.getByRole('link', { name: /Manage Slack/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Manage Jira/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Manage GitHub/i })).toBeInTheDocument();
    expect(screen.getByText(/Notification delivered to #qa-alerts/i)).toBeInTheDocument();
    expect(screen.getByText(/Commit status update delayed/i)).toBeInTheDocument();
  });

  it('surfaces errors when any integration status fails to load', async () => {
    mockedAxios.get.mockImplementation((url: string) => {
      if (url.endsWith('/integrations/slack/config')) {
        return Promise.reject({
          response: { data: { detail: 'Slack integration unavailable' } },
        });
      }

      if (url.endsWith('/integrations/jira/config')) {
        return Promise.resolve({
          data: {
            baseUrl: 'https://example.atlassian.net/rest/api/3',
            browseUrl: 'https://example.atlassian.net',
            userEmail: 'qa@example.com',
            apiTokenSet: true,
            projectMapping: {},
          },
        });
      }

      if (url.endsWith('/integrations/github/status')) {
        return Promise.resolve({
          data: {
            connected: false,
            account: null,
            authorizationUrl: 'https://github.com/login/oauth/authorize',
            syncSettings: null,
            repositories: [],
            lastSyncedAt: null,
          },
        });
      }

      if (url.endsWith('/integrations/logs')) {
        return Promise.resolve({ data: { items: [] } });
      }

      return Promise.reject(new Error(`Unhandled GET ${url}`));
    });

    renderWithProviders(<IntegrationsDashboard />);

    const errorAlert = await screen.findByRole('alert');
    expect(errorAlert).toHaveTextContent('Slack integration unavailable');

    // Other integration information is still rendered.
    expect(screen.getByRole('link', { name: /Manage GitHub/i })).toBeInTheDocument();
  });
});
