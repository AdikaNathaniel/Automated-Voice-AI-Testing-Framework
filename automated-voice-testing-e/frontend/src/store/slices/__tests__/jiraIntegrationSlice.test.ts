import { beforeEach, describe, expect, it, vi } from 'vitest';
import { configureStore } from '@reduxjs/toolkit';
import axios from 'axios';

import reducer, {
  fetchJiraIntegrationConfig,
  saveJiraIntegrationConfig,
  clearJiraIntegrationError,
  clearJiraIntegrationSuccess,
  initialState,
  type JiraIntegrationState,
  type JiraIntegrationUpdatePayload,
} from '../jiraIntegrationSlice';

vi.mock('axios', () => {
  const get = vi.fn();
  const put = vi.fn();

  return {
    default: { get, put },
    get,
    put,
  };
});

const mockedAxios = axios as unknown as {
  get: ReturnType<typeof vi.fn>;
  put: ReturnType<typeof vi.fn>;
};

const createStore = (overrides: Partial<JiraIntegrationState> = {}) =>
  configureStore({
    reducer: {
      jiraIntegration: reducer,
    },
    preloadedState: {
      jiraIntegration: { ...initialState, ...overrides },
    },
  });

describe('jiraIntegrationSlice', () => {
  beforeEach(() => {
    mockedAxios.get.mockReset();
    mockedAxios.put.mockReset();
  });

  it('fetches Jira integration configuration and normalises state', async () => {
    const response = {
      baseUrl: 'https://example.atlassian.net/rest/api/3',
      browseUrl: 'https://example.atlassian.net',
      userEmail: 'qa@example.com',
      apiTokenSet: true,
      timeoutSeconds: 15,
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
    };

    mockedAxios.get.mockResolvedValue({ data: response });

    const store = createStore();
    await store.dispatch(fetchJiraIntegrationConfig());

    expect(mockedAxios.get).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/integrations/jira/config',
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: expect.stringContaining('Bearer'),
        }),
      })
    );

    const state = store.getState().jiraIntegration;
    expect(state.loading).toBe(false);
    expect(state.error).toBeNull();
    expect(state.config).toEqual(response);
  });

  it('stores error when fetching Jira integration configuration fails', async () => {
    mockedAxios.get.mockRejectedValue({
      response: { data: { detail: 'Integration unavailable' } },
    });

    const store = createStore();
    await store.dispatch(fetchJiraIntegrationConfig());

    const state = store.getState().jiraIntegration;
    expect(state.loading).toBe(false);
    expect(state.error).toBe('Integration unavailable');
  });

  it('saves configuration updates and records success state', async () => {
    const payload: JiraIntegrationUpdatePayload = {
      baseUrl: 'https://example.atlassian.net/rest/api/3',
      browseUrl: 'https://example.atlassian.net',
      userEmail: 'qa@example.com',
      apiToken: 'new-token',
      timeoutSeconds: 20,
      projectMapping: {
        voice: {
          projectKey: 'QA',
          issueType: 'Bug',
        },
      },
    };

    const updatedResponse = {
      ...payload,
      apiTokenSet: true,
    };
    delete (updatedResponse as unknown).apiToken;

    mockedAxios.put.mockResolvedValue({ data: updatedResponse });

    const store = createStore();
    await store.dispatch(saveJiraIntegrationConfig(payload));

    expect(mockedAxios.put).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/integrations/jira/config',
      payload,
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: expect.stringContaining('Bearer'),
        }),
      })
    );

    const state = store.getState().jiraIntegration;
    expect(state.saving).toBe(false);
    expect(state.success).toBe('Configuration saved successfully');
    expect(state.config).toEqual(updatedResponse);

    store.dispatch(clearJiraIntegrationSuccess());
    expect(store.getState().jiraIntegration.success).toBeNull();
  });

  it('stores error when saving configuration fails and allows clearing', async () => {
    mockedAxios.put.mockRejectedValue({
      response: { data: { detail: 'Failed to update configuration' } },
    });

    const store = createStore();
    await store.dispatch(
      saveJiraIntegrationConfig({
        baseUrl: 'https://example.atlassian.net/rest/api/3',
        browseUrl: 'https://example.atlassian.net',
        userEmail: 'qa@example.com',
        projectMapping: {},
      })
    );

    const state = store.getState().jiraIntegration;
    expect(state.saving).toBe(false);
    expect(state.error).toBe('Failed to update configuration');

    store.dispatch(clearJiraIntegrationError());
    expect(store.getState().jiraIntegration.error).toBeNull();
  });
});
