import { beforeEach, describe, expect, it, vi } from 'vitest';
import { configureStore } from '@reduxjs/toolkit';
import axios from 'axios';

import reducer, {
  fetchSlackIntegrationConfig,
  saveSlackIntegrationConfig,
  disconnectSlackIntegration,
  clearSlackIntegrationError,
  clearSlackIntegrationSuccess,
  initialState,
  type SlackIntegrationState,
  type SlackIntegrationUpdatePayload,
} from '../slackIntegrationSlice';

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

const createStore = (overrides: Partial<SlackIntegrationState> = {}) =>
  configureStore({
    reducer: {
      slackIntegration: reducer,
    },
    preloadedState: {
      slackIntegration: { ...initialState, ...overrides },
    },
  });

describe('slackIntegrationSlice', () => {
  beforeEach(() => {
    mockedAxios.get.mockReset();
    mockedAxios.put.mockReset();
    mockedAxios.delete.mockReset();
  });

  it('fetches Slack integration configuration and normalises state', async () => {
    const response = {
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
    };

    mockedAxios.get.mockResolvedValue({ data: response });

    const store = createStore();
    await store.dispatch(fetchSlackIntegrationConfig());

    expect(mockedAxios.get).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/integrations/slack/config',
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: expect.stringContaining('Bearer'),
        }),
      })
    );

    const state = store.getState().slackIntegration;
    expect(state.loading).toBe(false);
    expect(state.error).toBeNull();
    expect(state.config).toEqual(response);
  });

  it('stores error when fetching Slack configuration fails', async () => {
    mockedAxios.get.mockRejectedValue({
      response: { data: { detail: 'Slack integration unavailable' } },
    });

    const store = createStore();
    await store.dispatch(fetchSlackIntegrationConfig());

    const state = store.getState().slackIntegration;
    expect(state.loading).toBe(false);
    expect(state.error).toBe('Slack integration unavailable');
  });

  it('saves configuration updates and records success state', async () => {
    const payload: SlackIntegrationUpdatePayload = {
      defaultChannel: '#qa-alerts',
      notificationPreferences: {
        suiteRun: { enabled: true, channel: '#qa-alerts' },
        criticalDefect: { enabled: true, channel: '#critical-alerts' },
        systemAlert: { enabled: true, channel: '#ops-alerts' },
      },
    };

    const updatedResponse = {
      ...payload,
      isConnected: true,
      workspaceName: 'VoiceAI QA',
      workspaceIconUrl: 'https://slack.example.com/icon.png',
      connectUrl: 'https://slack.com/oauth/authorize?client_id=123',
      botTokenSet: true,
      signingSecretSet: true,
    };

    mockedAxios.put.mockResolvedValue({ data: updatedResponse });

    const store = createStore();
    await store.dispatch(saveSlackIntegrationConfig(payload));

    expect(mockedAxios.put).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/integrations/slack/config',
      payload,
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: expect.stringContaining('Bearer'),
        }),
      })
    );

    const state = store.getState().slackIntegration;
    expect(state.saving).toBe(false);
    expect(state.success).toBe('Configuration saved successfully');
    expect(state.config).toEqual(updatedResponse);

    store.dispatch(clearSlackIntegrationSuccess());
    expect(store.getState().slackIntegration.success).toBeNull();
  });

  it('stores error when saving Slack configuration fails and allows clearing', async () => {
    mockedAxios.put.mockRejectedValue({
      response: { data: { detail: 'Failed to update Slack configuration' } },
    });

    const store = createStore();
    await store.dispatch(
      saveSlackIntegrationConfig({
        defaultChannel: '#qa-alerts',
        notificationPreferences: {
          suiteRun: { enabled: true, channel: '#qa-alerts' },
          criticalDefect: { enabled: true, channel: '#critical-alerts' },
          systemAlert: { enabled: false, channel: '#ops-alerts' },
        },
      })
    );

    const state = store.getState().slackIntegration;
    expect(state.saving).toBe(false);
    expect(state.error).toBe('Failed to update Slack configuration');

    store.dispatch(clearSlackIntegrationError());
    expect(store.getState().slackIntegration.error).toBeNull();
  });

  it('disconnects the Slack workspace and resets connection state', async () => {
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

    const store = createStore();
    await store.dispatch(disconnectSlackIntegration());

    expect(mockedAxios.delete).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/integrations/slack/config',
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: expect.stringContaining('Bearer'),
        }),
      })
    );

    const state = store.getState().slackIntegration;
    expect(state.config.isConnected).toBe(false);
    expect(state.success).toBe('Slack workspace disconnected');
  });
});
