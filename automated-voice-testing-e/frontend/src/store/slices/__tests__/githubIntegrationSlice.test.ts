import { beforeEach, describe, expect, it, vi } from 'vitest';
import { configureStore } from '@reduxjs/toolkit';
import axios from 'axios';

import reducer, {
  fetchGitHubIntegrationStatus,
  startGitHubConnection,
  disconnectGitHubIntegration,
  updateGitHubSyncSettings,
  type GitHubIntegrationState,
  initialState,
} from '../githubIntegrationSlice';

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

const createStore = (overrides: Partial<GitHubIntegrationState> = {}) =>
  configureStore({
    reducer: {
      githubIntegration: reducer,
    },
    preloadedState: {
      githubIntegration: { ...initialState, ...overrides },
    },
  });

describe('githubIntegrationSlice', () => {
  beforeEach(() => {
    mockedAxios.get.mockReset();
    mockedAxios.post.mockReset();
    mockedAxios.put.mockReset();
  });

  it('fetches integration status and normalises the state', async () => {
    const response = {
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
      ],
      lastSyncedAt: '2025-01-15T10:15:00Z',
    };

    mockedAxios.get.mockResolvedValue({ data: response });

    const store = createStore();
    await store.dispatch(fetchGitHubIntegrationStatus());

    expect(mockedAxios.get).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/integrations/github/status',
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: expect.stringContaining('Bearer'),
        }),
      })
    );

    const state = store.getState().githubIntegration;
    expect(state.isConnected).toBe(true);
    expect(state.account).toEqual(response.account);
    expect(state.connectionUrl).toBeNull();
    expect(state.syncSettings).toEqual(response.syncSettings);
    expect(state.repositories).toEqual(response.repositories);
    expect(state.lastSyncedAt).toBe(response.lastSyncedAt);
    expect(state.loading).toBe(false);
    expect(state.error).toBeNull();
  });

  it('stores error state when fetch status fails', async () => {
    mockedAxios.get.mockRejectedValue({
      response: { data: { detail: 'Integration status unavailable' } },
    });

    const store = createStore();
    await store.dispatch(fetchGitHubIntegrationStatus());

    const state = store.getState().githubIntegration;
    expect(state.loading).toBe(false);
    expect(state.error).toBe('Integration status unavailable');
    expect(state.isConnected).toBe(false);
  });

  it('captures the authorization URL when starting GitHub connection', async () => {
    mockedAxios.post.mockResolvedValue({
      data: { authorizationUrl: 'https://github.com/login/oauth/authorize?state=123' },
    });

    const store = createStore();
    await store.dispatch(startGitHubConnection());

    expect(mockedAxios.post).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/integrations/github/connect',
      undefined,
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: expect.stringContaining('Bearer'),
        }),
      })
    );

    const state = store.getState().githubIntegration;
    expect(state.connectionUrl).toBe('https://github.com/login/oauth/authorize?state=123');
    expect(state.loading).toBe(false);
    expect(state.error).toBeNull();
  });

  it('resets the state when disconnecting the integration', async () => {
    mockedAxios.post.mockResolvedValue({ data: { success: true } });

    const store = createStore({
      isConnected: true,
      account: {
        login: 'octocat',
        avatarUrl: 'avatar.png',
        htmlUrl: 'https://github.com/octocat',
      },
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
      ],
      connectionUrl: null,
    });

    await store.dispatch(disconnectGitHubIntegration());

    expect(mockedAxios.post).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/integrations/github/disconnect',
      undefined,
      expect.any(Object)
    );

    const state = store.getState().githubIntegration;
    expect(state).toEqual(initialState);
  });

  it('updates sync settings via API and stores the changes', async () => {
    const updatedSettings = {
      repository: 'voice-ai/automated-testing',
      syncDirection: 'pull',
      autoSync: false,
      createIssues: false,
    };

    mockedAxios.put.mockResolvedValue({ data: updatedSettings });

    const store = createStore({
      isConnected: true,
      account: {
        login: 'octocat',
        avatarUrl: 'avatar.png',
        htmlUrl: 'https://github.com/octocat',
      },
      syncSettings: {
        repository: '',
        syncDirection: 'both',
        autoSync: true,
        createIssues: true,
      },
    });

    await store.dispatch(updateGitHubSyncSettings(updatedSettings));

    expect(mockedAxios.put).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/integrations/github/sync-settings',
      updatedSettings,
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: expect.stringContaining('Bearer'),
        }),
      })
    );

    const state = store.getState().githubIntegration;
    expect(state.syncSettings).toEqual(updatedSettings);
    expect(state.savingSettings).toBe(false);
    expect(state.error).toBeNull();
  });
});

