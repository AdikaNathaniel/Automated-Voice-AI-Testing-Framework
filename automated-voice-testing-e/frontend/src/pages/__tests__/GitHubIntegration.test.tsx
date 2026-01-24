import { beforeEach, describe, expect, it, vi } from 'vitest';
import axios from 'axios';
import GitHubIntegrationPage from '../Integrations/GitHub';
import { renderWithProviders, screen, waitFor, userEvent } from '../../test/utils';

vi.mock('axios', () => {
  const get = vi.fn();
  const post = vi.fn();
  const put = vi.fn();

  return {
    default: { get, post, put },
    get,
    post,
    put,
  };
});

const mockedAxios = axios as unknown as {
  get: ReturnType<typeof vi.fn>;
  post: ReturnType<typeof vi.fn>;
  put: ReturnType<typeof vi.fn>;
};

describe('GitHubIntegrationPage', () => {
  beforeEach(() => {
    mockedAxios.get.mockReset();
    mockedAxios.post.mockReset();
    mockedAxios.put.mockReset();
  });

  it('renders the connect card when integration is disconnected and triggers OAuth flow', async () => {
    mockedAxios.get.mockResolvedValue({
      data: {
        connected: false,
        account: null,
        authorizationUrl: null,
        syncSettings: null,
        repositories: [],
        lastSyncedAt: null,
      },
    });

    mockedAxios.post.mockResolvedValue({
      data: {
        authorizationUrl: 'https://github.com/login/oauth/authorize?state=xyz',
      },
    });

    renderWithProviders(<GitHubIntegrationPage />);

    await waitFor(() => expect(mockedAxios.get).toHaveBeenCalledTimes(1));

    expect(screen.getByRole('heading', { name: /GitHub Integration/i })).toBeInTheDocument();
    expect(screen.getByText(/Connect your GitHub account to sync test cases/i)).toBeInTheDocument();

    const connectButton = screen.getByRole('button', { name: /Connect GitHub/i });
    await userEvent.click(connectButton);

    await waitFor(() => {
      expect(mockedAxios.post).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/integrations/github/connect',
        undefined,
        expect.any(Object)
      );
    });

    const authorizeLink = await screen.findByRole('link', { name: /Complete GitHub connection/i });
    expect(authorizeLink).toHaveAttribute(
      'href',
      'https://github.com/login/oauth/authorize?state=xyz'
    );
  });

  it('renders sync settings when connected and submits updates', async () => {
    mockedAxios.get.mockResolvedValue({
      data: {
        connected: true,
        account: {
          login: 'octocat',
          avatarUrl: 'https://github.com/images/error/octocat_happy.gif',
          htmlUrl: 'https://github.com/octocat',
        },
        authorizationUrl: null,
        syncSettings: {
          repository: 'voice-ai/automated-testing',
          syncDirection: 'both',
          autoSync: true,
          createIssues: true,
        },
        repositories: [
          {
            id: 1,
            name: 'automated-testing',
            fullName: 'voice-ai/automated-testing',
            private: true,
            defaultBranch: 'main',
          },
          {
            id: 2,
            name: 'qa-suite',
            fullName: 'voice-ai/qa-suite',
            private: false,
            defaultBranch: 'develop',
          },
        ],
        lastSyncedAt: '2025-01-10T08:00:00Z',
      },
    });

    const updatedSettings = {
      repository: 'voice-ai/qa-suite',
      syncDirection: 'pull',
      autoSync: false,
      createIssues: false,
    };

    mockedAxios.put.mockResolvedValue({ data: updatedSettings });

    renderWithProviders(<GitHubIntegrationPage />);

    const repositorySelect = await screen.findByLabelText(/Repository/i);
    await userEvent.selectOptions(repositorySelect, 'voice-ai/qa-suite');

    const pullOnlyRadio = screen.getByLabelText(/Pull from GitHub/i);
    await userEvent.click(pullOnlyRadio);

    const autoSyncCheckbox = screen.getByLabelText(/Automatic sync/i);
    await userEvent.click(autoSyncCheckbox);

    const createIssuesCheckbox = screen.getByLabelText(/Create GitHub issues/i);
    await userEvent.click(createIssuesCheckbox);

    const saveButton = screen.getByRole('button', { name: /Save settings/i });
    await userEvent.click(saveButton);

    await waitFor(() => {
      expect(mockedAxios.put).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/integrations/github/sync-settings',
        updatedSettings,
        expect.any(Object)
      );
    });

    const successAlert = await screen.findByText(/Sync settings updated successfully/i);
    expect(successAlert).toBeInTheDocument();
  });
});

